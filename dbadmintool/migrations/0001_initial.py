# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Data_logger'
        db.create_table('rebels_data_logger', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('collection_time', self.gf('django.db.models.fields.DateTimeField')()),
            ('number_of_campaigns', self.gf('django.db.models.fields.IntegerField')()),
            ('number_of_users', self.gf('django.db.models.fields.IntegerField')()),
            ('db_size_on_disk', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('rebels', ['Data_logger'])

    def backwards(self, orm):
        # Deleting model 'Data_logger'
        db.delete_table('rebels_data_logger')

    models = {
        'rebels.data_logger': {
            'Meta': {'object_name': 'Data_logger'},
            'collection_time': ('django.db.models.fields.DateTimeField', [], {}),
            'db_size_on_disk': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number_of_campaigns': ('django.db.models.fields.IntegerField', [], {}),
            'number_of_users': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['rebels']
