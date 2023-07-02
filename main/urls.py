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

from main import views

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('knock/add/', views.KnockCreateView.as_view(), name='knock-add'),
    path('knock/<int:pk>/', views.KnockDetailView.as_view(), name='knock-detail'),
    path('knock/<int:pk>/delete/', views.KnockDeleteView.as_view(), name='knock-delete'),
    path('knock/<int:knock_pk>/submit/', views.submit, name='knock-submit'),
    path('knock/<int:knock_pk>/assign_to/<int:user_pk>/', views.assing_to, name='knock-assign_to'),
    path('knock/<int:knock_pk>/rating/', views.rating, name='knock-rating'),
    path('profile/', views.my_profile, name='my-profile'),
    path('profile/<int:user_pk>/', views.profile, name='profile'),
    path('search/', views.search, name='search'),
]
