import logging
from datetime import timedelta

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.cache import cache
from django.db import models
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken

from apps.shared.models import BaseModel, Language
from apps.users.models.permissions import Role, Permission

logger = logging.getLogger(__name__)


class UserManager(BaseUserManager):
    """
    Custom manager for the User model.
    Handles user creation with flexible authentication fields.
    """

    def create_user(self, phone_number=None, password=None, **extra_fields):
        if not phone_number:
            raise ValueError('The username field must be set')
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username=None, password=None, **extra_fields):
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is False:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is False:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(username, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin, BaseModel):
    """
    Custom user model with flexible authentication fields
    """
    roles = models.ManyToManyField(
        Role,
        related_name='users'
    )

    phone_number = models.CharField(
        max_length=20, unique=True, db_index=True
    )
    email = models.EmailField(
        max_length=255, unique=True, null=True,
        blank=True, db_index=True
    )

    username = models.CharField(
        max_length=150, unique=True, null=True,
        blank=True, db_index=True
    )

    # Profile fields
    first_name = models.CharField(max_length=64, blank=True, null=True)
    last_name = models.CharField(max_length=64, blank=True, null=True)
    middle_name = models.CharField(max_length=64, blank=True, null=True)

    # Status fields
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    language = models.CharField(
        choices=Language, max_length=5, default=Language.EN
    )

    objects = UserManager()

    # This field is used for authentication
    USERNAME_FIELD = 'phone_number'  # Default to username, but can authenticate with any
    REQUIRED_FIELDS = []  # No required fields since we have flexible auth

    def get_tokens(self, access_lifetime=None, refresh_lifetime=None):
        """Generate JWT tokens for the user with optional custom expiration"""
        refresh = RefreshToken.for_user(self)

        # Set custom lifetimes if provided
        if access_lifetime:
            refresh.access_token.set_exp(lifetime=access_lifetime)
        if refresh_lifetime:
            refresh.set_exp(lifetime=refresh_lifetime)

        # Add custom claims
        refresh['user_id'] = self.id

        expires_at = timezone.now() + timedelta(seconds=refresh.access_token.lifetime.total_seconds())
        refresh_expires_at = timezone.now() + timedelta(seconds=refresh.lifetime.total_seconds())

        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'token_type': 'Bearer',
            'expires_at': expires_at.isoformat(),
            'refresh_expires_at': refresh_expires_at.isoformat(),
        }

    def has_permission(self, permission_codename):
        """Check if user has a specific permission (with caching)"""
        if self.is_superuser:
            return True

        # Check cache first
        cache_key = f'user_{self.id}_perms'
        cached_perms = cache.get(cache_key)

        if cached_perms is None:
            cached_perms = self._load_permissions()
            cache.set(cache_key, cached_perms, timeout=None)

        return permission_codename in cached_perms

    def _load_permissions(self):
        """Load all permission codenames from database"""
        perms = set()
        for role in self.roles.filter(is_active=True):
            for perm in role.get_all_permissions():
                perms.add(perm.codename)
        for perm in self.user_permissions_direct.all():
            perms.add(perm.permission.codename)
        return perms

    def get_all_permissions_list(self):
        """
        Get all permissions from all active roles
        Returns a list of Permission objects
        """
        if self.is_superuser:
            return list(Permission.objects.all())

        all_perms = set()
        for role in self.roles.filter(is_active=True):
            all_perms.update(role.get_all_permissions())
        return list(all_perms)

    def clear_permission_cache(self):
        """Clear cached permissions"""
        cache_key = f'user_{self.id}_perms'
        cache.delete(cache_key)

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'


class VerificationCode(BaseModel):
    """
    Model to store verification codes for user authentication
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='verification_codes')
    code = models.CharField(max_length=6)
    expiration_seconds = models.PositiveSmallIntegerField(default=120)

    class Meta:
        db_table = 'verification_codes'
        verbose_name = 'Verification Code'
        verbose_name_plural = 'Verification Codes'