__author__ = 'Mark Gray'

from projects.models import *
from django.contrib import admin

admin.site.register(AnnotationCodes, admin.ModelAdmin)
admin.site.register(QualifierCodes, admin.ModelAdmin)
admin.site.register(Project, admin.ModelAdmin)
admin.site.register(GenericAnnotationSet, admin.ModelAdmin)
admin.site.register(GenericPointAnnotation, admin.ModelAdmin)
admin.site.register(GenericWholeImageAnnotation, admin.ModelAdmin)
