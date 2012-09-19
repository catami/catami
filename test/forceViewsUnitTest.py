from django.utils import unittest 
from django.test.utils import setup_test_environment
setup_test_environment()
import sys
import os
import time
from dateutil import parser
from django.test import TestCase
from Force import *

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

    # The function "tearDown" will always be ran in order to cleanup the
    # test environment after all the tests have run.
    def tearDown(self):
        '''Verify environment is tore down properly''' # Printed if test fails
        pass

    #==================================================#
    # Add unittests here
    #==================================================#
    def testViews(self):
            response = self.client.get("/main/")
            self.assertEqual(response.status_code, 200)

            response = self.client.get("/main/campaigns/")
            self.assertEqual(response.status_code, 200)
          
            response = self.client.get("/main/auvdeployments/")
            self.assertEqual(response.status_code, 200)

            #response = self.client.get("/main/auvdeployments/1/")
            #self.assertEqual(response.status_code, 200)  

            response = self.client.get("/main/campaigns/1/")
            self.assertEqual(response.status_code, 200) 

if __name__=='__main__':
    unittest.main()

