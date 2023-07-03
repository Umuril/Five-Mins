# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from knock.models import Knock, Profile


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'profiles'


class UserAdmin(BaseUserAdmin):
    list_display = [
        'username',
        'email',
        'first_name',
        'last_name',
        # 'submits_count',
        'requests_count',
        'works_count',
    ]
    inlines = [ProfileInline]

    # def submits_count(self, obj):
    #     return obj.submits.count()

    def works_count(self, obj):
        return obj.works.count()

    def requests_count(self, obj):
        return obj.requests.count()


admin.site.unregister(get_user_model())
admin.site.register(get_user_model(), UserAdmin)


@admin.register(Knock)
class KnockAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'requester',
        'status',
        'request_date',
        'request_start_time',
        'request_end_time',
        'assigned_to',
        'request_stars',
        'work_stars',
        'submit_count',
    ]

    def submit_count(self, obj):
        return obj.submits.count()
