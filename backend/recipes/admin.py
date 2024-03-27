from django.contrib import admin

from .models import (
    Tag, Ingredient, Recipe, IngredientsInRecipe, Favorite, ShoppingCart
)

admin.site.empty_value_display = 'Не задано'


class IngredientsInRecipeInline(admin.TabularInline):
    model = Recipe.ingredients.through
    extra = 1


class TagAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'color',
        'slug'
    )
    list_editable = ('color',)
    search_fields = ('name', 'color', 'slug')


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'measurement_unit',
    )
    search_fields = ('name',)
    list_filter = ('name',)


class IngredientsInRecipeAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'ingredient',
        'recipe',
        'amount'
    )
    search_fields = ('recipe__name', 'ingredient__name')


class RecipeAdmin(admin.ModelAdmin):
    inlines = (IngredientsInRecipeInline,)
    list_display = (
        'pk',
        'name',
        'author'
    )
    list_filter = ('author', 'name', 'tags')
    readonly_fields = ('is_favorited',)

    def is_favorited(self, instance):
        return instance.users_favorites.count()

    is_favorited.short_description = 'В избранном'


class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'user',
        'recipe'
    )
    search_fields = (
        'user__username',
        'user__email',
        'recipe__name'
    )


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'user',
        'recipe'
    )
    search_fields = (
        'user__username',
        'user__email',
        'recipe__name'
    )


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(IngredientsInRecipe, IngredientsInRecipeAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
