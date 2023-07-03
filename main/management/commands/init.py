# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from main.models import Knock, Profile


class Command(BaseCommand):
    help = 'Run init scripts'

    def handle(self, *args, **kwargs):
        print('INIT COMMAND START')

        Group.objects.get_or_create(name='Test Users')
        print('Test Users group created')

        workers, _ = Group.objects.get_or_create(name='Workers')
        print('Workers group created')

        content_type = ContentType.objects.get_for_model(Knock)
        permission = Permission.objects.create(
            codename='can_submit_for_knocks',
            name='Can submit for Knock Knocks',
            content_type=content_type)  # creating permissions
        workers.permissions.add(permission)
        print('Permissions for group Workers created')

        user = get_user_model().objects.get(username='root')
        profile = Profile(user=user)
        profile.save()
        print('Profile for user root created')

        print('INIT COMMAND END')
