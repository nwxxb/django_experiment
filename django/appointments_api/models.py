from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Service(models.Model):
    name = models.CharField(max_length=100, null=False)
    address = models.CharField(max_length=255, null=False)
    doctor = models.ForeignKey(User, on_delete=models.CASCADE)
