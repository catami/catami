from django.contrib.gis import admin
from projects.models import *
from guardian.admin import GuardedModelAdmin


class ProjectAdmin(GuardedModelAdmin):
    pass

admin.site.register(Project, ProjectAdmin)

admin.site.register(AnnotationCodes, admin.ModelAdmin)
admin.site.register(QualifierCodes, admin.ModelAdmin)
admin.site.register(GenericAnnotationSet, admin.ModelAdmin)
admin.site.register(GenericPointAnnotation, admin.ModelAdmin)
admin.site.register(GenericWholeImageAnnotation, admin.ModelAdmin)