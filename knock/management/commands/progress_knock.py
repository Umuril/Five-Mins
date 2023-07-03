# -*- coding: utf-8 -*-
from datetime import date, datetime

from django.core.management.base import BaseCommand, CommandError
from faker import Faker

from knock.models import Knock


def progress_knock(faker, option):
    if option == 'wip':
        knock = Knock.objects.filter(
            status=Knock.Status.RESERVED).order_by('?').first()
        if knock is None:
            raise CommandError('No available Knock Knocks to progress.')

        knock.status = Knock.Status.IN_PROGRESS
        knock.request_date = date.today()

        while knock.request_start_time >= datetime.now().time():
            knock.request_start_time = faker.time_object().replace(second=0, microsecond=0)

        while knock.request_end_time <= datetime.now().time():
            knock.request_end_time = faker.time_object().replace(second=0, microsecond=0)
    elif option == 'done':
        knock = Knock.objects.filter(status__in=[Knock.Status.RESERVED, Knock.Status.IN_PROGRESS]).order_by('?').first()

        if knock is None:
            raise CommandError('No available Knock Knocks to progress.')

        knock.status = Knock.Status.DONE
        knock.request_date = faker.past_date()
    else:
        raise CommandError('Unexpecter option on progress_knock.')

    return knock


class Command(BaseCommand):
    help = 'Fakes a Knock Knock to be In Progress or Done'

    def add_arguments(self, parser):
        parser.add_argument('-i', '--wip', action='store_true', help='Status Work In Progress')
        parser.add_argument('-d', '--done', action='store_true', help='Status Done')
        parser.add_argument('-n', '--num', type=int, help='Applies to multiple Knock Knocks')

    def handle(self, *args, **kwargs):
        if not kwargs['wip'] ^ kwargs['done']:
            raise CommandError('Choose one option between --wip or --done.')
        option = 'wip' if kwargs['wip'] else 'done'
        count = kwargs['num'] if kwargs['num'] else 1

        faker = Faker(['it_IT'])  # https://faker.readthedocs.io/en/master/providers.html

        for idx in range(count):
            knock = progress_knock(faker, option)
            knock.save()

            print(f'[{idx + 1}] Knock Knock {knock} status changed to {knock.get_status_display().upper()}')
