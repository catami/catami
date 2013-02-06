# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Image.pitch'
        db.delete_column('Force_image', 'pitch')

        # Deleting field 'Image.yaw'
        db.delete_column('Force_image', 'yaw')

        # Deleting field 'Image.temperature'
        db.delete_column('Force_image', 'temperature')

        # Deleting field 'Image.altitude'
        db.delete_column('Force_image', 'altitude')

        # Deleting field 'Image.salinity'
        db.delete_column('Force_image', 'salinity')

        # Deleting field 'Image.roll'
        db.delete_column('Force_image', 'roll')


    def backwards(self, orm):

        # User chose to not deal with backwards NULL issues for 'Image.pitch'
        raise RuntimeError("Cannot reverse this migration. 'Image.pitch' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'Image.yaw'
        raise RuntimeError("Cannot reverse this migration. 'Image.yaw' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'Image.temperature'
        raise RuntimeError("Cannot reverse this migration. 'Image.temperature' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'Image.altitude'
        raise RuntimeError("Cannot reverse this migration. 'Image.altitude' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'Image.salinity'
        raise RuntimeError("Cannot reverse this migration. 'Image.salinity' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'Image.roll'
        raise RuntimeError("Cannot reverse this migration. 'Image.roll' and its values cannot be restored.")

    models = {
        'Force.annotation': {
            'Meta': {'object_name': 'Annotation'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'comments': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image_reference': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['Force.Image']"}),
            'method': ('django.db.models.fields.TextField', [], {}),
            'point': ('django.contrib.gis.db.models.fields.PointField', [], {}),
            'user_who_annotated': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['Force.User']"})
        },
        'Force.auvdeployment': {
            'Meta': {'object_name': 'AUVDeployment', '_ormbases': ['Force.Deployment']},
            'deployment_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['Force.Deployment']", 'unique': 'True', 'primary_key': 'True'}),
            'distance_covered': ('django.db.models.fields.FloatField', [], {}),
            'transect_shape': ('django.contrib.gis.db.models.fields.PolygonField', [], {})
        },
        'Force.bruvdeployment': {
            'Meta': {'object_name': 'BRUVDeployment', '_ormbases': ['Force.Deployment']},
            'deployment_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['Force.Deployment']", 'unique': 'True', 'primary_key': 'True'})
        },
        'Force.campaign': {
            'Meta': {'unique_together': "(('date_start', 'short_name'),)", 'object_name': 'Campaign'},
            'associated_publications': ('django.db.models.fields.TextField', [], {}),
            'associated_research_grant': ('django.db.models.fields.TextField', [], {}),
            'associated_researchers': ('django.db.models.fields.TextField', [], {}),
            'contact_person': ('django.db.models.fields.TextField', [], {}),
            'date_end': ('django.db.models.fields.DateField', [], {}),
            'date_start': ('django.db.models.fields.DateField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'Force.deployment': {
            'Meta': {'unique_together': "(('start_time_stamp', 'short_name'),)", 'object_name': 'Deployment'},
            'campaign': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['Force.Campaign']"}),
            'contact_person': ('django.db.models.fields.TextField', [], {}),
            'descriptive_keywords': ('django.db.models.fields.TextField', [], {}),
            'end_time_stamp': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'license': ('django.db.models.fields.TextField', [], {}),
            'max_depth': ('django.db.models.fields.FloatField', [], {}),
            'min_depth': ('django.db.models.fields.FloatField', [], {}),
            'mission_aim': ('django.db.models.fields.TextField', [], {}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'start_position': ('django.contrib.gis.db.models.fields.PointField', [], {}),
            'start_time_stamp': ('django.db.models.fields.DateTimeField', [], {})
        },
        'Force.dovdeployment': {
            'Meta': {'object_name': 'DOVDeployment', '_ormbases': ['Force.Deployment']},
            'deployment_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['Force.Deployment']", 'unique': 'True', 'primary_key': 'True'}),
            'diver_name': ('django.db.models.fields.TextField', [], {})
        },
        'Force.image': {
            'Meta': {'unique_together': "(('deployment', 'date_time'),)", 'object_name': 'Image'},
            'date_time': ('django.db.models.fields.DateTimeField', [], {}),
            'deployment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['Force.Deployment']"}),
            'depth': ('django.db.models.fields.FloatField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image_position': ('django.contrib.gis.db.models.fields.PointField', [], {}),
            'left_image_reference': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'left_thumbnail_reference': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        'Force.scientificmeasurement': {
            'Meta': {'unique_together': "(('measurement_type', 'image'),)", 'object_name': 'ScientificMeasurement'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['Force.Image']"}),
            'measurement_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['Force.ScientificMeasurementType']"}),
            'value': ('django.db.models.fields.FloatField', [], {})
        },
        'Force.scientificmeasurementtype': {
            'Meta': {'object_name': 'ScientificMeasurementType'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'display_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_value': ('django.db.models.fields.FloatField', [], {}),
            'min_value': ('django.db.models.fields.FloatField', [], {}),
            'normalised_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'units': ('django.db.models.fields.CharField', [], {'max_length': '5'})
        },
        'Force.stereoimage': {
            'Meta': {'object_name': 'StereoImage', '_ormbases': ['Force.Image']},
            'image_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['Force.Image']", 'unique': 'True', 'primary_key': 'True'}),
            'right_image_reference': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'right_thumbnail_reference': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        'Force.tideployment': {
            'Meta': {'object_name': 'TIDeployment', '_ormbases': ['Force.Deployment']},
            'deployment_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['Force.Deployment']", 'unique': 'True', 'primary_key': 'True'})
        },
        'Force.tvdeployment': {
            'Meta': {'object_name': 'TVDeployment', '_ormbases': ['Force.Deployment']},
            'deployment_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['Force.Deployment']", 'unique': 'True', 'primary_key': 'True'})
        },
        'Force.user': {
            'Meta': {'object_name': 'User'},
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'organisation': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['Force']