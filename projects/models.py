from django.db import models
from datetime import datetime
from dateutil.tz import tzutc
from django.contrib.gis.db import models
from django.contrib.auth.models import User
from catamidb.models import GenericImage, GenericDeployment
from random import sample
from django.db.utils import IntegrityError
from django.core.validators import MinValueValidator, MaxValueValidator

import logging


class AnnotationCodes(models.Model):
    """The base annotation (CAAB) structure.

    This stores all the levels of the classifaction tree
    with parent filled in as appropriate.
    """
    caab_code = models.CharField(max_length=8, unique=True) # 8 numbers
    cpc_code = models.CharField(max_length=5, unique=True) # CPC Code file code
    point_colour = models.CharField(max_length=6) # hex RGB colour
    code_name = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    parent = models.ForeignKey(
            'projects.AnnotationCodes',
            blank=True,
            null=True
        )

    def __unicode__(self):
        return "{0} - ({1})".format(self.code_name, self.caab_code)


class QualifierCodes(models.Model):
    """Qualifiers to annotations.

    Examples include anthropogenic labels, or natural labels
    that include bleaching, dead etc.
    """
    parent = models.ForeignKey('self', blank=True, null=True, related_name="children")
    short_name = models.CharField(max_length=200)
    description = models.CharField(max_length=200)

    #active - should this be displayed to the users
    #in case you want to keep the label for historical purposes,
    # but not display it to the users
    active = models.BooleanField()


class Project(models.Model):
    """
    Projects contain a set of images that a user works with. They also have
    associated worksets which are image sets to annotate.
    """

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    owner = models.ForeignKey(User, null=True)
    creation_date = models.DateTimeField()
    modified_date = models.DateTimeField()
    generic_images = models.ManyToManyField(GenericImage, null=True)

    class Meta:
        unique_together = (('owner', 'name', 'creation_date'), )
        permissions = (
            ('view_project', 'View the project.'),
        )


class GenericAnnotationSet(models.Model):
    """
    An annotated set is used to contain a set of images to be annotated.
    """

    IMAGE_SAMPLING_METHODOLOGY_CHOICES = (
        (0, 'Random'),
        (1, 'Stratified'),
        (2, 'Spatial'),
    )

    ANNOTATATION_SAMPLING_METHODOLOGY_CHOICES = (
        (0, 'Random Point'),
        (1, 'Stratified'),
        (2, 'Fixed 5 Point'),
        (3, 'Percentage Cover'),
    )

    project = models.ForeignKey('projects.Project')
    owner = models.ForeignKey(User, null=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    creation_date = models.DateTimeField()
    modified_date = models.DateTimeField()
    generic_images = models.ManyToManyField(GenericImage, related_name='projects')
    image_sampling_methodology = models.IntegerField(choices=IMAGE_SAMPLING_METHODOLOGY_CHOICES)
    annotation_methodology = models.IntegerField(choices=ANNOTATATION_SAMPLING_METHODOLOGY_CHOICES)

    class Meta:
        unique_together = (('owner', 'name', 'creation_date'), )
        permissions = (
            ('view_genericannotationset', 'View the generic annotation set.'),
        )


class GenericAnnotation(models.Model):
    """The common base for Point and Whole image annotations.
    """

    image = models.ForeignKey('catamidb.GenericImage')
    owner = models.ForeignKey(User, null=True)

    #loose reference to AnnotationCode table
    annotation_caab_code = models.CharField(max_length=200)

    #loose reference to qualifier table
    qualifier_short_name = models.CharField(max_length=200)

    class Meta:
        """Defines Metaparameters of the model."""
        abstract = True


class GenericPointAnnotation(GenericAnnotation):
    """
    A Point annotation.

    Contains position within the image (as a percent from top left) and
    the set to which it belongs.
    """

    generic_annotation_set = models.ForeignKey('projects.GenericAnnotationSet')

    x = models.FloatField(validators = [MinValueValidator(0.0), MaxValueValidator(100.0)])
    y = models.FloatField(validators = [MinValueValidator(0.0), MaxValueValidator(100.0)])


class GenericWholeImageAnnotation(GenericAnnotation):
    """
    A Whole Image annotation.

    Needed to distinguish the difference between point and whole image
    annotation.
    """

    generic_annotation_set = models.ForeignKey('projects.GenericAnnotationSet')