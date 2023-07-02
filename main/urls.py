# -*- coding: utf-8 -*-
"""
URL configuration for knock_knock project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path

from .views import main

urlpatterns = [
    path('', main.homepage, name='homepage'),
    path('knock/add/', main.KnockCreateView.as_view(), name='knock-add'),
    path('knock/<int:pk>/', main.KnockDetailView.as_view(), name='knock-detail'),
    path(
        'knock/<int:pk>/delete/',
        main.KnockDeleteView.as_view(),
        name='knock-delete'),
    path(
        'knock/<int:knock_pk>/submit/',
        main.submit,
        name='knock-submit'),
    path(
        'knock/<int:knock_pk>/assign_to/<int:user_pk>/',
        main.assing_to,
        name='knock-assign_to'),
    path(
        'knock/<int:knock_pk>/rating/',
        main.rating,
        name='knock-rating'),
    path('history', main.history, name='history'),
]
