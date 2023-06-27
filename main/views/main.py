from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import (
    TemplateView,
    FormView,
    CreateView,
    UpdateView,
    DeleteView,
    DetailView,
)
from ..forms import HandForm
from ..models import Hand
from django import forms


# Create your views here.
def homepage(request):
    return render(request, "main/index.html", context={"test_check": "ok"})


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
