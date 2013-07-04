# -*- coding: utf-8 -*-

import json
from django.db import models
from django.conf import settings


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
# TODO: cambiar por la busqueda de campos
            data = self.to_dict()
            a = Audit()
            a.action = action
            a.object_app = self._meta.app_label
            a.object_model = self._meta.object_name
            a.object_pk = self.pk
            a.data = json.dumps(data)
            a.save()


class Audit(models.Model):
    timestamp = models.DateTimeField(auto_now=True, auto_now_add=True)
    object_app = models.CharField(max_length=100)
    object_model = models.CharField(max_length=100)
    object_pk = models.IntegerField(null=True)
    action = models.CharField(max_length=10)
    data = models.CharField(max_length=200)

    def __unicode__(self):
        return '%s.%s [%d] - %s @ %s' % (self.object_app, self.object_model,
                                         self.object_id, self.action,
                                         self.timestamp)
