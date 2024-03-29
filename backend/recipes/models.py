from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from users.models import User
from .constants import (
    LIMIT_FOR_NAME, SHORT_LIMIT_LENGTH, LENGTH_FOR_DICSRIPTION,
    MIN_COOKING_TIME, MAX_COOCING_TIME,
    MIN_AMOUNT_INGREDIENT, MAX_AMOUNT_INGREDIENT
)


class Tag(models.Model):
    name = models.CharField(
        'Тег',
        max_length=LIMIT_FOR_NAME,
        unique=True
    )
    color = models.CharField(
        'Цвет',
        max_length=SHORT_LIMIT_LENGTH,
        unique=True
    )
    slug = models.SlugField(
        'Слаг',
        unique=True
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        'Ингредиент',
        max_length=LIMIT_FOR_NAME
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=SHORT_LIMIT_LENGTH
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    tags = models.ManyToManyField(
        Tag,
        db_index=True,
        verbose_name='Теги',
        related_name='recipes_tags'
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientsInRecipe',
        through_fields=('recipe', 'ingredient'),
        verbose_name='Ингредиенты',
    )
    name = models.CharField(
        'Название',
        max_length=LIMIT_FOR_NAME
    )
    image = models.ImageField(
        'Картинка рецепта',
        upload_to='recipes/images/'
    )
    text = models.CharField(
        'Описание',
        max_length=LENGTH_FOR_DICSRIPTION
    )
    cooking_time = models.IntegerField(
        'Время приготовления (мин)',
        validators=[
            MinValueValidator(
                MIN_COOKING_TIME,
                f'Минимальное время: {MIN_COOKING_TIME} минут(a)'
            ),
            MaxValueValidator(
                MAX_COOCING_TIME,
                f'Максимальное время: {MAX_COOCING_TIME} минут(a)'
            ),
        ]
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class IngredientsInRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredients_in_recipe',
        verbose_name='Рецепты'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredients_list',
        verbose_name='Ингредиенты',
    )
    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=[
            MinValueValidator(
                MIN_AMOUNT_INGREDIENT,
                f'Минимальное количество: {MIN_AMOUNT_INGREDIENT}'
            ),
            MaxValueValidator(
                MAX_AMOUNT_INGREDIENT,
                f'Максимальное количество: {MAX_AMOUNT_INGREDIENT}'
            ),
        ]
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('ingredient', 'recipe'),
                name='unique_ingredient'
            ),
        )
        verbose_name = 'Ингредиенты рецепта'
        verbose_name_plural = 'Ингредиенты рецептов'

    def __str__(self):
        return f'{self.recipe} с {self.ingredient}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Избранные рецепты',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='users_favorites',
        verbose_name='Избранные у пользователей',
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_favorite'
            ),
        )
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'

    def __str__(self):
        return f'{self.recipe} в избранном'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Список покупок',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='В списке у пользователей'
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_recipe'
            ),
        )
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'

    def __str__(self):
        return f'Список покупок {self.user}'
