# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count

from main.models import Knock


def reserve_knock():
    knock = Knock.objects.filter(status=Knock.Status.OPEN).annotate(submits_count=Count('submits')).filter(submits_count__gt=0).order_by('?').first()

    if knock is None:
        raise CommandError('No available Knock Knocks to reserve.')

    worker = knock.submits.order_by('?').first()

    knock.status = Knock.Status.RESERVED
    knock.assigned_to = worker

    return knock, worker


class Command(BaseCommand):
    help = 'Fakes reserving a Knock Knock'

    def add_arguments(self, parser):
        parser.add_argument('-n', '--num', type=int, help='Fakes multiple reserves')

    def handle(self, *args, **kwargs):
        count = kwargs['num'] if kwargs['num'] else 1

        for idx in range(count):
            knock, worker = reserve_knock()
            knock.save()

            print(f'[{idx + 1}] Knock Knock {knock} reserved to {worker}')
