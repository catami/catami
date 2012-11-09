"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.core.urlresolvers import reverse

from django.contrib.auth.models import User


class StagingTests(TestCase):
    """Tests for the staging application."""

    def setUp(self):
        """Set up the test variables/parameters."""
        # create a testing user
        self.username = 'testing'
        self.email = 'testing@example.com'
        self.password = User.objects.make_random_password()
        self.login = {'username': self.username, 'password': self.password}

        self.login_url = '/accounts/login/?next='

        # this creates the testing user and saves it
        self.user = User.objects.create_user(self.username, self.email, self.password)
    def test_loginprotection(self):
        """
        Test that the core pages can be accessed.
        """

        # the list of urls to check are protected
        test_urls = []
        test_urls.append(reverse('staging_index'))
        test_urls.append(reverse('staging_campaign_create'))
        test_urls.append(reverse('staging_campaign_created'))
        test_urls.append(reverse('staging_auv_import'))
        test_urls.append(reverse('staging_auv_import_manual'))
        test_urls.append(reverse('staging_auv_imported'))
        test_urls.append(reverse('staging_auv_progress'))
        test_urls.append(reverse('staging_file_import'))
        test_urls.append(reverse('staging_file_imported'))
        test_urls.append(reverse('staging_metadata_stage'))
        test_urls.append(reverse('staging_metadata_list'))
        test_urls.append(reverse('staging_metadata_book_update_public')) # requires ? parms
        test_urls.append(reverse('staging_metadata_book', args=['0'])) # file_id
        test_urls.append(reverse('staging_metadata_delete', args=['0'])) # file_id
        test_urls.append(reverse('staging_metadata_sheet', args=['0','name'])) # file_id, page_name
        test_urls.append(reverse('staging_metadata_import', args=['0','name','model'])) # file_id, page_name, model_name
        test_urls.append(reverse('staging_metadata_imported'))
        test_urls.append(reverse('staging_annotation_cpc_import'))
        test_urls.append(reverse('staging_annotation_cpc_imported'))

        # actually test each url
        for test_url in test_urls:
            response = self.client.get(test_url)
            self.assertRedirects(response, self.login_url + test_url)

    def test_login_and_logout(self):
        """Test that logging in and out can be done."""

        # redirect to staging index after login
        index_url = reverse('staging_index')
        response = self.client.post(self.login_url + index_url, self.login)
        self.assertRedirects(response, index_url)

        response = self.client.get('logout/')
        #self.assertRedirects(response, '/')

    def test_views_get(self):
        """Test getting the views (after login)."""
        # login, don't check carefully the other test does that
        response = self.client.post('/accounts/login/', self.login)

        test_urls = []
        test_urls.append((reverse('staging_index'),'staging/index.html'))
        test_urls.append((reverse('staging_auv_import'),'staging/auvimport.html'))
        test_urls.append((reverse('staging_auv_imported'),'staging/auvimported.html'))
        test_urls.append((reverse('staging_file_import'),'staging/fileupload.html'))
        test_urls.append((reverse('staging_file_imported'),'staging/fileuploaded.html'))

        for test_url, template in test_urls:
            response = self.client.get(test_url)
            # check you can get them all
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, template)
            self.assertTemplateUsed(response, 'staging/base.html')

        # logout, don't check carefully, the other test does that
        response = self.client.get('/accounts/logout/')

