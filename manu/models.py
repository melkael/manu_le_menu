from django.db import models


# Create your models here.
class Restaurant(models.Model):
    category = models.CharField(max_length=200)
    price = models.IntegerField()
    phone = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    arrondissement = models.IntegerField()
    name = models.CharField(max_length=200)
    score = models.FloatField()
    neighborhood = models.CharField(max_length=200)
