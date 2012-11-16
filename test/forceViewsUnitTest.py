from django.utils import unittest
from django.test.utils import setup_test_environment
from django.test.client import RequestFactory
setup_test_environment()
import sys
import os
import time
from dateutil import parser
from django.test import TestCase
from Force.models import *
from Force.views import *


# The following is the class in which all functions will be ran by unittest
class AddTest(TestCase):
    ''' Main class for add testing; Can be added to a suite'''

    # The function "setUp" will always be ran in order to setup the
    # test environment before all the tests have run.
    def setUp(self):

        '''Verify environment is setup properly'''  # Printed if test fails
        import catami_web_portal
        os.environ['DJANGO_SETTINGS_MODULE'] = 'catamiPortal.settings'
        setup_test_environment()

        self.factory = RequestFactory()

        #test data
        transect_shape_x = [-23.15, -23.53, -23.67, -23.25, -23.15]
        transect_shape_y = [113.12, 113.34, 112.9, 112.82, 113.12]
        min_depth = 5.0
        max_depth = 25.0
        time_start_00 = '2011-10-19 10:21:54+08:00'
        time_start = '2011-10-19 10:23:54+08:00'
        time_end = '2011-10-19 18:23:54+08:00'
        distance_covered = 20.3
        test_aim = 'unit test'
        test_short_name_auv = 'unit test deployment auv'
        test_short_name_bruv = 'unit test deployment bruv'
        test_short_name_dov = 'unit test deployment dov'
        test_short_name_ti = 'unit test deployment ti'
        test_short_name_tv = 'unit test deployment tv'

        #campaign01 has deployments
        campaign_01 = Campaign.objects.create(
            short_name='test campaign',
            description='dummy campaign for testing',
            associated_researchers='A. Nonymous',
            associated_publications='Document.pdf',
            associated_research_grant='Grant Reference',
            date_start='2011-10-01',
            date_end='2011-10-31'
        )
        transect_shape_x = [-23.15, -23.53, -23.67, -23.25, -23.15]
        transect_shape_y = [113.12, 113.34, 112.9, 112.82, 113.12]

        auv_deployment = AUVDeployment.objects.create(
            start_position='POINT(' + str(transect_shape_x[0]) + ' ' + str(transect_shape_y[0]) + ')',
            start_time_stamp=time_start,
            end_time_stamp=time_end,
            short_name=test_short_name_auv,
            mission_aim=test_aim,
            min_depth=min_depth,
            max_depth=max_depth,
            campaign=campaign_01,
            distance_covered=distance_covered,
            transect_shape='POLYGON((' + str(transect_shape_x[0]) + ' ' + str(transect_shape_y[0]) + ', ' + str(transect_shape_x[1]) + ' ' + str(transect_shape_y[1]) + ', ' + str(transect_shape_x[2]) + ' ' + str(transect_shape_y[2]) + ', ' + str(transect_shape_x[3]) + ' ' + str(transect_shape_y[3]) + ', ' + str(transect_shape_x[4]) + ' ' + str(transect_shape_y[4]) + '))'
        )

        image_00 = StereoImage.objects.create(
            deployment = auv_deployment,
            left_thumbnail_reference = 'http://df.arcs.org.au/ARCS/projects/IMOS/public/AUV//Tasmania200810/r20081006_231255_waterfall_05_transect/i20081006_231255_gtif/PR_20081006_231732_335_LC16.tif',
            left_image_reference = 'http://df.arcs.org.au/ARCS/projects/IMOS/public/AUV//Tasmania200810/r20081006_231255_waterfall_05_transect/i20081006_231255_gtif/PR_20081006_231732_335_LC16.tif',
            right_thumbnail_reference = 'http://df.arcs.org.au/ARCS/projects/IMOS/public/AUV//Tasmania200810/r20081006_231255_waterfall_05_transect/i20081006_231255_gtif/PR_20081006_231732_335_LC16.tif',
            right_image_reference = 'http://df.arcs.org.au/ARCS/projects/IMOS/public/AUV//Tasmania200810/r20081006_231255_waterfall_05_transect/i20081006_231255_gtif/PR_20081006_231732_335_LC16.tif',
            date_time = time_start_00,
            image_position = 'POINT(' + str(transect_shape_x[0]) + ' ' + str(transect_shape_y[0]) + ')',
            temperature = 12.0,
            salinity = 35.0,
            pitch = 0.05,
            roll = 0.02,
            yaw = .38,
            altitude = 35.5,
            depth = 1.49
        )

        image_01 = StereoImage.objects.create(
            deployment = auv_deployment,
            left_thumbnail_reference = 'http://df.arcs.org.au/ARCS/projects/IMOS/public/AUV//Tasmania200810/r20081006_231255_waterfall_05_transect/i20081006_231255_gtif/PR_20081006_231732_335_LC16.tif',
            left_image_reference = 'http://df.arcs.org.au/ARCS/projects/IMOS/public/AUV//Tasmania200810/r20081006_231255_waterfall_05_transect/i20081006_231255_gtif/PR_20081006_231732_335_LC16.tif',
            right_thumbnail_reference = 'http://df.arcs.org.au/ARCS/projects/IMOS/public/AUV//Tasmania200810/r20081006_231255_waterfall_05_transect/i20081006_231255_gtif/PR_20081006_231732_335_LC16.tif',
            right_image_reference = 'http://df.arcs.org.au/ARCS/projects/IMOS/public/AUV//Tasmania200810/r20081006_231255_waterfall_05_transect/i20081006_231255_gtif/PR_20081006_231732_335_LC16.tif',
            date_time = time_start,
            image_position = 'POINT(' + str(transect_shape_x[0]) + ' ' + str(transect_shape_y[0]) + ')',
            temperature = 12.0,
            salinity = 35.0,
            pitch = 0.05,
            roll = 0.02,
            yaw = .38,
            altitude = 35.5,
            depth = 1.49
        )

        test_user = User.objects.create(
            name = 'Test Test',
            title = 'Mr',
            organisation = 'Not Really',
            email = 'devnull@127.0.0.1'
        )

        annotation_01 = Annotation.objects.create(
            method = '1 point imaginary method',
            image_reference = image_01,
            code = 'sand',
            point = 'POINT(10 10)',
            user_who_annotated = test_user,
            comments = 'none'
        )
        
        bruv_deployment = BRUVDeployment.objects.create(
            start_position='POINT(' + str(transect_shape_x[0]) + ' ' + str(transect_shape_y[0]) + ')',
            start_time_stamp=time_start,
            end_time_stamp=time_end,
            short_name=test_short_name_bruv,
            mission_aim=test_aim,
            min_depth=min_depth,
            max_depth=max_depth,
            campaign=campaign_01
        )

        dov_deployment = DOVDeployment.objects.create(
            start_position='POINT(' + str(transect_shape_x[0]) + ' ' + str(transect_shape_y[0]) + ')',
            start_time_stamp=time_start,
            end_time_stamp=time_end,
            short_name=test_short_name_dov,
            mission_aim=test_aim,
            min_depth=min_depth,
            max_depth=max_depth,
            campaign=campaign_01,
            diver_name='Jim Diver'
        )

        tv_deployment = TVDeployment.objects.create(
            start_position='POINT(' + str(transect_shape_x[0]) + ' ' + str(transect_shape_y[0]) + ')',
            start_time_stamp=time_start,
            end_time_stamp=time_end,
            short_name=test_short_name_tv,
            mission_aim=test_aim,
            min_depth=min_depth,
            max_depth=max_depth,
            campaign=campaign_01
        )

        ti_deployment = TIDeployment.objects.create(
            start_position='POINT(' + str(transect_shape_x[0]) + ' ' + str(transect_shape_y[0]) + ')',
            start_time_stamp=time_start,
            end_time_stamp=time_end,
            short_name=test_short_name_ti,
            mission_aim=test_aim,
            min_depth=min_depth,
            max_depth=max_depth,
            campaign=campaign_01
        )
        #campaign02 has no deployments
        campaign_02 = Campaign.objects.create(
            short_name='test 02 campaign',
            description='dummy campaign for testing',
            associated_researchers='A. Nonymous',
            associated_publications='Document.pdf',
            associated_research_grant='Grant Reference',
            date_start='2010-10-01',
            date_end='2010-10-31'
        )

    # The function "tearDown" will always be ran in order to cleanup the
    # test environment after all the tests have run.
    def tearDown(self):
        '''Verify environment is tore down properly'''  # Printed if test fails
        pass

    #==================================================#
    # Add unittests here
    #==================================================#
    def test_views(self):
        """@brief Test top level interfaces

        """
        response = self.client.get("/data/")
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/data/spatialsearch/")
        self.assertEqual(response.status_code, 200)

    def test_campaigns(self):
        """@brief Test campaign browser interfaces

        """
        response = self.client.get("/data/campaigns/")
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/data/campaigns/1/")
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/data/campaigns/2/")
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/data/campaigns/99999/")
        self.assertEqual(response.status_code, 200)


    #test all deployments
    def test_deployments(self):
        """@brief Test deployment browser interfaces

        """
        response = self.client.get("/data/deployments/")
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/data/deployments/map/")
        self.assertEqual(response.status_code, 200)


    def test_auvdeployments(self):
        """@brief Test AUV deployment browser interfaces

        """
        response = self.client.get("/data/auvdeployments/")
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/data/auvdeployments/1/")
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/data/auvdeployments/1/annotationview/0/")
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/data/auvdeployments/99999/")
        self.assertEqual(response.status_code, 200)


    def test_bruvdeployments(self):
        """@brief Test BRUV deployment browser interfaces

        """        
        response = self.client.get("/data/bruvdeployments/")
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/data/bruvdeployments/1/")
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/data/bruvdeployments/99999/")
        self.assertEqual(response.status_code, 200)


    def test_dovdeployments(self):
        """@brief Test DOV deployment browser interfaces

        """             
        response = self.client.get("/data/dovdeployments/")
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/data/dovdeployments/1/")
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/data/dovdeployments/99999/")
        self.assertEqual(response.status_code, 200)

    def test_tveployments(self):
        """@brief Test TV deployment browser interfaces

        """          
        response = self.client.get("/data/tvdeployments/")
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/data/tvdeployments/1/")
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/data/tvdeployments/99999/")
        self.assertEqual(response.status_code, 200)

    def test_tideployments(self):
        """@brief Test TI deployment browser interfaces

        """          
        response = self.client.get("/data/tideployments/")
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/data/tideployments/1/")
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/data/tideployments/99999/")
        self.assertEqual(response.status_code, 200)

    def test_spatialsearch(self):
        #test the actual URL
        response = self.client.post("/data/spatialsearch/", {'latitude': '113.12', 'longitude': '-23.15', 'searchradius': '100.0'})
        self.assertEqual(response.status_code, 200)

        #deliberate form error (missing)
        response = self.client.post("/data/spatialsearch/", {'latitude': '113.12', 'longitude': '-23.15'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['form']['searchradius'].errors, [u'This field is required.'])


        #deliberate form error (non-numeric)
        response = self.client.post("/data/spatialsearch/", {'latitude': '113.12', 'longitude': '-23.15', 'searchradius': 'asd'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['form']['searchradius'].errors, [u'Enter a number.'])

        #test the spatial search function
        request = self.factory.post("/data/spatialsearch/", {'latitude': '113.12', 'longitude': '-23.15', 'searchradius': '100.0'})
        response = spatialsearch(request)
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
