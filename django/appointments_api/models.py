from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Service(models.Model):
    name = models.CharField(max_length=100, null=False)
    address = models.CharField(max_length=255, null=False)
    doctor = models.ForeignKey(User, on_delete=models.CASCADE)

class Appointment(models.Model):
    scheduled_at = models.DecimalField(max_digits=20, decimal_places=6, null=False)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="assignations")
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="appointments")
