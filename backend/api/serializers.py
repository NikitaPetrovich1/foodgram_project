import base64

import webcolors
from rest_framework import serializers
from django.core.files.base import ContentFile
from django.db import transaction

from recipes.models import (
    Tag, Ingredient, Recipe, IngredientsInRecipe, Favorite, ShoppingCart
)
from users.serializers import CustomUserSerializer


class Hex2NameColor(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('Для этого цвета нет имени')
        return data


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):
    color = Hex2NameColor()

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)


class IngredientCreateSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientsInRecipe
        fields = ('id', 'amount')


class IngredientForRecipesSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientsInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class ShortRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class RecipeReadSerializer(serializers.ModelSerializer):
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    author = CustomUserSerializer()
    tags = TagSerializer(many=True)
    ingredients = IngredientForRecipesSerializer(
        source='ingredients_in_recipe', read_only=True, many=True
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_in(self, obj, model):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return model.objects.filter(user=request.user, recipe=obj).exists()

    def get_is_favorited(self, obj):
        return self.get_in(obj, Favorite)

    def get_is_in_shopping_cart(self, obj):
        return self.get_in(obj, ShoppingCart)


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = IngredientCreateSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'ingredients', 'tags', 'image', 'name', 'text', 'cooking_time'
        )

    def to_representation(self, instance):
        serializer = RecipeReadSerializer(instance)
        return serializer.data

    def create_ingredients(self, ingredients, recipe):
        for ingredient in ingredients:
            amount = ingredient['amount']
            ingredient = ingredient['id']
            ingredients, _ = IngredientsInRecipe.objects.get_or_create(
                recipe=recipe,
                ingredient=ingredient,
                amount=amount
            )

    @transaction.atomic
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        recipe.save()
        self.create_ingredients(ingredients, recipe)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.ingredients.clear()
        self.create_ingredients(ingredients, instance)
        instance.tags.clear()
        instance.tags.set(tags)
        return super().update(instance, validated_data)

    def validate(self, data):
        current_ingredients = data.get('ingredients')
        if not current_ingredients:
            raise serializers.ValidationError(
                'Поле с ингредиентами не может быть пустым'
            )

        unique_ingredients = []
        for ingredient in current_ingredients:
            ingredient_id = ingredient['id']
            if int(ingredient['amount']) <= 0:
                raise serializers.ValidationError(
                    f'Некорректное количество для {ingredient_id}'
                )

            if not isinstance(ingredient['amount'], int):
                raise serializers.ValidationError(
                    'Количество ингредиентов должно быть целым числом'
                )

            if ingredient_id not in unique_ingredients:
                unique_ingredients.append(ingredient_id)
            else:
                raise serializers.ValidationError(
                    'В рецепте не может быть повторяющихся ингредиентов'
                )

        current_tags = data.get('tags')
        if not current_tags:
            raise serializers.ValidationError(
                'Поле с тегами не может быть пустым'
            )

        unique_tags = []
        for tag in current_tags:
            if tag not in unique_tags:
                unique_tags.append(tag)
            else:
                raise serializers.ValidationError(
                    'В рецепте не может быть повторяющихся тегов'
                )

        return data
