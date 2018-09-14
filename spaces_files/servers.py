#-*- coding: utf-8 -*-
import mimetypes
import os
import stat
from django.conf import settings
from django.http import (Http404, HttpResponse, HttpResponseBadRequest, 
    HttpResponseNotModified)
from django.utils.http import http_date
from django.views.static import was_modified_since

class DefaultServer(object):
    """
    Serve static files from the local filesystem through django.
    This is a bad idea for most situations other than testing.

    This will only work for files that can be accessed in the local filesystem.

    Mostly identical to the server from django_private_media, but this one ensures
    the file in question is indeed a file, not a directory.
    """
    def serve(self, request, path):
        # the following code is largely borrowed from `django.views.static.serve`
        # and django-filetransfers: filetransfers.backends.default
        fullpath = os.path.join(settings.PRIVATE_MEDIA_ROOT, path)
        if not os.path.exists(fullpath):
            raise Http404('"{0}" does not exist'.format(fullpath))
        # Respect the If-Modified-Since header.
        statobj = os.stat(fullpath)
        content_type = mimetypes.guess_type(fullpath)[0] or 'application/octet-stream'
        if not was_modified_since(request.META.get('HTTP_IF_MODIFIED_SINCE'),
                                  statobj[stat.ST_MTIME], statobj[stat.ST_SIZE]):
            return HttpResponseNotModified(content_type=content_type)
        if not os.path.isfile(fullpath):
            return HttpResponseBadRequest()
        response = HttpResponse(open(fullpath, 'rb').read(), content_type=content_type)
        response["Last-Modified"] = http_date(statobj[stat.ST_MTIME])
        # filename = os.path.basename(path)
        # response['Content-Disposition'] = smart_str(u'attachment; filename={0}'.format(filename))
        return response