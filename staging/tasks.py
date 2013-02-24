"""Tasks that are used to import data to the database."""

__author__ = "Lachlan Toohey"

from urllib2 import urlopen, HTTPError

import json
import datetime
import tempfile
import os.path

from django.db import transaction, IntegrityError
from django.core import serializers
from django.template.defaultfilters import slugify

from .extras import update_progress
from .auvimport import NetCDFParser, LimitTracker, TrackParser
from .annotations import CPCFileParser
import metadata

from dateutil.tz import tzutc

import catamidb.models

import logging

logger = logging.getLogger(__name__)


def get_known_file(key, url):
    """Download a file and return a file-like handle to it.

    This downloads a file either to memory if small enough or
    to a file if too large.

    Either way it returns a file-like handle to it and deletes
    the file on releasing of the handle.
    """
    # download the file async to get the file and give feedback

    # if it is a list, go through each element until one works
    # and return that one
    if isinstance(url, (list, tuple)):
        for u in url:
            try:
                return get_known_file(key, u)
            except (HTTPError, IOError):
                continue
        else:
            raise Exception("File could not be downloaded.")

        # we likely have an iterable...
    resp = urlopen(url)

    size = int(resp.headers["content-length"])
    downloaded = 0

    # if we get here there must be a valid file we would assume...
    file_handle = tempfile.SpooledTemporaryFile(mode='rw+b')

    while True:
        data = resp.read(8192)
        downloaded += len(data)
        if data == "":
            update_progress(key, 100)
            break
        else:
            file_handle.write(data)
            percent = int(float(100.0 * downloaded) / float(size))
            update_progress(key, percent)

    if downloaded < size:
        raise EOFError("Downloaded file ended unexpectedly.")

    file_handle.seek(0)

    return file_handle


def get_netcdf_file(key, pattern, start_time):
    """Search for then download a file that has a naming pattern based on time.

    The url_pattern contains {date_string} which is replaced with the start_time
    and second increments of it (up to 10 seconds ahead).

    Once the file is found (no 404 or other errors) the file is downloaded and a
    handle returned using get_known_file.

    If the file is not found an error an IO error is thrown.
    """
    search_seconds = 10

    for i in xrange(search_seconds):
        start_time += datetime.timedelta(0, 1)  # add a second
        url = pattern.format(date_string=start_time.strftime('%Y%m%dT%H%M%S'))
        try:
            file_handle = get_known_file(key, url)
        except (HTTPError, IOError):
            pass
        else:
            # no error in finding the file - have the right one so escape
            break
    else:
        raise IOError(0, "Cannot find netcdf file.", pattern)

    return file_handle


def auvfetch(base_url, campaign_date, campaign_name, mission_name):
    """Calculate the track file url and the netcdf url pattern.
    """
    # the YYYMMDD_hhmmss of the mission
    (day, time) = mission_name.lstrip('r').split('_')[0:2]

    mission_datetime = "{0}_{1}".format(day, time)

    # the descriptive text part of the name
    mission_text = mission_name.split('_', 2)[2]

    mission_base = base_url + "/" + campaign_name + "/" + mission_name

    # the track file that contains image positions and names
    trackfile_new_name = "{0}/track_files/{1}_latlong.csv".format(mission_base, mission_text)
    trackfile_old_name = "{0}/track_files/{2}_{1}_latlong.csv".format(mission_base, mission_text, mission_datetime)

    trackfile_name = [trackfile_new_name, trackfile_old_name]

    # the netcdf that give water condition measurements
    netcdf_base = mission_base + '/hydro_netcdf/'

    # still need to replace the string with the date... seconds need to be
    # incremented
    netcdfseabird_name = netcdf_base + 'IMOS_AUV_ST_{date_string}Z_SIRIUS_FV00.nc'

    datetime_object = datetime.datetime.strptime(mission_datetime, "%Y%m%d_%H%M%S")
    datetime_object = datetime_object.replace(tzinfo=tzutc())

    return (trackfile_name, netcdfseabird_name, datetime_object)


@transaction.commit_on_success
def auvprocess(track_file, netcdf_file, base_url, campaign_datestring, campaign_name, mission_name, limit=None):
    """Process the track and netcdf files into the importable json string."""
    # recreate the mission parameters etc.
    (day, time) = mission_name.lstrip('r').split('_')[0:2]
    mission_datetime = "{0}_{1}".format(day, time)

    # the descriptive text part of the name
    mission_text = mission_name.split('_', 2)[2]
    mission_base = base_url + "/" + campaign_name + "/" + mission_name

    # the base directory for the geotiffs
    image_base = mission_base + "/i" + mission_datetime + "_gtif/"

    # these have the precise local names of the files
    netcdf_seabird = NetCDFParser(netcdf_file)
    trackparser = TrackParser(track_file)

    lat_lim = LimitTracker('latitude')
    lon_lim = LimitTracker('longitude')

    # create the deployment instance
    auvdeployment = catamidb.models.AUVDeployment()

    # fill in the basic details
    auvdeployment.short_name = mission_text
    auvdeployment.campaign = catamidb.models.Campaign.objects.get(short_name=campaign_name)
    auvdeployment.mission_aim = "The aim of the mission."
    auvdeployment.license = "CC-BY"
    auvdeployment.descriptive_keywords = "keywords"
    auvdeployment.contact_person = "Catami <catami@ivec.org>"

    # now start going through and creating the data that will be tweaked
    # later (this is all placeholder)
    auvdeployment.min_depth = 12000
    auvdeployment.max_depth = 0
    auvdeployment.start_position = "POINT(0.0 0.0)"
    auvdeployment.end_position = "POINT(0.0 0.0)"
    auvdeployment.start_time_stamp = datetime.datetime.now()
    auvdeployment.end_time_stamp = datetime.datetime.now()

    auvdeployment.transect_shape = "POLYGON((0.0 0.0, 0.0 0.0, 0.0 0.0, 0.0 0.0, 0.0 0.0))"

    auvdeployment.save()

    # get the sm types that we are going to use
    temperature = catamidb.models.ScientificMeasurementType.objects.get(normalised_name='temperature')
    salinity = catamidb.models.ScientificMeasurementType.objects.get(normalised_name='salinity')
    pitch = catamidb.models.ScientificMeasurementType.objects.get(normalised_name='pitch')
    roll = catamidb.models.ScientificMeasurementType.objects.get(normalised_name='roll')
    yaw = catamidb.models.ScientificMeasurementType.objects.get(normalised_name='yaw')
    altitude = catamidb.models.ScientificMeasurementType.objects.get(normalised_name='altitude')

    first_image = None
    last_image = None

    earlier_seabird = netcdf_seabird.next()
    later_seabird = netcdf_seabird.next()

    for row in trackparser:
        if limit and len(poselist) / 2 >= limit:
            break

        image = catamidb.models.Image()
        limage = row['leftimage']
        #rimage = row['rightimage']
        image.deployment = auvdeployment

        seconds, centiseconds = row['second'].split('.')
        image_datetime = datetime.datetime.strptime(os.path.splitext(limage)[0], "PR_%Y%m%d_%H%M%S_%f_LC16")
        image.date_time = image_datetime.replace(tzinfo=tzutc())
        image.image_position = "POINT ({0} {1})".format(row['longitude'], row['latitude'])

        image.depth = row['depth']

        if image.depth > auvdeployment.max_depth:
            auvdeployment.max_depth = image.depth

        if image.depth < auvdeployment.min_depth:
            auvdeployment.min_depth = image.depth

        image_path = os.path.join(image_base, image_name)

        archive_path, webimage_path = image_import(campaign_name, mission_text, image_name, image_path)

        image.archive_location = archive_path
        image.webimage_location = webimage_path

        lat_lim.check(row)
        lon_lim.check(row)

        image.save()

        # get the extra measurements from the seabird data
        while image.date_time > later_seabird['date_time']:
            later_seabird, earlier_seabird = earlier_seabird, netcdf_seabird.next()

        # find which is closer - could use interpolation instead
        if (later_seabird['date_time'] - image.date_time) > (image.date_time - earlier_seabird['date_time']):
            closer_seabird = earlier_seabird
        else:
            closer_seabird = later_seabird

        # add those extra scientific measurements
        temp_m = catamidb.models.ScientificMeasurement()
        temp_m.measurement_type = temperature
        temp_m.value = closer_seabird['temperature']
        temp_m.image = image
        temp_m.save()

        sal_m = catamidb.models.ScientificMeasurement()
        sal_m.measurement_type = salinity
        sal_m.value = closer_seabird['salinity']
        sal_m.image = image
        sal_m.save()

        roll_m = catamidb.models.ScientificMeasurement()
        roll_m.measurement_type = roll
        roll_m.value = row['roll']
        roll_m.image = image
        roll_m.save()

        pitch_m = catamidb.models.ScientificMeasurement()
        pitch_m.measurement_type = pitch
        pitch_m.value = row['pitch']
        pitch_m.image = image
        pitch_m.save()

        yaw_m = catamidb.models.ScientificMeasurement()
        yaw_m.measurement_type = yaw
        yaw_m.value = row['heading']
        yaw_m.image = image
        yaw_m.save()

        alt_m = catamidb.models.ScientificMeasurement()
        alt_m.measurement_type = altitude
        alt_m.value = row['altitude']
        alt_m.image = image
        alt_m.save()

        # we need first and last to get start/end points and times
        last_image = image
        if not first_image:
            first_image = image

    auvdeployment.start_time_stamp = first_image.date_time
    auvdeployment.end_time_stamp = last_image.date_time

    auvdeployment.start_position = first_image.image_position
    auvdeployment.end_position = last_image.image_position

    auvdeployment.transect_shape = "POLYGON(({0} {2}, {0} {3}, {1} {3}, {1} {2}, {0} {2} ))".format(lon_lim.minimum, lon_lim.maximum, lat_lim.minimum, lat_lim.maximum)

    # now save the actual min/max depth as well as start/end times and
    # start position and end position
    auvdeployment.save()




def json_sload(json_string):
    """Load the json string into the database."""
    # now load into the database
    json_real_load(json_string)


def json_fload(file_name):
    """Load the json in file 'file_name' in to the database."""
    # now load into the database
    json_file = open(file_name, 'r')
    json_real_load(json_file)


def json_real_load(data):
    """The function that does the real load of json into the database.

    This data can be either a string or file-like object from which data
    can be read.

    Objects in the file have to be from catamidb.models else the whole contents
    will be rejected. This is a security issue.
    """
    with transaction.commit_manually():
        try:
            for obj in serializers.deserialize('json', data):
                # check if the class is in catamidb
                if obj.object.__class__.__module__ == "catamidb.models":
                    obj.save()
                else:
                    raise ValueError('Object does not come from target Module.', obj.object)
        except:
            transaction.rollback()
            # reraise the same error
            raise
        else:
            transaction.commit()


def metadata_type(metadata_file):
    base, extension = os.path.splitext(metadata_file)

    file_type = extension.lower()
    logger.debug("metadata_type: file extension (normalised) is {0}.".format(file_type))

    if file_type == ".xls":
        logger.debug("metadata_type: file is xls format.")
        return "xls"
    elif file_type == ".xlsx":
        logger.debug("metadata_type: file is xlsx format.")
        return "xlsx"
    else:
        logger.debug("metadata_type: file is unknown format.")
        return ""


def metadata_sheet_names(metadata_file):
    """Return a list of sheet names in the file."""
    logger.debug("metadata_sheet_names: getting sheet names.")

    structure = metadata_outline(metadata_file)

    return structure.keys()


def metadata_sheet_name_deslug(metadata_file, slugged_name):
    """Get the deslugged version of the sheet name."""
    sheet_names = metadata_sheet_names(metadata_file)

    for sheet_name in sheet_names:
        if slugify(sheet_name) == slugged_name:
            return sheet_name

    return None


def metadata_outline(metadata_file, *args, **kwargs):
    """Get an outline of the metadata file structure."""
    logger.debug("metadata_outline: getting file outline: {0}".format(metadata_file))
    data_type = metadata_type(metadata_file)

    if data_type == "xls":
        return metadata.xls_outline(metadata_file, *args, **kwargs)
    elif data_type == "xlsx":
        return metadata.xlsx_outline(metadata_file, *args, **kwargs)
    else:
        logger.warning("metadata_outline: cannot handle extension '{0}'".format(data_type))
        return None


def metadata_transform(metadata_file, *args, **kwargs):
    """Transform the and extract data from the metadata file."""
    logger.debug("metadata_transform: transforming file data.")
    data_type = metadata_type(metadata_file)

    if data_type == "xls":
        return metadata.xls_transform(metadata_file, *args, **kwargs)
    elif data_type == "xlsx":
        return metadata.xlsx_transform(metadata_file, *args, **kwargs)
    else:
        logger.warning("metadata_outline: cannot handle extension '{0}'".format(data_type))
        return None


def metadata_import(model_class, fields_list, field_mappings):
    """Import metadata into the database.

    - model_class is the django model.Model being imported
    - field_mappings are the objects that maps rows of data to fields
    - fields_list is the raw data that is being imported
    """
    # we are going to make some checks/assumptions here
    # first is that we *always* inherit from Deployment.
    # second (that possibly will get removed) is that the levels
    # are only one deep (ie AUV -> Deployment, not A -> B -> Deployment)

    base_model = catamidb.models.Deployment

    if len(model_class._meta.parents) != 1:
        raise Exception("Model to import to has multiple parents!")

    if model_class._meta.parents.keys()[0] != base_model:
        raise Exception("Model must directly inherit from Deployment")

    subclass_fields = model_class._meta.local_fields
    subclass_field_names = [f.name for f in subclass_fields]
    subclass_name = "{0}.{1}".format(model_class._meta.app_label,
                                     model_class._meta.object_name)

    base_fields = base_model._meta.local_fields
    base_field_names = [f.name for f in base_fields]
    base_name = "{0}.{1}".format(base_model._meta.app_label,
                                 base_model._meta.object_name)

    # only commit changes if no errors
    # there are going to be metadata errors...
    with transaction.commit_manually():
        try:
            # this is where all the magic happens
            for row in fields_list:
                # map to db fields
                outfields = {}
                try:
                    for field_name, extractor in field_mappings.iteritems():
                        outfields[field_name] = extractor.get_data(row)
                except Exception as exc:  # ValidationError as exc:
                    # do nothing, just drop row and continue to
                    # next
                    logger.warning("Validation failed on row.")
                    logger.warning("Error: " + str(exc))
                    continue

                # this gets fields and maps to the correct (sub)model
                # still probably doesn't work well with natural key/pk
                # and relationship fields
                # mainly thinking of campaigns... but others may arise

                # split to parent
                base_fields = {field: value for field, value in outfields.iteritems() if field in base_field_names}

                # and child
                subclass_fields = {field: value for field, value in outfields.iteritems() if field in subclass_field_names}

                # create data structures
                # HACK: if creating like this create the model directly
                #base_instance = base_model(**base_fields)
                #base_instance.save()
                # a little to hardcoded for my liking...
                #subclass_fields['deployment_ptr'] = base_instance
                #subclass_instance = model_class(**subclass_fields)
                subclass_instance = model_class(**base_fields)

                # save to the database
                try:
                    subclass_instance.save()
                except IntegrityError as exc:
                    logger.warning("IntegrityError: " + exc)
                    continue
        except:
            logger.debug("Rolling back")
            transaction.rollback()
            raise
        else:
            transaction.commit()
            logger.debug("Commiting")


def annotation_cpc_import(user, deployment, cpc_file_handles):
    """Import CPC annotations into the database.

    This is currently targetted at AUV dives. Not sure if used
    beyond that realm.
    """
    # deployment is used to reduce the search space/chance of collision with images
    # still also need mapping of local ids to catami users

    subset = catamidb.models.Image.objects.filter(deployment=deployment)

    # we are assuming AUV naming conventions for the image...

    # get the date time to look the image reference up from the
    # name of the file... this will assume AUV imagery.
    # Videos probably come from some other idea anyway...

    for cpc_handle in cpc_file_handles:
        annotations = CPCFileParser(cpc_handle)

        image_name = annotations.image_file_name

        # extract the timing info from the file name
        image_datetime = datetime.datetime.strptime(image_name, "PR_%Y%m%d_%H%M%S_%f_LC16")
        image_datetime = image_datetime.replace(tz=utc)
        # now look it up... hopefully the timestamp will match something in the database

        image = subset.get(date_time=image_datetime)

        for a in annotations:
            an = catamidb.models.Annotation()
            an.image_reference = image
            an.method = "50 Point CPC"
            an.code = a['label']
            an.point = "POINT({0} {1})".format(a['x'], a['y'])
            an.comments = a['notes']
            an.user_who_annotated = user

            an.save()

    # annotations are done!
