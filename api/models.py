from django.db import models

# Create your models here.

class User(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(max_length=254)
    password = models.CharField(max_length=50)
    username = models.CharField(max_length=50)


class Owner(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(max_length=254)
    password = models.CharField(max_length=50)
    username = models.CharField(max_length=50)

class Shop(models.Model):
    Brand_name = models.CharField(max_length=50)
    work_email = models.EmailField(max_length=254)
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE)


class Cloth_type(models.Model):
    name = models.CharField(max_length=50)
    price = models.CharField(max_length=50)
    shop = models.ForeignKey(Shop, verbose_name=_(""), on_delete=models.CASCADE)


