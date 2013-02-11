from datetime import datetime
from django.contrib.gis.db import models
from django.contrib.auth.models import User
from Force.models import Image, Deployment

class CollectionManager(models.Manager):

    def collection_from_deployment(self, user, deployment):
        """Create a collection using all images in a deployment.

        Returns the created collection."""

        # create and prefill the collection as much as possible
        c = Collection()
        c.name = deployment.short_name
        c.owner = user
        c.creation_date = datetime.now()
        c.modified_date = datetime.now()
        c.is_public = True
        c.is_locked = True

        # save the collection so we can associate images with it
        c.save()

        # now add all the images
        for image in deployment.image_set.all():
            c.images.add(image)

        return c

    def collection_from_deployments_with_name(self, user, collection_name, deployment_id_list_string):
        """Create a collection using all images in a deployment.

        Returns the created collection."""

        deployment_list = [int(x) for x in deployment_id_list_string.split(',')]

        # create and prefill the collection as much as possible
        c = Collection()
        c.name = collection_name
        c.owner = user
        c.creation_date = datetime.now()
        c.modified_date = datetime.now()
        c.is_public = False
        c.is_locked = True

        # save the collection so we can associate images with it
        c.save()

        # now add all the images
        for value in deployment_list:
            for image in Image.objects.filter(deployment=Deployment.objects.filter(id=value)):
                c.images.add(image)

        return c

class Collection(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    owner = models.ForeignKey(User)
    creation_date = models.DateTimeField()
    modified_date = models.DateTimeField()
    is_public = models.BooleanField()
    is_locked = models.BooleanField()
    parent = models.ForeignKey('Collection', null=True, blank=True, default=None)
    images = models.ManyToManyField(Image, related_name='collections')

    class Meta:
        unique_together = (('owner', 'name'), )
