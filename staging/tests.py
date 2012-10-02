"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.core.urlresolvers import reverse


class StagingTests(TestCase):
    def test_loginprotection(self):
        """
        Test that the core pages can be accessed.
        """

        # the index
        response = self.client.get(reverse('staging_index'))
        self.assertEqual(response.status_code, 302) # get /
        # this requires us to login
        # so now login

        # the auv import pages
        response = self.client.get(reverse('staging_auv_import'))
        self.assertEqual(response.status_code, 302) # get /auv/import

        response = self.client.get(reverse('staging_auv_imported'))
        self.assertEqual(response.status_code, 302) # get /auv/imported

        # the file upload pages
        response = self.client.get(reverse('staging_file_import'))
        self.assertEqual(response.status_code, 302) # get /file/import

        response = self.client.get(reverse('staging_file_imported'))
        self.assertEqual(response.status_code, 302) # get /file/imported
