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
from .annotations import CPCFileParser

from Force.models import Campaign

import datetime
from dateutil.tz import tzutc


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


class AUVImportTests(TestCase):
    """Test the components in auvimport.py."""

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

    def test_cpc_importer(self):
        """Test CPCFileParser used in annotation import."""
        cpc_file = open('staging/fixtures/cpctest.cpc')

        parser = CPCFileParser(cpc_file)

        # check it has the correct image name
        self.assertEqual('PR_20090611_072239_528_LC16', parser.image_file_name)

        # and the right number of points
        data = [row for row in parser]

        self.assertEqual(55, len(data))

        self.assertEqual(data[0]['label'], "ID")
        self.assertEqual(data[1]['label'], "RUG")


class AUVImport(TestCase):
    """Tests for Staging that require the internet to access things."""

    def setUp(self):
        """Set up the test variables/parameters."""
        setup_login(self)

        # create a campaign
        campaign = Campaign()
        campaign.short_name = "Tasmania200906"
        campaign.description = "IMOS Repeat Survey"
        campaign.associated_researchers = "ACFR, UTas"
        campaign.associated_publications = "Pending"
        campaign.associated_research_grant = "Pending"
        campaign.date_start = datetime.date(2009, 6, 1)
        campaign.date_end = datetime.date(2009, 6, 30)

        campaign.save()

        self.campaign = campaign

    def test_auv_fetch_names(self):
        """Test auv_fetch name generation."""
        # now load data into it
        base_url = "http://df.arcs.org.au/ARCS/projects/IMOS/public/AUV"
        campaign_name = self.campaign.short_name
        campaign_start = self.campaign.date_start
        mission_name = "r20090611_063540_freycinet_mpa_03_reef_south"

        self.input_params = (base_url, str(campaign_start), campaign_name, mission_name)

        return_values = tasks.auvfetch(*self.input_params)
        track_url, netcdf_urlpattern, start_time = return_values

        files_base = "{0}/{1}/{2}".format(base_url, campaign_name, mission_name)
        self.assertEqual(track_url[0], files_base + "/track_files/freycinet_mpa_03_reef_south_latlong.csv")
        self.assertEqual(netcdf_urlpattern, files_base + "/hydro_netcdf/IMOS_AUV_ST_{date_string}Z_SIRIUS_FV00.nc")
        self.assertEqual(start_time, datetime.datetime(2009, 06, 11, 6, 35, 40, tzinfo=tzutc()))

    def test_auv_process(self):
        """Test auv_process importing."""

        track_file = open('staging/fixtures/freycinet_mpa_03_reef_south_latlong.csv', 'r')
        nertcdf_file = open('staging/fixtures/IMOS_AUV_ST_20090611T063544Z_SIRIUS_FV00.nc', 'r')
        json_string = tasks.auvprocess(track_file, netcdf_file, *self.input_params)

        tasks.json_sload(json_string)
