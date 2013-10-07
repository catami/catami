import logging
from django.contrib.auth.models import Group, User
from django.db import transaction
from django.dispatch import receiver
import guardian
from guardian.models import UserObjectPermission
from guardian.shortcuts import assign_perm, remove_perm, get_users_with_perms, get_perms
from userena.signals import signup_complete

logger = logging.getLogger(__name__)


# default permissions for project objects
def apply_project_permissions(user, project):
    #assign all permissions view, add, change, delete
    logger.debug("Applying owner permissions to project: " + project.name + " " + project.id.__str__())

    assign_perm('view_project', user, project)
    assign_perm('add_project', user, project)
    assign_perm('change_project', user, project)
    assign_perm('delete_project', user, project)

    #assign view permissions to the Anonymous user
    #logger.debug("Making project public: " + project.name)

    #public_group, created = Group.objects.get_or_create(name='Public')
    #assign_perm('view_project', public_group, project)


def project_is_public(project):
    """
    True is project is public, false if not.
    """
    public_group, created = Group.objects.get_or_create(name='Public')
    return 'view_project' in get_perms(public_group, project)


def set_project_is_public(is_public, project):

    if is_public == "true" or is_public == True:
        make_project_public(project)
    else:
        make_project_private(project)


@transaction.commit_on_success
def set_detailed_project_permissions(current_user, detailed_permissions, project):
    """
    Resets the permissions for the project, based on the given structure
    in get_detailed_project_permissions.

    {
     username: "",
     display_name: "",
     permissions: ""
    }

    """

    logger.debug("Setting detailed permissions for project: " + project.name)

    ## clean out the permissions
    for item in get_detailed_project_permissions(current_user, project):
        user = User.objects.get(username=item['username'])
        remove_perm("view_project", user, project)
        remove_perm("add_project", user, project)
        remove_perm("change_project", user, project)
        remove_perm("delete_project", user, project)

    ## re apply permissions
    for item in detailed_permissions:
        user = User.objects.get(username=item['username'])
        perms = item['permissions']

        # set the permissions
        for perm in perms:
            assign_perm(perm, user, project)


def get_detailed_project_permissions(current_user, project):
    """
    Builds up a list of users and permissions for the project.

    {
     username: "",
     display_name: "",
     permissions: ""
    }

    """

    permission_table = []

    # ignore permissions for those in the public group
    users = get_users_with_perms(project, with_group_users=False)

    for user in users:
        display_name = user.first_name + " " + user.last_name

        # ignore the current user
        if user != current_user:
            permission_table.append({
                "username": user.username,
                "display_name": display_name,
                "permissions": get_perms(user, project)
            })

    return permission_table


def make_project_public(project):
    """
    Makes a given project public.
    """
    logger.debug("Making project public: " + project.name)

    public_group, created = Group.objects.get_or_create(name='Public')
    assign_perm('view_project', public_group, project)


def make_project_private(project):
    """
    Makes a given project private.
    """
    logger.debug("Making project private: " + project.name)

    public_group, created = Group.objects.get_or_create(name='Public')
    remove_perm('view_project', public_group, project)


def give_permission_to_project(user, project, permission):
    """
    Given a user and the defined permission, apply that to the project.
    """
    logger.debug("Giving permission to a project: " + project.name + " - " + user.name + " - " + permission)

    assign_perm(permission, user, project)


def apply_annotation_set_permissions(user, annotation_set):
    #assign all permissions view, add, change, delete
    logger.debug("Applying owner permissions to annotation set: " + annotation_set.name)

    assign_perm('view_annotationset', user, annotation_set)
    assign_perm('add_annotationset', user, annotation_set)
    assign_perm('change_annotationset', user, annotation_set)
    assign_perm('delete_annotationset', user, annotation_set)

    #assign view permissions to the Anonymous user
    #logger.debug("Making annotation set public: " + annotation_set.name)

    #public_group, created = Group.objects.get_or_create(name='Public')
    #assign_perm('view_annotationset', public_group, annotation_set)


def annotation_set_is_public(annotation_set):
    """
    True is project is public, false if not.
    """
    public_group, created = Group.objects.get_or_create(name='Public')
    return 'view_annotationset' in get_perms(public_group, annotation_set)


def set_annotation_set_is_public(is_public, annotation_set):

    if is_public == "true" or is_public == True:
        make_annotation_set_public(annotation_set)
    else:
        make_annotation_set_private(annotation_set)


def make_annotation_set_public(annotation_set):
    """
    Makes a given annotation_set public.
    """
    logger.debug("Making annotation_set public: " + annotation_set.name)

    public_group, created = Group.objects.get_or_create(name='Public')
    assign_perm('view_annotationset', public_group, annotation_set)


def make_annotation_set_private(annotation_set):
    """
    Makes a given project private.
    """
    logger.debug("Making annotation_set private: " + annotation_set.name)

    public_group, created = Group.objects.get_or_create(name='Public')
    remove_perm('view_annotationset', public_group, annotation_set)


@transaction.commit_on_success
def set_detailed_annotation_set_permissions(current_user, detailed_permissions, annotation_set):
    """
    Resets the permissions for the annotation_set, based on the given structure.

    {
     username: "",
     display_name: "",
     permissions: ""
    }

    """

    logger.debug("Setting detailed permissions for project: " + annotation_set.name)

    ## clean out the permissions
    for item in get_detailed_project_permissions(current_user, annotation_set):
        user = User.objects.get(username=item['username'])
        remove_perm("view_annotationset", user, annotation_set)
        remove_perm("add_annotationset", user, annotation_set)
        remove_perm("change_annotationset", user, annotation_set)
        remove_perm("delete_annotationset", user, annotation_set)

    ## apply the permissions
    for item in detailed_permissions:
        user = User.objects.get(username=item['username'])
        perms = item['permissions']

        # set the permissions
        for perm in perms:
            # replace project with annotation set, in case the permissions come in wrong
            perm = perm.replace("project", "annotationset")
            assign_perm(perm, user, annotation_set)


def get_detailed_annotation_set_permissions(current_user, annotation_set):
    """
    Builds up a list of users and permissions for the annotation set.
    """

    permission_table = []

    # ignore permissions for those in the public group
    users = get_users_with_perms(annotation_set, with_group_users=False)

    for user in users:
        display_name = user.first_name + " " + user.last_name
        # ignore the current user
        if user != current_user:
            permission_table.append({
                "username": user.username,
                "display_name": display_name,
                "permissions": get_perms(user, annotation_set)
            })

    return permission_table


def give_permission_to_annotation_set(user, annotation_set, permission):
    """
    Given a user and the defined permission, apply that to the annotation_set.
    """
    logger.debug("Giving permission to a project: " + annotation_set.name + " - " + user.name + " - " + permission)

    assign_perm(permission, user, annotation_set)