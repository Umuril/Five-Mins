# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from djmoney.money import Money
from faker import Faker

from knock.models import Knock


def create_open_knock(faker):
    requester = get_user_model().objects.filter(groups__name='Test Users').order_by('?').first()

    knock = Knock()

    job = faker.job()
    while len(job) > 50:
        job = faker.job()
    knock.title = job
    knock.description = faker.paragraph()
    knock.category = faker.enum(Knock.Category)

    # knock.request_location = faker.address()
    if faker.pybool():
        knock.request_price = Money(0, 'EUR')
    else:
        knock.request_price = Money(
            faker.pyfloat(
                left_digits=faker.pyint(
                    min_value=1,
                    max_value=3),
                right_digits=faker.pyint(
                    min_value=0,
                    max_value=2),
                positive=True),
            'EUR')

    knock.requester = requester
    knock.request_date = faker.future_date()

    time_one = faker.time_object().replace(second=0, microsecond=0)
    time_two = faker.time_object().replace(second=0, microsecond=0)

    while time_one == time_two:
        time_two = faker.time_object().replace(second=0, microsecond=0)

    knock.request_start_time = min(time_one, time_two)
    knock.request_end_time = max(time_one, time_two)

    return knock


class Command(BaseCommand):
    help = 'Create a fake Knock Knock'

    def add_arguments(self, parser):
        parser.add_argument('-n', '--num', type=int, help='Create multiple Knock Knocks')

    def handle(self, *args, **kwargs):
        count = kwargs['num'] if kwargs['num'] else 1

        faker = Faker(['it_IT'])  # https://faker.readthedocs.io/en/master/providers.html

        for idx in range(count):
            knock = create_open_knock(faker)

            knock.save()

            print(f'[{idx + 1}] Knock Knock {knock} created ')
