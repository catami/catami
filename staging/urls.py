"""URL Mappings for the staging application.
"""
__author__ = 'Lachlan Toohey'

from django.conf.urls import patterns, url

urlpatterns = patterns('staging.views',
    url(r'^$', 'index', name='staging_index'),
    url(r'^progress/(?P<key>\d+)$', 'progress'),
    url(r'^upload_progress/$', 'upload_progress'),
    url(r'^auv/import$', 'auvimport', name='staging_auv_import'),
    url(r'^auv/imported$', 'auvimported', name='staging_auv_imported'),
    url(r'^file/import$', 'fileupload', name='staging_file_import'),
    url(r'^file/imported$', 'fileuploaded', name='staging_file_imported'),
)

