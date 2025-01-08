# from django.shortcuts import render
# from django.http import JsonResponse
# from .models import ContactList, BroadcastMessage
# from .tasks import send_broadcast
# from datetime import datetime

# def create_contact(request):
#     if request.method == 'POST':
#         name = request.POST.get('name')
#         phone = request.POST.get('phone')
#         email = request.POST.get('email')
        
#         contact = ContactList(name=name, phone=phone, email=email)
#         contact.save()
#         return JsonResponse({'message': 'Contact created successfully!'})

# def schedule_broadcast(request):
#     if request.method == 'POST':
#         message = request.POST.get('message')
#         contact_ids = request.POST.getlist('contacts')
#         scheduled_time = request.POST.get('scheduled_time', None)
        
#         if scheduled_time:
#             scheduled_time = datetime.fromisoformat(scheduled_time)
        
#         broadcast = BroadcastMessage(message=message, scheduled_time=scheduled_time)
#         broadcast.save()
#         broadcast.contacts.set(contact_ids)
        
#         # Schedule the task
#         if scheduled_time:
#             delay = (scheduled_time - datetime.now()).total_seconds()
#             send_broadcast.apply_async((broadcast.id,), countdown=delay)
#         else:
#             send_broadcast.apply_async((broadcast.id,))
        
#         return JsonResponse({'message': 'Broadcast scheduled successfully!'})

from django.http import JsonResponse
from django.shortcuts import render
from .forms import ContactForm, BroadcastForm
from .models import Contact, MessageLog

def create_contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'message': 'Contact created successfully!'})
    else:
        form = ContactForm()
    return render(request, 'create_contact.html', {'form': form})

def schedule_broadcast(request):
    if request.method == 'POST':
        form = BroadcastForm(request.POST)
        if form.is_valid():
            broadcast = form.save(commit=False)
            broadcast.save()
            form.save_m2m()
            return JsonResponse({'message': 'Broadcast scheduled successfully!'})
    else:
        form = BroadcastForm()
    return render(request, 'schedule_broadcast.html', {'form': form})

def get_analytics(request):
    total_contacts = Contact.objects.count()
    total_messages = MessageLog.objects.count()
    response_rate = 0
    if total_messages > 0:
        responses = MessageLog.objects.filter(is_response=True).count()
        response_rate = (responses / total_messages) * 100

    data = {
        "total_contacts": total_contacts,
        "total_messages": total_messages,
        "response_rate": round(response_rate, 2),
    }
    return JsonResponse(data)

def dashboard(request):
    return render(request, 'index.html')  # Replace with your template file