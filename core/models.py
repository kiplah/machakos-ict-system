from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=15, unique=True)
    role = models.CharField(max_length=30, choices=[
        ('admin', 'Admin'),
        ('ict', 'ICT Officer'),
        ('clerk', 'Clerk'),
    ])
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.username
class Asset(models.Model):
    ASSET_STATUS = [
        ('active', 'Active'),
        ('assigned', 'Assigned'),
        ('maintenance', 'Maintenance'),
        ('disposed', 'Disposed')
    ]

    name = models.CharField(max_length=100)
    type = models.CharField(max_length=100)
    acquisition_date = models.DateField()
    value = models.DecimalField(max_digits=12, decimal_places=2)
    condition = models.CharField(max_length=100, default="New")
    status = models.CharField(max_length=20, choices=ASSET_STATUS, default='active')
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    department = models.CharField(max_length=100, blank=True)
    assigned_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.name
class Maintenance(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='maintenance_logs')
    description = models.TextField()
    date = models.DateField()
    next_service = models.DateField(null=True, blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    performed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.asset.name} - {self.date}"
class AuditLog(models.Model):
    ACTION_TYPES = [
        ('user_approved', 'User Approved'),
        ('asset_created', 'Asset Created'),
        ('asset_assigned', 'Asset Assigned'),
        ('maintenance_logged', 'Maintenance Logged'),
    ]

    action = models.CharField(max_length=50, choices=ACTION_TYPES)
    performed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    description = models.TextField()

    def __str__(self):
        return f"{self.action} by {self.performed_by} on {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
