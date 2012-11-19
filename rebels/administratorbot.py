"""A bot to check database integrity and manage backups
"""

__author__ = "Dan Marrable"

import logging
import tarfile
import hashlib
import os
from  shutil import copyfile
from django.db import connections
from django.db.utils import ConnectionDoesNotExist
from django.core import management
#from django.core import mail
from datetime import datetime
from StringIO import StringIO

logger = logging.getLogger(__name__)


class Robot():
    """Base class for the adminitrator bot"""

    def __init__(self):
        """class constructor for setting up the bot parameters"""
        # how often to poll the server for connection in sec
        self.dt_connection = 10

    def check_database_connection(self, dbname='Force'):
        """Check to see if database connection is open. Return True or False
    
        The return is true if connection is open false if connection failed
        """

        try:
            cursor = connections[dbname].cursor()

            if cursor:
                logger.debug('Connection open to database :: ' + dbname)
                return True

        except ConnectionDoesNotExist:
            logger.error('Cannot connect to database :: ' +
                         dbname + ' :: Query failed')
            return False

    def make_local_backup(self, dbname='Force', **kwargs):
        """Do a naive backup to local machine

        Keywords include:

        directory [./rebels/backup/] :: The directory to backup to.
        do_zip [True] :: compress or not.
        compression_type [gz] :: gz or bz2
        file_format [json] :: raw data output fomat. :: json, xml, yaml
        """

        # Extract any kwargs that are parsed

        # default to current dir '.'
        directory = kwargs.get('directory', './rebels/backup/')
        compression_type = kwargs.get('compression_type', 'gz')
        do_zip = kwargs.get('do_zip', True)
        file_format = kwargs.get('file_format', 'json')

        # Setup the files to write data to.
        fname = str(datetime.now()) + '-' + dbname + '.bak'

        # Catch the data from dumpdata on the stdio
        content = StringIO()
        management.call_command('dumpdata', stdout=content, interactive=False,
                                format=file_format)
        content.seek(0)
        data = content.read()

        # Zip up the data
        if do_zip:
            tmp_directory = '/tmp/'
            # let the os delete later.
            tmpfile = open(tmp_directory + fname, 'w')
            tar = tarfile.open(directory +
                               fname +
                               '.tar.' +
                               compression_type,
                               'w:' +
                               compression_type)
            tmpfile.write(data)
            tmpfile.close()
            tar.add(tmp_directory + fname, arcname=fname)
            tar.close()

            # Make a copy of the backup, extract it and check sum
            copyfile(directory + fname + '.tar.' + compression_type,
                     directory + 'copy_' + fname + '.tar.' + compression_type)

            #compare the two copied files
            chk_file = self.check_sum_file(directory + fname + '.tar.'
                                           + compression_type)
            logger.debug(directory + fname +
                         '.tar.' +
                         compression_type +
                         ' Checksum :: ' +
                         str(chk_file))

            chk_copy = self.check_sum_file(directory + 'copy_' +
                                           fname + '.tar.'
                                           + compression_type)

            logger.debug(directory + 'copy_'
                         + fname + '.tar.' +
                         compression_type +
                         ' Checksum :: ' +
                         str(chk_file))

            if chk_file == chk_copy:
                logger.debug('backup archive copied correctly')
            else:
                logger.error('backup archive check sum fail')
                return False

            # Check to see if file is in the archive
            tar = tarfile.open(directory +
                               'copy_' +
                               fname +
                               '.tar.' +
                               compression_type,
                               'r:' + compression_type)

            for tarinfo in tar:
                logger.debug(tarinfo.name + " is" +
                             str(tarinfo.size) +
                             " bytes in size")

            if tarinfo.name == fname:
                logger.debug('File name in archive matches backup file')
            else:
                logger.error('File name in archive does not match backup file')
                return False

            # Extract the data file from the copied archive and
            #checksum against the original
            tar.extractall(path=directory)
            chk_file = self.check_sum_file(directory + fname)
            logger.debug(directory + fname + ' Checksum :: ' + str(chk_file))
            chk_tmp_file = self.check_sum_file(tmp_directory + fname)
            logger.debug(tmp_directory +
                         fname +
                         ' Checksum :: '
                         + str(chk_tmp_file))

            if chk_file == chk_tmp_file:
                logger.debug('backup file copied correctly')
            else:
                logger.error('backup file check sum fail')
                return False

            tar.close()

            logger.debug('removing duplicate files')
            os.remove(directory + 'copy_' + fname + '.tar.' + compression_type)
            os.remove(directory + fname)

        else:
            f = open(directory + fname, 'w')
            fcopy = open('/tmp/' + fname, 'w')
            f.write(data)
            fcopy.write(data)
            f.close()
            fcopy.close()

            if (self.check_sum_file('/tmp/' + fname, 'w') ==
                self.check_sum_file(directory + fname, 'w')):

                logger.debug('File and copy checksums agree')
            else:
                logger.error('File and copy checksums dont agree')
        # Check to see if the file is there.

        return True

    def check_sum_file(self, fname):
        """Generate md5sum of a file

        We do it this way incase the file exceeds available memory
        """

        sha = hashlib.sha1()
        with open(fname, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha.update(chunk)
        return sha.hexdigest()

    def make_remote_backup(self, ipaddress, dbname='Force', **kwargs):
        """Make a back up of an offsite database"""
