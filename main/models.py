from django.db import models
from django.contrib.auth.models import User
from djmoney.models.fields import MoneyField

class Job(models.Model):
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=255)
    
    requester = models.ForeignKey(User, on_delete=models.PROTECT, related_name='requests')
    assigned_to = models.ForeignKey(User, on_delete=models.PROTECT, related_name='works')
    status = models.IntegerField(null=False)
    
    request_start_time = models.DateTimeField()
    request_duration = models.DurationField()
    request_location = models.CharField(max_length=255) # FIXME
    request_price = MoneyField(max_digits=6, decimal_places=2, default_currency='EUR', editable=True)
    
    stars = models.IntegerField(null=True)

    creation_time = models.DateTimeField(null=False, editable=False)
    over_time = models.DateTimeField(null=True, editable=False)
