try:
    from unittest import mock
except ImportError:
    import mock

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse
from django.http import HttpRequest
from django.contrib.auth.models import AnonymousUser, User
from django.test import TestCase, RequestFactory, Client
from spaces.models import Space
from djangoplugins.management.commands.syncplugins import SyncPlugins
from .models import Folder, File, SpacesFiles
from collab.permissions import FilesPermissions
from .views import add_file

class TestMediaFilePermissions(TestCase):
    """
    Test file download permissions. Files are served by django_private_media and
    should only be downloaded if user has read permissions for current space.

    TODO: Test file manipulation as admin/manager who is not a member of the space.
    """
    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.user = User.objects.create_user(
            username='jacob', email='jacob@…', password='top_secret')
        self.space = Space.objects.create(name='My Test Space', created_by = self.user, slug="my_test_space")
        self.files_plugin = SpacesFiles.objects.create(space=self.space, active=True)
        SyncPlugins(False, 0).all()
        self.folder = Folder.objects.create(
            name="Test Folder",
            file_manager=self.files_plugin,
            created_by = self.user
        )

        self.video = SimpleUploadedFile("file.mp4", b"file_content", content_type="video/mp4")
        request_kwargs = {'file':self.video, 'parent':self.folder.id}
        request = self.factory.post(reverse('spaces_files:add_file'), request_kwargs)
        request.user = self.user
        request.SPACE = self.space
        self.request = request


    ### ADD FILE
    def test_upload_file_as_anonymous(self):
        self.request.user = AnonymousUser()
        response = add_file(self.request)
        # was the form valid and the file created?
        self.assertEqual(response.status_code, 403)

    def test_upload_file_as_non_member(self):
        response = add_file(self.request)
        # was the form valid and the file created?
        self.assertEqual(response.status_code, 403)

    def test_upload_file_as_member(self):
        member_group = self.space.get_members()
        self.user.groups.add(member_group)
        response = add_file(self.request)
        # was the form valid and the file created?
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('spaces_files:index'))


    ### READ FILE
    def test_retrieve_file_as_anonymous(self):
        fp = FilesPermissions()
        self.request.user = AnonymousUser()
        result = fp.has_read_permission(self.request, '')
        self.assertEqual(result, False)

    def test_retrieve_file_as_non_member(self):
        fp = FilesPermissions()
        result = fp.has_read_permission(self.request, '')
        self.assertEqual(result, False)

    def test_retrieve_file_as_member(self):
        fp = FilesPermissions()
        group = self.space.get_members()
        self.request.user.groups.add(group)
        result = fp.has_read_permission(self.request, '')
        self.assertEqual(result, True)

    ### DELETE FOLDER
    def test_delete_folder_as_anonymous(self):
        fp = FilesPermissions()
        request = self.factory.post(reverse('spaces_files:delete_file', kwargs={'pk':self.folder.pk}))
        request.user = AnonymousUser()
        request.SPACE = self.space
        result = fp.has_read_permission(self.request, '')
        self.assertEqual(result, False)

    def test_delete_folder_as_non_member(self):
        fp = FilesPermissions()
        request = self.factory.post(reverse('spaces_files:delete_folder', kwargs={'pk':self.folder.pk}))
        request.user = self.user
        request.SPACE = self.space
        result = fp.has_read_permission(self.request, '')
        self.assertEqual(result, False)

    def test_delete_folder_as_member(self):
        fp = FilesPermissions()
        request = self.factory.post(reverse('spaces_files:delete_folder', kwargs={'pk':self.folder.pk}))
        request.user = self.user
        group = self.space.get_members()
        request.user.groups.add(group)
        request.SPACE = self.space
        result = fp.has_read_permission(self.request, '')
        self.assertEqual(result, True)

    ### DELETE FILE
    def test_delete_file_as_anonymous(self):
        fp = FilesPermissions()
        file = File.objects.create(
            file = self.video,
            parent = self.folder,
            created_by = self.user
        )
        request = self.factory.post(reverse('spaces_files:delete_file', kwargs={'pk':file.pk}))
        request.user = AnonymousUser()
        request.SPACE = self.space
        result = fp.has_read_permission(self.request, '')
        self.assertEqual(result, False)

    def test_delete_file_as_non_member(self):
        fp = FilesPermissions()
        file = File.objects.create(
            file = self.video,
            parent = self.folder,
            created_by = self.user
        )
        request = self.factory.post(reverse('spaces_files:delete_file', kwargs={'pk':file.pk}))
        request.user = self.user
        request.SPACE = self.space
        result = fp.has_read_permission(self.request, '')
        self.assertEqual(result, False)

    def test_delete_file_as_member(self):
        fp = FilesPermissions()
        file = File.objects.create(
            file = self.video,
            parent = self.folder,
            created_by = self.user
        )
        request = self.factory.post(reverse('spaces_files:delete_file', kwargs={'pk':file.pk}))
        request.user = self.user
        group = self.space.get_members()
        request.user.groups.add(group)
        request.SPACE = self.space
        result = fp.has_read_permission(self.request, '')
        self.assertEqual(result, True)

    