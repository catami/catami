from django.utils import unittest 
from django.test.utils import setup_test_environment
setup_test_environment()
import sys
import os
import time
import string
import mox
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
        self.mocker = mox.Mox()

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
        # User data file
        #__________________________________________________
        # Note This is just for testing, need to change
        # to auth_user in the django table 
        #==================================================#
        id = 1
        name = 'Dan M'
        title = 'Baron'
        organisation = 'iVEC'
        email = 'daniel.marrable@ivec.org'

        # Create a dummy file we know the details of, read in the file, check the database contents
        tmp = open('/tmp/user.json','w')
        tmp.write("{\n\"id\":"+str(id)+",\n\"name\":\""+name+"\",\n \"title\":\""+title+"\",\n\"organisation\":\""+organisation+" \",\n\"email\":\""+email+"\"\n}") 

        tmp.flush()
        catamiWebPortal.importTools.importMetaData.importMetaDataFromFile(tmp.name)

        # Grab the list of entries based on the mission aim keyworkd "unit"
        testEntryList = catamiWebPortal.user.objects.filter(name__startswith="Dan")
        testEntry = testEntryList[len(testEntryList) -1] # will return the last on in the list. Doesn't support [-1] for some reason

        #==================================================#
        # User Data Assertions
        #==================================================#
        self.assertEqual(id,testEntry.id)
        self.assertEqual(string.strip(name),string.strip(testEntry.name))
        self.assertEqual(string.strip(title),string.strip(testEntry.title))
        self.assertEqual(string.strip(email),string.strip(testEntry.email))

        #==================================================#
        # Campaign data file
        #==================================================#
        description = 'Unit Test'
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

        # Grab the list of entries based on the mission aim keyworkd "unit"
        testEntryList = catamiWebPortal.campaign.objects.filter(description__startswith="Unit")
        testEntry = testEntryList[len(testEntryList) -1] # will return the last on in the list. Doesn't support [-1] for some reason

        #==================================================#
        # Campaign Assertions
        #==================================================#
        self.assertEqual(string.strip(description), string.strip(testEntry.description))
        #self.assertEqual(associatedResearchers, testEntry.associatedResearchers)
        #self.assertEqual(associatedPublications, testEntry.associatedPublications)
        #self.assertEqual(string.strip(associatedResearchGrant), string.strip(testEntry.associatedResearchGrant))
        self.assertEqual(parser.parse(dateStart),testEntry.dateStart)
        self.assertEqual(parser.parse(dateEnd),testEntry.dateEnd)
        
        #==================================================#
        # Auv deployment data file
        #==================================================#
        startTimeStamp = '2011-10-19 10:23:54+08:00'
        endTimeStamp = '2011-10-19 14:23:54+08:00'
        missionAim = 'Unit Test'
        minDepth = 10.0
        maxDepth = 20.0
        startPosition_x = -23.15
        startPosition_y = 113.12
        startPosition = 'POINT('+str(startPosition_x)+' '+str(startPosition_y)+')'
        distanceCovered = 20.3
        transectShape_x = [-23.15,-23.53,-23.67,-23.25,-23.15]
        transectShape_y = [113.12,113.34,112.9,112.82,113.12]
        transectShape = 'POLYGON(('+str(transectShape_x[0])+' '+str(transectShape_y[0])+', '+str(transectShape_x[1])+' '+str(transectShape_y[1])+', '+str(transectShape_x[2])+' '+str(transectShape_y[2])+', '+str(transectShape_x[3])+' '+str(transectShape_y[3])+', '+str(transectShape_x[4])+' '+str(transectShape_y[4])+'))'
        campaignId = 1
        
        # Create a dummy file we know the details of, read in the file, check the database contents
        tmp = open('/tmp/auvdeployment.json','w')
        tmp.write("{\n\"startTimeStamp\":\""+startTimeStamp+"\",\n\"endTimeStamp\":\""+endTimeStamp+"\",\n\"missionAim\":\""+missionAim+" \",\n\"minDepth\":"+str(minDepth)+",\n\"maxDepth\":"+str(maxDepth)+",\n\"startPosition\":\""+startPosition+"\",\n\"distanceCovered\":"+str(distanceCovered)+",\n\"transectShape\":\""+transectShape+"\",\n\"campaign_id\":"+str(campaignId)+"\n}")

        tmp.flush()
        catamiWebPortal.importTools.importMetaData.importMetaDataFromFile(tmp.name)

        # Grab the list of entries based on the mission aim keyworkd "unit"
        testEntryList = catamiWebPortal.auvDeployment.objects.filter(missionAim__startswith="Unit")
        testEntry = testEntryList[len(testEntryList) -1] # will return the last on in the list. Doesn't support [-1] for some reason

        #==================================================#
        # AUV deployment Assertions
        #==================================================#
        self.assertEqual(parser.parse(startTimeStamp),testEntry.startTimeStamp)
        self.assertEqual(parser.parse(endTimeStamp),testEntry.endTimeStamp)
        self.assertEqual(string.strip(missionAim),string.strip(str(testEntry.missionAim)))
        self.assertEqual(minDepth,testEntry.minDepth)
        self.assertEqual(maxDepth,testEntry.maxDepth)
        self.assertEqual(startPosition_x,testEntry.startPosition.x)
        self.assertEqual(startPosition_y, testEntry.startPosition.y)

        for i in range(0,len(transectShape_x)):
            self.assertEqual(transectShape_x[i],testEntry.transectShape.coords[0][i][0])
            
        for j in range(0,len(transectShape_y)):
            self.assertEqual(transectShape_y[j],testEntry.transectShape.coords[0][j][1])
            
        self.assertEqual(distanceCovered,testEntry.distanceCovered)

        #==================================================#
        # images data file
        #==================================================#
        leftThumbnailReference = "https://df.arcs.org.au/ARCS/projects/IMOS/public/AUV//Tasmania201106/r20110614_055332_flindersCMRnorth_09_canyongrids/i20110614_055332_gtif/('PR_20110614_061205_092_RM16.tif"
        leftImageReference = "https://df.arcs.org.au/ARCS/projects/IMOS/public/AUV//Tasmania201106/r20110614_055332_flindersCMRnorth_09_canyongrids/i20110614_055332_gtif/('PR_20110614_061205_092_LC16.tif"
        temperature = 15.211
        yaw = 2.9119767014847424
        imagePosition_x = -40.5446848363899335
        imagePosition_y = 148.8015551780569012
        imagePosition = "\"POINT ("+str(imagePosition_x)+" "+str(imagePosition_y)+")\""
        dateTime = "2011-06-14 16:12:05.092029+08:00"
        depth = 120.13268785071226
        pitch = -0.0250635711698782
        salinity = 35.471
        altitude = 2.0
        roll = 0.3
        deployment_id = 1

        # Create a dummy file we know the details of, read in the file, check the database contents
        tmp = open('/tmp/image.json','w')
        tmp.write("{\n\"leftThumbnailReference\":\""+leftThumbnailReference+"\",\n\"leftImageReference\":\""+leftImageReference+"\",\n\"temperature\":"+str(temperature)+" ,\n\"yaw\":"+str(yaw)+",\n\"imagePosition\":"+imagePosition+",\n\"dateTime\":\""+dateTime+"\",\n\"depth\":"+str(depth)+",\n\"pitch\":"+str(pitch)+",\n\"salinity\":"+str(salinity)+",\n\"altitude\":"+str(altitude)+",\n\"roll\":"+str(roll)+",\n\"deployment_id\":"+str(deployment_id)+"\n}")

        tmp.flush()
        catamiWebPortal.importTools.importMetaData.importMetaDataFromFile(tmp.name)

        # Grab the list of entries based on the mission aim keyworkd "unit"
        testEntryList = catamiWebPortal.image.objects.filter(leftThumbnailReference__startswith="https://df.arcs.org.au/ARCS/projects/IMOS/public/AUV//Tasmania201106/r20110614_055332_flindersCMRnorth_09_canyongrids/i20110614_055332_gtif/('PR_20110614_061205_092_RM16.tif")
        testEntry = testEntryList[len(testEntryList) -1] # will return the last on in the list. Doesn't support [-1] for some reason

        #==================================================#
        # Image Assertions
        #==================================================#
        self.assertEqual(parser.parse(dateTime),testEntry.dateTime)
        self.assertEqual(string.strip(leftThumbnailReference),string.strip(str(testEntry.leftThumbnailReference)))
        self.assertEqual(string.strip(leftImageReference),string.strip(str(testEntry.leftImageReference)))
        self.assertEqual(temperature,testEntry.temperature)
        self.assertAlmostEqual(yaw,testEntry.yaw)
        self.assertAlmostEqual(imagePosition_x,testEntry.imagePosition.x)
        self.assertAlmostEqual(imagePosition_y, testEntry.imagePosition.y)
        self.assertAlmostEqual(depth, testEntry.depth)
        self.assertAlmostEqual(pitch,testEntry.pitch)
        self.assertAlmostEqual(salinity, testEntry.salinity)
        self.assertAlmostEqual(altitude, testEntry.altitude)
        self.assertAlmostEqual(roll,testEntry.roll)
        self.assertEqual(deployment_id,testEntry.deployment_id)
        
        #==================================================#
        # stereoImages data file
        #==================================================#
        rightThumbnailReference = "https://df.arcs.org.au/ARCS/projects/IMOS/public/AUV//Tasmania201106/r20110614_055332_flindersCMRnorth_09_canyongrids/i20110614_055332_gtif/('PR_20110614_061205_092_RM16.tif"
        rightImageReference = "https://df.arcs.org.au/ARCS/projects/IMOS/public/AUV//Tasmania201106/r20110614_055332_flindersCMRnorth_09_canyongrids/i20110614_055332_gtif/('PR_20110614_061205_092_LC16.tif"


        # Create a dummy file we know the details of, read in the file, check the database contents
        tmp = open('/tmp/stereoImages.json','w')
        tmp.write("{\n\"leftThumbnailReference\":\""+leftThumbnailReference+"\",\n\"leftImageReference\":\""+leftImageReference+"\",\n\"rightThumbnailReference\":\""+rightThumbnailReference+"\",\n\"rightImageReference\":\""+rightImageReference+"\",\n\"temperature\":"+str(temperature)+" ,\n\"yaw\":"+str(yaw)+",\n\"imagePosition\":"+imagePosition+",\n\"dateTime\":\""+dateTime+"\",\n\"depth\":"+str(depth)+",\n\"pitch\":"+str(pitch)+",\n\"salinity\":"+str(salinity)+",\n\"altitude\":"+str(altitude)+",\n\"roll\":"+str(roll)+",\n\"deployment_id\":"+str(deployment_id)+"\n}")

        tmp.flush()
        catamiWebPortal.importTools.importMetaData.importMetaDataFromFile(tmp.name)

        testEntryList = catamiWebPortal.stereoImages.objects.filter(leftThumbnailReference__startswith="https://df.arcs.org.au/ARCS/projects/IMOS/public/AUV//Tasmania201106/r20110614_055332_flindersCMRnorth_09_canyongrids/i20110614_055332_gtif/('PR_20110614_061205_092_RM16.tif")
        testEntry = testEntryList[len(testEntryList) -1] # will return the last on in the list. Doesn't support [-1] for some reason

        #==================================================#
        # Stereo Images Assertions
        #==================================================#
        self.assertEqual(parser.parse(dateTime),testEntry.dateTime)
        self.assertEqual(string.strip(leftThumbnailReference),string.strip(str(testEntry.leftThumbnailReference)))
        self.assertEqual(string.strip(leftImageReference),string.strip(str(testEntry.leftImageReference)))
        self.assertEqual(string.strip(rightThumbnailReference),string.strip(str(testEntry.rightThumbnailReference)))
        self.assertEqual(string.strip(rightImageReference),string.strip(str(testEntry.rightImageReference)))
        self.assertEqual(temperature,testEntry.temperature)
        self.assertAlmostEqual(yaw,testEntry.yaw)
        self.assertAlmostEqual(imagePosition_x,testEntry.imagePosition.x)
        self.assertAlmostEqual(imagePosition_y, testEntry.imagePosition.y)
        self.assertAlmostEqual(depth, testEntry.depth)
        self.assertAlmostEqual(pitch,testEntry.pitch)
        self.assertAlmostEqual(salinity, testEntry.salinity)
        self.assertAlmostEqual(altitude, testEntry.altitude)
        self.assertAlmostEqual(roll,testEntry.roll)
        self.assertEqual(deployment_id,testEntry.deployment_id)

        #==================================================#
        # annotoations data file
        #==================================================#
        method = '5 Point'
        code = '37 344000'
        point_x = 12
        point_y = 25
        point = 'POINT('+str(point_x)+' '+str(point_y)+')'
        comments = 'Unit Test'
        imageReference_id = 1
        userWhoAnnotated_id = 1

        # Create a dummy file we know the details of, read in the file, check the database contents
        tmp = open('/tmp/annotations.json','w')
        tmp.write("{\n\"method\":\""+method+"\",\n\"code\":\""+code+"\",\n\"point\":\""+point+" \",\n\"comments\":\""+comments+"\",\n\"imageReference_id\":\""+str(imageReference_id)+"\",\n\"userWhoAnnotated_id\":\""+str(userWhoAnnotated_id)+"\"\n}") 

        tmp.flush()
        catamiWebPortal.importTools.importMetaData.importMetaDataFromFile(tmp.name)

        # Grab the list of entries based on the mission aim keyworkd "unit"
        testEntryList = catamiWebPortal.annotations.objects.filter(comments__startswith="Unit")
        testEntry = testEntryList[len(testEntryList) -1] # will return the last on in the list. Doesn't support [-1] for some reason

        #==================================================#
        # Annotations Assertions
        #==================================================#
        self.assertEqual(string.strip(method), string.strip(testEntry.method))
        self.assertEqual(string.strip(code), string.strip(testEntry.code))
        self.assertEqual(point_x,testEntry.point.x)
        self.assertEqual(point_y,testEntry.point.y)
        self.assertEqual(string.strip(comments),string.strip(testEntry.comments))
        self.assertEqual(imageReference_id,testEntry.imageReference_id)
        self.assertEqual(userWhoAnnotated_id,testEntry.userWhoAnnotated_id)
        
    def test_ImportMetaDataFromDirectory(self):
        dao = self.mocker.CreateMock(catamiWebPortal.importTools.importMetaData)

        #dao.importMetaDataFromDirectory('/dir/file.json') #.AndReturn(1)
        #dao.importMetaDataFromFile('file.json')
        
        self.mocker.ReplayAll()
        #dao.importMetaDataFromDirectory('/dir/file.json')

        self.mocker.VerifyAll()
        
if __name__=='__main__':
    unittest.main()
