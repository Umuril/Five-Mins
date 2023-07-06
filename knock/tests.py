# -*- coding: utf-8 -*-
import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.test.client import Client
from django.urls import reverse

from knock.models import Knock, Profile

# Create your tests here.


class ExampleTestCase(TestCase):
    def test_ok(self):
        self.assertEqual(1, 1)
        with self.assertRaises(ZeroDivisionError):
            return 1 / 0


class KnockTestCase(TestCase):
    def setUp(self):
        super_user = get_user_model().objects.create_user(username='root', password='toor')
        super_user.save()

        super_user.profile = Profile()
        super_user.profile.save()

        user = get_user_model().objects.create(username='pippo', password='pippo')
        user.save()

        user.profile = Profile()
        user.profile.save()

        Knock.objects.create(
            requester=super_user,
            request_date=datetime.date.today(),
            request_start_time=datetime.time(),
            request_end_time=datetime.datetime.now() + datetime.timedelta(minutes=5),
            assigned_to=user
        )

    def test_client(self):
        cli = Client()
        response = cli.get('/')
        self.assertEqual(200, response.status_code)
        last_updated_knocks = response.context['last_updated_knocks']
        self.assertIsNotNone(last_updated_knocks)

    def test_update_stars_on_users_profile(self):
        knock = Knock.objects.get(pk=1)
        cli = Client()
        cli.login(username='root', password='toor')
        response = cli.post(reverse('knock-rating', args=(knock.pk,)), {'rating': 3}, follow=True)
        self.assertEqual(3, response.context['knock'].requester.profile.work_stars)
