from django.conf import settings

# the staging area - where we search for deployments to import
STAGING_IMPORT_DIR = getattr(settings, 'STAGING_IMPORT_DIR', '/media/catami_staging/uploadeddeployments/')

# web image directory - where compressed deployment images are served from
STAGING_WEBIMAGE_DIR = getattr(settings, 'STAGING_WEBIMAGE_DIR', '/media/catami_live/importedimages/')

# the archive directory where we put original full resolution uncompressed images
STAGING_ARCHIVE_DIR = getattr(settings, 'STAGING_ARCHIVE_DIR', '/media/catami_tape/archiveimages/')

# should the original images be moved/deleted or not... also does not archive them if True
STAGING_MOVE_ORIGINAL_IMAGES = getattr(settings, 'STAGING_MOVE_ORIGINAL_IMAGES', True)
