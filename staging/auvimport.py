"""Contains functions to create AUV Structure.

Given a base_url, campaign_name and mission_name create
a structure that can be converted to JSON string or file for
direct import into the Djano database via deserialize.


Base URL format (and example):
fabric_base = "http://df.arcs.org.au/ARCS/projects/IMOS/public/AUV/"

"""

# date handling
import datetime

# needed for thumbnailing
import Image
from cStringIO import StringIO

# for netcdf files
from scipy.io import netcdf

# for trackfiles from the data fabric
import csv

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
    secs_in_day = 24.0 * 3600.0
    imos_seconds_offset = 631152000.0
    imos_days_offset = imos_seconds_offset / secs_in_day

    def __init__(self, file_handle):
        self.file_handle = file_handle

        # the netcdf file
        self.reader = netcdf.netcdf_file(self.file_handle, mode='r')

        if not 'TIME' in self.reader.variables:
            # error, something is missing
            raise KeyError("Key 'TIME' not in netcdf file variables list.")

        if not 'PSAL' in self.reader.variables:
            raise KeyError("Key 'PSAL' not in netcdf file variables list.")

        if not 'TEMP' in self.reader.variables:
            raise KeyError("Key 'TEMP' not in netcdf file variables list.")

        # the index we are up to...
        self.index = 0
        self.items = len(self.reader.variables['TIME'].data)

    def imos_to_unix(self, imos_time):
        """Convert IMOS time to UNIX time.

        IMOS time is days since IMOS epoch which is 1950-01-01.
        """

        return (imos_time - self.imos_days_offset) * self.secs_in_day

    def imos_to_datetime(self, imos_time):
        """Convert IMOS time to python datetime object.

        Utility function that chains the imos to unix and
        unix to datetime functions.
        """
        return datetime.datetime.fromtimestamp(self.imos_to_unix(imos_time))

    def next(self):
        """Get the next row in the NetCDF File.
        """
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
        """Get next row of track file."""
        # create a dict of the column headers and the values
        return dict(zip(self.header, self.reader.next()))

    def __iter__(self):
        return self

