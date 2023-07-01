# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView

from main.forms import HandForm
from main.models import Hand, HandSubmit

# Create your views here.


def homepage(request):

    my_hands = []
    my_submits = []

    if request.user.is_authenticated:
        first_filter = Q(requester=request.user.pk) & ~Q(status=Hand.Status.CLOSED) & Q(work_stars__isnull=True)
        second_filter = Q(assigned_to=request.user.pk) & ~Q(status=Hand.Status.CLOSED) & Q(request_stars__isnull=True)
        my_hands = Hand.objects.filter(first_filter | second_filter).select_related('requester')

        my_submits = Hand.objects.filter(submits=request.user.pk, status=Hand.Status.OPEN).select_related('requester')

    last_updated_hands = Hand.objects.exclude().select_related('requester').order_by('-update_time')[:20]

    ctx = {'last_updated_hands': last_updated_hands, 'my_hands': my_hands, 'my_submits': my_submits}

    return render(request, 'main/homepage.html', context=ctx)


class HandCreateView(LoginRequiredMixin, CreateView):
    model = Hand
    form_class = HandForm

    def form_valid(self, form):
        form.instance.requester = self.request.user
        return super().form_valid(form)


class HandDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Hand
    # form_class = HandForm
    success_url = reverse_lazy('homepage')

    def test_func(self):
        return self.get_object().requester.pk == self.request.user.pk and self.get_object().status in [Hand.Status.OPEN, Hand.Status.RESERVED]


class HandDetailView(DetailView):
    model = Hand
    form_class = HandForm


@login_required
def history(request):
    hands = Hand.objects.filter(status=Hand.Status.CLOSED).filter(Q(requester=request.user.pk) | Q(
        assigned_to=request.user.pk)).select_related('requester').order_by('-update_time')

    return render(request, 'main/history.html', context={'hands': hands})


@login_required
@permission_required('main.can_submit_for_hands')
def submit(request, hand_pk):
    hand = get_object_or_404(Hand, pk=hand_pk)

    if hand.requester.pk == request.user.pk:
        raise PermissionDenied('Cannot submit to owned hands')

    if HandSubmit.objects.filter(hand=hand, user=request.user).exists():
        raise PermissionDenied('User already submitted for this Hand')

    hand.submits.add(request.user)
    hand.save()

    return redirect(reverse('hand-detail', args=[hand_pk]))


@login_required
def assing_to(request, hand_pk, user_pk):
    hand = get_object_or_404(Hand, pk=hand_pk)
    user = get_object_or_404(get_user_model(), pk=user_pk)

    if hand.requester.pk != request.user.pk:
        raise PermissionDenied('Can assign only to owned Hands')

    if not HandSubmit.objects.filter(hand=hand_pk, user=user_pk).exists():
        raise PermissionDenied('Cannot assing if worker didn\'t submit before')

    hand.assigned_to = user
    hand.save()

    return redirect(reverse('hand-detail', args=[hand_pk]))


@login_required
def rating(request, hand_pk):
    hand = get_object_or_404(Hand, pk=hand_pk)
    rating_value = request.POST.get('rating', None)

    if rating_value is None:
        raise PermissionDenied('rating field missing')

    try:
        rating_value = int(rating_value)
        if rating_value < 1 or rating_value > 5:
            raise ValueError()
    except ValueError as exc:
        raise PermissionDenied('rating must be a value between 1 and 5') from exc

    if hand.assigned_to.pk == request.user.pk:
        # Worker who has the Hand assigned rating the requester
        if hand.request_stars is not None:
            raise PermissionDenied('Worker already rated this Hand')

        hand.request_stars = rating_value
        hand.save()

    elif hand.requester.pk == request.user.pk:
        # User who created the Hand rating the Worker

        if hand.work_stars is not None:
            raise PermissionDenied('Worker already rated this Hand')

        hand.work_stars = rating_value
        hand.save()
    else:
        raise PermissionDenied('Only requester and assigned can rate this Hand')

    return redirect(reverse('hand-detail', args=[hand_pk]))
