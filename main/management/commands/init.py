# -*- coding: utf-8 -*-
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from main.models import Hand


class Command(BaseCommand):
    help = 'Run init scripts'

    def handle(self, *args, **kwargs):
        print('INIT COMMAND START')

        Group.objects.get_or_create(name='Test Users')
        print('Test Users group created')

        workers, _ = Group.objects.get_or_create(name='Workers')
        print('Workers group created')

        content_type = ContentType.objects.get_for_model(Hand)
        permission = Permission.objects.create(
            codename='can_submit_for_hands',
            name='Can submit for Hands',
            content_type=content_type)  # creating permissions
        workers.permissions.add(permission)
        print('Permissions for group Workers created')

        print('INIT COMMAND END')
