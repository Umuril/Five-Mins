from django.db import models
from django.contrib.auth.models import User
from djmoney.models.fields import MoneyField

class Hand(models.Model):
    title = models.CharField(max_length=50)
    description = models.CharField(null=True, blank=True, max_length=255)
    
    requester = models.ForeignKey(User, on_delete=models.PROTECT, related_name='requests')
    assigned_to = models.ForeignKey(User, null=True, blank=True, on_delete=models.PROTECT, related_name='works')
    status = models.IntegerField(null=True, blank=True)
    
    request_start_time = models.DateTimeField()
    request_duration = models.DurationField()
    request_location = models.CharField(null=True, blank=True, max_length=255) # FIXME
    request_price = MoneyField(null=True, blank=True, max_digits=6, decimal_places=2, default_currency='EUR', editable=True)
    
    stars = models.IntegerField(null=True, blank=True)

    creation_time = models.DateTimeField(null=False, editable=False, auto_now_add=True)
    over_time = models.DateTimeField(null=True, blank=True, editable=False)

    def __str__(self):
        return self.title + ' requested by ' + self.requester.username
    
