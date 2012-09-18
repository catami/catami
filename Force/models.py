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

class campaign(models.Model):
    '''
    @brief A campain describes a field campaign that has many deployments.
    '''
    #==================================================#
    # shortName <Text> : is a short name for the campaign
    # description <Text> : is a general description of the campaign
    # associateResearchers <array> :
    # associatedPublications <array> :
    # associatedResearchGrant <array> :
    # deployments <unique id> :
    # date start <dateTime> :
    # date End <dateTime> : 
    #==================================================#

    shortName=models.CharField(max_length=100)
    description=models.TextField()
    associatedResearchers=dbarray.TextArrayField()
    associatedPublications=dbarray.TextArrayField()
    associatedResearchGrant=dbarray.TextArrayField()
    dateStart=models.DateField()
    dateEnd=models.DateField()

class deployment(models.Model):
    ''' 
    @brief This is the abstract deployment class.  
    '''
    startPosition=models.PointField()
    startTimeStamp=models.DateTimeField()
    endTimeStamp=models.DateTimeField()
    shortName=models.CharField(max_length=100)
    missionAim=models.TextField()
    minDepth=models.FloatField()
    maxDepth=models.FloatField()
    campaign=models.ForeignKey(campaign)

    #class Meta:
    #    abstract = True
    
class image(models.Model):
    '''
    @brief This is the abstract image class, mono images reference use the left imgage field
    '''

    # ??? Maybe make an image reference class and instantiate left and right instances ?????

    deployment=models.ForeignKey(deployment)
    leftThumbnailReference=models.URLField() #!!!!ImageField(upload_to='photos/%Y/%m/%d')
    leftImageReference=models.URLField()
    dateTime=models.DateTimeField()
    imagePosition=models.PointField()
    temperature=models.FloatField()
    salinity=models.FloatField()
    pitch=models.FloatField()
    roll=models.FloatField()
    yaw=models.FloatField()
    altitude=models.FloatField()
    depth=models.FloatField()

    #class Meta:
    #    abstract = True
    
class user(models.Model):
    '''
    @breif contains all of the information for the database users
    '''
    #==================================================#
    # name <Char> : The name of the usr
    # title <Char> : Mr, Mrs etc
    # Organisation <Char> : Name of the organisation the user works for
    # email <email> : The users email
    #==================================================#

    name=models.CharField(max_length=200)
    title=models.CharField(max_length=200)
    organisation=models.CharField(max_length=200)
    email=models.EmailField()
 
class auvDeployment(deployment):
    '''
    @brief AUV meta data
    '''
    #==================================================#
    # StartPosition : <point>
    # distanceCovered : <double>
    # startTimeStamp : <dateTime>
    # endTimeStamp : <dateTime>
    # transectShape : <Polygon>
    # shortName <Text> : is a short name for the deployment
    # missionAim : <Text>
    # minDepth : <double>
    # maxDepth : <double> 
    #--------------------------------------------------#
    # Maybe need to add unique AUV fields here later when
    # we have more deployments
    #==================================================#

    transectShape=models.PolygonField()
    distanceCovered=models.FloatField()

class stereoImages(image):
    '''
    @brief
    '''
    #==================================================#
    # deployment : <deployment ID>
    # leftThumbnailReference : <Text blob>
    # leftImageReference : <url>
    # rightThumbnailReference : <Text blob>
    # rightImageReference : <url>
    # dateTime : <DateTime>
    # imagePosition : <point>
    # Temperature : <real>
    # Salinity : <real>
    # Pitch : <real>
    # Roll : <real>
    # Yaw : <real>
    # altitude : <real>
    # depth : <real>
    #==================================================#

    rightThumbnailReference=models.URLField()#!!!!!!!ImageField(upload_to='photos/%Y/%m/%d')
    rightImageReference=models.URLField()

class annotations(models.Model):
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

    method=models.TextField()
    imageReference=models.ForeignKey(image) # Check this! How to link back to table field
    code=models.CharField(max_length=200)
    point=models.PointField() # Do we need a list of points ?  ie 5 point method?
    userWhoAnnotated=models.ForeignKey(user)
    comments=models.TextField()
