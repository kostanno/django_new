from django import forms
from django.core.exceptions import ValidationError

from homework.models import Product

FORBIDDEN_WORDS = [
    'казино',
    'криптовалюта',
    'крипта',
    'биржа',
    'дешево',
    'бесплатно',
    'обман',
    'полиция',
    'радар',
]


class ProductForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = ['name', 'description', 'image', 'category', 'price']
        widgets = {
            'description': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Опишите ваш товар'
            }),
        }
        labels = {
            'name': 'Название товара',
            'description': 'Описание',
            'image': 'Изображение',
            'category': 'Категория',
            'price': 'Цена (руб.)'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name == 'image':
                field.widget.attrs['class'] = 'form-control-file'
            else:
                field.widget.attrs['class'] = 'form-control'
            if field_name == 'name':
                field.widget.attrs['placeholder'] = 'Введите название товара'
            elif field_name == 'price':
                field.widget.attrs['placeholder'] = '0.00'

    def clean_name(self):
        name = self.cleaned_data.get('name', '')
        name_lower = name.lower()
        for word in FORBIDDEN_WORDS:
            if word in name_lower:
                return "содержит запрещенное слово"
        return name

    def clean_description(self):
        description = self.cleaned_data.get('description', '')
        if not description:
            return description
        description_lower = description.lower()
        for word in FORBIDDEN_WORDS:
            if word in description_lower:
                return "содержит запрещенное слово"
        return description

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price < 0:
            raise ValidationError('Цена не может быть отрицательной! ')
        return price