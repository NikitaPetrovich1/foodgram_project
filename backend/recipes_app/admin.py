from django.contrib import admin

from recipes_app.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredientQuantity,
    ShoppingCart,
    Tag,
)


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
    list_filter = ('name',)


class RecipeIngredientQuantityAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'ingredient',
        'recipe',
        'amount'
    )


class RecipeIngredientQuantityInline(admin.TabularInline):
    model = Recipe.ingredients.through
    min_num = 1


class RecipeAdmin(admin.ModelAdmin):
    inlines = (RecipeIngredientQuantityInline,)
    list_display = (
        'pk',
        'name',
        'author'
    )
    list_filter = ('name', 'author', 'tags')
    readonly_fields = ('is_favorite',)

    def is_favorite(self, instance):
        return instance.users_favorites.count()

    is_favorite.short_description = 'В избранном'


class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'user',
        'recipe'
    )


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'user',
        'recipe'
    )


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(RecipeIngredientQuantity, RecipeIngredientQuantityAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
