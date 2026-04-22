from datetime import timedelta

from django.core.validators import validate_ipv46_address
from django.db import models
from django.utils import timezone

from apps.shared.models import BaseModel, Language, DeviceType, DeviceTheme
from apps.users.models.users import User

class AppVersion(BaseModel):
    """
    Model to track app versions for analytics and compatibility checks.
    Devices can link to this to know which app version they're using.
    """
    version_number = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        help_text="App version number (e.g., 1.0.0)"
    )
    release_date = models.DateField(
        null=True,
        blank=True,
        help_text="When this app version was released"
    )
    changelog = models.TextField(
        null=True,
        blank=True,
        help_text="Changelog or release notes for this version"
    )

    class Meta:
        db_table = 'app_versions'
        verbose_name = 'App Version'
        verbose_name_plural = 'App Versions'
        ordering = ['-release_date', '-created_at']
        indexes = [
            models.Index(fields=['version_number'], name='app_version_number_idx'),
            models.Index(fields=['release_date'], name='app_version_release_date_idx'),
        ]

    def __str__(self):
        return f"Version {self.version_number} ({self.release_date})"


class Device(BaseModel):
    """
    Model to track user devices and manage per-device sessions.
    Each device has its own refresh token managed via JTI.
    """
    # Device Information
    device_model = models.CharField(max_length=255, db_index=True)
    operation_version = models.CharField(max_length=155)
    device_type = models.CharField(
        max_length=7,
        choices=DeviceType.choices,
        default=DeviceType.ANDROID,
        db_index=True
    )
    device_id = models.CharField(
        max_length=255,
        db_index=True,
        help_text="Unique device identifier (UUID from mobile app)"
    )
    ip_address = models.GenericIPAddressField(
        validators=[validate_ipv46_address],
        help_text="IP address of the device"
    )
    last_login = models.DateTimeField(auto_now=True, db_index=True)
    first_login = models.DateTimeField(auto_now_add=True)
    visit_location = models.JSONField(
        null=True,
        blank=True,
        help_text="Geographic location data"
    )

    # User Preferences
    language = models.CharField(
        max_length=3,
        choices=Language.choices,
        default=Language.CRL
    )
    theme = models.CharField(
        max_length=5,
        choices=DeviceTheme.choices,
        default=DeviceTheme.LIGHT
    )

    # Status Flags
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Device session is active"
    )
    is_push_notification = models.BooleanField(
        default=True,
        verbose_name="Push Notifications Enabled"
    )
    is_auth_password = models.BooleanField(
        default=False,
        verbose_name="Biometric Authentication Enabled"
    )

    # Session Management - Critical for per-device logout
    refresh_token_jti = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
        help_text="JWT refresh token JTI (JWT ID) for this device session"
    )
    refresh_token_expires_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        help_text="When the refresh token expires"
    )
    logged_out_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When user logged out from this device"
    )

    # Firebase Push Notifications
    firebase_token = models.CharField(
        max_length=500,
        unique=True,
        null=True,
        blank=True,
        db_index=True
    )

    # Relationships
    app_version = models.ForeignKey(
        AppVersion,
        on_delete=models.PROTECT,
        related_name='devices',
        db_index=True
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="devices",
        db_index=True
    )

    class Meta:
        db_table = 'devices'
        verbose_name = 'Device'
        verbose_name_plural = 'Devices'
        ordering = ['-last_login']
        indexes = [
            models.Index(fields=['user', 'is_active'], name='device_user_active_idx'),
            models.Index(fields=['device_id', 'device_type'], name='device_id_type_idx'),
            models.Index(fields=['refresh_token_jti', 'is_active'], name='device_token_active_idx'),
            models.Index(fields=['-last_login'], name='device_last_login_idx'),
            models.Index(
                fields=['refresh_token_jti', 'is_active', 'refresh_token_expires_at'],
                name='device_token_validation_idx'
            ),
        ]

    def __str__(self):
        user_info = f"{self.user.username}" if self.user else "Anonymous"
        status = "Active" if self.is_active else "Logged Out"
        return f"{user_info} - {self.device_type} ({self.device_model}) [{status}]"

    def logout(self):
        """
        Logout from this specific device.
        Marks device as inactive and records logout time.
        This effectively invalidates the refresh token.
        """
        self.is_active = False
        self.logged_out_at = timezone.now()
        self.save(update_fields=['is_active', 'logged_out_at'])

    def refresh_session(self, new_refresh_token_jti, expires_at=None):
        """
        Update device session with new refresh token JTI.
        Called when refresh token is rotated.

        Args:
            new_refresh_token_jti: The new JWT ID for the refresh token
            expires_at: When the token expires (default: 30 days from now)
        """
        if expires_at is None:
            expires_at = timezone.now() + timedelta(days=30)

        self.refresh_token_jti = new_refresh_token_jti
        self.refresh_token_expires_at = expires_at
        self.is_active = True
        self.logged_out_at = None
        self.save(update_fields=[
            'refresh_token_jti',
            'refresh_token_expires_at',
            'is_active',
            'logged_out_at',
            'last_login'
        ])

    def update_firebase_token(self, token):
        """Update firebase token for push notifications"""
        self.firebase_token = token
        self.save(update_fields=['firebase_token'])

    @classmethod
    def get_active_devices(cls, user):
        """Get all active devices for a user"""
        return cls.objects.filter(
            user=user,
            is_active=True,
            refresh_token_expires_at__gt=timezone.now()
        ).order_by('-last_login')

    @classmethod
    def logout_all_devices(cls, user):
        """Logout from all devices for a user"""
        return cls.objects.filter(user=user, is_active=True).update(
            is_active=False,
            logged_out_at=timezone.now()
        )

    @classmethod
    def logout_other_devices(cls, user, current_device_id):
        """Logout from all devices except current one"""
        return cls.objects.filter(
            user=user,
            is_active=True
        ).exclude(
            id=current_device_id
        ).update(
            is_active=False,
            logged_out_at=timezone.now()
        )

    @classmethod
    def is_token_valid(cls, refresh_token_jti):
        """
        Check if refresh token JTI is valid.
        Token is valid if device is active AND token hasn't expired.
        """
        return cls.objects.filter(
            refresh_token_jti=refresh_token_jti,
            is_active=True,
            refresh_token_expires_at__gt=timezone.now()
        ).exists()

    @classmethod
    def get_by_valid_token(cls, refresh_token_jti):
        """
        Get device by refresh token JTI if valid.
        Returns None if token is invalid or expired.
        """
        try:
            return cls.objects.get(
                refresh_token_jti=refresh_token_jti,
                is_active=True,
                refresh_token_expires_at__gt=timezone.now()
            )
        except cls.DoesNotExist:
            return None

    @classmethod
    def cleanup_expired_sessions(cls):
        """
        Remove expired and old inactive sessions.
        Should be run periodically (e.g., daily cron job).

        Deletes:
        - Sessions with expired refresh tokens
        - Sessions that have been logged out for more than 30 days
        """
        old_logout_threshold = timezone.now() - timedelta(days=30)

        return cls.objects.filter(
            models.Q(refresh_token_expires_at__lt=timezone.now()) |
            models.Q(is_active=False, logged_out_at__lt=old_logout_threshold)
        ).delete()

    @property
    def is_logged_in(self):
        """Check if device currently has active session"""
        return (
                self.is_active and
                self.logged_out_at is None and
                self.refresh_token_expires_at and
                self.refresh_token_expires_at > timezone.now()
        )

    @property
    def is_token_expired(self):
        """Check if refresh token has expired"""
        if not self.refresh_token_expires_at:
            return True
        return self.refresh_token_expires_at <= timezone.now()

    @property
    def session_duration(self):
        """Calculate how long the session has been active"""
        if self.logged_out_at:
            return self.logged_out_at - self.first_login
        return timezone.now() - self.first_login

    @property
    def display_name(self):
        """Friendly display name for the device"""
        return f"{self.get_device_type_display()} - {self.device_model}"


class TokenBlocklist(BaseModel):
    """
    Blocklist for access tokens (JWTs) that were logged out before natural expiry.

    Note: Refresh tokens are NOT stored here - they're managed via Device.is_active flag.
    This model only handles access tokens that need to be invalidated immediately.

    Tokens are automatically cleaned up after they expire naturally.
    """
    jti = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
        help_text="JWT ID (jti claim) of the access token"
    )
    expires_at = models.DateTimeField(
        db_index=True,
        help_text="When the access token expires naturally (for auto-cleanup)"
    )
    blocked_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the token was added to blocklist"
    )
    reason = models.CharField(
        max_length=50,
        default='logout',
        help_text="Reason for blocking (logout, password_change, etc.)"
    )

    # Optional: Track which device/user this token belonged to
    device = models.ForeignKey(
        Device,
        on_delete=models.CASCADE,
        related_name='blocked_tokens',
        null=True,
        blank=True,
        help_text="Device this token was issued to"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='blocked_tokens',
        null=True,
        blank=True,
        help_text="User this token was issued to"
    )

    class Meta:
        db_table = 'token_blocklist'
        verbose_name = 'Blocked Token'
        verbose_name_plural = 'Blocked Tokens'
        ordering = ['-blocked_at']
        indexes = [
            models.Index(fields=['jti', 'expires_at'], name='blocklist_lookup_idx'),
            models.Index(fields=['expires_at'], name='blocklist_expiry_idx'),
            models.Index(fields=['user', '-blocked_at'], name='blocklist_user_idx'),
        ]

    def __str__(self):
        user_info = f"{self.user.username}" if self.user else "Unknown"
        return f"Blocked token for {user_info} - {self.reason}"

    @classmethod
    def block_token(cls, jti, expires_at, device=None, user=None, reason='logout'):
        """
        Add an access token to the blocklist.

        Args:
            jti: JWT ID of the access token
            expires_at: When the token expires
            device: Device object (optional)
            user: User object (optional)
            reason: Reason for blocking
        """
        return cls.objects.create(
            jti=jti,
            expires_at=expires_at,
            device=device,
            user=user,
            reason=reason
        )

    @classmethod
    def is_blocked(cls, jti):
        """
        Check if an access token is blocked.
        Only checks non-expired tokens (expired tokens are automatically invalid anyway).
        """
        return cls.objects.filter(
            jti=jti,
            expires_at__gt=timezone.now()
        ).exists()

    @classmethod
    def cleanup_expired(cls):
        """
        Remove expired tokens from blocklist.
        Should be run periodically (e.g., hourly cron job).

        Returns the count of deleted tokens.
        """
        result = cls.objects.filter(expires_at__lt=timezone.now()).delete()
        return result[0]  # Returns count of deleted objects

    @classmethod
    def block_all_user_tokens(cls, user, reason='security'):
        """
        Block all active tokens for a user.
        Useful for password changes, account security issues, etc.

        Note: This won't actually know all active JTIs unless you track them.
        Better approach is to logout all devices via Device.logout_all_devices()
        """
        # Get all active devices for user
        active_devices = Device.objects.filter(user=user, is_active=True)

        # Logout all devices (which invalidates refresh tokens)
        Device.logout_all_devices(user)

        return active_devices.count()

    @classmethod
    def get_user_blocked_tokens(cls, user, limit=10):
        """Get recent blocked tokens for a user"""
        return cls.objects.filter(user=user).order_by('-blocked_at')[:limit]

    @property
    def is_expired(self):
        """Check if the blocked token has already expired naturally"""
        return self.expires_at <= timezone.now()

    @property
    def time_until_expiry(self):
        """Time remaining until token expires naturally"""
        if self.is_expired:
            return timedelta(0)
        return self.expires_at - timezone.now()