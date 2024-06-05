from colorfield.fields import ColorField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from recipes_app.constants import (
    INGREDIENT_AMOUNT_MAX_VALUE,
    INGREDIENT_AMOUNT_MIN_VALUE,
    INGREDIENT_NAME_MAX_LENGTH,
    INGREDIENT_UNIT_MAX_LENGTH,
    RECIPE_COOKING_TIME_MAX_VALUE,
    RECIPE_COOKING_TIME_MIN_VALUE,
    RECIPE_IMAGE_MAX_VALUE,
    RECIPE_NAME_MAX_LENGTH,
    TAG_COLOR_MAX_LENGTH,
    TAG_NAME_MAX_LENGTH,
    TAG_SLUG_MAX_LENGTH
)
from users_app.models import User


class Tag(models.Model):
    """
    Модель Тегов.
    """
    name = models.CharField(
        blank=False,
        verbose_name='Название',
        max_length=TAG_NAME_MAX_LENGTH,
        help_text=f'Ограничение {TAG_NAME_MAX_LENGTH} символов.'
    )
    color = ColorField(
        blank=False,
        verbose_name='Цвет',
        help_text=f'Поддерживается около {TAG_COLOR_MAX_LENGTH} названий.',
        max_length=TAG_COLOR_MAX_LENGTH
    )
    slug = models.SlugField(
        blank=False,
        unique=True,
        max_length=TAG_SLUG_MAX_LENGTH,
        verbose_name='Идентификатор',
        help_text=('Идентификатор страницы URL. Разрешены символы латиницы'
                   ', цифры, дефис и подчёркивание.'
                   f' Ограничение {TAG_SLUG_MAX_LENGTH} символов.'),
    )

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """
    Модель Ингредиентов.
    """
    name = models.CharField(
        blank=False,
        verbose_name='Название',
        max_length=INGREDIENT_NAME_MAX_LENGTH,
        help_text=f'Ограничение {INGREDIENT_NAME_MAX_LENGTH} символов.'
    )
    measurement_unit = models.CharField(
        blank=False,
        verbose_name='Единица измерения',
        help_text=('Например, кг., гр., шт. и т.д.'
                   f' Ограничение {INGREDIENT_UNIT_MAX_LENGTH} символов.'),
        max_length=INGREDIENT_UNIT_MAX_LENGTH
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_Ingredient'
            ),
        )
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self) -> str:
        return self.name


class Recipe(models.Model):
    """
    Модель рецептов.
    """
    name = models.CharField(
        blank=False,
        verbose_name='Название',
        help_text=f'Ограничение {RECIPE_NAME_MAX_LENGTH} символов.',
        max_length=RECIPE_NAME_MAX_LENGTH
    )
    pub_date = models.DateTimeField(
        blank=False,
        auto_now_add=True,
        verbose_name='Дата публикации',
        db_index=True
    )
    text = models.TextField(
        blank=False,
        verbose_name='Описание рецепта',
        help_text='Подробное описание приготовления.'
    )
    image = models.ImageField(
        blank=False,
        verbose_name='Фото',
        upload_to='recipes/images/',
        default=None,
        help_text=f'Максимальный размер {RECIPE_IMAGE_MAX_VALUE} МБ.'
    )
    cooking_time = models.PositiveSmallIntegerField(
        blank=False,
        verbose_name='Время приготовления, мин.',
        help_text=(
            f'Минимально - {RECIPE_COOKING_TIME_MIN_VALUE} мин. Целое число.'),
        validators=[MinValueValidator(RECIPE_COOKING_TIME_MIN_VALUE),
                    MaxValueValidator(RECIPE_COOKING_TIME_MAX_VALUE)]
    )
    author = models.ForeignKey(
        User,
        blank=False,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта'
    )
    ingredients = models.ManyToManyField(Ingredient,
                                         blank=False,
                                         through='RecipeIngredientQuantity',
                                         verbose_name='Ингредиенты'
                                         )
    tags = models.ManyToManyField(Tag,
                                  blank=False,
                                  related_name='recipes_tags',
                                  verbose_name='Теги'
                                  )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'


class RecipeIngredientQuantity(models.Model):
    """
    Таблица для связи Ингредиентов и Рецептов с количеством определенного
    ингредиента.
    """
    ingredient = models.ForeignKey(Ingredient,
                                   blank=False,
                                   null=False,
                                   on_delete=models.CASCADE,
                                   verbose_name='Ингредиент',
                                   related_name='ingredient_list',
                                   db_index=True
                                   )
    recipe = models.ForeignKey(
        Recipe,
        blank=False,
        null=False,
        related_name='recipe_ingredients',
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        db_index=True
    )
    amount = models.PositiveSmallIntegerField(
        blank=False,
        null=False,
        verbose_name='Количество',
        help_text=(
            f'Минимально - {INGREDIENT_AMOUNT_MIN_VALUE}.'
            f' Максимально - {INGREDIENT_AMOUNT_MAX_VALUE}. Целые числа.'),
        validators=[MinValueValidator(INGREDIENT_AMOUNT_MIN_VALUE),
                    MaxValueValidator(INGREDIENT_AMOUNT_MAX_VALUE)],
    )

    class Meta:
        verbose_name = 'ингредиент и количество'
        verbose_name_plural = 'Ингредиенты и количество'
        constraints = (models.UniqueConstraint(
            fields=('ingredient', 'recipe'),
            name='unique_ingredient'
        ),
        )

    def __str__(self) -> str:
        return (
            f'{self.amount} {self.ingredient.measurement_unit}'
            f' {self.ingredient.name}'
        )


class AbstractUserRecipeRelation(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:
        abstract = True
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_%(class)s'
            ),
        )


class Favorite(AbstractUserRecipeRelation):
    class Meta(AbstractUserRecipeRelation.Meta):
        verbose_name = 'избранное'
        verbose_name_plural = 'Избранное'
        default_related_name = 'users_favorites'

    def __str__(self) -> str:
        return f'{self.recipe} в избранном'


class ShoppingCart(AbstractUserRecipeRelation):
    class Meta(AbstractUserRecipeRelation.Meta):
        verbose_name = 'список покупок'
        verbose_name_plural = 'Списки покупок'
        default_related_name = 'shopping_cart'

    def __str__(self):
        return f'Список покупок {self.user}'
