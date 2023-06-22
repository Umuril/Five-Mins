from django.db import models
from django.contrib.auth.models import User, AbstractUser
from djmoney.models.fields import MoneyField
from django.db.models import Q, F
from django.db.models.signals import pre_save
from django.dispatch import receiver

GENDER_CHOICES = [
    ("M", "Male"),
    ("F", "Female"),
]

# https://docs.djangoproject.com/en/4.2/topics/auth/customizing/#extending-user
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)


class Hand(models.Model):
    class Status(models.TextChoices):
        OPEN = "O", "Open"
        RESERVED = "R", "Reserved"
        IN_PROGRESS = "I", "In Progress"
        DONE = "D", "Done"
        CLOSED = "C", "Closed"

    class StarsAnswer(models.IntegerChoices):
        EXCELLENT = 5, "Excellent"
        ABOVE_AVERAGE = 4, "Above average"
        AVERAGE = 3, "Average"
        BELOW_AVERAGE = 2, "Below average"
        POOR = 1, "Poor"

    title = models.CharField(max_length=50)
    description = models.CharField(null=True, blank=True, max_length=255)
    
    requester = models.ForeignKey(User, on_delete=models.PROTECT, related_name='requests')
    status = models.CharField(max_length=1, choices=Status.choices, default=Status.OPEN)
    
    request_date = models.DateField()
    request_start_time = models.TimeField()
    request_end_time = models.TimeField()
    # request_duration = models.DurationField()

    request_location = models.CharField(null=True, blank=True, max_length=255) # FIXME
    request_price = MoneyField(null=True, blank=True, max_digits=6, decimal_places=2, default_currency='EUR', editable=True)
    
    assigned_to = models.ForeignKey(User, null=True, blank=True, on_delete=models.PROTECT, related_name='works')
    
    request_stars = models.IntegerField(null=True, blank=True, choices=StarsAnswer.choices)
    work_stars = models.IntegerField(null=True, blank=True, choices=StarsAnswer.choices)

    creation_time = models.DateTimeField(null=False, editable=False, auto_now_add=True)

    submits = models.ManyToManyField(User, related_name='submits')

    def __str__(self):
        return self.title + ' requested by ' + self.requester.username

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=Q(request_start_time__lt=F('request_end_time')),
                name = "request_start_time must be less than request_end_time"
            )
    ]

@receiver(pre_save, sender=Hand)
def both_have_rated(sender, instance, *args, **kwargs):
    if instance.status == Hand.Status.DONE and instance.request_stars and instance.work_stars:
        instance.status = Hand.Status.CLOSED
