# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from djmoney.money import Money
from faker import Faker

from main.models import Hand


def create_open_hand(faker):
    requester = get_user_model().objects.filter(
        groups__name='Test Users').order_by('?').first()

    hand = Hand()

    job = faker.job()
    while len(job) > 50:
        job = faker.job()
    hand.title = job
    hand.description = faker.paragraph()
    # hand.request_location = faker.address()
    hand.request_price = Money(
        faker.pyfloat(left_digits=3, right_digits=2, positive=True), 'EUR'
    )

    hand.requester = requester
    hand.request_date = faker.future_date()

    time_one = faker.time_object().replace(second=0, microsecond=0)
    time_two = faker.time_object().replace(second=0, microsecond=0)

    hand.request_start_time = min(time_one, time_two)
    hand.request_end_time = max(time_one, time_two)

    return hand


class Command(BaseCommand):
    help = 'Create a fake Hand'

    def add_arguments(self, parser):
        parser.add_argument('-n', '--num', type=int,
                            help='Create multiple Hands')

    def handle(self, *args, **kwargs):
        count = kwargs['num'] if kwargs['num'] else 1

        faker = Faker(
            ['it_IT']
        )  # https://faker.readthedocs.io/en/master/providers.html

        for idx in range(count):
            hand = create_open_hand(faker)

            hand.save()

            print(f"[{idx + 1}] {hand.status} Hand '{hand}' created ")
