from apps.users.models.users import User
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q


class MultiFieldBackend(ModelBackend):
    """
    Authentication backend that allows login with email, username, or phone_number
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Try to find user by email, username
            user = User.objects.get(
                Q(email__iexact=username) |
                Q(username__iexact=username) |
                Q(phone_number__iexact=username)
            )

            if user.check_password(password) and user.is_active:
                return user
        except User.DoesNotExist:
            pass
        return None