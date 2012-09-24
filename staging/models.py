from django.db import models

import logging

logger = logging.getLogger(__name__)

class ProgressManager(models.Manager):
    def get_new(self):
        # create a new one and get the key
        prog = self.create(progress=0)

        prog.save()

        logger.debug("ProgressManager.get_new created new progress pk='{0}'.".format(prog.pk)

        return prog.pk

class Progress(models.Model):
    """A model to track progress of an action."""
    objects = ProgressManager()

    progress = models.IntegerField()
