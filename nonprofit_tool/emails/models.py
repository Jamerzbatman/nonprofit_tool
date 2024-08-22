from django.db import models

class EmailConfiguration(models.Model):
    smtp_server = models.CharField(max_length=255, default='smtp.gmail.com')
    smtp_port = models.PositiveIntegerField(default=587)
    use_tls = models.BooleanField(default=True)
    email_address = models.EmailField()
    email_password = models.CharField(max_length=255)  # Store this securely!

    def __str__(self):
        return f"{self.user.username}'s Email Configuration"