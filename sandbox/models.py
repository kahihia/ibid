import json
from django.db import models
from django.conf import settings

from bidding.models import Member


class Notification(models.Model):
    to = models.ForeignKey(Member)
    message = models.TextField()
    status = models.CharField(max_length=20)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)


class AuditedModel(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        super(AuditedModel, self).save(*args, **kwargs)
        self._audit('save')

    def delete(self, *args, **kwargs):
        self._audit('delete')
        super(AuditedModel, self).delete(*args, **kwargs)

    def _audit(self, action):
        if settings.AUDIT_ENABLED:
            data = self.to_dict()
            a = Audit()
            a.model = self.__class__.__name__
            a.object_id = data['id']
            a.action = action
            a.data = json.dumps(data)
            a.save()


class Item(AuditedModel):
    name = models.CharField(max_length=20)
    counter = models.IntegerField(default=0, blank=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'counter': self.counter,
        }

    def __unicode__(self):
        return self.name


class User(AuditedModel):
    name = models.CharField(max_length=20)
    email = models.EmailField()

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
        }

    def __unicode__(self):
        return self.name


class Audit(models.Model):
    timestamp = models.DateTimeField(auto_now=True, auto_now_add=True)
    model = models.CharField(max_length=20)
    object_id = models.IntegerField(null=True)
    action = models.CharField(max_length=10)
    data = models.CharField(max_length=200)

    def __unicode__(self):
        return '%s %s [%d] @ %s' % (self.action, self.model, self.object_id, self.timestamp)
