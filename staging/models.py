"""Models for the staging Django application.
"""
from django.db import models

import logging

logger = logging.getLogger(__name__)

class MetadataFile(models.Model):
    """Handles info about metadata files that have been uploaded.

    These files are temporary in that once importing is complete they
    are no longer needed.
    """
    owner = models.ForeignKey('auth.user')
    metadata_file = models.FileField(upload_to='staging/metadata')
    is_public = models.BooleanField()
    description = models.CharField(max_length=100)

    def __unicode__(self):
        return "<MetadataFile {0}>".format(self.metadata_file)

