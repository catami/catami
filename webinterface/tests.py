"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from django.contrib.auth.models import User
from django.contrib.gis.geos import Point, Polygon
from django.test.client import RequestFactory
from django.test import TestCase
from django.utils.datetime_safe import datetime
from model_mommy import mommy
from model_mommy.recipe import Recipe
from catamidb import authorization
from catamidb.models import AUVDeployment, Image, Camera
from collection.models import Collection
from waffle import Switch


class TestViews(TestCase):
    ''' Main class for webinterface testing'''
    # Flag.objects.create(name='Collections', everyone=False)

    def setUp(self):
        # turn on collections for testing
        # Flag.objects.create(name='Collections', everyone=True)
        # self.flag_mommy = mommy.make_one('waffle.Flag', id=1,
        # name='Collections', everyone=True)  this turns on waffle switched
        # collection code for test we might like to load th waffle.json fixture
        # instead, but it's sitting in catamidb/fixtures
        Switch.objects.create(name='Collections', active=True)

        self.user_bob = User.objects.create_user('bob',
                                                 'daniel@example.com',
                                                 'bob')


        self.factory = RequestFactory()
        self.first_campaign_id = 1
        self.campaign_01 = mommy.make_one('catamidb.Campaign', id=1)
        self.deployment1 = mommy.make_recipe('webinterface.auvdeployment1',
                                             id=1, campaign=self.campaign_01)
        self.deployment2 = mommy.make_recipe('webinterface.auvdeployment2',
                                             id=2, campaign=self.campaign_01)

        self.pose_01 = mommy.make_recipe('webinterface.pose_01',
                                         id=1,
                                         deployment=self.deployment1)

        self.pose_02 = mommy.make_recipe('webinterface.pose_01',
                                         id=2,
                                         deployment=self.deployment2)

        self.camera_01 = mommy.make_one('catamidb.Camera', deployment=self.
        deployment1)

        self.image_01 = mommy.make_one('catamidb.Image',
                                       id=1,
                                       pose=self.pose_01,
                                       camera=self.camera_01
        )

        self.collection_01 = mommy.make_one('collection.Collection', images=[
            self.image_01])

        self.second_campaign_id = 2
        self.third_campaign_id = 3
        self.campaign_02 = mommy.make_one('catamidb.Campaign', id=self.
        second_campaign_id)
        self.campaign_03 = mommy.make_one('catamidb.Campaign', id=self.
        third_campaign_id)

        self.dummy_dep = mommy.make_one('catamidb.Deployment',
                                        start_position=Point(12.4604, 43.9420), end_position=Point(
                12.4604, 43.9420), transect_shape=Polygon(((0.0, 0.0), (0.0, 50.0
            ), (50.0, 50.0), (50.0, 0.0), (0.0, 0.0))), id=1, campaign=self.
            campaign_02)

        self.dummy_dep1 = mommy.make_recipe('webinterface.auvdeployment',
                                            id=3, campaign=self.campaign_02, short_name='campaign'+datetime.now().strftime('%Y%m%d%H%M%S%f'))
        self.dummy_dep2 = mommy.make_recipe('webinterface.bruvdeployment',
                                            id=4, campaign=self.campaign_02, short_name='campaign'+datetime.now().strftime('%Y%m%d%H%M%S%f'))
        self.dummy_dep3 = mommy.make_recipe('webinterface.dovdeployment',
                                            id=5, campaign=self.campaign_02, short_name='campaign'+datetime.now().strftime('%Y%m%d%H%M%S%f'))
        self.dummy_dep4 = mommy.make_recipe('webinterface.tvdeployment', id=6, 
                                            campaign=self.campaign_02, short_name='campaign'+datetime.now().strftime('%Y%m%d%H%M%S%f'))
        self.dummy_dep5 = mommy.make_recipe('webinterface.tideployment', id=7,
                                            campaign=self.campaign_02, short_name='campaign'+datetime.now().strftime('%Y%m%d%H%M%S%f'))

        #apply permissions to the campaigns so we get nice reponses
        authorization.apply_campaign_permissions(self.user_bob, self.campaign_01)
        authorization.apply_campaign_permissions(self.user_bob, self.campaign_02)
        authorization.apply_campaign_permissions(self.user_bob, self.campaign_03)

        # setup some images and assign to deployment_one self.image_list =
        # list() for i in xrange(0, 200): #print i
        # self.image_list.append(mommy.make_one('catamidb.Image',
        # deployment=self.dummy_dep1, image_position=Point(12.4604, 43.9420)))
        # self.test_collection = mommy.make_one('collection.collection', id=1,
        # creation_info='Deployments: 1', images=self.image_list)

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

        response = self.client.get("/api/")
        self.assertEqual(response.status_code, 200)


    def test_campaigns(self):
        """@brief Test campaign browser interfaces

        """
        response = self.client.get("/data/campaigns/")
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/data/campaigns/" + str(self.
        first_campaign_id) + "/")
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/data/campaigns/" + str(self.
        second_campaign_id) + "/")
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/data/campaigns/99999/")
        self.assertEqual(response.status_code, 200)

    #test all deployments
    def test_deployments(self):
        """@brief Test deployment browser interfaces

        """
        response = self.client.get("/data/deployments/")
        self.assertEqual(response.status_code, 200)
