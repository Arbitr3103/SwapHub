# users/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.urls import reverse
from .forms import UserRegisterForm, UserUpdateForm, ProfileForm, ProfileUpdateForm
from .models import Profile, Notification, Friendship
from .services import get_unread_notifications_count, get_recent_notifications, mark_all_as_read, create_notification
from django.db.models import Q
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Аккаунт создан для {username}!')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})

@login_required
def profile(request):
    # Перенаправляем на profile_view для единообразия
    return redirect('profile_view', username=request.user.username)

@login_required
def edit_profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Профиль успешно обновлен')
            return redirect('profile')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    
    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'users/edit_profile.html', context)

def profile_view(request, username=None):
    # Проверка аутентификации, если username не указан
    if username is None and not request.user.is_authenticated:
        messages.warning(request, 'Пожалуйста, войдите в систему для просмотра профиля')
        return redirect('login')
    
    # Определяем пользователя профиля
    if username:
        profile_user = get_object_or_404(User, username=username)
    else:
        profile_user = request.user
    
    # Получаем данные о дружбе, если пользователь авторизован
    friendship_status = None
    if request.user.is_authenticated and request.user != profile_user:
        # Проверяем запросы в обоих направлениях
        outgoing_request = Friendship.objects.filter(from_user=request.user, to_user=profile_user).first()
        incoming_request = Friendship.objects.filter(from_user=profile_user, to_user=request.user).first()
        
        if outgoing_request:
            if outgoing_request.status == 'pending':
                friendship_status = 'pending_outgoing'
            elif outgoing_request.status == 'accepted':
                friendship_status = 'accepted'
        elif incoming_request:
            if incoming_request.status == 'pending':
                friendship_status = 'pending_incoming'
            elif incoming_request.status == 'accepted':
                friendship_status = 'accepted'
    
    context = {
        'profile_user': profile_user,
        'friendship_status': friendship_status,
    }
    
    
    return render(request, 'users/profile.html', context)

# Функционал друзей
@login_required
def send_friend_request(request, username):
    to_user = get_object_or_404(User, username=username)
    
    # Проверяем, не отправлен ли уже запрос
    if Friendship.objects.filter(from_user=request.user, to_user=to_user).exists():
        messages.warning(request, 'Вы уже отправили запрос дружбы этому пользователю')
        return redirect('user_profile', username=username)
    
    # Проверяем, не получен ли уже запрос от этого пользователя
    existing_request = Friendship.objects.filter(from_user=to_user, to_user=request.user).first()
    if existing_request:
        # Если получен, принимаем его автоматически
        existing_request.accept()
        create_notification(
            to_user, 
            'friend_accepted', 
            'Запрос дружбы принят', 
            f'Пользователь {request.user.username} принял ваш запрос дружбы',
            reverse('user_profile', args=[request.user.username])
        )
        messages.success(request, f'Вы и {to_user.username} теперь друзья!')
        return redirect('user_profile', username=username)
    
    # Создаем новый запрос
    friendship = Friendship.objects.create(from_user=request.user, to_user=to_user)
    
    # Создаем уведомление для получателя
    create_notification(
        to_user, 
        'friend_request',
        'Новый запрос дружбы',
        f'Пользователь {request.user.username} хочет добавить вас в друзья',
        reverse('user_profile', args=[request.user.username])
    )
    
    messages.success(request, f'Запрос дружбы отправлен пользователю {to_user.username}')
    return redirect('user_profile', username=username)

@login_required
def accept_friend_request(request, username):
    from_user = get_object_or_404(User, username=username)
    friendship_request = get_object_or_404(Friendship, from_user=from_user, to_user=request.user, status='pending')
    friendship_request.accept()
    
    # Создаем уведомление для отправителя запроса
    create_notification(
        from_user,
        'friend_accepted',
        'Запрос дружбы принят',
        f'Пользователь {request.user.username} принял ваш запрос дружбы',
        reverse('user_profile', args=[request.user.username])
    )
    
    messages.success(request, f'Вы приняли запрос дружбы от {from_user.username}')
    return redirect('user_profile', username=username)

@login_required
def reject_friend_request(request, username):
    from_user = get_object_or_404(User, username=username)
    friendship_request = get_object_or_404(Friendship, from_user=from_user, to_user=request.user, status='pending')
    friendship_request.reject()
    messages.info(request, f'Вы отклонили запрос дружбы от {from_user.username}')
    return redirect('user_profile', username=username)

@login_required
def friendship_requests(request):
    # Запросы, которые получил текущий пользователь
    received_requests = Friendship.objects.filter(
        to_user=request.user,
        status='pending'
    )
    
    # Запросы, которые отправил текущий пользователь
    sent_requests = Friendship.objects.filter(
        from_user=request.user,
        status='pending'
    )
    
    # Список друзей
    friends_list = Friendship.objects.filter(
        from_user=request.user,
        status='accepted'
    ) | Friendship.objects.filter(
        to_user=request.user,
        status='accepted'
    )
    
    context = {
        'received_requests': received_requests,
        'sent_requests': sent_requests,
        'friends_list': friends_list,
    }
    
    return render(request, 'users/friendship_requests.html', context)

# Список друзей пользователя
@login_required
@login_required
def remove_friend(request, username):
    friend = get_object_or_404(User, username=username)
    friendship = Friendship.objects.filter(
        (Q(from_user=request.user, to_user=friend) | Q(from_user=friend, to_user=request.user)),
        status='accepted'
    ).first()
    
    if friendship:
        friendship.remove()
        messages.success(request, f'Пользователь {username} удален из друзей')
    else:
        messages.error(request, f'Пользователь {username} не найден в списке друзей')
    
    return redirect('user_profile', username=username)

def friends_list(request, username=None):
    if username:
        user = get_object_or_404(User, username=username)
    else:
        user = request.user
    
    # Получаем список друзей пользователя
    friends = Friendship.objects.filter(
        (Q(from_user=user) | Q(to_user=user)),
        status='accepted'
    )
    
    # Преобразуем в список пользователей
    friends_users = []
    for friendship in friends:
        if friendship.from_user == user:
            friends_users.append(friendship.to_user)
        else:
            friends_users.append(friendship.from_user)
    
    # Пагинация списка друзей
    paginator = Paginator(friends_users, 9)  # По 9 друзей на странице
    page = request.GET.get('page', 1)
    
    try:
        friends_paginated = paginator.page(page)
    except PageNotAnInteger:
        # Если page не число, показываем первую страницу
        friends_paginated = paginator.page(1)
    except EmptyPage:
        # Если page больше максимального, показываем последнюю страницу
        friends_paginated = paginator.page(paginator.num_pages)
    
    context = {
        'profile_user': user,
        'friends': friends_paginated,
        'page_obj': friends_paginated,  # Для совместимости с шаблонами пагинации
    }
    
    return render(request, 'users/friends_list.html', context)

# Уведомления
@login_required
def notifications_list(request):
    notifications = request.user.notifications.all()
    return render(request, 'users/notifications_list.html', {'notifications': notifications})

@login_required
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notification.mark_as_read()
    return redirect(notification.url) if notification.url else redirect('notifications_list')

@login_required
def mark_all_notifications_read(request):
    mark_all_as_read(request.user)
    messages.success(request, 'Все уведомления отмечены как прочитанные')
    return redirect('notifications_list')

@login_required
def get_notifications_data(request):
    unread_count = get_unread_notifications_count(request.user)
    recent_notifications = get_recent_notifications(request.user)
    
    return JsonResponse({
        'unread_count': unread_count,
        'notifications': [
            {
                'id': n.id,
                'title': n.title,
                'message': n.short_message,
                'url': n.url,
                'is_read': n.is_read,
                'created_at': n.created_at.strftime('%d.%m.%Y %H:%M')
            } for n in recent_notifications
        ]
    })

@login_required
def search_users(request):
    """Поиск пользователей для добавления в друзья"""
    query = request.GET.get('q', '')
    users = []
    
    if query:
        # Поиск пользователей по имени пользователя и email, исключая текущего пользователя
        users = User.objects.filter(
            Q(username__icontains=query) | 
            Q(email__icontains=query) | 
            Q(first_name__icontains=query) | 
            Q(last_name__icontains=query)
        ).exclude(id=request.user.id).distinct()
        
        # Добавим информацию о статусе дружбы для каждого пользователя
        for user in users:
            # Проверяем запросы в обоих направлениях
            outgoing_request = Friendship.objects.filter(from_user=request.user, to_user=user).first()
            incoming_request = Friendship.objects.filter(from_user=user, to_user=request.user).first()
            
            if outgoing_request:
                if outgoing_request.status == 'pending':
                    user.friendship_status = 'pending_outgoing'
                elif outgoing_request.status == 'accepted':
                    user.friendship_status = 'accepted'
            elif incoming_request:
                if incoming_request.status == 'pending':
                    user.friendship_status = 'pending_incoming'
                elif incoming_request.status == 'accepted':
                    user.friendship_status = 'accepted'
            else:
                user.friendship_status = None
    
    # Пагинация результатов
    paginator = Paginator(users, 10)  # 10 пользователей на страницу
    page = request.GET.get('page')
    
    try:
        users_page = paginator.page(page)
    except PageNotAnInteger:
        users_page = paginator.page(1)
    except EmptyPage:
        users_page = paginator.page(paginator.num_pages)
    
    context = {
        'users': users_page,
        'query': query
    }
    
    return render(request, 'users/search_users.html', context)
