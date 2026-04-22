from django.db import models

from apps.shared.models import BaseModel


class Permission(BaseModel):
    """Base permissions"""
    name = models.CharField(max_length=100, unique=True)
    codename = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='children'
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_all_permissions(self):
        """Get this permission and all child permissions"""
        perms = [self]
        for child in self.children.all():
            perms.extend(child.get_all_permissions())
        return perms


class Endpoint(BaseModel):
    """Store all API endpoints in database"""
    HTTP_METHODS = [
        ('GET', 'GET'),
        ('POST', 'POST'),
        ('PUT', 'PUT'),
        ('PATCH', 'PATCH'),
        ('DELETE', 'DELETE'),
    ]
    ACCESS_TYPES = [
        ('public', 'Public'),  # Anyone can access (no authentication)
        ('authenticated', 'Authenticated'),  # Any authenticated user can access
        ('permission', 'Permission Required'),  # Requires specific permission
    ]

    path = models.CharField(max_length=255, help_text="e.g., /api/products/ or /api/users/{id}/")
    method = models.CharField(max_length=10, choices=HTTP_METHODS)
    name = models.CharField(max_length=100, help_text="Human readable name")
    description = models.TextField(blank=True)
    permission = models.ForeignKey(
        Permission,
        on_delete=models.SET_NULL,
        null=True,
        related_name='endpoints',
        help_text="Permission required to access this endpoint"
    )
    access_type = models.CharField(
        max_length=20,
        choices=ACCESS_TYPES,
        default='permission',
        db_index=True,
        help_text="Access control type for this endpoint"
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ['path', 'method']
        ordering = ['path', 'method']

    def __str__(self):
        return f"{self.method} {self.path}"

    @classmethod
    def check_access(cls, user, path, method):
        """Check if user can access this endpoint"""
        if user.is_superuser:
            return True

        # Try to find matching endpoint

        endpoint = cls.objects.filter(
            path=path,
            method=method.upper(),
            is_active=True
        ).select_related('permission').first()
        # If endpoint not found or no permission required, allow access
        if not endpoint or not endpoint.permission:
            return False

        # Check if user has the required permission
        return user.has_permission(endpoint.permission.codename)


class Role(BaseModel):
    """Roles that group permissions"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    permissions = models.ManyToManyField(Permission, related_name='roles')
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_all_permissions(self):
        """Get all permissions including hierarchical ones"""
        all_perms = set()
        for perm in self.permissions.all():
            all_perms.update(perm.get_all_permissions())
        return list(all_perms)