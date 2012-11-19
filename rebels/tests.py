"""Unit tests for the administratorbot
"""

from django.test import TestCase
import rebels.administratorbot as administratorbot


class DatabaseTest(TestCase):
    """Tests for checking the database administratorbot"""

    def setUp(self):
        """Set up the defaults for the test"""
        self.bender = administratorbot.Robot()

    def test_check_database_connection(self):
        """Test that administratorbot returns True if open connection and

        False if no connection is found
        """

        # The unt test database is called default.see if we can get a connection
        self.assertTrue(self.bender.check_database_connection(
            dbname='default'))

        # Now check that we get a logical return if we cannot connect
        self.assertFalse(self.bender.check_database_connection(
            dbname='nodatabase'))

    def test_make_local_backup(self):
        self.assertTrue(self.bender.make_local_backup())
