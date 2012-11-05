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

    def __unicode__(self):
        return "{0} - {1}".format(self.date_start, self.short_name)

    def natural_key(self):
        """@return natural_key date_start short_name """
        return (self.date_start, self.short_name)

    class Meta:
        """@brief defines the natural key pair"""
        unique_together = (('date_start','short_name'),)

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

    def __unicode__(self):
        # want to attempt to autodetect which subtype this is...
        subtypes = ['bruvdeployment', 'auvdeployment', 'dovdeployment']

        for subtype in subtypes:
            try:
                subclass = getattr(self, subtype)
            except self.DoesNotExist:
                continue # go to the next
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
        unique_together = (('start_time_stamp','short_name'),)
    
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
    temperature = models.FloatField()
    salinity = models.FloatField()
    pitch = models.FloatField()
    roll = models.FloatField()
    yaw = models.FloatField()
    altitude = models.FloatField()
    depth = models.FloatField()

    def natural_key(self):
        """@return natural_key deployment date_time  """
        return self.deployment.natural_key() + (self.dateTime,)
    natural_key.dependencies = ['Force.deployment']

    class Meta:
        """@brief defines the natural key pair"""
        unique_together = (('deployment', 'date_time'),)

class User(models.Model):
    '''
    @brief contains all of the information for the database users
    '''
    #==================================================#
    # name <Char> : The name of the usr
    # title <Char> : Mr, Mrs etc
    # organisation <Char> : Name of the organisation the user works for
    # email <email> : The users email
    #==================================================#

    name = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    organisation = models.CharField(max_length=200)
    email = models.EmailField()

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

class Annotation(models.Model):
    """@brief Model that hold the annotation data refering to the images"""

    # ??? Do we want differnt annotation types?  ie an abstract class ???

    #==================================================#
    # Type/Method (5point, percent cover) : Text
    # ImageReference : image Id
    # Code (Substrate, Species) : text
    # Point, Region - find better way : point in image x,y
    # UserWhoAnnotated : user reference
    # Comments / notes : Text
    #==================================================#

    method = models.TextField()
    image_reference = models.ForeignKey(Image)
    code = models.CharField(max_length=200)
    point = models.PointField()
    user_who_annotated = models.ForeignKey(User)
    comments = models.TextField()

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
