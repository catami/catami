# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'AnnotationCodes'
        db.create_table('projects_annotationcodes', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('caab_code', self.gf('django.db.models.fields.CharField')(unique=True, max_length=8)),
            ('cpc_code', self.gf('django.db.models.fields.CharField')(unique=True, max_length=5)),
            ('point_colour', self.gf('django.db.models.fields.CharField')(max_length=6)),
            ('code_name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['projects.AnnotationCodes'], null=True, blank=True)),
        ))
        db.send_create_signal('projects', ['AnnotationCodes'])

        # Adding model 'QualifierCodes'
        db.create_table('projects_qualifiercodes', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='children', null=True, to=orm['projects.QualifierCodes'])),
            ('short_name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('projects', ['QualifierCodes'])

        # Adding model 'Project'
        db.create_table('projects_project', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True)),
            ('creation_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('modified_date', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('projects', ['Project'])

        # Adding unique constraint on 'Project', fields ['owner', 'name', 'creation_date']
        db.create_unique('projects_project', ['owner_id', 'name', 'creation_date'])

        # Adding M2M table for field images on 'Project'
        m2m_table_name = db.shorten_name('projects_project_images')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('project', models.ForeignKey(orm['projects.project'], null=False)),
            ('image', models.ForeignKey(orm['catamidb.image'], null=False))
        ))
        db.create_unique(m2m_table_name, ['project_id', 'image_id'])

        # Adding model 'AnnotationSet'
        db.create_table('projects_annotationset', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['projects.Project'])),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('creation_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('modified_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('image_sampling_methodology', self.gf('django.db.models.fields.IntegerField')()),
            ('annotation_methodology', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('projects', ['AnnotationSet'])

        # Adding unique constraint on 'AnnotationSet', fields ['owner', 'name', 'creation_date']
        db.create_unique('projects_annotationset', ['owner_id', 'name', 'creation_date'])

        # Adding M2M table for field images on 'AnnotationSet'
        m2m_table_name = db.shorten_name('projects_annotationset_images')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('annotationset', models.ForeignKey(orm['projects.annotationset'], null=False)),
            ('image', models.ForeignKey(orm['catamidb.image'], null=False))
        ))
        db.create_unique(m2m_table_name, ['annotationset_id', 'image_id'])

        # Adding model 'PointAnnotation'
        db.create_table('projects_pointannotation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('image', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['catamidb.Image'])),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True)),
            ('annotation_caab_code', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('qualifier_short_name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('annotation_set', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['projects.AnnotationSet'])),
            ('x', self.gf('django.db.models.fields.FloatField')()),
            ('y', self.gf('django.db.models.fields.FloatField')()),
        ))
        db.send_create_signal('projects', ['PointAnnotation'])

        # Adding model 'WholeImageAnnotation'
        db.create_table('projects_wholeimageannotation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('image', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['catamidb.Image'])),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True)),
            ('annotation_caab_code', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('qualifier_short_name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('annotation_set', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['projects.AnnotationSet'])),
        ))
        db.send_create_signal('projects', ['WholeImageAnnotation'])


    def backwards(self, orm):
        # Removing unique constraint on 'AnnotationSet', fields ['owner', 'name', 'creation_date']
        db.delete_unique('projects_annotationset', ['owner_id', 'name', 'creation_date'])

        # Removing unique constraint on 'Project', fields ['owner', 'name', 'creation_date']
        db.delete_unique('projects_project', ['owner_id', 'name', 'creation_date'])

        # Deleting model 'AnnotationCodes'
        db.delete_table('projects_annotationcodes')

        # Deleting model 'QualifierCodes'
        db.delete_table('projects_qualifiercodes')

        # Deleting model 'Project'
        db.delete_table('projects_project')

        # Removing M2M table for field images on 'Project'
        db.delete_table(db.shorten_name('projects_project_images'))

        # Deleting model 'AnnotationSet'
        db.delete_table('projects_annotationset')

        # Removing M2M table for field images on 'AnnotationSet'
        db.delete_table(db.shorten_name('projects_annotationset_images'))

        # Deleting model 'PointAnnotation'
        db.delete_table('projects_pointannotation')

        # Deleting model 'WholeImageAnnotation'
        db.delete_table('projects_wholeimageannotation')


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
            'annotation_methodology': ('django.db.models.fields.IntegerField', [], {}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image_sampling_methodology': ('django.db.models.fields.IntegerField', [], {}),
            'images': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'projects'", 'symmetrical': 'False', 'to': "orm['catamidb.Image']"}),
            'modified_date': ('django.db.models.fields.DateTimeField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'}),
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