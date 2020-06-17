from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.encoding import force_text
from django.utils.translation import ugettext as _
from django.views.generic.edit import DeleteView
from actstream.signals import action as actstream_action
from spaces.models import SpacePluginRegistry
from spaces_notifications.forms import NotificationFormSet
from spaces_notifications.mixins import process_n12n_formset
from collab.decorators import permission_required_or_403
from .decorators import file_owner_or_admin_required
from .forms import FolderForm, FileForm
from .models import Folder, File, FilesPlugin

def base_extra_context(request):
    extra_context = {}
    extra_context['plugin_selected'] = FilesPlugin.name
    return extra_context


@permission_required_or_403('access_space')
def index(request):
    extra_context = base_extra_context(request)
    extra_context["folders"] = Folder.objects.all().filter(file_manager__space=request.SPACE)
    return render(request, 'spaces_files/index.html', extra_context)


@permission_required_or_403('access_space')
def show_folder(request, folder_id=None):
    """
    Show a folder branch starting from the given folder id.
    """
    folder = get_object_or_404(Folder, id=folder_id, file_manager__space=request.SPACE)
    extra_context = base_extra_context(request)
    extra_context["folder"] = folder
    extra_context["folders"] = folder.get_descendants(include_self=True)
    return render(request, 'spaces_files/subfolder.html', extra_context)


def save_files_form(request, form):
    """
    Save a folder/file given the form data. Used for both adding and editing folders/files.
    """
    obj = form.save(commit=False)
    obj.created_by = request.user
    files_plugin = SpacePluginRegistry().get_instance(
        plugin_name='spaces_files',
        space=request.SPACE
    )
    obj.file_manager = files_plugin
    obj.save()
    return obj

    
@permission_required_or_403('access_space')#TODO:finetune permissions according to spec
def edit_folder(request, folder_id=None):
    """
    Display and process a form for editing a given folder.
    """
    folder = get_object_or_404(Folder, id=folder_id, file_manager__space=request.SPACE)
    if request.method == 'POST':
        form = FolderForm(request.POST, instance=folder, space=request.SPACE)
        if form.is_valid():
            folder = save_files_form(request, form)
            actstream_action.send(
                sender=request.user,
                verb=_("was edited"),
                target=request.SPACE,
                action_object= folder
            )

            return redirect('spaces_files:index')
    else:
        form = FolderForm(instance=folder, space=request.SPACE)
    extra_context = base_extra_context(request)
    extra_context["form"] = form
    return render(request, 'spaces_files/add_folder.html', extra_context)


# TODO: finetune permissions according to spec
class DeleteFolder(SuccessMessageMixin, DeleteView):

    model = Folder
    success_message = _("Folder was deleted successfully")
    success_url = reverse_lazy('spaces_files:index')

    @file_owner_or_admin_required
    @method_decorator(permission_required_or_403('access_space'))
    def delete(self, request, *args, **kwargs):
        actstream_action.send(
                sender=request.user,
                verb=_("was deleted"),
                target=request.SPACE,
                action_object=self.get_object()
            )

        messages.success(request, self.success_message)
        return super(DeleteFolder, self).delete(request, *args, **kwargs)

    # ensure only folders of own space can get deleted
    def get_queryset(self):
        qs = super(DeleteFolder, self).get_queryset()
        qs = qs.filter(file_manager__space=self.request.SPACE)
        return qs

@permission_required_or_403('access_space')
def show_file(request, file_id=None):
    """
    Show a folder branch starting from the given folder id.
    """
    file = get_object_or_404(File, id=file_id, parent__file_manager__space=request.SPACE)
    extra_context = base_extra_context(request)
    extra_context["file"] = file
    return render(request, 'spaces_files/file.html', extra_context)


@permission_required_or_403('access_space')
def add_folder(request, folder_id=None):
    if request.method == 'POST':
        form = FolderForm(request.POST, space=request.SPACE)
        if form.is_valid():
            folder = save_files_form(request, form)
            messages.success(request, _("Folder successfully created."))
            actstream_action.send(
                sender=request.user,
                verb=_("was created"),
                target=request.SPACE,
                action_object=folder
            )
            return redirect(folder.get_absolute_url())
    else:
        form = FolderForm(initial={'parent':folder_id}, space=request.SPACE)
    extra_context = base_extra_context(request)
    extra_context["form"] = form
    return render(request, 'spaces_files/add_folder.html', extra_context)


@permission_required_or_403('access_space')#TODO:finetune permissions according to spec
def edit_file(request, file_id=None):
    """
    Display and process a form for editing a given file.
    """
    file = get_object_or_404(File, id=file_id, parent__file_manager__space=request.SPACE)
    if request.method == 'POST':
        form = FileForm(request.POST, instance=file, space=request.SPACE)
        n12n_formset = NotificationFormSet(request.SPACE, request.POST)
        if form.is_valid():
            file = save_files_form(request, form)
            actstream_action.send(
                sender=request.user,
                verb=_("was edited"),
                target=request.SPACE,
                action_object=file
            )
            messages.success(request, _("File successfully modified."))
            process_n12n_formset(
                n12n_formset,
                'spaces_files_file_modify',
                request.SPACE,
                file,
                file.get_absolute_url()
            )
            return redirect('spaces_files:index')
    else:
        form = FileForm(instance=file, space=request.SPACE)
        n12n_formset = NotificationFormSet(request.SPACE)
    extra_context = base_extra_context(request)
    extra_context["form"] = form
    extra_context["notification_formset"] = n12n_formset
    return render(request, 'spaces_files/add_file.html', extra_context)


@permission_required_or_403('access_space')
def add_file(request, parent_id=None):
    if request.method == 'POST':
        form = FileForm(request.POST, request.FILES, space=request.SPACE)
        n12n_formset = NotificationFormSet(request.SPACE, request.POST)
        if form.is_valid():
            file = save_files_form(request, form)
            actstream_action.send(
                sender=request.user,
                verb=_("was created"),
                target=request.SPACE,
                action_object=file
            )
            messages.success(request, _("File successfully created."))
            process_n12n_formset(
                n12n_formset,
                'spaces_files_file_create',
                request.SPACE,
                file,
                file.get_absolute_url()
            )
            redirect_target = file.parent.get_absolute_url() if file.parent else 'spaces_files:index'
            return redirect(redirect_target)
    else:
        form = FileForm(initial={'parent':parent_id}, space=request.SPACE)
        n12n_formset = NotificationFormSet(request.SPACE)
    extra_context = base_extra_context(request)
    extra_context["form"] = form
    extra_context["notification_formset"] = n12n_formset
    return render(request, 'spaces_files/add_file.html', extra_context)

class DeleteFile(SuccessMessageMixin,DeleteView):

    model = File
    success_message = _("File was deleted successfully")
    success_url = reverse_lazy('spaces_files:index')

    @file_owner_or_admin_required
    @method_decorator(permission_required_or_403('access_space'))
    def delete(self, request, *args, **kwargs):
        messages.success(request, self.success_message)
        # Note: on object deletion, all other activities are deleted, too.
        # That means the following signal won't show up in the activity stream.
        # Options for making deleted objects appear in the the stream would be
        # a) not really deleting but deactivating them with e.g. a boolean field
        # b) somehow presevering the name of the deleted instance in another 
        #    table and replacing all instance references in the stream with
        #    that one.
        actstream_action.send(
                sender=request.user,
                verb=_("was deleted"),
                target=request.SPACE,
                action_object=self.get_object()
            )
        return super(DeleteFile, self).delete(request, *args, **kwargs)


    # ensure only files of own space can get deleted
    def get_queryset(self):
        qs = super(DeleteFile, self).get_queryset()
        qs = qs.filter(parent__file_manager__space=self.request.SPACE)
        return qs
