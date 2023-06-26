from django.contrib import admin
from main.models import Hand, Profile
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from main.models import Hand


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = "profiles"


class UserAdmin(BaseUserAdmin):
    list_display = [
        "username",
        "email",
        "first_name",
        "last_name",
        "submits_count",
        "requests_count",
        "works_count",
    ]
    inlines = [ProfileInline]

    def submits_count(self, obj):
        return obj.submits.count()

    def works_count(self, obj):
        return obj.works.count()

    def requests_count(self, obj):
        return obj.requests.count()


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(Hand)
class HandAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "requester",
        "status",
        "request_date",
        "request_start_time",
        "request_end_time",
        "assigned_to",
        "request_stars",
        "work_stars",
        "submit_count",
    ]

    def submit_count(self, obj):
        return obj.submits.count()
