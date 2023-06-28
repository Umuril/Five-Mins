from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.db.models import Count

from faker import Faker
from ...models import Hand

import random
from datetime import UTC, date, datetime, time
from djmoney.money import Money


def progress_hand(faker, option):
    if option == "wip":
        hand = Hand.objects.filter(status=Hand.Status.RESERVED).order_by("?").first()
        if hand is None:
            raise CommandError("No available Hands to progress.")

        hand.status = Hand.Status.IN_PROGRESS
        hand.request_date = date.today()

        while hand.request_start_time >= datetime.now().time():
            hand.request_start_time = faker.time_object().replace(
                second=0, microsecond=0
            )

        while hand.request_end_time <= datetime.now().time():
            hand.request_end_time = faker.time_object().replace(second=0, microsecond=0)
    elif option == "done":
        hand = (
            Hand.objects.filter(
                status__in=[Hand.Status.RESERVED, Hand.Status.IN_PROGRESS]
            )
            .order_by("?")
            .first()
        )
        if hand is None:
            raise CommandError("No available Hands to progress.")

        hand.status = Hand.Status.DONE
        hand.request_date = faker.past_date()
    else:
        raise CommandError("Unexpecter option on progress_hand.")

    return hand


class Command(BaseCommand):
    help = "Fakes a Hand to be In Progress or Done"

    def add_arguments(self, parser):
        parser.add_argument(
            "-i", "--wip", action="store_true", help="Status Work In Progress"
        )
        parser.add_argument("-d", "--done", action="store_true", help="Status Done")
        parser.add_argument("-n", "--num", type=int, help="Applies to multiple Hands")

    def handle(self, *args, **kwargs):
        if not (kwargs["wip"] ^ kwargs["done"]):
            raise CommandError("Choose one option between --wip or --done.")
        option = "wip" if kwargs["wip"] else "done"
        count = kwargs["num"] if kwargs["num"] else 1

        faker = Faker(
            ["it_IT"]
        )  # https://faker.readthedocs.io/en/master/providers.html

        for idx in range(count):
            hand = progress_hand(faker, option)
            hand.save()

            print(f"[{idx + 1}] Hand '{hand}' status changed to '{hand.status.label}'")
