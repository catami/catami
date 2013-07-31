# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Campaign'
        db.create_table('catamidb_campaign', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('short_name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('associated_researchers', self.gf('django.db.models.fields.TextField')()),
            ('associated_publications', self.gf('django.db.models.fields.TextField')()),
            ('associated_research_grant', self.gf('django.db.models.fields.TextField')()),
            ('date_start', self.gf('django.db.models.fields.DateField')()),
            ('date_end', self.gf('django.db.models.fields.DateField')()),
            ('contact_person', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('catamidb', ['Campaign'])

        # Adding unique constraint on 'Campaign', fields ['date_start', 'short_name']
        db.create_unique('catamidb_campaign', ['date_start', 'short_name'])

        # Adding model 'Deployment'
        db.create_table('catamidb_deployment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('operator', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('start_position', self.gf('django.contrib.gis.db.models.fields.PointField')()),
            ('end_position', self.gf('django.contrib.gis.db.models.fields.PointField')()),
            ('transect_shape', self.gf('django.contrib.gis.db.models.fields.PolygonField')()),
            ('start_time_stamp', self.gf('django.db.models.fields.DateTimeField')()),
            ('end_time_stamp', self.gf('django.db.models.fields.DateTimeField')()),
            ('short_name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('mission_aim', self.gf('django.db.models.fields.TextField')()),
            ('min_depth', self.gf('django.db.models.fields.FloatField')()),
            ('max_depth', self.gf('django.db.models.fields.FloatField')()),
            ('campaign', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['catamidb.Campaign'])),
            ('contact_person', self.gf('django.db.models.fields.TextField')()),
            ('descriptive_keywords', self.gf('django.db.models.fields.TextField')()),
            ('license', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('catamidb', ['Deployment'])

        # Adding unique constraint on 'Deployment', fields ['start_time_stamp', 'short_name']
        db.create_unique('catamidb_deployment', ['start_time_stamp', 'short_name'])

        # Adding model 'ImageUpload'
        db.create_table('catamidb_imageupload', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('img', self.gf('django.db.models.fields.files.ImageField')(max_length=255, null=True, blank=True)),
        ))
        db.send_create_signal('catamidb', ['ImageUpload'])

        # Adding model 'Image'
        db.create_table('catamidb_image', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('deployment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['catamidb.Deployment'])),
            ('image_name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('date_time', self.gf('django.db.models.fields.DateTimeField')()),
            ('position', self.gf('django.contrib.gis.db.models.fields.PointField')()),
            ('depth', self.gf('django.db.models.fields.FloatField')()),
        ))
        db.send_create_signal('catamidb', ['Image'])

        # Adding unique constraint on 'Image', fields ['date_time', 'deployment']
        db.create_unique('catamidb_image', ['date_time', 'deployment_id'])

        # Adding model 'Camera'
        db.create_table('catamidb_camera', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('image', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['catamidb.Image'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('angle', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('catamidb', ['Camera'])

        # Adding unique constraint on 'Camera', fields ['image', 'name']
        db.create_unique('catamidb_camera', ['image_id', 'name'])

        # Adding model 'Measurements'
        db.create_table('catamidb_measurements', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('image', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['catamidb.Image'])),
            ('temperature', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('temperature_unit', self.gf('django.db.models.fields.CharField')(default='cel', max_length=50)),
            ('salinity', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('salinity_unit', self.gf('django.db.models.fields.CharField')(default='psu', max_length=50)),
            ('pitch', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('pitch_unit', self.gf('django.db.models.fields.CharField')(default='rad', max_length=50)),
            ('roll', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('roll_unit', self.gf('django.db.models.fields.CharField')(default='rad', max_length=50)),
            ('yaw', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('yaw_unit', self.gf('django.db.models.fields.CharField')(default='rad', max_length=50)),
            ('altitude', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('altitude_unit', self.gf('django.db.models.fields.CharField')(default='m', max_length=50)),
        ))
        db.send_create_signal('catamidb', ['Measurements'])


    def backwards(self, orm):
        # Removing unique constraint on 'Camera', fields ['image', 'name']
        db.delete_unique('catamidb_camera', ['image_id', 'name'])

        # Removing unique constraint on 'Image', fields ['date_time', 'deployment']
        db.delete_unique('catamidb_image', ['date_time', 'deployment_id'])

        # Removing unique constraint on 'Deployment', fields ['start_time_stamp', 'short_name']
        db.delete_unique('catamidb_deployment', ['start_time_stamp', 'short_name'])

        # Removing unique constraint on 'Campaign', fields ['date_start', 'short_name']
        db.delete_unique('catamidb_campaign', ['date_start', 'short_name'])

        # Deleting model 'Campaign'
        db.delete_table('catamidb_campaign')

        # Deleting model 'Deployment'
        db.delete_table('catamidb_deployment')

        # Deleting model 'ImageUpload'
        db.delete_table('catamidb_imageupload')

        # Deleting model 'Image'
        db.delete_table('catamidb_image')

        # Deleting model 'Camera'
        db.delete_table('catamidb_camera')

        # Deleting model 'Measurements'
        db.delete_table('catamidb_measurements')


    models = {
        'catamidb.camera': {
            'Meta': {'unique_together': "(('image', 'name'),)", 'object_name': 'Camera'},
            'angle': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['catamidb.Image']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'catamidb.campaign': {
            'Meta': {'unique_together': "(('date_start', 'short_name'),)", 'object_name': 'Campaign'},
            'associated_publications': ('django.db.models.fields.TextField', [], {}),
            'associated_research_grant': ('django.db.models.fields.TextField', [], {}),
            'associated_researchers': ('django.db.models.fields.TextField', [], {}),
            'contact_person': ('django.db.models.fields.TextField', [], {}),
            'date_end': ('django.db.models.fields.DateField', [], {}),
            'date_start': ('django.db.models.fields.DateField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'short_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        'catamidb.deployment': {
            'Meta': {'unique_together': "(('start_time_stamp', 'short_name'),)", 'object_name': 'Deployment'},
            'campaign': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['catamidb.Campaign']"}),
            'contact_person': ('django.db.models.fields.TextField', [], {}),
            'descriptive_keywords': ('django.db.models.fields.TextField', [], {}),
            'end_position': ('django.contrib.gis.db.models.fields.PointField', [], {}),
            'end_time_stamp': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'license': ('django.db.models.fields.TextField', [], {}),
            'max_depth': ('django.db.models.fields.FloatField', [], {}),
            'min_depth': ('django.db.models.fields.FloatField', [], {}),
            'mission_aim': ('django.db.models.fields.TextField', [], {}),
            'operator': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'start_position': ('django.contrib.gis.db.models.fields.PointField', [], {}),
            'start_time_stamp': ('django.db.models.fields.DateTimeField', [], {}),
            'transect_shape': ('django.contrib.gis.db.models.fields.PolygonField', [], {}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'catamidb.image': {
            'Meta': {'unique_together': "(('date_time', 'deployment'),)", 'object_name': 'Image'},
            'date_time': ('django.db.models.fields.DateTimeField', [], {}),
            'deployment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['catamidb.Deployment']"}),
            'depth': ('django.db.models.fields.FloatField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'position': ('django.contrib.gis.db.models.fields.PointField', [], {})
        },
        'catamidb.imageupload': {
            'Meta': {'object_name': 'ImageUpload'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'img': ('django.db.models.fields.files.ImageField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        'catamidb.measurements': {
            'Meta': {'object_name': 'Measurements'},
            'altitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'altitude_unit': ('django.db.models.fields.CharField', [], {'default': "'m'", 'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['catamidb.Image']"}),
            'pitch': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'pitch_unit': ('django.db.models.fields.CharField', [], {'default': "'rad'", 'max_length': '50'}),
            'roll': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'roll_unit': ('django.db.models.fields.CharField', [], {'default': "'rad'", 'max_length': '50'}),
            'salinity': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'salinity_unit': ('django.db.models.fields.CharField', [], {'default': "'psu'", 'max_length': '50'}),
            'temperature': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'temperature_unit': ('django.db.models.fields.CharField', [], {'default': "'cel'", 'max_length': '50'}),
            'yaw': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'yaw_unit': ('django.db.models.fields.CharField', [], {'default': "'rad'", 'max_length': '50'})
        }
    }

    complete_apps = ['catamidb']