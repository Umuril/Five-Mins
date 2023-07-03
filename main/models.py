# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import F, Q
from django.urls import reverse
from djmoney.models.fields import MoneyField
from PIL import Image

GENDER_CHOICES = [
    ('M', 'Male'),
    ('F', 'Female'),
]


# https://docs.djangoproject.com/en/4.2/topics/auth/customizing/#extending-user
class Profile(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, primary_key=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        img = Image.open(self.image.path)  # Open image

        # resize image
        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)  # Resize image
            img.save(self.image.path)  # Save it again and override the larger image


class Knock(models.Model):
    # pylint: disable=too-many-instance-attributes

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

    class Category(models.TextChoices):
        BUY = 'Buy', 'Buy'
        DO = 'Do', 'Do'
        MEET = 'Meet', 'Meet'

    title = models.CharField(max_length=50)
    description = models.CharField(null=True, blank=True, max_length=255)
    category = models.CharField(max_length=20, choices=Category.choices)

    requester = models.ForeignKey(get_user_model(), on_delete=models.PROTECT, related_name='requests')
    status = models.CharField(max_length=1, choices=Status.choices, default=Status.OPEN)

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

    assigned_to = models.ForeignKey(get_user_model(), null=True, blank=True, on_delete=models.PROTECT, related_name='works')

    request_stars = models.IntegerField(null=True, blank=True, choices=StarsAnswer.choices)
    work_stars = models.IntegerField(null=True, blank=True, choices=StarsAnswer.choices)

    creation_time = models.DateTimeField(null=False, editable=False, auto_now_add=True)

    update_time = models.DateTimeField(null=False, editable=False, auto_now=True)

    submits = models.ManyToManyField(get_user_model(), through='KnockSubmit')

    def __str__(self):
        desc_str = f'[{self.category.upper()}] ' if self.category else ''
        desc_str += f"'{self.title}' requested by {self.requester}"
        time_str = f'from {self.request_start_time} to {self.request_end_time}'
        price_str = f'paying {self.request_price}' if self.request_price else ''
        return f'{desc_str} for day {self.request_date} {time_str} {price_str}'

    def get_absolute_url(self):
        return reverse('knock-detail', kwargs={'pk': self.pk})

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=Q(
                    request_start_time__lt=F('request_end_time')),
                name='request_start_time must be less than request_end_time',
            )]


class KnockSubmit(models.Model):
    knock = models.ForeignKey(Knock, on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    submit_time = models.DateTimeField(null=False, editable=False, auto_now_add=True)


class KnockChat(models.Model):
    class Status(models.TextChoices):
        OPEN = 'O', 'Open'
        CLOSED = 'C', 'Closed'

    knock = models.ForeignKey(Knock, on_delete=models.CASCADE, related_name='chats')
    user = models.ForeignKey(get_user_model(), on_delete=models.DO_NOTHING, related_name='chats')
    creation_time = models.DateTimeField(null=False, editable=False, auto_now_add=True)
    status = models.CharField(max_length=1, choices=Status.choices, default=Status.OPEN)

    def __str__(self):
        return f'Chat with {self.user}'


class KnockChatMessage(models.Model):
    chat = models.ForeignKey(KnockChat, on_delete=models.CASCADE, related_name='messages')
    timestamp = models.DateTimeField(null=False, editable=False, auto_now_add=True)
    sender = models.ForeignKey(get_user_model(), on_delete=models.DO_NOTHING, related_name='+')
    receiver = models.ForeignKey(get_user_model(), on_delete=models.DO_NOTHING, related_name='+')
    text = models.CharField(max_length=1024)

    def __str__(self):
        return f'{self.timestamp} - {self.sender} - {self.text}'
