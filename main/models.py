# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import F, Q
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.urls import reverse
from djmoney.models.fields import MoneyField

GENDER_CHOICES = [
    ('M', 'Male'),
    ('F', 'Female'),
]


# https://docs.djangoproject.com/en/4.2/topics/auth/customizing/#extending-user
class Profile(models.Model):
    user = models.OneToOneField(
        get_user_model(), on_delete=models.CASCADE, primary_key=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)


class Hand(models.Model):
    class Status(models.TextChoices):
        OPEN = 'O', 'Open'
        RESERVED = 'R', 'Reserved'
        IN_PROGRESS = 'I', 'In Progress'
        DONE = 'D', 'Done'
        CLOSED = 'C', 'Closed'

    class StarsAnswer(models.IntegerChoices):
        EXCELLENT = 5, 'Excellent'
        ABOVE_AVERAGE = 4, 'Above average'
        AVERAGE = 3, 'Average'
        BELOW_AVERAGE = 2, 'Below average'
        POOR = 1, 'Poor'

    title = models.CharField(max_length=50)
    description = models.CharField(null=True, blank=True, max_length=255)

    requester = models.ForeignKey(
        get_user_model(), on_delete=models.PROTECT, related_name='requests'
    )
    status = models.CharField(
        max_length=1, choices=Status.choices, default=Status.OPEN)

    request_date = models.DateField()
    request_start_time = models.TimeField()
    request_end_time = models.TimeField()

    request_price = MoneyField(
        null=True,
        blank=True,
        max_digits=6,
        decimal_places=2,
        default_currency='EUR',
        editable=True,
    )

    assigned_to = models.ForeignKey(
        get_user_model(), null=True, blank=True, on_delete=models.PROTECT, related_name='works'
    )

    request_stars = models.IntegerField(
        null=True, blank=True, choices=StarsAnswer.choices
    )
    work_stars = models.IntegerField(
        null=True, blank=True, choices=StarsAnswer.choices)

    creation_time = models.DateTimeField(
        null=False, editable=False, auto_now_add=True)

    submits = models.ManyToManyField(get_user_model(), related_name='submits')

    def __str__(self):
        desc_str = f"'{self.title}' requested by {self.requester.username}"
        time_str = f'from {self.request_start_time} to {self.request_end_time}'
        return f'{desc_str} for day {self.request_date} {time_str} paying {self.request_price}'

    def get_absolute_url(self):
        return reverse('hand-detail', kwargs={'pk': self.pk})

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=Q(request_start_time__lt=F('request_end_time')),
                name='request_start_time must be less than request_end_time',
            )
        ]


@receiver(pre_save, sender=Hand)
def both_have_rated(sender, instance, *args, **kwargs):
    # pylint: disable=unused-argument
    if (
        instance.status == Hand.Status.DONE
        and instance.request_stars
        and instance.work_stars
    ):
        instance.status = Hand.Status.CLOSED
