from django.db import models
import datetime
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.db.models import CASCADE
from django.utils import timezone


class Customer(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    first_name=models.CharField(max_length=50)
    last_name=models.CharField(max_length=50)
    location=models.CharField(max_length=200,null=True, blank=True)
    city=models.CharField(max_length=200)
    pincode=models.IntegerField(null=True, blank=True)
    phone=models.CharField(max_length=10,null=True, blank=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'
