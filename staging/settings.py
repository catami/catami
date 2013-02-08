from django.conf import settings

STAGING_IMPORT_DIR = getattr(settings, 'STAGING_IMPORT_DIR', '/media/water/RELEASE_DATA')
STAGING_WEBIMAGE_DIR = getattr(settings, 'STAGING_WEBIMAGE_DIR', '/media/catami_live/importedimages/')
STAGING_ARCHIVE_DIR = getattr(settings, 'STAGING_ARCHIVE_DIR', '/media/catami_tape/archiveimages/')
