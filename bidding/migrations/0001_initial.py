# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Member'
        db.create_table(u'bidding_member', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('last_login', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('is_superuser', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('username', self.gf('django.db.models.fields.CharField')(unique=True, max_length=30)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, blank=True)),
            ('is_staff', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('date_joined', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('about_me', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('facebook_id', self.gf('django.db.models.fields.BigIntegerField')(unique=True, null=True, blank=True)),
            ('access_token', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('facebook_name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('facebook_profile_url', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('website_url', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('blog_url', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('date_of_birth', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('gender', self.gf('django.db.models.fields.CharField')(max_length=1, null=True, blank=True)),
            ('raw_data', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('facebook_open_graph', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('new_token_required', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=255, null=True, blank=True)),
            ('bids_left', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('tokens_left', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('bidsto_left', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('session', self.gf('django.db.models.fields.TextField')(default='{}')),
            ('remove_from_chat', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'bidding', ['Member'])

        # Adding M2M table for field groups on 'Member'
        db.create_table(u'bidding_member_groups', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('member', models.ForeignKey(orm[u'bidding.member'], null=False)),
            ('group', models.ForeignKey(orm[u'auth.group'], null=False))
        ))
        db.create_unique(u'bidding_member_groups', ['member_id', 'group_id'])

        # Adding M2M table for field user_permissions on 'Member'
        db.create_table(u'bidding_member_user_permissions', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('member', models.ForeignKey(orm[u'bidding.member'], null=False)),
            ('permission', models.ForeignKey(orm[u'auth.permission'], null=False))
        ))
        db.create_unique(u'bidding_member_user_permissions', ['member_id', 'permission_id'])

        # Adding model 'Item'
        db.create_table(u'bidding_item', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('category', self.gf('django.db.models.fields.CharField')(max_length=5, null=True, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50)),
            ('retail_price', self.gf('django.db.models.fields.DecimalField')(max_digits=10, decimal_places=2)),
            ('total_price', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=2, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('specification', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'bidding', ['Item'])

        # Adding model 'ItemImage'
        db.create_table(u'bidding_itemimage', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('item', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['bidding.Item'])),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
        ))
        db.send_create_signal(u'bidding', ['ItemImage'])

        # Adding model 'Auction'
        db.create_table(u'bidding_auction', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('item', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['bidding.Item'])),
            ('precap_bids', self.gf('django.db.models.fields.IntegerField')()),
            ('minimum_precap', self.gf('django.db.models.fields.IntegerField')(default=10)),
            ('bid_type', self.gf('django.db.models.fields.CharField')(default='bid', max_length=5)),
            ('status', self.gf('django.db.models.fields.CharField')(default='precap', max_length=15)),
            ('bidding_time', self.gf('django.db.models.fields.IntegerField')(default=10)),
            ('saved_time', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('always_alive', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('won_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('winner', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='autcions', null=True, to=orm['bidding.Member'])),
            ('won_price', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=2, blank=True)),
            ('start_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('threshold1', self.gf('django.db.models.fields.IntegerField')(default=7, null=True, blank=True)),
            ('threshold2', self.gf('django.db.models.fields.IntegerField')(default=5, null=True, blank=True)),
            ('threshold3', self.gf('django.db.models.fields.IntegerField')(default=3, null=True, blank=True)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'bidding', ['Auction'])

        # Adding M2M table for field bidders on 'Auction'
        db.create_table(u'bidding_auction_bidders', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('auction', models.ForeignKey(orm[u'bidding.auction'], null=False)),
            ('member', models.ForeignKey(orm[u'bidding.member'], null=False))
        ))
        db.create_unique(u'bidding_auction_bidders', ['auction_id', 'member_id'])

        # Adding model 'PrePromotedAuction'
        db.create_table(u'bidding_prepromotedauction', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('item', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['bidding.Item'])),
            ('precap_bids', self.gf('django.db.models.fields.IntegerField')()),
            ('minimum_precap', self.gf('django.db.models.fields.IntegerField')(default=10)),
            ('bid_type', self.gf('django.db.models.fields.CharField')(default='bid', max_length=5)),
            ('status', self.gf('django.db.models.fields.CharField')(default='precap', max_length=15)),
            ('bidding_time', self.gf('django.db.models.fields.IntegerField')(default=10)),
            ('saved_time', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('threshold1', self.gf('django.db.models.fields.IntegerField')(default=12, null=True, blank=True)),
            ('threshold2', self.gf('django.db.models.fields.IntegerField')(default=8, null=True, blank=True)),
            ('threshold3', self.gf('django.db.models.fields.IntegerField')(default=5, null=True, blank=True)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'bidding', ['PrePromotedAuction'])

        # Adding model 'PromotedAuction'
        db.create_table(u'bidding_promotedauction', (
            (u'auction_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['bidding.Auction'], unique=True, primary_key=True)),
            ('promoter', self.gf('django.db.models.fields.related.ForeignKey')(related_name='promoter_user', to=orm['bidding.Member'])),
        ))
        db.send_create_signal(u'bidding', ['PromotedAuction'])

        # Adding model 'Bid'
        db.create_table(u'bidding_bid', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('auction', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['bidding.Auction'])),
            ('bidder', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['bidding.Member'])),
            ('unixtime', self.gf('django.db.models.fields.DecimalField')(max_digits=17, decimal_places=5, db_index=True)),
            ('placed_amount', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('used_amount', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal(u'bidding', ['Bid'])

        # Adding unique constraint on 'Bid', fields ['auction', 'bidder']
        db.create_unique(u'bidding_bid', ['auction_id', 'bidder_id'])

        # Adding model 'BidPackage'
        db.create_table(u'bidding_bidpackage', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=55)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('price', self.gf('django.db.models.fields.IntegerField')()),
            ('bids', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal(u'bidding', ['BidPackage'])

        # Adding model 'AuctionInvoice'
        db.create_table(u'bidding_auctioninvoice', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('auction', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['bidding.Auction'])),
            ('member', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['bidding.Member'])),
            ('status', self.gf('django.db.models.fields.CharField')(default='created', max_length=55)),
            ('payment', self.gf('django.db.models.fields.CharField')(default='direct', max_length=55)),
            ('uid', self.gf('django.db.models.fields.CharField')(max_length=40, db_index=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal(u'bidding', ['AuctionInvoice'])

        # Adding model 'Invitation'
        db.create_table(u'bidding_invitation', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('inviter', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['bidding.Member'])),
            ('invited_facebook_id', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('deleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'bidding', ['Invitation'])

        # Adding model 'AuctionInvitation'
        db.create_table(u'bidding_auctioninvitation', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('inviter', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['bidding.Member'])),
            ('request_id', self.gf('django.db.models.fields.BigIntegerField')()),
            ('auction', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['bidding.Auction'])),
        ))
        db.send_create_signal(u'bidding', ['AuctionInvitation'])

        # Adding model 'ConvertHistory'
        db.create_table(u'bidding_converthistory', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('member', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['bidding.Member'])),
            ('tokens_amount', self.gf('django.db.models.fields.IntegerField')(default=0, null=True)),
            ('bids_amount', self.gf('django.db.models.fields.IntegerField')(default=0, null=True)),
            ('total_tokens', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('total_bids', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('total_bidsto', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'bidding', ['ConvertHistory'])

        # Adding model 'FBOrderInfo'
        db.create_table(u'bidding_fborderinfo', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('member', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['bidding.Member'])),
            ('package', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['bidding.BidPackage'])),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=25)),
            ('fb_payment_id', self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
        ))
        db.send_create_signal(u'bidding', ['FBOrderInfo'])

        # Adding model 'ConfigKey'
        db.create_table(u'bidding_configkey', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('value', self.gf('django.db.models.fields.TextField')()),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('value_type', self.gf('django.db.models.fields.CharField')(default='text', max_length=10)),
        ))
        db.send_create_signal(u'bidding', ['ConfigKey'])


    def backwards(self, orm):
        # Removing unique constraint on 'Bid', fields ['auction', 'bidder']
        db.delete_unique(u'bidding_bid', ['auction_id', 'bidder_id'])

        # Deleting model 'Member'
        db.delete_table(u'bidding_member')

        # Removing M2M table for field groups on 'Member'
        db.delete_table('bidding_member_groups')

        # Removing M2M table for field user_permissions on 'Member'
        db.delete_table('bidding_member_user_permissions')

        # Deleting model 'Item'
        db.delete_table(u'bidding_item')

        # Deleting model 'ItemImage'
        db.delete_table(u'bidding_itemimage')

        # Deleting model 'Auction'
        db.delete_table(u'bidding_auction')

        # Removing M2M table for field bidders on 'Auction'
        db.delete_table('bidding_auction_bidders')

        # Deleting model 'PrePromotedAuction'
        db.delete_table(u'bidding_prepromotedauction')

        # Deleting model 'PromotedAuction'
        db.delete_table(u'bidding_promotedauction')

        # Deleting model 'Bid'
        db.delete_table(u'bidding_bid')

        # Deleting model 'BidPackage'
        db.delete_table(u'bidding_bidpackage')

        # Deleting model 'AuctionInvoice'
        db.delete_table(u'bidding_auctioninvoice')

        # Deleting model 'Invitation'
        db.delete_table(u'bidding_invitation')

        # Deleting model 'AuctionInvitation'
        db.delete_table(u'bidding_auctioninvitation')

        # Deleting model 'ConvertHistory'
        db.delete_table(u'bidding_converthistory')

        # Deleting model 'FBOrderInfo'
        db.delete_table(u'bidding_fborderinfo')

        # Deleting model 'ConfigKey'
        db.delete_table(u'bidding_configkey')


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
        u'bidding.auction': {
            'Meta': {'ordering': "['-id']", 'object_name': 'Auction'},
            'always_alive': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'bid_type': ('django.db.models.fields.CharField', [], {'default': "'bid'", 'max_length': '5'}),
            'bidders': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['bidding.Member']", 'null': 'True', 'blank': 'True'}),
            'bidding_time': ('django.db.models.fields.IntegerField', [], {'default': '10'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['bidding.Item']"}),
            'minimum_precap': ('django.db.models.fields.IntegerField', [], {'default': '10'}),
            'precap_bids': ('django.db.models.fields.IntegerField', [], {}),
            'saved_time': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'start_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'precap'", 'max_length': '15'}),
            'threshold1': ('django.db.models.fields.IntegerField', [], {'default': '7', 'null': 'True', 'blank': 'True'}),
            'threshold2': ('django.db.models.fields.IntegerField', [], {'default': '5', 'null': 'True', 'blank': 'True'}),
            'threshold3': ('django.db.models.fields.IntegerField', [], {'default': '3', 'null': 'True', 'blank': 'True'}),
            'winner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'autcions'", 'null': 'True', 'to': u"orm['bidding.Member']"}),
            'won_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'won_price': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'})
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
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'value': ('django.db.models.fields.TextField', [], {}),
            'value_type': ('django.db.models.fields.CharField', [], {'default': "'text'", 'max_length': '10'})
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
        u'bidding.fborderinfo': {
            'Meta': {'object_name': 'FBOrderInfo'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'fb_payment_id': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
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
            'about_me': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'access_token': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'bids_left': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'bidsto_left': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'blog_url': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'date_of_birth': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'facebook_id': ('django.db.models.fields.BigIntegerField', [], {'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'facebook_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'facebook_open_graph': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'facebook_profile_url': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'new_token_required': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'raw_data': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'remove_from_chat': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'session': ('django.db.models.fields.TextField', [], {'default': "'{}'"}),
            'tokens_left': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'}),
            'website_url': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        u'bidding.prepromotedauction': {
            'Meta': {'ordering': "['-id']", 'object_name': 'PrePromotedAuction'},
            'bid_type': ('django.db.models.fields.CharField', [], {'default': "'bid'", 'max_length': '5'}),
            'bidding_time': ('django.db.models.fields.IntegerField', [], {'default': '10'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['bidding.Item']"}),
            'minimum_precap': ('django.db.models.fields.IntegerField', [], {'default': '10'}),
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
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['bidding']