"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.core.urlresolvers import reverse

from django.core.exceptions import ValidationError

from django.core.serializers.base import DeserializationError

from django.contrib.auth.models import User

from django.forms import FloatField, TextInput

from .auvimport import LimitTracker
from . import tasks
from . import widgets
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
        test_urls.append((reverse('staging_campaign_create'), 'staging/campaigncreate.html'))
        test_urls.append((reverse('staging_campaign_created'), 'staging/campaigncreated.html'))
        test_urls.append((reverse('staging_auv_import'), 'staging/auvimport.html'))
        test_urls.append((reverse('staging_auv_import_manual'), 'staging/auvmanualimport.html'))
        test_urls.append((reverse('staging_auv_imported'), 'staging/auvimported.html'))
        test_urls.append((reverse('staging_file_import'), 'staging/fileupload.html'))
        test_urls.append((reverse('staging_file_imported'), 'staging/fileuploaded.html'))
        test_urls.append((reverse('staging_file_imported'), 'staging/fileuploaded.html'))
        test_urls.append((reverse('staging_metadata_stage'), 'staging/metadatastage.html'))
        test_urls.append((reverse('staging_metadata_list'), 'staging/metadatalist.html'))

        for test_url, template in test_urls:
            response = self.client.get(test_url)
            # check you can get them all
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, template)
            self.assertTemplateUsed(response, 'staging/base.html')

        # logout, don't check carefully, the other test does that
        response = self.client.get('/accounts/logout/')


class JSONImport(TestCase):
    """Test the JSON importing."""

    def test_json_fload_protection(self):
        non_force_file_name = "staging/fixtures/non_force_model.json"
        invalid_model_file_name = "staging/fixtures/invalid_model.json"
        invalid_file_name = "staging/fixtures/klsdfkldfskldf.json"

        self.assertRaises(ValueError, tasks.json_fload, non_force_file_name)
        self.assertRaises(DeserializationError, tasks.json_fload, invalid_model_file_name)
        self.assertRaises(IOError, tasks.json_fload, invalid_file_name)


class AUVImportTools(TestCase):
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

        # the final (odd) cases
        # should throw error... or silently ignore?

        # using a dict, but give it a value
        self.assertRaises(TypeError, dict_value_track.check, (20.0))
        # or a dict with the wrong key
        dict_value_track.check({'other': -20.0})

        self.assertEqual(dict_value_track.maximum, 10.0)
        self.assertEqual(dict_value_track.minimum, -10.0)

        # using a value but give it a dict
        self.assertRaises(TypeError, direct_track.check, ({'val': 20.0}))

        self.assertEqual(direct_track.minimum, -10.0)
        self.assertEqual(direct_track.maximum, 10.0)

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


class MetadataImport(TestCase):
    """Tests the metadata tasks."""

    def setUp(self):
        """Set the names of the metadata files to test with."""
        self.xls_file_name = "staging/fixtures/bruv_metadata.xls"
        self.xlsx_file_name = "staging/fixtures/bruv_metadata.xlsx"
        self.xls_sheet_names = [u"Offshore BRUVS Co-ord",
            u"Inshore BRUVS co-ord", u"BRUVS Lengths", u"BRUVS MaxN"]
        self.xlsx_sheet_names = [u"Offshore BRUVS Co-ord",
            u"Inshore BRUVS co-ord", u"BRUVS Lengths", u"BRUVS MaxN"]

    def test_type_recognition(self):
        """Test type recognition with the files."""

        self.assertEqual("xls", tasks.metadata_type(self.xls_file_name))
        self.assertEqual("xlsx", tasks.metadata_type(self.xlsx_file_name))

    def test_sheet_names(self):
        """Test that sheet names are correctly extracted."""

        self.assertEqual(self.xls_sheet_names, tasks.metadata_sheet_names(self.xls_file_name))
        self.assertEqual(self.xlsx_sheet_names, tasks.metadata_sheet_names(self.xlsx_file_name))

    def test_outline(self):
        """Test that the outlines work correctly."""
        self.assertIsNotNone(tasks.metadata_outline(self.xls_file_name))
        self.assertIsNotNone(tasks.metadata_outline(self.xlsx_file_name))

    def test_transform(self):
        self.assertIsNotNone(tasks.metadata_transform(self.xls_file_name, self.xls_sheet_names[0]))
        self.assertIsNotNone(tasks.metadata_transform(self.xlsx_file_name, self.xlsx_sheet_names[0]))


class WidgetTest(TestCase):
    """Tests the multi-value widgets that were created."""

    def test_point_widget_field(self):
        """Test the PointField and PointWidget."""
        point_widget = widgets.PointWidget()
        point_value = widgets.PointField()

        # invalid strings
        self.assertEqual([None, None], point_widget.decompress(None))
        self.assertEqual([None, None], point_widget.decompress(""))
        self.assertEqual([None, None], point_widget.decompress("a string"))
        self.assertEqual([None, None], point_widget.decompress("1.5456 6.23345"))
        self.assertEqual([None, None], point_widget.decompress("POINT(5.6, 36.3)"))
        self.assertEqual([None, None], point_widget.decompress("POINT(5.636.3)"))
        self.assertEqual([None, None], point_widget.decompress("POINT(5.6363)"))

        # valid strings
        self.assertEqual([1.5, 2.5], point_widget.decompress("POINT(2.5 1.5)"))
        self.assertEqual([1.5, 2.5], point_widget.decompress("POINT     (2.5 1.5)"))
        self.assertEqual([1.5, 2.5], point_widget.decompress("POINT ( 2.5   1.5  )"))

        self.assertEqual([-1.5, 2.5], point_widget.decompress("POINT(+2.5 -1.5)"))
        self.assertEqual([-1.5, 2.5], point_widget.decompress("POINT     ( 2.5 -1.5)"))

        # empty value
        self.assertIsNone(point_value.compress(None))

        # actual values
        self.assertEqual("POINT(2.0 2.0)", point_value.compress([2.0, 2.0]))
        self.assertEqual("POINT(4.5 4.5)", point_value.compress([4.5, 4.5]))
        self.assertEqual("POINT(8.25 8.25)", point_value.compress([8.25, 8.25]))
        self.assertEqual("POINT(-8.25 4.25)", point_value.compress([4.25, -8.25]))
        self.assertEqual("POINT(1.25 -8.25)", point_value.compress([-8.25, 1.25]))

        # check exceptions
        self.assertRaises(ValidationError, point_value.compress, [None, 4.5])
        self.assertRaises(ValidationError, point_value.compress, [4.5, None])

        # now check the compress and decompress work together as expected
        values = [[1.5, 1.5], [2.0, 1.5], [1.0, 10.0], [-10.0, 5.0]]

        for value in values:
            self.assertEqual(value, point_widget.decompress(point_value.compress(value)))

    def test_extract_single_column(self):
        """Test the utility used to wrap data chunks in the multi fields/widgets."""
        columns = {'first': '1.0', 'second': '2.0', 'third': '3.0'}
        base_field = FloatField()  # the field this is all based on
        source = 'fixed'  # 'fixed' or 'column' depending on source sub widget
        labels = ['first']  # the column label selected
        fixed_data = 4.5  # the fixed data entered (post cleaning)

        extractor = widgets.ExtractData(base_field, source, labels, fixed_data)

        decompressed = [source, labels, fixed_data]
        self.assertEqual(extractor.decompress(), decompressed)

        self.assertEqual(extractor.get_data(columns), 4.5)
        extractor.source = 'columns'
        self.assertEqual(extractor.get_data(columns), 1.0)

    def test_extract_multiple_columns(self):
        """Test the utility used to wrap data chunks in the multi fields/widgets."""
        columns = {'first': '1.0', 'second': '2.0', 'third': '3.0'}
        base_field = widgets.PointField()  # the field this is all based on
        source = 'fixed'  # 'fixed' or 'column' depending on source sub widget
        labels = ['first', 'third']  # the column label selected
        fixed_data = "POINT(1.0 2.0)"  # the fixed data entered (post cleaning)
        cleaned_data = "POINT(3.0 1.0)"  # the fixed data entered (post cleaning)

        extractor = widgets.ExtractData(base_field, source, labels, fixed_data)

        decompressed = [source, labels, fixed_data]
        self.assertEqual(extractor.decompress(), decompressed)

        self.assertEqual(extractor.get_data(columns), fixed_data)
        extractor.source = 'columns'
        self.assertEqual(extractor.get_data(columns), cleaned_data)

    def test_multiple_source_field(self):
        """Tests the MultiSourceField."""

        base_field = FloatField()
        headings = ['first', 'second', 'third', 'fourth']
        choices = zip(headings, headings)
        field = widgets.MultiSourceField(base_field=base_field, columns=choices)

        # test a full working instance
        data = ['fixed', 'first', 4.5]
        ex = field.compress(data)

        # check the compressed matches expected
        self.assertEqual(ex.source, data[0])
        self.assertEqual(ex.fixed_data, data[2])
        self.assertEqual(ex.column_labels, data[1])

        # test partial working instance
        data = ['column', 'column_name', None]
        field.compress(data)

        data = ['fixed', None, 4.5]
        field.compress(data)

        # test completely empty instance
        self.assertIsNone(field.compress(None))

        # now test error inducing variations
        data = ['fixed', 'column_name', None]
        self.assertRaises(ValidationError, field.compress, data)

        data = ['column', None, 4.5]
        self.assertRaises(ValidationError, field.compress, data)

        data = [None, 'column_name', 4.5]
        self.assertRaises(ValidationError, field.compress, data)

    def test_multiple_column_field(self):
        """Tests the MultiColumnField."""

        # common elements
        headings = ['first', 'second', 'third']
        columns = zip(headings, headings)

        # simplest case, single column
        base_field = FloatField()
        base_widget = base_field.widget
        widget = widgets.MultiColumnWidget(base_widget)
        field = widgets.MultiColumnField(base_field, columns, widget=widget)

        # now test the compress routine
        self.assertIsNone(field.compress(None))
        data = ["first"]
        self.assertEqual(field.compress(data), data)
        self.assertRaises(ValidationError, field.compress, [None])

        # more complex, multiple column
        base_field = widgets.PointField()
        base_widget = base_field.widget
        widget = widgets.MultiColumnWidget(base_widget)
        field = widgets.MultiColumnField(base_field, columns, widget=widget)

        # now test the compress routine
        self.assertIsNone(field.compress(None))
        data = ["first", "second"]
        self.assertEqual(field.compress(data), data)
        self.assertRaises(ValidationError, field.compress, [None, None])
        self.assertRaises(ValidationError, field.compress, [None, "second"])
        self.assertRaises(ValidationError, field.compress, ["first", None])
        self.assertRaises(ValidationError, field.compress, ["only"])

        # error inducing
        base_field = widgets.PointWidget()
        base_widget = None
        self.assertRaises(Exception, widgets.MultiColumnField, base_field, columns, widget=widget)

    def test_multi_column_widget(self):
        """Test initialise and decompress of MultiColumnWidget."""
        base_widget = widgets.PointWidget()
        widget = widgets.MultiColumnWidget(base_widget)

        self.assertEqual(widget.decompress(None), [None] * 2)
        data = ["first", "second"]
        self.assertEqual(widget.decompress(data), data)

        base_widget = TextInput()
        widget = widgets.MultiColumnWidget(base_widget)
        self.assertEqual(widget.decompress(None), [None])
        data = ["first"]
        self.assertEqual(widget.decompress(data), data)

    def test_widget_rendering(self):
        """A generic test to make sure the custom widgets render."""

        # also test the MultiSourceWidget decompress paths

        # single column
        base_field = FloatField()
        headings = ['first', 'second', 'third', 'fourth']
        choices = zip(headings, headings)
        field = widgets.MultiSourceField(base_field=base_field, columns=choices)
        widget = field.widget
        widget.render("widget_name", ["fixed", headings[0], 4.3], {'id': 'name'})
        widget.render("widget_name", widgets.ExtractData(base_field, *["fixed", headings[0], 4.2]))

        self.assertEqual(widget.decompress(None), ["column", [None], None])

        # multi column
        base_field = widgets.PointField()
        field = widgets.MultiSourceField(base_field=base_field, columns=choices)
        widget = field.widget
        widget.render("widget_name", widgets.ExtractData(base_field, *["fixed", headings[0], "POINT(2.0 1.0)"]), {'id': 'name'})
        widget.render("widget_name", widgets.ExtractData(base_field, *["fixed", headings[0], "POINT(2.0 1.0)"]))

        self.assertEqual(widget.decompress(None), ["column", [None] * 2, None])


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

        base_url = "http://df.arcs.org.au/ARCS/projects/IMOS/public/AUV"
        campaign_name = campaign.short_name
        campaign_start = campaign.date_start
        mission_name = "r20090611_063540_freycinet_mpa_03_reef_south"
        self.input_params = (base_url, str(campaign_start), campaign_name, mission_name)

    def test_auv_fetch_names(self):
        """Test auv_fetch name generation."""

        # call the function we are testing
        return_values = tasks.auvfetch(*self.input_params)

        # break out the return values
        track_url, netcdf_urlpattern, start_time = return_values

        # calculate the values to compare against, and compare them
        files_base = "{0}/{2}/{3}".format(*self.input_params)
        self.assertEqual(track_url[0], files_base + "/track_files/freycinet_mpa_03_reef_south_latlong.csv")
        self.assertEqual(netcdf_urlpattern, files_base + "/hydro_netcdf/IMOS_AUV_ST_{date_string}Z_SIRIUS_FV00.nc")
        self.assertEqual(start_time, datetime.datetime(2009, 06, 11, 6, 35, 40, tzinfo=tzutc()))

    def test_auv_process(self):
        """Test auv_process importing."""

        track_file = open('staging/fixtures/freycinet_mpa_03_reef_south_latlong.csv', 'r')
        netcdf_file = open('staging/fixtures/IMOS_AUV_ST_20090611T063544Z_SIRIUS_FV00.nc', 'r')
        json_string = tasks.auvprocess(track_file, netcdf_file, *self.input_params)

        tasks.json_sload(json_string)
