from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

from model_bakery import baker

class Command(BaseCommand):
    help = 'Create a logged user'

    def add_arguments(self, parser):
        parser.add_argument('-n', '--num', type=int, help='Create multiple users')


    def handle(self, *args, **kwargs):
        count = kwargs['num'] if kwargs['num'] else 1

        for idx in range(count):
            user = baker.prepare(User)

            key =  user.username[:5].capitalize()

            user.username = f"USER-{key}"
            user.set_password(key)
            user.save()

            print(f"[{idx + 1}] User {user.username} created with password {key}")

