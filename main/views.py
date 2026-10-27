from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from pyexpat.errors import messages
from django.contrib import messages

from main.forms import RegisterForm, RecipeForm, RecipeStepFormSet, ReviewForm
from main.models import Recipe, Category, RECEPTION_CHOICES, Review


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
        'title': 'Усі рецепти',
        'recipes': recipes,
        'categories': categories,
        'complexities': RECEPTION_CHOICES,
    }

    return render(request, 'main/recipe_list.html', context)


def recipe_detail(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    reviews = recipe.reviews.select_related('author')
    form = ReviewForm()

    return render(request, 'main/recipe_detail.html',
                  {'recipe': recipe, 'reviews': reviews, 'form': form})


@login_required
def my_recipes(request):
    recipes = Recipe.objects.filter(author=request.user)

    return render(request, 'main/my_recipes.html',
                  {'recipes': recipes, 'title': 'Мои рецепты'})


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('recipe_list')
    else:
        form = RegisterForm()

    return render(request, 'registration/register.html', {'form': form})


@login_required
def recipe_create(request):
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES)
        formset = RecipeStepFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            recipe = form.save(commit=False)
            recipe.author = request.user
            recipe.save()
            formset.instance = recipe
            formset.save()
            messages.success(request, f'Рецепт "{recipe.name}" додано')
            return redirect('recipe_detail', pk=recipe.pk)
    else:
        form = RecipeForm()
        formset = RecipeStepFormSet()
    return render(request, 'main/recipe_form.html', {'form': form, 'formset': formset})


def home(request):
    categories = Category.objects.all()
    context = {
        'title': 'Головна сторінка',
        'categories': categories,
    }
    return render(request, 'main/home.html', context)


@login_required
def recipe_delete(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk, author=request.user)

    if request.method == 'POST':
        recipe.delete()
        messages.success(request, f'Рецепт "{recipe.name}" видалено')
        return redirect(
            'my_recipes'
        )
    return render(request, 'main/recipe_confirm_delete.html', {'recipe': recipe})


@login_required
def add_review(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)

    if Review.objects.filter(recipe=recipe, author=request.user).exists():
        messages.warning(request, 'Ви не можете повторно залишати відгук')
        return redirect('recipe_detail', pk=recipe.pk)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.recipe = recipe
            review.author = request.user
            review.save()
            messages.success(request, f'Відгук доданий для: {recipe.name}')
        else:
            messages.error(request, 'Перевірте форму')
    return redirect('recipe_detail', pk=recipe.pk)
