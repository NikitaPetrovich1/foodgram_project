from rest_framework.mixins import (
    RetrieveModelMixin, ListModelMixin
)
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import filters, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.validators import ValidationError
from django.db.models import Sum
from django.shortcuts import get_object_or_404

from recipes.models import (
    Tag, Ingredient, Recipe, Favorite, ShoppingCart, IngredientsInRecipe
)
from .serializers import (
    TagSerializer, IngredientSerializer, RecipeReadSerializer,
    RecipeCreateSerializer, ShortRecipeSerializer
)
from .permissions import IsAuthorOrReadOnly
from .filters import RecipeFilter, IngredientFilter
from .utils import convert_to_txt


class TagsViewSet(RetrieveModelMixin, ListModelMixin, GenericViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class IngredientViewSet(RetrieveModelMixin, ListModelMixin, GenericViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_class = IngredientFilter
    pagination_class = None


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeReadSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(author=user)

    def add_recipe(self, model, request, pk, message):
        try:
            recipe = Recipe.objects.get(pk=pk)
        except Exception:
            raise ValidationError('Такого рецепта не существует')

        user = self.request.user

        if model.objects.filter(recipe=recipe, user=user).exists():
            raise ValidationError(message)

        model.objects.create(recipe=recipe, user=user)
        serializer = ShortRecipeSerializer(recipe)
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    def delete_recipe(self, model, request, pk, message):
        recipe = get_object_or_404(Recipe, pk=pk)

        user = self.request.user

        obj, _ = model.objects.filter(recipe=recipe, user=user).delete()
        if not obj:
            raise ValidationError(message)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk=None):
        if request.method == 'POST':
            if_exists = 'Рецепт уже добавлен в избранное'
            return self.add_recipe(Favorite, request, pk, if_exists)
        else:
            if_not_exists = 'Такого рецепта нет в избранном'
            return self.delete_recipe(Favorite, request, pk, if_not_exists)

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        if_exists = 'Рецепт уже добавлен в список покупок'
        if request.method == 'POST':
            return self.add_recipe(ShoppingCart, request, pk, if_exists)
        else:
            if_not_exists = 'Такого рецепта нет в списке покупок'
            return self.delete_recipe(ShoppingCart, request, pk, if_not_exists)

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        ingredients = IngredientsInRecipe.objects.filter(
            recipe__shopping_cart__user=request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).order_by(
            'ingredient__name'
        ).annotate(ingredient_total=Sum('amount'))

        return convert_to_txt(ingredients)
