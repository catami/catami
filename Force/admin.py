__author__ = 'mat'

from django.contrib import admin
from Force.models import *

class AuvDeploymentAdmin(admin.ModelAdmin):
	list_display = ('startTimeStamp','endTimeStamp','distanceCovered','minDepth','maxDepth','missionAim')

admin.site.register(auvDeployment, AuvDeploymentAdmin)
admin.site.register(campaign)
