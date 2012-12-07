# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Campaign'
        db.create_table('Force_campaign', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('short_name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('associated_researchers', self.gf('django.db.models.fields.TextField')()),
            ('associated_publications', self.gf('django.db.models.fields.TextField')()),
            ('associated_research_grant', self.gf('django.db.models.fields.TextField')()),
            ('date_start', self.gf('django.db.models.fields.DateField')()),
            ('date_end', self.gf('django.db.models.fields.DateField')()),
        ))
        db.send_create_signal('Force', ['Campaign'])

        # Adding unique constraint on 'Campaign', fields ['date_start', 'short_name']
        db.create_unique('Force_campaign', ['date_start', 'short_name'])

        # Adding model 'Deployment'
        db.create_table('Force_deployment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('start_position', self.gf('django.contrib.gis.db.models.fields.PointField')()),
            ('start_time_stamp', self.gf('django.db.models.fields.DateTimeField')()),
            ('end_time_stamp', self.gf('django.db.models.fields.DateTimeField')()),
            ('short_name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('mission_aim', self.gf('django.db.models.fields.TextField')()),
            ('min_depth', self.gf('django.db.models.fields.FloatField')()),
            ('max_depth', self.gf('django.db.models.fields.FloatField')()),
            ('campaign', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['Force.Campaign'])),
        ))
        db.send_create_signal('Force', ['Deployment'])

        # Adding unique constraint on 'Deployment', fields ['start_time_stamp', 'short_name']
        db.create_unique('Force_deployment', ['start_time_stamp', 'short_name'])

        # Adding model 'Image'
        db.create_table('Force_image', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('deployment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['Force.Deployment'])),
            ('left_thumbnail_reference', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('left_image_reference', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('date_time', self.gf('django.db.models.fields.DateTimeField')()),
            ('image_position', self.gf('django.contrib.gis.db.models.fields.PointField')()),
            ('temperature', self.gf('django.db.models.fields.FloatField')()),
            ('salinity', self.gf('django.db.models.fields.FloatField')()),
            ('pitch', self.gf('django.db.models.fields.FloatField')()),
            ('roll', self.gf('django.db.models.fields.FloatField')()),
            ('yaw', self.gf('django.db.models.fields.FloatField')()),
            ('altitude', self.gf('django.db.models.fields.FloatField')()),
            ('depth', self.gf('django.db.models.fields.FloatField')()),
        ))
        db.send_create_signal('Force', ['Image'])

        # Adding unique constraint on 'Image', fields ['deployment', 'date_time']
        db.create_unique('Force_image', ['deployment_id', 'date_time'])

        # Adding model 'User'
        db.create_table('Force_user', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('organisation', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
        ))
        db.send_create_signal('Force', ['User'])

        # Adding model 'AUVDeployment'
        db.create_table('Force_auvdeployment', (
            ('deployment_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['Force.Deployment'], unique=True, primary_key=True)),
            ('transect_shape', self.gf('django.contrib.gis.db.models.fields.PolygonField')()),
            ('distance_covered', self.gf('django.db.models.fields.FloatField')()),
        ))
        db.send_create_signal('Force', ['AUVDeployment'])

        # Adding model 'StereoImage'
        db.create_table('Force_stereoimage', (
            ('image_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['Force.Image'], unique=True, primary_key=True)),
            ('right_thumbnail_reference', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('right_image_reference', self.gf('django.db.models.fields.URLField')(max_length=200)),
        ))
        db.send_create_signal('Force', ['StereoImage'])

        # Adding model 'Annotation'
        db.create_table('Force_annotation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('method', self.gf('django.db.models.fields.TextField')()),
            ('image_reference', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['Force.Image'])),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('point', self.gf('django.contrib.gis.db.models.fields.PointField')()),
            ('user_who_annotated', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['Force.User'])),
            ('comments', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('Force', ['Annotation'])

        # Adding model 'BRUVDeployment'
        db.create_table('Force_bruvdeployment', (
            ('deployment_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['Force.Deployment'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('Force', ['BRUVDeployment'])

        # Adding model 'DOVDeployment'
        db.create_table('Force_dovdeployment', (
            ('deployment_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['Force.Deployment'], unique=True, primary_key=True)),
            ('diver_name', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('Force', ['DOVDeployment'])

        # Adding model 'TVDeployment'
        db.create_table('Force_tvdeployment', (
            ('deployment_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['Force.Deployment'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('Force', ['TVDeployment'])

        # Adding model 'TIDeployment'
        db.create_table('Force_tideployment', (
            ('deployment_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['Force.Deployment'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('Force', ['TIDeployment'])


    def backwards(self, orm):
        # Removing unique constraint on 'Image', fields ['deployment', 'date_time']
        db.delete_unique('Force_image', ['deployment_id', 'date_time'])

        # Removing unique constraint on 'Deployment', fields ['start_time_stamp', 'short_name']
        db.delete_unique('Force_deployment', ['start_time_stamp', 'short_name'])

        # Removing unique constraint on 'Campaign', fields ['date_start', 'short_name']
        db.delete_unique('Force_campaign', ['date_start', 'short_name'])

        # Deleting model 'Campaign'
        db.delete_table('Force_campaign')

        # Deleting model 'Deployment'
        db.delete_table('Force_deployment')

        # Deleting model 'Image'
        db.delete_table('Force_image')

        # Deleting model 'User'
        db.delete_table('Force_user')

        # Deleting model 'AUVDeployment'
        db.delete_table('Force_auvdeployment')

        # Deleting model 'StereoImage'
        db.delete_table('Force_stereoimage')

        # Deleting model 'Annotation'
        db.delete_table('Force_annotation')

        # Deleting model 'BRUVDeployment'
        db.delete_table('Force_bruvdeployment')

        # Deleting model 'DOVDeployment'
        db.delete_table('Force_dovdeployment')

        # Deleting model 'TVDeployment'
        db.delete_table('Force_tvdeployment')

        # Deleting model 'TIDeployment'
        db.delete_table('Force_tideployment')


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
            'date_end': ('django.db.models.fields.DateField', [], {}),
            'date_start': ('django.db.models.fields.DateField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'Force.deployment': {
            'Meta': {'unique_together': "(('start_time_stamp', 'short_name'),)", 'object_name': 'Deployment'},
            'campaign': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['Force.Campaign']"}),
            'end_time_stamp': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
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
            'altitude': ('django.db.models.fields.FloatField', [], {}),
            'date_time': ('django.db.models.fields.DateTimeField', [], {}),
            'deployment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['Force.Deployment']"}),
            'depth': ('django.db.models.fields.FloatField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image_position': ('django.contrib.gis.db.models.fields.PointField', [], {}),
            'left_image_reference': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'left_thumbnail_reference': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'pitch': ('django.db.models.fields.FloatField', [], {}),
            'roll': ('django.db.models.fields.FloatField', [], {}),
            'salinity': ('django.db.models.fields.FloatField', [], {}),
            'temperature': ('django.db.models.fields.FloatField', [], {}),
            'yaw': ('django.db.models.fields.FloatField', [], {})
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