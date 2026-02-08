from django.contrib.auth.models import AbstractUser
from django.db import models
from .managers import UserManager

class User(AbstractUser):
    username = None

    email = models.EmailField(unique=True)

    membership_tier = models.CharField(
        max_length=10,
        choices=[
            ('SILVER', 'Silver'),
            ('GOLD', 'Gold'),
            ('PLATINUM', 'Platinum'),
            ('BLACK', 'Black'),
        ],
        default='SILVER'
    )
    points = models.IntegerField(default=0)
    phone_number = models.CharField(max_length=20, blank=True)
    license_number = models.CharField(max_length=50, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email
