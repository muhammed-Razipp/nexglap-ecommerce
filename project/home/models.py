from django.db import models

class Members (models.Model):
    username = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
