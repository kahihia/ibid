# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Member'
        db.create_table('bidding_member', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('bids_left', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('tokens_left', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('remove_from_chat', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('about_me', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('facebook_id', self.gf('django.db.models.fields.BigIntegerField')(unique=True, null=True, blank=True)),
            ('access_token', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('facebook_name', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('facebook_profile_url', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('website_url', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('blog_url', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=255, null=True, blank=True)),
            ('date_of_birth', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('raw_data', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('bidding', ['Member'])

        # Adding model 'Item'
        db.create_table('bidding_item', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('category', self.gf('django.db.models.fields.CharField')(max_length=5, null=True, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50)),
            ('retail_price', self.gf('django.db.models.fields.DecimalField')(max_digits=10, decimal_places=2)),
            ('total_price', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=2, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('specification', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('bidding', ['Item'])

        # Adding model 'ItemImage'
        db.create_table('bidding_itemimage', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('item', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['bidding.Item'])),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
        ))
        db.send_create_signal('bidding', ['ItemImage'])

        # Adding model 'Auction'
        db.create_table('bidding_auction', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('item', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['bidding.Item'])),
            ('precap_bids', self.gf('django.db.models.fields.IntegerField')()),
            ('minimum_precap', self.gf('django.db.models.fields.IntegerField')(default=5)),
            ('bid_type', self.gf('django.db.models.fields.CharField')(default='bid', max_length=5)),
            ('status', self.gf('django.db.models.fields.CharField')(default='precap', max_length=15)),
            ('bidding_time', self.gf('django.db.models.fields.IntegerField')(default=10)),
            ('saved_time', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('won_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('winner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('won_price', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=2, blank=True)),
            ('start_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('threshold1', self.gf('django.db.models.fields.IntegerField')(default=7, null=True, blank=True)),
            ('threshold2', self.gf('django.db.models.fields.IntegerField')(default=5, null=True, blank=True)),
            ('threshold3', self.gf('django.db.models.fields.IntegerField')(default=3, null=True, blank=True)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('bidding', ['Auction'])

        # Adding M2M table for field bidders on 'Auction'
        db.create_table('bidding_auction_bidders', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('auction', models.ForeignKey(orm['bidding.auction'], null=False)),
            ('member', models.ForeignKey(orm['bidding.member'], null=False))
        ))
        db.create_unique('bidding_auction_bidders', ['auction_id', 'member_id'])

        # Adding model 'AuctionFixture'
        db.create_table('bidding_auctionfixture', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('bid_type', self.gf('django.db.models.fields.CharField')(default='bid', max_length=5)),
            ('automatic', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('threshold', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=5)),
        ))
        db.send_create_signal('bidding', ['AuctionFixture'])

        # Adding model 'TemplateAuction'
        db.create_table('bidding_templateauction', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('item', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['bidding.Item'])),
            ('precap_bids', self.gf('django.db.models.fields.IntegerField')()),
            ('minimum_precap', self.gf('django.db.models.fields.IntegerField')(default=5)),
            ('fixture', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['bidding.AuctionFixture'])),
        ))
        db.send_create_signal('bidding', ['TemplateAuction'])

        # Adding model 'Bid'
        db.create_table('bidding_bid', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('auction', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['bidding.Auction'])),
            ('bidder', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['bidding.Member'])),
            ('unixtime', self.gf('django.db.models.fields.DecimalField')(max_digits=17, decimal_places=5, db_index=True)),
            ('placed_amount', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('used_amount', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('bidding', ['Bid'])

        # Adding unique constraint on 'Bid', fields ['auction', 'bidder']
        db.create_unique('bidding_bid', ['auction_id', 'bidder_id'])

        # Adding model 'BidPackage'
        db.create_table('bidding_bidpackage', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=55)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('price', self.gf('django.db.models.fields.IntegerField')()),
            ('bids', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal('bidding', ['BidPackage'])

        # Adding model 'AuctionInvoice'
        db.create_table('bidding_auctioninvoice', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('auction', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['bidding.Auction'])),
            ('member', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['bidding.Member'])),
            ('status', self.gf('django.db.models.fields.CharField')(default='created', max_length=55)),
            ('payment', self.gf('django.db.models.fields.CharField')(default='direct', max_length=55)),
            ('uid', self.gf('django.db.models.fields.CharField')(max_length=40, db_index=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal('bidding', ['AuctionInvoice'])

        # Adding model 'AuctionInvitation'
        db.create_table('bidding_auctioninvitation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('inviter', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['bidding.Member'])),
            ('request_id', self.gf('django.db.models.fields.BigIntegerField')()),
            ('auction', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['bidding.Auction'])),
        ))
        db.send_create_signal('bidding', ['AuctionInvitation'])

    def backwards(self, orm):
        # Removing unique constraint on 'Bid', fields ['auction', 'bidder']
        db.delete_unique('bidding_bid', ['auction_id', 'bidder_id'])

        # Deleting model 'Member'
        db.delete_table('bidding_member')

        # Deleting model 'Item'
        db.delete_table('bidding_item')

        # Deleting model 'ItemImage'
        db.delete_table('bidding_itemimage')

        # Deleting model 'Auction'
        db.delete_table('bidding_auction')

        # Removing M2M table for field bidders on 'Auction'
        db.delete_table('bidding_auction_bidders')

        # Deleting model 'AuctionFixture'
        db.delete_table('bidding_auctionfixture')

        # Deleting model 'TemplateAuction'
        db.delete_table('bidding_templateauction')

        # Deleting model 'Bid'
        db.delete_table('bidding_bid')

        # Deleting model 'BidPackage'
        db.delete_table('bidding_bidpackage')

        # Deleting model 'AuctionInvoice'
        db.delete_table('bidding_auctioninvoice')

        # Deleting model 'AuctionInvitation'
        db.delete_table('bidding_auctioninvitation')

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
        'bidding.auction': {
            'Meta': {'ordering': "['-id']", 'object_name': 'Auction'},
            'bid_type': ('django.db.models.fields.CharField', [], {'default': "'bid'", 'max_length': '5'}),
            'bidders': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['bidding.Member']", 'null': 'True', 'blank': 'True'}),
            'bidding_time': ('django.db.models.fields.IntegerField', [], {'default': '10'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['bidding.Item']"}),
            'minimum_precap': ('django.db.models.fields.IntegerField', [], {'default': '5'}),
            'precap_bids': ('django.db.models.fields.IntegerField', [], {}),
            'saved_time': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'start_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'precap'", 'max_length': '15'}),
            'threshold1': ('django.db.models.fields.IntegerField', [], {'default': '7', 'null': 'True', 'blank': 'True'}),
            'threshold2': ('django.db.models.fields.IntegerField', [], {'default': '5', 'null': 'True', 'blank': 'True'}),
            'threshold3': ('django.db.models.fields.IntegerField', [], {'default': '3', 'null': 'True', 'blank': 'True'}),
            'winner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'won_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'won_price': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'})
        },
        'bidding.auctionfixture': {
            'Meta': {'object_name': 'AuctionFixture'},
            'automatic': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'bid_type': ('django.db.models.fields.CharField', [], {'default': "'bid'", 'max_length': '5'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'threshold': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '5'})
        },
        'bidding.auctioninvitation': {
            'Meta': {'object_name': 'AuctionInvitation'},
            'auction': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['bidding.Auction']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inviter': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['bidding.Member']"}),
            'request_id': ('django.db.models.fields.BigIntegerField', [], {})
        },
        'bidding.auctioninvoice': {
            'Meta': {'object_name': 'AuctionInvoice'},
            'auction': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['bidding.Auction']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'member': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['bidding.Member']"}),
            'payment': ('django.db.models.fields.CharField', [], {'default': "'direct'", 'max_length': '55'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'created'", 'max_length': '55'}),
            'uid': ('django.db.models.fields.CharField', [], {'max_length': '40', 'db_index': 'True'})
        },
        'bidding.bid': {
            'Meta': {'unique_together': "(('auction', 'bidder'),)", 'object_name': 'Bid'},
            'auction': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['bidding.Auction']"}),
            'bidder': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['bidding.Member']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'placed_amount': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'unixtime': ('django.db.models.fields.DecimalField', [], {'max_digits': '17', 'decimal_places': '5', 'db_index': 'True'}),
            'used_amount': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'bidding.bidpackage': {
            'Meta': {'object_name': 'BidPackage'},
            'bids': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'price': ('django.db.models.fields.IntegerField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '55'})
        },
        'bidding.item': {
            'Meta': {'object_name': 'Item'},
            'category': ('django.db.models.fields.CharField', [], {'max_length': '5', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'retail_price': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'}),
            'specification': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'total_price': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'})
        },
        'bidding.itemimage': {
            'Meta': {'object_name': 'ItemImage'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['bidding.Item']"})
        },
        'bidding.member': {
            'Meta': {'object_name': 'Member'},
            'about_me': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'access_token': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'bids_left': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'blog_url': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'date_of_birth': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'facebook_id': ('django.db.models.fields.BigIntegerField', [], {'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'facebook_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'facebook_profile_url': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'raw_data': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'remove_from_chat': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'tokens_left': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'website_url': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        'bidding.templateauction': {
            'Meta': {'object_name': 'TemplateAuction'},
            'fixture': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['bidding.AuctionFixture']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['bidding.Item']"}),
            'minimum_precap': ('django.db.models.fields.IntegerField', [], {'default': '5'}),
            'precap_bids': ('django.db.models.fields.IntegerField', [], {})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['bidding']