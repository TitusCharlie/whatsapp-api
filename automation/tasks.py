from celery import shared_task
import pywhatkit as kit
from .models import BroadcastMessage

@shared_task
def send_message(phone, message):
    try:
        kit.sendwhatmsg_instantly(phone, message)
        print(f"Message sent to {phone}")
    except Exception as e:
        print(f"Failed to send message to {phone}: {str(e)}")

@shared_task
def send_broadcast(broadcast_id):
    broadcast = BroadcastMessage.objects.get(id=broadcast_id)
    for contact in broadcast.contacts.all():
        send_message.apply_async((contact.phone, broadcast.message), countdown=5)
