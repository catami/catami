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


    def setUp(self):
        self.factory = RequestFactory()
        self.first_campaign_id = 1
        self.campaign_01 = mommy.make_one('Force.Campaign', id=1)
        self.deployment1 = mommy.make_recipe('webinterface.auvdeployment1', id=1, campaign=self.campaign_01)
        self.deployment2 = mommy.make_recipe('webinterface.auvdeployment2', id=2, campaign=self.campaign_01)


    def test_get_multiple_deployment_extent(self):

        # test OK
        post_data = {"deployment_ids" :  self.deployment1.id.__str__() + "," + self.deployment1.id.__str__() }
        response = self.client.post("/explore/getmapextent", post_data)
        self.assertEqual(response.content.__str__(), "{\"extent\": \"(12.4604, 43.942, 12.4604, 43.942)\"}");

        # test with GET
        response = self.client.get("/explore/getmapextent")
        self.assertEqual(response.content.__str__(), "{\"message\": \"GET operation invalid, must use POST.\"}")