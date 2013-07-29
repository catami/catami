"""Admin interface for catamidb models."""
from django.contrib.auth.models import User, Group
from guardian.admin import GuardedModelAdmin
from catamiPortal import settings

__author__ = 'mat'

from catamidb.models import *
from django.contrib.gis import admin
import logging

logger = logging.getLogger(__name__)

admin.site.register(Campaign, admin.GeoModelAdmin)
admin.site.register(Deployment, admin.GeoModelAdmin)
admin.site.register(Camera, admin.ModelAdmin)
admin.site.register(ImageUpload, admin.ModelAdmin)
admin.site.register(Image, admin.GeoModelAdmin)
admin.site.register(Measurements, admin.ModelAdmin)

#class CampaignAdmin(GuardedModelAdmin):
#    pass

#admin.site.register(Campaign, CampaignAdmin)