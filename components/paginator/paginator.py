# -*- coding: utf-8 -*-
from django_components import component


@component.register('paginator')
class Paginator(component.Component):
    template_name = 'paginator/paginator.html'

    def get_context_data(self, *args, **kwargs):
        kwargs.setdefault('url_params', '')
        return kwargs
