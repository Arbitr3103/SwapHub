from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import Profile, Friendship
from items.models import Item, ExchangeRequest, Review
from django.utils import timezone
import random

class Command(BaseCommand):
    help = 'Creates test data for SwapHub'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating test data...')

        # Create test users with profiles
        test_users = []
        usernames = ['alice', 'bob', 'charlie', 'diana', 'evan']
        
        for username in usernames:
            user, created = User.objects.get_or_create(
                username=username,
                email=f'{username}@example.com'
            )
            if created:
                user.set_password('testpass123')
                user.save()
                Profile.objects.get_or_create(
                    user=user,
                    defaults={
                        'bio': f'Тестовый профиль пользователя {username}',
                        'phone': f'+7900{random.randint(1000000, 9999999)}',
                        'location': 'Москва'
                    }
                )
            test_users.append(user)
            self.stdout.write(f'Created user: {username}')

        # Create some friendships
        for i in range(len(test_users)):
            for j in range(i + 1, len(test_users)):
                if random.choice([True, False]):
                    Friendship.objects.get_or_create(
                        from_user=test_users[i],
                        to_user=test_users[j],
                        defaults={'status': 'accepted'}
                    )
                    self.stdout.write(f'Created friendship: {test_users[i].username} - {test_users[j].username}')

        # Create test items
        categories = ['Книги', 'Электроника', 'Одежда', 'Спорт', 'Игры']
        items = []
        
        for user in test_users:
            for _ in range(3):  # 3 items per user
                item = Item.objects.create(
                    owner=user,
                    title=f'Предмет от {user.username} #{_+1}',
                    description=f'Описание предмета #{_+1} пользователя {user.username}',
                    category=random.choice(['electronics', 'clothing', 'sports', 'tools', 'home', 'books', 'toys', 'vehicles', 'other']),
                    rental_price=random.randint(100, 1000),
                    location='Москва',
                    is_available=True
                )
                items.append(item)
                self.stdout.write(f'Created item: {item.title}')

        # Create exchange requests
        for _ in range(10):  # Create 10 random exchange requests
            sender = random.choice(test_users)
            receiver = random.choice([u for u in test_users if u != sender])
            sender_item = random.choice([i for i in items if i.owner == sender])
            receiver_item = random.choice([i for i in items if i.owner == receiver])
            
            status = random.choice(['pending', 'accepted', 'rejected'])
            
            request = ExchangeRequest.objects.create(
                requester=sender,
                requested_item=receiver_item,
                offered_item=sender_item,
                status=status
            )
            self.stdout.write(f'Created exchange request: {sender.username} -> {receiver.username}')

            # If request was accepted, create reviews
            if status == 'accepted':
                # Создаем отзывы на предметы
                Review.objects.create(
                    item=sender_item,
                    reviewer=receiver,
                    rating=random.randint(3, 5),
                    comment=f'Отзыв о предмете {sender_item.title}'
                )
                self.stdout.write(f'Created review for item: {sender_item.title}')

                Review.objects.create(
                    item=receiver_item,
                    reviewer=sender,
                    rating=random.randint(3, 5),
                    comment=f'Отзыв о предмете {receiver_item.title}'
                )
                self.stdout.write(f'Created review for item: {receiver_item.title}')

        self.stdout.write(self.style.SUCCESS('Successfully created test data'))
