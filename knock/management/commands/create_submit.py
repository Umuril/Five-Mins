# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from knock.models import Knock


def create_submit():
    knock = Knock.objects.filter(status=Knock.Status.OPEN).order_by('?').first()
    worker = get_user_model().objects.filter(groups__name='Test Users').order_by('?').first()
    while knock.requester.pk == worker.pk:
        worker = get_user_model().objects.filter(groups__name='Test Users').order_by('?').first()
    knock.submits.add(worker)

    return knock, worker


class Command(BaseCommand):
    help = 'Create a fake Submit'

    def add_arguments(self, parser):
        parser.add_argument('-n', '--num', type=int, help='Create multiple Submits')

    def handle(self, *args, **kwargs):
        count = kwargs['num'] if kwargs['num'] else 1

        for idx in range(count):
            knock, worker = create_submit()
            knock.save()

            print(f'[{idx + 1}] Submit for knock {knock} created by {worker}')
