__author__ = 'Lachlan Toohey'

from annotations.models import *
from django.contrib.gis import admin

admin.site.register(PointAnnotationSet, admin.GeoModelAdmin)
admin.site.register(PointAnnotation, admin.GeoModelAdmin)
admin.site.register(AnnotationCode, admin.GeoModelAdmin)
admin.site.register(QualifierCode, admin.GeoModelAdmin)
