from django import forms
from django.core.exceptions import ValidationError
from .models import ExchangeRequest, Item, RentalRequest, Review, ItemImage

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['title', 'description', 'category', 'rental_price', 'location', 'is_available']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Опишите вашу вещь подробнее: состояние, особенности, комплектация и т.д.'}),
            'title': forms.TextInput(attrs={'placeholder': 'Например: Велосипед горный'}),
            'rental_price': forms.NumberInput(attrs={'placeholder': 'Например: 500', 'min': '0', 'step': '10'}),
            'location': forms.TextInput(attrs={'placeholder': 'Например: Москва, ул. Ленина, 10'}),
        }
        labels = {
            'title': 'Название вещи',
            'description': 'Описание',
            'category': 'Категория',
            'rental_price': 'Стоимость аренды (₽/день)',
            'location': 'Местоположение',
            'is_available': 'Доступна для аренды',
        }
        help_texts = {
            'title': 'Укажите краткое и понятное название вещи',
            'description': 'Чем подробнее описание, тем больше шансов найти арендатора',
            'rental_price': 'Укажите стоимость аренды за один день',
            'location': 'Укажите, где находится вещь и где её можно забрать',
            'is_available': 'Снимите галочку, если вещь временно недоступна',
        }

class ItemImageForm(forms.ModelForm):
    class Meta:
        model = ItemImage
        fields = ['image', 'is_primary']
        widgets = {
            'is_primary': forms.HiddenInput(),
        }
        labels = {
            'image': 'Фотография',
            'is_primary': 'Основное фото',
        }
        help_texts = {
            'image': 'Загрузите фотографию вашей вещи',
        }

class RentalRequestForm(forms.ModelForm):
    """
    Форма для создания запроса аренды.
    При инициализации ожидается параметр `item` – объект вещи,
    для проверки занятых дат и предотвращения пересечения.
    """
    def __init__(self, *args, **kwargs):
        # Извлекаем объект item из аргументов, если он передан
        self.item = kwargs.pop('item', None)
        super().__init__(*args, **kwargs)

    class Meta:
        model = RentalRequest
        fields = ['start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        # Проверяем, что обе даты указаны
        if start_date and end_date:
            if start_date > end_date:
                raise ValidationError("Дата начала не может быть позже даты окончания.")

            # Если объект вещи передан, проверяем пересечение с уже одобренными запросами
            if self.item:
                overlapping_requests = RentalRequest.objects.filter(
                    item=self.item,
                    status='approved',
                    start_date__lte=end_date,
                    end_date__gte=start_date
                )
                if overlapping_requests.exists():
                    raise ValidationError("Выбранный период пересекается с уже забронированными датами.")
        return cleaned_data

class ExchangeRequestForm(forms.ModelForm):
    # Будем предоставлять выбор из списка вещей пользователя для offered_item
    offered_item = forms.ModelChoiceField(
        queryset=Item.objects.none(),
        label="Ваша вещь для обмена"
    )

    class Meta:
        model = ExchangeRequest
        # Пользователь выбирает только предлагаемый товар и указывает период обмена, если требуется (здесь просто два поля)
        fields = ['offered_item']

    def __init__(self, *args, **kwargs):
        # Передаём в форму объект requested_item и текущего пользователя, чтобы ограничить выбор offered_item
        self.requested_item = kwargs.pop('requested_item', None)
        self.requester = kwargs.pop('requester', None)
        super().__init__(*args, **kwargs)
        if self.requester:
            # Ограничиваем выбор до вещей, которыми владеет текущий пользователь
            self.fields['offered_item'].queryset = Item.objects.filter(owner=self.requester)

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
            'comment': forms.Textarea(attrs={'rows': 4}),
        }