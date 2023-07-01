# -*- coding: utf-8 -*-
"""
URL configuration for five_mins project.

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
    path('hand/add/', main.HandCreateView.as_view(), name='hand-add'),
    path('hand/<int:pk>/', main.HandDetailView.as_view(), name='hand-detail'),
    path(
        'hand/<int:pk>/delete/',
        main.HandDeleteView.as_view(),
        name='hand-delete'),
    path(
        'hand/<int:hand_pk>/submit/',
        main.submit,
        name='hand-submit'),
    path(
        'hand/<int:hand_pk>/assign_to/<int:user_pk>/',
        main.assing_to,
        name='hand-assign_to'),
    path(
        'hand/<int:hand_pk>/rating/',
        main.rating,
        name='hand-rating'),
    path('history', main.history, name='history'),
]
