from django.contrib.auth import get_user_model
from django.db import models

from apps.shared.models import BaseModel
from apps.users.models.permissions import Permission

User = get_user_model()


class UserPermission(BaseModel):
    """
    Direct permissions assigned to specific users.
    These override or supplement role permissions.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_permissions_direct'
    )
    permission = models.ForeignKey(
        Permission,
        on_delete=models.CASCADE,
        related_name='user_assignments'
    )

    granted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='permissions_granted'
    )
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        unique_together = ['user', 'permission']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['is_active']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.permission.codename}"