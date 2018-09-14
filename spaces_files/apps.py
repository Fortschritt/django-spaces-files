from django.apps import AppConfig


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
