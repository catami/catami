"""Contains functions to create AUV Structure.

Given a base_url, campaign_name and mission_name create
a structure that can be converted to JSON string or file for
direct import into the Djano database via deserialize.

Main functions and prototypes:
def structure_string(structure) => returns string.
def structure_file(structure, output_filename) => no returns.
def create_structure(base_url, campaign_name, mission_name, limit=None) => returns structure.

Base URL format (and example):
fabric_base = "http://df.arcs.org.au/ARCS/projects/IMOS/public/AUV/"

"""
import json
import datetime

# needed for thumbnailing
import Image
from cStringIO import StringIO

from scipy.io import netcdf

# for trackfiles from the data fabric
import urllib
import csv

import os
import os.path
import re

# fabric_base = "http://df.arcs.org.au/ARCS/projects/IMOS/public/AUV/"

def thumbnailer(filename):
    """Returns a string containing base64 encoded JPEG thumbnails.

    This only works for local files, remotely located files are too
    bandwidth intensive to use.
    """

    thumbsize = (64, 64)
    limage = Image.open(filename)
    # make the thumbnail
    limage.thumbnail(thumbsize)
    # create memory buffer
    buff = StringIO()
    # save into the stringIO
    limage.save(buff, "JPEG")
    # go back to start of buffer
    buff.seek(0)

    # encode in base64 and put into string
    output = buff.read().encode("base64").replace("\n", "")

    return output

class LimitTracker:
    """A class to easily track limits of a value/field.

    The field specifies the option key of the object to look up, or if
    field is None (the default) use the value itself. All values are
    converted to floats before comparison.

    minimum and maximum specify starting points.
    """
    def __init__(self, field=None, minimum=float("inf"), maximum=float("-inf")):
        self.maximum = maximum
        self.minimum = minimum
        self.field = field

    def check(self, newobject):
        """Check a new value against the existing limits.
        """
        # check if field exists
        if self.field and self.field in newobject:
            value = float(newobject[self.field])
            # then see if it is a new maximum
            self.maximum = max(self.maximum, value)
            self.minimum = min(self.minimum, value)
        elif not self.field:
            value = float(newobject)
            self.maximum = max(self.maximum, value)
            self.minimum = min(self.minimum, value)


class NetCDFParser:
    """A class to wrap retrieving values from AUV NetCDF files.

    The class requires a string with {date_string} in the place for the
    date string as it is not absolutely defined given the starting point.
    It searches for times within 10 seconds of the initial guess.

    It implements the iterator interface returning dictionaries with salinity,
    temperature and time of measurement.
    """
    def __init__(self, file_handle):
        self.file_handle = file_handle

        # the netcdf file
        self.reader = netcdf.netcdf_file(self.file_handle, mode='r')

        if not 'TIME' in self.reader.variables:
            # error, something is missing
            raise KeyError("Key 'TIME' not in netcdf file variables list.")

        if not 'PSAL' in self.reader.variables or not 'TEMP' in self.reader.variables:
            raise KeyError("Key 'PSAL' or 'TEMP' not in netcdf file variables list.")
            

        # the index we are up to...
        self.index = 0
        self.items = len(self.reader.variables['TIME'].data)

    def imos_to_unix(self, imos_time):
        self.secs_in_day = 24.0 * 3600.0;
        self.imos_seconds_offset = 631152000.0;
        self.imos_days_offset = self.imos_seconds_offset / self.secs_in_day

        return (imos_time - self.imos_days_offset) * self.secs_in_day

    def unix_to_datetime(self, unix_time):
        return datetime.datetime.fromtimestamp(unix_time)

    def imos_to_datetime(self, imos_time):
         return self.unix_to_datetime(self.imos_to_unix(imos_time))

    def next(self):
        i = self.index
        self.index += 1
    
        time = self.reader.variables['TIME'].data[i]
        sal = self.reader.variables['PSAL'].data[i]
        temp = self.reader.variables['TEMP'].data[i]

        return {'date_time': self.imos_to_datetime(time), 
                    'salinity':sal, 
                    'temperature':temp}


class TrackParser:
    """A class to parse the csv stereo pose tracks for AUV deployments.

    It can be given a URI that it will retrieve the file from. It returns
    a dictionary using the header row to determine the keys and the values
    for each row.
    """
    def __init__(self, file_handle):
        """Open a parser for AUV track files.

        -- file_location can be url or local file location.
        """
        self.file_handle = file_handle

        self.reader = csv.reader(self.file_handle)

        # skip until year is the first entry
        for row in self.reader:
            if len(row) >= 1 and row[0] == 'year':
                self.header = row
                break

        # the next line is the first data line
        # so construction is finished

    def next(self):
        # create a dict of the column headers and the values
        return dict(zip(self.header, self.reader.next()))

    def __iter__(self):
        return self

def structure_string(structure):
    """Output the structure to a string and return.
    """
    return json.dumps(structure)

def structure_file(structure, output_filename):
    """Output the structure to a named file.
    """
    outfile = open(output_filename, 'w')
    json.dump(structure, outfile)


def create_structure(base_url, campaign_name, mission_name, limit=None):
    """Wrap retrieval and creation of a structure to serialise for database ingestion.

    It takes in the campaign name and mission, as well as an optional limit on the number
    of poses to record.
    """

    # base location for AUV data in the fabric
    fabric_base = "http://df.arcs.org.au/ARCS/projects/IMOS/public/AUV/"

    matches = re.match("([a-zA-Z]+)(\d\d\d\d)(\d\d)(Eng)?", campaign_name)
    if matches:
        year = int(matches.group(2))
        month = int(matches.group(3))
        campaign_datestring = str(datetime.date(year, month, 1))
    else:
        raise ValueError("Can't get campaign date.")

    # could take the bit before the date... but oh well
    campaign_text = campaign_name

    # the YYYMMDD_hhmmss of the mission
    mission_datetime = "{0}_{1}".format(*mission_name.lstrip('r').split('_')[0:2])

    # the descriptive text part of the name
    mission_text = mission_name.split('_', 2)[2]

    mission_base = fabric_base + "/" + campaign_name + "/" + mission_name

    # the base directory for the geotiffs
    image_base =  mission_base + "/i" + mission_datetime + "_gtif/"

    # the track file that contains image positions and names
    trackfile_name = mission_base + "/track_files/" + mission_text + "_latlong.csv"

    trackparser = TrackParser(trackfile_name)

    # the netcdf that give water condition measurements
    netcdf_base = mission_base + '/hydro_netcdf/'

    # still need to replace the string with the date... seconds need to be
    # incremented
    netcdfseabird_name = netcdf_base + 'IMOS_AUV_ST_{date_string}Z_SIRIUS_FV00.nc'

    datetime_object = datetime.datetime.strptime(mission_datetime, "%Y%m%d_%H%M%S")

    start_datestring = str(datetime_object)

    deployment_nk = [start_datestring , mission_text]


    netcdf_seabird = NetCDFParser(netcdfseabird_name, datetime_object)

    # not currently used
    #netcdf_ecopuck = netcdf_base + 'IMOS_AUV_ST_{date_string}Z_SIRIUS_FV00.nc'

    # the running max and min survey depths
    depth_lim = LimitTracker('depth')

    # latitude and longitude limits
    lat_lim = LimitTracker('latitude')
    lon_lim = LimitTracker('longitude')

    #ex = extractmeasurement(auvraw_folder, "SEABIRD")

    #lastseabird = seabird_parser(ex.next())
    #nextseabird = seabird_parser(ex.next())

    poselist = []

    earlier_seabird = netcdf_seabird.next()
    later_seabird = netcdf_seabird.next()

    for row in trackparser:
        if limit and len(poselist) / 2 >= limit:
            break

        limage = row['leftimage']
        rimage = row['rightimage']

        pose = dict()
        pose['deployment'] = deployment_nk # the foreign key, whatever the natural key is
        seconds, centiseconds = row['second'].split('.')
        pose['date_time'] = datetime.datetime(int(row['year']), int(row['month']), 
                                    int(row['day']), int(row['hour']), 
                                    int(row['minute']), int(seconds),
                                    int(centiseconds) * 10000) # convert to microseconds

        pose['image_position'] = "POINT ({0} {1})".format(row['latitude'], row['longitude'])

        pose['left_image_reference'] = image_base + "{0}.tif".format(os.path.splitext(limage)[0])

        pose['pitch'] = row['pitch']
        pose['roll'] = row['roll']
        pose['yaw'] = row['heading']

        pose['altitude'] = row['altitude']
        pose['depth'] = row['depth']

        # get the two measurements either side of the stereo pose
        while pose['date_time'] > later_seabird['date_time']:
            earlier_seabird, later_seabird = later_seabird, netcdf_seabird.next()

        # find which is closer - could use interpolation instead
        if (later_seabird['date_time'] - pose['date_time']) > (pose['date_time'] - earlier_seabird['date_time']):
            closer_seabird = earlier_seabird
        else:
            closer_seabird = later_seabird

        # add in salinity and temperature
        pose['temperature'] = closer_seabird['temperature']
        pose['salinity'] = closer_seabird['salinity']

        pose['date_time'] = str(pose['date_time'])

        depth_lim.check(pose)
        # lat and long are embedded in pose, but direct in row
        lat_lim.check(row)
        lon_lim.check(row)

    
        # get the actual image (probably png/tiff)
        #pose['left_thumbnail_reference'] = thumbnailer(os.path.join(img_dir_name, pose['left_image_reference']))
        #pose['right_thumbnail_reference'] = thumbnailer(os.path.join(img_dir_name, pose['right_image_reference']))

        # quick hax to use instead of embedding the thumbnail
        pose['left_thumbnail_reference'] = pose['left_image_reference']


        # add the stereo here
        stereopose = {}
        stereopose['image_ptr'] = [deployment_nk, pose['date_time']] #list(deployment_nk).append(pose['date_time'])
        stereopose['right_image_reference'] = image_base + "{0}.tif".format(os.path.splitext(rimage)[0])
        stereopose['right_thumbnail_reference'] = stereopose['right_image_reference']


        print "Added pose at ", pose['date_time']

        poselist.append({'pk': None, 'model': 'Force.Image', 'fields': pose})
        poselist.append({'pk': None, 'model': 'Force.StereoImage', 'fields': stereopose})

    deployment = {}
    # take the position of the first image
    deployment['campaign'] = [ campaign_datestring, campaign_text] # the foreign key
    deployment['short_name'] = mission_text
    deployment['start_position'] = poselist[0]['fields']['image_position']
    # the start from the mission time - potentially should shift to first image?
    deployment['start_time_stamp'] = start_datestring 
    # from the last image taken (last image, not stereoImages)
    deployment['end_time_stamp'] = poselist[-2]['fields']['date_time']
    deployment['mission_aim'] = "The aim of the mission."
    deployment['min_depth'] = depth_lim.minimum
    deployment['max_depth'] = depth_lim.maximum


    auvdeployment = {}
    auvdeployment['deployment_ptr'] = deployment_nk # the foreign key, whatever the natural key is
    auvdeployment['transect_shape'] = "POLYGON(({0} {2}, {0} {3}, {1} {3}, {1} {2}, {0} {2} ))".format(lat_lim.minimum, lat_lim.maximum, lon_lim.minimum, lon_lim.maximum)
    auvdeployment['distance_covered'] = 100.0 # just make it up... will work out later

    deploy = { 'pk': None, 'model': 'Force.Deployment', 'fields': deployment }
    auvdeploy = { 'pk': None, 'model': 'Force.AUVDeployment', 'fields': auvdeployment }

    #campaign = {}
    #campaign['short_name'] = campaign_text
    #campaign['date_start'] = campaign_datestring
    #campaign['date_end'] = campaign_datestring
    #campaign['associated_researchers'] = "ACFR + TAFI"
    #campaign['associated_publications'] = "Heaps."
    #campaign['associated_research_grant'] = "Grant Name"
    #campaign['description'] = "IMOS Repeat Survey to Tasmania"

    #camp = { 'pk': None, 'model': 'Force.Campaign', 'fields': campaign }

    structure = [deploy, auvdeploy]
    structure.extend(poselist)

    return structure

if __name__ == "__main__":
    structure = create_structure('Tasmania201106', 'r20110614_055332_flindersCMRnorth_09_canyongrids', limit=5)
    campaign_file = open('campaign.json', 'w')
    deployment_file = open('deployment.json', 'w')
    auvdeployment_file = open('auvdeployment.json', 'w')
    images_file = open('images.json', 'w')
    all_file = open('outfile.json', 'w')


    json.dump(structure[0:1], campaign_file)
    json.dump(structure[1:2], deployment_file)
    json.dump(structure[2:3], auvdeployment_file)
    json.dump(structure[3:], images_file)
    json.dump(structure, all_file)
