# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'FacebookUser'
        db.create_table(u'bidding_facebookuser', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user_id', self.gf('django.db.models.fields.IntegerField')()),
            ('facebook_id', self.gf('django.db.models.fields.BigIntegerField')()),
            ('name', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('gender', self.gf('django.db.models.fields.CharField')(max_length=1, null=True, blank=True)),
        ))
        db.send_create_signal(u'bidding', ['FacebookUser'])

        # Adding unique constraint on 'FacebookUser', fields ['user_id', 'facebook_id']
        db.create_unique(u'bidding_facebookuser', ['user_id', 'facebook_id'])

        # Adding model 'FacebookLike'
        db.create_table(u'bidding_facebooklike', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user_id', self.gf('django.db.models.fields.IntegerField')()),
            ('facebook_id', self.gf('django.db.models.fields.BigIntegerField')()),
            ('name', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('category', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('created_time', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'bidding', ['FacebookLike'])

        # Adding unique constraint on 'FacebookLike', fields ['user_id', 'facebook_id']
        db.create_unique(u'bidding_facebooklike', ['user_id', 'facebook_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'FacebookLike', fields ['user_id', 'facebook_id']
        db.delete_unique(u'bidding_facebooklike', ['user_id', 'facebook_id'])

        # Removing unique constraint on 'FacebookUser', fields ['user_id', 'facebook_id']
        db.delete_unique(u'bidding_facebookuser', ['user_id', 'facebook_id'])

        # Deleting model 'FacebookUser'
        db.delete_table(u'bidding_facebookuser')

        # Deleting model 'FacebookLike'
        db.delete_table(u'bidding_facebooklike')


    models = {
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
        u'bidding.auction': {
            'Meta': {'ordering': "['-id']", 'object_name': 'Auction'},
            'bid_type': ('django.db.models.fields.CharField', [], {'default': "'bid'", 'max_length': '5'}),
            'bidders': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['bidding.Member']", 'null': 'True', 'blank': 'True'}),
            'bidding_time': ('django.db.models.fields.IntegerField', [], {'default': '10'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['bidding.Item']"}),
            'minimum_precap': ('django.db.models.fields.IntegerField', [], {'default': '5'}),
            'precap_bids': ('django.db.models.fields.IntegerField', [], {}),
            'saved_time': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'start_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'precap'", 'max_length': '15'}),
            'threshold1': ('django.db.models.fields.IntegerField', [], {'default': '7', 'null': 'True', 'blank': 'True'}),
            'threshold2': ('django.db.models.fields.IntegerField', [], {'default': '5', 'null': 'True', 'blank': 'True'}),
            'threshold3': ('django.db.models.fields.IntegerField', [], {'default': '3', 'null': 'True', 'blank': 'True'}),
            'winner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'won_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'won_price': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'})
        },
        u'bidding.auctionfixture': {
            'Meta': {'object_name': 'AuctionFixture'},
            'automatic': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'bid_type': ('django.db.models.fields.CharField', [], {'default': "'bid'", 'max_length': '5'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'threshold': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '5'})
        },
        u'bidding.auctioninvitation': {
            'Meta': {'object_name': 'AuctionInvitation'},
            'auction': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['bidding.Auction']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inviter': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['bidding.Member']"}),
            'request_id': ('django.db.models.fields.BigIntegerField', [], {})
        },
        u'bidding.auctioninvoice': {
            'Meta': {'object_name': 'AuctionInvoice'},
            'auction': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['bidding.Auction']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'member': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['bidding.Member']"}),
            'payment': ('django.db.models.fields.CharField', [], {'default': "'direct'", 'max_length': '55'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'created'", 'max_length': '55'}),
            'uid': ('django.db.models.fields.CharField', [], {'max_length': '40', 'db_index': 'True'})
        },
        u'bidding.bid': {
            'Meta': {'unique_together': "(('auction', 'bidder'),)", 'object_name': 'Bid'},
            'auction': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['bidding.Auction']"}),
            'bidder': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['bidding.Member']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'placed_amount': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'unixtime': ('django.db.models.fields.DecimalField', [], {'max_digits': '17', 'decimal_places': '5', 'db_index': 'True'}),
            'used_amount': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'bidding.bidpackage': {
            'Meta': {'object_name': 'BidPackage'},
            'bids': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'price': ('django.db.models.fields.IntegerField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '55'})
        },
        u'bidding.configkey': {
            'Meta': {'object_name': 'ConfigKey'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'bidding.converthistory': {
            'Meta': {'object_name': 'ConvertHistory'},
            'bids_amount': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'member': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['bidding.Member']"}),
            'tokens_amount': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True'}),
            'total_bids': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'total_bidsto': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'total_tokens': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'bidding.facebooklike': {
            'Meta': {'unique_together': "(['user_id', 'facebook_id'],)", 'object_name': 'FacebookLike'},
            'category': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'created_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'facebook_id': ('django.db.models.fields.BigIntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'user_id': ('django.db.models.fields.IntegerField', [], {})
        },
        u'bidding.facebookuser': {
            'Meta': {'unique_together': "(['user_id', 'facebook_id'],)", 'object_name': 'FacebookUser'},
            'facebook_id': ('django.db.models.fields.BigIntegerField', [], {}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'user_id': ('django.db.models.fields.IntegerField', [], {})
        },
        u'bidding.fborderinfo': {
            'Meta': {'object_name': 'FBOrderInfo'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'member': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['bidding.Member']"}),
            'package': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['bidding.BidPackage']"}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '25'})
        },
        u'bidding.invitation': {
            'Meta': {'object_name': 'Invitation'},
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invited_facebook_id': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'inviter': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['bidding.Member']"})
        },
        u'bidding.item': {
            'Meta': {'object_name': 'Item'},
            'category': ('django.db.models.fields.CharField', [], {'max_length': '5', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'retail_price': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'}),
            'specification': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'total_price': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'})
        },
        u'bidding.itemimage': {
            'Meta': {'object_name': 'ItemImage'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['bidding.Item']"})
        },
        u'bidding.member': {
            'Meta': {'object_name': 'Member'},
            'about_me': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'access_token': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'bids_left': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'bidsto_left': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'blog_url': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'date_of_birth': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'facebook_id': ('django.db.models.fields.BigIntegerField', [], {'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'facebook_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'facebook_profile_url': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'new_token_required': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'raw_data': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'remove_from_chat': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'tokens_left': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'website_url': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        u'bidding.prepromotedauction': {
            'Meta': {'ordering': "['-id']", 'object_name': 'PrePromotedAuction'},
            'bid_type': ('django.db.models.fields.CharField', [], {'default': "'bid'", 'max_length': '5'}),
            'bidding_time': ('django.db.models.fields.IntegerField', [], {'default': '10'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['bidding.Item']"}),
            'minimum_precap': ('django.db.models.fields.IntegerField', [], {'default': '5'}),
            'precap_bids': ('django.db.models.fields.IntegerField', [], {}),
            'saved_time': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'precap'", 'max_length': '15'}),
            'threshold1': ('django.db.models.fields.IntegerField', [], {'default': '12', 'null': 'True', 'blank': 'True'}),
            'threshold2': ('django.db.models.fields.IntegerField', [], {'default': '8', 'null': 'True', 'blank': 'True'}),
            'threshold3': ('django.db.models.fields.IntegerField', [], {'default': '5', 'null': 'True', 'blank': 'True'})
        },
        u'bidding.promotedauction': {
            'Meta': {'ordering': "['-id']", 'object_name': 'PromotedAuction', '_ormbases': [u'bidding.Auction']},
            u'auction_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['bidding.Auction']", 'unique': 'True', 'primary_key': 'True'}),
            'promoter': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'promoter_user'", 'to': u"orm['bidding.Member']"})
        },
        u'bidding.templateauction': {
            'Meta': {'object_name': 'TemplateAuction'},
            'fixture': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['bidding.AuctionFixture']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['bidding.Item']"}),
            'minimum_precap': ('django.db.models.fields.IntegerField', [], {'default': '5'}),
            'precap_bids': ('django.db.models.fields.IntegerField', [], {})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['bidding']