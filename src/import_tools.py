"""@brief This module is adds functions for ingesting metadata
files directly from a console - for now.  Files
include .json .xml .yaml but must conform to
catami metadata datamodel

Created Dan marrable 5/09/2012
d.marrable@ivec.org

Edits :: Name : Date : description

#--------------------------------------------------#
@todo Include more import file formats.
@todo Include more deployment types
#--------------------------------------------------#

"""

import catamiWebPortal
import os
from django.core import serializers
from Force.models import *
import json
from django.contrib.gis.geos import GEOSGeometry

class ImportMetaData():
    """
    @brief This class is used for importing meta data in to the catami database
    that is stored in a markup file.  Individual models can be populated with
    import_metadata_from_file(file) or batched using
    importMetaDataFromDirectory.

    So far the supported models are:

        campaign.json
        deployment.json
        auvdeployment.json
        images.json
        stereoImages.json
        annotations.json

        """

    def __init__():
        pass

    @staticmethod
    def import_metadata_from_file(d_file):
        """@brief Reads in a metadta d_file that includes campaign information.
        Destinction between deployment types is made on the fine name.
        <type><deployment>.<supported text> auvdeployment.json
        @param d_file The d_file that holds the metata data.  formats include .json
        todo:-> .xml .yaml

        """
        catamiWebPortal.logging.info("Importing metadata from " + d_file)
        filename, fileextension = os.path.splitext(d_file)
        read = True

        if fileextension == '.json':
            try:
                data = json.load(open(d_file))
            except Exception as e:
                catamiWebPortal.logging.error(
                    "Error opening data d_file :: " + str(e))

            if os.path.basename(filename.upper()) == 'CAMPAIGN':
                catamiWebPortal.logging.info("Found valid campaign d_file"
                                             + d_file)
                data_model = Campaign(**data)
            elif os.path.basename(filename.upper()) == 'DEPLOYMENT':
                catamiWebPortal.logging.info(
                    "Found valid deployment d_file" + d_file)
                data_model = Deployment(**data)
            elif os.path.basename(filename.upper()) == 'AUVDEPLOYMENT':
                catamiWebPortal.logging.info(
                    "Found valid deployment d_file" + d_file)
                data_model = AUVDeployment(**data)
            elif os.path.basename(filename.upper()) == 'ANNOTATIONS':
                catamiWebPortal.logging.info(
                    "Found valid annotation d_file" + d_file)
                data_model = Annotations(**data)
            elif os.path.basename(filename.upper()) == 'IMAGE':
                catamiWebPortal.logging.info("Found valid image d_file"
                                             + d_file)
                data_model = Image(**data)
            elif os.path.basename(filename.upper()) == 'STEREOIMAGES':
                catamiWebPortal.logging.info(
                    "Found valid stereo image d_file" + d_file)
                data_model = StereoImage(**data)
            elif os.path.basename(filename.upper()) == 'USER':
                catamiWebPortal.logging.info("Found valid campaign d_file"
                                             + d_file)
                data_model = User(**data)
            else:
                catamiWebPortal.logging.error(
                    "No supported filname found \
                    Data not logged :: filename :: " + d_file)
                read = False
            if read == True:
                try:
                    data_model.full_clean()
                except Exception as e:
                    catamiWebPortal.logging.warning(
                        "Possible validation error :: " + str(e))
                try:
                    data_model.save()
                except Exception as e:
                    catamiWebPortal.logging.error("Couldn't save :: " + str(e))
        else:
            catamiWebPortal.logging.error(
                "No supported fileformat found.  Data not logged  \
                :: d_file extension :: " + fileextension)


    @staticmethod
    def import_metadata_from_directory(directory):
        """@brief This functions is used for parsing all of the supported data
        files in a directory. Each file must be named with the following syntax
        <model-name>.<format> eg: stereoImages.json.  This functions will
        ignore any other files.
        @param directory is the directory holding the data files
        including the / eg /home/data/

        """

        listing = os.listdir(directory)
        catamiWebPortal.logging.info('Found files :: ' + str(listing))
        for infile in listing:
            filename, fileextension = os.path.splitext(infile)
            if  fileextension == '.json':  #@todo: or other supported files
                catamiWebPortal.importTools.importMetaData.import_
                metadata_from_file(directory + infile)
