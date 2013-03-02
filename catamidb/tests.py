"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.

"""
from django.contrib.admin import AdminSite
from django.contrib.auth.models import User, Group
from django.forms import ModelForm
from django.http import HttpRequest

from django.utils import unittest
from django.test.utils import setup_test_environment
from django.test.client import RequestFactory
import guardian
from guardian.shortcuts import assign
from model_mommy import mommy
from tastypie.test import ResourceTestCase, TestApiClient
from catamiPortal import settings
from catamidb import authorization
from catamidb.models import Campaign

setup_test_environment()
from django.core import management
import sys
import os
import time
from dateutil import parser
from django.test import TestCase
from django.contrib.gis.geos import Point
from django.contrib.auth.models import AnonymousUser

#======================================#
# Test the authorization.py functions
#======================================#
class TestAuthorizationRules(TestCase):

    def setUp(self):

        #create an actual user
        self.user = User.objects.create_user("Joe")

        #create an anonymous user, to apply view permissions to
        self.anonymous_user =  guardian.utils.get_anonymous_user() #User.objects.get(id=settings.ANONYMOUS_USER_ID)

        #'prepare' a campaign, do not persist it yet
        self.campaign_one = mommy.make_one('catamidb.Campaign', id=1)

        #add users to the Public group
        public_group, created = Group.objects.get_or_create(name='Public')
        self.anonymous_user.groups.add(public_group)
        self.user.groups.add(public_group)

        print self.anonymous_user.id

    def tearDown(self):
        pass

    #==================================================#
    # Add unittests here
    #==================================================#

    def test_campaign_permissions_assigned(self):
        #this is the important call, it applies the permissions to the campaign object before saving
        authorization.apply_campaign_permissions(self.user, self.campaign_one)

        #check that our created user has ALL permissions to the campaign
        self.assertTrue(self.user.has_perm('catamidb.view_campaign', self.campaign_one))
        self.assertTrue(self.user.has_perm('catamidb.add_campaign', self.campaign_one))
        self.assertTrue(self.user.has_perm('catamidb.change_campaign', self.campaign_one))
        self.assertTrue(self.user.has_perm('catamidb.delete_campaign', self.campaign_one))

        #check that the only thing the anonymous user can do is view the campaign
        self.assertTrue(self.anonymous_user.has_perm('catamidb.view_campaign', self.campaign_one))
        self.assertFalse(self.anonymous_user.has_perm('catamidb.add_campaign', self.campaign_one))
        self.assertFalse(self.anonymous_user.has_perm('catamidb.change_campaign', self.campaign_one))
        self.assertFalse(self.anonymous_user.has_perm('catamidb.delete_campaign', self.campaign_one))

#======================================#
# Test the API                         #
#======================================#

class TestCampaignResource(ResourceTestCase):

    def setUp(self):

        #Tastypie stuff
        super(TestCampaignResource, self).setUp()

        self.bob_api_client = TestApiClient()
        self.bill_api_client = TestApiClient()
        self.anon_api_client = TestApiClient()

        # Create a user bob.
        self.user_bob_username = 'bob'
        self.user_bob_password = 'bob'
        self.user_bob = User.objects.create_user(self.user_bob_username, 'daniel@example.com', self.user_bob_password)

        # Create a user bob.
        self.user_bill_username = 'bill'
        self.user_bill_password = 'bill'
        self.user_bill = User.objects.create_user(self.user_bill_username, 'daniel@example.com', self.user_bill_password)

        self.bob_api_client.client.login(username='bob', password='bob')
        self.bill_api_client.client.login(username='bill', password='bill')

        #assign users to the Public group
        public_group, created = Group.objects.get_or_create(name='Public')
        self.user_bob.groups.add(public_group)
        self.user_bill.groups.add(public_group)
        guardian.utils.get_anonymous_user().groups.add(public_group)

        #make a couple of campaigns and save
        self.campaign_bobs = mommy.make_one('catamidb.Campaign', id=1)
        self.campaign_bills = mommy.make_one('catamidb.Campaign', id=2)

        #assign this one to bob
        authorization.apply_campaign_permissions(self.user_bob, self.campaign_bobs)

        #assign this one to bill
        authorization.apply_campaign_permissions(self.user_bill, self.campaign_bills)

        #the API url for campaigns
        self.campaign_url = '/api/dev/campaign/'

        #some post data for testing campaign creation
        self.post_data = {
            'short_name': 'Blah',
            'description': 'Blah',
            'associated_researchers': 'Blah',
            'associated_publications': 'Blah',
            'associated_research_grant': 'Blah',
            'date_start': '2012-05-01',
            'date_end': '2012-05-01',
            'contact_person': 'Blah',
        }

    # can only do GET at this stage
    def test_campaign_operations_disabled(self):
        # test that we can NOT create
        self.assertHttpMethodNotAllowed(self.anon_api_client.post(self.campaign_url, format='json', data=self.post_data))

        # test that we can NOT modify
        self.assertHttpMethodNotAllowed(self.anon_api_client.put(self.campaign_url + self.campaign_bobs.id.__str__() + "/", format='json', data={}))

        # test that we can NOT delete
        self.assertHttpMethodNotAllowed(self.anon_api_client.delete(self.campaign_url + self.campaign_bobs.id.__str__() + "/", format='json'))

        # test that we can NOT create authenticated
        self.assertHttpMethodNotAllowed(self.bob_api_client.post(self.campaign_url, format='json', data=self.post_data))

        # test that we can NOT modify authenticated
        self.assertHttpMethodNotAllowed(self.bob_api_client.put(self.campaign_url + self.campaign_bobs.id.__str__() + "/", format='json', data={}))

        # test that we can NOT delete authenticated
        self.assertHttpMethodNotAllowed(self.bob_api_client.delete(self.campaign_url + self.campaign_bobs.id.__str__() + "/", format='json'))

    #test can get a list of campaigns authorised
    def test_campaigns_operations_as_authorised_users(self):
        # create a campaign that only bill can see
        bills_campaign = mommy.make_one('catamidb.Campaign', id=3)
        assign('view_campaign', self.user_bill, bills_campaign)

        # check that bill can see via the API
        response = self.bill_api_client.get(self.campaign_url, format='json')
        self.assertValidJSONResponse(response)
        self.assertEqual(len(self.deserialize(response)['objects']), 3)

        # check that bill can get to the object itself
        response = self.bill_api_client.get(self.campaign_url + "3/", format='json')
        self.assertValidJSONResponse(response)

        # check that bob can not see - now we know tastypie API has correct permission validation
        response = self.bob_api_client.get(self.campaign_url, format='json')
        self.assertValidJSONResponse(response)
        self.assertEqual(len(self.deserialize(response)['objects']), 2)

        # check bob can NOT get to the hidden object
        response = self.bob_api_client.get(self.campaign_url + "3/", format='json')
        self.assertHttpUnauthorized(response)

        #check that anonymous can see public ones as well
        response = self.anon_api_client.get(self.campaign_url, format='json')
        self.assertValidJSONResponse(response)
        self.assertEqual(len(self.deserialize(response)['objects']), 2)

        #check anonymous can NOT get to the hidden object
        response = self.anon_api_client.get(self.campaign_url + "3/", format='json')
        self.assertHttpUnauthorized(response)

if __name__ == '__main__':
    unittest.main()
