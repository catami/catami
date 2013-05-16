"""
Annotation API/model test set

"""
from django.contrib.auth.models import User, Group
from django.test.utils import setup_test_environment
from django.test.client import RequestFactory
import guardian
from guardian.shortcuts import assign, get_perms, get_perms_for_model
from model_mommy import mommy
from tastypie.test import ResourceTestCase, TestApiClient
from catamiPortal import settings
from catamidb import authorization
from catamidb.models import Campaign, Deployment,Image, ScientificMeasurementType
from collection import authorization
from collection.models import CollectionManager, Collection
from django.contrib.gis.geos import Point, Polygon

setup_test_environment()
from django.core import management
from django.test import TestCase
from django.contrib.auth.models import AnonymousUser


# basic setup
def create_setup(self):

    self.collection_manager = CollectionManager()

    self.campaign_one = mommy.make_one('catamidb.Campaign', id=1)

    self.deployment_one = mommy.make_one(
        'catamidb.Deployment',
        start_position=Point(12.4604, 43.9420),
        end_position=Point(12.4604,43.9420),
        transect_shape=Polygon(((0.0, 0.0), (0.0, 50.0), (50.0, 50.0), (50.0, 0.0), (0.0, 0.0))),
        id=1,
        campaign=self.campaign_one)



    self.pose_one = mommy.make_one('catamidb.Pose',
                                   position=Point(12.4, 23.5),
                                   id=1,
                                   deployment=self.deployment_one,
                                   depth=10
    )

    self.pose_two = mommy.make_one('catamidb.Pose',
                                   position=Point(12.42, 23.5),
                                   id=2,
                                   deployment=self.deployment_one,
                                   depth=15
    )

    self.camera_one = mommy.make_one('catamidb.Camera',
                                     deployment=self.deployment_one,
                                     id=1,
    )

    self.image_list = ['/live/test/test2.jpg', '/live/test/test1.jpg']
    self.mock_image_one = mommy.make_one('catamidb.Image',
                                         pose=self.pose_one,
                                         camera=self.camera_one,
                                         web_location=self.image_list[0],
                                         pk=1
    )
    self.mock_image_two = mommy.make_one('catamidb.Image',
                                         pose=self.pose_two,
                                         camera=self.camera_one,
                                         web_location=self.image_list[1],
                                         pk=2
    )


    #make pose measurements
    self.temp_one = mommy.make_one('catamidb.ScientificPoseMeasurement',
                                   id=1,
                                   pose=self.pose_one,
                                   measurement_type=ScientificMeasurementType.objects.get(normalised_name="temperature"),
                                   value=10)

    self.temp_two = mommy.make_one('catamidb.ScientificPoseMeasurement',
                                   id=2,
                                   pose=self.pose_two,
                                   measurement_type=ScientificMeasurementType.objects.get(normalised_name="temperature"),
                                   value=15)

    self.salinity_one = mommy.make_one('catamidb.ScientificPoseMeasurement',
                                   id=3,
                                   pose=self.pose_one,
                                   measurement_type=ScientificMeasurementType.objects.get(normalised_name="salinity"),
                                   value=10)

    self.salinity_two = mommy.make_one('catamidb.ScientificPoseMeasurement',
                                   id=4,
                                   pose=self.pose_two,
                                   measurement_type=ScientificMeasurementType.objects.get(normalised_name="salinity"),
                                   value=15)

    self.altitude_one = mommy.make_one('catamidb.ScientificPoseMeasurement',
                                   id=5,
                                   pose=self.pose_one,
                                   measurement_type=ScientificMeasurementType.objects.get(normalised_name="altitude"),
                                   value=10)

    self.altitude_two = mommy.make_one('catamidb.ScientificPoseMeasurement',
                                   id=6,
                                   pose=self.pose_two,
                                   measurement_type=ScientificMeasurementType.objects.get(normalised_name="altitude"),
                                   value=15)

#======================================#
# Test Stuff
#======================================#
class TestAnnotationModel(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def some_kind_of_model_test(self):
        pass

class TestAnnotationAPI(ResourceTestCase):
    def setUp(self):
        super(TestAnnotationAPI, self).setUp()
        create_setup(self)


        #API urls
        self.annotation_code_url = '/api/dev/annotation_code/'
        self.point_annotation_url = '/api/dev/point_annotation/'
        self.point_annotation_set_url = '/api/dev/point_annotation_set/'

        #setup test case
        self.user_api_client = TestApiClient()
        self.anon_api_client = TestApiClient()

        # Create a user for authent
        self.user_bob_username = 'bob'
        self.user_bob_password = 'bob'

        self.user_bob = User.objects.create_user(self.user_bob_username,
                                         'person@example.com',
                                         self.user_bob_password)

        #assign('annotations.create_pointannotationset', self.user_bob)
        #assign('annotations.view_pointannotationset', self.user_bob)

        #check that required permissions were applied
        #self.assertTrue(self.user_bob.has_perm('annotations.create_pointannotationset'))
        #self.assertTrue(self.user_bob.has_perm('annotations.view_pointannotationset'))

        self.user_api_client.client.login(username='bob', password='bob')

        #assign users to the Public group
        public_group, created = Group.objects.get_or_create(name='Public')
        self.user_bob.groups.add(public_group)
        guardian.utils.get_anonymous_user().groups.add(public_group)

        #make a collection and assign to user 'bob'
        self.collection_bobs = mommy.make_recipe('collection.collection1', id=1, owner=self.user_bob,name='collectionname')
        #self.collection_manager.collection_from_deployment(self.user_bob, self.deployment_one)
        #self.collection_bobs = Collection.objects.get(name=self.deployment_one.short_name)

        authorization.apply_collection_permissions(self.user_bob, self.collection_bobs)

        self.null_post_data = {}

        #create annotation needs collection, owner, name, methodology, count
        self.post_data = {
            'collection': '/api/dev/collection/{0}/'.format(self.collection_bobs.pk),
            'owner': '/api/dev/users/{0}/'.format(self.user_bob.pk),
            'name': 'useful_name',
            'methodology': '0',
            'count': '50',
        }

    def tearDown(self):
        pass

    #==================================================#
    # unittests
    #==================================================#

    def test_create_annotation_set_nonauth_user(self):
        self.assertHttpUnauthorized(
            self.anon_api_client.post(self.point_annotation_set_url,
                                      format='json',
                                      data=self.post_data))

    def test_create_read_delete_point_annotation_set(self):
        #make an annotation set
        response = self.user_api_client.post(self.point_annotation_set_url, format='json', data=self.post_data)
        self.assertHttpCreated(response)

        #is it there? yes!
        response = self.user_api_client.get(self.point_annotation_set_url + "1/", format='json')
        self.assertHttpOK(response)

        #anonymous should not be able to delte it
        response = self.anon_api_client.delete(self.point_annotation_set_url + "1/", format='json')
        self.assertHttpUnauthorized(response)

        #delete it - there is an empty response from deletes
        response = self.user_api_client.delete(self.point_annotation_set_url + "1/", format='json')

        #is it there? no
        response = self.user_api_client.get(self.point_annotation_set_url + "1/", format='json')
        self.assertHttpNotFound(response)

    # def test_apply_annotation(self):
    #     pass

    # def test_apply_and_reapply_annotation(self):
    #     pass

    # def test_apply_and_clear_annotation(self):
    #     pass

    # def test_make_and_delete_annotation_set(self):
    #     pass

if __name__ == '__main__':
    unittest.main()
