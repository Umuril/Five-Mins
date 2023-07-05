# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from knock.models import Knock, Profile


class Command(BaseCommand):
    help = 'Run init scripts'

    def handle(self, *args, **kwargs):
        print('INIT COMMAND START')

        Group.objects.get_or_create(name='Test Users')
        print('Test Users group created')

        only_free, _ = Group.objects.get_or_create(name='Only Free Users')
        print('Only Free Users group created')

        only_work, _ = Group.objects.get_or_create(name='Only Work Users')
        print('Only Work Users group created')

        content_type = ContentType.objects.get_for_model(Knock)
        permission = Permission.objects.create(
            codename='view_only_free', name='Can view only Free Knock Knocks', content_type=content_type
        )
        only_free.permissions.add(permission)
        permission = Permission.objects.create(
            codename='view_only_work', name='Can view only Not Free Knock Knocks', content_type=content_type
        )
        only_work.permissions.add(permission)
        print('Permissions for groups created')

        user = get_user_model().objects.get(username='root')
        profile = Profile(user=user)
        profile.save()
        print('Profile for user root created')

        print('INIT COMMAND END')
