"""Unit tests for the administratorbot
"""

from django.test import TestCase
from model_mommy import mommy
import dbadmintool.administratorbot as administratorbot
from django.contrib.gis.geos import Point

from django.test.client import RequestFactory


class DatabaseTest(TestCase):
    """Tests for checking the database administratorbot"""

    #fixtures = ['data.json', ]

    def setUp(self):
        """Set up the defaults for the test"""
        self.bender = administratorbot.Robot()
        self.april = administratorbot.ReportTools()

        #==========
        # Mommy fixture
        #==========
        self.image_list = ['/live/test/test2.jpg', '/live/test/test1.jpg']
        self.campaign_01 = mommy.make_one('Force.Campaign', id=1)

        self.deployment_one = mommy.make_one('Force.Deployment',
            start_position=Point(12.4604, 43.9420),campaign=self.campaign_01,
            id=1)
        self.mock_image = mommy.make_one('Force.Image', deployment=self.
            deployment_one, left_image_reference=self.image_list[0],
            image_position=Point(12.4604, 43.9420), pk=1)

        self.dummy_dep1 = mommy.make_recipe('dbadmintool.auvdeployment', id=3,
            campaign=self.campaign_01)
        self.dummy_dep2 = mommy.make_recipe('dbadmintool.bruvdeployment', id=4,
            campaign=self.campaign_01)
        self.dummy_dep3 = mommy.make_recipe('dbadmintool.dovdeployment', id=5,
            campaign=self.campaign_01)
        self.dummy_dep4 = mommy.make_recipe('dbadmintool.tvdeployment', id=6,
            campaign=self.campaign_01)
        self.dummy_dep5 = mommy.make_recipe('dbadmintool.tideployment', id=7,
            campaign=self.campaign_01)

    def test_check_database_connection(self):
        """Test that administratorbot returns True if open connection and

        False if no connection is found
        """

        # The unt test database is called default.see if we can get a
        # connection
        self.assertTrue(self.bender.check_database_connection(
            dbname='default'))

        # Now check that we get a logical return if we cannot connect
        self.assertFalse(self.bender.check_database_connection(
            dbname='nodatabase'))

    def test_make_local_backup(self):
        self.assertTrue(self.bender.make_local_backup())
        self.assertTrue(self.bender.make_local_backup(do_zip=False))
        self.assertFalse(self.bender.make_local_backup(do_zip=False,
            unit_test='corrupt'))
        self.assertFalse(self.bender.make_local_backup(unit_test='corrupt'))

    def test_collect_db_stats(self):
        # Load some data to count
        self.assertTrue(self.april.collect_number_of_fields())
        self.assertTrue(self.april.collect_stats())
        self.assertTrue(isinstance(self.april.query_database_size(), int))
        self.assertTrue(isinstance(self.april.query_table_size(), list))

    #def test_db_stats_view(self):
        #response = self.client.get("/report/")

