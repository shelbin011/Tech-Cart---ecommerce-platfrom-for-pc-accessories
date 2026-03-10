from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    image = models.ImageField(upload_to='products/')
    stock = models.IntegerField()

    def __str__(self):
        return self.name
    

