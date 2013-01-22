from django.db import models
from Force.models import Image
from collection.models import Collection

class ClusterRun(models.Model):
    """The clustering of a Collection with a certain tuning parameter """
    collection = models.ForeignKey(Collection)

    # Tuning parameter
    cluster_width = models.FloatField()

class ImageProbability(models.Model):
    """ The probability the image belongs to a label"""
    image = models.ForeignKey(Image)
    probability = models.FloatField()# may need to add max and min
    cluster_label = models.ForeignKey('ClusterLabels')

class ClusterLabels(models.Model):
    image = models.ManyToManyField(Image,related_name='clusters')
    cluster_label = models.IntegerField()
    probabilities = models.ManyToManyField(Image,through='ImageProbability', related_name='cluster_probabilities')
    cluster_run = models.ForeignKey(ClusterRun)



