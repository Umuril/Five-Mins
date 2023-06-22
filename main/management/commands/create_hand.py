from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

from faker import Faker
from ...models import Hand

import random
from datetime import UTC
from djmoney.money import Money

class Command(BaseCommand):
    help = 'Create a fake Hand'

    def add_arguments(self, parser):
        parser.add_argument('-n', '--num', type=int, help='Create multiple Hands')


    def handle(self, *args, **kwargs):
        count = kwargs['num'] if kwargs['num'] else 1

        faker = Faker(['it_IT']) # https://faker.readthedocs.io/en/master/providers.html

        for idx in range(count):
            requester = User.objects.order_by("?").first()

            hand = Hand()

            hand.title = faker.job()
            hand.description = faker.paragraph()
            hand.request_location = faker.address()
            hand.request_price = Money(faker.pyfloat(left_digits=3, right_digits=2, positive=True), 'EUR')

            hand.requester = requester
            hand.request_start_time = faker.future_datetime().replace(tzinfo=UTC)

            a = faker.future_datetime().replace(tzinfo=UTC)
            b = faker.future_datetime().replace(tzinfo=UTC)
            delta = a - b if a > b else b - a
            hand.request_duration = delta

            hand.save()

            print(f"[{idx + 1}] Hand {hand} created")


