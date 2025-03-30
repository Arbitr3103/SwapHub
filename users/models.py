from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse

# Create your models here.

from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator

def validate_avatar_size(value):
    filesize = value.size
    if filesize > 5 * 1024 * 1024:  # 5MB
        raise ValidationError('Максимальный размер файла 5MB')

def validate_phone_number(value):
    if value:
        # Удаляем все нецифровые символы
        phone = ''.join(filter(str.isdigit, value))
        if len(phone) < 10 or len(phone) > 15:
            raise ValidationError('Неверный формат номера телефона')

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif']),
            validate_avatar_size
        ],
        verbose_name='Фотография профиля'
    )
    bio = models.TextField(max_length=500, blank=True, verbose_name='О себе')
    location = models.CharField(max_length=100, blank=True, verbose_name='Местоположение')
    phone = models.CharField(max_length=20, blank=True, validators=[validate_phone_number], verbose_name='Телефон')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    def clean(self):
        super().clean()
        if self.phone:
            self.phone = ''.join(filter(str.isdigit, self.phone))

    def __str__(self):
        return f'Профиль пользователя {self.user.username}'

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        Profile.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class Friendship(models.Model):
    STATUS_CHOICES = (
        ('pending', 'В ожидании'),
        ('accepted', 'Принято'),
        ('rejected', 'Отклонено'),
    )
    
    from_user = models.ForeignKey(User, related_name='friendship_requests_sent', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='friendship_requests_received', on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('from_user', 'to_user')
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.from_user.username} -> {self.to_user.username}: {self.get_status_display()}'
    
    def accept(self):
        if self.status == 'pending':
            self.status = 'accepted'
            self.save()
    
    def reject(self):
        if self.status == 'pending':
            self.status = 'rejected'
            self.save()
    
    def remove(self):
        """Удалить дружбу"""
        self.delete()

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('rental_request', 'Запрос аренды'),
        ('rental_approved', 'Аренда одобрена'),
        ('rental_rejected', 'Аренда отклонена'),
        ('exchange_request', 'Запрос обмена'),
        ('exchange_approved', 'Обмен одобрен'),
        ('exchange_rejected', 'Обмен отклонен'),
        ('friend_request', 'Запрос дружбы'),
        ('friend_accepted', 'Запрос дружбы принят'),
        ('message', 'Сообщение'),
    )

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=100)
    message = models.TextField()
    url = models.CharField(max_length=255, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Уведомление для {self.recipient.username}: {self.title}'

    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.save()

    @property
    def short_message(self):
        return self.message[:50] + '...' if len(self.message) > 50 else self.message
