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
        'image_url': 'https://cdn.pixabay.com/photo/2015/05/29/19/18/bicycle-789648_1280.jpg',
    },
    {
        'title': 'Электросамокат Xiaomi Pro 2',
        'description': 'Мощный электросамокат с большим запасом хода. Идеален для городской среды.',
        'category': 'electronics',
        'location': 'Санкт-Петербург',
        'rental_price': 2000,
        'image_url': 'https://cdn.pixabay.com/photo/2019/10/26/13/36/electric-scooter-4579992_1280.jpg',
    },
    {
        'title': 'Велосипед BMX',
        'description': 'Трюковой велосипед для экстремального катания. Усиленная рама.',
        'category': 'sports',
        'location': 'Новосибирск',
        'rental_price': 1200,
        'image_url': 'https://cdn.pixabay.com/photo/2020/01/21/16/26/bike-4783374_1280.jpg',
    },
    {
        'title': 'Электросамокат Ninebot Max',
        'description': 'Надежный электросамокат с большими колесами. Подходит для дальних поездок.',
        'category': 'electronics',
        'location': 'Москва',
        'rental_price': 2500,
        'image_url': 'https://cdn.pixabay.com/photo/2022/08/09/14/30/e-scooter-7375375_1280.jpg',
    },
    {
        'title': 'Складной велосипед Brompton',
        'description': 'Компактный городской велосипед. Легко складывается и удобен для хранения.',
        'category': 'sports',
        'location': 'Санкт-Петербург',
        'rental_price': 1800,
        'image_url': 'https://cdn.pixabay.com/photo/2016/11/18/12/49/bicycle-1834265_1280.jpg',
    },
    {
        'title': 'Гироскутер Segway',
        'description': 'Современный гироскутер с подсветкой. Отлично подходит для развлечений.',
        'category': 'electronics',
        'location': 'Новосибирск',
        'rental_price': 1000,
        'image_url': 'https://cdn.pixabay.com/photo/2019/05/26/08/06/hoverboard-4229893_1280.jpg',
    },
    {
        'title': 'Городской велосипед Schwinn',
        'description': 'Классический городской велосипед с корзиной. Идеален для поездок по городу.',
        'category': 'sports',
        'location': 'Москва',
        'rental_price': 1300,
        'image_url': 'https://cdn.pixabay.com/photo/2014/07/05/08/20/bike-384566_1280.jpg',
    },
    {
        'title': 'Электровелосипед Bosch',
        'description': 'Мощный электровелосипед с длительным временем работы от батареи.',
        'category': 'electronics',
        'location': 'Санкт-Петербург',
        'rental_price': 3000,
        'image_url': 'https://cdn.pixabay.com/photo/2016/02/22/20/22/mountain-bike-1216431_1280.jpg',
    },
    {
        'title': 'Детский велосипед Giant',
        'description': 'Надежный детский велосипед с дополнительными колесами.',
        'category': 'sports',
        'location': 'Новосибирск',
        'rental_price': 800,
        'image_url': 'https://cdn.pixabay.com/photo/2014/06/22/05/49/childrens-bicycle-374310_1280.jpg',
    },
    {
        'title': 'Электроскейт Boosted',
        'description': 'Мощный электрический скейтборд. Развивает скорость до 40 км/ч.',
        'category': 'electronics',
        'location': 'Москва',
        'rental_price': 2200,
        'image_url': 'https://cdn.pixabay.com/photo/2017/08/01/08/29/people-2563491_1280.jpg',
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
            # Добавляем заголовки, чтобы обойти ограничения
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
            }
            response = requests.get(item_data['image_url'], headers=headers, stream=True)
            print(f"Image download status for {item.title}: {response.status_code}")
            
            if response.status_code == 200:
                img_temp = NamedTemporaryFile(delete=True)
                img_temp.write(response.content)
                img_temp.flush()
                
                # Создаем изображение для вещи и устанавливаем его как основное
                image = ItemImage(item=item, is_primary=True)
                image.image.save(f"item_{item.id}.jpg", File(img_temp), save=True)
                print(f"Created item: {item.title} with image at {image.image.url}")
            else:
                print(f"Failed to download image for {item.title} - status code: {response.status_code}")
        except Exception as e:
            print(f"Error creating image for {item.title}: {str(e)}")

if __name__ == '__main__':
    create_test_items()
