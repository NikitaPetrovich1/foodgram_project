from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.permissions import (AllowAny,
                                        IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from recipes_app.models import (Favorite,
                                Ingredient,
                                Recipe,
                                RecipeIngredientQuantity,
                                ShoppingCart,
                                Tag
                                )
from recipes_app.serializers import (FavoriteSerializer,
                                     IngredientSerializer,
                                     RecipeCreateSerializer,
                                     RecipeRetrieveSerializer,
                                     ShoppingCartSerializer,
                                     TagSerializer
                                     )
from foodgram_api.filters import IngredientFilter, RecipeFilter
from recipes_app.permissions import IsAuthorOrReadOnly
from foodgram_api.utils import convert_shopping_cart_to_txt


class TagsViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    http_method_names = ('get',)
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class IngredientViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    http_method_names = ('get',)
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_class = IngredientFilter
    pagination_class = None


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeRetrieveSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(author=user)

    def add_recipe(self, model, request, pk, message):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = self.request.user

        if model.objects.filter(recipe=recipe, user=user).exists():
            return Response(data=message, status=status.HTTP_400_BAD_REQUEST)

        data = {
            'recipe': recipe.pk,
            'user': user.pk
        }
        if model.__name__ == 'Favorite':
            serializer = FavoriteSerializer(data=data)
        else:
            serializer = ShoppingCartSerializer(data=data)

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    def delete_recipe(self, model, request, pk, message):
        get_object_or_404(model,
                          recipe=Recipe.objects.filter(pk=pk).first(),
                          user=self.request.user).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True,
            methods=('post',),
            permission_classes=(IsAuthenticated,)
            )
    def favorite(self, request, pk=None):
        return self.add_recipe(Favorite,
                               request,
                               pk,
                               'Рецепт уже есть в избранном.')

    @favorite.mapping.delete
    def delete_from_favorites(self, request, pk=None):
        return self.delete_recipe(Favorite,
                                  request,
                                  pk,
                                  'Такого рецепта нет в избранном.')

    @action(detail=True,
            methods=('post',),
            permission_classes=(IsAuthenticated,)
            )
    def shopping_cart(self, request, pk):
        return self.add_recipe(ShoppingCart,
                               request,
                               pk,
                               'Рецепт уже есть в списке покупок.')

    @shopping_cart.mapping.delete
    def delete_from_shopping_cart(self, request, pk):
        return self.delete_recipe(ShoppingCart,
                                  request,
                                  pk,
                                  'Такого рецепта нет в списке покупок.')

    @action(detail=False,
            permission_classes=(IsAuthenticated,)
            )
    def download_shopping_cart(self, request):
        ingredients = RecipeIngredientQuantity.objects.filter(
            recipe__shopping_cart__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).order_by(
            'ingredient__name'
        ).annotate(
            ingredient_total=Sum('amount')
        )

        return convert_shopping_cart_to_txt(ingredients)
