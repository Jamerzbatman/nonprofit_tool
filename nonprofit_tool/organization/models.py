from django.core.validators import EmailValidator, RegexValidator
from django.contrib.auth.models import User
from django.db import models

class Organization(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, blank=True, null=True, validators=[EmailValidator()])
    website = models.URLField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(
        max_length=20, 
        blank=True, 
        null=True, 
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")]
    )
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
