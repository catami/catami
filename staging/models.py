from django.db import models

class ProgressManager(models.Manager):
    def get_new(self):
        # create a new one and get the key
        prog = self.create(progress=0)

        prog.save()

        return prog.pk

class Progress(models.Model):
    """A model to track progress of an action."""
    objects = ProgressManager()

    progress = models.IntegerField()
