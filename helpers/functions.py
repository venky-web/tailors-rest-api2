from django.utils import timezone


def get_current_time():
    """returns current time"""
    now = timezone.now().isoformat()
    return now
