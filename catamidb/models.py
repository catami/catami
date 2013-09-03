"""Data models for the core Catami data storage.

Created Dan marrable 4/09/2012
d.marrable@ivec.org

Significantly rewritten Lachlan Toohey 21/2/2013

"""
from random import sample
from django.contrib.auth.models import Group

from django.contrib.gis.db import models
from django.dispatch import receiver
from guardian.shortcuts import assign
from userena.signals import signup_complete
import logging
import os
from catamiPortal import settings

logger = logging.getLogger(__name__)


class CampaignManager(models.GeoManager):
    """Model Manager for Campaign.
    Provides (by inheritance) gis methods and ability
    to get a campaign by natural key.
    """

    def get_by_natural_key(self, year, month, short_name):
        """Get a campaign from its natural key.
        :date_start: the start date of the campaign
        :short_name: the name of the campaign
        :returns: the campaign with the given natural key

        """

        return self.get(
            date_start__year=year,
            date_start__month=month,
            short_name=short_name
        )


class Campaign(models.Model):
    """A campaign describes a field campaign that has many deployments."""
    objects = CampaignManager()

    short_name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    associated_researchers = models.TextField()
    associated_publications = models.TextField()
    associated_research_grant = models.TextField()
    date_start = models.DateField()
    date_end = models.DateField()

    contact_person = models.TextField()

    def __unicode__(self):
        return "{0} - {1}".format(self.date_start, self.short_name)

    def natural_key(self):
        """Return the natural key for this Campaign.
        :returns: tuple representing the natural key
        """

        return (self.date_start.year, self.date_start.month, self.short_name)

    class Meta:
        """Defines Metaparameters of the model."""
        unique_together = (('date_start', 'short_name'), )
        permissions = (('view_campaign', 'View the campaign'), )


class DeploymentManager(models.GeoManager):
    """Model Manager for Deployment.
    Provides (by inheritance) gis methods and ability
    to get a deployment by natural key.
    """

    def get_by_natural_key(self, start_time_stamp, short_name):
        """Method to get object by its natural key.

        :returns: object represented by the natural key

        """
        return self.get(start_time_stamp=start_time_stamp,
                        short_name=short_name)


class Deployment(models.Model):
    """
    Defining a simple Deployment Model. Operator is included in the model as part of denormalising the subtypes
    This is to replace existing Deployment and subtypes BRUVDeployment, DOVDeployment, TIDEDeployment and TVDeployment
    
    """
    objects = DeploymentManager()

    type = models.CharField(max_length=100)
    operator = short_name = models.CharField(max_length=100)

    start_position = models.PointField()
    end_position = models.PointField()
    transect_shape = models.PolygonField()

    start_time_stamp = models.DateTimeField()
    end_time_stamp = models.DateTimeField()

    short_name = models.CharField(max_length=100)
    mission_aim = models.TextField()

    min_depth = models.FloatField()
    max_depth = models.FloatField()

    campaign = models.ForeignKey(Campaign)

    contact_person = models.TextField()
    descriptive_keywords = models.TextField()
    license = models.TextField()

    def __unicode__(self):
        return "Deployment: {0} - {1}".format(
                self.start_time_stamp, self.short_name
            )

    def natural_key(self):
        """Get the natural key of this object.
        :returns: tuple representing the natural key
        """

        return (self.start_time_stamp, self.short_name)

    class Meta:
        """Defines Metaparameters of the model."""
        unique_together = (('start_time_stamp', 'short_name'), )


class ImageUpload(models.Model):
    """
    Model used to upload images to server, and have server generate thumbnails
    Upload path defaults to "images" folder but will change during POST; use specified "deployment" to get Campaign and Deployment names
    e.g. deployment id = 2, look up Deployment short_name = "r20110612_033752_st_helens_01_elephant_rock_deep_repeat"
    and respective Campaign short_name = "Campaign1"
    Upload image goes into: UPLOAD_PATH/r20110612_033752_st_helens_01_elephant_rock_deep_repeat/Campaign1/images/
    Generated thumbnail goes into: UPLOAD_PATH/r20110612_033752_st_helens_01_elephant_rock_deep_repeat/Campaign1/thumbnails/
    UPLOAD_PATH defined in settings.py
    """

    img = models.ImageField(upload_to="images", null=True, blank=True, max_length=255)   


class ImageManager(models.GeoManager):
    """ Handles logic functions related to images """

    def random_sample_images(self, images, sample_size):
        """ Randomly sample images from a set """

        #return sample(images, int(sample_size))
        return images.order_by('?')[:sample_size]

    def stratified_sample_images(self, images, sample_size):
        """ Stratified sample images from a set """

        images.order_by('deployment', 'date_time')
        every_nth = images.count()/int(sample_size)
        sampled_images = images[0:images.count():every_nth]

        return sampled_images

    def construct_path_from_deployment(self, deployment, context_path, import_path) :
        """ Using specified deployment id,get Campaign and Deployment ids, which is used to create path for image and thumbnails """        
        deploymentId = str(deployment.id)
        campaignId = str(deployment.campaign.id)
        return os.path.join(import_path, campaignId, deploymentId, context_path, "")

    def get_image_destination(self, deployment, import_path) :
        """ Return web location of image """    
        return self.construct_path_from_deployment(deployment, "images", import_path)

    def get_thumbnail_destination(self, deployment, import_path) :
        """ Return web location of thumbnail """
        return self.construct_path_from_deployment(deployment, "thumbnails", import_path)

    def get_image_location(self, imageDest, imgName) :
        """ Return absolute location of image """
        return os.path.normpath(imageDest + imgName)

    def get_thumbanail_location(self, thumbDest, imageName, thumbnail_size) :
        """ Return absolute location of thumbnail """        
        imgNameNoExt, imgExt = os.path.splitext(imageName)
        size = str(thumbnail_size[0]) + "x" + str(thumbnail_size[1])
        return os.path.normpath(thumbDest + imgNameNoExt + "_" + size + imgExt)

    def get_image_path(self, image):
        return settings.IMPORT_PATH + "/" + str(image.deployment.campaign.id) + "/" + str(image.deployment.id) + "/images/" + image.image_name


class Image(models.Model):
    """
    Defining a simple image Model. Depth is included in the model to make
    queries flat, simple and faster.

    This is to replace existing Image and Pose.
    """

    deployment = models.ForeignKey(Deployment)
    image_name = models.CharField(max_length=200)   
    date_time = models.DateTimeField()
    position = models.PointField()
    depth = models.FloatField()
    objects = models.GeoManager()

    class Meta:
        """Defines Metaparameters of the model."""
        unique_together = (('date_time', 'deployment'), )


class Camera(models.Model):
    """Data about a camera used in a deployment.
    Contains information about the orientation and quality of the images
    as well as a name for the camera itself.
    
    This will replace Camera eventually.
    """

    DOWN_ANGLE = 0
    UP_ANGLE = 1
    SLANT_ANGLE = 2
    HORIZONTAL_ANGLE = 3

    CAMERA_ANGLES = (
        (DOWN_ANGLE, 'Downward'),
        (UP_ANGLE, 'Upward'),
        (SLANT_ANGLE, 'Slanting/Oblique'),
        (HORIZONTAL_ANGLE, 'Horizontal/Seascape'),
    )

    image = models.ForeignKey(Image)
    name = models.CharField(max_length=50)
    angle = models.IntegerField(choices=CAMERA_ANGLES)    

    class Meta:
        """Defines Metaparameters of the model."""
        unique_together = (('image', 'name'), )


class Measurements(models.Model):
    """
    A simple measurements model. To make joins and queries on images
    faster.

    This is to replace ScientificMeasurement models.
    """

    UNITS_CHOICES = (
        ('ppm', 'ppm'),
        ('ms', 'm s<sup>-1</sup>'),
        ('m', 'm'),
        ('cel', '&ordm;C'),
        ('rad', 'radians'),
        ('deg', '&ordm;'),
        ('psu', 'PSU'),
        ('dbar', 'dbar'),
        ('umoll', 'umol/l'),
        ('umolk', 'umol/kg'),
        ('mgm3', 'mg/m<sup>3</sup>'),
        ('',''), 
    )
        
    image = models.ForeignKey(Image)

    #The water temperature at the location (and time) of the image.
    temperature = models.FloatField(null=True, blank=True)
    temperature_unit = models.CharField(max_length=50, choices=UNITS_CHOICES, default='cel')

    #Water salinity at the measurement point.
    salinity = models.FloatField(null=True, blank=True)
    salinity_unit = models.CharField(max_length=50, choices=UNITS_CHOICES, default='psu')

    #Pitch of camera at time of image.
    pitch = models.FloatField(null=True, blank=True)
    pitch_unit = models.CharField(max_length=50, choices=UNITS_CHOICES, default='rad')

    #Roll of camera at time of image.
    roll = models.FloatField(null=True, blank=True)
    roll_unit = models.CharField(max_length=50, choices=UNITS_CHOICES, default='rad')

    #Yaw of camera at time of image.
    yaw = models.FloatField(null=True, blank=True)
    yaw_unit = models.CharField(max_length=50, choices=UNITS_CHOICES, default='rad')

    #Altitude of camera at time of image.
    altitude = models.FloatField(null=True, blank=True)
    altitude_unit = models.CharField(max_length=50, choices=UNITS_CHOICES, default='m')