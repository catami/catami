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
from guardian.shortcuts import assign, get_perms, get_perms_for_model
from model_mommy import mommy
from tastypie.test import ResourceTestCase, TestApiClient
from catamiPortal import settings
from catamidb import authorization
from catamidb.models import Campaign, Image, Measurements, Deployment

setup_test_environment()
from django.core import management
import sys
import os
import time
from dateutil import parser
from django.test import TestCase
from django.contrib.gis.geos import Point
from django.contrib.auth.models import AnonymousUser
from datetime import datetime
import logging
import socket

#disable logging on the build server so it goes faster, and model mommy
#output does not interfere with jenkins XML files
if "build" in socket.gethostname():
    logging.disable(logging.DEBUG)


#======================================#
# Test the authorization.py functions
#======================================#
class TestAuthorizationRules(TestCase):
    def setUp(self):
        #create an actual user
        self.user = User.objects.create_user("Joe")

        #create an anonymous user, to apply view permissions to
        self.anonymous_user = guardian.utils.get_anonymous_user()
        # User.objects.get(id=settings.ANONYMOUS_USER_ID)

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
        # this is the important call, it applies the permissions to the
        # campaign object before saving
        authorization.apply_campaign_permissions(self.user, self.campaign_one)

        #check that our created user has ALL permissions to the campaign
        self.assertTrue(self.user.has_perm('catamidb.view_campaign',
                                           self.campaign_one))
        self.assertTrue(self.user.has_perm('catamidb.add_campaign',
                                           self.campaign_one))
        self.assertTrue(self.user.has_perm('catamidb.change_campaign',
                                           self.campaign_one))
        self.assertTrue(self.user.has_perm('catamidb.delete_campaign',
                                           self.campaign_one))

        # check that the only thing the anonymous user can do is view the
        # campaign
        self.assertTrue(self.anonymous_user.has_perm('catamidb.view_campaign',
                                                     self.campaign_one))
        self.assertFalse(self.anonymous_user.has_perm('catamidb.add_campaign',
                                                      self.campaign_one))
        self.assertFalse(self.anonymous_user.has_perm(
            'catamidb.change_campaign',
            self.campaign_one)
        )
        self.assertFalse(
            self.anonymous_user.has_perm(
                'catamidb.delete_campaign',
                self.campaign_one
            )
        )

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
        self.user_bob = User.objects.create_user(self.user_bob_username,
                                                 'daniel@example.com',
                                                 self.user_bob_password)

        # Create a user bob.
        self.user_bill_username = 'bill'
        self.user_bill_password = 'bill'
        self.user_bill = User.objects.create_user(self.user_bill_username,
                                                  'daniel@example.com',
                                                  self.user_bill_password)

        self.bob_api_client.client.login(username='bob', password='bob')
        self.bill_api_client.client.login(username='bill', password='bill')

        #assign users to the Public group
        public_group, created = Group.objects.get_or_create(name='Public')
        self.user_bob.groups.add(public_group)
        self.user_bill.groups.add(public_group)
        guardian.utils.get_anonymous_user().groups.add(public_group)

        #make a couple of campaigns and save
        self.campaign_bobs = mommy.make_one('catamidb.Campaign')
        self.campaign_bills = mommy.make_one('catamidb.Campaign')

        #assign this one to bob
        authorization.apply_campaign_permissions(
            self.user_bob, self.campaign_bobs)

        #assign this one to bill
        authorization.apply_campaign_permissions(
            self.user_bill, self.campaign_bills)

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
        # test that we are unauthorized to create

        self.assertHttpUnauthorized(
            self.anon_api_client.post(self.campaign_url,
                                      format='json',
                                      data=self.post_data))

        # test that we can NOT modify
        self.assertHttpMethodNotAllowed(
            self.anon_api_client.put(
                self.campaign_url + self.campaign_bobs.id.__str__() + "/",
                format='json',
                data={})
        )

        # test that we can NOT delete
        self.assertHttpMethodNotAllowed(
            self.anon_api_client.delete(
                self.campaign_url + self.campaign_bobs.id.__str__() + "/",
                format='json')
        )

        # test that we can NOT modify authenticated
        self.assertHttpMethodNotAllowed(
            self.bob_api_client.put(
                self.campaign_url + self.campaign_bobs.id.__str__() + "/",
                format='json',
                data={})
        )

        # test that we can NOT delete authenticated
        self.assertHttpMethodNotAllowed(
            self.bob_api_client.delete(
                self.campaign_url + self.campaign_bobs.id.__str__() + "/",
                format='json'))

    #test can get a list of campaigns authorised
    def test_campaigns_operations_as_authorised_users(self):
        # create a campaign that only bill can see
        bills_campaign = mommy.make_one('catamidb.Campaign')
        assign('view_campaign', self.user_bill, bills_campaign)

        # check that bill can see via the API
        response = self.bill_api_client.get(self.campaign_url, format='json')
        self.assertValidJSONResponse(response)
        self.assertEqual(len(self.deserialize(response)['objects']), 3)

        # check that bill can get to the object itself
        response = self.bill_api_client.get(self.campaign_url + bills_campaign.id.__str__() +"/",
                                            format='json')
        self.assertValidJSONResponse(response)

        # check that bob can not see - now we know tastypie API has correct
        # permission validation
        response = self.bob_api_client.get(self.campaign_url, format='json')
        self.assertValidJSONResponse(response)
        self.assertEqual(len(self.deserialize(response)['objects']), 2)

        # check bob can NOT get to the hidden object
        response = self.bob_api_client.get(self.campaign_url + bills_campaign.id.__str__() +"/",
                                           format='json')
        self.assertHttpUnauthorized(response)

        #check that anonymous can see public ones as well
        response = self.anon_api_client.get(self.campaign_url, format='json')
        self.assertValidJSONResponse(response)
        self.assertEqual(len(self.deserialize(response)['objects']), 2)

        #check anonymous can NOT get to the hidden object
        response = self.anon_api_client.get(self.campaign_url + bills_campaign.id.__str__() +"/",
                                            format='json')
        self.assertHttpUnauthorized(response)

        #create via the API
        auth_post_data = {
            'short_name': 'AuthBlah',
            'description': 'AuthBlah',
            'associated_researchers': 'AuthBlah',
            'associated_publications': 'AuthBlah',
            'associated_research_grant': 'AuthBlah',
            'date_start': '2012-05-01',
            'date_end': '2012-05-01',
            'contact_person': 'AuthBlah',
        }

        # test that we can create authenticated
        self.assertHttpCreated(
            self.bob_api_client.post(self.campaign_url,
                                     format='json',
                                     data=auth_post_data)
        )

        #check that ones we created via API are there
        response = self.bill_api_client.get(self.campaign_url, format='json')
        self.assertValidJSONResponse(response)
        self.assertEqual(len(self.deserialize(response)['objects']), 4)

        #check public can see it too
        response = self.anon_api_client.get(self.campaign_url, format='json')
        self.assertValidJSONResponse(response)
        self.assertEqual(len(self.deserialize(response)['objects']), 3)


class TestDeploymentResource(ResourceTestCase):
    def setUp(self):
        #Tastypie stuff
        super(TestDeploymentResource, self).setUp()

        self.bob_api_client = TestApiClient()
        self.bill_api_client = TestApiClient()
        self.anon_api_client = TestApiClient()

        # Create a user bob.
        self.user_bob_username = 'bob'
        self.user_bob_password = 'bob'
        self.user_bob = User.objects.create_user(self.user_bob_username,
                                                 'daniel@example.com',
                                                 self.user_bob_password)

        # Create a user bob.
        self.user_bill_username = 'bill'
        self.user_bill_password = 'bill'
        self.user_bill = User.objects.create_user(self.user_bill_username,
                                                  'daniel@example.com',
                                                  self.user_bill_password)

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

        #make a deployments
        self.deployment_bobs = mommy.make_recipe('catamidb.Deployment1',
                                                 id=1,
                                                 campaign=self.campaign_bobs)
        self.deployment_bills = mommy.make_recipe('catamidb.Deployment2',
                                                  id=2,
                                                  campaign=self.campaign_bills)

        #assign this one to bob
        authorization.apply_campaign_permissions(
            self.user_bob, self.campaign_bobs)

        #assign this one to bill
        authorization.apply_campaign_permissions(self.user_bill,
                                                 self.campaign_bills)

        #the API url for deployments
        self.deployment_url = '/api/dev/deployment/'

        #some post data for testing deployment creation
        self.post_data = {
            'type': 'AUV',
            'operator': 'XXX',
        }


    # can only do GET at this stage
    def test_deployment_operations_disabled(self):
        # test that we can NOT create

        self.assertHttpUnauthorized(
            self.anon_api_client.post(self.deployment_url,
                                      format='json',
                                      data=self.post_data))

        # test that we can NOT modify
        self.assertHttpMethodNotAllowed(
            self.anon_api_client.put(
                self.deployment_url + self.deployment_bobs.id.__str__() + "/",
                format='json',
                data={}
            )
        )

        # test that we can NOT delete
        self.assertHttpMethodNotAllowed(
            self.anon_api_client.delete(
                self.deployment_url + self.deployment_bobs.id.__str__() + "/",
                format='json'
            )
        )

        # test that we can NOT modify authenticated
        self.assertHttpMethodNotAllowed(
            self.bob_api_client.put(
                self.deployment_url + self.deployment_bobs.id.__str__() + "/",
                format='json',
                data={}
            )
        )

        # test that we can NOT delete authenticated
        self.assertHttpMethodNotAllowed(
            self.bob_api_client.delete(
                self.deployment_url + self.deployment_bobs.id.__str__() + "/",
                format='json'
            )
        )

    def test_deployments_operations_as_authorised_users(self):
        # create a campaign & deployment that ONLY bill can see
        bills_campaign = mommy.make_one('catamidb.Campaign', id=3, short_name='cp_3')
        bills_deployment = mommy.make_recipe('catamidb.Deployment3', id=3,
                                             campaign=bills_campaign)
        assign('view_campaign', self.user_bill, bills_campaign)

        # check that bill can see via the API
        response = self.bill_api_client.get(self.deployment_url, format='json')
        self.assertValidJSONResponse(response)
        self.assertEqual(len(self.deserialize(response)['objects']), 3)

        # check that bill can get to the object itself
        response = self.bill_api_client.get(self.deployment_url + "3/",
                                            format='json')
        self.assertValidJSONResponse(response)

        # check that bob can not see - now we know tastypie API has correct
        # permission validation
        response = self.bob_api_client.get(self.deployment_url, format='json')
        self.assertValidJSONResponse(response)
        self.assertEqual(len(self.deserialize(response)['objects']), 2)

        # check bob can NOT get to the hidden object
        response = self.bob_api_client.get(self.deployment_url + "3/",
                                           format='json')
        self.assertHttpUnauthorized(response)

        #check that anonymous can see public ones as well
        response = self.anon_api_client.get(self.deployment_url, format='json')
        self.assertValidJSONResponse(response)
        self.assertEqual(len(self.deserialize(response)['objects']), 2)

        #check anonymous can NOT get to the hidden object
        response = self.anon_api_client.get(self.deployment_url + "3/",
                                            format='json')
        self.assertHttpUnauthorized(response)


class TestImageResource(ResourceTestCase):
    def setUp(self):
        #Tastypie stuff
        super(TestImageResource, self).setUp()

        self.bob_api_client = TestApiClient()
        self.bill_api_client = TestApiClient()
        self.anon_api_client = TestApiClient()

        # Create a user bob.
        self.user_bob_username = 'bob'
        self.user_bob_password = 'bob'
        self.user_bob = User.objects.create_user(self.user_bob_username,
                                                 'daniel@example.com',
                                                 self.user_bob_password)

        # Create a user bob.
        self.user_bill_username = 'bill'
        self.user_bill_password = 'bill'
        self.user_bill = User.objects.create_user(self.user_bill_username,
                                                  'daniel@example.com',
                                                  self.user_bill_password)

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

        #make a deployments
        self.deployment_bobs = mommy.make_recipe('catamidb.Deployment1',
                                                 id=1,
                                                 campaign=self.campaign_bobs)
        self.deployment_bills = mommy.make_recipe('catamidb.Deployment2',
                                                  id=2,
                                                  campaign=self.campaign_bills) 

        #make images
        self.image_bobs = mommy.make_recipe(
            'catamidb.Image1',
            id=1,             
            deployment=self.deployment_bobs)

        self.image_bills = mommy.make_recipe(
            'catamidb.Image2',
            id=2,            
            deployment=self.deployment_bills)

        #assign this one to bob
        authorization.apply_campaign_permissions(
            self.user_bob, self.campaign_bobs)

        #assign this one to bill
        authorization.apply_campaign_permissions(
            self.user_bill, self.campaign_bills)

        #the API url for Image
        self.image_url = '/api/dev/image/'

        #some post data for testing image creation
        self.post_data = {
            'date_time': '2012-05-01',
            'depth': '1.0',
        }

    # can only do GET at this stage
    def test_image_operations_disabled(self):
        # test that anonymous are unauthorized to create
        self.assertHttpUnauthorized(
            self.anon_api_client.post(self.image_url,
                                      format='json',
                                      data=self.post_data))

        # test that we can NOT modify
        self.assertHttpMethodNotAllowed(
            self.anon_api_client.put(
                self.image_url + self.deployment_bobs.id.__str__() + "/",
                format='json',
                data={}
            )
        )

        # test that we can NOT delete
        self.assertHttpMethodNotAllowed(
            self.anon_api_client.delete(
                self.image_url + self.deployment_bobs.id.__str__() + "/",
                format='json')
        )

        # test that we can NOT modify authenticated
        self.assertHttpMethodNotAllowed(
            self.bob_api_client.put(
                self.image_url + self.deployment_bobs.id.__str__() + "/",
                format='json',
                data={}
            )
        )

        # test that we can NOT delete authenticated
        self.assertHttpMethodNotAllowed(
            self.bob_api_client.delete(
                self.image_url + self.deployment_bobs.id.__str__() + "/",
                format='json'
            )
        )

    def test_image_operations_as_authorised_users(self):
        # create a campaign & deployment that ONLY bill can see
        bills_campaign = mommy.make_one('catamidb.Campaign', id=3, short_name='cp__1')
        bills_deployment = mommy.make_recipe('catamidb.Deployment3', id=3,
                                             campaign=bills_campaign)
        bills_image = mommy.make_recipe('catamidb.Image3',
                                        id=3,                                        
                                        deployment=bills_deployment)
        assign('view_campaign', self.user_bill, bills_campaign)

        # check that bill can see via the API
        response = self.bill_api_client.get(self.image_url, format='json')
        self.assertValidJSONResponse(response)
        self.assertEqual(len(self.deserialize(response)['objects']), 3)

        # check that bill can get to the object itself
        response = self.bill_api_client.get(self.image_url + "3/",
                                            format='json')
        self.assertValidJSONResponse(response)

        # check that bob can not see - now we know tastypie API has correct
        # permission validation
        response = self.bob_api_client.get(self.image_url, format='json')
        self.assertValidJSONResponse(response)
        self.assertEqual(len(self.deserialize(response)['objects']), 2)

        # check bob can NOT get to the hidden object
        response = self.bob_api_client.get(self.image_url + "3/",
                                           format='json')
        self.assertHttpUnauthorized(response)

        #check that anonymous can see public ones as well
        response = self.anon_api_client.get(self.image_url, format='json')
        self.assertValidJSONResponse(response)
        self.assertEqual(len(self.deserialize(response)['objects']), 2)

        #check anonymous can NOT get to the hidden object
        response = self.anon_api_client.get(self.image_url + "3/",
                                            format='json')
        self.assertHttpUnauthorized(response)


class TestCameraResource(ResourceTestCase):
    def setUp(self):
        #Tastypie stuff
        super(TestCameraResource, self).setUp()

        self.bob_api_client = TestApiClient()
        self.bill_api_client = TestApiClient()
        self.anon_api_client = TestApiClient()

        # Create a user bob.
        self.user_bob_username = 'bob'
        self.user_bob_password = 'bob'
        self.user_bob = User.objects.create_user(self.user_bob_username,
                                                 'daniel@example.com',
                                                 self.user_bob_password)

        # Create a user bob.
        self.user_bill_username = 'bill'
        self.user_bill_password = 'bill'
        self.user_bill = User.objects.create_user(self.user_bill_username,
                                                  'daniel@example.com',
                                                  self.user_bill_password)

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

        #make a deployments
        self.deployment_bobs = mommy.make_recipe('catamidb.Deployment1',
                                                 id=1,
                                                 campaign=self.campaign_bobs)
        self.deployment_bills = mommy.make_recipe('catamidb.Deployment2',
                                                  id=2,
                                                  campaign=self.campaign_bills)

        #make images
        self.image_bobs = mommy.make_recipe(
            'catamidb.Image1',
            id=1, 
            deployment=self.deployment_bobs)

        self.image_bills = mommy.make_recipe(
            'catamidb.Image2',
            id=2,
            deployment=self.deployment_bills)

        #make cameras
        self.camera_bobs = mommy.make_one(
            'catamidb.Camera',
            id=1,
            image=self.image_bobs)
        self.camera_bills = mommy.make_one(
            'catamidb.Camera',
            id=2,
            image=self.image_bills)

        #assign this one to bob
        authorization.apply_campaign_permissions(
            self.user_bob, self.campaign_bobs)

        #assign this one to bill
        authorization.apply_campaign_permissions(
            self.user_bill, self.campaign_bills)

        #the API url for deployments
        self.camera_url = '/api/dev/camera/'

        #some post data for testing camera creation
        self.post_data = []

    # can only do GET at this stage
    def test_camera_operations_disabled(self):
        # test that we can NOT create

        self.assertHttpUnauthorized(
            self.anon_api_client.post(self.camera_url,
                                      format='json',
                                      data=self.post_data))

        # test that we can NOT modify
        self.assertHttpMethodNotAllowed(
            self.anon_api_client.put(
                self.camera_url + self.deployment_bobs.id.__str__() + "/",
                format='json',
                data={}
            )
        )

        # test that we can NOT delete
        self.assertHttpMethodNotAllowed(
            self.anon_api_client.delete(
                self.camera_url + self.deployment_bobs.id.__str__() + "/",
                format='json'
            )
        )

        # test that we can NOT modify authenticated
        self.assertHttpMethodNotAllowed(
            self.bob_api_client.put(
                self.camera_url + self.deployment_bobs.id.__str__() + "/",
                format='json',
                data={}
            )
        )

        # test that we can NOT delete authenticated
        self.assertHttpMethodNotAllowed(
            self.bob_api_client.delete(
                self.camera_url + self.deployment_bobs.id.__str__() + "/",
                format='json'
            )
        )

    def test_camera_operations_as_authorised_users(self):
        # create a campaign & deployment that ONLY bill can see
        bills_campaign = mommy.make_one('catamidb.Campaign', id=3, short_name='cp_3')
        bills_deployment = mommy.make_recipe('catamidb.Deployment3', id=3,
                                             campaign=bills_campaign)
        assign('view_campaign', self.user_bill, bills_campaign)

        #make exclusive image for bill and assign this image to camera to image
        self.image_bill_exc = mommy.make_recipe(
            'catamidb.Image3',
            id=3,             
            deployment=bills_deployment) #IMPORTANT camera checks campaign which has reference to deployment. Image has reference to deployment and camera

        #make exclusive camera for bill
        self.camera_bill_exc = mommy.make_one(
            'catamidb.Camera',
            id=3,
            image=self.image_bill_exc)

        # check that bill can see via the API
        response = self.bill_api_client.get(self.camera_url, format='json')
        self.assertValidJSONResponse(response)
        self.assertEqual(len(self.deserialize(response)['objects']), 3)

        # check that bill can get to the object itself
        response = self.bill_api_client.get(self.camera_url + "3/",
                                            format='json')
        self.assertValidJSONResponse(response)

        # check that bob can not see - now we know tastypie API has correct
        # permission validation
        response = self.bob_api_client.get(self.camera_url, format='json')       
        self.assertValidJSONResponse(response)
        self.assertEqual(len(self.deserialize(response)['objects']), 2)

        # check bob can NOT get to the hidden object
        response = self.bob_api_client.get(self.camera_url + "3/",
                                           format='json')
        self.assertHttpUnauthorized(response)

        #check that anonymous can see public ones as well
        response = self.anon_api_client.get(self.camera_url, format='json')
        self.assertValidJSONResponse(response)
        self.assertEqual(len(self.deserialize(response)['objects']), 2)

        #check anonymous can NOT get to the hidden object
        response = self.anon_api_client.get(self.camera_url + "3/",
                                            format='json')
        self.assertHttpUnauthorized(response)


class TestMeasurementsResource(ResourceTestCase):
    def setUp(self):
        #Tastypie stuff
        super(TestMeasurementsResource, self).setUp()

        self.bob_api_client = TestApiClient()
        self.bill_api_client = TestApiClient()
        self.anon_api_client = TestApiClient()

        # Create a user bob.
        self.user_bob_username = 'bob'
        self.user_bob_password = 'bob'
        self.user_bob = User.objects.create_user(self.user_bob_username,
                                                 'daniel@example.com',
                                                 self.user_bob_password)

        # Create a user bob.
        self.user_bill_username = 'bill'
        self.user_bill_password = 'bill'
        self.user_bill = User.objects.create_user(self.user_bill_username,
                                                  'daniel@example.com',
                                                  self.user_bill_password)

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

        #make a deployments
        self.deployment_bobs = mommy.make_recipe('catamidb.Deployment1',
                                                 id=1,
                                                 campaign=self.campaign_bobs)
        self.deployment_bills = mommy.make_recipe('catamidb.Deployment2',
                                                  id=2,
                                                  campaign=self.campaign_bills)
        #make images
        self.image_bobs = mommy.make_recipe(
            'catamidb.Image1',
            id=1, 
            deployment=self.deployment_bobs)

        self.image_bills = mommy.make_recipe(
            'catamidb.Image2',
            id=2,
            deployment=self.deployment_bills)

        #make measurements
        self.measurements_bobs = mommy.make_one(
            'catamidb.Measurements',
            id=1,
            image=self.image_bobs)
        self.measurements_bills = mommy.make_one(
            'catamidb.Measurements',
            id=2,
            image=self.image_bills)

        #assign this one to bob
        authorization.apply_campaign_permissions(
            self.user_bob, self.campaign_bobs)

        #assign this one to bill
        authorization.apply_campaign_permissions(
            self.user_bill, self.campaign_bills)

        #the API url for Measurements
        self.image_measurement_url = '/api/dev/measurements/'

        self.post_data = {
            'altitude': '13',
            'pitch': '1',
            'roll': '5',
            'salinity': '20',
            'temperature': '22',
            'yaw': '1'
        }

    # can only do GET at this stage
    def test_measurement_operations_disabled(self):
        # test that we can NOT modify
        self.assertHttpMethodNotAllowed(
            self.anon_api_client.put(
                self.image_measurement_url +
                self.deployment_bobs.id.__str__() + "/",
                format='json',
                data={}
            )
        )

        # test that we can NOT delete
        self.assertHttpMethodNotAllowed(
            self.anon_api_client.delete(
                self.image_measurement_url +
                self.deployment_bobs.id.__str__() + "/",
                format='json'
            )
        )

        # test that we can NOT modify authenticated
        self.assertHttpMethodNotAllowed(
            self.bob_api_client.put(
                self.image_measurement_url +
                self.deployment_bobs.id.__str__() + "/",
                format='json',
                data={}
            )
        )

        # test that we can NOT delete authenticated
        self.assertHttpMethodNotAllowed(
            self.bob_api_client.delete(
                self.image_measurement_url +
                self.deployment_bobs.id.__str__() + "/",
                format='json'
            )
        )

    def test_measurement_operations_as_authorised_users(self):
        # create a campaign & deployment that ONLY bill can see
        bills_campaign = mommy.make_one('catamidb.Campaign', id=3, short_name='cp__3')
        bills_deployment = mommy.make_recipe('catamidb.Deployment1', id=3,
                                             campaign=bills_campaign, short_name='dp__3')
        bills_image = mommy.make_recipe('catamidb.Image3',
                                        id=3,                                        
                                        deployment=bills_deployment)
        bills_measurements = mommy.make_one('catamidb.Measurements', 
                                            id=3,
                                            image=bills_image)

        assign('view_campaign', self.user_bill, bills_campaign)

        # check that bill can see via the API
        response = self.bill_api_client.get(self.image_measurement_url,
                                            format='json')
        self.assertValidJSONResponse(response)
        self.assertEqual(len(self.deserialize(response)['objects']), 3)

        # check that bill can get to the object itself
        response = self.bill_api_client.get(self.image_measurement_url + "3/",
                                            format='json')
        self.assertValidJSONResponse(response)

        # check that bob can not see - now we know tastypie API has correct
        # permission validation
        response = self.bob_api_client.get(self.image_measurement_url,
                                           format='json')

        self.assertValidJSONResponse(response)
        self.assertEqual(len(self.deserialize(response)['objects']), 2)

        # check bob can NOT get to the hidden object
        response = self.bob_api_client.get(self.image_measurement_url + "3/",
                                           format='json')
        self.assertHttpUnauthorized(response)

        #check that anonymous can see public ones as well
        response = self.anon_api_client.get(self.image_measurement_url,
                                            format='json')
        self.assertValidJSONResponse(response)
        self.assertEqual(len(self.deserialize(response)['objects']), 2)

        #check anonymous can NOT get to the hidden object
        response = self.anon_api_client.get(self.image_measurement_url + "3/",
                                            format='json')
        self.assertHttpUnauthorized(response)


if __name__ == '__main__':
    unittest.main()
