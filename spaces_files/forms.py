from django import forms
from .models import File, Folder

class FolderForm(forms.ModelForm):
    description = forms.CharField(
        widget = forms.Textarea(attrs={'rows': 2}),
        required = False
    )

    def __init__(self, *args, **kwargs):
        self.space = kwargs.pop('space', None)
        super(FolderForm, self).__init__(*args, **kwargs)
        parent = self.fields['parent']
        parent.queryset = parent.queryset.filter(file_manager__space=self.space)
        self.fields.update({'parent': parent})

    class Meta:
        model = Folder
        fields = ('name', 'description', 'parent')

class FileForm(forms.ModelForm):
    description = forms.CharField(
        widget = forms.Textarea(attrs={'rows': 2}),
        required = False
    )

    def __init__(self, *args, **kwargs):
        self.space = kwargs.pop('space', None)
        super(FileForm, self).__init__(*args, **kwargs)
        parent = self.fields['parent']
        parent.queryset = parent.queryset.filter(file_manager__space=self.space)
        self.fields.update({'parent': parent})
    
    class Meta:
        model = File
        fields = ('name', 'description', 'file', 'parent')