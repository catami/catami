from django.contrib.auth.models import User, Group
import guardian
from guardian.core import ObjectPermissionChecker
from guardian.shortcuts import assign_perm
from model_mommy import mommy
from tastypie.test import ResourceTestCase, TestApiClient
from datetime import datetime
from projects.models import Project, GenericAnnotationSet, GenericPointAnnotation, AnnotationCodes
from django.contrib.gis.geos import Point, Polygon
from projects import authorization
from catamidb import authorization as catamidbauthorization
import logging
import socket

#logger = logging.getLogger(__name__)
logging.disable(logging.DEBUG)


#======================================#
# Test the API                         #
#======================================#
def create_setup(self):
    self.campaign_one = mommy.make_one('catamidb.Campaign')

    self.deployment_one = mommy.make_one(
        'catamidb.GenericDeployment',
        start_position=Point(12.4604, 43.9420),
        end_position=Point(12.4604,43.9420),
        transect_shape=Polygon(((0.0, 0.0), (0.0, 50.0), (50.0, 50.0), (50.0, 0.0), (0.0, 0.0))),
        campaign=self.campaign_one)

    self.deployment_two = mommy.make_one(
        'catamidb.GenericDeployment',
        start_position=Point(12.4604, 43.9420),
        end_position=Point(12.4604, 43.9420),
        transect_shape=Polygon(((0.0, 0.0), (0.0, 50.0), (50.0, 50.0), (50.0, 0.0), (0.0, 0.0))),
        campaign=self.campaign_one)

    #self.image_list = ['/live/test/test2.jpg', '/live/test/test1.jpg']
    self.mock_image_one = mommy.make_recipe('projects.genericImage1', deployment=self.deployment_one)
    self.mock_image_two = mommy.make_recipe('projects.genericImage2', deployment=self.deployment_two)

    self.camera_one = mommy.make_one('catamidb.GenericCamera', image=self.mock_image_one)
    self.camera_two = mommy.make_one('catamidb.GenericCamera', image=self.mock_image_two)

    self.mock_image_list = []

    for i in xrange(20):
        mock_image = mommy.make_recipe('projects.genericImage1', deployment=self.deployment_one, date_time=datetime.now())
        self.mock_image_list.append(mock_image)


class TestProjectResource(ResourceTestCase):

    def setUp(self):
        #Tastypie stuff
        super(TestProjectResource, self).setUp()

        create_setup(self)

        self.bob_api_client = TestApiClient()
        self.bill_api_client = TestApiClient()
        self.anon_api_client = TestApiClient()

        # Create a user bob.
        self.user_bob_username = 'bob'
        self.user_bob_password = 'bob'
        self.user_bob = User.objects.create_user(self.user_bob_username,
                                                 'bob@example.com',
                                                 self.user_bob_password)

        # Create a user bob.
        self.user_bill_username = 'bill'
        self.user_bill_password = 'bill'
        self.user_bill = User.objects.create_user(self.user_bill_username,
                                                  'bill@example.com',
                                                  self.user_bill_password)

        self.bob_api_client.client.login(username='bob', password='bob')
        self.bill_api_client.client.login(username='bill', password='bill')

        #need these permissions for bill and bob to attach images to projects
        catamidbauthorization.apply_campaign_permissions(self.user_bob, self.campaign_one)
        catamidbauthorization.apply_campaign_permissions(self.user_bill, self.campaign_one)

        #assign users to the Public group
        public_group, created = Group.objects.get_or_create(name='Public')
        self.user_bob.groups.add(public_group)
        self.user_bill.groups.add(public_group)
        guardian.utils.get_anonymous_user().groups.add(public_group)

        #make a couple of projects and save
        #self.project_bobs = mommy.make_recipe('project.project1', id=1, owner=self.user_bob)
        #self.project_bills = mommy.make_recipe('project.project2', id=2, owner=self.user_bill)
        self.project_bobs = mommy.make_one(Project,
                                           name="one",
                                           owner=self.user_bob,
                                           creation_date=datetime.now(),
                                           modified_date=datetime.now(),
                                           generic_images=[self.mock_image_one, self.mock_image_two])

        self.project_bills = mommy.make_one(Project,
                                            name="two",
                                            owner=self.user_bill,
                                            creation_date=datetime.now(),
                                            modified_date=datetime.now(),
                                            generic_images=[self.mock_image_one, self.mock_image_two])

        #assign this one to bob
        authorization.apply_project_permissions(
            self.user_bob, self.project_bobs)

        #assign this one to bill
        authorization.apply_project_permissions(
            self.user_bill, self.project_bills)

        #the API url for campaigns
        self.project_url = '/api/dev/project/'

    def test_project_operations_disabled(self):

        # test that we can not Create Update Delete as anonymous
        self.assertHttpUnauthorized(
            self.anon_api_client.post(
                self.project_url,
                format='json',
                data={})
        )

        self.assertHttpUnauthorized(
            self.anon_api_client.put(
                self.project_url + self.project_bobs.id.__str__() + "/",
                format='json',
                data={})
        )

        self.assertHttpUnauthorized(
            self.anon_api_client.delete(
                self.project_url + self.project_bobs.id.__str__() + "/",
                format='json')
        )

    #test can get a list of campaigns authorised
    def test_projects_operations_as_authorised_users(self):
        # create a campaign that only bill can see
        bills_project = mommy.make_one(Project,
                                        name="three",
                                        owner=self.user_bill,
                                        creation_date=datetime.now(),
                                        modified_date=datetime.now(),
                                        generic_images=[self.mock_image_one, self.mock_image_two])

        assign_perm('view_project', self.user_bill, bills_project)

        # check that bill can see via the API
        response = self.bill_api_client.get(self.project_url, format='json')
        self.assertValidJSONResponse(response)
        self.assertEqual(len(self.deserialize(response)['objects']), 3)

        # check that bill can get to the object itself
        response = self.bill_api_client.get(self.project_url + bills_project.id.__str__() + "/",
                                            format='json')
        self.assertValidJSONResponse(response)

        # check that bob can not see - now we know tastypie API has correct
        # permission validation
        response = self.bob_api_client.get(self.project_url, format='json')
        self.assertValidJSONResponse(response)
        self.assertEqual(len(self.deserialize(response)['objects']), 2)

        # check bob can NOT get to the hidden object
        response = self.bob_api_client.get(self.project_url + bills_project.id.__str__() + "/",
                                           format='json')
        self.assertHttpUnauthorized(response)

        #check that anonymous can see public ones as well
        response = self.anon_api_client.get(self.project_url, format='json')
        self.assertValidJSONResponse(response)
        self.assertEqual(len(self.deserialize(response)['objects']), 2)

        #check anonymous can NOT get to the hidden object
        response = self.anon_api_client.get(self.project_url + bills_project.id.__str__() + "/",
                                            format='json')
        self.assertHttpUnauthorized(response)

        #check bill can POST
        #some post data for testing project creation
        self.bill_post_data = {'name': 'myName',
                               'description': 'my description',
                               'generic_images': ''
                               }

        response = self.bill_api_client.post(
                self.project_url,
                format='json',
                data=self.bill_post_data)

        self.assertHttpCreated(response)

        # check that bill can see via the API
        response = self.bill_api_client.get(self.project_url, format='json')
        self.assertValidJSONResponse(response)
        self.assertEqual(len(self.deserialize(response)['objects']), 4)

        # check that bill can get to the object itself
        response = self.bill_api_client.get(self.project_url + "?name=myName&owner=" + self.user_bill.id.__str__(),
                                            format='json')
        self.assertValidJSONResponse(response)

        new_project_id = self.deserialize(response)['objects'][0]['id'].__str__()

        #check we can modify it - add images
        self.bill_put_data = {'generic_images' : ["/api/dev/generic_image/" + self.mock_image_one.id.__str__() + "/",
                                                  "/api/dev/generic_image/" + self.mock_image_two.id.__str__() + "/"]}
        response = self.bill_api_client.put(
                self.project_url + new_project_id + "/",
                format='json',
                data=self.bill_put_data)

        print new_project_id
        print "---------*****"
        print response.status_code

        self.assertHttpAccepted(response)

        response = self.bill_api_client.get(self.project_url + "?name=myName&owner=" + self.user_bill.id.__str__(),
                                            format='json')

        #check bill can DELETE
        response = self.bill_api_client.delete(
            self.project_url + new_project_id + "/",
            format='json')

        self.assertHttpAccepted(response)

        # check that bill can see via the API
        response = self.bill_api_client.get(self.project_url, format='json')
        self.assertValidJSONResponse(response)
        self.assertEqual(len(self.deserialize(response)['objects']), 3)


class TestGenericAnnotationSetResource(ResourceTestCase):

    def setUp(self):
        #Tastypie stuff
        super(TestGenericAnnotationSetResource, self).setUp()

        create_setup(self)

        self.bob_api_client = TestApiClient()
        self.bill_api_client = TestApiClient()
        self.anon_api_client = TestApiClient()

        # Create a user bob.
        self.user_bob_username = 'bob'
        self.user_bob_password = 'bob'
        self.user_bob = User.objects.create_user(self.user_bob_username,
                                                 'bob@example.com',
                                                 self.user_bob_password)

        # Create a user bob.
        self.user_bill_username = 'bill'
        self.user_bill_password = 'bill'
        self.user_bill = User.objects.create_user(self.user_bill_username,
                                                  'bill@example.com',
                                                  self.user_bill_password)

        self.bob_api_client.client.login(username='bob', password='bob')
        self.bill_api_client.client.login(username='bill', password='bill')

        #need these permissions for bill and bob to attach images to projects
        catamidbauthorization.apply_campaign_permissions(self.user_bob, self.campaign_one)
        catamidbauthorization.apply_campaign_permissions(self.user_bill, self.campaign_one)

        #assign users to the Public group
        public_group, created = Group.objects.get_or_create(name='Public')
        self.user_bob.groups.add(public_group)
        self.user_bill.groups.add(public_group)
        guardian.utils.get_anonymous_user().groups.add(public_group)

        #make a couple of projects and save
        #self.project_bobs = mommy.make_recipe('project.project1', id=1, owner=self.user_bob)
        #self.project_bills = mommy.make_recipe('project.project2', id=2, owner=self.user_bill)
        self.project_bobs = mommy.make_one(Project, owner=self.user_bob,
                                           creation_date=datetime.now(),
                                           modified_date=datetime.now(),
                                           generic_images=[self.mock_image_one, self.mock_image_two])

        self.project_bills = mommy.make_one(Project,
                                            owner=self.user_bill,
                                            creation_date=datetime.now(),
                                            modified_date=datetime.now(),
                                            generic_images=[self.mock_image_one, self.mock_image_two])

        #assign this one to bob
        authorization.apply_project_permissions(
            self.user_bob, self.project_bobs)

        #assign this one to bill
        authorization.apply_project_permissions(
            self.user_bill, self.project_bills)

        self.generic_annotation_set_bobs = mommy.make_one(GenericAnnotationSet,
                                            project=self.project_bobs,
                                            owner=self.user_bob,
                                            creation_date=datetime.now(),
                                            modified_date=datetime.now(),
                                            generic_images=[self.mock_image_one, self.mock_image_two],
                                            annotation_methodology=0,
                                            image_sampling_methodology=0)

        self.generic_annotation_set_bills = mommy.make_one(GenericAnnotationSet,
                                            project=self.project_bills,
                                            owner=self.user_bob,
                                            creation_date=datetime.now(),
                                            modified_date=datetime.now(),
                                            generic_images=[self.mock_image_one, self.mock_image_two],
                                            annotation_methodology=1,
                                            image_sampling_methodology=0)

        #assign this one to bob
        authorization.apply_generic_annotation_set_permissions(
            self.user_bob, self.generic_annotation_set_bobs)

        #assign this one to bill
        authorization.apply_generic_annotation_set_permissions(
            self.user_bill, self.generic_annotation_set_bills)


        #create a big project with 20 images
        self.project_bills_big = mommy.make_one(Project,
                                            owner=self.user_bill,
                                            creation_date=datetime.now(),
                                            modified_date=datetime.now(),
                                            generic_images=self.mock_image_list)
        #assign this one to bill
        authorization.apply_project_permissions(
            self.user_bill, self.project_bills_big)

        #the API url for resources
        self.generic_annotation_set_url = '/api/dev/generic_annotation_set/'
        self.generic_point_annotation_url = '/api/dev/generic_point_annotation/'

    def test_project_operations_disabled(self):

        # test that we can not Create Update Delete as anonymous
        self.assertHttpUnauthorized(
            self.anon_api_client.post(
                self.generic_annotation_set_url,
                format='json',
                data={'image_sample_size': '20'})
        )

        self.assertHttpUnauthorized(
            self.anon_api_client.put(
                self.generic_annotation_set_url + self.generic_annotation_set_bobs.id.__str__() + "/",
                format='json',
                data={})
        )

        self.assertHttpUnauthorized(
            self.anon_api_client.delete(
                self.generic_annotation_set_url + self.generic_annotation_set_bobs.id.__str__() + "/",
                format='json')
        )

    def test_annotationset_operations_as_authorised_users(self):
        # create a campaign that only bill can see
        bills_generic_annotation_set = mommy.make_one(GenericAnnotationSet,
                                            project=self.project_bills,
                                            owner=self.user_bob,
                                            creation_date=datetime.now(),
                                            modified_date=datetime.now(),
                                            generic_images=[self.mock_image_one, self.mock_image_two],
                                            annotation_methodology=2,
                                            image_sampling_methodology=0)

        assign_perm('view_genericannotationset', self.user_bill, bills_generic_annotation_set)

        # check that bill can see via the API
        response = self.bill_api_client.get(self.generic_annotation_set_url, format='json')
        self.assertValidJSONResponse(response)
        self.assertEqual(len(self.deserialize(response)['objects']), 3)

        # check that bill can get to the object itself
        response = self.bill_api_client.get(self.generic_annotation_set_url + bills_generic_annotation_set.id.__str__() + "/",
                                            format='json')
        self.assertValidJSONResponse(response)

        # check that bob can not see - now we know tastypie API has correct
        # permission validation
        response = self.bob_api_client.get(self.generic_annotation_set_url, format='json')
        self.assertValidJSONResponse(response)
        self.assertEqual(len(self.deserialize(response)['objects']), 2)

        # check bob can NOT get to the hidden object
        response = self.bob_api_client.get(self.generic_annotation_set_url + bills_generic_annotation_set.id.__str__() + "/",
                                           format='json')
        self.assertHttpUnauthorized(response)

        #check that anonymous can see public ones as well
        response = self.anon_api_client.get(self.generic_annotation_set_url, format='json')
        self.assertValidJSONResponse(response)
        self.assertEqual(len(self.deserialize(response)['objects']), 2)

        #check anonymous can NOT get to the hidden object
        response = self.anon_api_client.get(self.generic_annotation_set_url + bills_generic_annotation_set.id.__str__() + "/",
                                            format='json')
        self.assertHttpUnauthorized(response)

        #check bill can POST
        #some post data for testing project creation
        self.bill_post_data = {'project':'/api/dev/project/' + self.project_bills_big.id.__str__() + '/',
                               'name': 'myName2',
                               'description': 'my description',
                               #'owner': "/api/dev/users/" + self.user_bill.id.__str__()+"/",
                               #'creation_date': '2012-05-01',
                               #'modified_date': '2012-05-01',
                               #'generic_images': [ "/api/dev/generic_image/" + self.mock_image_one.id.__str__() + "/",
                               #                    "/api/dev/generic_image/" + self.mock_image_two.id.__str__() + "/"],
                               #'generic_images': '',
                               'annotation_methodology': '0',
                               'image_sampling_methodology': '0',
                               'image_sample_size': '10',
                               'point_sample_size': '15'
                                }

        response = self.bill_api_client.post(
                self.generic_annotation_set_url,
                format='json',
                data=self.bill_post_data)

        self.assertHttpCreated(response)

        # check that bill can see via the API
        response = self.bill_api_client.get(self.generic_annotation_set_url, format='json')
        self.assertValidJSONResponse(response)
        self.assertEqual(len(self.deserialize(response)['objects']), 4)

        # check that bill can get to the object itself
        response = self.bill_api_client.get(self.generic_annotation_set_url + "?name=myName2&owner=" + self.user_bill.id.__str__(),
                                            format='json')
        self.assertValidJSONResponse(response)

        new_annotationset_id = self.deserialize(response)['objects'][0]['id'].__str__()

        #check we can modify it - add images
        self.bill_put_data = {'description' : 'my new description'}
        response = self.bill_api_client.put(
                self.generic_annotation_set_url + new_annotationset_id + "/",
                format='json',
                data=self.bill_put_data)

        self.assertHttpAccepted(response)

        response = self.bill_api_client.get(self.generic_annotation_set_url + "?name=myName&owner=" + self.user_bill.id.__str__(),
                                            format='json')

        #check bill can DELETE
        response = self.bill_api_client.delete(
            self.generic_annotation_set_url + new_annotationset_id + "/",
            format='json')

        self.assertHttpAccepted(response)

        # check that bill can see via the API
        response = self.bill_api_client.get(self.generic_annotation_set_url, format='json')
        self.assertValidJSONResponse(response)
        self.assertEqual(len(self.deserialize(response)['objects']), 3)

    def test_annotation_set_creation_random(self):
        #some post data for testing project creation
        self.bill_post_data = {'project':'/api/dev/project/' + self.project_bills_big.id.__str__() + '/',
                               'name': 'myName',
                               'description': 'my description',
                               #'owner': "/api/dev/users/" + self.user_bill.id.__str__()+"/",
                               #'creation_date': '2012-05-01',
                               #'modified_date': '2012-05-01',
                               #'generic_images': '',
                               'annotation_methodology': '0',
                               'image_sampling_methodology': '0',
                               'image_sample_size': '10',
                               'point_sample_size': '15'
                                }

        response = self.bill_api_client.post(
                self.generic_annotation_set_url,
                format='json',
                data=self.bill_post_data)

        self.assertHttpCreated(response)

        # check that bill can get to the object itself
        response = self.bill_api_client.get(self.generic_annotation_set_url + "?name=myName&owner=" + self.user_bill.id.__str__(),
                                            format='json')

        # check that the API did indeed samle 10 images
        generic_images = self.deserialize(response)['objects'][0]['generic_images']
        self.assertEqual(len(generic_images), 10)

        # check that the API set 15 points per image
        for image in generic_images:
            response = self.bill_api_client.get(self.generic_point_annotation_url + "?image=" + image['id'].__str__(),
                                            format='json')
            self.assertEqual(len(self.deserialize(response)['objects']), 15)

    def test_annotation_set_creation_stratified(self):
        #some post data for testing project creation
        self.bill_post_data = {'project':'/api/dev/project/' + self.project_bills_big.id.__str__() + '/',
                               'name': 'myName',
                               'description': 'my description',
                               #'owner': "/api/dev/users/" + self.user_bill.id.__str__()+"/",
                               #'creation_date': '2012-05-01',
                               #'modified_date': '2012-05-01',
                               #'generic_images': '',
                               'annotation_methodology': '0',
                               'image_sampling_methodology': '1',
                               'image_sample_size': '10',
                               'point_sample_size': '5'
                                }

        response = self.bill_api_client.post(
                self.generic_annotation_set_url,
                format='json',
                data=self.bill_post_data)

        self.assertHttpCreated(response)

        # check that bill can get to the object itself
        response = self.bill_api_client.get(self.generic_annotation_set_url + "?name=myName&owner=" + self.user_bill.id.__str__(),
                                            format='json')

        # check that the API did indeed samle 10 images
        generic_images = self.deserialize(response)['objects'][0]['generic_images']
        self.assertEqual(len(generic_images), 10)

        # check that the API set 5 points per image
        for image in generic_images:
            response = self.bill_api_client.get(self.generic_point_annotation_url + "?image=" + image['id'].__str__(),
                                            format='json')
            self.assertEqual(len(self.deserialize(response)['objects']), 5)

    def test_annotation_set_creation_unimplemented(self):
        #some post data for testing project creation
        self.bill_post_data = {'project':'/api/dev/project/' + self.project_bills_big.id.__str__() + '/',
                               'name': 'myName2',
                               'description': 'my description',
                               'owner': "/api/dev/users/" + self.user_bill.id.__str__()+"/",
                               'creation_date': '2012-05-01',
                               'modified_date': '2012-05-01',
                               'generic_images': '',
                               'annotation_methodology': '4',
                               'image_sampling_methodology': '4',
                               'image_sample_size': '10',
                               'point_sample_size': '5'
                                }

        response = self.bill_api_client.post(
                self.generic_annotation_set_url,
                format='json',
                data=self.bill_post_data)

        self.assertHttpNotImplemented(response)

class TestGenericPointAnnotationResource(ResourceTestCase):

    def setUp(self):
        #Tastypie stuff
        super(TestGenericPointAnnotationResource, self).setUp()

        create_setup(self)

        self.bob_api_client = TestApiClient()
        self.bill_api_client = TestApiClient()
        self.anon_api_client = TestApiClient()

        # Create a user bob.
        self.user_bob_username = 'bob'
        self.user_bob_password = 'bob'
        self.user_bob = User.objects.create_user(self.user_bob_username,
                                                 'bob@example.com',
                                                 self.user_bob_password)

        # Create a user bob.
        self.user_bill_username = 'bill'
        self.user_bill_password = 'bill'
        self.user_bill = User.objects.create_user(self.user_bill_username,
                                                  'bill@example.com',
                                                  self.user_bill_password)

        self.bob_api_client.client.login(username='bob', password='bob')
        self.bill_api_client.client.login(username='bill', password='bill')

        #add the users to the main campaign for permission purposes
        catamidbauthorization.apply_campaign_permissions(self.user_bob, self.campaign_one)
        catamidbauthorization.apply_campaign_permissions(self.user_bill, self.campaign_one)

        #assign users to the Public group
        public_group, created = Group.objects.get_or_create(name='Public')
        self.user_bob.groups.add(public_group)
        self.user_bill.groups.add(public_group)
        guardian.utils.get_anonymous_user().groups.add(public_group)

        #make a couple of projects and save
        #self.project_bobs = mommy.make_recipe('project.project1', id=1, owner=self.user_bob)
        #self.project_bills = mommy.make_recipe('project.project2', id=2, owner=self.user_bill)
        self.project_bobs = mommy.make_one(Project, owner=self.user_bob,
                                           creation_date=datetime.now(),
                                           modified_date=datetime.now(),
                                           generic_images=[self.mock_image_one, self.mock_image_two])

        self.project_bills = mommy.make_one(Project,
                                            owner=self.user_bill,
                                            creation_date=datetime.now(),
                                            modified_date=datetime.now(),
                                            generic_images=[self.mock_image_one, self.mock_image_two])

        #assign this one to bob
        authorization.apply_project_permissions(
            self.user_bob, self.project_bobs)

        #assign this one to bill
        authorization.apply_project_permissions(
            self.user_bill, self.project_bills)

        self.generic_annotation_set_bobs = mommy.make_one(GenericAnnotationSet,
                                            project=self.project_bobs,
                                            owner=self.user_bob,
                                            creation_date=datetime.now(),
                                            modified_date=datetime.now(),
                                            generic_images=[self.mock_image_one, self.mock_image_two],
                                            annotation_methodology=0,
                                            image_sampling_methodology=0)

        self.generic_annotation_set_bills = mommy.make_one(GenericAnnotationSet,
                                            project=self.project_bills,
                                            owner=self.user_bill,
                                            creation_date=datetime.now(),
                                            modified_date=datetime.now(),
                                            generic_images=[self.mock_image_one, self.mock_image_two],
                                            annotation_methodology=1,
                                            image_sampling_methodology=0)

        #assign this one to bob
        authorization.apply_generic_annotation_set_permissions(
            self.user_bob, self.generic_annotation_set_bobs)

        #assign this one to bill
        authorization.apply_generic_annotation_set_permissions(
            self.user_bill, self.generic_annotation_set_bills)

        self.annotation_point_bobs = mommy.make_one(GenericPointAnnotation,
                                                    generic_annotation_set=self.generic_annotation_set_bobs,
                                                    image=self.mock_image_one,
                                                    owner=self.user_bob,
                                                    )

        self.annotation_point_bills = mommy.make_one(GenericPointAnnotation,
                                                    generic_annotation_set=self.generic_annotation_set_bills,
                                                    image=self.mock_image_one,
                                                    owner=self.user_bill,
                                                    )

        #the API url for annotation points
        self.point_annotation_url = '/api/dev/generic_point_annotation/'

    def test_point_annotation_operations_disabled(self):

        # test that we can not Create Update Delete as anonymous
        self.assertHttpUnauthorized(
            self.anon_api_client.post(
                self.point_annotation_url,
                format='json',
                data={})
        )

        self.assertHttpUnauthorized(
            self.anon_api_client.put(
                self.point_annotation_url + self.annotation_point_bills.id.__str__() + "/",
                format='json',
                data={})
        )

        self.assertHttpUnauthorized(
            self.anon_api_client.delete(
                self.point_annotation_url + self.annotation_point_bills.id.__str__() + "/",
                format='json')
        )

    def test_point_annotation_operations_as_authorised_users(self):
        # create a point annotation that only bill can see
        bills_private_generic_annotation_set = mommy.make_one(GenericAnnotationSet,
                                            project=self.project_bills,
                                            owner=self.user_bob,
                                            creation_date=datetime.now(),
                                            modified_date=datetime.now(),
                                            generic_images=[self.mock_image_one, self.mock_image_two],
                                            annotation_methodology=2,
                                            image_sampling_methodology=0)

        assign_perm('view_genericannotationset', self.user_bill, bills_private_generic_annotation_set)

        bills_private_point_annotation = mommy.make_one(GenericPointAnnotation,
                                            generic_annotation_set=bills_private_generic_annotation_set,
                                            image=self.mock_image_one,
                                            owner=self.user_bill,
                                            )

        #assign('view_genericannotationset', self.user_bill, bills_point_annotation)

        # check that bill can see via the API
        response = self.bill_api_client.get(self.point_annotation_url, format='json')
        self.assertValidJSONResponse(response)
        self.assertEqual(len(self.deserialize(response)['objects']), 3)

        # check that bill can get to the object itself
        response = self.bill_api_client.get(self.point_annotation_url + bills_private_point_annotation.id.__str__() + "/",
                                            format='json')
        self.assertValidJSONResponse(response)

        # check that bob can not see - now we know tastypie API has correct
        # permission validation
        response = self.bob_api_client.get(self.point_annotation_url, format='json')
        self.assertValidJSONResponse(response)
        self.assertEqual(len(self.deserialize(response)['objects']), 2)

        # check bob can NOT get to the hidden object
        response = self.bob_api_client.get(self.point_annotation_url + bills_private_point_annotation.id.__str__() + "/",
                                           format='json')
        self.assertHttpUnauthorized(response)

        #check that anonymous can see public ones as well
        response = self.anon_api_client.get(self.point_annotation_url, format='json')
        self.assertValidJSONResponse(response)
        self.assertEqual(len(self.deserialize(response)['objects']), 2)

        #check anonymous can NOT get to the hidden object
        response = self.anon_api_client.get(self.point_annotation_url + bills_private_point_annotation.id.__str__() + "/",
                                            format='json')
        self.assertHttpUnauthorized(response)

        #check bill can POST
        #some post data for testing project creation
        self.bill_post_data = {'generic_annotation_set':'/api/dev/generic_annotation_set/' + self.generic_annotation_set_bills.id.__str__() + '/',
                               #'generic_annotation_set': self.generic_annotation_set_bills.id.__str__(),
                               'annotation_caab_code': 'caab1',
                               'qualifier_short_name': 'qualifier1',
                               'owner': "/api/dev/users/" + self.user_bill.id.__str__()+"/",
                               'image': "/api/dev/generic_image/" + self.mock_image_one.id.__str__() +"/",
                               'x': '5',
                               'y': '15'
                                }

        response = self.bill_api_client.post(
                self.point_annotation_url,
                format='json',
                data=self.bill_post_data)

        self.assertHttpCreated(response)

        # check that bill can see via the API
        response = self.bill_api_client.get(self.point_annotation_url, format='json')
        self.assertValidJSONResponse(response)
        self.assertEqual(len(self.deserialize(response)['objects']), 4)

        # check that bill can get to the object itself
        response = self.bill_api_client.get(self.point_annotation_url + "?annotation_caab_code=caab1",
                                            format='json')
        self.assertValidJSONResponse(response)

        new_pointannotation_id = self.deserialize(response)['objects'][0]['id'].__str__()

        #check we can modify it - add images
        self.bill_put_data = {'annotation_caab_code' : 'caab2'}
        response = self.bill_api_client.put(
                self.point_annotation_url + new_pointannotation_id + "/",
                format='json',
                data=self.bill_put_data)

        self.assertHttpAccepted(response)

        response = self.bill_api_client.get(self.point_annotation_url + "?image=" + self.mock_image_one.id.__str__(),
                                            format='json')

        #check bill can DELETE
        response = self.bill_api_client.delete(
            self.point_annotation_url + new_pointannotation_id + "/",
            format='json')

        self.assertHttpAccepted(response)

        # check that bill can see via the API
        response = self.bill_api_client.get(self.point_annotation_url, format='json')
        self.assertValidJSONResponse(response)
        self.assertEqual(len(self.deserialize(response)['objects']), 3)


class TestAnnotationCodesResource(ResourceTestCase):

    def setUp(self):
        #Tastypie stuff
        super(TestAnnotationCodesResource, self).setUp()

        #make some codes
        self.codes = mommy.make_many(AnnotationCodes, 10)

        self.bob_api_client = TestApiClient()
        self.anon_api_client = TestApiClient()

        # Create a user bob.
        self.user_bob_username = 'bob'
        self.user_bob_password = 'bob'
        self.user_bob = User.objects.create_user(self.user_bob_username,
                                                 'bob@example.com',
                                                 self.user_bob_password)

        self.bob_api_client.client.login(username='bob', password='bob')

        #end point for the API
        self.annotation_code_url = '/api/dev/annotation_code/'

    def test_get_codes_anon(self):

        #check annon can get all the codes
        response = self.anon_api_client.get(self.annotation_code_url, format='json')
        self.assertValidJSONResponse(response)
        self.assertEqual(len(self.deserialize(response)['objects']), len(self.codes))

        #check annon can get the real code value
        for code in self.codes:
            response = self.anon_api_client.get(self.annotation_code_url + code.id.__str__() +"/", format='json')
            self.assertValidJSONResponse(response)
            code_from_request = self.deserialize(response)['caab_code'].__str__()
            self.assertEqual(code.caab_code.__str__(), code_from_request)

        #check bob can get all the codes
        response = self.bob_api_client.get(self.annotation_code_url, format='json')
        self.assertValidJSONResponse(response)
        self.assertEqual(len(self.deserialize(response)['objects']), len(self.codes))

        #check bob can get the real code value
        for code in self.codes:
            response = self.bob_api_client.get(self.annotation_code_url + code.id.__str__() +"/", format='json')
            self.assertValidJSONResponse(response)
            code_from_request = self.deserialize(response)['caab_code'].__str__()
            self.assertEqual(code.caab_code.__str__(), code_from_request)




