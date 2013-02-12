"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.

"""

from django.utils import unittest
from django.test.utils import setup_test_environment
from django.test.client import RequestFactory
setup_test_environment()
from django.core import management
import sys
import os
import time
from dateutil import parser
from django.test import TestCase
from Force.models import *
from Force.views import *
from django.contrib.gis.geos import Point

from model_mommy import mommy

# The following is the class in which all functions will be ran by unittest
class TestViews(TestCase):
    ''' Main class for add testing; Can be added to a suite'''


    #fixtures = ['force_data.json', ]


    # The function "setUp" will always be ran in order to setup the
    # test environment before all the tests have run.
    def setUp(self):

        #'''Verify environment is setup properly'''  # Printed if test fails
        #import catami_web_portal
        #os.environ['DJANGO_SETTINGS_MODULE'] = 'catamiPortal.settings'
        #setup_test_environment()

        self.factory = RequestFactory()

        self.first_campaign_id = 1
        self.second_campaign_id = 2
        self.campaign_01 = mommy.make_one('Force.Campaign', id=1)
        self.campaign_02 = mommy.make_one('Force.Campaign', id=2)

        self.dummy_dep = mommy.make_one('Force.Deployment', start_position=Point(12.4604, 43.9420), id=1, campaign=self.campaign_01)

        self.dummy_dep1 = mommy.make_recipe('Force.auvdeployment', id=1, campaign=self.campaign_01)
        self.dummy_dep2 = mommy.make_recipe('Force.bruvdeployment', id=2, campaign=self.campaign_01)
        self.dummy_dep3 = mommy.make_recipe('Force.dovdeployment', id=3, campaign=self.campaign_01)
        self.dummy_dep4 = mommy.make_recipe('Force.tvdeployment', id=4, campaign=self.campaign_01)
        self.dummy_dep5 = mommy.make_recipe('Force.tideployment', id=5, campaign=self.campaign_01)

        #setup some images and assign to deployment_one
        self.image_list = list()
        for i in xrange(0, 1):
            self.image_list.append(mommy.make_one('Force.Image', deployment=self.dummy_dep1, image_position=Point(12.4604, 43.9420)))



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

        # response = self.client.get("/data/spatialsearch/")
        # self.assertEqual(response.status_code, 200)

    def test_campaigns(self):
        """@brief Test campaign browser interfaces

        """

        
        response = self.client.get("/data/campaigns/")
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/data/campaigns/" + str(self.first_campaign_id) + "/")
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/data/campaigns/" + str(self.second_campaign_id) + "/")
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/data/campaigns/99999/")
        self.assertEqual(response.status_code, 200)

    #test all deployments
    def test_deployments(self):
        pass
    
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

        # response = self.client.get("/data/auvdeployments/1/annotationview/0/")
        # self.assertEqual(response.status_code, 200)

        # response = self.client.get("/data/auvdeployments/1/annotationview/1/")
        # self.assertEqual(response.status_code, 200)

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

    # def test_spatialsearch(self):
    #     #test the actual URL
    #     response = self.client.post("/data/spatialsearch/", {'latitude': '113.12', 'longitude': '-23.15', 'searchradius': '100.0'})
    #     self.assertEqual(response.status_code, 200)

    #     #deliberate form error (missing)
    #     response = self.client.post("/data/spatialsearch/", {'latitude': '113.12', 'longitude': '-23.15'})
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(response.context['form']['searchradius'].errors, [u'This field is required.'])

    #     #deliberate form error (non-numeric)
    #     response = self.client.post("/data/spatialsearch/", {'latitude': '113.12', 'longitude': '-23.15', 'searchradius': 'asd'})
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(response.context['form']['searchradius'].errors, [u'Enter a number.'])

    #     #test the spatial search function
    #     request = self.factory.post("/data/spatialsearch/", {'latitude': '113.12', 'longitude': '-23.15', 'searchradius': '100.0'})
    #     response = spatialsearch(request)
    #     self.assertEqual(response.status_code, 200)

        
    def test_checkdb(self):
        """Check that the checkdb command checks the database

        ./manage checkdb is used to check the bounds on Force data
        """
        from StringIO import StringIO
        content = StringIO()
        management.call_command('checkdb', stderr=content, interactive=False)
        content.seek(0)
        data = content.read()
        self.assertTrue(data,'Detected 0 errors in 0 models')

if __name__ == '__main__':
    unittest.main()
