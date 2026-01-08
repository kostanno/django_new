from django import forms
from .models import BlogPost


class BlogPostForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = ['title', 'content', 'preview', 'is_published']

        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите заголовок статьи'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 10,
                'placeholder': 'Введите содержимое статьи'
            }),
        }

        labels = {
            'title': 'Заголовок',
            'content': 'Содержимое',
            'preview': 'Превью-изображение',
            'is_published': 'Опубликовать'
        }