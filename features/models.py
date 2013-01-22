from django.db import models
from django_orm.postgresql.fields.arrays import ArrayField
from django_orm.postgresql.manager import Manager

import logging
from Force.models import Image

logger = logging.getLogger(__name__)

class ImageFeature(models.Model):
    """Extends Force.Image to include feature arrays for clustering and classification"""

    feature = ArrayField(dbtype='double precision')
    image = models.OneToOneField(Image)

