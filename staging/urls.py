"""URL Mappings for the staging application.
"""
__author__ = 'Lachlan Toohey'

from django.conf.urls import patterns, url

urlpatterns = patterns('staging.views',
    url(r'^$', 'index', name='staging_index'),
    url(r'^upload_progress/$', 'upload_progress'),
    url(r'^auv/import$', 'auvimport', name='staging_auv_import'),
    url(r'^auv/progress$', 'auvprogress'),
    url(r'^auv/imported$', 'auvimported', name='staging_auv_imported'),
    url(r'^file/import$', 'fileupload', name='staging_file_import'),
    url(r'^file/imported$', 'fileuploaded', name='staging_file_imported'),
    url(r'^metadata/stage$', 'metadatastage', name='staging_metadata_stage'), # upload/import file
    url(r'^metadata/list$', 'metadatalist', name='staging_metadata_list'), # list files
    url(r'^metadata/change_public/$', 'change_public', name='staging_metadata_book_update_public'), # list sheets and headings
    url(r'^metadata/book/(?P<file_id>\d+)$', 'metadatabook', name='staging_metadata_book'), # list sheets and headings
    url(r'^metadata/book/(?P<file_id>\d+)/delete$', 'metadatadelete', name='staging_metadata_delete'), # delete a file
    url(r'^metadata/sheet/(?P<file_id>\d+)/(?P<page_name>[\w-]+)$', 'metadatasheet', name='staging_metadata_sheet'), # show sheet data/info
    url(r'^metadata/import/(?P<file_id>\d+)/(?P<page_name>[\w-]+)/(?P<model_name>[\w-]+)$', 'metadataimport', name='staging_metadata_import'), # show import data/info
    url(r'^metadata/imported$', 'metadataimported', name='staging_metadata_imported'), # thanks/confirmation of import
    # annotations
    url(r'^annotations/cpc/import$', 'annotationcpcimport', name='staging_annotation_cpc_import'),
    url(r'^annotations/cpc/imported$', 'annotationcpcimported', name='staging_annotation_cpc_imported'),
)

