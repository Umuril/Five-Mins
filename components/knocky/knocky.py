# -*- coding: utf-8 -*-
from django_components import component


@component.register('knocky')
class Knocky(component.Component):
    template_name = 'knocky/knocky.html'

    def get_context_data(self, *args, **kwargs):
        return kwargs

    class Media:
        # pylint: disable=too-few-public-methods
        css = 'knocky/knocky.css'
