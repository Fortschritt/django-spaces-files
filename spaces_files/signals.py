import os
from django.conf import settings
from django.db import models
#from django.dispatch import receiver
from django.utils.translation import ugettext_noop as _
#from .models import File

# These two auto-delete files from filesystem when they are unneeded:
#@receiver(models.signals.post_delete, sender=File)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `File` object is deleted.
    """
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)



def create_notice_types(sender, **kwargs):
    if "pinax.notifications" in settings.INSTALLED_APPS:
        from spaces_notifications.utils import register_notification
        register_notification(
            'spaces_files_file_create',
            _('A new file has been uploaded.'),
            _('A new file has been uploaded.')
        )
        register_notification(
            'spaces_files_file_modify',
            _('A file has been modified.'),
            _('A file has been modified.')
        )
