import hashlib
import os

from django.db import models

# Create your models here.
class User(models.Model):
    phone_number = models.CharField(max_length=50)
    password_hash = models.CharField(max_length=100)
    password_salt = models.CharField(max_length=50)
    status = models.IntegerField(default=0)

    def  __str__(self):
        return self.phone_number

class Order(models.Model):
    order_number = models.CharField(max_length=50)
    user_id = models.IntegerField()
    airline = models.CharField(max_length=100)
    key = models.CharField(max_length=50)
    status = models.IntegerField()

    def __str__(self):
        return self.order_number


