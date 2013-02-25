import logging
from django.contrib.auth.models import User
from django.contrib.gis.geos import Point, Polygon
from django.test.utils import setup_test_environment
from django.test import TestCase
from model_mommy import mommy
from catamidb.models import Image
from collection.models import CollectionManager, Collection

logger = logging.getLogger(__name__)

def create_setup(self):
    self.campaign_one = mommy.make_one('catamidb.Campaign', id=1)

    self.deployment_one = mommy.make_one('catamidb.Deployment',
            start_position=Point(12.4604, 43.9420),
            end_position=Point(12.4604, 43.9420),
            transect_shape=Polygon(((0.0, 0.0), (0.0, 50.0), (50.0, 50.0), (50.0, 0.0), (0.0, 0.0))),
            id=1,
            campaign=self.campaign_one
        )
    self.deployment_two = mommy.make_one('catamidb.Deployment',
            start_position=Point(12.4604, 43.9420),
            end_position=Point(12.4604, 43.9420),
            transect_shape=Polygon(((0.0, 0.0), (0.0, 50.0), (50.0, 50.0), (50.0, 0.0), (0.0, 0.0))),
            id=2,
            campaign=self.campaign_one
        )

    self.pose_one = mommy.make_one('catamidb.Pose',
            position=Point(12.4, 23.5),
            id=1,
            deployment=self.deployment_one
        )
    self.pose_two = mommy.make_one('catamidb.Pose',
            position=Point(12.4, 23.5),
            id=2,
            deployment=self.deployment_two
        )
        
    self.camera_one = mommy.make_one('catamidb.Camera',
            deployment=self.deployment_one,
            id=1,
        )
    self.camera_two = mommy.make_one('catamidb.Camera',
            deployment=self.deployment_two,
            id=2,
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
            camera=self.camera_two,
            web_location=self.image_list[1],
            pk=2
        )

class TestCollectionModel(TestCase):

    def setUp(self):
        create_setup(self)
        self.user = User.objects.create_user("Joe")
        self.collection_name = "Joe's Collection"
        self.collection_manager = CollectionManager()

    def test_collection_from_deployment(self):
        #create a collection
        self.collection_manager.collection_from_deployment(self.user, self.deployment_one)

        #check it got created
        collection = Collection.objects.get(name=self.deployment_one.short_name)
        self.assertIsInstance(collection, Collection)

        #check that the user and details were assigned
        self.assertEqual(collection.owner, self.user)
        self.assertEqual(collection.is_public, True)
        self.assertEqual(collection.is_locked, True)

        #check the images went across - IMPORTANT!
        #get images for the deployment and the collection
        collection_images = collection.images.all().order_by("web_location")
        deployment_images = Image.objects.filter(pose__deployment=self.deployment_one).order_by("web_location")

        #check the image set is the same
        self.assertEqual(collection_images.values_list("web_location").__str__(),
                         deployment_images.values_list("web_location").__str__())

        #try create with no user, should be an error
        try:
            self.collection_manager.collection_from_deployment(None, self.deployment_one)
        except Exception:
            self.assertTrue(True)

        #try create with no deployment
        try:
            self.collection_manager.collection_from_deployment(self.user, None)
        except Exception:
            self.assertTrue(True)

    def test_collection_from_deployments_with_name(self):
        #create the list of deployment ids to create a collection from
        deployment_ids = self.deployment_one.id.__str__() + ',' + self.deployment_two.id.__str__()

        #create a collection
        self.collection_manager.collection_from_deployments_with_name(self.user, self.collection_name, deployment_ids.__str__())

        #check it got created
        collection = Collection.objects.get(name=self.collection_name)
        self.assertIsInstance(collection, Collection)

        #check that the user and details were assigned
        self.assertEqual(collection.owner, self.user)
        self.assertEqual(collection.is_public, False)
        self.assertEqual(collection.is_locked, True)

        #check the images went across - IMPORTANT!
        #get images for the deployment and the collection
        collection_images = collection.images.all().order_by("web_location")
        deployment_one_images = Image.objects.filter(pose__deployment=self.deployment_one).order_by("web_location")
        deployment_two_images = Image.objects.filter(pose__deployment=self.deployment_two).order_by("web_location")

        #check that combined lengths of the deployment images is the same as the collection
        self.assertEqual(collection_images.count(), deployment_one_images.count()+deployment_two_images.count())

        #check that the collection contains all the images from both deployments
        for image in deployment_one_images:
            self.assertIsNotNone(collection_images.filter(id=image.id))

        for image in deployment_two_images:
            self.assertIsNotNone(collection_images.filter(id=image.id))

        #try create with no user, should be an error
        try:
            self.collection_manager.collection_from_deployment(None, self.collection_name, deployment_ids.__str__())
        except Exception:
            self.assertTrue(True)

        #try create with no name
        try:
            self.collection_manager.collection_from_deployment(self.user, None, deployment_ids.__str__())
        except Exception:
            self.assertTrue(True)

        #try create with no deployments
        try:
            self.collection_manager.collection_from_deployment(self.user, self.collection_name, "")
        except Exception:
            self.assertTrue(True)

        #try create collection with duplicate name
        try:
            self.collection_manager.collection_from_deployments_with_name(self.user, self.collection_name, deployment_ids.__str__())
        except Exception:
            self.assertTrue(True)

class TestCollectionAPI(TestCase):

    def set_up(self):
        create_setup(self)
        self.collection_one = mommy.make_one("collections.Collection")
        self.user = User.objects.create_user("Joe")
        self.collection_manager = CollectionManager()

    def test_get_all_camapaigns(self):
        api_url = "/api/dev/campaign/?format=json&campaign="

    def test_get_deployements_for_given_campaign(self):
        api_url = "/api/dev/deployment/?format=json"

    def test_get_paginated_images_for_campaign(self):
        api_url = "/api/dev/image/?limit=30&campaign="

    def test_get_paginated_images_for_deployment(self):
        api_url = "/api/dev/image/?limit=30&deployment="

    def test_get_paginated_images_for_collection(self):
        api_url = "/api/dev/image/?limit=30&collection="
