__author__ = 'mat'

from django.contrib import admin
from collection.models import *
from django.contrib.gis import admin


admin.site.register(Collection, admin.GeoModelAdmin)

