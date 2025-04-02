# items/models.py

from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
import os
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile

class Item(models.Model):
    CATEGORY_CHOICES = [
        ('electronics', 'Электроника'),
        ('clothing', 'Одежда'),
        ('sports', 'Спорт и отдых'),
        ('tools', 'Инструменты'),
        ('home', 'Товары для дома'),
        ('books', 'Книги'),
        ('toys', 'Игрушки'),
        ('vehicles', 'Транспорт'),
        ('other', 'Другое'),
    ]
    
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='items')
    title = models.CharField(max_length=255, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES, default='other', verbose_name='Категория')
    rental_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена аренды (руб/день)')
    location = models.CharField(max_length=255, blank=True, help_text="Город или адрес", verbose_name='Местоположение')
    is_available = models.BooleanField(default=True, verbose_name='Доступна для аренды')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    view_count = models.PositiveIntegerField(default=0, verbose_name='Количество просмотров')

    def __str__(self):
        return self.title

    @property
    def approved_rental_requests(self):
        return self.rental_requests.filter(status='approved')

    @property
    def average_rating(self):
        reviews = self.reviews.all()
        if not reviews:
            return 0
        return sum(review.rating for review in reviews) / len(reviews)

    @property
    def reviews_count(self):
        return self.reviews.count()


class RentalRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='rental_requests')
    renter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rental_requests')
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Rental Request for {self.item.title} by {self.renter.username}"

class ExchangeRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    # Вещь, которую запрашивает пользователь (то, что принадлежит владельцу)
    requested_item = models.ForeignKey('Item', on_delete=models.CASCADE, related_name='exchange_requests_received')
    # Вещь, которую предлагает пользователь (предлагается обменять)
    offered_item = models.ForeignKey('Item', on_delete=models.CASCADE, related_name='exchange_requests_offered')
    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exchange_requests')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Обмен: {self.requester.username} предлагает {self.offered_item.title} за {self.requested_item.title}"

class Review(models.Model):
    item = models.ForeignKey('Item', on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField()  # например, от 1 до 5
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Отзыв {self.rating} для {self.item.title} от {self.reviewer.username}"


def item_image_path(instance, filename):
    # Генерируем путь для сохранения изображения вещи
    # Формат: uploads/items/item_id/filename
    base_filename, file_extension = os.path.splitext(filename)
    # Создаем безопасное имя файла на основе названия вещи
    slugified_title = slugify(instance.item.title)
    # Возвращаем путь для сохранения
    return f'uploads/items/{instance.item.id}/{slugified_title}_{base_filename}{file_extension}'

class ItemImage(models.Model):
    item = models.ForeignKey('Item', on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=item_image_path)
    is_primary = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Изображение для {self.item.title} ({self.id})"
    
    def save(self, *args, **kwargs):
        # Проверяем, является ли это новым изображением
        if self.pk is None and self.image:
            # Максимальные размеры для изображения
            max_width = 1200
            max_height = 900
            
            # Открываем изображение с помощью Pillow
            img = Image.open(self.image)
            
            # Получаем формат изображения
            img_format = img.format
            
            # Проверяем, нужно ли изменять размер
            if img.width > max_width or img.height > max_height:
                # Сохраняем пропорции
                img.thumbnail((max_width, max_height), Image.LANCZOS)
                
                # Сохраняем изображение в буфер
                buffer = BytesIO()
                # Сохраняем с оптимальным качеством
                img.save(buffer, format=img_format, quality=85, optimize=True)
                buffer.seek(0)
                
                # Заменяем оригинальное изображение
                self.image.save(
                    self.image.name,
                    ContentFile(buffer.read()),
                    save=False
                )
                
        super().save(*args, **kwargs)