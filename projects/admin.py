from django.contrib.gis import admin
from projects.models import *
from guardian.admin import GuardedModelAdmin


class ProjectAdmin(GuardedModelAdmin):
    pass


class AnnotationSetAdmin(GuardedModelAdmin):
    pass

admin.site.register(Project, ProjectAdmin)
admin.site.register(AnnotationSet, AnnotationSetAdmin)

admin.site.register(AnnotationCodes, admin.ModelAdmin)
admin.site.register(QualifierCodes, admin.ModelAdmin)
admin.site.register(PointAnnotation, admin.ModelAdmin)
admin.site.register(WholeImageAnnotation, admin.ModelAdmin)