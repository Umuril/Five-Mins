# -*- coding: utf-8 -*-

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Create a Worker user'

    def add_arguments(self, parser):
        parser.add_argument('-n', '--num', type=int, help='Create multiple workers')

    def handle(self, *args, **kwargs):
        try:
            test_users = Group.objects.get(name='Test Users')
            workers = Group.objects.get(name='Workers')
        except Group.DoesNotExist as exc:
            raise CommandError('"python3 manage.py init" command is required first.') from exc

        count = kwargs['num'] if kwargs['num'] else 1

        available_users = list(get_user_model().objects.filter(groups=test_users).exclude(groups=workers).all())

        for idx in range(count):

            if len(available_users) == 0:
                raise CommandError('No more Users free for working.')

            user = available_users.pop()
            user.groups.add(workers)
            user.save()

            print(f'[{idx + 1}] Worker assigned to user {user.username}.')
