from django.db import models, transaction
from datetime import datetime
from dateutil.tz import tzutc
from django.contrib.gis.db import models
from django.contrib.auth.models import User
from guardian.shortcuts import get_perms
from catamidb.models import Image, Deployment
from random import sample
from django.db.utils import IntegrityError
from django.core.validators import MinValueValidator, MaxValueValidator

import random
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
    images = models.ManyToManyField(Image, null=True)

    class Meta:
        unique_together = (('owner', 'name', 'creation_date'), )
        permissions = (
            ('view_project', 'View the project.'),
        )


class AnnotationSet(models.Model):
    """
    An annotated set is used to contain a set of images to be annotated.
    """

    IMAGE_SAMPLING_METHODOLOGY_CHOICES = (
        (0, 'Random'),
        (1, 'Stratified'),
        (2, 'Spatial'),
        (3, 'All'),
    )

    POINT_SAMPLING_METHODOLOGY_CHOICES = (
        (-1, 'Not Applicable'),
        (0, 'Random Point'),
        (1, 'Stratified Point'),
        (2, 'Fixed 5 Point'),
    )

    ANNOTATATION_SET_TYPE_CHOICES = (
        (0, 'Point'),
        (1, 'Whole Image'),
    )

    project = models.ForeignKey('projects.Project')
    owner = models.ForeignKey(User, null=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    creation_date = models.DateTimeField()
    modified_date = models.DateTimeField()
    images = models.ManyToManyField(Image, related_name='projects')
    image_sampling_methodology = models.IntegerField(choices=IMAGE_SAMPLING_METHODOLOGY_CHOICES)
    point_sampling_methodology = models.IntegerField(choices=POINT_SAMPLING_METHODOLOGY_CHOICES)
    annotation_set_type = models.IntegerField(choices=ANNOTATATION_SET_TYPE_CHOICES)

    class Meta:
        unique_together = (('owner', 'name', 'creation_date'), )
        permissions = (
            ('view_annotationset', 'View the  annotation set.'),
        )


class Annotation(models.Model):
    """The common base for Point and Whole image annotations.
    """

    image = models.ForeignKey('catamidb.Image')
    owner = models.ForeignKey(User, null=True)

    #loose reference to AnnotationCode table
    annotation_caab_code = models.CharField(max_length=200)

    #loose reference to qualifier table
    qualifier_short_name = models.CharField(max_length=200)

    class Meta:
        """Defines Metaparameters of the model."""
        abstract = True


class PointAnnotationManager(models.Manager):
    """ Handles logic functions related to points annotations """

    def apply_random_sampled_points(self, annotation_set, sample_size):
        """ Randomly apply points to the images attached to this annotation
            set """

        images = annotation_set.images.all()
        points_to_bulk_save = []

        # iterate through the images and create points
        for image in images:
            for i in range(int(sample_size)):

                point_annotation = PointAnnotation()

                point_annotation.annotation_set = annotation_set
                point_annotation.image = image
                point_annotation.owner = annotation_set.owner
                point_annotation.x = random.uniform(0.008, 0.992) #random.random()
                point_annotation.y = random.uniform(0.008, 0.992)

                point_annotation.annotation_caab_code = ""
                point_annotation.qualifier_short_name = ""

                #point_annotation.save()
                points_to_bulk_save.append(point_annotation)

        # do the bulk save - for performance
        PointAnnotation.objects.bulk_create(points_to_bulk_save)

    def apply_stratified_sampled_points(self, annotation_set, sample_size):
        """ Apply points to the images attached to this annotation set using
            stratified sampling """

        #TODO: implement
        return None


class WholeImageAnnotationManager(models.Manager):
    """ Handles logic functions related to whole image annotations """

    def apply_whole_image_points(self, annotation_set):
        """ Randomly apply points to the images attached to this annotation
            set """
            
        whole_image_annotation_count = 4
        images = annotation_set.images.all()
        points_to_bulk_save = []

        # iterate through the images and create points
        for image in images:
            for i in range(whole_image_annotation_count):
                whole_image_annotation = WholeImageAnnotation()

                whole_image_annotation.annotation_set = annotation_set
                whole_image_annotation.image = image
                whole_image_annotation.owner = annotation_set.owner

                whole_image_annotation.annotation_caab_code = ""
                whole_image_annotation.qualifier_short_name = ""

                points_to_bulk_save.append(whole_image_annotation)

        # do the bulk save - for performance
        WholeImageAnnotation.objects.bulk_create(points_to_bulk_save)

    @transaction.commit_on_success
    def copy_annotations_to_image(self, annotation_set_id, source_image_id, destination_image_id):
        """
        Copies whole image annotations from one image to another
        """

        # get whole image annotations for the source image
        source_image_annotations = WholeImageAnnotation.objects.filter(annotation_set=annotation_set_id,
                                                                       image=source_image_id)

        # get whole image annotations for the destination image
        destination_image_annotations = WholeImageAnnotation.objects.filter(annotation_set=annotation_set_id,
                                                                            image=destination_image_id)

        # delete the annotations from destination
        for annotation in destination_image_annotations:
            annotation.delete()

        # copy annotations from source
        for annotation in source_image_annotations:
            WholeImageAnnotation(annotation_set_id=annotation_set_id,
                                    image_id=destination_image_id,
                                    annotation_caab_code=annotation.annotation_caab_code,
                                    qualifier_short_name=annotation.qualifier_short_name).save()


class PointAnnotation(Annotation):
    """
    A Point annotation.

    Contains position within the image (as a percent from top left) and
    the set to which it belongs.
    """

    annotation_set = models.ForeignKey('projects.AnnotationSet')

    x = models.FloatField(validators = [MinValueValidator(0.0), MaxValueValidator(100.0)])
    y = models.FloatField(validators = [MinValueValidator(0.0), MaxValueValidator(100.0)])


class WholeImageAnnotation(Annotation):
    """
    A Whole Image annotation.

    Needed to distinguish the difference between point and whole image
    annotation.
    """

    annotation_set = models.ForeignKey('projects.AnnotationSet')