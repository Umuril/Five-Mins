# -*- coding: utf-8 -*-
import datetime

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Avg, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView

from knock.forms import (KnockForm, ProfileUpdateForm, UserRegisterForm,
                         UserUpdateForm)
from knock.models import Knock, KnockChat, KnockChatMessage, KnockSubmit


def homepage(request):

    my_knocks = []
    my_submits = []

    if request.user.is_authenticated:
        first_filter = Q(requester=request.user.pk) & ~Q(status=Knock.Status.CLOSED) & Q(work_stars__isnull=True)
        second_filter = Q(assigned_to=request.user.pk) & ~Q(status=Knock.Status.CLOSED) & Q(request_stars__isnull=True)
        my_knocks = Knock.objects.filter(first_filter | second_filter).select_related('requester')

        my_submits = Knock.objects.filter(submits=request.user.pk, status=Knock.Status.OPEN).select_related('requester')

    last_updated_knocks = Knock.objects.exclude().select_related('requester').order_by('-update_time')

    paginator = Paginator(last_updated_knocks, 20)
    page = request.GET.get('page')

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
        return super().form_valid(form)


class KnockDeleteView(LoginRequiredMixin, DeleteView):
    model = Knock
    success_url = reverse_lazy('homepage')

    def get_queryset(self):
        return super().get_queryset().filter(requester=self.request.user, status__in=[Knock.Status.OPEN, Knock.Status.RESERVED])


class KnockDetailView(DetailView):
    model = Knock
    form_class = KnockForm

    def get_queryset(self):
        return super().get_queryset().prefetch_related('knocksubmit_set__user')


@login_required
@permission_required('knock.can_submit_for_knocks')
def submit(request, knock_pk):
    knock = get_object_or_404(Knock, pk=knock_pk)

    if knock.requester.pk == request.user.pk:
        raise PermissionDenied('Cannot submit to owned knocks')

    if KnockSubmit.objects.filter(knock=knock, user=request.user).exists():
        raise PermissionDenied('User already submitted for this Knock Knock')

    knock.submits.add(request.user)
    knock.save()

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

    elif knock.requester.pk == request.user.pk:
        # User who created the Knock Knock rating the Worker

        if knock.work_stars is not None:
            raise PermissionDenied('Worker already rated this Knock Knock')

        knock.work_stars = rating_value
        knock.save()
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
    return render(request, 'knock/register.html', {'form': form})


def profile(request, user_pk):
    if request.method == 'POST':
        if not request.user.is_authenticated or user_pk != request.user.pk:
            raise PermissionDenied('Cannot change other user profile')

        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your account has been updated!')
            return redirect(reverse('profile', args=[request.user.pk]))

    elif request.user.is_authenticated and user_pk == request.user.pk:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
        user_profile = request.user
    else:
        u_form = None
        p_form = None
        user_profile = get_object_or_404(get_user_model(), pk=user_pk)

    knocks = Knock.objects.filter(Q(requester=user_pk) | Q(assigned_to=user_pk)).select_related('requester').order_by('-update_time')

    request_rating = Knock.objects.filter(requester=user_pk).aggregate(Avg('request_stars'))['request_stars__avg']
    work_rating = Knock.objects.filter(assigned_to=user_pk).aggregate(Avg('work_stars'))['work_stars__avg']

    ctx = {
        'user_profile': user_profile,
        'knocks': knocks,
        'request_rating': request_rating,
        'work_rating': work_rating,
        'u_form': u_form,
        'p_form': p_form
    }

    return render(request, 'knock/profile.html', context=ctx)


def search(request):

    results = []
    filters = []

    title = request.GET.get('title', '')
    if title.strip():
        filters += [Q(title__icontains=title)]

    date = request.GET.get('date', '')
    if title is not None:
        try:
            date = datetime.date.fromisoformat(date)
            filters += [Q(request_date=date)]
        except ValueError:
            pass

    category = request.GET.get('category', '')
    if category.strip():
        filters += [Q(category__icontains=category)]

    filter_acc = Q()
    if len(filters) > 0:
        for filt in filters:
            filter_acc &= filt
        results = Knock.objects.filter(filter_acc).select_related('requester').all()

    paginator = Paginator(results, 20)
    page = request.GET.get('page')

    try:
        results = paginator.page(page)
    except PageNotAnInteger:
        results = paginator.page(1)
    except EmptyPage:
        results = paginator.page(paginator.num_pages)

    url_params = f'title={title}&date={date}&category={category}'

    ctx = {'results': results, 'url_params': url_params}

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
        knock_chat = KnockChat.objects.select_related(
            'user', 'knock__requester').prefetch_related('messages__sender').get(
            knock=knock_pk, user=user_pk)
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
