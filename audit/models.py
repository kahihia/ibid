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
            # Make a dict from the models fields
            data = {}
            fields = [ str(x.name) for x in self._meta.fields ]
            for field_name in fields:
                field = self._meta.get_field_by_name(field_name)[0]
                data[field_name] = self.to_python(field.value_from_object(self))

            l = Log()
            l.action = action
            l.object_app = self._meta.app_label
            l.object_model = self._meta.object_name
            l.object_pk = self.pk
            l.data = json.dumps(data)
            l.save()


class Log(models.Model):
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
