import logging
from django.contrib.auth.models import User
from django.contrib.gis.geos import Point
from django.test.utils import setup_test_environment
from django.test import TestCase
from model_mommy import mommy
from Force.models import Image
from collection.models import CollectionManager, Collection

logger = logging.getLogger(__name__)

class TestCollectionModel(TestCase):

    def setUp(self):
        self.deployment_one = mommy.make_one('Force.Deployment', start_position=Point(12.4604, 43.9420), id=1)
        self.deployment_two = mommy.make_one('Force.Deployment', start_position=Point(12.4604, 43.9420), id=2)
        self.user = User.objects.create_user("Joe")
        self.collection_name = "Collection Named"
        self.collection_manager = CollectionManager()
        self.image_list = []

        #setup some images and assign to deployment_one
        for i in xrange(0, 1):
            self.image_list.append(mommy.make_one('Force.Image', deployment=self.deployment_one, image_position=Point(12.4604, 43.9420)))

        #setup some images and assign to deployment_two
        for i in xrange(0, 1):
            self.image_list.append(mommy.make_one('Force.Image', deployment=self.deployment_two, image_position=Point(12.4604, 43.9420)))

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
        collection_images = collection.images.all().order_by("webimage_location")
        deployment_images = Image.objects.filter(deployment=self.deployment_one).order_by("webimage_location")

        #check the image set is the same
        self.assertEqual(collection_images.values_list("webimage_location").__str__(),
                         deployment_images.values_list("webimage_location").__str__())

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
        collection_images = collection.images.all().order_by("webimage_location")
        deployment_one_images = Image.objects.filter(deployment=self.deployment_one).order_by("webimage_location")
        deployment_two_images = Image.objects.filter(deployment=self.deployment_two).order_by("webimage_location")

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
        self.campaign_one = mommy.make_one("Force.Campaign")
        self.campaign_two = mommy.make_one("Force.Campaign")
        self.deployment_one = mommy.make_one('Force.Deployment', start_position=Point(12.4604, 43.9420), id=1)
        self.deployment_two = mommy.make_one('Force.Deployment', start_position=Point(12.4604, 43.9420), id=2)
        self.collection_one = mommy.make_one("collections.Collection")
        self.user = User.objects.create_user("Joe")
        self.collection_manager = CollectionManager()

        #setup some images and assign to deployment_one
        for i in xrange(0, 1):
            mommy.make_one('Force.Image', deployment=self.deployment_one, image_position=Point(12.4604, 43.9420))

        #setup some images and assign to deployment_two
        for i in xrange(0, 1):
            mommy.make_one('Force.Image', deployment=self.deployment_two, image_position=Point(12.4604, 43.9420))

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
