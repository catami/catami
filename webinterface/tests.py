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
from waffle import Switch


class TestViews(TestCase):
    ''' Main class for webinterface testing'''
    # Flag.objects.create(name='Collections', everyone=False)

    def setUp(self):
        # creation_info='Deployments: 1', images=self.image_list)
        return None

    def tearDown(self):
        '''Verify environment is tore down properly'''  # Printed if test fails
        pass


    #==================================================#
    # Add unittests here
    #==================================================#
    def test_views(self):
      return None
