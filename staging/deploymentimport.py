"""Functions and classes for import of deployments matching the template."""

__author__ = "Lachlan Toohey"

import os
import os.path
import shutil

import csv
import cv2
import datetime
from dateutil.parser import parse as dateparse

import catamidb.models as models

import logging

import staging.settings as staging_settings

logger = logging.getLogger(__name__)

class CSVParser(csv.DictReader):
    """A class to parse CSV row by row (with a heading row)."""

    def __init__(self, file_handle):
        """Create parser for open file.
        
        -- file_handle a file object to read from.
        """

        # auto detect the dialect from an initial sample
        dialect = csv.Sniffer().sniff(file_handle.read(1000))
        file_handle.seek(0)

        csv.DictReader.__init__(self, file_handle, dialect=dialect)

def image_import(campaign_name, deployment_name, image_name, image_path):
    """Create the web versions of the given images and return their path.

    This creates a copy of the image in jpg format and places it in the media
    location. After this it moves the raw image to archival location for long term
    storage (for feature calculation etc.).
    """

    # the location to place the original image
    archive_path = os.path.join(staging_settings.STAGING_ARCHIVE_DIR, campaign_name, deployment_name, image_name)

    if staging_settings.STAGING_MOVE_ORIGINAL_IMAGES and not os.path.exists(os.path.dirname(archive_path)):
        try:
            os.makedirs(os.path.dirname(archive_path))
        except OSError:
            raise Exception("Could not create archive location, full path: {0}".format(archive_path))

    # the place to put the web version of the image
    # (converted from whatever to jpg with high quality etc.)
    image_title, original_type = os.path.splitext(image_name)
    webimage_name = image_title + '.jpg'
    # the place relative to serving root
    webimage_location = os.path.join(campaign_name, deployment_name, webimage_name)
    # absolute filesystem location
    webimage_path = os.path.join(staging_settings.STAGING_WEBIMAGE_DIR, webimage_location)

    if not os.path.exists(os.path.dirname(webimage_path)):
        try:
            os.makedirs(os.path.dirname(webimage_path))
        except OSError:
            raise Exception("Could not create thumbnail location, full path: {0}".format(webimage_path))

    # now actually move/convert the images
    image = cv2.imread(image_path)

    # save the web version
    # if we are wanting lowres web version... scale it down
    if staging_settings.STAGING_LOWRES_WEB_IMAGES:
        # calculate the nominal new size of the image to fit within 96x72px
        # (this size chosen due to 4:3 ratio, and multiples of 8)

        # target size
        target_width = 96
        target_height = 72

        # get original image parameters
        height, width, channels = image.shape

        # calculating scaling factor
        scale_width = target_width / width
        scale_height = target_height / height

        # determine which scaling factor we want to use as we are aiming for
        # a max size take the smaller factor and use it
        if scale_width < scale_height:
            scale = scale_width
        else:
            scale = scale_height

        # scale them
        out_width = width * scale
        out_height = height * scale

        outsize = (out_height, out_width)

        # use INTER_AREA to see better shrunk results
        # use INTER_CUBIC, INTER_LINEAR for better enlargement
        if scale < 1.0:
            image = cv2.resize(image, outsize, interpolation=INTER_AREA)
        else:
            image = cv2.resize(image, outsize, interpolation=INTER_LINEAR)
    
    # save the web version (full size or shrunk)
    cv2.imwrite(webimage_path, image)

    # copy/move to archive
    if staging_settings.STAGING_MOVE_ORIGINAL_IMAGES:
        shutil.move(image_path, archive_path)
    else:
        # don't move it, just pretend to have the original...
        #shutil.copyfile(image_path, archive_path)
        pass

    # return the image details
    return archive_path, webimage_location


def deployment_import(deployment, path):
    """Import a deployment from disk.

    Certain parameters should be prefilled - namely short_name, campaign
    license, descriptive_keywords, and owner. The rest are obtained from the
    information on disk (which the path should point to).

    Information obtained within the function includes start and end time stamps,
    start position, min and max depths and mission_aim.
    """

    description_file_name = os.path.join(path, 'description.txt')
    image_location_file_name = os.path.join(path, 'image-locations.csv')
    whole_image_file_name = os.path.join(path, 'whole-image-classification.csv')
    point_label_file_name = os.path.join(path, 'within-image-classifcation.csv')

    # check the path exists
    if not os.path.isdir(path):
        raise IOError("Deployment Directory does not exist.")

    # the description file
    if not os.path.isfile(description_file_name):
        raise IOError("description.txt is missing in deployment folder.")

    # and the image locations file
    if not os.path.isfile(image_location_file_name):
        raise IOError("image-locations.csv is missing in deployment folder.")

    # load the description
    description_file = open(description_file_name, "r")
    description_text = description_file.read()
    description_file.close()

    # get the deployment into the database
    deployment.mission_aim = description_text

    # fake some of the values - these will be revisited
    deployment.min_depth = 12000
    deployment.max_depth = 0

    deployment.start_position = "POINT(0.0 0.0)"
    deployment.start_time_stamp = datetime.datetime.now()
    deployment.end_time_stamp = datetime.datetime.now()

    deployment.save()

    # load the relevant files of metadata
    image_locations = CSVParser(image_location_file_name)

    # create a lookup on all available sm types
    smtypes = {}
    for smtype in models.ScientificMeasurementType.objects.all():
        smtypes[smtype.normalised_name] = (smtype, min_value, max_value)

    # this will contain the types we are actually using
    # in this deployment
    used_types = {}

    # now get the types in use
    for field in image_locations.fieldnames:
        # check over each field in fieldnames to see if we have a matching
        # measurement type
        norm = slugify(field)

        if norm in smtypes:
            used_types[norm] = smtypes[norm]

    first_image = None
    last_image = None

    # load the images and associated data
    for image_attributes in image_locations:
        # image_attributes is a dictionary with the values in it
        # extract the requirements for image
        # the loop through the used types to create the scientific measurements

        # we need to slugify all the keys first however...
        im_att = {}
        for k,v in image_attributes.iteritems():
            im_att[slugify(k)] = v

        # get the name of the file
        # (prepend path + '/images/' to get on disk location)
        image_name = im_att['imagename']

        # create the image instance
        image = models.Image()
        image.deployment = deployment
        image.date_time = dateparse(im_att['datetime'])
        image.image_position = "POINT({0} {1})".format(im_att['longitude'], im_att['latitude'])
        image.depth = im_att['depth']

        if image.depth > deployment.max_depth:
            deployment.max_depth = image.depth

        if image.depth < deployment.min_depth:
            deployment.min_depth = image.depth

        # do the thumbnailing magic
        campaign_name = deployment.campaign.short_name
        deployment_name = deployment.short_name
        image_path = os.path.join(path, 'image', image_name)

        archive_path, webimage_path = image_import(campaign_name, deployment_name, image_name, image_path)

        image.archive_location = archive_path
        image.webimage_location = webimage_path

        # save the image
        image.save()

        # we need first and last to get start/end points and times
        last_image = image
        if not first_image:
            first_image = image

        # get the scientific measurements now and save them
        for field_name, sm_info in used_types.iteritems():
            value = im_att[field_name]

            # test within range
            if sm_info[1] <= value and value <= sm_info[2]:
                sm = models.ScientificMeasurement()

                sm.measurement_type = sm_info[0]
                sm.image = image
                sm.value = value

                sm.save()

            else:
                # out of range
                # possibly should throw error to indicate likely improper units
                pass

    deployment.start_time_stamp = first_image.date_time
    deployment.end_time_stamp = last_image.date_time

    deployment.start_position = first_image.image_position
    deployment.end_position = last_image.image_position

    # now save the actual min/max depth as well as start/end times and
    # start position and end position
    deployment.save()

    # now do the importing of annotations if they exist

    if os.path.isfile(whole_image_file_name):
        # import habitat classifications
        deployment_habitat_import(deployment, whole_image_file_name)

    if os.path.isfile(point_image_file_name):
        # import point annotations
        deployment_annotation_import(deployment, point_image_file_name)

    # our work is now done!


def deployment_habitat_import(deployment, habitat_file_name):
    """Import habitat information from a csv knowing the source deployment.

    Expected headers are ImageName, and HabitatCode.
    """
    pass

def deployment_annotation_import(deployment, annotation_file_name):
    """Import Point Labels (annotations) from a csv knowing source deployment.

    Expected headers are ImageName, x, y, Label.

    x and y are given as percentages from top left corner.
    """
    pass
