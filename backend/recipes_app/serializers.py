import base64

import webcolors
from django.core.files.base import ContentFile
from rest_framework import serializers

from recipes_app.constants import (INGREDIENT_AMOUNT_MAX_VALUE,
                                   INGREDIENT_AMOUNT_MIN_VALUE,
                                   IMAGE_EXTENSION_TYPE,
                                   RECIPE_COOKING_TIME_MAX_VALUE,
                                   RECIPE_COOKING_TIME_MIN_VALUE,
                                   TAG_SLUG_MAX_LENGTH)
from recipes_app.models import (Favorite,
                                Ingredient,
                                Recipe,
                                RecipeIngredientQuantity,
                                ShoppingCart,
                                Tag)
from users_app.serializers import UserSerializer


class Hex2NameColor(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('Для этого цвета нет имени.')
        return data


class Base64ImageField(serializers.ImageField):

    def __init__(self, *args, **kwargs):
        self.file_name = kwargs.pop('file_name', 'temp')
        super().__init__(*args, **kwargs)

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[IMAGE_EXTENSION_TYPE]
            data = ContentFile(base64.b64decode(imgstr),
                               name=self.file_name + '.' + ext)

        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):
    color = Hex2NameColor()
    slug = serializers.RegexField(
        regex=r'^[-a-zA-Z0-9_]+$',
        max_length=TAG_SLUG_MAX_LENGTH
    )

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)


class RecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Favorite
        fields = ('id', 'recipe', 'user')


class ShoppingCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShoppingCart
        fields = ('id', 'recipe', 'user')


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredientQuantity
        fields = ('id', 'name', 'measurement_unit', 'amount')


class IngredientCreateSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField(
        min_value=INGREDIENT_AMOUNT_MIN_VALUE,
        max_value=INGREDIENT_AMOUNT_MAX_VALUE
    )

    class Meta:
        model = RecipeIngredientQuantity
        fields = ('id', 'amount')


class RecipeRetrieveSerializer(serializers.ModelSerializer):
    author = UserSerializer()
    ingredients = IngredientRecipeSerializer(
        source='recipe_ingredients',
        read_only=True,
        many=True
    )
    tags = TagSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'author',
            'ingredients',
            'image',
            'text',
            'cooking_time',
            'tags',
            'is_favorited',
            'is_in_shopping_cart',
        )

    def get_model_object(self, obj, model):
        request = self.context.get('request')

        return not request or (
            not request.user.is_anonymous
            and model.objects.filter(
                user=request.user,
                recipe=obj).exists()
        )

    def get_is_favorited(self, obj):
        return self.get_model_object(obj, Favorite)

    def get_is_in_shopping_cart(self, obj):
        return self.get_model_object(obj, ShoppingCart)


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = IngredientCreateSerializer(many=True)
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(
        min_value=RECIPE_COOKING_TIME_MIN_VALUE,
        max_value=RECIPE_COOKING_TIME_MAX_VALUE
    )

    class Meta:
        model = Recipe
        fields = (
            'ingredients', 'tags', 'image', 'name', 'text', 'cooking_time'
        )

    def to_representation(self, instance):
        serializer = RecipeRetrieveSerializer(instance)
        return serializer.data

    def create_ingredients(self, ingredients, recipe):
        for ingredient in ingredients:
            amount = ingredient['amount']
            ingredient = ingredient['id']
            ingredients, _ = RecipeIngredientQuantity.objects.get_or_create(
                recipe=recipe,
                ingredient=ingredient,
                amount=amount
            )

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        recipe.save()
        self.create_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.ingredients.clear()
        self.create_ingredients(ingredients, instance)
        instance.tags.clear()
        instance.tags.set(tags)
        return super().update(instance, validated_data)

    def validate(self, data):
        ingredients = data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError(
                'Поле с ингредиентами должно быть заполнено.'
            )

        unique_ingredients = []
        for ingredient in ingredients:
            ingredient_name = ingredient.get(
                'recipes_ingredients__name',
                None
            )
            ingredient_id = ingredient['id']
            if int(ingredient['amount']) <= 0:
                raise serializers.ValidationError(
                    f'Количество {ingredient_name} должно быть больше 0.'
                )

            if not isinstance(ingredient['amount'], int):
                raise serializers.ValidationError(
                    f'Количество {ingredient_name} должно быть целым числом.'
                )

            if ingredient_id not in unique_ingredients:
                unique_ingredients.append(ingredient_id)
            else:
                raise serializers.ValidationError(
                    f'Ингредиент {ingredient_name} уже указан в рецепте.'
                )

        tags = data.get('tags')
        if not tags:
            raise serializers.ValidationError(
                'Поле с тегами должно быть заполнено.'
            )

        unique_tags = []
        for tag in tags:
            if tag not in unique_tags:
                unique_tags.append(tag)
            else:
                raise serializers.ValidationError(
                    'Теги не должны повторяться.'
                )

        return data
