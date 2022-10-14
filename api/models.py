# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
import jwt
from datetime import datetime, timedelta
from django.conf import settings


SEX_CHOICES = (
    ('M', 'Male'),
    ('F', 'Female')
)


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Discount(models.Model):
    name = models.CharField(max_length=150)
    percent = models.IntegerField()
    allow_to_sum_with_promo = models.BooleanField()

    def __str__(self):
        return self.name


class ProductItem(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    count_on_stock = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='media/products', null=True, blank=True, default=None)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    discount = models.ForeignKey(Discount, on_delete=models.SET_NULL, null=True, default=None, blank=True)

    def __str__(self):
        return self.name


class Promocode(models.Model):
    name = models.CharField(max_length=50)
    percent = models.IntegerField()
    expire = models.DateTimeField()

    def __str__(self):
        return self.name


class UserManager(BaseUserManager):
    def create_user(self, password, phone=None,
                    is_admin=False, is_staff=False,
                    is_active=True, age=18, login='', weekly_discount_notif_required=True):

        if not phone:
            raise ValueError("User must have phone")
        if not password:
            raise ValueError("User must have a password")

        user = self.model(
            phone=phone
        )
        user.set_password(password)
        user.login = login
        user.age = age
        user.is_admin = is_admin
        user.is_staff = is_staff
        user.is_active = is_active
        user.is_superuser = False
        user.weekly_discount_notif_required = weekly_discount_notif_required
        user.save()

        return user

    def create_superuser(self, password, phone, email=None):
        if not phone:
            raise ValueError("User must have an phone")
        if not password:
            raise ValueError("User must have a password")

        user = self.create_user(password, phone, is_admin=True, is_staff=True, is_active=True)
        user.is_superuser = True
        user.is_staff = True
        user.save()
        return user


class RegistredUser(AbstractUser):
    username = None
    age = models.IntegerField()
    sex = models.CharField(choices=SEX_CHOICES, max_length=20, default='M')
    phone = models.CharField(max_length=20, unique=True)
    login = models.CharField(max_length=100, default='')
    weekly_discount_notif_required = models.BooleanField(default=True)
    cashback_points = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'phone'

    @property
    def token(self):
        return self._generate_jwt_token()

    def _generate_jwt_token(self):
        dt = datetime.now() + timedelta(days=1)

        token = jwt.encode({
            'id': self.pk,
            'exp': int(dt.strftime('%s'))
        }, settings.SECRET_KEY, algorithm='HS256')

        return token










