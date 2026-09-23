from django.db import models
from django.contrib.auth.models import User

RECEPTION_CHOICES = (
    ('Легко', 'Легко'),
    ('Средне', 'Средне'),
    ('Сложно', 'Сложно'),
)


class Category(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(max_length=200)
    preparation_time = models.IntegerField()
    complexity = models.CharField(max_length=10, choices=RECEPTION_CHOICES)
    description = models.TextField()
    image = models.ImageField(upload_to='images/')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
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
