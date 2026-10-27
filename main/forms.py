from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Recipe, RecipeStep, RECEPTION_CHOICES, Review
from django.forms import inlineformset_factory


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(label="Ім'я", max_length=150)
    last_name = forms.CharField(label="Прізвище", max_length=150)
    email = forms.EmailField(label="Електронна пошта")

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email")
        labels = {
            "username": "Ім'я користувача",
            "first_name": "Ім'я",
            "last_name": "Прізвище",
            "email": "Електронна пошта",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].label = "Пароль"
        self.fields["password2"].label = "Підтвердження пароля"
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"
            self.fields["password1"].help_text = ""


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ['name', 'preparation_time', 'complexity', 'description', 'image', 'category']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].empty_label = 'Выберите категорию'
        self.fields['complexity'].choices = [('', 'Выберите сложность')] + list(RECEPTION_CHOICES)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


RecipeStepFormSet = inlineformset_factory(
    Recipe,
    RecipeStep,
    fields=('number', 'text'),
    extra=5,
    can_delete=False,

    widgets={
        'number': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '1'}),
        'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 2,
                                      'placeholder': 'Опишіть цей крок'}),
    },
    labels={
        'number': 'Номер кроку',
        'text': 'Опис кроку',
    },
)


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ('rating', 'text')
        widgets = {
            'rating': forms.Select(
                choices=[(i, i) for i in range(1, 6)],
                attrs={'class': 'form-select'},
            ),
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'rating': 'Оцінка (1–5)',
            'text': 'Текст відгуку',
        }
