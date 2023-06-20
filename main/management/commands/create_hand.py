from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

from model_bakery import baker

from ...models import Hand

import random

class Command(BaseCommand):
    help = 'Create a fake Hand'

    def add_arguments(self, parser):
        parser.add_argument('-n', '--num', type=int, help='Create multiple Hands')


    def handle(self, *args, **kwargs):
        count = kwargs['num'] if kwargs['num'] else 1

        for idx in range(count):
            random_prefix = random.choices(['USER-', 'WORKER-'], cum_weights=[4, 5])[0] # One worker every five users
            requester = User.objects.filter(username__startswith=random_prefix).order_by("?").first()

            hand = baker.prepare(Hand)

            hand.requester = requester

            hand.save()

            print(f"[{idx + 1}] Hand {hand} created")


