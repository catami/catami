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
        testEntryList = catamiWebPortal.User.objects.filter(name__startswith="Dan")
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
        short_name = 'Short Name'
        associated_researchers = 'Dan M, Mat W, Luke E, Mark G'
        associated_publications = 'test.pdf, two.pdf'
        associated_research_grant = 'Grant number 3131321'
        date_start = '2011-10-19'
        date_end = '2011-10-21'

        # Create a dummy file we know the details of, read in the file, check the database contents
        tmp = open('/tmp/campaign.json','w')
        tmp.write("{\n\"description\":\""+description+"\",\n\"short_name\":\""+short_name+"\",\n\"associated_researchers\":\""+associated_researchers+"\",\n\"associated_publications\":\""+associated_publications+" \",\n\"associated_research_grant\":\""+associated_research_grant+"\",\n\"date_start\":\""+date_start+"\",\n\"date_end\":\""+date_end+"\"\n}") 

        tmp.flush()
        catamiWebPortal.importTools.importMetaData.importMetaDataFromFile(tmp.name)

        # Grab the list of entries based on the mission aim keyworkd "unit"
        testEntryList = catamiWebPortal.Campaign.objects.filter(description__startswith="Unit")
        testEntry = testEntryList[len(testEntryList) -1] # will return the last on in the list. Doesn't support [-1] for some reason

        #==================================================#
        # Campaign Assertions
        #==================================================#
        self.assertEqual(string.strip(description), string.strip(testEntry.description))
        self.assertEqual(string.strip(short_name), string.strip(testEntry.short_name))
        #self.assertEqual(associated_researchers, testEntry.associated_researchers)
        #self.assertEqual(associated_publications, testEntry.associated_publications)
        #self.assertEqual(string.strip(associated_research_grant), string.strip(testEntry.associated_research_grant))
        self.assertEqual(parser.parse(date_start).date(),testEntry.date_start)
        self.assertEqual(parser.parse(date_end).date(),testEntry.date_end)
        
        #==================================================#
        # Auv deployment data file
        #==================================================#
        start_time_stamp = '2011-10-19 10:23:54+08:00'
        end_time_stamp = '2011-10-19 14:23:54+08:00'
        mission_aim = 'Unit Test'
        min_depth = 10.0
        max_depth = 20.0
        start_position_x = -23.15
        start_position_y = 113.12
        start_position = 'POINT('+str(start_position_x)+' '+str(start_position_y)+')'
        short_name = 'Short Name'
        distance_covered = 20.3
        transect_shape_x = [-23.15,-23.53,-23.67,-23.25,-23.15]
        transect_shape_y = [113.12,113.34,112.9,112.82,113.12]
        transect_shape = 'POLYGON(('+str(transect_shape_x[0])+' '+str(transect_shape_y[0])+', '+str(transect_shape_x[1])+' '+str(transect_shape_y[1])+', '+str(transect_shape_x[2])+' '+str(transect_shape_y[2])+', '+str(transect_shape_x[3])+' '+str(transect_shape_y[3])+', '+str(transect_shape_x[4])+' '+str(transect_shape_y[4])+'))'
        campaign_id = 1
        
        # Create a dummy file we know the details of, read in the file, check the database contents
        tmp = open('/tmp/auvdeployment.json','w')
        tmp.write("{\n\"start_time_stamp\":\""+start_time_stamp+"\",\n\"end_time_stamp\":\""+end_time_stamp+"\",\n\"short_name\":\""+short_name+"\",\n\"mission_aim\":\""+mission_aim+" \",\n\"min_depth\":"+str(min_depth)+",\n\"max_depth\":"+str(max_depth)+",\n\"start_position\":\""+start_position+"\",\n\"distance_covered\":"+str(distance_covered)+",\n\"transect_shape\":\""+transect_shape+"\",\n\"campaign_id\":"+str(campaign_id)+"\n}")

        tmp.flush()
        catamiWebPortal.importTools.importMetaData.importMetaDataFromFile(tmp.name)

        # Grab the list of entries based on the mission aim keyworkd "unit"
        testEntryList = catamiWebPortal.AUVDeployment.objects.filter(mission_aim__startswith="Unit")
        testEntry = testEntryList[len(testEntryList) -1] # will return the last on in the list. Doesn't support [-1] for some reason

        #==================================================#
        # AUV deployment Assertions
        #==================================================#
        self.assertEqual(parser.parse(start_time_stamp),testEntry.start_time_stamp)
        self.assertEqual(parser.parse(end_time_stamp),testEntry.end_time_stamp)
        self.assertEqual(string.strip(mission_aim),string.strip(str(testEntry.mission_aim)))
        self.assertEqual(min_depth,testEntry.min_depth)
        self.assertEqual(max_depth,testEntry.max_depth)
        self.assertEqual(start_position_x,testEntry.start_position.x)
        self.assertEqual(start_position_y, testEntry.start_position.y)

        for i in range(0,len(transect_shape_x)):
            self.assertEqual(transect_shape_x[i],testEntry.transect_shape.coords[0][i][0])
            
        for j in range(0,len(transect_shape_y)):
            self.assertEqual(transect_shape_y[j],testEntry.transect_shape.coords[0][j][1])
            
        self.assertEqual(distance_covered,testEntry.distance_covered)

        #==================================================#
        # images data file
        #==================================================#
        left_thumbnail_reference = "https://df.arcs.org.au/ARCS/projects/IMOS/public/AUV//Tasmania201106/r20110614_055332_flindersCMRnorth_09_canyongrids/i20110614_055332_gtif/PR_20110614_061205_092_LC16.tif"
        left_image_reference = "https://df.arcs.org.au/ARCS/projects/IMOS/public/AUV//Tasmania201106/r20110614_055332_flindersCMRnorth_09_canyongrids/i20110614_055332_gtif/PR_20110614_061205_092_LC16.tif"
        temperature = 15.211
        yaw = 2.9119767014847424
        image_position_x = -40.5446848363899335
        image_position_y = 148.8015551780569012
        image_position = "\"POINT ("+str(image_position_x)+" "+str(image_position_y)+")\""
        date_time = "2011-06-14 16:12:05.092029+08:00"
        depth = 120.13268785071226
        pitch = -0.0250635711698782
        salinity = 35.471
        altitude = 2.0
        roll = 0.3
        deployment_id = 1

        # Create a dummy file we know the details of, read in the file, check the database contents
        tmp = open('/tmp/image.json','w')
        tmp.write("{\n\"left_thumbnail_reference\":\""+left_thumbnail_reference+"\",\n\"left_image_reference\":\""+left_image_reference+"\",\n\"temperature\":"+str(temperature)+" ,\n\"yaw\":"+str(yaw)+",\n\"image_position\":"+image_position+",\n\"date_time\":\""+date_time+"\",\n\"depth\":"+str(depth)+",\n\"pitch\":"+str(pitch)+",\n\"salinity\":"+str(salinity)+",\n\"altitude\":"+str(altitude)+",\n\"roll\":"+str(roll)+",\n\"deployment_id\":"+str(deployment_id)+"\n}")

        tmp.flush()
        catamiWebPortal.importTools.importMetaData.importMetaDataFromFile(tmp.name)

        # Grab the list of entries based on the mission aim keyworkd "unit"
        testEntryList = catamiWebPortal.Image.objects.filter(left_thumbnail_reference__startswith="https://df.arcs.org.au/ARCS/projects/IMOS/public/AUV//Tasmania201106/r20110614_055332_flindersCMRnorth_09_canyongrids/i20110614_055332_gtif/PR_20110614_061205_092_LC16.tif")
        testEntry = testEntryList[len(testEntryList) -1] # will return the last on in the list. Doesn't support [-1] for some reason

        #==================================================#
        # Image Assertions
        #==================================================#
        self.assertEqual(parser.parse(date_time),testEntry.date_time)
        self.assertEqual(string.strip(left_thumbnail_reference),string.strip(str(testEntry.left_thumbnail_reference)))
        self.assertEqual(string.strip(left_image_reference),string.strip(str(testEntry.left_image_reference)))
        self.assertEqual(temperature,testEntry.temperature)
        self.assertAlmostEqual(yaw,testEntry.yaw)
        self.assertAlmostEqual(image_position_x, testEntry.image_position.x)
        self.assertAlmostEqual(image_position_y, testEntry.image_position.y)
        self.assertAlmostEqual(depth, testEntry.depth)
        self.assertAlmostEqual(pitch,testEntry.pitch)
        self.assertAlmostEqual(salinity, testEntry.salinity)
        self.assertAlmostEqual(altitude, testEntry.altitude)
        self.assertAlmostEqual(roll,testEntry.roll)
        self.assertEqual(deployment_id,testEntry.deployment_id)

        #==================================================#
        # stereoImages data file
        #==================================================#
        right_thumbnail_reference = "https://df.arcs.org.au/ARCS/projects/IMOS/public/AUV//Tasmania201106/r20110614_055332_flindersCMRnorth_09_canyongrids/i20110614_055332_gtif/PR_20110614_061205_093_RM16.tif"
        right_image_reference = "https://df.arcs.org.au/ARCS/projects/IMOS/public/AUV//Tasmania201106/r20110614_055332_flindersCMRnorth_09_canyongrids/i20110614_055332_gtif/PR_20110614_061205_093_RM16.tif"
        date_time = "2011-06-14 16:12:05.093+08:00"


        # Create a dummy file we know the details of, read in the file, check the database contents
        tmp = open('/tmp/stereoImages.json','w')
        tmp.write("{\n\"left_thumbnail_reference\":\""+left_thumbnail_reference+"\",\n\"left_image_reference\":\""+left_image_reference+"\",\n\"right_thumbnail_reference\":\""+right_thumbnail_reference+"\",\n\"right_image_reference\":\""+right_image_reference+"\",\n\"temperature\":"+str(temperature)+" ,\n\"yaw\":"+str(yaw)+",\n\"image_position\":"+image_position+",\n\"date_time\":\""+date_time+"\",\n\"depth\":"+str(depth)+",\n\"pitch\":"+str(pitch)+",\n\"salinity\":"+str(salinity)+",\n\"altitude\":"+str(altitude)+",\n\"roll\":"+str(roll)+",\n\"deployment_id\":"+str(deployment_id)+"\n}")

        tmp.flush()
        catamiWebPortal.importTools.importMetaData.importMetaDataFromFile(tmp.name)

        testEntryList = catamiWebPortal.StereoImage.objects.filter(right_thumbnail_reference__startswith="https://df.arcs.org.au/ARCS/projects/IMOS/public/AUV//Tasmania201106/r20110614_055332_flindersCMRnorth_09_canyongrids/i20110614_055332_gtif/PR_20110614_061205_093_RM16.tif")
        testEntry = testEntryList[len(testEntryList) -1] # will return the last on in the list. Doesn't support [-1] for some reason

        #==================================================#
        # Stereo Images Assertions
        #==================================================#
        self.assertEqual(parser.parse(date_time),testEntry.date_time)
        self.assertEqual(string.strip(left_thumbnail_reference),string.strip(str(testEntry.left_thumbnail_reference)))
        self.assertEqual(string.strip(left_image_reference),string.strip(str(testEntry.left_image_reference)))
        self.assertEqual(string.strip(right_thumbnail_reference),string.strip(str(testEntry.right_thumbnail_reference)))
        self.assertEqual(string.strip(right_image_reference),string.strip(str(testEntry.right_image_reference)))
        self.assertEqual(temperature,testEntry.temperature)
        self.assertAlmostEqual(yaw,testEntry.yaw)
        self.assertAlmostEqual(image_position_x,testEntry.image_position.x)
        self.assertAlmostEqual(image_position_y, testEntry.image_position.y)
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
        image_reference_id = 1
        user_who_annotated_id = 1

        # Create a dummy file we know the details of, read in the file, check the database contents
        tmp = open('/tmp/annotations.json','w')
        tmp.write("{\n\"method\":\""+method+"\",\n\"code\":\""+code+"\",\n\"point\":\""+point+" \",\n\"comments\":\""+comments+"\",\n\"image_reference_id\":\""+str(image_reference_id)+"\",\n\"user_who_annotated_id\":\""+str(user_who_annotated_id)+"\"\n}") 

        tmp.flush()
        catamiWebPortal.importTools.importMetaData.importMetaDataFromFile(tmp.name)

        # Grab the list of entries based on the mission aim keyworkd "unit"
        testEntryList = catamiWebPortal.Annotations.objects.filter(comments__startswith="Unit")
        testEntry = testEntryList[len(testEntryList) -1] # will return the last on in the list. Doesn't support [-1] for some reason

        #==================================================#
        # Annotations Assertions
        #==================================================#
        self.assertEqual(string.strip(method), string.strip(testEntry.method))
        self.assertEqual(string.strip(code), string.strip(testEntry.code))
        self.assertEqual(point_x,testEntry.point.x)
        self.assertEqual(point_y,testEntry.point.y)
        self.assertEqual(string.strip(comments),string.strip(testEntry.comments))
        self.assertEqual(image_reference_id,testEntry.image_reference_id)
        self.assertEqual(user_who_annotated_id,testEntry.user_who_annotated_id)

        #print dir(testEntry)
        
    def test_ImportMetaDataFromDirectory(self):
        dao = self.mocker.CreateMock(catamiWebPortal.importTools.importMetaData)

        #dao.importMetaDataFromDirectory('/dir/file.json') #.AndReturn(1)
        #dao.importMetaDataFromFile('file.json')
        
        self.mocker.ReplayAll()
        #dao.importMetaDataFromDirectory('/dir/file.json')

        self.mocker.VerifyAll()
        
if __name__=='__main__':
    unittest.main()
