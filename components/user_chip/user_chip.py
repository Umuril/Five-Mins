# -*- coding: utf-8 -*-
from django_components import component


@component.register('user_chip')
class Knocky(component.Component):
    template_name = 'user_chip/user_chip.html'

    def get_context_data(self, *args, **kwargs):
        kwargs.setdefault('as_request', True)
        kwargs.setdefault('with_stars', True)
        return kwargs

    class Media:
        # pylint: disable=too-few-public-methods
        css = 'user_chip/user_chip.css'
