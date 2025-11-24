from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone

class CustomUserManager(BaseUserManager):  # ← Doit hériter de BaseUserManager
    def create_user(self, username, email, password=None, **extra_fields):
        """
        Create and return a regular user with an email and password.
        """
        if not email:
            raise ValueError('The Email field must be set')
        if not username:
            raise ValueError('The Username field must be set')
        
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        """
        Create and return a superuser with an email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(username, email, password, **extra_fields)

    def get_by_natural_key(self, username):
        """
        Required for authentication - get user by username
        """
        return self.get(username=username)

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Champs pour le soft delete
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    # Utiliser le manager personnalisé
    objects = CustomUserManager()
    

    def __str__(self):
        if self.is_deleted:
            return f"{self.username} (DELETED)"
        
        return self.username

    # def __str__(self):
    #     if self.is_deleted:
    #         return f"{self.first_name} {self.last_name} (DELETED)"
    #     return f"{self.first_name} {self.last_name} ({self.username})"
    
    def soft_delete(self):
        """Marquer l'utilisateur comme supprimé sans le supprimer réellement"""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        # Désactiver aussi le compte pour la connexion
        self.is_active = False
        self.save()
    
    def restore(self):
        """Restaurer un utilisateur supprimé"""
        self.is_deleted = False
        self.deleted_at = None
        self.is_active = True
        self.save()
    
    class Meta:
        db_table = 'auth_user'