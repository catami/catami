from datetime import datetime
from django.contrib.gis.db import models
from django.contrib.auth.models import User
from catamidb.models import Image, Deployment
from random import sample
import logging

logger = logging.getLogger(__name__)


class CollectionManager(models.Manager):
    """Manager for collection objects.

    Has methods to assist in creation collections and worksets.
    """

    def collection_from_deployment(self, user, deployment):
        """Create a collection using all images in a deployment.

        :returns: the created collection.
        """

        # create and prefill the collection as much as possible
        c = Collection()
        c.name = deployment.short_name
        c.owner = user
        c.creation_date = datetime.now()
        c.modified_date = datetime.now()
        c.is_public = True
        c.is_locked = True
        c.creation_info = "Deployments: {0}".format(deployment)

        # save the collection so we can associate images with it
        c.save()

        # now add all the images
        images = Image.objects.filter(pose__deployment=deployment)
        c.images.add(*images)

        return c

    def collection_from_deployments_with_name(self, user, collection_name, deployment_id_list_string):
        """Create a collection using all images in a deployment.

        :returns: the created collection.
        """

        deployment_list = [int(x) for x in deployment_id_list_string.split(',')]

        # create and prefill the collection as much as possible
        c = Collection()
        c.name = collection_name
        c.owner = user
        c.creation_date = datetime.now()
        c.modified_date = datetime.now()
        c.is_public = False
        c.is_locked = True
        c.creation_info = "Deployments: {0}".format(deployment_id_list_string)

        # save the collection so we can associate images with it
        c.save()

        # now add all the images
        for value in deployment_list:
            images = Image.objects.filter(pose__deployment=Deployment.objects.filter(id=value))
            c.images.add(*images)

        return c

    # NOTE: it may make sense to create one function for all the
    # different sampling methods instead of a separate one for each.
    def workset_from_collection(self, user, name, description, ispublic, c_id, n, method):
        """Create a workset (or child collection) from a parent collection

        :returns: the created workset."""

        c = Collection.objects.get(pk=c_id)
        cimages = c.images.all()

        # Create new collection entry
        ws = Collection()
        ws.parent = c
        ws.name = name
        ws.owner = user
        ws.creation_date = datetime.now()
        ws.modified_date = datetime.now()
        ws.is_public = ispublic
        ws.description = description
        ws.is_locked = True

        # check that n < number of images in collection
        if cimages.count() < n:
            logger.warning("Not enough images to subsample... setting n=images.count")  # TODO: what is the best way to handle warnings?
            n = cimages.count()

        # subsample collection images and add to workset
        if method == "random":
            wsimglist = sample(cimages, n)
            ws.creation_info = "Random: {0} images".format(n)
        elif method == "stratified":
            wsimglist = cimages[0:cimages.count():n]
            ws.creation_info = "Stratified: every {0}th image".format(n)  # TODO: add some logic "th" does not work for 1-3
        else:
            logger.error("Unrecognised method")  # TODO: what is the best way to handle warnings?

        # save the workset so we can associate images with it
        ws.save()
        # Associate images with workset
        ws.images.add(*wsimglist)

        return ws


class Collection(models.Model):
    """Collections are a set of images that a user works with.

    They contain 'worksets' and 'collections' in front end
    terminology. The only difference here is that collections
    don't have a parent whilst worksets do.
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User)
    creation_date = models.DateTimeField()
    modified_date = models.DateTimeField()
    is_public = models.BooleanField()
    is_locked = models.BooleanField()
    parent = models.ForeignKey('Collection', null=True, blank=True)
    images = models.ManyToManyField(Image, related_name='collections')
    creation_info = models.CharField(max_length=200)

    class Meta:
        unique_together = (('owner', 'name'), )
