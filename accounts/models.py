import secrets
import string

from django.contrib.auth.models import AbstractUser
from django.db import models

NICKNAME_LENGTH = 8
NICKNAME_MAX_LENGTH = 10


def generate_random_nickname():
    while True:
        candidate = "".join(secrets.choice(string.ascii_lowercase) for _ in range(NICKNAME_LENGTH))
        if not User.objects.filter(nickname=candidate).exists():
            return candidate


class User(AbstractUser):
    is_banned = models.BooleanField(default=False)
    is_dormant = models.BooleanField(default=False)
    nickname = models.CharField(max_length=NICKNAME_MAX_LENGTH, blank=True)
    bio = models.CharField(max_length=300, blank=True)
    profile_image = models.ImageField(upload_to="profiles/", blank=True, null=True)
    failed_attempts = models.PositiveIntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)
    balance = models.PositiveIntegerField(default=100000)
