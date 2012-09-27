"""Models for the staging Django application.
"""
from django.db import models

import logging

logger = logging.getLogger(__name__)

class ProgressManager(models.Manager):
    """Manager for progress objects.

    Enables simpler creation of Progress objects.
    """

    def get_new(self):
        """Create new Progress object and return the key.
        """
        prog = self.create(progress=0)

        prog.save()

        logger.debug("ProgressManager.get_new created new progress pk='{0}'.".format(prog.pk))

        return prog.pk

class Progress(models.Model):
    """A model to track progress of an action."""
    objects = ProgressManager()

    progress = models.IntegerField()
