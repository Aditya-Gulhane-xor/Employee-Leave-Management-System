from .models import Notification

def unread_notifications_count(request):
    """Adds the count of unread notifications to all templates."""
    if request.user.is_authenticated:
        count = Notification.objects.filter(recipient=request.user, is_read=False).count()
        return {'unread_count': count}
    return {'unread_count': 0}