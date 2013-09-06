# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Image.depth_uncertainty'
        db.add_column('catamidb_image', 'depth_uncertainty',
                      self.gf('django.db.models.fields.FloatField')(null=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Image.depth_uncertainty'
        db.delete_column('catamidb_image', 'depth_uncertainty')


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
            'depth_uncertainty': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
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