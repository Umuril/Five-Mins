# -*- coding: utf-8 -*-
from django.apps import AppConfig


class KnockConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'knock'

    def ready(self):
        pass
