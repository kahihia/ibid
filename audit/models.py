# -*- coding: utf-8 -*-

from django.db import models
from django.conf import settings
from django.core import serializers


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
        try:
            if settings.AUDIT_ENABLED:
                l = Log()
                l.action = action
                l.object_app = self._meta.app_label
                l.object_model = self._meta.object_name
                l.object_pk = self.pk
                l.data = serializers.serialize('json', (self,))
                l.save()
        except AttributeError:
            # AUDIT_ENABLED option not defined in any settings
            pass


class Log(models.Model):
    timestamp = models.DateTimeField(auto_now=True, auto_now_add=True)
    action = models.CharField(max_length=10)
    object_app = models.CharField(max_length=100)
    object_model = models.CharField(max_length=100)
    object_pk = models.IntegerField(null=True)
    data = models.CharField(max_length=200)

    def __unicode__(self):
        return '%s.%s [%d] - %s @ %s' % (self.object_app, self.object_model,
                                         self.object_pk, self.action,
                                         self.timestamp)
