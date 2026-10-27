from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth.models import User

RECEPTION_CHOICES = (
    ('Легко', 'Легко'),
    ('Середньо', 'Середньо'),
    ('Важко', 'Важко'),
)


class Category(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название')
    image = models.ImageField(upload_to='categories/', blank=True)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название')

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название')
    preparation_time = models.IntegerField(verbose_name='Время приготовления (мин)')
    complexity = models.CharField(max_length=10, choices=RECEPTION_CHOICES, verbose_name='Сложность')
    description = models.TextField(verbose_name='Описание')
    image = models.ImageField(upload_to='images/', verbose_name='Изображение')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Категория')
    ingredients = models.ManyToManyField(Ingredient, through='RecipeIngredient')

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="recipe_choice"
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, related_name="ingredient_choice"
    )
    amount = models.CharField(max_length=200)
    unit = models.CharField(max_length=200)


    def __str__(self):
        return self.ingredient.name


class RecipeStep(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='steps')
    number = models.IntegerField()
    text = models.TextField()

    class Meta:
        ordering = ['number']

    def __str__(self):
        return f"{self.number}"

class Review(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='reviews')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ]
    )
    text = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Відгук',
        verbose_name_plural = 'Відгуки',

        ordering = ['-date_created']
        constraints = [
            models.UniqueConstraint(fields=['recipe', 'author'], name='unique_review_per_user')
        ]

    def __str__(self):
        return f'{self.author} → {self.recipe} ({self.rating})'
