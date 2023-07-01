# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count

from main.models import Hand


def reserve_hand():
    hand = Hand.objects.filter(status=Hand.Status.OPEN).annotate(submits_count=Count('submits')).filter(submits_count__gt=0).order_by('?').first()

    if hand is None:
        raise CommandError('No available Hands to reserve.')

    worker = hand.submits.order_by('?').first()

    hand.status = Hand.Status.RESERVED
    hand.assigned_to = worker

    return hand, worker


class Command(BaseCommand):
    help = 'Fakes reserving a Hand'

    def add_arguments(self, parser):
        parser.add_argument('-n', '--num', type=int, help='Fakes multiple reserves')

    def handle(self, *args, **kwargs):
        count = kwargs['num'] if kwargs['num'] else 1

        for idx in range(count):
            hand, worker = reserve_hand()
            hand.save()

            print(f'[{idx + 1}] Hand {hand} reserved to {worker}')
