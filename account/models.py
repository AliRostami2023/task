from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import timedelta
from django.utils import timezone
import random
from .managers import UserManager


class User(AbstractUser):
    phone = models.CharField(max_length=15, unique=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    full_name = models.CharField(max_length=100)

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['username']

    objects = UserManager()


class OTP(models.Model):
    phone = models.CharField(max_length=15)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)


    def generate_code(self):
        self.code = str(random.randint(100000, 999999))
        self.save()

    def is_expired(self, valid_minutes=10):
        """
        بررسی می‌کند که آیا این OTP منقضی شده یا نه.
        """
        return timezone.now() - self.created_at > timedelta(minutes=valid_minutes)


class LoginAttempt(models.Model):
    ip_address = models.GenericIPAddressField()
    phone = models.CharField(max_length=15)
    is_successful = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def block_ip(cls, ip_address):
        return cls.objects.filter(ip_address=ip_address, created_at__gte=timezone.now() - timedelta(hours=1)).count() >= 3

    @classmethod
    def block_phone(cls, phone):
        return cls.objects.filter(phone=phone, created_at__gte=timezone.now() - timedelta(hours=1)).count() >= 3
