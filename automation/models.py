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

class Contact(models.Model):
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20, unique=True)
    email = models.EmailField(max_length=255, blank=True, null=True)
    country_code = models.CharField(max_length=10, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name


class MessageLog(models.Model):
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name='messages')
    message_content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    is_response = models.BooleanField(default=False)

    def __str__(self):
        return f"Message to {self.contact.full_name} at {self.sent_at}"