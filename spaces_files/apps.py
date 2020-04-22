from django.apps import AppConfig
from django.db.models.signals import post_delete, post_migrate

from spaces_files.signals import create_notice_types, auto_delete_file_on_delete


class SpacesFilesConfig(AppConfig):
    name = 'spaces_files'

    def ready(self):
        from . import signals
        # activate activity streams for CalendarEvent
        from actstream import registry
        from .models import Folder, File
        registry.register(Folder)
        registry.register(File)

        # register a custom notification
        """
        from spaces_notifications.utils import register_notification
        from django.utils.translation import ugettext_noop as _
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
        """
        post_migrate.connect(create_notice_types, sender=self)
        post_delete.connect(auto_delete_file_on_delete, sender=File)
