import django_filters
from django.db.models import Q
from .models import Item

class ItemFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name='rental_price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='rental_price', lookup_expr='lte')
    location = django_filters.CharFilter(field_name='location', lookup_expr='icontains')
    category = django_filters.CharFilter(field_name='category', lookup_expr='iexact')
    owner = django_filters.CharFilter(field_name='owner__username', lookup_expr='exact')
    
    # Поиск по названию и описанию
    search = django_filters.CharFilter(method='search_filter')
    
    # Сортировка
    ordering = django_filters.OrderingFilter(
        choices=(
            ('created_at', 'Дата добавления (по возрастанию)'),
            ('-created_at', 'Дата добавления (по убыванию)'),
            ('rental_price', 'Цена (по возрастанию)'),
            ('-rental_price', 'Цена (по убыванию)'),
            ('avg_rating', 'Рейтинг (по возрастанию)'),
            ('-avg_rating', 'Рейтинг (по убыванию)'),
            ('total_reviews', 'Количество отзывов (по возрастанию)'),
            ('-total_reviews', 'Количество отзывов (по убыванию)'),
        ),
        fields={
            'created_at': 'created_at',
            'rental_price': 'rental_price',
            'avg_rating': 'avg_rating',
            'total_reviews': 'total_reviews',
        }
    )

    def search_filter(self, queryset, name, value):
        return queryset.filter(
            Q(title__icontains=value) |
            Q(description__icontains=value)
        )

    class Meta:
        model = Item
        fields = ['min_price', 'max_price', 'location', 'category', 'is_available', 'owner'] 