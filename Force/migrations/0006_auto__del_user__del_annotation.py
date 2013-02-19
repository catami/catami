# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'User'
        db.delete_table('Force_user')

        # Deleting model 'Annotation'
        db.delete_table('Force_annotation')


    def backwards(self, orm):
        # Adding model 'User'
        db.create_table('Force_user', (
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('organisation', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
        ))
        db.send_create_signal('Force', ['User'])

        # Adding model 'Annotation'
        db.create_table('Force_annotation', (
            ('code', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('user_who_annotated', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['Force.User'])),
            ('image_reference', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['Force.Image'])),
            ('point', self.gf('django.contrib.gis.db.models.fields.PointField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('comments', self.gf('django.db.models.fields.TextField')()),
            ('method', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('Force', ['Annotation'])


    models = {
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
        }
    }

    complete_apps = ['Force']