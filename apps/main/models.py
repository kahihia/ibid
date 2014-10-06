from django.db import models
from datetime import datetime
from bidding.models import Member

NOTIFICATION_TYPES = (('FinishedAuction' , 'FinishedAuction'),
                    ('',''))

class Notification(models.Model):
    recipient = models.ForeignKey(Member, related_name='notifications_recieved')
    sender = models.ForeignKey(Member, related_name='notifications_sent', null=True, blank=True)
    notification_type = models.CharField(choices=NOTIFICATION_TYPES, null=False, blank=False, max_length=25, default='text')
    message = models.TextField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(default='Unread', max_length=20)
    
    def __unicode__(self):
        return "To: %s, From: %s, Message: %s" % (self.recipient, self.sender, self.message)

class Survey(models.Model):
    
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(auto_now=True)
    reward= models.CharField(max_length=20)
    survey_image = models.ImageField(upload_to='bid_packages/', blank=True, null=True)
    detail_image = models.ImageField(upload_to='bid_packages/', blank=True, null=True)
    num_questions = models.IntegerField()
    
class Question(models.Model):

    survey = models.ForeignKey(Survey, related_name='questions',null=True,blank=True)
    question = models.CharField(max_length=255)
    options = models.CharField(max_length=255)
    type = models.IntegerField()
    number = models.IntegerField()
    
    def toDict(self):
        import json
        dic = {}
        dic['type'] = self.type
        dic['question_id'] = self.id
        dic['question'] = self.question
        dic['question_number'] = self.number
        dic['images'] = list(self.images.values_list('image', flat=True))
        if self.options:
            dic['options'] = json.loads(self.options)
        return dic
    
class Image(models.Model):
    
    image = models.ImageField(upload_to='bid_packages/', blank=True, null=True)
    question = models.ForeignKey(Question, related_name='images',null=True,blank=True)
    
class Answer(models.Model):
    
    image = models.ImageField(upload_to='bid_packages/', blank=True, null=True)
    question = models.ForeignKey(Question, related_name='answers',null=True,blank=True)
    answer = models.CharField(max_length=255)
    checked = models.BooleanField(default=False)