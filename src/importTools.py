import catamiWebPortal
import os
from django.core import serializers
from Force.models import *
import json
from django.contrib.gis.geos import GEOSGeometry

#==================================================#
# Created Dan marrable 5/09/2012
# d.marrable@ivec.org
#
# Edits :: Name : Date : description
#
#--------------------------------------------------#
# This module is adds functions for ingesting metadata
# files directly from a console - for now.  Files
# include .json .xml .yaml but must conform to 
# catami metadata datamodel
#--------------------------------------------------#
# @todo Include more import file formats.
# @todo Include more deployment types
#==================================================#

class importMetaData():
    '''
    @brief This class is used for importing meta data in to the catami database that is stored in a markup file.  Individual models can be populated with importMetaDataFromFile(file) or batched using importMetaDataFromDirectory.

    So far the supported models are:

        campaign.json
        deployment.json
        auvdeployment.json
        images.json
        stereoImages.json
        annotations.json
    '''

    @staticmethod
    def importMetaDataFromFile(file):
        '''
        @brief This function reads in a metadta file that includes campaign information.  Destinction between deployment types is made on the fine name.  <type><deployment>.<supported text> auvdeployment.json
        @param file The file that holds the metata data.  formats include .json todo:-> .xml .yaml
        '''
        catamiWebPortal.logging.info("Importing metadata from " + file)
        fileName, fileExtension = os.path.splitext(file)
        read = True

        if fileExtension == '.json':
            try:
                data = json.load(open(file))
            except Exception as e:
                catamiWebPortal.logging.error("Error opening data file :: " + str(e))

            if os.path.basename(fileName.upper()) == 'CAMPAIGN':
                catamiWebPortal.logging.info("Found valid campaign file" + file)
                dataModel = Campaign(**data)
            elif os.path.basename(fileName.upper()) == 'DEPLOYMENT':
                catamiWebPortal.logging.info("Found valid deployment file" + file)
                dataModel = Deployment(**data)
            elif os.path.basename(fileName.upper()) == 'AUVDEPLOYMENT':
                catamiWebPortal.logging.info("Found valid deployment file" + file)
                dataModel = AUVDeployment(**data)
            elif os.path.basename(fileName.upper()) == 'ANNOTATIONS':
                catamiWebPortal.logging.info("Found valid annotation file" + file)
                dataModel = Annotations(**data)
            elif os.path.basename(fileName.upper()) == 'IMAGE':
                catamiWebPortal.logging.info("Found valid image file" + file)
                dataModel = Image(**data)
            elif os.path.basename(fileName.upper()) == 'STEREOIMAGES':
                catamiWebPortal.logging.info("Found valid stereo image file" + file)
                dataModel = StereoImage(**data)
            elif os.path.basename(fileName.upper()) == 'USER':
                catamiWebPortal.logging.info("Found valid campaign file" + file)
                dataModel = User(**data)                
            else:
                catamiWebPortal.logging.error("No supported filname found.  Data not logged :: filename :: " + file)
                read = False
            if read == True:    
                try:
                    dataModel.full_clean()
                except Exception as e:
                    catamiWebPortal.logging.warning("Possible validation error :: " + str(e))
                try:    
                    dataModel.save()
                except Exception as e:
                    catamiWebPortal.logging.error("Couldn't save :: " + str(e))
        else:
            catamiWebPortal.logging.error("No supported fileformat found.  Data not logged :: file extension :: " + fileExtension)


    @staticmethod
    def importMetaDataFromDirectory(directory):
        '''
        @brief This functions is used for parsing all of the supported data files in a directory. Each file must be named with the following syntax <model-name>.<format> eg: stereoImages.json.  This functions will ignore any other files.
        @param directory is the directory holding the data files including the / eg /home/data/
        '''
        listing = os.listdir(directory)
        catamiWebPortal.logging.info('Found files :: ' + str(listing))
        for infile in listing:
            fileName, fileExtension = os.path.splitext(infile)
            if  fileExtension == '.json':  #@todo: or other supported files
                catamiWebPortal.importTools.importMetaData.importMetaDataFromFile(directory + infile)

#==================================================#
# The following functions are redundant.  Will be
# removed soon
#==================================================#
    

    @staticmethod
    def importUsersFromFile(file):
        '''
        @brief This function reads in a metadta file that includes users information.
        @param file The file that holds the metata data.  formats include .json todo:-> .xml .yaml
        '''
        catamiWebPortal.logging.info("Importing metadata from " + file)
        fileName, fileExtension = os.path.splitext(file)
                
        if fileExtension == '.json':
            data = json.load(open(file))
            dataModel = Users(**data)
            dataModel.full_clean()
            dataModel.save()
        else:
            catamiWebPortal.logging.error("No supported fileformat found.  Data not logged :: file extension :: " + fileExtension)

    @staticmethod
    def importImageFromFile(file):
        '''
        @brief This function reads in a metadta file that includes users information.
        @param file The file that holds the metata data.  formats include .json todo:-> .xml .yaml
        '''
        catamiWebPortal.logging.info("Importing metadata from " + file)
        fileName, fileExtension = os.path.splitext(file)
                
        if fileExtension == '.json':
            data = json.load(open(file))
            dataModel = Image(**data)
            dataModel.full_clean()
            dataModel.save()
        else:
            catamiWebPortal.logging.error("No supported fileformat found.  Data not logged :: file extension :: " + fileExtension)

    @staticmethod
    def importStereoImagesFromFile(file):
        '''
        @brief This function reads in a metadta file that includes users information.
        @param file The file that holds the metata data.  formats include .json todo:-> .xml .yaml
        '''
        catamiWebPortal.logging.info("Importing metadata from " + file)
        fileName, fileExtension = os.path.splitext(file)
                
        if fileExtension == '.json':
            data = json.load(open(file))
            dataModel = StereoImage(**data)
            dataModel.full_clean()
            dataModel.save()
        else:
            catamiWebPortal.logging.error("No supported fileformat found.  Data not logged :: file extension :: " + fileExtension)

            

    @staticmethod
    def importCampaignFromFile(file):
        '''
        @brief This function reads in a metadta file that includes campaign information.
        @param file The file that holds the metata data.  formats include .json todo:-> .xml .yaml
        '''
        catamiWebPortal.logging.info("Importing metadata from " + file)
        fileName, fileExtension = os.path.splitext(file)
        
        
        if fileExtension == '.json':
            data = json.load(open(file))
            dataModel = Campaign(**data)
            dataModel.full_clean()
            dataModel.save()
        else:
            catamiWebPortal.logging.error("No supported fileformat found.  Data not logged :: file extension :: " + fileExtension)

            

    @staticmethod
    def importDeploymentFromFile(file):
        '''
        @brief This function reads in a metadta file that includes campaign information.  Destinction between deployment types is made on the fine name.  <type><deployment>.<supported text> auvdeployment.json
        @param file The file that holds the metata data.  formats include .json todo:-> .xml .yaml
        '''
        catamiWebPortal.logging.info("Importing metadata from " + file)
        fileName, fileExtension = os.path.splitext(file)

        if fileExtension == '.json':
            if os.path.basename(fileName.upper()) == 'AUVDEPLOYMENT':
                catamiWebPortal.logging.info("Found valid deployment file")
                data = json.load(open(file))
                dataModel = AUVDeployment(**data)
                try:
                    dataModel.full_clean()
                except Exception as e:
                    catamiWebPortal.logging.warning("Possible validation error :: " + str(e))
                    
                dataModel.save()
            else:
                catamiWebPortal.logging.error("No supported filname found.  Data not logged :: filename :: " + file)
        else:
            catamiWebPortal.logging.error("No supported fileformat found.  Data not logged :: file extension :: " + fileExtension)

    @staticmethod
    def importAnnotationsFromFile(file):
        '''
        @brief This function reads in a metadta file that includes users information.
        @param file The file that holds the metata data.  formats include .json todo:-> .xml .yaml
        '''
        catamiWebPortal.logging.info("Importing metadata from " + file)
        fileName, fileExtension = os.path.splitext(file)
                
        if fileExtension == '.json':
            data = json.load(open(file))
            dataModel = Annotations(**data)
            dataModel.full_clean()
            dataModel.save()
        else:
            catamiWebPortal.logging.error("No supported fileformat found.  Data not logged :: file extension :: " + fileExtension)
