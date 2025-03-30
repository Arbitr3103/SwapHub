import datetime
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .forms import ItemForm, RentalRequestForm, ExchangeRequestForm, ReviewForm, ItemImageForm
from .models import Item, RentalRequest, ExchangeRequest, Review, ItemImage
from django.db.models import Q, Avg, Count
from .filters import ItemFilter


def item_list(request):
    # Получаем все вещи с рейтингом и количеством отзывов
    items = Item.objects.annotate(
        avg_rating=Avg('reviews__rating'),
        total_reviews=Count('reviews')
    ).order_by('-created_at')
    
    # Применяем фильтры из GET-параметров
    item_filter = ItemFilter(request.GET, queryset=items)
    filtered_items = item_filter.qs
    
    # Проверяем, есть ли параметр owner в URL
    owner_username = request.GET.get('owner')
    if owner_username and request.user.is_authenticated and request.user.username == owner_username:
        # Если это текущий пользователь смотрит свои вещи
        show_my_items = True
    else:
        show_my_items = False
    
    context = {
        'filter': item_filter,
        'items': filtered_items,
        'user': request.user,
        'show_my_items': show_my_items
    }
    return render(request, 'items/item_list.html', context)

@login_required
def add_item(request):
    if request.method == "POST":
        form = ItemForm(request.POST)
        if form.is_valid():
            # Сохраняем вещь
            item = form.save(commit=False)
            item.owner = request.user  # Привязываем вещь к текущему пользователю
            item.save()
            
            # Обрабатываем загруженные изображения
            files = request.FILES.getlist('images')
            
            if files:
                for i, image_file in enumerate(files):
                    # Первое изображение становится основным
                    is_primary = (i == 0)
                    ItemImage.objects.create(
                        item=item,
                        image=image_file,
                        is_primary=is_primary
                    )
                
                messages.success(request, 'Вещь и изображения успешно добавлены!')
                return redirect('item_detail', pk=item.pk)
            else:
                messages.success(request, 'Вещь успешно добавлена! Теперь вы можете добавить изображения.')
                # Перенаправляем на страницу добавления изображений
                return redirect('add_item_images', pk=item.pk)
    else:
        form = ItemForm()
    return render(request, 'items/add_item.html', {'form': form})

@login_required
def add_item_images(request, pk):
    item = get_object_or_404(Item, pk=pk, owner=request.user)
    
    if request.method == "POST":
        # Обрабатываем загруженные изображения
        files = request.FILES.getlist('images')
        
        if files:
            # Если это первые изображения для этой вещи, делаем первое основным
            is_first_image = not ItemImage.objects.filter(item=item).exists()
            
            for i, image_file in enumerate(files):
                is_primary = is_first_image and i == 0
                ItemImage.objects.create(
                    item=item,
                    image=image_file,
                    is_primary=is_primary
                )
            
            messages.success(request, 'Изображения успешно загружены!')
        
        # Если нажата кнопка завершения
        if 'finish' in request.POST:
            return redirect('item_detail', pk=item.pk)
    
    # Получаем существующие изображения для отображения
    images = ItemImage.objects.filter(item=item).order_by('-is_primary', 'uploaded_at')
    
    return render(request, 'items/add_item_images.html', {
        'item': item,
        'images': images
    })

def item_detail(request, pk):
    item = get_object_or_404(Item, pk=pk)
    user_request = None
    reviews = item.reviews.all().order_by('-created_at')
    
    # Получаем изображения вещи
    images = ItemImage.objects.filter(item=item).order_by('-is_primary', 'uploaded_at')
    primary_image = images.filter(is_primary=True).first()
    additional_images = images.filter(is_primary=False)
    
    if request.user.is_authenticated and request.user != item.owner:
        user_request = RentalRequest.objects.filter(item=item, renter=request.user).first()
    
    return render(request, 'items/item_detail.html', {
        'item': item,
        'user_request': user_request,
        'reviews': reviews,
        'primary_image': primary_image,
        'additional_images': additional_images,
        'images': images,
    })

@login_required
def edit_item(request, pk):
    item = get_object_or_404(Item, pk=pk, owner=request.user)
    
    # Получаем существующие изображения
    images = ItemImage.objects.filter(item=item).order_by('-is_primary', 'uploaded_at')
    
    if request.method == "POST":
        form = ItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            
            # Обрабатываем загруженные изображения
            files = request.FILES.getlist('images')
            
            if files:
                # Устанавливаем первое изображение как основное, если еще нет изображений
                is_first_image = not images.exists()
                
                for i, image_file in enumerate(files):
                    is_primary = is_first_image and i == 0
                    ItemImage.objects.create(
                        item=item,
                        image=image_file,
                        is_primary=is_primary
                    )
                
                messages.success(request, 'Изображения успешно добавлены!')
            
            # Обрабатываем удаление изображений
            if 'delete_images' in request.POST:
                image_ids = request.POST.getlist('delete_images')
                if image_ids:
                    # Удаляем выбранные изображения
                    ItemImage.objects.filter(id__in=image_ids, item=item).delete()
                    
                    # Если удалили основное изображение и есть другие изображения, устанавливаем новое основное
                    if not ItemImage.objects.filter(item=item, is_primary=True).exists():
                        first_image = ItemImage.objects.filter(item=item).first()
                        if first_image:
                            first_image.is_primary = True
                            first_image.save()
                    
                    messages.success(request, 'Выбранные изображения удалены!')
            
            # Устанавливаем новое основное изображение
            if 'set_primary' in request.POST:
                primary_id = request.POST.get('set_primary')
                if primary_id:
                    # Снимаем признак основного со всех изображений
                    ItemImage.objects.filter(item=item).update(is_primary=False)
                    # Устанавливаем новое основное
                    image = ItemImage.objects.get(id=primary_id, item=item)
                    image.is_primary = True
                    image.save()
                    messages.success(request, 'Основное изображение изменено!')
            
            return redirect('item_detail', pk=item.pk)
    else:
        form = ItemForm(instance=item)
    
    # Обновляем список изображений после возможных изменений
    images = ItemImage.objects.filter(item=item).order_by('-is_primary', 'uploaded_at')
    
    return render(request, 'items/edit_item.html', {
        'form': form, 
        'item': item,
        'images': images
    })

@login_required
def delete_item(request, pk):
    item = get_object_or_404(Item, pk=pk, owner=request.user)
    if request.method == "POST":
        item.delete()
        return redirect('item_list')
    return render(request, 'items/delete_item.html', {'item': item})

@login_required
def rental_calendar(request, pk):
    item = get_object_or_404(Item, pk=pk)

    # Проверка на существование уже активного запроса от текущего пользователя.
    existing_request = RentalRequest.objects.filter(
        item=item,
        renter=request.user,
        status__in=['pending', 'approved']
    ).first()
    if existing_request:
        messages.info(request, "Вы уже отправили запрос аренды для этой вещи.")
        return redirect('item_detail', pk=pk)

    # Получаем все одобренные периоды для этой вещи
    approved_requests = item.approved_rental_requests

    # Формируем список занятых дат в формате YYYY-MM-DD
    busy_dates = []
    for req in approved_requests:
        current_date = req.start_date
        while current_date <= req.end_date:
            busy_dates.append(current_date.strftime('%Y-%m-%d'))
            current_date += datetime.timedelta(days=1)

    if request.method == 'POST':
        form = RentalRequestForm(request.POST, item=item)
        if form.is_valid():
            rental_request = form.save(commit=False)
            rental_request.item = item
            rental_request.renter = request.user
            rental_request.save()
            messages.success(request, "Ваш запрос аренды отправлен!")
            return redirect('item_detail', pk=pk)
    else:
        form = RentalRequestForm(item=item)

    return render(request, 'items/rental_calendar.html', {
        'item': item,
        'busy_dates': busy_dates,
        'form': form
    })

@login_required
def owner_requests(request):
    requests = RentalRequest.objects.filter(item__owner=request.user).order_by('-created_at')
    return render(request, 'items/owner_requests.html', {'requests': requests})

@login_required
def approve_request(request, request_id):
    rental_request = get_object_or_404(RentalRequest, id=request_id, item__owner=request.user)
    rental_request.status = 'approved'
    rental_request.save()
    
    # Отправляем уведомление арендатору
    send_mail(
        'Ваш запрос аренды одобрен',
        f'Ваш запрос на аренду {rental_request.item.title} был одобрен. '
        f'Период аренды: с {rental_request.start_date} по {rental_request.end_date}.',
        settings.DEFAULT_FROM_EMAIL,
        [rental_request.renter.email],
        fail_silently=True,
    )
    
    messages.success(request, "Запрос аренды одобрен.")
    return redirect('owner_requests')

@login_required
def reject_request(request, request_id):
    rental_request = get_object_or_404(RentalRequest, id=request_id, item__owner=request.user)
    rental_request.status = 'rejected'
    rental_request.save()
    
    # Отправляем уведомление арендатору
    send_mail(
        'Ваш запрос аренды отклонен',
        f'К сожалению, ваш запрос на аренду {rental_request.item.title} был отклонен.',
        settings.DEFAULT_FROM_EMAIL,
        [rental_request.renter.email],
        fail_silently=True,
    )
    
    messages.info(request, "Запрос аренды отклонен.")
    return redirect('owner_requests')

@login_required
def create_exchange_request(request, pk):
    """
    Представление для создания запроса обмена для вещи с id=pk.
    Запрашиваемая вещь – это item с pk, а предлагаемая выбирается из списка вещей текущего пользователя.
    """
    requested_item = get_object_or_404(Item, pk=pk)
    if request.method == 'POST':
        form = ExchangeRequestForm(request.POST, requested_item=requested_item, requester=request.user)
        if form.is_valid():
            exchange_request = form.save(commit=False)
            exchange_request.requested_item = requested_item
            exchange_request.requester = request.user
            exchange_request.save()
            messages.success(request, "Ваш запрос обмена отправлен!")
            return redirect('item_detail', pk=pk)
    else:
        form = ExchangeRequestForm(requested_item=requested_item, requester=request.user)

    context = {
        'form': form,
        'requested_item': requested_item,
    }
    print("Контекст шаблона:", context)  # Вывод в консоль
    return render(request, 'items/create_exchange_request.html', context)

    # Проверим, не был ли уже отправлен обменный запрос для этой вещи от этого пользователя
    existing_request = ExchangeRequest.objects.filter(requested_item=requested_item, requester=request.user).first()
    if existing_request:
        messages.info(request, "Вы уже отправили запрос обмена для этой вещи.")
        return redirect('item_detail', pk=pk)

    if request.method == 'POST':
        form = ExchangeRequestForm(request.POST, requested_item=requested_item, requester=request.user)
        if form.is_valid():
            exchange_request = form.save(commit=False)
            exchange_request.requested_item = requested_item
            exchange_request.requester = request.user
            exchange_request.save()
            messages.success(request, "Ваш запрос обмена отправлен!")
            return redirect('item_detail', pk=pk)
    else:
        form = ExchangeRequestForm(requested_item=requested_item, requester=request.user)

    return render(request, 'items/create_exchange_request.html', {
        'form': form,
        'requested_item': requested_item,
    })

@login_required
def owner_exchange_requests(request):
    # Получаем все обменные запросы для вещей, которыми владеет текущий пользователь
    exchange_requests = ExchangeRequest.objects.filter(requested_item__owner=request.user).order_by('-created_at')
    return render(request, 'items/owner_exchange_requests.html', {'exchange_requests': exchange_requests})

@login_required
def approve_exchange_request(request, request_id):
    exchange_request = get_object_or_404(ExchangeRequest, id=request_id, requested_item__owner=request.user)
    exchange_request.status = 'approved'
    exchange_request.save()
    
    # Отправляем уведомление пользователю, предложившему обмен
    send_mail(
        'Ваш запрос на обмен одобрен',
        f'Ваш запрос на обмен {exchange_request.offered_item.title} '
        f'на {exchange_request.requested_item.title} был одобрен.',
        settings.DEFAULT_FROM_EMAIL,
        [exchange_request.requester.email],
        fail_silently=True,
    )
    
    messages.success(request, "Запрос обмена одобрен.")
    return redirect('owner_exchange_requests')

@login_required
def reject_exchange_request(request, request_id):
    exchange_request = get_object_or_404(ExchangeRequest, id=request_id, requested_item__owner=request.user)
    exchange_request.status = 'rejected'
    exchange_request.save()
    
    # Отправляем уведомление пользователю, предложившему обмен
    send_mail(
        'Ваш запрос на обмен отклонен',
        f'К сожалению, ваш запрос на обмен {exchange_request.offered_item.title} '
        f'на {exchange_request.requested_item.title} был отклонен.',
        settings.DEFAULT_FROM_EMAIL,
        [exchange_request.requester.email],
        fail_silently=True,
    )
    
    messages.info(request, "Запрос обмена отклонён.")
    return redirect('owner_exchange_requests')

@login_required
def add_review(request, pk):
    item = get_object_or_404(Item, pk=pk)
    
    # Проверяем, может ли пользователь оставить отзыв (например, если он арендовал вещь)
    # Здесь можно добавить дополнительную логику проверки

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.item = item
            review.reviewer = request.user
            review.save()
            messages.success(request, "Ваш отзыв успешно сохранён!")
            return redirect('item_detail', pk=pk)
    else:
        form = ReviewForm()
    
    return render(request, 'items/add_review.html', {'form': form, 'item': item})

@login_required
def rental_calendar_view(request):
    # Простой рендеринг шаблона без дополнительных данных
    return render(request, 'items/rental_calendar.html')

@login_required
def user_requests(request):
    """Представление для просмотра запросов на аренду, отправленных текущим пользователем"""
    requests = RentalRequest.objects.filter(renter=request.user).order_by('-created_at')
    return render(request, 'items/user_requests.html', {'requests': requests})

@login_required
def user_exchange_requests(request):
    """Представление для просмотра запросов на обмен, отправленных текущим пользователем"""
    requests = ExchangeRequest.objects.filter(requester=request.user).order_by('-created_at')
    return render(request, 'items/user_exchange_requests.html', {'requests': requests})
