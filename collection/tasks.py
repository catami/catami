from Force.models import Deployment, Image
from .models import Collection
from datetime import datetime

def collection_from_deployment(user, deployment):
    """Create a collection using all images in a deployment.

    Returns the created collection."""

    # create and prefill the collection as much as possible
    c = Collection()
    c.name = deployment.short_name
    c.owner = user
    c.creation_date = datetime.now()
    c.modified_date = datetime.now()
    c.is_public = True
    c.is_locked = True

    # save the collection so we can associate images with it
    c.save()

    # now add all the images
    for image in deployment.image_set.all():
        c.images.add(image)

    return c


def collection_from_deployment_with_name(user, collection_name, deployment_id_list_string):
    """Create a collection using all images in a deployment.

    Returns the created collection."""
    deployment_list = [int(x) for x in deployment_id_list_string.split(',')]

    # create and prefill the collection as much as possible
    c = Collection()
    c.name = collection_name
    c.owner = user
    c.creation_date = datetime.now()
    c.modified_date = datetime.now()
    c.is_public = False
    c.is_locked = True

    # save the collection so we can associate images with it
    c.save()

    # now add all the images
    for value in deployment_list:
        for image in Image.objects.filter(deployment=Deployment.objects.filter(id=value)):
            c.images.add(image)

    return c
