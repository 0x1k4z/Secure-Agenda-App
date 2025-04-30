from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.base_user import BaseUserManager
from argon2 import PasswordHasher
from hashlib import sha256
from django.db import models

class CustomUserManager(BaseUserManager):
    def create_user(self, username, displayname, private_key, public_key, tag, nonce, **extra_fields):
        if not username or not displayname:
            raise ValueError(('Username, password and display name must be set'))
        user = self.model(username=username, displayname=displayname, private_key=private_key,
                         public_key=public_key, tag=tag, nonce=nonce)
        return user

class CustomUser(AbstractBaseUser):
    username = models.CharField(max_length=64, unique=True)
    displayname = models.OneToOneField('UserDisplayName', on_delete=models.CASCADE, unique=True)
    public_key = models.TextField(max_length=500000)
    private_key = models.TextField(max_length=500000)
    tag = models.CharField(max_length=1000000, default="")
    nonce = models.CharField(max_length=10000, default="")
    challenge = models.CharField(max_length=10, default="")

    password = None
    last_login = None
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['password', 'displayname', 'public_key', 'private_key']

    objects = CustomUserManager()

    def __str__(self):
        return self.username

class UserDisplayName(models.Model):
    displayName = models.CharField(max_length=64, unique=True)