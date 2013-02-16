# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Assassin'
        db.create_table(u'assassins_manager_assassin', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('picture', self.gf('django.db.models.fields.files.ImageField')(max_length=100, blank=True)),
            ('alive', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('lifecode', self.gf('django.db.models.fields.CharField')(max_length=8, blank=True)),
            ('kills', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('is_admin', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('deadline', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('role', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('squad', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['assassins_manager.Squad'], null=True, blank=True)),
            ('game', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['assassins_manager.Game'])),
        ))
        db.send_create_signal(u'assassins_manager', ['Assassin'])

        # Adding model 'Game'
        db.create_table(u'assassins_manager_game', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('disavowed_time', self.gf('django.db.models.fields.IntegerField')(default=72)),
            ('police_resurrect_time', self.gf('django.db.models.fields.IntegerField')(default=24)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('squadsize', self.gf('django.db.models.fields.IntegerField')(default=4)),
        ))
        db.send_create_signal(u'assassins_manager', ['Game'])

        # Adding model 'Squad'
        db.create_table(u'assassins_manager_squad', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('alive', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('kills', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('game', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['assassins_manager.Game'])),
            ('public', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=10)),
        ))
        db.send_create_signal(u'assassins_manager', ['Squad'])

        # Adding model 'Contract'
        db.create_table(u'assassins_manager_contract', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('holder', self.gf('django.db.models.fields.related.ForeignKey')(related_name='holder', to=orm['assassins_manager.Squad'])),
            ('target', self.gf('django.db.models.fields.related.ForeignKey')(related_name='target', to=orm['assassins_manager.Squad'])),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('game', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['assassins_manager.Game'])),
        ))
        db.send_create_signal(u'assassins_manager', ['Contract'])

        # Adding model 'KillReport'
        db.create_table(u'assassins_manager_killreport', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('killer', self.gf('django.db.models.fields.related.ForeignKey')(related_name='killreporter', to=orm['assassins_manager.Assassin'])),
            ('corpse', self.gf('django.db.models.fields.related.ForeignKey')(related_name='corpse', to=orm['assassins_manager.Assassin'])),
            ('killtype', self.gf('django.db.models.fields.IntegerField')()),
            ('report', self.gf('django.db.models.fields.TextField')()),
            ('game', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['assassins_manager.Game'])),
            ('date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal(u'assassins_manager', ['KillReport'])


    def backwards(self, orm):
        # Deleting model 'Assassin'
        db.delete_table(u'assassins_manager_assassin')

        # Deleting model 'Game'
        db.delete_table(u'assassins_manager_game')

        # Deleting model 'Squad'
        db.delete_table(u'assassins_manager_squad')

        # Deleting model 'Contract'
        db.delete_table(u'assassins_manager_contract')

        # Deleting model 'KillReport'
        db.delete_table(u'assassins_manager_killreport')


    models = {
        u'assassins_manager.assassin': {
            'Meta': {'object_name': 'Assassin'},
            'alive': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'deadline': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'game': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['assassins_manager.Game']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_admin': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'kills': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'lifecode': ('django.db.models.fields.CharField', [], {'max_length': '8', 'blank': 'True'}),
            'picture': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'role': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'squad': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['assassins_manager.Squad']", 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'assassins_manager.contract': {
            'Meta': {'object_name': 'Contract'},
            'game': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['assassins_manager.Game']"}),
            'holder': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'holder'", 'to': u"orm['assassins_manager.Squad']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'target': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'target'", 'to': u"orm['assassins_manager.Squad']"})
        },
        u'assassins_manager.game': {
            'Meta': {'object_name': 'Game'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'disavowed_time': ('django.db.models.fields.IntegerField', [], {'default': '72'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'police_resurrect_time': ('django.db.models.fields.IntegerField', [], {'default': '24'}),
            'squadsize': ('django.db.models.fields.IntegerField', [], {'default': '4'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'assassins_manager.killreport': {
            'Meta': {'object_name': 'KillReport'},
            'corpse': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'corpse'", 'to': u"orm['assassins_manager.Assassin']"}),
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'game': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['assassins_manager.Game']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'killer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'killreporter'", 'to': u"orm['assassins_manager.Assassin']"}),
            'killtype': ('django.db.models.fields.IntegerField', [], {}),
            'report': ('django.db.models.fields.TextField', [], {})
        },
        u'assassins_manager.squad': {
            'Meta': {'object_name': 'Squad'},
            'alive': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'code': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'game': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['assassins_manager.Game']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kills': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['assassins_manager']