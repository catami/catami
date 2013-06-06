# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ImageUpload'
        db.create_table('catamidb_imageupload', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('img', self.gf('django.db.models.fields.files.ImageField')(max_length=255, null=True, blank=True)),
        ))
        db.send_create_signal('catamidb', ['ImageUpload'])


    def backwards(self, orm):
        # Deleting model 'ImageUpload'
        db.delete_table('catamidb_imageupload')


    models = {
        'catamidb.auvdeployment': {
            'Meta': {'object_name': 'AUVDeployment', '_ormbases': ['catamidb.Deployment']},
            'deployment_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['catamidb.Deployment']", 'unique': 'True', 'primary_key': 'True'})
        },
        'catamidb.bruvdeployment': {
            'Meta': {'object_name': 'BRUVDeployment', '_ormbases': ['catamidb.Deployment']},
            'deployment_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['catamidb.Deployment']", 'unique': 'True', 'primary_key': 'True'})
        },
        'catamidb.camera': {
            'Meta': {'unique_together': "(('deployment', 'name'),)", 'object_name': 'Camera'},
            'angle': ('django.db.models.fields.IntegerField', [], {}),
            'deployment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['catamidb.Deployment']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
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
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
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
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'start_position': ('django.contrib.gis.db.models.fields.PointField', [], {}),
            'start_time_stamp': ('django.db.models.fields.DateTimeField', [], {}),
            'transect_shape': ('django.contrib.gis.db.models.fields.PolygonField', [], {})
        },
        'catamidb.dovdeployment': {
            'Meta': {'object_name': 'DOVDeployment', '_ormbases': ['catamidb.Deployment']},
            'deployment_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['catamidb.Deployment']", 'unique': 'True', 'primary_key': 'True'}),
            'diver_name': ('django.db.models.fields.TextField', [], {})
        },
        'catamidb.genericimage': {
            'Meta': {'unique_together': "(('date_time', 'camera'),)", 'object_name': 'GenericImage'},
            'archive_location': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'camera': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['catamidb.Camera']"}),
            'date_time': ('django.db.models.fields.DateTimeField', [], {}),
            'deployment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['catamidb.Deployment']"}),
            'depth': ('django.db.models.fields.FloatField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'measurements': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['catamidb.Measurements']"}),
            'position': ('django.contrib.gis.db.models.fields.PointField', [], {}),
            'web_location': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'catamidb.image': {
            'Meta': {'unique_together': "(('pose', 'camera'),)", 'object_name': 'Image'},
            'archive_location': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'camera': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['catamidb.Camera']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pose': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['catamidb.Pose']"}),
            'web_location': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'catamidb.imageupload': {
            'Meta': {'object_name': 'ImageUpload'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'img': ('django.db.models.fields.files.ImageField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        'catamidb.measurements': {
            'Meta': {'object_name': 'Measurements'},
            'altitude': ('django.db.models.fields.FloatField', [], {}),
            'altitude_unit': ('django.db.models.fields.CharField', [], {'default': "'m'", 'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pitch': ('django.db.models.fields.FloatField', [], {}),
            'pitch_unit': ('django.db.models.fields.CharField', [], {'default': "'rad'", 'max_length': '50'}),
            'roll': ('django.db.models.fields.FloatField', [], {}),
            'roll_unit': ('django.db.models.fields.CharField', [], {'default': "'rad'", 'max_length': '50'}),
            'salinity': ('django.db.models.fields.FloatField', [], {}),
            'salinity_unit': ('django.db.models.fields.CharField', [], {'default': "'psu'", 'max_length': '50'}),
            'temperature': ('django.db.models.fields.FloatField', [], {}),
            'temperature_unit': ('django.db.models.fields.CharField', [], {'default': "'cel'", 'max_length': '50'}),
            'yaw': ('django.db.models.fields.FloatField', [], {}),
            'yaw_unit': ('django.db.models.fields.CharField', [], {'default': "'rad'", 'max_length': '50'})
        },
        'catamidb.pose': {
            'Meta': {'unique_together': "(('deployment', 'date_time'),)", 'object_name': 'Pose'},
            'date_time': ('django.db.models.fields.DateTimeField', [], {}),
            'deployment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['catamidb.Deployment']"}),
            'depth': ('django.db.models.fields.FloatField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'position': ('django.contrib.gis.db.models.fields.PointField', [], {})
        },
        'catamidb.scientificimagemeasurement': {
            'Meta': {'unique_together': "(('measurement_type', 'image'),)", 'object_name': 'ScientificImageMeasurement'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['catamidb.Image']"}),
            'measurement_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['catamidb.ScientificMeasurementType']"}),
            'value': ('django.db.models.fields.FloatField', [], {})
        },
        'catamidb.scientificmeasurementtype': {
            'Meta': {'object_name': 'ScientificMeasurementType'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'display_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_value': ('django.db.models.fields.FloatField', [], {}),
            'min_value': ('django.db.models.fields.FloatField', [], {}),
            'normalised_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'units': ('django.db.models.fields.CharField', [], {'max_length': '5'})
        },
        'catamidb.scientificposemeasurement': {
            'Meta': {'unique_together': "(('measurement_type', 'pose'),)", 'object_name': 'ScientificPoseMeasurement'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'measurement_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['catamidb.ScientificMeasurementType']"}),
            'pose': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['catamidb.Pose']"}),
            'value': ('django.db.models.fields.FloatField', [], {})
        },
        'catamidb.tideployment': {
            'Meta': {'object_name': 'TIDeployment', '_ormbases': ['catamidb.Deployment']},
            'deployment_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['catamidb.Deployment']", 'unique': 'True', 'primary_key': 'True'})
        },
        'catamidb.tvdeployment': {
            'Meta': {'object_name': 'TVDeployment', '_ormbases': ['catamidb.Deployment']},
            'deployment_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['catamidb.Deployment']", 'unique': 'True', 'primary_key': 'True'})
        }
    }

    complete_apps = ['catamidb']