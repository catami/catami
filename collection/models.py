from datetime import datetime
from dateutil.tz import tzutc
from django.contrib.gis.db import models

from django.contrib.auth.models import User
from catamidb.models import Image, GenericImage, Deployment, ScientificMeasurementType
from random import sample
import logging
from collection import authorization
from django.db.utils import IntegrityError

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
        collection = Collection()
        collection.name = deployment.short_name
        collection.owner = user
        collection.creation_date = datetime.now(tz=tzutc())
        collection.modified_date = datetime.now(tz=tzutc())
        collection.is_locked = True
        collection.creation_info = "Deployments: {0}".format(deployment.short_name)

        # save the collection so we can associate images with it
        collection.save()

        #apply permissions
        authorization.apply_collection_permissions(user, collection)

        # now add all the images
        images = Image.objects.filter(pose__deployment=deployment)
        collection.images.add(*images)

        return collection

    def collection_from_deployments_with_name(self, user, collection_name,
        deployment_id_list_string):
        """Create a collection using all images in a deployment.

        :returns: the created collection.
        """

        deployment_list = [int(x) for x in deployment_id_list_string.split(','
            )]

        # create and prefill the collection as much as possible
        collection = Collection()
        collection.name = collection_name
        collection.owner = user
        collection.creation_date = datetime.now(tz=tzutc())
        collection.modified_date = datetime.now(tz=tzutc())
        collection.is_public = False
        collection.is_locked = True
        collection.creation_info = "Deployments: {0}".format(deployment_id_list_string)

        # save the collection so we can associate images with it
        collection.save()

        #apply permissions
        authorization.apply_collection_permissions(user, collection)

        # now add all the images
        for value in deployment_list:
            images = Image.objects.filter(pose__deployment=Deployment.objects.
                filter(id=value))
            collection.images.add(*images)

        return collection

    def collection_from_explore(self, user,
                                collection_name,
                                deployment_id_list_string,
                                depth__gte,
                                depth__lte,
                                temperature__gte,
                                temperature__lte,
                                salinity__gte,
                                salinity__lte,
                                altitude__gte,
                                altitude__lte):

        """Create a collection using all images in a deployment.

        :returns: the created collection.
        """

        deployment_list = [int(x) for x in deployment_id_list_string.split(','
        )]

        # create and prefill the collection as much as possible
        collection = Collection()
        collection.name = collection_name
        collection.owner = user
        collection.creation_date = datetime.now(tz=tzutc())
        collection.modified_date = datetime.now(tz=tzutc())
        collection.is_public = False
        collection.is_locked = True
        collection.creation_info = "Deployments: {0}".format(deployment_id_list_string)

        # save the collection so we can associate images with it
        collection.save()

        #apply permissions
        authorization.apply_collection_permissions(user, collection)

        # now add all the images
        #for value in deployment_list:

        #filter deployment id and depth
        images = Image.objects.filter(pose__deployment__id__in=deployment_list,
                                      pose__depth__gte=depth__gte,
                                      pose__depth__lte=depth__lte)

        # get the measurement types we want to query
        measurement_types = ScientificMeasurementType.objects.all()
        temperature = measurement_types.get(normalised_name="temperature")
        salinity = measurement_types.get(normalised_name="salinity")
        altitude = measurement_types.get(normalised_name="altitude")

        #filter temp
        images = images.filter(pose__scientificposemeasurement__measurement_type=temperature, pose__scientificposemeasurement__value__range=(temperature__gte, temperature__lte))

        #filter salinity
        images = images.filter(pose__scientificposemeasurement__measurement_type=salinity, pose__scientificposemeasurement__value__range=(salinity__gte, salinity__lte))

        #filter altitude
        images = images.filter(pose__scientificposemeasurement__measurement_type=altitude, pose__scientificposemeasurement__value__range=(altitude__gte, altitude__lte))

        collection.images.add(*images)

        return collection

    # NOTE: it may make sense to create one function for all the
    # different sampling methods instead of a separate one for each.
    def workset_from_collection(self, user, name, description, ispublic, c_id, n, method):
        """Create a workset (or child collection) from a parent collection

        returns: the created workset id (or None if error)
                 a status/error message
        """

        try:
            collection = Collection.objects.get(pk=c_id)
            collection_images = collection.images.all()

            #check if the user has permission to do this
            if not user.has_perm('collection.change_collection', collection):
                raise CollectionError("Sorry. You don't have sufficient privileges to create a Workset in this Project.")

            # check that n < number of images in collection
            if collection_images.count() < n:
                #n = collection_images.count()
                raise CollectionError("Not enough images to subsample. The value for 'N' was greater than the number of images in the collection.")


            # Create new collection entry
            workset = Collection()
            workset.parent = collection
            workset.name = name
            workset.owner = user
            workset.creation_date = datetime.now(tz=tzutc())
            workset.modified_date = datetime.now(tz=tzutc())
            workset.is_public = ispublic
            workset.description = description
            workset.is_locked = True

            # subsample collection images and add to workset
            if method == "random":
                wsimglist = sample(collection_images, n)
                workset.creation_info = "%s random images" % n

            elif method == "stratified":
                wsimglist = collection_images[0:collection_images.count():n]

                # Format number as ordinal string
                if 10 < n < 14: nstr =  "%sth" % n
                elif n % 10 == 1: nstr =  "%sst" % n
                elif n % 10 == 2: nstr =  "%snd" % n
                elif n % 10 == 3: nstr =  "%srd" % n
                else: nstr = "%sth" % n
                workset.creation_info = "Every %s image" % nstr

            else:
                raise CollectionError("Unrecognised method argument for Workset creation")


            # save the workset so we can associate images with it
            workset.save()

            # Associate images with workset
            workset.images.add(*wsimglist)

            #apply permissions
            authorization.apply_collection_permissions(user, workset)

            wsid = workset.id
            msg="Your Workset has been created successfully!"

        except CollectionError as e:
            wsid = None
            msg = e.msg
            #logger.error(msg)

        except IntegrityError as e:
            wsid = None
            msg = "This Workset is to similar to an existing one. Please choose a more unique name."

        except Exception as e:
            wsid = None
            msg = "An unknown error has occurred during the creation of your Workset..."
            print ("Exception Type: %s" % e.__class__)
            #logger.error(msg)

        #print "Debug (wsid: {0}, msg: {1})".format(wsid, msg)
        return wsid, msg


class CollectionError(Exception):
    """Exception raised for errors in the input.
    Attributes:
        msg  -- explanation of the error
    """
    def __init__(self, msg):
        self.msg = msg


class Collection(models.Model):
    """Collections are a set of images that a user works with.

    They contain 'worksets' and 'collections' in front end
    terminology. The only difference here is that collections
    don't have a parent whilst worksets do.
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    owner = models.ForeignKey(User)
    creation_date = models.DateTimeField()
    modified_date = models.DateTimeField()
    is_locked = models.BooleanField()
    parent = models.ForeignKey('Collection', null=True, blank=True)
    images = models.ManyToManyField(Image, related_name='collections')
    generic_images = models.ManyToManyField(GenericImage, related_name='collections')
    creation_info = models.CharField(max_length=200)

    class Meta:
        unique_together = (('owner', 'name', 'parent'), )
        permissions = (
            ('view_collection', 'View the collection.'),
        )

    def __unicode__(self):
        description = u"Collection: {0}".format(self.name)

        if self.is_locked:
            description += u" - locked"
        return description
