# -*- coding: utf-8 -*-
import datetime

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView

from knock.forms import (KnockForm, ProfileUpdateForm, UserRegisterForm,
                         UserUpdateForm)
from knock.models import (Knock, KnockChat, KnockChatMessage, KnockSubmit,
                          Profile)


def homepage(request):
    my_knocks = []
    my_submits = []
    page = request.GET.get('page')

    if request.user.is_authenticated:

        if request.user.has_perm('knock.view_only_free'):
            auth_filter = Q(request_price=0)
        elif request.user.has_perm('knock.view_only_work'):
            auth_filter = Q(request_price__gt=0)
        else:
            auth_filter = Q()

        first_filter = Q(requester=request.user.pk) & ~Q(status=Knock.Status.CLOSED) & Q(work_stars__isnull=True)
        second_filter = Q(assigned_to=request.user.pk) & ~Q(status=Knock.Status.CLOSED) & Q(request_stars__isnull=True)
        third_filter = Q(status=Knock.Status.OPEN) & ~Q(requester=request.user.pk)
        four_filter = Q(submits=request.user.pk, status=Knock.Status.OPEN)
        five_filter = Q(chats__user=request.user.pk, status=Knock.Status.OPEN)

        if not page or int(page) <= 1:
            my_knocks = Knock.objects.filter(first_filter | second_filter).select_related('requester').order_by('-update_time')
            my_submits = Knock.objects.filter(four_filter).select_related('requester') \
                .union(Knock.objects.filter(five_filter).select_related('requester')).order_by('-update_time')

        last_updated_knocks = Knock.objects.filter(auth_filter & third_filter).exclude(
            five_filter).select_related('requester').order_by('-update_time')
    else:
        # last_updated_knocks = Knock.objects.all().select_related('requester').order_by('-update_time')
        last_updated_knocks = Knock.objects.all().select_related('requester').order_by('?')

    paginator = Paginator(last_updated_knocks, 20)

    try:
        last_updated_knocks = paginator.page(page)
    except PageNotAnInteger:
        last_updated_knocks = paginator.page(1)
    except EmptyPage:
        last_updated_knocks = paginator.page(paginator.num_pages)

    ctx = {'last_updated_knocks': last_updated_knocks, 'my_knocks': my_knocks, 'my_submits': my_submits}

    return render(request, 'knock/homepage.html', context=ctx)


class KnockCreateView(LoginRequiredMixin, CreateView):
    model = Knock
    form_class = KnockForm

    def form_valid(self, form):
        form.instance.requester = self.request.user
        messages.success(self.request, 'Knock knock created successfully')
        return super().form_valid(form)


class KnockDeleteView(LoginRequiredMixin, DeleteView):
    model = Knock

    def get_queryset(self):
        return super().get_queryset().filter(requester=self.request.user, status__in=[Knock.Status.OPEN, Knock.Status.RESERVED])

    def get_success_url(self):
        messages.success(self.request, 'Knock knock removed successfully')
        return reverse('homepage')


class KnockDetailView(DetailView):
    model = Knock
    form_class = KnockForm

    def get_queryset(self):
        return super().get_queryset().prefetch_related('knocksubmit_set__user')


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileUpdateForm


@login_required
def update_profile(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile is updated successfully')
            return redirect(to='my-profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    return render(request, 'knock/profile_edit.html', {'user_form': user_form, 'profile_form': profile_form})


@login_required
def submit(request, knock_pk):
    knock = get_object_or_404(Knock, pk=knock_pk)

    if knock.requester.pk == request.user.pk:
        raise PermissionDenied('Cannot submit to owned knocks')

    if KnockSubmit.objects.filter(knock=knock, user=request.user).exists():
        raise PermissionDenied('User already submitted for this Knock Knock')

    knock.submits.add(request.user)
    knock.save()

    messages.success(request, 'Knock knock submitted successfully')

    return redirect(reverse('knock-detail', args=[knock_pk]))


@login_required
def unsubmit(request, knock_pk):
    knock = get_object_or_404(Knock, pk=knock_pk)

    if knock.requester.pk == request.user.pk:
        raise PermissionDenied('Cannot unsubmit to owned Knocks')

    if not KnockSubmit.objects.filter(knock=knock, user=request.user).exists():
        raise PermissionDenied('User never submitted for this Knock Knock')

    knock.submits.remove(request.user)
    knock.save()

    messages.success(request, 'Knock knock unsubmitted successfully')

    return redirect(reverse('knock-detail', args=[knock_pk]))


@login_required
def assing_to(request, knock_pk, user_pk):
    knock = get_object_or_404(Knock, pk=knock_pk)
    user = get_object_or_404(get_user_model(), pk=user_pk)

    if knock.requester.pk != request.user.pk:
        raise PermissionDenied('Can assign only to owned Knock Knocks')

    if not KnockSubmit.objects.filter(knock=knock_pk, user=user_pk).exists():
        raise PermissionDenied('Cannot assing if worker didn\'t submit before')

    knock.assigned_to = user
    knock.save()

    messages.success(request, 'Knock knock assigned successfully')

    return redirect(reverse('knock-detail', args=[knock_pk]))


@login_required
def rating(request, knock_pk):
    knock = get_object_or_404(Knock, pk=knock_pk)
    rating_value = request.POST.get('rating', None)

    if rating_value is None:
        raise PermissionDenied('rating field missing')

    try:
        rating_value = int(rating_value)
        if rating_value < 1 or rating_value > 5:
            raise ValueError()
    except ValueError as exc:
        raise PermissionDenied('rating must be a value between 1 and 5') from exc

    if knock.assigned_to.pk == request.user.pk:
        # Worker who has the Knock Knock assigned rating the requester
        if knock.request_stars is not None:
            raise PermissionDenied('Worker already rated this Knock Knock')

        knock.request_stars = rating_value
        knock.save()

        user_profile = knock.requester.profile
        user_profile.recalculate_stars()
        user_profile.save()

    elif knock.requester.pk == request.user.pk:
        # User who created the Knock Knock rating the Worker

        if knock.work_stars is not None:
            raise PermissionDenied('Worker already rated this Knock Knock')

        knock.work_stars = rating_value
        knock.save()

        user_profile = knock.requester.profile
        user_profile.recalculate_stars()
        user_profile.save()
    else:
        raise PermissionDenied('Only requester and assigned can rate this Knock Knock')

    return redirect(reverse('knock-detail', args=[knock_pk]))


@login_required
def my_profile(request):
    return redirect(reverse('profile', args=[request.user.pk]))


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            form.cleaned_data.get('username')
            messages.success(request, 'Your account has been created! You are now able to log in')
            return redirect('login', )
    else:
        form = UserRegisterForm()
    return render(request, 'registration/register.html', {'form': form})


def profile(request, user_pk):
    if request.user.is_authenticated and user_pk == request.user.pk:
        user_profile = request.user
    else:
        user_profile = get_object_or_404(get_user_model(), pk=user_pk)

    knocks = Knock.objects.filter(Q(requester=user_pk) | Q(assigned_to=user_pk)).select_related('requester').order_by('-update_time')

    paginator = Paginator(knocks, 5)
    page = request.GET.get('page')

    try:
        knocks = paginator.page(page)
    except PageNotAnInteger:
        knocks = paginator.page(1)
    except EmptyPage:
        knocks = paginator.page(paginator.num_pages)

    ctx = {
        'user_profile': user_profile,
        'knocks': knocks,
    }

    return render(request, 'knock/profile.html', context=ctx)


def search(request):

    results = []
    filters = []

    title = request.GET.get('title', '')
    if title.strip():
        filters += [Q(title__icontains=title)]

    category = request.GET.get('category', '')
    if category.strip():
        filters += [Q(category__icontains=category)]

    status = request.GET.get('status', '')
    if status.strip():
        filters += [Q(status=status[0])]

    date = request.GET.get('date', '')
    try:
        date = datetime.date.fromisoformat(date)
        filters += [Q(request_date=date)]
    except ValueError:
        pass

    filter_acc = Q()
    if len(filters) > 0:
        for filt in filters:
            filter_acc &= filt

        if request.user.is_authenticated and request.user.has_perm('knock.view_only_free'):
            auth_filter = Q(request_price=0)
        elif request.user.is_authenticated and request.user.has_perm('knock.view_only_work'):
            auth_filter = Q(request_price__gt=0)
        else:
            auth_filter = Q()

        results = Knock.objects.filter(auth_filter & filter_acc).select_related('requester').all()

        if len(results) == 0:
            messages.error(request, 'No results found')

    paginator = Paginator(results, 20)
    page = request.GET.get('page')

    try:
        results = paginator.page(page)
    except PageNotAnInteger:
        results = paginator.page(1)
    except EmptyPage:
        results = paginator.page(paginator.num_pages)

    url_params = f'title={title}&date={date}&category={category}&status={status}'

    ctx = {'results': results, 'url_params': url_params, 'current': {'title': title, 'date': date, 'category': category, 'status': status}}

    return render(request, 'knock/search.html', context=ctx)


@login_required
def chat(request, knock_pk, user_pk):

    if request.method == 'POST':
        text = request.POST.get('text', '')

        knock_chat = get_object_or_404(KnockChat, knock=knock_pk, user=user_pk)

        if request.user.pk == knock_chat.knock.requester.pk:
            receiver = knock_chat.user
        elif request.user.pk == knock_chat.user.pk:
            receiver = knock_chat.knock.requester
        else:
            raise PermissionDenied('User id errors on chat')

        msg = KnockChatMessage()
        msg.chat = knock_chat
        msg.sender = request.user
        msg.receiver = receiver
        msg.text = text
        msg.save()

        return redirect(reverse('chat', args=[knock_pk, user_pk]))

    try:
        knock_chat = KnockChat.objects \
            .select_related('user', 'knock__requester') \
            .prefetch_related('messages__sender') \
            .get(knock=knock_pk, user=user_pk)
    except KnockChat.DoesNotExist:
        knock_chat = KnockChat()
        knock_chat.knock = get_object_or_404(Knock, pk=knock_pk)
        knock_chat.user = get_object_or_404(get_user_model(), pk=user_pk)
        knock_chat.save()

    if request.user == knock_chat.knock.requester:
        receiver = knock_chat.user
    elif request.user == knock_chat.user:
        receiver = knock_chat.knock.requester
    else:
        raise PermissionDenied('User id errors on chat')

    can_write = knock_chat.knock.requester.pk == request.user.pk and knock_chat.knock.work_stars is None \
        or knock_chat.user.pk == request.user.pk and (
            knock_chat.knock.assigned_to is None or knock_chat.knock.assigned_to.pk == request.user.pk
        ) and knock_chat.knock.request_stars is None

    ctx = {'chat': knock_chat, 'receiver': receiver, 'can_write': can_write}

    return render(request, 'knock/chat.html', context=ctx)
