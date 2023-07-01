# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from faker import Faker

from main.models import Hand


def rate_hand(faker):
    hand = Hand.objects.filter(Q(request_stars=None) | Q(work_stars=None), status=Hand.Status.DONE).order_by('?').first()
    if hand is None:
        raise CommandError('No available Hands to rate.')

    rate_value = faker.enum(Hand.StarsAnswer)

    if hand.request_stars is None and hand.work_stars is None:
        if faker.pybool():
            hand.request_stars = rate_value
        else:
            hand.work_stars = rate_value
    elif hand.request_stars is None:
        hand.request_stars = rate_value
    else:
        hand.work_stars = rate_value

    return hand


class Command(BaseCommand):
    help = 'Fakes a rating for a Hand'

    def add_arguments(self, parser):
        parser.add_argument('-n', '--num', type=int, help='Applies to multiple Hands')

    def handle(self, *args, **kwargs):
        count = kwargs['num'] if kwargs['num'] else 1

        faker = Faker(['it_IT'])  # https://faker.readthedocs.io/en/master/providers.html

        for idx in range(count):
            hand = rate_hand(faker)
            hand.save()

            status_str = hand.get_status_display().upper()

            print(f'[{idx + 1}] Hand {hand} rated - Current status: {status_str}')
