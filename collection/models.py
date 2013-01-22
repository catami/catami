from django.contrib.gis.db import models
from django.contrib.auth.models import User  
from Force.models import Image

# Create your models here.

class Collection(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    owner = models.ForeignKey(User)
    creation_date = models.DateTimeField()
    modified_date = models.DateTimeField()
    is_public = models.BooleanField()
    is_locked = models.BooleanField()
    parent = models.ForeignKey('Collection', null=True, blank=True, default = None)
    images = models.ManyToManyField(Image)
