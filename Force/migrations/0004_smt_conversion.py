# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):
        "Create the required AUV measurement types and move into new tables."
        temperature = orm['Force.ScientificMeasurementType']()
        temperature.normalised_name = "temperature"
        temperature.display_name = "Temperature"
        temperature.max_value = 40.0
        temperature.min_value = -2.5
        temperature.description = "The water temperature at the location (and time) of the image."
        temperature.units = "cel"
        temperature.save()

        salinity = orm['Force.ScientificMeasurementType']()
        salinity.normalised_name = "salinity"
        salinity.display_name = "Salinity"
        salinity.max_value = 41.0
        salinity.min_value = 2.0
        salinity.description = "Water salinity at the measurement point."
        salinity.units = "psu"
        salinity.save()

        pitch = orm['Force.ScientificMeasurementType']()
        pitch.normalised_name = "pitch"
        pitch.display_name = "Pitch"
        pitch.max_value = 1.58
        pitch.min_value = -1.58
        pitch.description = "Pitch of camera at time of image."
        pitch.units = "rad"
        pitch.save()

        roll = orm['Force.ScientificMeasurementType']()
        roll.normalised_name = "roll"
        roll.display_name = "Roll"
        roll.max_value = 3.15
        roll.min_value = -3.15
        roll.description = "Roll of camera at time of image."
        roll.units = "rad"
        roll.save()

        yaw = orm['Force.ScientificMeasurementType']()
        yaw.normalised_name = "yaw"
        yaw.display_name = "Yaw"
        yaw.max_value = 3.15
        yaw.min_value = -3.15
        yaw.description = "Yaw of camera at time of image."
        yaw.units = "rad"
        yaw.save()

        altitude = orm['Force.ScientificMeasurementType']()
        altitude.normalised_name = "altitude"
        altitude.display_name = "Altitude"
        altitude.max_value = 12000.0
        altitude.min_value = 0.0
        altitude.description = "Altitude of camera at time of image."
        altitude.units = "m"
        altitude.save()


        for image in orm['Force.Image'].objects.all():
            a = orm['Force.ScientificMeasurement']()
            a.image = image
            a.measurement_type = altitude
            a.value = image.altitude
            a.save()

            y = orm['Force.ScientificMeasurement']()
            y.image = image
            y.measurement_type = yaw
            y.value = image.yaw
            y.save()

            p = orm['Force.ScientificMeasurement']()
            p.image = image
            p.measurement_type = pitch
            p.value = image.pitch
            p.save()

            r = orm['Force.ScientificMeasurement']()
            r.image = image
            r.measurement_type = roll
            r.value = image.roll
            r.save()

            s = orm['Force.ScientificMeasurement']()
            s.image = image
            s.measurement_type = salinity
            s.value = image.salinity
            s.save()

            t = orm['Force.ScientificMeasurement']()
            t.image = image
            t.measurement_type = temperature
            t.value = image.temperature
            t.save()


    def backwards(self, orm):
        "Write your backwards methods here."

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
    symmetrical = True
