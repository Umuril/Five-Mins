# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from faker import Faker

from knock.models import Knock


def rate_knock(faker):
    knock = Knock.objects.filter(Q(request_stars=None) | Q(work_stars=None), status=Knock.Status.DONE).order_by('?').first()
    if knock is None:
        raise CommandError('No available Knock Knocks to rate.')

    rate_value = faker.enum(Knock.StarsAnswer)

    if knock.request_stars is None and knock.work_stars is None:
        if faker.pybool():
            knock.request_stars = rate_value
        else:
            knock.work_stars = rate_value
    elif knock.request_stars is None:
        knock.request_stars = rate_value
    else:
        knock.work_stars = rate_value

    return knock


class Command(BaseCommand):
    help = 'Fakes a rating for a Knock Knock'

    def add_arguments(self, parser):
        parser.add_argument('-n', '--num', type=int, help='Applies to multiple Knock Knocks')

    def handle(self, *args, **kwargs):
        count = kwargs['num'] if kwargs['num'] else 1

        faker = Faker(['it_IT'])  # https://faker.readthedocs.io/en/master/providers.html

        for idx in range(count):
            knock = rate_knock(faker)
            knock.save()

            status_str = knock.get_status_display().upper()

            print(f'[{idx + 1}] Knock Knock {knock} rated - Current status: {status_str}')
