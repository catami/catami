from django.db import models
from django_orm.postgresql.fields.arrays import ArrayField
from django_orm.postgresql.manager import Manager

from Force.models import Image

class ImageFeature(models.Model):
    """Extends Force.Image to include feature arrays for clustering and classification"""

    feature = ArrayField(dbtype='double precision')
<<<<<<< HEAD
    #image = models.OneToOneField(Image)
    image = models.ForeignKey(Image)
||||||| merged common ancestors
    image = models.OneToOneField(Image)
=======
    image = models.OneToOneField(Image)
    objects = Manager()
>>>>>>> 903b07fc6266e9eb34c2b7ae8fa1acc66d5a05e8

