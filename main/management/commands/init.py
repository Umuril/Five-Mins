from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Group

class Command(BaseCommand):
    help = 'Run init scripts'

    def handle(self, *args, **kwargs):
        print("INIT COMMAND START")

        Group.objects.get_or_create(name='Workers')
        print("Workers group created")

        Group.objects.get_or_create(name='Test Users')
        print("Test Users group created")

        print("INIT COMMAND END")