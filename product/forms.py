from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from product.models import Product, Category
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
        fields_1 = [
            'name', 'description', 'image', 'category',
            'price', 'publication_status', 'owner'
        ]

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


    class Meta:
        model = Product
        fields = [
            'name', 'description', 'image', 'category',
            'price', 'publication_status', 'owner'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'publication_status': forms.Select(attrs={'class': 'form-control'}),
            'owner': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'name':_('Название'),
            'description': _('Описание'),
            'image': _('Изображение'),
            'category': _('Категория'),
            'price': _('Цена'),
            'publication_status': _('Статус публикации'),
            'owner': _('Владелец'),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        if self.request and not (
                self.request.user.is_superuser or
                self.request.user.has_perm('products.can_edit_any_product')
        ):
            self.fields['owner'].widget = forms.HiddenInput()
            if self.instance and self.instance.pk:
                self.fields['owner'].disabled = True
            self.fields['publication_status'].disabled = True
            self.fields['publication_status'].widget = forms.HiddenInput()


class ProductFilterForm(forms.Form):

    STATUS_CHOICES = [('', 'Все статусы')] + list(Product.PublicationStatus.choices)
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        label=_('Статус публикации')
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        label=_('Категория'),
        empty_label=_('Все категории')
    )
    search = forms.CharField(
        required=False,
        label=_('Поиск'),
        widget=forms.TextInput(attrs={'placeholder': _('Поиск по названию')})
    )