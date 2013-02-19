"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.contrib.gis.geos import Point, Polygon
from django.test.client import RequestFactory
from django.test import TestCase
from django.utils.datetime_safe import datetime
from model_mommy import mommy
from model_mommy.recipe import Recipe
from Force.models import AUVDeployment

class TestViews(TestCase):
    ''' Main class for webinterface testing'''



    def setUp(self):
        self.factory = RequestFactory()
        self.first_campaign_id = 1
        self.campaign_01 = mommy.make_one('Force.Campaign', id=1)
        self.deployment1 = mommy.make_recipe('webinterface.auvdeployment1', id=1, campaign=self.campaign_01)
        self.deployment2 = mommy.make_recipe('webinterface.auvdeployment2', id=2, campaign=self.campaign_01)

        self.factory = RequestFactory()

        self.second_campaign_id = 2
        self.third_campaign_id = 3
        self.campaign_02 = mommy.make_one('Force.Campaign', id=self.second_campaign_id)
        self.campaign_03 = mommy.make_one('Force.Campaign', id=self.third_campaign_id)

        self.dummy_dep = mommy.make_one('Force.Deployment', start_position=Point(12.4604, 43.9420), id=1, campaign=self.campaign_02)

        self.dummy_dep1 = mommy.make_recipe('Force.auvdeployment', id=3, campaign=self.campaign_02)
        self.dummy_dep2 = mommy.make_recipe('Force.bruvdeployment', id=4, campaign=self.campaign_02)
        self.dummy_dep3 = mommy.make_recipe('Force.dovdeployment', id=5, campaign=self.campaign_02)
        self.dummy_dep4 = mommy.make_recipe('Force.tvdeployment', id=6, campaign=self.campaign_02)
        self.dummy_dep5 = mommy.make_recipe('Force.tideployment', id=7, campaign=self.campaign_02)

        #setup some images and assign to deployment_one
        self.image_list = list()
        for i in xrange(0, 1):
            self.image_list.append(mommy.make_one('Force.Image', deployment=self.dummy_dep1, image_position=Point(12.4604, 43.9420)))



    def test_get_multiple_deployment_extent(self):

        # test OK
        post_data = {"deployment_ids" :  self.deployment1.id.__str__() + "," + self.deployment1.id.__str__() }
        response = self.client.post("/explore/getmapextent", post_data)
        self.assertEqual(response.content.__str__(), "{\"extent\": \"(12.4604, 43.942, 12.4604, 43.942)\"}");

        # test with GET
        response = self.client.get("/explore/getmapextent")
        self.assertEqual(response.content.__str__(), "{\"message\": \"GET operation invalid, must use POST.\"}")

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

        response = self.client.get("/explore")
        self.assertEqual(response.status_code, 200)

        #response = self.client.get("/collections/")
        #self.assertEqual(response.status_code, 200)

        # response = self.client.get("/my_collections")
        # self.assertEqual(response.status_code, 200)

        # response = self.client.get("/public_collections")
        # self.assertEqual(response.status_code, 200)

        # response = self.client.get("/api")
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
