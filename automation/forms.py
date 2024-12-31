from django import forms
from .models import ContactList, BroadcastMessage

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactList
        fields = ['name', 'phone_number', 'email']  # Replace with actual fields from the Contact model

class BroadcastForm(forms.ModelForm):
    class Meta:
        model = BroadcastMessage
        fields = ['message', 'contacts', 'scheduled_time']  # Replace with actual fields from the Broadcast model