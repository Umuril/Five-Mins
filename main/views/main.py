# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView

from main.forms import KnockForm
from main.models import Knock, KnockSubmit

# Create your views here.


def homepage(request):

    my_knocks = []
    my_submits = []

    if request.user.is_authenticated:
        first_filter = Q(requester=request.user.pk) & ~Q(status=Knock.Status.CLOSED) & Q(work_stars__isnull=True)
        second_filter = Q(assigned_to=request.user.pk) & ~Q(status=Knock.Status.CLOSED) & Q(request_stars__isnull=True)
        my_knocks = Knock.objects.filter(first_filter | second_filter).select_related('requester')

        my_submits = Knock.objects.filter(submits=request.user.pk, status=Knock.Status.OPEN).select_related('requester')

    last_updated_knocks = Knock.objects.exclude().select_related('requester').order_by('-update_time')[:20]

    ctx = {'last_updated_knocks': last_updated_knocks, 'my_knocks': my_knocks, 'my_submits': my_submits}

    return render(request, 'main/homepage.html', context=ctx)


class KnockCreateView(LoginRequiredMixin, CreateView):
    model = Knock
    form_class = KnockForm

    def form_valid(self, form):
        form.instance.requester = self.request.user
        return super().form_valid(form)


class KnockDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Knock
    success_url = reverse_lazy('homepage')

    def test_func(self):
        return self.get_object().requester.pk == self.request.user.pk and self.get_object().status in [Knock.Status.OPEN, Knock.Status.RESERVED]


class KnockDetailView(DetailView):
    model = Knock
    form_class = KnockForm


@login_required
def history(request):
    knocks = Knock.objects.filter(status=Knock.Status.CLOSED).filter(Q(requester=request.user.pk) | Q(
        assigned_to=request.user.pk)).select_related('requester').order_by('-update_time')

    return render(request, 'main/history.html', context={'knocks': knocks})


@login_required
@permission_required('main.can_submit_for_knocks')
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
