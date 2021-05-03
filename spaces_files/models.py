from os.path import basename
import time

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from mptt.models import MPTTModel, TreeForeignKey
from private_media.storages import PrivateMediaStorage

from spaces.models import Space,SpacePluginRegistry, SpacePlugin, SpaceModel

def file_upload_path(instance, filename):
    space = instance.parent.file_manager.space.slug
    time_string = time.strftime('%Y/%m/%d')
    return 'spaces_files/%s/%s/%s' % (space, time_string, filename)


class SpacesFiles(SpacePlugin):
    """
    File manager model for Spaces. This only provides general metadata.
    Actual models are Folder and File instances and have a ForeignKey to this
    model.
    """
    # active field (boolean) inherited from SpacePlugin
    # space field (foreignkey) inherited from SpacePlugin
    reverse_url = 'spaces_files:index'
    


class Folder(MPTTModel):
    """
    A Folder. Can contain files and other folders.
    """
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    file_manager = models.ForeignKey(SpacesFiles, on_delete=models.CASCADE)
    parent = TreeForeignKey(
        'self', 
        blank=True, 
        null=True, 
        related_name='children', 
        db_index=True, 
        verbose_name=_('parent folder'),
        on_delete=models.CASCADE)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('folder')
        verbose_name_plural = _('folders')

    class MPTTMeta:
        order_insertion_by = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('spaces_files:folder', args=[str(self.id)])


class File(SpaceModel):
    """
    A File. Must be contained in a Folder.
    """
    name = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to=file_upload_path, storage=PrivateMediaStorage())
    parent = TreeForeignKey(
        Folder, 
        db_index=True, 
        verbose_name=_('parent folder'),
        on_delete=models.CASCADE)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    spaceplugin_field_name = "parent__file_manager"

    class Meta:
        verbose_name = _('file')
        verbose_name_plural = _('files')
        ordering = ["name"]

    def __str__(self):
        return self.get_name()

    def get_name(self):
        return self.name if self.name else basename(self.file.name)

    def get_absolute_url(self):
        return reverse('spaces_files:file', args=[str(self.id)])

    def save(self, **kwargs):
        # if the user doesn't provide a name, copy the filename
        if not self.name:
            self.name = basename(self.file.name)
        super().save(**kwargs)


class FilesPlugin(SpacePluginRegistry):
    """
    Provide a simple file manager plugin for Spaces. This makes the SpacesFiles
    class visible to the plugin system.
    """
    name = 'spaces_files'
    title = _('Files')
    plugin_model = SpacesFiles
    searchable_fields = (File, ('name','description', 'file'))
