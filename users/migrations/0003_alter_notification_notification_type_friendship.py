# Generated by Django 5.0.2 on 2025-03-18 18:03

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_notification'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='notification_type',
            field=models.CharField(choices=[('rental_request', 'Запрос аренды'), ('rental_approved', 'Аренда одобрена'), ('rental_rejected', 'Аренда отклонена'), ('exchange_request', 'Запрос обмена'), ('exchange_approved', 'Обмен одобрен'), ('exchange_rejected', 'Обмен отклонен'), ('friend_request', 'Запрос дружбы'), ('friend_accepted', 'Запрос дружбы принят'), ('message', 'Сообщение')], max_length=20),
        ),
        migrations.CreateModel(
            name='Friendship',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('pending', 'В ожидании'), ('accepted', 'Принято'), ('rejected', 'Отклонено')], default='pending', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('from_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='friendship_requests_sent', to=settings.AUTH_USER_MODEL)),
                ('to_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='friendship_requests_received', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
                'unique_together': {('from_user', 'to_user')},
            },
        ),
    ]
