"""Admin interface for catamidb models."""
from django.contrib.auth.models import User, Group
from catamiPortal import settings

__author__ = 'mat'

from catamidb.models import *
from django.contrib.gis import admin
from guardian.shortcuts import assign
import logging

logger = logging.getLogger(__name__)

admin.site.register(Campaign, admin.GeoModelAdmin)
admin.site.register(Deployment, admin.GeoModelAdmin)
admin.site.register(Pose, admin.GeoModelAdmin)
admin.site.register(Camera, admin.ModelAdmin)
admin.site.register(Image, admin.ModelAdmin)
admin.site.register(GenericImage, admin.ModelAdmin)
admin.site.register(Measurements, admin.ModelAdmin)
admin.site.register(ScientificPoseMeasurement, admin.ModelAdmin)
admin.site.register(ScientificImageMeasurement, admin.ModelAdmin)
admin.site.register(ScientificMeasurementType, admin.ModelAdmin)

admin.site.register(AUVDeployment, admin.GeoModelAdmin)
admin.site.register(BRUVDeployment, admin.GeoModelAdmin)
admin.site.register(DOVDeployment, admin.GeoModelAdmin)
admin.site.register(TVDeployment, admin.GeoModelAdmin)
admin.site.register(TIDeployment, admin.GeoModelAdmin)
