from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User, Group

from faker import Faker
from ...models import Profile
import random


class Command(BaseCommand):
    help = "Create a logged user"

    def add_arguments(self, parser):
        parser.add_argument("-n", "--num", type=int, help="Create multiple users")

    def handle(self, *args, **kwargs):
        try:
            test_users = Group.objects.get(name="Test Users")
        except Group.DoesNotExist:
            raise CommandError('"python3 manage.py init" command is required first.')

        count = kwargs["num"] if kwargs["num"] else 1

        faker = Faker(
            ["it_IT"]
        )  # https://faker.readthedocs.io/en/master/providers.html

        for idx in range(count):
            gender = random.choice(["M", "F"])

            user = User()

            if gender == "M":
                user.first_name = faker.first_name_male()
                user.last_name = faker.last_name_male()
            elif gender == "F":
                user.first_name = faker.first_name_female()
                user.last_name = faker.last_name_female()
            domain_name = faker.domain_name()

            user.username = f"{user.first_name[0].lower()}.{user.last_name.lower()}"

            user.email = f"{user.username}@{domain_name}"

            user.set_password("password")
            user.save()

            Profile(user=user, gender=gender).save()

            user.groups.add(test_users)
            user.save()

            print(f"[{idx + 1}] User {user.username} created.")
