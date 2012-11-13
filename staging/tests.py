"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.core.urlresolvers import reverse

from django.contrib.auth.models import User

from .auvimport import LimitTracker
from . import tasks

from Force.models import Campaign

import datetime


def setup_login(self):
    # create a testing user
    self.username = 'testing'
    self.email = 'testing@example.com'
    self.password = User.objects.make_random_password()
    self.login = {'username': self.username, 'password': self.password}

    self.login_url = '/accounts/login/?next='

    # this creates the testing user and saves it
    self.user = User.objects.create_user(self.username, self.email, self.password)


class StagingTests(TestCase):
    """Tests for the staging application."""

    def setUp(self):
        """Set up the test variables/parameters."""
        setup_login(self)

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
        test_urls.append(reverse('staging_metadata_book_update_public'))
        test_urls.append(reverse('staging_metadata_book', args=['0']))
        test_urls.append(reverse('staging_metadata_delete', args=['0']))
        test_urls.append(reverse('staging_metadata_sheet', args=['0', 'name']))
        test_urls.append(reverse('staging_metadata_import', args=['0', 'name', 'model']))
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
        test_urls.append((reverse('staging_index'), 'staging/index.html'))
        test_urls.append((reverse('staging_auv_import'), 'staging/auvimport.html'))
        test_urls.append((reverse('staging_auv_imported'), 'staging/auvimported.html'))
        test_urls.append((reverse('staging_file_import'), 'staging/fileupload.html'))
        test_urls.append((reverse('staging_file_imported'), 'staging/fileuploaded.html'))

        for test_url, template in test_urls:
            response = self.client.get(test_url)
            # check you can get them all
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, template)
            self.assertTemplateUsed(response, 'staging/base.html')

        # logout, don't check carefully, the other test does that
        response = self.client.get('/accounts/logout/')

    def test_limit_tracker(self):
        """Test LimitTracker used in auvimport."""

        # check direct values
        direct_track = LimitTracker()

        direct_track.check(1.0)

        self.assertEqual(direct_track.minimum, 1.0)
        self.assertEqual(direct_track.maximum, 1.0)

        direct_track.check(10.0)
        direct_track.check(-10.0)

        self.assertEqual(direct_track.minimum, -10.0)
        self.assertEqual(direct_track.maximum, 10.0)

        # check values in a dictionary
        dict_value_track = LimitTracker('val')

        dict_value_track.check({'val': 1.0})

        self.assertEqual(dict_value_track.minimum, 1.0)

        dict_value_track.check({'val': 10.0})
        dict_value_track.check({'val': -10.0})

        self.assertEqual(dict_value_track.maximum, 10.0)
        self.assertEqual(dict_value_track.minimum, -10.0)


class StagingNetworkTests(TestCase):
    """Tests for Staging that require the internet to access things."""

    def setUp(self):
        """Set up the test variables/parameters."""
        setup_login(self)

    def test_auv_import(self):
        """Test AUV importing."""
        # here we don't want to go downloading, we are testing file name
        # construction and correct results from a known 'mission'

        # create a campaign
        campaign = Campaign()
        campaign.short_name = "Tasmania201106"
        campaign.description = "IMOS Repeat Survey"
        campaign.associated_researchers = "ACFR, UTas"
        campaign.associated_publications = "Pending"
        campaign.associated_research_grant = "Pending"
        campaign.date_start = datetime.date(2011, 6, 1)
        campaign.date_end = datetime.date(2011, 6, 30)

        campaign.save()

        # now load data into it
        base_url = "http://df.arcs.org.au/ARCS/projects/IMOS/public/AUV/"
        campaign_name = campaign.short_name
        campaign_start = campaign.date_start
        mission_name = "r20110614_055332_flindersCMRnorth_09_canyongrids"

        input_params = (base_url, str(campaign_start), campaign_name, mission_name)

        track_key = "track_key"
        netcdf_key = "netcdf_key"

        return_values = tasks.auvfetch(*input_params)
        track_url, netcdf_urlpattern, start_time = return_values

        track_file = tasks.get_known_file(track_key, track_url)
        netcdf_file = tasks.get_netcdf_file(netcdf_key, netcdf_urlpattern, start_time)
        json_string = tasks.auvprocess(track_file, netcdf_file, *input_params)

        tasks.json_sload(json_string)

        # we are done once we reach this point
        # if done without error... of course
        # should query this once a few parameters of the mission are known
