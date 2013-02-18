# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'AnnotationCode'
        db.create_table('annotations_annotationcode', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code_name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['annotations.AnnotationCode'])),
        ))
        db.send_create_signal('annotations', ['AnnotationCode'])

        # Adding model 'QualifierCode'
        db.create_table('annotations_qualifiercode', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('modifier_name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('annotations', ['QualifierCode'])

        # Adding model 'PointAnnotationSet'
        db.create_table('annotations_pointannotationset', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('collection', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['collection.Collection'])),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('methodology', self.gf('django.db.models.fields.IntegerField')()),
            ('count', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('annotations', ['PointAnnotationSet'])

        # Adding model 'PointAnnotation'
        db.create_table('annotations_pointannotation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('image', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['Force.Image'])),
            ('label', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['annotations.AnnotationCode'])),
            ('labeller', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('annotation_set', self.gf('django.db.models.fields.related.ForeignKey')(related_name='images', to=orm['annotations.PointAnnotationSet'])),
            ('x', self.gf('django.db.models.fields.FloatField')()),
            ('y', self.gf('django.db.models.fields.FloatField')()),
            ('level', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('annotations', ['PointAnnotation'])

        # Adding model 'ImageAnnotationSet'
        db.create_table('annotations_imageannotationset', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('collection', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['collection.Collection'])),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('annotations', ['ImageAnnotationSet'])

        # Adding model 'ImageAnnotation'
        db.create_table('annotations_imageannotation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('image', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['Force.Image'])),
            ('label', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['annotations.AnnotationCode'])),
            ('labeller', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('annotation_set', self.gf('django.db.models.fields.related.ForeignKey')(related_name='images', to=orm['annotations.ImageAnnotationSet'])),
            ('cover', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('annotations', ['ImageAnnotation'])

        # Adding model 'PointQualifier'
        db.create_table('annotations_pointqualifier', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('qualifier_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['annotations.QualifierCode'])),
            ('point_annotation', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['annotations.PointAnnotation'])),
        ))
        db.send_create_signal('annotations', ['PointQualifier'])

        # Adding model 'ImageQualifier'
        db.create_table('annotations_imagequalifier', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('qualifier_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['annotations.QualifierCode'])),
            ('image_annotation', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['annotations.ImageAnnotation'])),
        ))
        db.send_create_signal('annotations', ['ImageQualifier'])


    def backwards(self, orm):
        # Deleting model 'AnnotationCode'
        db.delete_table('annotations_annotationcode')

        # Deleting model 'QualifierCode'
        db.delete_table('annotations_qualifiercode')

        # Deleting model 'PointAnnotationSet'
        db.delete_table('annotations_pointannotationset')

        # Deleting model 'PointAnnotation'
        db.delete_table('annotations_pointannotation')

        # Deleting model 'ImageAnnotationSet'
        db.delete_table('annotations_imageannotationset')

        # Deleting model 'ImageAnnotation'
        db.delete_table('annotations_imageannotation')

        # Deleting model 'PointQualifier'
        db.delete_table('annotations_pointqualifier')

        # Deleting model 'ImageQualifier'
        db.delete_table('annotations_imagequalifier')


    models = {
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
            'end_position': ('django.contrib.gis.db.models.fields.PointField', [], {}),
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
        'Force.image': {
            'Meta': {'unique_together': "(('deployment', 'date_time'),)", 'object_name': 'Image'},
            'archive_location': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'date_time': ('django.db.models.fields.DateTimeField', [], {}),
            'deployment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['Force.Deployment']"}),
            'depth': ('django.db.models.fields.FloatField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image_position': ('django.contrib.gis.db.models.fields.PointField', [], {}),
            'webimage_location': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        },
        'annotations.annotationcode': {
            'Meta': {'object_name': 'AnnotationCode'},
            'code_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['annotations.AnnotationCode']"})
        },
        'annotations.imageannotation': {
            'Meta': {'object_name': 'ImageAnnotation'},
            'annotation_set': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'images'", 'to': "orm['annotations.ImageAnnotationSet']"}),
            'cover': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['Force.Image']"}),
            'label': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['annotations.AnnotationCode']"}),
            'labeller': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'annotations.imageannotationset': {
            'Meta': {'object_name': 'ImageAnnotationSet'},
            'collection': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['collection.Collection']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'annotations.imagequalifier': {
            'Meta': {'object_name': 'ImageQualifier'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image_annotation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['annotations.ImageAnnotation']"}),
            'qualifier_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['annotations.QualifierCode']"})
        },
        'annotations.pointannotation': {
            'Meta': {'object_name': 'PointAnnotation'},
            'annotation_set': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'images'", 'to': "orm['annotations.PointAnnotationSet']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['Force.Image']"}),
            'label': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['annotations.AnnotationCode']"}),
            'labeller': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'level': ('django.db.models.fields.IntegerField', [], {}),
            'x': ('django.db.models.fields.FloatField', [], {}),
            'y': ('django.db.models.fields.FloatField', [], {})
        },
        'annotations.pointannotationset': {
            'Meta': {'object_name': 'PointAnnotationSet'},
            'collection': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['collection.Collection']"}),
            'count': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'methodology': ('django.db.models.fields.IntegerField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'annotations.pointqualifier': {
            'Meta': {'object_name': 'PointQualifier'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'point_annotation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['annotations.PointAnnotation']"}),
            'qualifier_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['annotations.QualifierCode']"})
        },
        'annotations.qualifiercode': {
            'Meta': {'object_name': 'QualifierCode'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modifier_name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
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
        'collection.collection': {
            'Meta': {'unique_together': "(('owner', 'name'),)", 'object_name': 'Collection'},
            'creation_date': ('django.db.models.fields.DateTimeField', [], {}),
            'creation_info': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'images': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'collections'", 'symmetrical': 'False', 'to': "orm['Force.Image']"}),
            'is_locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modified_date': ('django.db.models.fields.DateTimeField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['collection.Collection']", 'null': 'True', 'blank': 'True'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['annotations']