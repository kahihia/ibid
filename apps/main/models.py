from django.db import models
from datetime import datetime
from bidding.models import Member

NOTIFICATION_TYPES = (('FinishedAuction' , 'FinishedAuction'),
                    ('',''))

class Notification(models.Model):
    to = models.ForeignKey(Member, related_name='notifications_recieved')
    n_from = models.ForeignKey(Member, related_name='notifications_sent', null=True)
    n_type = models.CharField(choices=NOTIFICATION_TYPES, null=False, blank=False, max_length=25, default='text')
    message = models.TextField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(default='Unread', max_length=20)
    
    def __unicode__(self):
        return "To: %s, From: $s, Message: %s" % (self.To, self.From, self.Message)
