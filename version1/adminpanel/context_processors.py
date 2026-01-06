from userpanel.models import ContactMessage

def latest_messages_context(request):
    latest_messages = ContactMessage.objects.order_by('-created_at')[:3]
    return {'latest_messages': latest_messages}