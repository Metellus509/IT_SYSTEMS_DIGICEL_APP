from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class DeviceAccountManager(models.Manager):
    def accessible_accounts(self, user):
        """
        Retourne les comptes accessibles à un utilisateur donné
        """
        if user.is_authenticated:
            return self.filter(
                Q(is_shared=True) | 
                Q(username=user.username, is_shared=False)
            )
        return self.none()

class DeviceType(models.TextChoices):
    SERVER = 'SERVER', 'Server'
    SWITCH = 'SWITCH', 'Switch'
    STORAGE = 'STORAGE', 'Storage'

class DeviceStatus(models.TextChoices):
    ACTIVE = 'ACTIVE', 'Active'
    INACTIVE = 'INACTIVE', 'Inactive'

class Device(models.Model):
    hostname = models.CharField(max_length=100, unique=True)
    ip_address = models.GenericIPAddressField(unique=True)
    location = models.CharField(max_length=200)
    device_type = models.CharField(
        max_length=20,
        choices=DeviceType.choices,
        default=DeviceType.SERVER
    )
    status = models.CharField(
        max_length=20,
        choices=DeviceStatus.choices,
        default=DeviceStatus.ACTIVE
    )
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='devices'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.hostname} ({self.ip_address})"

    class Meta:
        db_table = 'devices'
        ordering = ['-created_at']

class DeviceAccount(models.Model):
    device = models.ForeignKey(
        Device,
        on_delete=models.CASCADE,
        related_name='accounts'
    )
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=255)
    description = models.CharField(max_length=200, blank=True)
    
    # NOUVEAU CHAMP : shared account
    is_shared = models.BooleanField(default=False)
    
    # NOUVEAU CHAMP : propriétaire du compte (pour les comptes personnels)
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='personal_accounts'
    )
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_accounts'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        shared_status = "SHARED" if self.is_shared else "PERSONAL"
        return f"{self.username}@{self.device.hostname} ({shared_status})"

    objects = DeviceAccountManager()

    class Meta:
        db_table = 'device_accounts'
        unique_together = ['device', 'username', 'owner']  # Modifié
        ordering = ['username']