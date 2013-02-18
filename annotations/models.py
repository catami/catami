from django.db import models
from django.contrib.auth.models import User

class AnnotationCode(models.Model):
    code_name = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    parent = models.ForeignKey('annotations.AnnotationCode')


class QualifierCode(models.Model):
    modifier_name = models.CharField(max_length=100)
    description = models.CharField(max_length=200)


class AnnotationSet(models.Model):
    collection = models.ForeignKey('collection.Collection')
    owner = models.ForeignKey(User)
    name = models.CharField(max_length=100)

    class Meta:
        abstract = True


class Annotation(models.Model):
    image = models.ForeignKey('Force.image')
    label = models.ForeignKey('annotations.AnnotationCode')
    labeller = models.ForeignKey(User)

    class Meta:
        abstract = True


POINT_METHODOLOGIES = (
    (0, 'Random Point'),
    (1, 'Stratified'),
    (2, 'Fixed Pattern'),
)
class PointAnnotationSet(AnnotationSet):
    methodology = models.IntegerField(choices=POINT_METHODOLOGIES)
    count = models.IntegerField()


LEVELS = (
    (0, "Primary"),
    (1, "Secondary"),
    (2, "Tertiary"),
)
class PointAnnotation(Annotation):
    annotation_set = models.ForeignKey(PointAnnotationSet, related_name='images')
    x = models.FloatField()
    y = models.FloatField()
    level = models.IntegerField(choices=LEVELS)


class ImageAnnotationSet(AnnotationSet):
    pass


COVER = (
    (0, "C > 80%"),
    (1, "60% < C < 80%"),
    (2, "40% < C < 60%"),
    (3, "20% < C < 40%"),
    (4, "C < 20%"),
)
class ImageAnnotation(Annotation):
    annotation_set = models.ForeignKey(ImageAnnotationSet, related_name='images')
    cover = models.IntegerField(choices=COVER)


# refactor as many to many?
# or as m2m through?
class PointQualifier(models.Model):
    qualifier_code = models.ForeignKey(QualifierCode)
    point_annotation = models.ForeignKey(PointAnnotation)


class ImageQualifier(models.Model):
    qualifier_code = models.ForeignKey(QualifierCode)
    image_annotation = models.ForeignKey(ImageAnnotation)
