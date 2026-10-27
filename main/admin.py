from django.contrib import admin
from .models import Category, Ingredient, Recipe, RecipeIngredient, RecipeStep, Review


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1

class RecipeAdmin(admin.ModelAdmin):
    inlines = [RecipeIngredientInline]

class RecipeStepInline(admin.StackedInline):
    model = RecipeStep
    extra = 1

class RecipeAdmin(admin.ModelAdmin):
    inlines = [RecipeIngredientInline, RecipeStepInline]

admin.site.register(Category)
admin.site.register(Ingredient)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Review)
