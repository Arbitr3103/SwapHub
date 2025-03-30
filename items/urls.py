from django.urls import path
from .views import (
    item_list, add_item, item_detail, edit_item, delete_item, rental_calendar,
    owner_requests, approve_request, reject_request, user_requests,
    create_exchange_request, owner_exchange_requests, approve_exchange_request, reject_exchange_request,
    add_review, rental_calendar_view, user_exchange_requests, add_item_images
)

urlpatterns = [
    path('', item_list, name='item_list'),
    path('add/', add_item, name='add_item'),
    path('<int:pk>/images/', add_item_images, name='add_item_images'),
    path('<int:pk>/', item_detail, name='item_detail'),
    path('<int:pk>/edit/', edit_item, name='edit_item'),
    path('<int:pk>/delete/', delete_item, name='delete_item'),
    path('<int:pk>/calendar/', rental_calendar, name='rental_calendar'),
    path('<int:pk>/review/', add_review, name='add_review'),
    # Пути для обмена
    path('<int:pk>/exchange/', create_exchange_request, name='create_exchange_request'),
    path('exchange/owner/', owner_exchange_requests, name='owner_exchange_requests'),
    path('exchange/<int:request_id>/approve/', approve_exchange_request, name='approve_exchange_request'),
    path('exchange/<int:request_id>/reject/', reject_exchange_request, name='reject_exchange_request'),
    # Пути для аренды
    path('requests/owner/', owner_requests, name='owner_requests'),
    path('requests/<int:request_id>/approve/', approve_request, name='approve_request'),
    path('requests/<int:request_id>/reject/', reject_request, name='reject_request'),
    path('calendar/', rental_calendar_view, name='rental_calendar'),
    path('requests/my/', user_requests, name='user_requests'),
    path('exchange/my/', user_exchange_requests, name='user_exchange_requests'),
]

