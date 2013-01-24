# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ClusterRun'
        db.create_table('clustering_clusterrun', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('collection', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['collection.Collection'])),
            ('cluster_width', self.gf('django.db.models.fields.FloatField')()),
        ))
        db.send_create_signal('clustering', ['ClusterRun'])

        # Adding model 'ImageProbability'
        db.create_table('clustering_imageprobability', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('image', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['Force.Image'])),
            ('probability', self.gf('django.db.models.fields.FloatField')()),
            ('cluster_label', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['clustering.ClusterLabels'])),
        ))
        db.send_create_signal('clustering', ['ImageProbability'])

        # Adding model 'ClusterLabels'
        db.create_table('clustering_clusterlabels', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('cluster_label', self.gf('django.db.models.fields.IntegerField')()),
            ('cluster_run', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['clustering.ClusterRun'])),
        ))
        db.send_create_signal('clustering', ['ClusterLabels'])

        # Adding M2M table for field image on 'ClusterLabels'
        db.create_table('clustering_clusterlabels_image', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('clusterlabels', models.ForeignKey(orm['clustering.clusterlabels'], null=False)),
            ('image', models.ForeignKey(orm['Force.image'], null=False))
        ))
        db.create_unique('clustering_clusterlabels_image', ['clusterlabels_id', 'image_id'])


    def backwards(self, orm):
        # Deleting model 'ClusterRun'
        db.delete_table('clustering_clusterrun')

        # Deleting model 'ImageProbability'
        db.delete_table('clustering_imageprobability')

        # Deleting model 'ClusterLabels'
        db.delete_table('clustering_clusterlabels')

        # Removing M2M table for field image on 'ClusterLabels'
        db.delete_table('clustering_clusterlabels_image')


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
        'clustering.clusterlabels': {
            'Meta': {'object_name': 'ClusterLabels'},
            'cluster_label': ('django.db.models.fields.IntegerField', [], {}),
            'cluster_run': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['clustering.ClusterRun']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'clusters'", 'symmetrical': 'False', 'to': "orm['Force.Image']"}),
            'probabilities': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'cluster_probabilities'", 'symmetrical': 'False', 'through': "orm['clustering.ImageProbability']", 'to': "orm['Force.Image']"})
        },
        'clustering.clusterrun': {
            'Meta': {'object_name': 'ClusterRun'},
            'cluster_width': ('django.db.models.fields.FloatField', [], {}),
            'collection': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['collection.Collection']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'clustering.imageprobability': {
            'Meta': {'object_name': 'ImageProbability'},
            'cluster_label': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['clustering.ClusterLabels']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['Force.Image']"}),
            'probability': ('django.db.models.fields.FloatField', [], {})
        },
        'collection.collection': {
            'Meta': {'object_name': 'Collection'},
            'creation_date': ('django.db.models.fields.DateTimeField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'images': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['Force.Image']", 'symmetrical': 'False'}),
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

    complete_apps = ['clustering']