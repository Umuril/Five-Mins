from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User, Group

from model_bakery import baker

class Command(BaseCommand):
    help = 'Create a Worker user'

    def add_arguments(self, parser):
        parser.add_argument('-n', '--num', type=int, help='Create multiple workers')

    def handle(self, *args, **kwargs):
        try:
            workers = Group.objects.get(name='Workers')
        except Group.DoesNotExist:
            raise CommandError('"python3 manage.py init" command is required first.')

        count = kwargs['num'] if kwargs['num'] else 1
        
        for idx in range(count):
            user = baker.prepare(User)

            key =  user.username[:5].capitalize()

            user.username = f"WORKER-{key}"
            user.set_password(key)
            user.save()

            user.groups.add(workers)
            user.save()

            print(f"[{idx + 1}] User {user.username} created with password {key}")
