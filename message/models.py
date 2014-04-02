from django.db import models

# Create your models here.
class EventLog(models.Model):
    event = models.TextField()
    data = models.TextField()
    sender = models.TextField()
    receiver = models.TextField()
    transport = models.TextField()
    timestamp = models.DateTimeField(null=True, blank=True)
    event_id = models.IntegerField(null=True)

    def saveEvent(self, event):
        self.event = event["event"]
        self.data = event["data"]
        self.sender = event["sender"]
        self.receiver = event["receiver"]
        self.transport = event["transport"]
        self.timestamp = event["timestamp"]
        self.event_id = event["id"]
        self.save()
