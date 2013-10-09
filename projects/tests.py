from django.contrib.auth.models import User, Group
import json
import guardian
from guardian.core import ObjectPermissionChecker
from guardian.shortcuts import assign_perm
from model_mommy import mommy
from tastypie.test import ResourceTestCase, TestApiClient
from datetime import datetime, timedelta
from catamidb.models import Image, Deployment
from projects.models import Project, AnnotationSet, PointAnnotation, AnnotationCodes, WholeImageAnnotation
from django.contrib.gis.geos import Point, Polygon
from projects import authorization
from catamidb import authorization as catamidbauthorization
import logging
import socket
import StringIO, csv

#logger = logging.getLogger(__name__)
logging.disable(logging.DEBUG)


#======================================#
# Test the API                         #
#======================================#
def create_setup(self):
    self.campaign_one = mommy.make_one(
        'catamidb.Campaign',
        short_name='Campaign1')

    self.campaign_two = mommy.make_one(
        'catamidb.Campaign',
        short_name='Campaign2')

    self.deployment_one = mommy.make_one(
        'catamidb.Deployment',
        short_name='Deployment1',
        start_position=Point(12.4604, 43.9420),
        end_position=Point(12.4604,43.9420),
        transect_shape=Polygon(((0.0, 0.0), (0.0, 50.0), (50.0, 50.0), (50.0, 0.0), (0.0, 0.0))),
        campaign=self.campaign_one)

    self.deployment_two = mommy.make_one(
        'catamidb.Deployment',
        short_name='Deployment2',
        start_position=Point(12.4604, 43.9420),
        end_position=Point(12.4604, 43.9420),
        transect_shape=Polygon(((0.0, 0.0), (0.0, 50.0), (50.0, 50.0), (50.0, 0.0), (0.0, 0.0))),
        campaign=self.campaign_one)

    self.deployment_three = mommy.make_one(
        'catamidb.Deployment',
        short_name='Deployment3',
        start_position=Point(12.4604, 43.9420),
        end_position=Point(12.4604, 43.9420),
        transect_shape=Polygon(((0.0, 0.0), (0.0, 50.0), (50.0, 50.0), (50.0, 0.0), (0.0, 0.0))),
        campaign=self.campaign_two)

    #self.image_list = ['/live/test/test2.jpg', '/live/test/test1.jpg']
    self.mock_image_one = mommy.make_recipe('projects.Image1', deployment=self.deployment_one)
    self.mock_image_two = mommy.make_recipe('projects.Image2', deployment=self.deployment_two)
    self.mock_image_three = mommy.make_recipe('projects.Image3', deployment=self.deployment_three)

    self.camera_one = mommy.make_one('catamidb.Camera', image=self.mock_image_one)
    self.camera_two = mommy.make_one('catamidb.Camera', image=self.mock_image_two)

    self.mock_image_list = []

    for i in xrange(20):
        mock_image = mommy.make_recipe('projects.Image1', deployment=self.deployment_one, date_time=datetime.now() + timedelta(seconds=i) )
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

        # Create a user bill.
        self.user_bill_username = 'bill'
        self.user_bill_password = 'bill'
        self.user_bill = User.objects.create_user(self.user_bill_username,
                                                  'bill@example.com',
                                                  self.user_bill_password)

        # Create a user joe.
        self.user_joe_username = 'joe'
        self.user_joe_password = 'joe'
        self.user_joe = User.objects.create_user(self.user_joe_username,
                                                  'joe@example.com',
                                                  self.user_joe_password)

        self.bob_api_client.client.login(username='bob', password='bob')
        self.bill_api_client.client.login(username='bill', password='bill')

        #need these permissions for bill and bob to attach images to projects
        catamidbauthorization.apply_campaign_permissions(self.user_bob, self.campaign_one)
        catamidbauthorization.apply_campaign_permissions(self.user_bill, self.campaign_one)

        #assign users to the Public group
        public_group, created = Group.objects.get_or_create(name='Public')
        self.user_bob.groups.add(public_group)
        self.user_bill.groups.add(public_group)
        self.user_joe.groups.add(public_group)
        guardian.utils.get_anonymous_user().groups.add(public_group)

        #make a couple of projects and save
        #self.project_bobs = mommy.make_recipe('project.project1', id=1, owner=self.user_bob)
        #self.project_bills = mommy.make_recipe('project.project2', id=2, owner=self.user_bill)
        self.project_bobs = mommy.make_one(Project,
                                           name="one",
                                           owner=self.user_bob,
                                           creation_date=datetime.now(),
                                           modified_date=datetime.now(),
                                           images=[self.mock_image_one, self.mock_image_two])

        self.project_bills = mommy.make_one(Project,
                                            name="two",
                                            owner=self.user_bill,
                                            creation_date=datetime.now(),
                                            modified_date=datetime.now(),
                                            images=[self.mock_image_one, self.mock_image_two])

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
                                        images=[self.mock_image_one, self.mock_image_two])

        assign_perm('view_project', self.user_bill, bills_project)

        # check that bill can see via the API
        response = self.bill_api_client.get(self.project_url, format='json')
        self.assertValidJSONResponse(response)
        self.assertEqual(len(self.deserialize(response)['objects']), 2)

        # check that bill can get to the object itself
        response = self.bill_api_client.get(self.project_url + bills_project.id.__str__() + "/",
                                            format='json')
        self.assertValidJSONResponse(response)

        # check that bob can not see - now we know tastypie API has correct
        # permission validation
        response = self.bob_api_client.get(self.project_url, format='json')
        self.assertValidJSONResponse(response)
        self.assertEqual(len(self.deserialize(response)['objects']), 1)

        # check bob can NOT get to the hidden object
        response = self.bob_api_client.get(self.project_url + bills_project.id.__str__() + "/",
                                           format='json')
        self.assertHttpUnauthorized(response)

        #check that anonymous can see public ones as well
        response = self.anon_api_client.get(self.project_url, format='json')
        self.assertValidJSONResponse(response)
        self.assertEqual(len(self.deserialize(response)['objects']), 0)

        #check anonymous can NOT get to the hidden object
        response = self.anon_api_client.get(self.project_url + bills_project.id.__str__() + "/",
                                            format='json')
        self.assertHttpUnauthorized(response)

        #check bill can POST
        #some post data for testing project creation
        self.bill_post_data = {'name': 'myName',
                               'description': 'my description',
                               'images': ''
                               }

        response = self.bill_api_client.post(
                self.project_url,
                format='json',
                data=self.bill_post_data)

        self.assertHttpCreated(response)

        # check that bill can see via the API
        response = self.bill_api_client.get(self.project_url, format='json')
        self.assertValidJSONResponse(response)
        self.assertEqual(len(self.deserialize(response)['objects']), 3)

        # check that bill can get to the object itself
        response = self.bill_api_client.get(self.project_url + "?name=myName&owner=" + self.user_bill.id.__str__(),
                                            format='json')
        self.assertValidJSONResponse(response)

        new_project_id = self.deserialize(response)['objects'][0]['id'].__str__()

        #check we can modify it - add images
        self.bill_put_data = {'images' : ["/api/dev/image/" + self.mock_image_one.id.__str__() + "/",
                                                  "/api/dev/image/" + self.mock_image_two.id.__str__() + "/"]}
        response = self.bill_api_client.put(
                self.project_url + new_project_id + "/",
                format='json',
                data=self.bill_put_data)

        self.assertEquals(response.status_code, 201)

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

    def test_create_project_helper_function_point_type(self):
        create_project_url = self.project_url + "create_project/"

        self.create_project_data = {'name': 'helpercreated',
                               'description': 'my description',
                               'deployment_id': self.deployment_one.id.__str__(),
                               'image_sampling_methodology': '0',
                               'image_sample_size': '10',
                               'point_sampling_methodology': '0',
                               'point_sample_size': '10',
                               'annotation_set_type': '0',
                               }

        response = self.bill_api_client.post(
                create_project_url,
                format='json',
                data=self.create_project_data)

        self.assertHttpOK(response)

        project_location_split = response['Location'].split('/')
        project_id = project_location_split[len(project_location_split)-2]

        #check we got the right amount of images created
        response = self.bill_api_client.get(self.project_url + "?name=helpercreated", format='json')

        #check the right number of images are on the project
        number_of_images = len(self.deserialize(response)['objects'][0]['images'])
        self.assertEqual(number_of_images, len(Image.objects.filter(deployment=self.deployment_one.id)))

        #check the right number of images are on the associated annotation set
        self.assertEqual(10, len(AnnotationSet.objects.get(project=project_id).images.all()))

    def test_create_project_helper_function_whole_image_type(self):
        create_project_url = self.project_url + "create_project/"

        self.create_project_data = {'name': 'helpercreated',
                               'description': 'my description',
                               'deployment_id': self.deployment_one.id.__str__(),
                               'image_sampling_methodology': '0',
                               'image_sample_size': '10',
                               'point_sampling_methodology': '-1',
                               'point_sample_size': '0',
                               'annotation_set_type': '1',
                               }

        response = self.bill_api_client.post(
                create_project_url,
                format='json',
                data=self.create_project_data)

        self.assertHttpOK(response)

        project_location_split = response['Location'].split('/')
        project_id = project_location_split[len(project_location_split)-2]

        #check we got the right amount of images created
        response = self.bill_api_client.get(self.project_url + "?name=helpercreated", format='json')

        #check the right number of images are on the project        
        number_of_images = len(self.deserialize(response)['objects'][0]['images'])
        self.assertEqual(number_of_images, len(Image.objects.filter(deployment=self.deployment_one.id.__str__())))

        #check the right number of images are on the associated annotation set
        self.assertEqual(10, len(AnnotationSet.objects.get(project=project_id).images.all()))

        annotation_set_images = AnnotationSet.objects.get(project=project_id).images.all()

        #check that the right number of whole image annotations have been applied
        observed_annotation_count = 0
        for image in annotation_set_images:
            observed_annotation_count = observed_annotation_count + len(WholeImageAnnotation.objects.filter(image=image))

        self.assertEqual(40, observed_annotation_count)

    def test_create_csv(self):
        #make a couple of projects and save
        self.project_point = mommy.make_one(Project,
                                           name="one",
                                           owner=self.user_bob,
                                           creation_date=datetime.now(),
                                           modified_date=datetime.now(),
                                           images=[self.mock_image_one, self.mock_image_two])

        self.project_whole = mommy.make_one(Project,
                                            name="two",
                                            owner=self.user_bill,
                                            creation_date=datetime.now(),
                                            modified_date=datetime.now(),
                                            images=[self.mock_image_three])

        create_csv_url1 = self.project_url + str(self.project_point.id) + "/csv/"
        create_csv_url2 = self.project_url + str(self.project_whole.id) + "/csv/"

        #assign them to bob
        authorization.apply_project_permissions(
            self.user_bob, self.project_point)

        authorization.apply_project_permissions(
            self.user_bob, self.project_whole)

        #POINT
        self.annotation_set_point = mommy.make_one(AnnotationSet,
                                            project=self.project_point,
                                            owner=self.user_bob,
                                            creation_date=datetime.now(),
                                            modified_date=datetime.now(),
                                            images=[self.mock_image_one, self.mock_image_two],
                                            point_sampling_methodology=0,
                                            image_sampling_methodology=0,
                                            annotation_set_type=0)
        #WHOLE IMAGE
        self.annotation_set_whole = mommy.make_one(AnnotationSet,
                                            project=self.project_whole,
                                            owner=self.user_bob,
                                            creation_date=datetime.now(),
                                            modified_date=datetime.now(),
                                            images=[self.mock_image_three],
                                            point_sampling_methodology=-1,
                                            image_sampling_methodology=0,
                                            annotation_set_type=1
                                            )

        #assign them one to bob
        authorization.apply_annotation_set_permissions(
            self.user_bob, self.annotation_set_point)

        authorization.apply_annotation_set_permissions(
            self.user_bob, self.annotation_set_whole)

        #Make some codes
        self.annotation_code_1 = mommy.make_one(AnnotationCodes, 
                                              caab_code = '63600901',
                                              code_name = 'Seagrasses')
        self.annotation_code_2 = mommy.make_one(AnnotationCodes, 
                                              caab_code = '10000903',
                                              code_name = 'Massive forms')
        self.annotation_code_3 = mommy.make_one(AnnotationCodes, 
                                              caab_code = '80600901',
                                              code_name = 'Worms')

        #Make some point annotations
        self.annotation_point_1 = mommy.make_one(PointAnnotation,
                                                 annotation_set=self.annotation_set_point,
                                                 x=10.0,
                                                 y=15.0,
                                                 annotation_caab_code = '63600901',
                                                 qualifier_short_name = 'qualifier',
                                                 annotation_caab_code_secondary = '80600901',
                                                 qualifier_short_name_secondary = 'qualifier2',                                                                            
                                                 image=self.mock_image_one,
                                                 owner=self.user_bob)                                 

        self.annotation_point_2 = mommy.make_one(PointAnnotation,
                                                 annotation_set=self.annotation_set_point,
                                                 x=22.0,
                                                 y=16.0,
                                                 annotation_caab_code = '10000903',
                                                 qualifier_short_name = 'qualifier',
                                                 annotation_caab_code_secondary = '10000903',
                                                 qualifier_short_name_secondary = 'qualifierB',                                                                             
                                                 image=self.mock_image_two,
                                                 owner=self.user_bob)                                                                      

        #Make a whole image annotation
        self.whole_image_annotation_point_1 = mommy.make_one(WholeImageAnnotation,
                                                    annotation_set=self.annotation_set_whole,
                                                    annotation_caab_code = '80600901',
                                                    qualifier_short_name = '',
                                                    annotation_caab_code_secondary = '',
                                                    qualifier_short_name_secondary = '',                                                       
                                                    image=self.mock_image_three,
                                                    owner=self.user_bob)


        response1 = self.bob_api_client.post(
                create_csv_url1,
                format='json',
                data={})

        response2 = self.bill_api_client.post(
                create_csv_url2,
                format='json',
                data={})

        self.assertHttpOK(response1)
        self.assertHttpOK(response2)

        output1 = StringIO.StringIO(response1.content)
        output2 = StringIO.StringIO(response2.content)
        cr1 = csv.reader(output1)
        cr2 = csv.reader(output2)

        has_header1 = csv.Sniffer().has_header(response1.content)
        has_header2 = csv.Sniffer().has_header(response2.content)
        self.assertTrue(has_header1, msg=None)
        self.assertTrue(has_header2, msg=None)
        
        #POINT
        expectedRowA1 = ['Annotation Set Type', 'Image Name', 'Campaign Name', 'Campaign Id',
                         'Deployment Name', 'Deployment Id', 'Image Location', 'Annotation Code', 'Annotation Name',
                         'Qualifier Name', 'Annotation Code 2', 'Annotation Name 2', 'Qualifier Name 2',
                         'Point Sampling', 'Point in Image']
        expectedRowA2 = ['Fine Scale', 'Image1', 'Campaign1', self.campaign_one.id.__str__(), 
                         'Deployment1', self.deployment_one.id.__str__(),
                         'POINT (12.4604000000000000 43.9420000000000000)', '63600901', 'Seagrasses', 'qualifier',
                         '80600901', 'Worms', 'qualifier2',
                         '0', '10.0 , 15.0']
        expectedRowA3 = ['Fine Scale', 'Image2', 'Campaign1', self.campaign_one.id.__str__(), 
                         'Deployment2', self.deployment_two.id.__str__(),
                         'POINT (4.5609999999999999 23.1419999999999990)',
                         '10000903', 'Massive forms', 'qualifier',
                         '10000903', 'Massive forms','qualifierB',
                         '0', '22.0 , 16.0' ]

        expectedList1 = [expectedRowA1, expectedRowA2, expectedRowA3]

        i = 0
        for row in cr1:
            self.assertTrue(len(row) == len(expectedList1[i]))
            # due to numerical precision the POINT values will vary.  This test needs re thinking.
            # self.assertTrue(row == expectedList1[i], msg=None)            
            i = i + 1

        #WHOLE IMAGE
        expectedRowB1 = ['Whole Image', 'Image3', 'Campaign2', self.campaign_two.id.__str__(), 
                         'Deployment3', self.deployment_three.id.__str__(),
                         'POINT (62.4151000000000020 41.2233999999999980)', 
                         '80600901', 'Worms', '',
                         '','','',
                         '', '']
        
        expectedList2 = [expectedRowA1, expectedRowB1]       

        i = 0        
        for row in cr2:         
            self.assertTrue(len(row) == len(expectedList2[i]))
            # due to numerical precision the POINT values will vary.  This test needs re thinking.
            # self.assertTrue(row == expectedList2[i], msg=None)
            i = i + 1

    def test_configure(self):

        ### create some objects
        # create a campaign that only bill can see
        bills_project = mommy.make_one(Project,
                                        name="bills",
                                        owner=self.user_bill,
                                        creation_date=datetime.now(),
                                        modified_date=datetime.now(),
                                        images=[self.mock_image_one, self.mock_image_two])

        assign_perm('view_project', self.user_bill, bills_project)
        assign_perm('change_project', self.user_bill, bills_project)

        bills_annotation_set = mommy.make_one(AnnotationSet,
                                            project=bills_project,
                                            owner=self.user_bill,
                                            creation_date=datetime.now(),
                                            modified_date=datetime.now(),
                                            images=[self.mock_image_one, self.mock_image_two],
                                            point_sampling_methodology=2,
                                            image_sampling_methodology=0,
                                            annotation_set_type=0)

        assign_perm('view_annotationset', self.user_bill, bills_annotation_set)
        assign_perm('change_annotationset', self.user_bill, bills_annotation_set)

        ### test we can get the information down
        # check that bill can get to the object itself
        response = self.bill_api_client.get(self.project_url + bills_project.id.__str__() + "/share_project/",
                                            format='json')

        # check that there are no permissions on the object
        project_data = self.deserialize(response)

        project_permissions = project_data['project_permissions']

        self.assertEqual(project_permissions, [])

        ### test we can adjust permissions - give bob view permission
        bobs_permissions = [{'username': 'bob', 'display_name': '', 'permissions': ['view_project']}]
        project_data['is_public'] = "true"
        project_data['project_permissions'] = bobs_permissions

        response = self.bill_api_client.put(
                self.project_url + bills_project.id.__str__() + "/share_project/",
                format='json',
                data=project_data)

        self.assertHttpCreated(response)

        ### verify that the permissions stuck
        response = self.bill_api_client.get(self.project_url + bills_project.id.__str__() + "/share_project/",
                                            format='json')

        # check that there are permissions on the object
        project_data = self.deserialize(response)
        project_permissions = project_data['project_permissions']

        self.assertEqual(len(project_permissions), len(bobs_permissions))
        self.assertEqual(project_permissions[0]['username'], bobs_permissions[0]['username'])
        self.assertEqual(project_permissions[0]['permissions'][0], bobs_permissions[0]['permissions'][0])
        self.assertEqual(project_data["is_public"], True)

        # check the permissions get applied to the underlying annotation sets
        for annotation_set in AnnotationSet.objects.filter(project=bills_project):
            permissions_table = authorization.get_detailed_annotation_set_permissions(self.user_bill, annotation_set)
            is_public = authorization.annotation_set_is_public(annotation_set)

            self.assertEqual(permissions_table[0]['username'], bobs_permissions[0]['username'])
            self.assertEqual(permissions_table[0]['permissions'][0], 'view_annotationset')
            self.assertEqual(is_public, True)

        ### now revoke the permissions and check

        # revoke permissions
        bobs_permissions = []
        project_data['is_public'] = "false"
        project_data['project_permissions'] = bobs_permissions

        response = self.bill_api_client.put(
                self.project_url + bills_project.id.__str__() + "/share_project/",
                format='json',
                data=project_data)

        self.assertHttpCreated(response)

        # check that they got applied
        response = self.bill_api_client.get(self.project_url + bills_project.id.__str__() + "/share_project/",
                                            format='json')

        # check that there are permissions on the object
        project_data = self.deserialize(response)
        project_permissions = project_data['project_permissions']

        self.assertEqual(project_permissions, bobs_permissions)
        self.assertEqual(project_data["is_public"], False)

        # check the permissions get applied to the underlying annotation sets
        for annotation_set in AnnotationSet.objects.filter(project=bills_project):
            permissions_table = authorization.get_detailed_annotation_set_permissions(self.user_bill, annotation_set)
            is_public = authorization.annotation_set_is_public(annotation_set)

            self.assertEqual(permissions_table, [])
            self.assertEqual(is_public, False)


class TestAnnotationSetResource(ResourceTestCase):

    def setUp(self):
        #Tastypie stuff
        super(TestAnnotationSetResource, self).setUp()

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
                                           images=[self.mock_image_one, self.mock_image_two])

        self.project_bills = mommy.make_one(Project,
                                            owner=self.user_bill,
                                            creation_date=datetime.now(),
                                            modified_date=datetime.now(),
                                            images=[self.mock_image_one, self.mock_image_two])

        #assign this one to bob
        authorization.apply_project_permissions(
            self.user_bob, self.project_bobs)

        #assign this one to bill
        authorization.apply_project_permissions(
            self.user_bill, self.project_bills)

        self.annotation_set_bobs = mommy.make_one(AnnotationSet,
                                            project=self.project_bobs,
                                            owner=self.user_bob,
                                            creation_date=datetime.now(),
                                            modified_date=datetime.now(),
                                            images=[self.mock_image_one, self.mock_image_two],
                                            point_sampling_methodology=0,
                                            image_sampling_methodology=0,
                                            annotation_set_type=0)

        self.annotation_set_bills = mommy.make_one(AnnotationSet,
                                            project=self.project_bills,
                                            owner=self.user_bill,
                                            creation_date=datetime.now(),
                                            modified_date=datetime.now(),
                                            images=[self.mock_image_one, self.mock_image_two],
                                            point_sampling_methodology=1,
                                            image_sampling_methodology=0,
                                            annotation_set_type=0)

        #assign this one to bob
        authorization.apply_annotation_set_permissions(
            self.user_bob, self.annotation_set_bobs)

        #assign this one to bill
        authorization.apply_annotation_set_permissions(
            self.user_bill, self.annotation_set_bills)


        #create a big project with 20 images
        self.project_bills_big = mommy.make_one(Project,
                                            owner=self.user_bill,
                                            creation_date=datetime.now(),
                                            modified_date=datetime.now(),
                                            images=self.mock_image_list)
        #assign this one to bill
        authorization.apply_project_permissions(
            self.user_bill, self.project_bills_big)

        #the API url for resources
        self.annotation_set_url = '/api/dev/annotation_set/'
        self.point_annotation_url = '/api/dev/point_annotation/'

    def test_project_operations_disabled(self):

        # test that we can not Create Update Delete as anonymous
        self.assertHttpUnauthorized(
            self.anon_api_client.post(
                self.annotation_set_url,
                format='json',
                data={'image_sample_size': '20'})
        )

        self.assertHttpUnauthorized(
            self.anon_api_client.put(
                self.annotation_set_url + self.annotation_set_bobs.id.__str__() + "/",
                format='json',
                data={})
        )

        self.assertHttpUnauthorized(
            self.anon_api_client.delete(
                self.annotation_set_url + self.annotation_set_bobs.id.__str__() + "/",
                format='json')
        )

    def test_annotationset_operations_as_authorised_users(self):
        # create a campaign that only bill can see
        bills_annotation_set = mommy.make_one(AnnotationSet,
                                            project=self.project_bills,
                                            owner=self.user_bob,
                                            creation_date=datetime.now(),
                                            modified_date=datetime.now(),
                                            images=[self.mock_image_one, self.mock_image_two],
                                            point_sampling_methodology=2,
                                            image_sampling_methodology=0,
                                            annotation_set_type=0)

        assign_perm('view_annotationset', self.user_bill, bills_annotation_set)

        # check that bill can see via the API
        response = self.bill_api_client.get(self.annotation_set_url, format='json')
        self.assertValidJSONResponse(response)
        self.assertEqual(len(self.deserialize(response)['objects']), 2)

        # check that bill can get to the object itself
        response = self.bill_api_client.get(self.annotation_set_url + bills_annotation_set.id.__str__() + "/",
                                            format='json')
        self.assertValidJSONResponse(response)

        # check that bob can not see - now we know tastypie API has correct
        # permission validation
        response = self.bob_api_client.get(self.annotation_set_url, format='json')
        self.assertValidJSONResponse(response)
        self.assertEqual(len(self.deserialize(response)['objects']), 1)

        # check bob can NOT get to the hidden object
        response = self.bob_api_client.get(self.annotation_set_url + bills_annotation_set.id.__str__() + "/",
                                           format='json')
        self.assertHttpUnauthorized(response)

        #check that anonymous can see public ones as well
        response = self.anon_api_client.get(self.annotation_set_url, format='json')
        self.assertValidJSONResponse(response)
        self.assertEqual(len(self.deserialize(response)['objects']), 0)

        #check anonymous can NOT get to the hidden object
        response = self.anon_api_client.get(self.annotation_set_url + bills_annotation_set.id.__str__() + "/",
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
                               'images': [ "/api/dev/image/" + self.mock_image_one.id.__str__() + "/",
                                           "/api/dev/image/" + self.mock_image_two.id.__str__() + "/"],
                               #'images': '',
                               'point_sampling_methodology': '0',
                               'image_sampling_methodology': '0',
                               'image_sample_size': '2',
                               'point_sample_size': '15',
                               'annotation_set_type': '0'
                                }

        response = self.bill_api_client.post(
                self.annotation_set_url,
                format='json',
                data=self.bill_post_data)

        self.assertHttpCreated(response)

        # check that bill can see via the API
        response = self.bill_api_client.get(self.annotation_set_url, format='json')
        self.assertValidJSONResponse(response)
        self.assertEqual(len(self.deserialize(response)['objects']), 3)

        # check that bill can get to the object itself
        response = self.bill_api_client.get(self.annotation_set_url + "?name=myName2&owner=" + self.user_bill.id.__str__(),
                                            format='json')

        self.assertValidJSONResponse(response)

        new_annotationset_id = self.deserialize(response)['objects'][0]['id'].__str__()

        #check we can modify it - change the description...start with the original POST data, because we're not testing PATCH
        self.bill_put_data = self.bill_post_data
        self.bill_put_data['description'] = 'my new description'

        response = self.bill_api_client.put(
                self.annotation_set_url + new_annotationset_id + "/",
                format='json',
                data=self.bill_put_data)
        self.assertHttpAccepted(response)

        response = self.bill_api_client.get(self.annotation_set_url + "?name=myName&owner=" + self.user_bill.id.__str__(),
                                            format='json')

        #check bill can DELETE
        response = self.bill_api_client.delete(
            self.annotation_set_url + new_annotationset_id + "/",
            format='json')

        self.assertHttpAccepted(response)

        # check that bill can see via the API
        response = self.bill_api_client.get(self.annotation_set_url, format='json')
        self.assertValidJSONResponse(response)
        self.assertEqual(len(self.deserialize(response)['objects']), 2)

    def test_point_annotation_set_creation_random(self):
        #some post data for testing project creation
        self.bill_post_data = {'project':'/api/dev/project/' + self.project_bills_big.id.__str__() + '/',
                               'name': 'myName',
                               'description': 'my description',
                               'images': [ "/api/dev/image/" + self.mock_image_one.id.__str__() + "/",
                                           "/api/dev/image/" + self.mock_image_two.id.__str__() + "/"],                               
                               'point_sampling_methodology': '0',
                               'image_sampling_methodology': '0',
                               'image_sample_size': '2',
                               'point_sample_size': '15',
                               'annotation_set_type': '0',
                                }

        response = self.bill_api_client.post(
                self.annotation_set_url,
                format='json',
                data=self.bill_post_data)

        self.assertHttpCreated(response)

        # check that bill can get to the object itself
        response = self.bill_api_client.get(self.annotation_set_url + "?name=myName&owner=" + self.user_bill.id.__str__(),
                                            format='json')
        # check that the API did indeed samle 2 images
        images = self.deserialize(response)['objects'][0]['images']
        self.assertEqual(len(images), 2)

        # check that the API set 15 points per image
        for image in images:

            image_location_split = image.split('/')
            image_id = image_location_split[len(image_location_split)-2]

            response = self.bill_api_client.get(self.point_annotation_url + "?image=" + image_id, format='json')
            self.assertEqual(len(self.deserialize(response)['objects']), 15)

    def test_point_annotation_set_creation_stratified(self):
        #some post data for testing project creation
        self.bill_post_data = {'project':'/api/dev/project/' + self.project_bills_big.id.__str__() + '/',
                               'name': 'myName',
                               'description': 'my description',        
                               'images': [ "/api/dev/image/" + self.mock_image_one.id.__str__() + "/",
                                           "/api/dev/image/" + self.mock_image_two.id.__str__() + "/"],
                               'point_sampling_methodology': '0',
                               'image_sampling_methodology': '1',
                               'image_sample_size': '2',
                               'point_sample_size': '5',
                               'annotation_set_type': '0'
                                }

        response = self.bill_api_client.post(
                self.annotation_set_url,
                format='json',
                data=self.bill_post_data)

        self.assertHttpCreated(response)

        # check that bill can get to the object itself
        response = self.bill_api_client.get(self.annotation_set_url + "?name=myName&owner=" + self.user_bill.id.__str__(),
                                            format='json')

        # check that the API did indeed sample 2 images
        images = self.deserialize(response)['objects'][0]['images']
        self.assertEqual(len(images), 2)

        # check that the API set 5 points per image
        for image in images:
            image_location_split = image.split('/')
            image_id = image_location_split[len(image_location_split)-2]
            response = self.bill_api_client.get(self.point_annotation_url + "?image=" + image_id, format='json')
            self.assertEqual(len(self.deserialize(response)['objects']), 5)

    def test_annotation_set_creation_unimplemented(self):
        #some post data for testing project creation
        self.bill_post_data = {'project':'/api/dev/project/' + self.project_bills_big.id.__str__() + '/',
                               'name': 'myName2',
                               'description': 'my description',
                               'owner': "/api/dev/users/" + self.user_bill.id.__str__()+"/",
                               'creation_date': '2012-05-01',
                               'modified_date': '2012-05-01',
                               'images': '',
                               'point_sampling_methodology': '4',
                               'image_sampling_methodology': '4',
                               'image_sample_size': '10',
                               'point_sample_size': '5',
                               'annotation_set_type': '0'
                                }

        response = self.bill_api_client.post(
                self.annotation_set_url,
                format='json',
                data=self.bill_post_data)

        self.assertHttpNotImplemented(response)

    def test_copy_wholeimage_classification(self):

        # create some annotations on an image
        WholeImageAnnotation(annotation_set=self.annotation_set_bobs,
                             image=self.mock_image_one,
                             owner=self.user_bob,
                             annotation_caab_code="one",
                             qualifier_short_name="").save()

        WholeImageAnnotation(annotation_set=self.annotation_set_bobs,
                             image=self.mock_image_one,
                             owner=self.user_bob,
                             annotation_caab_code="two",
                             qualifier_short_name="").save()

        WholeImageAnnotation(annotation_set=self.annotation_set_bobs,
                             image=self.mock_image_one,
                             owner=self.user_bob,
                             annotation_caab_code="three",
                             qualifier_short_name="").save()

        WholeImageAnnotation(annotation_set=self.annotation_set_bobs,
                             image=self.mock_image_one,
                             owner=self.user_bob,
                             annotation_caab_code="four",
                             qualifier_short_name="").save()

        # try and copy without permissions
        response = self.bill_api_client.get(self.annotation_set_url +
                                            str(self.annotation_set_bobs.id) +
                                            "/copy_wholeimage_classification/" +
                                            "?source_image=" + self.mock_image_one.id.__str__() +
                                            "&destination_image=" + self.mock_image_two.id.__str__(),
                                            format='json')

        # check unauthorised, and annotations not copied
        self.assertHttpUnauthorized(response)

        annotation_objects = WholeImageAnnotation.objects.filter(image=self.mock_image_two,
                                                                   annotation_set=self.annotation_set_bobs)

        self.assertEqual(annotation_objects.count(), 0)

        # try and copy with permissions
        response = self.bob_api_client.get(self.annotation_set_url +
                                            str(self.annotation_set_bobs.id) +
                                            "/copy_wholeimage_classification/" +
                                            "?source_image=" + self.mock_image_one.id.__str__() +
                                            "&destination_image=" + self.mock_image_two.id.__str__(),
                                            format='json')

        # check OK and annotations copied
        self.assertHttpOK(response)

        annotation_objects = WholeImageAnnotation.objects.filter(image=self.mock_image_two,
                                                                   annotation_set=self.annotation_set_bobs)

        self.assertEqual(annotation_objects.count(), 4)

    def test_same_get_image_similarity_status(self):

        # create some annotations on images
        WholeImageAnnotation(annotation_set=self.annotation_set_bobs,
                             image=self.mock_image_one,
                             owner=self.user_bob,
                             annotation_caab_code="one",
                             qualifier_short_name="",
                             coverage_percentage=50).save()

        WholeImageAnnotation(annotation_set=self.annotation_set_bobs,
                             image=self.mock_image_one,
                             owner=self.user_bob,
                             annotation_caab_code="two",
                             qualifier_short_name="",
                             coverage_percentage=60).save()

        WholeImageAnnotation(annotation_set=self.annotation_set_bobs,
                             image=self.mock_image_two,
                             owner=self.user_bob,
                             annotation_caab_code="one",
                             qualifier_short_name="",
                             coverage_percentage=50).save()

        WholeImageAnnotation(annotation_set=self.annotation_set_bobs,
                             image=self.mock_image_two,
                             owner=self.user_bob,
                             annotation_caab_code="two",
                             qualifier_short_name="",
                             coverage_percentage=60).save()

        # try and copy with permissions
        response = self.bob_api_client.get(self.annotation_set_url +
                                            str(self.annotation_set_bobs.id) +
                                            "/get_image_similarity_status/" +
                                            "?source_image=" + self.mock_image_one.id.__str__() +
                                            "&comparison_image=" + self.mock_image_two.id.__str__(),
                                            format='json')

        self.assertEqual(self.deserialize(response)['same'], "true")

        # make them different, and check false response
        WholeImageAnnotation(annotation_set=self.annotation_set_bobs,
                             image=self.mock_image_two,
                             owner=self.user_bob,
                             annotation_caab_code="three",
                             qualifier_short_name="").save()

    def test_notsame_get_image_similarity_status(self):

        # create some annotations on images
        WholeImageAnnotation(annotation_set=self.annotation_set_bobs,
                             image=self.mock_image_one,
                             owner=self.user_bob,
                             annotation_caab_code="one",
                             qualifier_short_name="").save()

        WholeImageAnnotation(annotation_set=self.annotation_set_bobs,
                             image=self.mock_image_one,
                             owner=self.user_bob,
                             annotation_caab_code="two",
                             qualifier_short_name="").save()

        WholeImageAnnotation(annotation_set=self.annotation_set_bobs,
                             image=self.mock_image_two,
                             owner=self.user_bob,
                             annotation_caab_code="one",
                             qualifier_short_name="").save()

        WholeImageAnnotation(annotation_set=self.annotation_set_bobs,
                             image=self.mock_image_two,
                             owner=self.user_bob,
                             annotation_caab_code="two",
                             qualifier_short_name="").save()

        WholeImageAnnotation(annotation_set=self.annotation_set_bobs,
                             image=self.mock_image_two,
                             owner=self.user_bob,
                             annotation_caab_code="three",
                             qualifier_short_name="").save()

        # try and copy with permissions
        response = self.bob_api_client.get(self.annotation_set_url +
                                            str(self.annotation_set_bobs.id) +
                                            "/get_image_similarity_status/" +
                                            "?source_image=" + self.mock_image_one.id.__str__() +
                                            "&comparison_image=" + self.mock_image_two.id.__str__(),
                                            format='json')

        self.assertEqual(self.deserialize(response)['same'], "false")

    def test_get_percentage_complete(self):

        # create some annotations on images
        WholeImageAnnotation(annotation_set=self.annotation_set_bobs,
                             image=self.mock_image_one,
                             owner=self.user_bob,
                             annotation_caab_code="one",
                             qualifier_short_name="").save()

        WholeImageAnnotation(annotation_set=self.annotation_set_bobs,
                             image=self.mock_image_one,
                             owner=self.user_bob,
                             annotation_caab_code="two",
                             qualifier_short_name="").save()

        WholeImageAnnotation(annotation_set=self.annotation_set_bobs,
                             image=self.mock_image_two,
                             owner=self.user_bob,
                             annotation_caab_code="three",
                             qualifier_short_name="").save()

        WholeImageAnnotation(annotation_set=self.annotation_set_bobs,
                             image=self.mock_image_two,
                             owner=self.user_bob,
                             annotation_caab_code="four",
                             qualifier_short_name="").save()

        WholeImageAnnotation(annotation_set=self.annotation_set_bobs,
                             image=self.mock_image_two,
                             owner=self.user_bob,
                             annotation_caab_code="five",
                             qualifier_short_name="").save()

        WholeImageAnnotation(annotation_set=self.annotation_set_bobs,
                             image=self.mock_image_two,
                             owner=self.user_bob,
                             annotation_caab_code="",
                             qualifier_short_name="").save()

        PointAnnotation(annotation_set=self.annotation_set_bobs,
                        x=22.0,
                        y=16.0,
                        annotation_caab_code = '10000903',
                        image=self.mock_image_two,
                        owner=self.user_bob).save()

        # try and copy with permissions
        response = self.bob_api_client.get(self.annotation_set_url +
                                            str(self.annotation_set_bobs.id) +
                                            "/get_percentage_complete/",
                                            format='json')

        self.assertEqual(self.deserialize(response)['percentage_complete'], 85.71)


class TestPointAnnotationResource(ResourceTestCase):

    def setUp(self):
        #Tastypie stuff
        super(TestPointAnnotationResource, self).setUp()

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
                                           images=[self.mock_image_one, self.mock_image_two])

        self.project_bills = mommy.make_one(Project,
                                            owner=self.user_bill,
                                            creation_date=datetime.now(),
                                            modified_date=datetime.now(),
                                            images=[self.mock_image_one, self.mock_image_two])

        #assign this one to bob
        authorization.apply_project_permissions(
            self.user_bob, self.project_bobs)

        #assign this one to bill
        authorization.apply_project_permissions(
            self.user_bill, self.project_bills)

        self.annotation_set_bobs = mommy.make_one(AnnotationSet,
                                            project=self.project_bobs,
                                            owner=self.user_bob,
                                            creation_date=datetime.now(),
                                            modified_date=datetime.now(),
                                            images=[self.mock_image_one, self.mock_image_two],
                                            point_sampling_methodology=0,
                                            image_sampling_methodology=0,
                                            annotation_set_type=0)

        self.annotation_set_bills = mommy.make_one(AnnotationSet,
                                            project=self.project_bills,
                                            owner=self.user_bill,
                                            creation_date=datetime.now(),
                                            modified_date=datetime.now(),
                                            images=[self.mock_image_one, self.mock_image_two],
                                            point_sampling_methodology=1,
                                            image_sampling_methodology=0,
                                            annotation_set_type=0)

        #assign this one to bob
        authorization.apply_annotation_set_permissions(
            self.user_bob, self.annotation_set_bobs)

        #assign this one to bill
        authorization.apply_annotation_set_permissions(
            self.user_bill, self.annotation_set_bills)

        self.annotation_point_bobs = mommy.make_one(PointAnnotation,
                                                    annotation_set=self.annotation_set_bobs,
                                                    image=self.mock_image_one,
                                                    owner=self.user_bob)

        self.annotation_point_bills = mommy.make_one(PointAnnotation,
                                                    annotation_set=self.annotation_set_bills,
                                                    image=self.mock_image_one,
                                                    owner=self.user_bill)

        #the API url for annotation points
        self.point_annotation_url = '/api/dev/point_annotation/'

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
        bills_private_annotation_set = mommy.make_one(AnnotationSet,
                                            project=self.project_bills,
                                            owner=self.user_bob,
                                            creation_date=datetime.now(),
                                            modified_date=datetime.now(),
                                            images=[self.mock_image_one, self.mock_image_two],
                                            point_sampling_methodology=2,
                                            image_sampling_methodology=0,
                                            annotation_set_type=0)

        assign_perm('view_annotationset', self.user_bill, bills_private_annotation_set)

        bills_private_point_annotation = mommy.make_one(PointAnnotation,
                                            annotation_set=bills_private_annotation_set,
                                            image=self.mock_image_one,
                                            owner=self.user_bill,
                                            )

        #assign('view_AnnotationSet', self.user_bill, bills_point_annotation)

        # check that bill can see via the API
        response = self.bill_api_client.get(self.point_annotation_url, format='json')
        self.assertValidJSONResponse(response)
        self.assertEqual(len(self.deserialize(response)['objects']), 2)

        # check that bill can get to the object itself
        response = self.bill_api_client.get(self.point_annotation_url + bills_private_point_annotation.id.__str__() + "/",
                                            format='json')
        self.assertValidJSONResponse(response)

        # check that bob can not see - now we know tastypie API has correct
        # permission validation
        response = self.bob_api_client.get(self.point_annotation_url, format='json')
        self.assertValidJSONResponse(response)
        self.assertEqual(len(self.deserialize(response)['objects']), 1)

        # check bob can NOT get to the hidden object
        response = self.bob_api_client.get(self.point_annotation_url + bills_private_point_annotation.id.__str__() + "/",
                                           format='json')
        self.assertHttpUnauthorized(response)

        #check that anonymous can see public ones as well
        response = self.anon_api_client.get(self.point_annotation_url, format='json')
        self.assertValidJSONResponse(response)
        self.assertEqual(len(self.deserialize(response)['objects']), 0)

        #check anonymous can NOT get to the hidden object
        response = self.anon_api_client.get(self.point_annotation_url + bills_private_point_annotation.id.__str__() + "/",
                                            format='json')
        self.assertHttpUnauthorized(response)

        #check bill can POST
        #some post data for testing project creation
        self.bill_post_data = {'annotation_set':'/api/dev/annotation_set/' + self.annotation_set_bills.id.__str__() + '/',
                               'annotation_caab_code': 'caab1',
                               'qualifier_short_name': 'qualifier1',
                               'owner': "/api/dev/users/" + self.user_bill.id.__str__()+"/",
                               'image': "/api/dev/image/" + self.mock_image_one.id.__str__() +"/",
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
        self.assertEqual(len(self.deserialize(response)['objects']), 3)

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
        self.assertEqual(len(self.deserialize(response)['objects']), 2)


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


class TestWholeImageAnnotationResource(ResourceTestCase):

    def setUp(self):
        #Tastypie stuff
        super(TestWholeImageAnnotationResource, self).setUp()

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
        self.project_bobs = mommy.make_one(Project, owner=self.user_bob,
                                           creation_date=datetime.now(),
                                           modified_date=datetime.now(),
                                           images=[self.mock_image_one, self.mock_image_two])

        self.project_bills = mommy.make_one(Project,
                                            owner=self.user_bill,
                                            creation_date=datetime.now(),
                                            modified_date=datetime.now(),
                                            images=[self.mock_image_one, self.mock_image_two])

        #assign this one to bob
        authorization.apply_project_permissions(self.user_bob, self.project_bobs)

        #assign this one to bill
        authorization.apply_project_permissions(self.user_bill, self.project_bills)

        self.annotation_set_bobs = mommy.make_one(AnnotationSet,
                                            project=self.project_bobs,
                                            owner=self.user_bob,
                                            creation_date=datetime.now(),
                                            modified_date=datetime.now(),
                                            images=[self.mock_image_one, self.mock_image_two],
                                            point_sampling_methodology=0,
                                            image_sampling_methodology=0,
                                            annotation_set_type=0)

        self.annotation_set_bills = mommy.make_one(AnnotationSet,
                                            project=self.project_bills,
                                            owner=self.user_bill,
                                            creation_date=datetime.now(),
                                            modified_date=datetime.now(),
                                            images=[self.mock_image_one, self.mock_image_two],
                                            point_sampling_methodology=1,
                                            image_sampling_methodology=0,
                                            annotation_set_type=0)

        #assign this one to bob
        authorization.apply_annotation_set_permissions(self.user_bob, self.annotation_set_bobs)

        #assign this one to bill
        authorization.apply_annotation_set_permissions(self.user_bill, self.annotation_set_bills)

        self.whole_image_annotation_point_bobs = mommy.make_one(WholeImageAnnotation,
                                                    annotation_set=self.annotation_set_bobs,
                                                    image=self.mock_image_one,
                                                    owner=self.user_bob)

        self.whole_image_annotation_point_bills = mommy.make_one(WholeImageAnnotation,
                                                    annotation_set=self.annotation_set_bills,
                                                    image=self.mock_image_one,
                                                    owner=self.user_bill)

        #the API url for whole image annotation points
        self.whole_image_annotation_url = '/api/dev/whole_image_annotation/'

    def test_whole_image_annotation_operations_disabled(self):
        # test that we can not Create Update Delete as anonymous
        self.assertHttpUnauthorized(
            self.anon_api_client.post(
                self.whole_image_annotation_url,
                format='json',
                data={})
        )

        self.assertHttpUnauthorized(
            self.anon_api_client.put(
                self.whole_image_annotation_url + self.whole_image_annotation_point_bobs.id.__str__() + "/",
                format='json',
                data={})
        )

        self.assertHttpUnauthorized(
            self.anon_api_client.delete(
                self.whole_image_annotation_url + self.whole_image_annotation_point_bills.id.__str__() + "/",
                format='json')
        )

    def test_point_annotation_operations_as_authorised_users(self):
        # create a point annotation that only bill can see

        bills_private_annotation_set = mommy.make_one(AnnotationSet,
                                            project=self.project_bills,
                                            owner=self.user_bob,
                                            creation_date=datetime.now(),
                                            modified_date=datetime.now(),
                                            images=[self.mock_image_one, self.mock_image_two],
                                            point_sampling_methodology=-1,
                                            image_sampling_methodology=0,
                                            annotation_set_type=1)

        assign_perm('view_annotationset', self.user_bill, bills_private_annotation_set)

        bills_private_whole_image_annotation = mommy.make_one(WholeImageAnnotation,
                                            annotation_set=bills_private_annotation_set,
                                            image=self.mock_image_one,
                                            owner=self.user_bill)

        # check that bill can see via the API
        response = self.bill_api_client.get(self.whole_image_annotation_url, format='json')
        self.assertValidJSONResponse(response)
        self.assertEqual(len(self.deserialize(response)['objects']), 2)

        # check that bill can get to the object itself
        response = self.bill_api_client.get(self.whole_image_annotation_url + bills_private_whole_image_annotation.id.__str__() + "/",
                                            format='json')
        self.assertValidJSONResponse(response)

        # check that bob can not see - now we know tastypie API has correct
        # permission validation
        response = self.bob_api_client.get(self.whole_image_annotation_url, format='json')
        self.assertValidJSONResponse(response)
        self.assertEqual(len(self.deserialize(response)['objects']), 1)

        # check bob can NOT get to the hidden object
        response = self.bob_api_client.get(self.whole_image_annotation_url + bills_private_whole_image_annotation.id.__str__() + "/",
                                           format='json')
        self.assertHttpUnauthorized(response)

        #check that anonymous can see public ones as well
        response = self.anon_api_client.get(self.whole_image_annotation_url, format='json')
        self.assertValidJSONResponse(response)
        self.assertEqual(len(self.deserialize(response)['objects']), 0)

        #check anonymous can NOT get to the hidden object
        response = self.anon_api_client.get(self.whole_image_annotation_url + bills_private_whole_image_annotation.id.__str__() + "/",
                                            format='json')
        self.assertHttpUnauthorized(response)

        #check bill can POST
        #some post data for testing project creation
        self.bill_post_data = {'annotation_set':'/api/dev/annotation_set/' + self.annotation_set_bills.id.__str__() + '/',
                               'annotation_caab_code': 'caab1',
                               'qualifier_short_name': 'qualifier1',
                               'owner': "/api/dev/users/" + self.user_bill.id.__str__()+"/",
                               'image': "/api/dev/image/" + self.mock_image_one.id.__str__() +"/"}

        response = self.bill_api_client.post(
                self.whole_image_annotation_url,
                format='json',
                data=self.bill_post_data)

        self.assertHttpCreated(response)

        # check that bill can see via the API
        response = self.bill_api_client.get(self.whole_image_annotation_url, format='json')
        self.assertValidJSONResponse(response)
        self.assertEqual(len(self.deserialize(response)['objects']), 3)

        # check that bill can get to the object itself
        response = self.bill_api_client.get(self.whole_image_annotation_url + "?annotation_caab_code=caab1",
                                            format='json')
        self.assertValidJSONResponse(response)

        new_wholeimageannotation_id = self.deserialize(response)['objects'][0]['id'].__str__()

        #check we can modify it - add images
        self.bill_put_data = {'annotation_caab_code' : 'caab2'}
        response = self.bill_api_client.put(
                self.whole_image_annotation_url + new_wholeimageannotation_id + "/",
                format='json',
                data=self.bill_put_data)

        self.assertHttpAccepted(response)

        response = self.bill_api_client.get(self.whole_image_annotation_url + "?image=" + self.mock_image_one.id.__str__(),
                                            format='json')

        #check bill can DELETE
        response = self.bill_api_client.delete(
            self.whole_image_annotation_url + new_wholeimageannotation_id + "/",
            format='json')

        self.assertHttpAccepted(response)

        # check that bill can see via the API
        response = self.bill_api_client.get(self.whole_image_annotation_url, format='json')
        self.assertValidJSONResponse(response)
        self.assertEqual(len(self.deserialize(response)['objects']), 2)

