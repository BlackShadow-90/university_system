"""
Context processors for the core app
"""
from django.utils.translation import gettext_lazy as _
from apps.announcements.models import Announcement
from apps.notifications.models import Notification
from apps.semesters.models import Semester


def site_settings(request):
    """Add site-wide context variables"""
    context = {
        'site_name': _('University Academic Performance System'),
    }
    
    # Add current semester if available
    try:
        current_semester = Semester.objects.filter(is_active=True).first()
        context['current_semester'] = current_semester
    except:
        pass
    
    # Add unread notification count for logged-in users
    if request.user.is_authenticated:
        unread_count = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).count()
        context['unread_notifications'] = unread_count
        
        # Add latest announcements
        context['latest_announcements'] = Announcement.objects.filter(
            is_active=True
        ).select_related('published_by')[:5]
    
    return context
