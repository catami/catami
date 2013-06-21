import logging
from django.contrib.auth.models import Group
from django.dispatch import receiver
import guardian
from guardian.shortcuts import assign
from userena.signals import signup_complete

logger = logging.getLogger(__name__)


# default permissions for project objects
def apply_project_permissions(user, project):
    #assign all permissions view, add, change, delete
    logger.debug("Applying owner permissions to project: " + project.name)

    assign('view_project', user, project)
    assign('add_project', user, project)
    assign('change_project', user, project)
    assign('delete_project', user, project)

    #assign view permissions to the Anonymous user
    logger.debug("Making project public: " + project.name)

    public_group, created = Group.objects.get_or_create(name='Public')
    assign('view_project', public_group, project)

def apply_generic_annotation_set_permissions(user, generic_annotation_set):
    #assign all permissions view, add, change, delete
    logger.debug("Applying owner permissions to annotation set: " + generic_annotation_set.name)

    assign('view_genericannotationset', user, generic_annotation_set)
    assign('add_genericannotationset', user, generic_annotation_set)
    assign('change_genericannotationset', user, generic_annotation_set)
    assign('delete_genericannotationset', user, generic_annotation_set)

    #assign view permissions to the Anonymous user
    logger.debug("Making annotation set public: " + generic_annotation_set.name)

    public_group, created = Group.objects.get_or_create(name='Public')
    assign('view_genericannotationset', public_group, generic_annotation_set)