from django.conf.urls import url
from spaces.urls import space_patterns

from . import views

app_name = 'spaces_files'
urlpatterns = space_patterns(

    url(r'^files/$', views.index, name='index'),

    url(
        r'^files/folder/(\d+)/$', 
        views.show_folder, 
        name='folder'
    ),

    url(
        r'^files/file/(\d+)/$', 
        views.show_file, 
        name='file'
    ),

    url(
        r'^files/add_file/$',
        views.add_file,
        name='add_file'
    ),

    url(
        r'^files/add_file/(\d+)$',
        views.add_file,
        name='add_file'
    ),

    url(
        r'^files/add_folder/$',
        views.add_folder,
        name='add_folder'
    ),

    url(
        r'^files/add_folder/(\d+)$',
        views.add_folder,
        name='add_folder'
    ),

    url(
        r'^files/file/edit/(\d+)/$', 
        views.edit_file, 
        name='edit_file'
    ),


    url(
        r'^files/folder/edit/(\d+)/$', 
        views.edit_folder, 
        name='edit_folder'
    ),

    url(
        r'^files/folder/delete/(?P<pk>\d+)/$', 
        views.DeleteFolder.as_view(), 
        name='delete_folder'
    ),


    url(
        r'^files/file/delete/(?P<pk>\d+)/$', 
        views.DeleteFile.as_view(), 
        name='delete_file'
    ),

)