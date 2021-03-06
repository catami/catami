from django.db import models, transaction
from datetime import datetime
from dateutil.tz import tzutc
from django.contrib.gis.db import models
from django.contrib.auth.models import User
from guardian.shortcuts import get_perms
import math
from catamidb.models import Image, Deployment
from random import sample
from django.db.utils import IntegrityError
from django.core.validators import MinValueValidator, MaxValueValidator
import numpy as np

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
        (3, 'Uniform Grid'),
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

    #secondary annotation code and qualifier 
    annotation_caab_code_secondary = models.CharField(max_length=200, blank=True)
    qualifier_short_name_secondary = models.CharField(max_length=200, blank=True)

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

                point_annotation.annotation_caab_code_secondary = ""
                point_annotation.qualifier_short_name_secondary = ""

                #point_annotation.save()
                points_to_bulk_save.append(point_annotation)

        # do the bulk save - for performance
        PointAnnotation.objects.bulk_create(points_to_bulk_save)

    def import_sampled_points(self, annotation_set, import_data):
        """ create annotation points with information from uploaded CSV and add to this annotation
            set """

        images = annotation_set.images.all()
        points_to_bulk_save = []

        # iterate through the images and create points
        for image in images:
            for annotation in import_data[str(image.deployment.id)][image.image_name]:

                point_annotation = PointAnnotation()
                point_annotation.annotation_set = annotation_set
                point_annotation.image = image
                point_annotation.owner = annotation_set.owner
                point_annotation.x = annotation['Point in Image'].split(',')[0]
                point_annotation.y = annotation['Point in Image'].split(',')[1]

                point_annotation.annotation_caab_code = annotation['Annotation Code']
                point_annotation.qualifier_short_name = annotation['Qualifier Name']

                point_annotation.annotation_caab_code_secondary = annotation['Annotation Code 2']
                point_annotation.qualifier_short_name_secondary = annotation['Qualifier Name 2']

                #point_annotation.save()
                points_to_bulk_save.append(point_annotation)

        # do the bulk save - for performance
        PointAnnotation.objects.bulk_create(points_to_bulk_save)

    def apply_stratified_sampled_points(self, annotation_set, sample_size):
        """ Apply points to the images attached to this annotation set using
            stratified sampling """

        #TODO: implement
        return None

    def apply_uniform_grid_points(self, annotation_set, sample_size):
        """ Apply a uniform grid of points to an image. """

        images = annotation_set.images.all()
        points_to_bulk_save = []

        # take the square root of the sample size and round
        square = math.sqrt(int(sample_size))
        rows = columns = round(square)

        # +1 to the rows and cols
        rows += 1
        columns += 1

        # create the grid
        row_points = np.linspace(0.008, 0.992, num=rows, endpoint=False)
        column_points = np.linspace(0.008, 0.992, num=columns, endpoint=False)

        # pop the first item from the arrays - we do this so we get an even spacing excluding edges
        row_points = np.delete(row_points, 0)
        column_points = np.delete(column_points, 0)

        # apply the points to the images
        for image in images:
            for row in row_points:
                for column in column_points:

                    point_annotation = PointAnnotation()

                    point_annotation.annotation_set = annotation_set
                    point_annotation.image = image
                    point_annotation.owner = annotation_set.owner
                    point_annotation.x = row
                    point_annotation.y = column

                    point_annotation.annotation_caab_code = ""
                    point_annotation.qualifier_short_name = ""

                    point_annotation.annotation_caab_code_secondary = ""
                    point_annotation.qualifier_short_name_secondary = ""

                    #point_annotation.save()
                    points_to_bulk_save.append(point_annotation)

        # do the bulk save - for performance
        PointAnnotation.objects.bulk_create(points_to_bulk_save)

    def apply_fixed_five_points(self, annotation_set):
        """ 5 points based on AIMS standard """

        images = annotation_set.images.all()
        points_to_bulk_save = []

        # create the grid
        row_points = [0.25, 0.25, 0.5, 0.75, 0.75]
        column_points = [0.25, 0.75, 0.5, 0.75, 0.25]

        # apply the points to the images
        for image in images:
            for i in range(int(5)):
                    point_annotation = PointAnnotation()

                    point_annotation.annotation_set = annotation_set
                    point_annotation.image = image
                    point_annotation.owner = annotation_set.owner
                    point_annotation.x = row_points[i]
                    point_annotation.y = column_points[i]

                    point_annotation.annotation_caab_code = ""
                    point_annotation.qualifier_short_name = ""

                    point_annotation.annotation_caab_code_secondary = ""
                    point_annotation.qualifier_short_name_secondary = ""

                    #point_annotation.save()
                    points_to_bulk_save.append(point_annotation)

        # do the bulk save - for performance
        PointAnnotation.objects.bulk_create(points_to_bulk_save)

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

                whole_image_annotation.annotation_caab_code_secondary = ""
                whole_image_annotation.qualifier_short_name_secondary = ""

                points_to_bulk_save.append(whole_image_annotation)

        # do the bulk save - for performance
        WholeImageAnnotation.objects.bulk_create(points_to_bulk_save)

    def import_whole_image_points(self,annotation_set, import_data):
        """ create annotation points with information from uploaded CSV and add to this annotation
            set """

        images = annotation_set.images.all()
        points_to_bulk_save = []

        # iterate through the images and create points
        for image in images:
            for annotation in import_data[str(image.deployment.id)][image.image_name]:
                whole_image_annotation = WholeImageAnnotation()

                whole_image_annotation.annotation_set = annotation_set
                whole_image_annotation.image = image
                whole_image_annotation.owner = annotation_set.owner

                whole_image_annotation.annotation_caab_code = annotation['Annotation Code']
                whole_image_annotation.qualifier_short_name = ['Qualifier Name']

                whole_image_annotation.annotation_caab_code_secondary = annotation['Annotation Code']
                whole_image_annotation.qualifier_short_name_secondary = ['Qualifier Name 2']

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
                                    qualifier_short_name=annotation.qualifier_short_name,
                                    coverage_percentage=annotation.coverage_percentage).save()

    def check_if_images_have_same_annotations(self, annotation_set_id, image_one, image_two):

        # get whole image annotations for the source image
        image_one_annotations = WholeImageAnnotation.objects.filter(annotation_set=annotation_set_id,
                                                                    image=image_one)

        # get whole image annotations for the destination image
        image_two_annotations = WholeImageAnnotation.objects.filter(annotation_set=annotation_set_id,
                                                                    image=image_two)

        results_one = image_one_annotations.filter(annotation_caab_code="")
        results_two = image_two_annotations.filter(annotation_caab_code="")

        # if there are no annoatations on either, then not the same
        if (image_one_annotations.count() or image_two_annotations.count()) == 0:
            return "false"

        if results_one.count() == image_one_annotations.count():
            return "false"

        if results_two.count() == image_two_annotations.count():
            return "false"

        #if sizes are different, then they are not the same
        if image_one_annotations.count() != image_two_annotations.count():
            return "false"

        # loop through and check if A and B have the same contents
        for annotation in image_one_annotations:
            results = image_two_annotations.filter(annotation_caab_code=annotation.annotation_caab_code,
                                                   coverage_percentage=annotation.coverage_percentage)

            # no ? then these lists are not the same
            if results.count() == 0:
                return "false"

        return "true"


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

    # -1 signifies that no percentage cover has been given
    coverage_percentage = models.IntegerField(validators = [MinValueValidator(-1), MaxValueValidator(100)], default = -1)
