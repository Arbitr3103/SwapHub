from django.shortcuts import render
from items.models import Item

def home(request):
    """
    Представление для главной страницы
    """
    # Получаем последние 6 добавленных вещей
    latest_items = Item.objects.all().order_by('-created_at')[:6]
    
    context = {
        'latest_items': latest_items,
    }
    
    return render(request, 'home.html', context)
