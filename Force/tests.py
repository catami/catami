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
from django.contrib.gis.geos import Point

# The following is the class in which all functions will be ran by unittest
class TestViews(TestCase):
    ''' Main class for add testing; Can be added to a suite'''


    #fixtures = ['force_data.json', ]


    # The function "setUp" will always be ran in order to setup the
    # test environment before all the tests have run.
    def setUp(self):

        # some dummy data from mommy
        self.factory = RequestFactory()


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
