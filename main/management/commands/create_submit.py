from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

from faker import Faker
from ...models import Hand

import random
from datetime import UTC, date, datetime
from djmoney.money import Money


def create_submit(faker):
    hand = Hand.objects.filter(status=Hand.Status.OPEN).order_by("?").first()
    worker = User.objects.filter(groups__name="Workers").order_by("?").first()
    hand.submits.add(worker)

    return hand, worker


class Command(BaseCommand):
    help = "Create a fake Submit"

    def add_arguments(self, parser):
        parser.add_argument("-n", "--num", type=int, help="Create multiple Submits")

    def handle(self, *args, **kwargs):
        count = kwargs["num"] if kwargs["num"] else 1

        faker = Faker(
            ["it_IT"]
        )  # https://faker.readthedocs.io/en/master/providers.html

        for idx in range(count):
            hand, worker = create_submit(faker)
            hand.save()

            print(f"[{idx + 1}] Submit for hand '{hand}' created by {worker}")
