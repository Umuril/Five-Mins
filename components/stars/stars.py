# -*- coding: utf-8 -*-
from django_components import component


@component.register('stars')
class Stars(component.Component):
    template_name = 'stars/stars.html'

    def get_context_data(self, *args, **kwargs):
        return kwargs

    class Media:
        # pylint: disable=too-few-public-methods
        css = 'stars/stars.css'
