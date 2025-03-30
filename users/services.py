from .models import Notification

def create_notification(user, notification_type, title, message, url=''):
    """
    Создает новое уведомление для пользователя
    """
    return Notification.objects.create(
        recipient=user,
        notification_type=notification_type,
        title=title,
        message=message,
        url=url
    )

def get_unread_notifications_count(user):
    """
    Возвращает количество непрочитанных уведомлений для пользователя
    """
    return Notification.objects.filter(recipient=user, is_read=False).count()

def get_recent_notifications(user, limit=5):
    """
    Возвращает последние уведомления пользователя
    """
    return Notification.objects.filter(recipient=user).order_by('-created_at')[:limit]

def mark_all_as_read(user):
    """
    Отмечает все уведомления пользователя как прочитанные
    """
    Notification.objects.filter(recipient=user, is_read=False).update(is_read=True) 