"""Data models for the annotation component.
"""
from django.db import models
from django.contrib.auth.models import User


class AnnotationCode(models.Model):
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
            'annotations.AnnotationCode',
            blank=True,
            null=True
        )

    def __unicode__(self):
        return "{0} - ({1})".format(self.code_name, self.caab_code)


class QualifierCode(models.Model):
    """Qualifiers to annotations.

    Examples include anthropogenic labels, or natural labels
    that include bleaching, dead etc.
    """
    modifier_name = models.CharField(max_length=100)
    description = models.CharField(max_length=200)

    def __unicode__(self):
        return self.modifier_name


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
    image = models.ForeignKey('catamidb.Image')
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

class PointAnnotationManager(models.Manager):
    """Manager for PointAnnotationSet.

    Helps create the pointannotations for images
    within the set.
    """

    def create_annotations(self, annotation_set, image, labeller):

        if annotation_set.methodology == 0:
            random_point(annotation_set, image, labeller)
        else:
            # don't know what to do... invalid choice etc.
            pass

    def random_point(annotation_set, image, labeller):
        import random
        for i in xrange(annotation_set.count):
            x = random.random()
            y = random.random()

            ann = PointAnnotation()

            ann.annotation_set = annotation_set
            ann.image = image
            ann.labeller = labeller
            ann.x = x
            ann.y = y

            ann.label = AnnotationCode.objects.get(id=1) # not considered
            ann.level = 0 # not considered

            ann.save()

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

    def __unicode__(self):
        return "{0} ({1} - {2}: {3})".format(
                self.name,
                self.collection.name,
                POINT_METHODOLOGIES[self.methodology][1],
                self.count
            )

    class Meta:
        unique_together = (('owner', 'name', 'collection'), )
        permissions = (
                ('create_pointannotationset', 'Create a pointannotation set'),
                ('view_pointannotationset', 'View pointannotation set'),
            )



LEVELS = (
    (0, "Not Specified"),
    (1, "Primary"),
    (2, "Secondary"),
    (3, "Tertiary"),
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

    objects = PointAnnotationManager()


class ImageAnnotationSet(AnnotationSet):
    """A Whole Image annotation set.
    """

    class Meta:
        unique_together = (('owner', 'name', 'collection'), )


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
