from django.db import models
from django.contrib.auth import get_user_model

from phonenumber_field.modelfields import PhoneNumberField


User = get_user_model()

class PhoneNumber(models.Model):
    user = models.OneToOneField(User, related_name='phone', on_delete=models.CASCADE)
    phone_number = PhoneNumberField(unique=True)
    passcode = models.CharField(max_length=4, default='0000')
    verified = models.BooleanField(default=False)