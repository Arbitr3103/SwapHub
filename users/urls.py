# users/urls.py

from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/<str:username>/', views.profile_view, name='user_profile'),
    
    # Друзья
    path('friends/', views.friends_list, name='friends_list'),
    path('friends/<str:username>/', views.friends_list, name='user_friends_list'),
    path('friend-requests/', views.friendship_requests, name='friendship_requests'),
    path('send-friend-request/<str:username>/', views.send_friend_request, name='send_friend_request'),
    path('accept-friend-request/<str:username>/', views.accept_friend_request, name='accept_friend_request'),
    path('reject-friend-request/<str:username>/', views.reject_friend_request, name='reject_friend_request'),
    path('remove-friend/<str:username>/', views.remove_friend, name='remove_friend'),
    
    # Поиск пользователей
    path('search/', views.search_users, name='search_users'),
    
    # Уведомления
    path('notifications/', views.notifications_list, name='notifications_list'),
    path('notifications/mark-read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('notifications/data/', views.get_notifications_data, name='get_notifications_data'),
]
