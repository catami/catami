from django.utils import unittest 
from django.test.utils import setup_test_environment
setup_test_environment()
import sys
import os
import time
from dateutil import parser
from django.test import TestCase

# The following is the class in which all functions will be ran by unittest
class AddTest(TestCase):
    ''' Main class for add testing; Can be added to a suite'''
        
    # The function "setUp" will always be ran in order to setup the
    # test environment before all the tests have run.
    def setUp(self):
        '''Verify environment is setup properly''' # Printed if test fails
        import catamiWebPortal
        os.environ['DJANGO_SETTINGS_MODULE'] = 'catamiPortal.settings'
        setup_test_environment()

    # The function "tearDown" will always be ran in order to cleanup the
    # test environment after all the tests have run.
    def tearDown(self):
        '''Verify environment is tore down properly''' # Printed if test fails
        pass

    #==================================================#
    # Add unittests here
    #==================================================#

    def test_ImportMetaDataFromFile(self):

        #==================================================#
        # Campaign data file
        #==================================================#
        description = 'This is a test description'
        associatedResearchers = 'Dan M, Mat W, Luke E, Mark G'
        associatedPublications = 'test.pdf, two.pdf'
        associatedResearchGrant = 'Grant number 3131321'
        dateStart = '2011-10-19 10:23:54+08:00'
        dateEnd = '2011-10-21 10:23:54+08:00'

        # Create a dummy file we know the details of, read in the file, check the database contents
        tmp = open('/tmp/campaign.json','w')
        tmp.write("{\n\"description\":\""+description+"\",\n\"associatedResearchers\":\""+associatedResearchers+"\",\n\"associatedPublications\":\""+associatedPublications+" \",\n\"associatedResearchGrant\":\""+associatedResearchGrant+"\",\n\"dateStart\":\""+dateStart+"\",\n\"dateEnd\":\""+dateEnd+"\"\n}") 

        tmp.flush()
        catamiWebPortal.importTools.importMetaData.importMetaDataFromFile(tmp.name)
        
        #==================================================#
        # Auv deployment data file
        #==================================================#
        startTimeStamp = '2011-10-19 10:23:54+08:00'
        endTimeStamp = '2011-10-19 14:23:54+08:00'
        missionAim = 'Unit Test'
        minDepth = 10.0
        maxDepth = 20.0
        startPosition = 'POINT(-23.15 113.12)'
        distanceCovered = 20.3
        transectShape = 'POLYGON((-23.15 113.12, -23.53 113.34, -23.67 112.9, -23.25 112.82, -23.15 113.12))'
        campaignId = 1
        
        # Create a dummy file we know the details of, read in the file, check the database contents
        tmp = open('/tmp/auvdeployment.json','w')
        tmp.write("{\n\"startTimeStamp\":\""+startTimeStamp+"\",\n\"endTimeStamp\":\""+endTimeStamp+"\",\n\"missionAim\":\""+missionAim+" \",\n\"minDepth\":"+str(minDepth)+",\n\"maxDepth\":"+str(maxDepth)+",\n\"startPosition\":\""+startPosition+"\",\n\"distanceCovered\":"+str(distanceCovered)+",\n\"transectShape\":\""+transectShape+"\",\n\"campaign_id\":"+str(campaignId)+"\n}")

        tmp.flush()
        catamiWebPortal.importTools.importMetaData.importMetaDataFromFile(tmp.name)

        # Grab the list of entries based on the mission aim keyworkd "unit"

        testEntryList = catamiWebPortal.auvDeployment.objects.filter(missionAim__startswith="Unit")
        testEntry = testEntryList[len(testEntryList) -1] # will return the last on in the list. Doesn't support [-1] for some reason

        # Assertions
        self.assertEqual(parser.parse(startTimeStamp),testEntry.startTimeStamp)
        self.assertEqual(parser.parse(endTimeStamp),testEntry.endTimeStamp)
        #self.assertEqual(missionAim,str(testEntry.missionAim))
        #self.assertEqual(minDepth,testEntry.minDepth)
        #self.assertEqual(maxDepth,testEntry.maxDepth)
        #self.assertEqual(startPosition,testEntry.startPosition)
        #self.assertEqual(distanceCovered,testEntry.distanceCovered)
        #self.assertEqual(transectShape,testEntry.transectShape)

        
    def test_ImportMetaDataFromDirectory(self):
        #catamiWebPortal.importTools.importMetaData.importMetaDataFromDirectory('/home/marrabld/catamiPortal/test/data/metadatafiles/')
        pass
                
if __name__=='__main__':
    unittest.main()
