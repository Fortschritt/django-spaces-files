from django.core.exceptions import PermissionDenied
from collab.util import is_owner_or_admin


def file_owner_or_admin_required(func):
    """
    method decorator raising 403 if user is neither the owner of the file
    nor a space administrator or manager.
    """
    def _decorator(self, *args, **kwargs):
        if self.request.user and self.request.user.is_authenticated:
            is_allowed = is_owner_or_admin(
                self.request.user, 
                self.get_object().created_by,
                self.request.SPACE
            )
            if is_allowed:
                return func(self, *args, **kwargs)
        raise PermissionDenied
    return _decorator
