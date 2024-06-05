from django.apps import AppConfig


class RecipesAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'recipes_app'
    verbose_name = 'Рецепты, ингредиенты и теги'
