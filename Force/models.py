"""@brief This module hold the django models that will populate the
catami database.

Created Dan marrable 4/09/2012
d.marrable@ivec.org

Edits :: Name : Date : description

"""

from django.db import models
#from django_postgresql.manager import PgManager
from django.contrib.gis.db import models

#from django.contrib.gis.geos import GEOSGeometry

class CampaignManager(models.GeoManager):
    """@brief Define a natural key for the Campaign class and return
    date_start and short_name keypair
    
    """

    def get_by_natural_key(self, date_start, short_name):
        """@brief Accessor method for natural key
        @return natural_key pair

        """
        return self.get(date_start=date_start, short_name=short_name)


class Campaign(models.Model):
    """@brief A campain describes a field campaign that has many deployments."""
    #==================================================#
    # short_name <Text> : is a short name for the campaign
    # description <Text> : is a general description of the campaign
    # associate_researchers <array> :
    # associated_publications <array> :
    # associated_research_grant <array> :
    # deployments <unique id> :
    # date_start <dateTime> :
    # date_end <dateTime> :
    #==================================================#
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
        """@return natural_key date_start short_name """
        return (self.date_start, self.short_name)

    class Meta:
        """@brief defines the natural key pair"""
        unique_together = (('date_start', 'short_name'), )


class DeploymentManager(models.GeoManager):
    """@brief Define a natural key for the Deployment class and return
    start_time and short_name keypair
    
    """

    def get_by_natural_key(self, start_time_stamp, short_name):
        """@brief Accessor method for the natural key
        @return natural key start_time_stamp short_name pair

        """
        return self.get(start_time_stamp=start_time_stamp,
                        short_name=short_name)


class Deployment(models.Model):
    """ @brief This is the super deployment class which holds all
    of the common data types for all types of deployments.  Unique
    data types should be extended with sub classes 

    """
    objects = DeploymentManager()
    start_position = models.PointField()
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
        # want to attempt to autodetect which subtype this is...
        subtypes = ['bruvdeployment', 'auvdeployment', 'dovdeployment']

        for subtype in subtypes:
            try:
                subclass = getattr(self, subtype)
            except self.DoesNotExist:
                continue  # go to the next
            else:
                return subclass.__unicode__()
        else:
            # if we don't match a subtype...
            return "Deployment: {0} - {1}".format(self.start_time_stamp, self.short_name)

    def natural_key(self):
        """@return natural_key start_time_stamp short_name """
        return (self.start_time_stamp, self.short_name)

    class Meta:
        """@brief defines the natural key pair"""
        unique_together = (('start_time_stamp', 'short_name'), )


class ImageManager(models.Manager):
    """@brief Define a natural key for the Image class and return
    date_start and short_name keypair
    
    """

    def get_by_natural_key(self, deployment_key, date_time):
        """@brief Accessor method for natural key
        @return natural_key deployment date_time paie

        """
        deployment = Deployment.objects.get_by_natural_key(*deployment_key)
        return self.get(deployment=deployment, date_time=date_time)


class Image(models.Model):
    """@brief This is the super image class, mono images reference use the left
    imgage field.  Stereo images extend this class
    
    """
    objects = ImageManager()

    deployment = models.ForeignKey(Deployment)
    left_thumbnail_reference = models.URLField()
    left_image_reference = models.URLField()
    date_time = models.DateTimeField()
    image_position = models.PointField()
    depth = models.FloatField()

    def natural_key(self):
        """@return natural_key deployment date_time  """
        return self.deployment.natural_key() + (self.dateTime, )
    natural_key.dependencies = ['Force.deployment']

    class Meta:
        """@brief defines the natural key pair"""
        unique_together = (('deployment', 'date_time'), )


class ScientificMeasurementTypeManager(models.Manager):
    """Management class for ScientificMeasurementType."""

    def get_by_natural_key(self, normalised_name):
        """Accessor to query for type based on normalised name."""
        return self.get(normalised_name=normalised_name)


class ScientificMeasurementType(models.Model):
    normalised_name = models.CharField(max_length=50)
    display_name = models.CharField(max_length=50)

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
        return (self.normalised_name, )


class ScientificMeasurementManager(models.Manager):
    """Manager class for ScientificMeasurements."""

    def get_by_natural_key(self, measurement_type_key, image_key):
        """Accessor to query for value based on measurement type and image."""
        mt = ScientificMeasurementType.objects.get_by_natural_key(*measurement_type_key)
        im = Image.objects.get_by_natural_key(*image_key)

        return self.get(measurement_type=mt, image=im)


class ScientificMeasurement(models.Model):
    measurement_type = models.ForeignKey(ScientificMeasurementType)
    image = models.ForeignKey(Image)
    value = models.FloatField()

    def natural_key(self):
        return self.measurement_type.natural_key() + self.image.natural_key()

    natural_key.dependencies = ['Force.image', 'Force.scientificmeasurementtype']

    class Meta:
        unique_together = (('measurement_type', 'image'), )


class AUVDeployment(Deployment):
    """@brief Deployment model for AUV data"""
    #==================================================#
    # start_position : <point>
    # start_time_stamp : <dateTime>
    # end_time_stamp : <dateTime>
    # short_name <Text> : is a short name for the deployment
    # mission_aim : <Text>
    # min_depth : <double>
    # max_depth : <double>
    #--------------------------------------------------#
    # Maybe need to add unique AUV fields here later when
    # we have more deployments
    #==================================================#
    objects = models.GeoManager()
    transect_shape = models.PolygonField()
    distance_covered = models.FloatField()

    def __unicode__(self):
        return "AUV: {0} - {1}".format(self.start_time_stamp, self.short_name)


class StereoImage(Image):
    """@brief Extends the image class to include right images"""
    #==================================================#
    # deployment : <deployment ID>
    # left_thumbnail_reference : <Text blob>
    # left_image_reference : <url>
    # right_thumbnail_reference : <Text blob>
    # right_image_reference : <url>
    # date_time : <DateTime>
    # image_position : <point>
    # temperature : <real>
    # salinity : <real>
    # pitch : <real>
    # roll : <real>
    # yaw : <real>
    # altitude : <real>
    # depth : <real>
    #==================================================#

    right_thumbnail_reference = models.URLField()
    right_image_reference = models.URLField()


class BRUVDeployment(Deployment):
    """@brief Model that holds the Baited RUV data """
    objects = models.GeoManager()

    def __unicode__(self):
        return "BRUV: {0} - {1}".format(self.start_time_stamp, self.short_name)


class DOVDeployment(Deployment):
    """@brief Model that holds the Diver Operated data """
    objects = models.GeoManager()

    diver_name = models.TextField()

    def __unicode__(self):
        return "DOV: {0} - {1}".format(self.start_time_stamp, self.short_name)


class TVDeployment(Deployment):
    """@brief Model that holds the Towed Video data """
    objects = models.GeoManager()

    def __unicode__(self):
        return "TV: {0} - {1}".format(self.start_time_stamp, self.short_name)


class TIDeployment(Deployment):
    """@brief Model that holds the Towed Imagery data """
    objects = models.GeoManager()

    def __unicode__(self):
        return "TI: {0} - {1}".format(self.start_time_stamp, self.short_name)
