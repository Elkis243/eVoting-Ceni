from django.db import models
from django.contrib.auth.models import AbstractUser
class User(AbstractUser):
    username = models.CharField(max_length=50, unique=False, blank=True, null=True)
    email = models.EmailField(max_length=254, unique=True)
    user_type = models.CharField(max_length=50)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'user_type']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.email