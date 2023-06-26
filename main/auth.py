from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import Group, User


class PasswordlessTestBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        return User.objects.filter(groups__name="Test Users", username=username).first()

    def get_user(self, user_id):
        return User.objects.filter(groups__name="Test Users", pk=user_id).first()
