# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from main.models import Hand


def create_submit():
    hand = Hand.objects.filter(status=Hand.Status.OPEN).order_by('?').first()
    worker = get_user_model().objects.filter(
        groups__name='Workers').order_by('?').first()
    hand.submits.add(worker)

    return hand, worker


class Command(BaseCommand):
    help = 'Create a fake Submit'

    def add_arguments(self, parser):
        parser.add_argument('-n', '--num', type=int,
                            help='Create multiple Submits')

    def handle(self, *args, **kwargs):
        count = kwargs['num'] if kwargs['num'] else 1

        for idx in range(count):
            hand, worker = create_submit()
            hand.save()

            print(f"[{idx + 1}] Submit for hand '{hand}' created by {worker}")
