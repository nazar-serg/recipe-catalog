import io
import shutil
import tempfile

from PIL import Image
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from main.forms import ReviewForm
from main.models import Category, Ingredient, Recipe, RecipeIngredient, RecipeStep, Review

MEDIA_ROOT = tempfile.mkdtemp()


def make_test_image():
    buffer = io.BytesIO()
    Image.new('RGB', (10, 10), color='red').save(buffer, format='PNG')
    buffer.seek(0)
    return SimpleUploadedFile('test.png', buffer.read(), content_type='image/png')


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class RecipeCatalogTestCase(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.author = User.objects.create_user(username='chef', password='pass12345')
        self.other_user = User.objects.create_user(username='guest', password='pass12345')
        self.category = Category.objects.create(name='Супи')
        self.ingredient = Ingredient.objects.create(name='Картопля')

    def create_recipe(self, **kwargs):
        defaults = {
            'name': 'Борщ',
            'preparation_time': 60,
            'complexity': 'Легко',
            'description': 'Класичний український борщ',
            'image': make_test_image(),
            'author': self.author,
            'category': self.category,
        }
        defaults.update(kwargs)
        return Recipe.objects.create(**defaults)


class ModelTests(RecipeCatalogTestCase):
    def test_recipe_str_returns_name(self):
        recipe = self.create_recipe(name='Вареники')
        self.assertEqual(str(recipe), 'Вареники')

    def test_category_and_ingredient_str(self):
        self.assertEqual(str(self.category), 'Супи')
        self.assertEqual(str(self.ingredient), 'Картопля')

    def test_recipe_steps_are_ordered_by_number(self):
        recipe = self.create_recipe()
        RecipeStep.objects.create(recipe=recipe, number=2, text='Другий крок')
        RecipeStep.objects.create(recipe=recipe, number=1, text='Перший крок')

        numbers = list(recipe.steps.values_list('number', flat=True))
        self.assertEqual(numbers, [1, 2])

    def test_recipe_ingredient_str_returns_ingredient_name(self):
        recipe = self.create_recipe()
        link = RecipeIngredient.objects.create(
            recipe=recipe, ingredient=self.ingredient, amount='2', unit='шт',
        )
        self.assertEqual(str(link), 'Картопля')

    def test_user_cannot_leave_two_reviews_for_same_recipe(self):
        recipe = self.create_recipe()
        Review.objects.create(recipe=recipe, author=self.other_user, rating=5, text='Смачно')

        with self.assertRaises(Exception):
            Review.objects.create(recipe=recipe, author=self.other_user, rating=3, text='Ще раз')


class RecipeListViewTests(RecipeCatalogTestCase):
    def test_list_page_returns_ok_and_uses_correct_template(self):
        self.create_recipe()
        response = self.client.get(reverse('recipe_list'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/recipe_list.html')

    def test_filter_by_category(self):
        other_category = Category.objects.create(name='Десерти')
        matching = self.create_recipe(name='Борщ', category=self.category)
        self.create_recipe(name='Торт', category=other_category)

        response = self.client.get(reverse('recipe_list'), {'category': self.category.name})

        recipes = list(response.context['recipes'])
        self.assertEqual(recipes, [matching])

    def test_filter_by_complexity(self):
        easy = self.create_recipe(name='Борщ', complexity='Легко')
        self.create_recipe(name='Карпаччо', complexity='Важко')

        response = self.client.get(reverse('recipe_list'), {'complexity': 'Легко'})

        recipes = list(response.context['recipes'])
        self.assertEqual(recipes, [easy])

    def test_search_matches_name_or_description(self):
        match_by_name = self.create_recipe(name='Борщ', description='Суп')
        match_by_description = self.create_recipe(name='Суп дня', description='Борщовий смак')
        self.create_recipe(name='Салат', description='Нічого спільного')

        response = self.client.get(reverse('recipe_list'), {'q': 'борщ'})

        recipes = set(response.context['recipes'])
        self.assertEqual(recipes, {match_by_name, match_by_description})

    def test_pagination_splits_recipes_into_pages_of_four(self):
        for i in range(5):
            self.create_recipe(name=f'Рецепт {i}')

        first_page = self.client.get(reverse('recipe_list'))
        second_page = self.client.get(reverse('recipe_list'), {'page': 2})

        self.assertEqual(len(first_page.context['page_obj']), 4)
        self.assertEqual(len(second_page.context['page_obj']), 1)


class RecipeDetailViewTests(RecipeCatalogTestCase):
    def test_detail_page_shows_recipe_and_reviews(self):
        recipe = self.create_recipe()
        Review.objects.create(recipe=recipe, author=self.other_user, rating=4, text='Добре')

        response = self.client.get(reverse('recipe_detail', args=[recipe.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, recipe.name)
        self.assertEqual(len(response.context['reviews']), 1)


class MyRecipesViewTests(RecipeCatalogTestCase):
    def test_anonymous_user_is_redirected_to_login(self):
        response = self.client.get(reverse('my_recipes'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_shows_only_recipes_of_logged_in_user(self):
        own_recipe = self.create_recipe(name='Мій борщ', author=self.author)
        self.create_recipe(name='Чужий борщ', author=self.other_user)

        self.client.login(username='chef', password='pass12345')
        response = self.client.get(reverse('my_recipes'))

        recipes = list(response.context['recipes'])
        self.assertEqual(recipes, [own_recipe])


class RecipeDeleteViewTests(RecipeCatalogTestCase):
    def test_other_user_cannot_delete_recipe(self):
        recipe = self.create_recipe(author=self.author)

        self.client.login(username='guest', password='pass12345')
        response = self.client.post(reverse('recipe_delete', args=[recipe.pk]))

        self.assertEqual(response.status_code, 404)
        self.assertTrue(Recipe.objects.filter(pk=recipe.pk).exists())

    def test_author_can_delete_own_recipe(self):
        recipe = self.create_recipe(author=self.author)

        self.client.login(username='chef', password='pass12345')
        response = self.client.post(reverse('recipe_delete', args=[recipe.pk]))

        self.assertRedirects(response, reverse('my_recipes'))
        self.assertFalse(Recipe.objects.filter(pk=recipe.pk).exists())


class AddReviewViewTests(RecipeCatalogTestCase):
    def test_anonymous_user_is_redirected_to_login(self):
        recipe = self.create_recipe()
        response = self.client.post(reverse('add_review', args=[recipe.pk]), {'rating': 5, 'text': 'Супер'})
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_logged_in_user_can_leave_a_review(self):
        recipe = self.create_recipe()
        self.client.login(username='guest', password='pass12345')

        response = self.client.post(reverse('add_review', args=[recipe.pk]), {'rating': 5, 'text': 'Супер'})

        self.assertRedirects(response, reverse('recipe_detail', args=[recipe.pk]))
        self.assertEqual(Review.objects.filter(recipe=recipe, author=self.other_user).count(), 1)

    def test_user_cannot_leave_second_review_for_same_recipe(self):
        recipe = self.create_recipe()
        Review.objects.create(recipe=recipe, author=self.other_user, rating=5, text='Перший')
        self.client.login(username='guest', password='pass12345')

        self.client.post(reverse('add_review', args=[recipe.pk]), {'rating': 1, 'text': 'Другий'})

        self.assertEqual(Review.objects.filter(recipe=recipe, author=self.other_user).count(), 1)


class ReviewFormTests(TestCase):
    def test_rating_must_be_between_one_and_five(self):
        form = ReviewForm(data={'rating': 6, 'text': 'Текст відгуку'})
        self.assertFalse(form.is_valid())
        self.assertIn('rating', form.errors)

    def test_valid_data_passes(self):
        form = ReviewForm(data={'rating': 5, 'text': 'Чудовий рецепт'})
        self.assertTrue(form.is_valid())
