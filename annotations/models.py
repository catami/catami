"""Data models for the annotation component.
"""
from django.db import models
from django.contrib.auth.models import User


class AnnotationCode(models.Model):
    """The base annotation (CAAB) structure.
    
    This stores all the levels of the classifaction tree
    with parent filled in as appropriate.
    """
    code_name = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    parent = models.ForeignKey('annotations.AnnotationCode')


class QualifierCode(models.Model):
    """Qualifiers to annotations.

    Examples include anthropogenic labels, or natural labels
    that include bleaching, dead etc.
    """
    modifier_name = models.CharField(max_length=100)
    description = models.CharField(max_length=200)


class AnnotationSet(models.Model):
    """The common base for Point and Whole image annotation sets.
    """
    collection = models.ForeignKey('collection.Collection')
    owner = models.ForeignKey(User)
    name = models.CharField(max_length=100)

    class Meta:
        """Defines Metaparameters of the model."""
        abstract = True


class Annotation(models.Model):
    """The common base for Point and Whole image annotations.
    """
    image = models.ForeignKey('catamidb.Pose')
    label = models.ForeignKey('annotations.AnnotationCode')
    labeller = models.ForeignKey(User)

    class Meta:
        """Defines Metaparameters of the model."""
        abstract = True

POINT_METHODOLOGIES = (
    (0, 'Random Point'),
    (1, 'Stratified'),
    (2, 'Fixed Pattern'),
)


class PointAnnotationSet(AnnotationSet):
    """Point Annotation Container.

    Relates a collection/workset to a set of annotations and
    the methodologies used to create them.
    """
    # a choice of methodology
    methodology = models.IntegerField(choices=POINT_METHODOLOGIES)
    # an integer parameter (for random selection, stratified etc)
    # not always used
    count = models.IntegerField()

LEVELS = (
    (0, "Primary"),
    (1, "Secondary"),
    (2, "Tertiary"),
)


class PointAnnotation(Annotation):
    """A Point annotation.

    Contains position within the image (as a percent from top left) and
    the set to which it belongs.
    """
    annotation_set = models.ForeignKey(
            PointAnnotationSet,
            related_name='images'
        )
    x = models.FloatField()
    y = models.FloatField()
    level = models.IntegerField(choices=LEVELS)
    qualifiers = models.ManyToManyField(
            'QualifierCode',
            related_name='point_annotations'
        )


class ImageAnnotationSet(AnnotationSet):
    """A Whole Image annotation set.
    """
    pass

COVER = (
    (0, "C > 80%"),
    (1, "60% < C < 80%"),
    (2, "40% < C < 60%"),
    (3, "20% < C < 40%"),
    (4, "C < 20%"),
)


class ImageAnnotation(Annotation):
    """A Whole Image annotation.

    Contains the percent cover for the dominant class.
    """
    annotation_set = models.ForeignKey(
            ImageAnnotationSet,
            related_name='images'
        )
    cover = models.IntegerField(choices=COVER)
    qualifiers = models.ManyToManyField(
            'QualifierCode',
            related_name='image_annotations'
        )
