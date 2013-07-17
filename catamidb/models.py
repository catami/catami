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

    short_name = models.CharField(max_length=100)
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

class GenericDeployment(models.Model):
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

class Deployment(models.Model):
    """Core Deployment class that holds basic position and time information.
    This is inherited by other types where more specific information is stored.
    """
    objects = DeploymentManager()

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
        subtypes = [
            'bruvdeployment',
            'auvdeployment',
            'dovdeployment',
            'tideployment',
            'tvdeployment'
        ]

        # check if subclass member variables exist
        for subtype in subtypes:
            try:
                subclass = getattr(self, subtype)
            except self.DoesNotExist:
                continue  # go to the next
            else:
                # use subclasses __unicode__ method
                return subclass.__unicode__()
        else:
            # If no sub type is matched
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


class PoseManager(models.GeoManager):
    """Model Manager for Pose.
    Provides (by inheritance) gis methods and ability
    to get a pose by natural key.
    """

    def get_by_natural_key(self, deployment_key, date_time):
        """Get a pose by its natural key (deployment key, pose time)
        :returns: nat

        """
        deployment = Deployment.objects.get_by_natural_key(*deployment_key)
        return self.get(deployment=deployment, date_time=date_time)


class Pose(models.Model):
    """Position of vehicle at image capture time.
    The intent is that there will be more than one image linking
    to a particular pose.
    Also associated are scientific measurements from other sensors
    such as salinity, chlorophyll and vehicle orientation. Images
    may have their own parameters attached that are image specific
    such as rugosity, reflectance etc.
    """
    objects = PoseManager()

    deployment = models.ForeignKey(Deployment)
    date_time = models.DateTimeField()
    position = models.PointField()
    depth = models.FloatField()

    def natural_key(self):
        """Get the natural key of the pose.
        :returns: natural key of the pose"""
        return self.deployment.natural_key() + (self.date_time, )

    # note that this is dependant on another object for its natural key
    natural_key.dependencies = ['Force.deployment']

    class Meta:
        """Defines Metaparameters of the model."""
        unique_together = (('deployment', 'date_time'), )


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


class GenericImageManager(models.GeoManager):
    """ Handles logic functions related to images """

    def random_sample_images(self, images, sample_size):
        """ Randomly sample images from a set """

        return sample(images, int(sample_size))

    def stratified_sample_images(self, images, sample_size):
        """ Stratified sample images from a set """

        every_nth = images.count()/int(sample_size)

        sampled_images = images[0:images.count():every_nth]

        return sampled_images


class GenericImage(models.Model):
    """
    Defining a simple image Model. Depth is included in the model to make
    queries flat, simple and faster.

    This is to replace existing Image and Pose.
    """

    deployment = models.ForeignKey(GenericDeployment)
    image_name = models.CharField(max_length=200)   
    date_time = models.DateTimeField()
    position = models.PointField()
    depth = models.FloatField()
    objects = models.GeoManager()

    class Meta:
        """Defines Metaparameters of the model."""
        unique_together = (('date_time', 'deployment'), )

class GenericCamera(models.Model):
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

    image = models.ForeignKey(GenericImage)
    name = models.CharField(max_length=50)
    angle = models.IntegerField(choices=CAMERA_ANGLES)    

    class Meta:
        """Defines Metaparameters of the model."""
        unique_together = (('image', 'name'), )

class Camera(models.Model):
    """Data about a camera used in a deployment.
    Contains information about the orientation and quality of the images
    as well as a name for the camera itself.
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

    deployment = models.ForeignKey(Deployment)
    name = models.CharField(max_length=50)
    angle = models.IntegerField(choices=CAMERA_ANGLES)

    class Meta:
        """Defines Metaparameters of the model."""
        unique_together = (('deployment', 'name'), )


class Image(models.Model):
    """The Image model that refers to a single still capture.
    It refers to a pose (for position of the image) and a
    camera to gain extra information about the orientation
    of the camera.
    """

    pose = models.ForeignKey(Pose)
    camera = models.ForeignKey(Camera)
    web_location = models.CharField(max_length=200)
    archive_location = models.CharField(max_length=200)

    class Meta:
        """Defines Metaparameters of the model."""
        unique_together = (('pose', 'camera'), )


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
        
    image = models.ForeignKey(GenericImage)

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

class ScientificMeasurementTypeManager(models.Manager):
    """Management class for ScientificMeasurementType."""

    def get_by_natural_key(self, normalised_name):
        """Accessor to query for type based on normalised name.
        :returns: object with given natural key.
        """
        return self.get(normalised_name=normalised_name)


class ScientificMeasurementType(models.Model):
    """A type of Scientific Measurement (ie salinity).
    This is used to store validation information about a measurement
    type as well as the units and general description.
    """
    objects = ScientificMeasurementTypeManager()

    normalised_name = models.CharField(max_length=50, unique=True)
    display_name = models.CharField(max_length=50, unique=True)

    max_value = models.FloatField()
    min_value = models.FloatField()

    description = models.TextField()

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
    )

    units = models.CharField(max_length=5, choices=UNITS_CHOICES)

    def natural_key(self):
        """Returns the natural key of the measurement type.
        :returns: tuple representing the natural key
        """
        return (self.normalised_name, )

    def __unicode__(self):
        return u"{0} - {1}".format(self.display_name, self.units)


class ScientificPoseMeasurement(models.Model):
    """Scientific Measurement relating to a pose."""
    measurement_type = models.ForeignKey(ScientificMeasurementType)
    pose = models.ForeignKey(Pose)
    value = models.FloatField()

    class Meta:
        """Defines Metaparameters of the model."""
        unique_together = (('measurement_type', 'pose'), )


class ScientificImageMeasurement(models.Model):
    """Scientific Measurement relating to an image."""
    measurement_type = models.ForeignKey(ScientificMeasurementType)
    image = models.ForeignKey(Image)
    value = models.FloatField()

    class Meta:
        """Defines Metaparameters of the model."""
        unique_together = (('measurement_type', 'image'), )


class AUVDeployment(Deployment):
    """Deployment model for AUV data"""
    objects = models.GeoManager()

    def __unicode__(self):
        return "AUV: {0} - {1}".format(self.start_time_stamp, self.short_name)


class BRUVDeployment(Deployment):
    """Model that holds the Baited RUV data """
    objects = models.GeoManager()

    def __unicode__(self):
        return "BRUV: {0} - {1}".format(self.start_time_stamp, self.short_name)



class DOVDeployment(Deployment):
    """Model that holds the Diver Operated data """
    objects = models.GeoManager()

    diver_name = models.TextField()

    def __unicode__(self):
        return "DOV: {0} - {1}".format(self.start_time_stamp, self.short_name)


class TVDeployment(Deployment):
    """Model that holds the Towed Video data """
    objects = models.GeoManager()

    def __unicode__(self):
        return "TV: {0} - {1}".format(self.start_time_stamp, self.short_name)


class TIDeployment(Deployment):
    """Model that holds the Towed Imagery data """
    objects = models.GeoManager()

    def __unicode__(self):
        return "TI: {0} - {1}".format(self.start_time_stamp, self.short_name)
