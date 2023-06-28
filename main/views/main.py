# -*- coding: utf-8 -*-
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView

from main.forms import HandForm
from main.models import Hand


# Create your views here.
def homepage(request):
    hands = Hand.objects.all().select_related('requester')
    my_hands = Hand.objects.filter(requester=request.user.pk).select_related(
        'requester'
    )
    return render(
        request, 'main/homepage.html', context={'hands': hands, 'my_hands': my_hands}
    )


class HandCreateView(LoginRequiredMixin, CreateView):
    model = Hand
    form_class = HandForm

    def form_valid(self, form):
        form.instance.requester = self.request.user
        return super().form_valid(form)


class HandUpdateView(LoginRequiredMixin, UpdateView):
    model = Hand
    form_class = HandForm


class HandDeleteView(LoginRequiredMixin, DeleteView):
    model = Hand
    form_class = HandForm


class HandDetailView(LoginRequiredMixin, DetailView):
    model = Hand
    form_class = HandForm
