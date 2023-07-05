# -*- coding: utf-8 -*-
from django_components import component

from knock.models import Knock


@component.register('status')
class Status(component.Component):
    template_name = 'status/status.html'

    def get_context_data(self, *args, **kwargs):
        mapping = {
            Knock.Status.OPEN: 1,
            Knock.Status.RESERVED: 2,
            Knock.Status.IN_PROGRESS: 3,
            Knock.Status.DONE: 4,
            Knock.Status.CLOSED: 5,
        }
        kwargs['num'] = mapping[kwargs['status']]
        return kwargs

    class Media:
        # pylint: disable=too-few-public-methods
        css = 'status/status.css'
