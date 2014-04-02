# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding unique constraint on 'AuctioneerPhrase', fields ['key']
        db.create_unique(u'chat_auctioneerphrase', ['key'])


    def backwards(self, orm):
        # Removing unique constraint on 'AuctioneerPhrase', fields ['key']
        db.delete_unique(u'chat_auctioneerphrase', ['key'])


    models = {
        u'chat.auctioneerphrase': {
        'Meta': {'object_name': 'AuctioneerPhrase'},
        'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
        u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
        'key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '20'}),
        'text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        u'chat.chatuser': {
            'Meta': {'object_name': 'ChatUser'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        u'chat.message': {
            'Meta': {'object_name': 'Message'},
            '_user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['chat.ChatUser']", 'null': 'True', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'text': ('django.db.models.fields.TextField', [], {})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['chat']