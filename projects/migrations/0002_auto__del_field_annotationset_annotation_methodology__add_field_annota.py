# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'AnnotationSet.annotation_methodology'
        db.delete_column('projects_annotationset', 'annotation_methodology')

        # Adding field 'AnnotationSet.point_sampling_methodology'
        db.add_column('projects_annotationset', 'point_sampling_methodology',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)

        # Adding field 'AnnotationSet.annotation_set_type'
        db.add_column('projects_annotationset', 'annotation_set_type',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'AnnotationSet.annotation_methodology'
        db.add_column('projects_annotationset', 'annotation_methodology',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)

        # Deleting field 'AnnotationSet.point_sampling_methodology'
        db.delete_column('projects_annotationset', 'point_sampling_methodology')

        # Deleting field 'AnnotationSet.annotation_set_type'
        db.delete_column('projects_annotationset', 'annotation_set_type')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
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
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'projects.annotationcodes': {
            'Meta': {'object_name': 'AnnotationCodes'},
            'caab_code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '8'}),
            'code_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'cpc_code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '5'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['projects.AnnotationCodes']", 'null': 'True', 'blank': 'True'}),
            'point_colour': ('django.db.models.fields.CharField', [], {'max_length': '6'})
        },
        'projects.annotationset': {
            'Meta': {'unique_together': "(('owner', 'name', 'creation_date'),)", 'object_name': 'AnnotationSet'},
            'annotation_set_type': ('django.db.models.fields.IntegerField', [], {}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image_sampling_methodology': ('django.db.models.fields.IntegerField', [], {}),
            'images': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'projects'", 'symmetrical': 'False', 'to': "orm['catamidb.Image']"}),
            'modified_date': ('django.db.models.fields.DateTimeField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'}),
            'point_sampling_methodology': ('django.db.models.fields.IntegerField', [], {}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['projects.Project']"})
        },
        'projects.pointannotation': {
            'Meta': {'object_name': 'PointAnnotation'},
            'annotation_caab_code': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'annotation_set': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['projects.AnnotationSet']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['catamidb.Image']"}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'}),
            'qualifier_short_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'x': ('django.db.models.fields.FloatField', [], {}),
            'y': ('django.db.models.fields.FloatField', [], {})
        },
        'projects.project': {
            'Meta': {'unique_together': "(('owner', 'name', 'creation_date'),)", 'object_name': 'Project'},
            'creation_date': ('django.db.models.fields.DateTimeField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'images': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['catamidb.Image']", 'null': 'True', 'symmetrical': 'False'}),
            'modified_date': ('django.db.models.fields.DateTimeField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'})
        },
        'projects.qualifiercodes': {
            'Meta': {'object_name': 'QualifierCodes'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': "orm['projects.QualifierCodes']"}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'projects.wholeimageannotation': {
            'Meta': {'object_name': 'WholeImageAnnotation'},
            'annotation_caab_code': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'annotation_set': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['projects.AnnotationSet']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['catamidb.Image']"}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'}),
            'qualifier_short_name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['projects']