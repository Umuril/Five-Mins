# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from main.models import Knock, Profile


@receiver(pre_save, sender=Knock)
def both_have_rated(sender, instance, *args, **kwargs):
    # pylint: disable=unused-argument
    if instance.status == Knock.Status.DONE and instance.request_stars and instance.work_stars:
        instance.status = Knock.Status.CLOSED

    if instance.status == Knock.Status.OPEN and instance.assigned_to:
        instance.status = Knock.Status.RESERVED


@receiver(post_save, sender=get_user_model())
def create_profile(_sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=get_user_model())
def save_profile(_sender, instance, **kwargs):
    instance.profile.save()
