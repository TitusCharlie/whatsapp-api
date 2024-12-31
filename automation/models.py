from django.db import models


class ContactList(models.Model):
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    
    def __str__(self):
        return f'{self.name} - {self.phone}'

class BroadcastMessage(models.Model):
    message = models.TextField()
    contacts = models.ManyToManyField(ContactList)
    scheduled_time = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f'Broadcast at {self.scheduled_time}'

