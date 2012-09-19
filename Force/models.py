from django.db import models
#from django_postgresql.manager import PgManager
from django.contrib.gis.db import models
from django.contrib.gis.geos import GEOSGeometry

import dbarray

#==================================================#
# Created Dan marrable 4/09/2012
# d.marrable@ivec.org
#
# Edits :: Name : Date : description
#
#==================================================#

class CampaignManager(models.Manager):
    def get_by_natural_key(self, date_start, short_name):
        return self.get(date_start=date_start, short_name=short_name)

class Campaign(models.Model):
    '''
    @brief A campain describes a field campaign that has many deployments.
    '''
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
    associated_researchers = dbarray.TextArrayField()
    associated_publications = dbarray.TextArrayField()
    associated_research_grant = dbarray.TextArrayField()
    date_start = models.DateField()
    date_end = models.DateField()

    def natural_key(self):
        return (self.dateStart, self.short_name)

    class Meta:
        unique_together = (('date_start','short_name'),)

class DeploymentManager(models.Manager):
    def get_by_natural_key(self, start_time_stamp, short_name):
        return self.get(start_time_stamp=start_time_stamp, short_name=short_name)

class Deployment(models.Model):
    ''' 
    @brief This is the abstract deployment class.  
    '''
    objects = DeploymentManager()
    start_position = models.PointField()
    start_time_stamp = models.DateTimeField()
    end_time_stamp = models.DateTimeField()
    short_name = models.CharField(max_length=100)
    mission_aim = models.TextField()
    min_depth = models.FloatField()
    max_depth = models.FloatField()
    campaign = models.ForeignKey(Campaign)

    def natural_key(self):
        return (self.start_time_stamp, self.short_name)

    class Meta:
        unique_together = (('start_time_stamp','short_name'),)
    
class ImageManager(models.Manager):
    def get_by_natural_key(self, deployment_key, date_time):
        depplyment = deployment.objects.get_by_natural_key(*deployment_key)
        return self.get(deployment=deployment, date_time=date_time)


class Image(models.Model):
    '''
    @brief This is the abstract image class, mono images reference use the left imgage field
    '''

    # ??? Maybe make an image reference class and instantiate left and right instances ?????

    objects = ImageManager()

    deployment = models.ForeignKey(Deployment)
    left_thumbnail_reference = models.URLField() #!!!!ImageField(upload_to='photos/%Y/%m/%d')
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
        return self.deployment.natural_key() + (self.dateTime,)
    natural_key.dependencies = ['Force.deployment']

    class Meta:
        unique_together = (('deployment', 'date_time'),)

class User(models.Model):
    '''
    @breif contains all of the information for the database users
    '''
    #==================================================#
    # name <Char> : The name of the usr
    # title <Char> : Mr, Mrs etc
    # organisation <Char> : Name of the organisation the user works for
    # email <email> : The users email
    #==================================================#

    name=models.CharField(max_length=200)
    title=models.CharField(max_length=200)
    organisation=models.CharField(max_length=200)
    email=models.EmailField()
 
class AUVDeployment(Deployment):
    '''
    @brief AUV meta data
    '''
    #==================================================#
    # start_position : <point>
    # start_time_tamp : <dateTime>
    # end_time_stamp : <dateTime>
    # short_name <Text> : is a short name for the deployment
    # mission_aim : <Text>
    # min_depth : <double>
    # max_depth : <double> 
    #--------------------------------------------------#
    # Maybe need to add unique AUV fields here later when
    # we have more deployments
    #==================================================#

    transect_shape = models.PolygonField()
    distance_covered = models.FloatField()

class StereoImage(Image):
    '''
    @brief
    '''
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

    right_thumbnail_reference = models.URLField()#!!!!!!!ImageField(upload_to='photos/%Y/%m/%d')
    right_image_reference = models.URLField()

class Annotations(models.Model):
    '''
    @brief
    '''

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
    image_reference = models.ForeignKey(Image) # Check this! How to link back to table field
    code = models.CharField(max_length=200)
    point = models.PointField() # Do we need a list of points ?  ie 5 point method?
    user_who_annotated = models.ForeignKey(User)
    comments = models.TextField()
