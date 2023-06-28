# -*- coding: utf-8 -*-
import random

from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand, CommandError
from faker import Faker

from main.management.commands.create_user import create_user
from main.models import Profile


class Command(BaseCommand):
    help = 'Create a Worker user'

    def add_arguments(self, parser):
        parser.add_argument('-n', '--num', type=int,
                            help='Create multiple workers')

    def handle(self, *args, **kwargs):
        try:
            test_users = Group.objects.get(name='Test Users')
            workers = Group.objects.get(name='Workers')
        except Group.DoesNotExist as exc:
            raise CommandError(
                '"python3 manage.py init" command is required first.') from exc

        faker = Faker(
            ['it_IT']
        )  # https://faker.readthedocs.io/en/master/providers.html

        count = kwargs['num'] if kwargs['num'] else 1

        for idx in range(count):
            gender = random.choice(['M', 'F'])

            user = create_user(faker, gender)
            user.save()

            user.groups.add(workers)
            user.groups.add(test_users)
            user.save()

            Profile(user=user, gender=gender).save()

            print(f'[{idx + 1}] Worker {user.username} created.')
