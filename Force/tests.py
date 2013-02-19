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

        # some dummy data from mommy
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
