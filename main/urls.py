from django.urls import path
from django.contrib.auth import views as auth_views

from main import views
from .forms import LoginForm

urlpatterns = [
    path('', views.recipe_list, name='recipe_list'),
    path('recipe/<int:pk>/', views.recipe_detail, name='recipe_detail'),
    path('my_recipes/', views.my_recipes, name='my_recipes'),
    path('login/', auth_views.LoginView.as_view(authentication_form=LoginForm), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='recipe_list'), name='logout'),
    path('register/', views.register, name='register'),
    path('recipe/new/', views.recipe_create, name='recipe_create'),
    path('recipe/<int:pk>/delete/', views.recipe_delete, name="recipe_delete"),
    path('recipe/<int:pk>/review/', views.add_review, name="add_review")
]
