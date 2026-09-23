
from django.shortcuts import render, get_object_or_404

from main.models import Recipe, Category, RECEPTION_CHOICES


def recipe_list(request):
    recipes = Recipe.objects.all()
    categories = Category.objects.all()

    selected_category = request.GET.get('category')
    selected_complexity = request.GET.get('complexity')

    if selected_category:
        recipes = recipes.filter(category__name=selected_category)

    if selected_complexity:
        recipes = recipes.filter(complexity=selected_complexity)

    context = {
        'title': 'Все рецепты',
        'recipes': recipes,
        'categories': categories,
        'complexities': RECEPTION_CHOICES,
    }

    return render(request, 'main/recipe_list.html', context)


def recipe_detail(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)

    return render(request, 'main/recipe_detail.html', {'recipe': recipe})

