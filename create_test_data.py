import os
import django
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
import requests

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SwapHub.settings')
django.setup()

from django.contrib.auth.models import User
from items.models import Item, ItemImage

# Список тестовых данных
test_items = [
    {
        'title': 'Горный велосипед Trek',
        'description': 'Отличный горный велосипед для активного отдыха. В хорошем состоянии.',
        'category': 'sports',
        'location': 'Москва',
        'rental_price': 1500,
        'image_url': 'https://images.unsplash.com/photo-1576435728678-68d0fbf94e91?w=800',
    },
    {
        'title': 'Электросамокат Xiaomi Pro 2',
        'description': 'Мощный электросамокат с большим запасом хода. Идеален для городской среды.',
        'category': 'electronics',
        'location': 'Санкт-Петербург',
        'rental_price': 2000,
        'image_url': 'https://images.unsplash.com/photo-1605557626697-2e29953cec5c?w=800',
    },
    {
        'title': 'Велосипед BMX',
        'description': 'Трюковой велосипед для экстремального катания. Усиленная рама.',
        'category': 'sports',
        'location': 'Новосибирск',
        'rental_price': 1200,
        'image_url': 'https://images.unsplash.com/photo-1583118443607-33f6a50cafdd?w=800',
    },
    {
        'title': 'Электросамокат Ninebot Max',
        'description': 'Надежный электросамокат с большими колесами. Подходит для дальних поездок.',
        'category': 'electronics',
        'location': 'Москва',
        'rental_price': 2500,
        'image_url': 'https://images.unsplash.com/photo-1628898576802-af4d9174ae67?w=800',
    },
    {
        'title': 'Складной велосипед Brompton',
        'description': 'Компактный городской велосипед. Легко складывается и удобен для хранения.',
        'category': 'sports',
        'location': 'Санкт-Петербург',
        'rental_price': 1800,
        'image_url': 'https://images.unsplash.com/photo-1593764592116-bfb2a97c642a?w=800',
    },
    {
        'title': 'Гироскутер Segway',
        'description': 'Современный гироскутер с подсветкой. Отлично подходит для развлечений.',
        'category': 'electronics',
        'location': 'Новосибирск',
        'rental_price': 1000,
        'image_url': 'https://images.unsplash.com/photo-1527674905530-6b94d31e7897?w=800',
    },
    {
        'title': 'Городской велосипед Schwinn',
        'description': 'Классический городской велосипед с корзиной. Идеален для поездок по городу.',
        'category': 'sports',
        'location': 'Москва',
        'rental_price': 1300,
        'image_url': 'https://images.unsplash.com/photo-1485965120184-e220f721d03e?w=800',
    },
    {
        'title': 'Электровелосипед Bosch',
        'description': 'Мощный электровелосипед с длительным временем работы от батареи.',
        'category': 'electronics',
        'location': 'Санкт-Петербург',
        'rental_price': 3000,
        'image_url': 'https://images.unsplash.com/photo-1571068316344-75bc76f77890?w=800',
    },
    {
        'title': 'Детский велосипед Giant',
        'description': 'Надежный детский велосипед с дополнительными колесами.',
        'category': 'sports',
        'location': 'Новосибирск',
        'rental_price': 800,
        'image_url': 'https://images.unsplash.com/photo-1507035895480-2b3156c31fc8?w=800',
    },
    {
        'title': 'Электроскейт Boosted',
        'description': 'Мощный электрический скейтборд. Развивает скорость до 40 км/ч.',
        'category': 'electronics',
        'location': 'Москва',
        'rental_price': 2200,
        'image_url': 'https://images.unsplash.com/photo-1547447134-cd3f5c716030?w=800',
    },
]

def create_test_items():
    # Получаем пользователя
    user = User.objects.get(username='Arbitr')
    
    # Создаем вещи
    for item_data in test_items:
        # Создаем объект вещи
        item = Item.objects.create(
            owner=user,
            title=item_data['title'],
            description=item_data['description'],
            category=item_data['category'],
            location=item_data['location'],
            rental_price=item_data['rental_price']
        )
        
        # Загружаем изображение
        try:
            response = requests.get(item_data['image_url'])
            if response.status_code == 200:
                img_temp = NamedTemporaryFile(delete=True)
                img_temp.write(response.content)
                img_temp.flush()
                
                # Создаем изображение для вещи
                image = ItemImage.objects.create(item=item)
                image.image.save(f"item_{item.id}.jpg", File(img_temp))
                print(f"Created item: {item.title} with image")
            else:
                print(f"Failed to download image for {item.title}")
        except Exception as e:
            print(f"Error creating image for {item.title}: {str(e)}")

if __name__ == '__main__':
    create_test_items()
