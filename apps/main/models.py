from django.db import models
from datetime import datetime
from bidding.models import Member

NOTIFICATION_TYPES = (('FinishedAuction' , 'FinishedAuction'),
                    ('',''))

class Notification(models.Model):
    To = models.ForeignKey(Member)
    From = models.ForeignKey(Member,related_name='notifications', null=True)
    Type = models.CharField(choices=NOTIFICATION_TYPES, null=False, blank=False, max_length=10, default='text')
    Message = models.TextField(null=True, blank=True)
    Created = models.DateTimeField(default=datetime.now)
    Read = models.DateTimeField(default=None, null=True)
    
    def __unicode__(self):
        return "To: %s, From: $s, Message: %s" % (self.To, self.From, self.Message)
