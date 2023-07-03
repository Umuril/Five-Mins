# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend


class PasswordlessTestBackend(BaseBackend):
    def authenticate(self, *args, username=None, **kwargs):
        return get_user_model().objects.filter(
            groups__name='Test Users', username=username).first()

    def get_user(self, user_id):
        return get_user_model().objects.filter(
            groups__name='Test Users', pk=user_id).first()
