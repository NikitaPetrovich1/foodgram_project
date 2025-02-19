from django_filters import rest_framework as filters

from recipes_app.models import Ingredient, Recipe, Tag
from users_app.models import User


class RecipeFilter(filters.FilterSet):
    author = filters.ModelChoiceFilter(queryset=User.objects.all())
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        queryset=Tag.objects.all(),
        to_field_name='slug',
    )
    is_favorited = filters.BooleanFilter(method='get_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')

    def get_is_favorited(self, queryset, name, value):
        if self.request.user and value:
            return queryset.filter(
                users_favorites__user__id=self.request.user.id
            )
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        if self.request.user and value:
            return queryset.filter(
                shopping_cart__user__id=self.request.user.id
            )
        return queryset


class IngredientFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)
