# Recipe Catalog

A Django web application for browsing, publishing, and reviewing cooking recipes. Built as a learning/portfolio project to practice Django fundamentals: models & relations, forms, authentication, class-free views, templating with Bootstrap 5, and automated testing.

**Live demo:** [recipe-catalog-5h7j.onrender.com](https://recipe-catalog-5h7j.onrender.com/)

> Hosted on Render's free tier — the first request after a period of inactivity may take ~30–60 seconds while the service spins back up.

## Features

- **Recipe catalog** with category and complexity filters, free-text search, and pagination.
- **Recipe detail page** with ingredients, step-by-step instructions, and an image.
- **User accounts** — registration, login/logout, and a "My recipes" page scoped to the logged-in user.
- **Recipe management** — authenticated users can create recipes (with a dynamic ingredients/steps formset) and delete only their own.
- **Reviews & ratings** — logged-in users can leave one review (1–5 stars + comment) per recipe; duplicate reviews are blocked.
- **Django admin** panel for managing categories, ingredients, recipes, and reviews.
- **Automated tests** covering models, views, permissions, and forms (see [Testing](#testing)).

## Tech stack

- [Django 6.1](https://www.djangoproject.com/) (SQLite database)
- [Bootstrap 5](https://getbootstrap.com/) for styling
- [Pillow](https://python-pillow.org/) for image handling

## Project structure

```
recipes/        # Django project settings & root URLconf
main/           # Application: models, views, forms, templates, tests
  models.py     # Category, Ingredient, Recipe, RecipeIngredient, RecipeStep, Review
  views.py      # recipe_list, recipe_detail, my_recipes, recipe_create, recipe_delete, add_review ...
  forms.py      # RegisterForm, LoginForm, RecipeForm, RecipeStepFormSet, ReviewForm
  templates/    # HTML templates (Bootstrap 5)
  tests.py      # Automated test suite
```

## Getting started

### Prerequisites

- Python 3.11+

### Setup

```bash
# 1. Clone the repository
git clone <repository-url>
cd recipe-catalog

# 2. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Apply database migrations
python manage.py migrate

# 5. (Optional) create an admin user
python manage.py createsuperuser

# 6. Run the development server
python manage.py runserver
```

The app will be available at `http://127.0.0.1:8000/`, and the admin panel at `/admin/`.

## Testing

The project includes a test suite (`main/tests.py`) covering models, view behavior (filtering, search, pagination, permissions), and form validation.

```bash
python manage.py test main
```

## Possible improvements

- Database-level full-text search (current search is done in Python to correctly handle case-insensitive Cyrillic matching, since SQLite's `LIKE` is ASCII-only).
- REST API for recipes/reviews.
- Recipe favorites/bookmarks.
- Average rating displayed on the recipe list, not just on the detail page.
