from django.contrib import admin
from django.contrib.admin import display

from recipes.models import (Favorite, Ingredient, IngredientsInRecipe, Recipe,
                            ShoppingCart, Tag)


class IngredientsInline(admin.TabularInline):
    model = Recipe.ingredients.through
    extra = 1
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author', 'added_to_favorites')
    readonly_fields = ('added_to_favorites',)
    list_filter = ('author', 'name', 'tags',)
    inlines = (IngredientsInline,)

    @display
    def added_to_favorites(self, obj):
        return Favorite.objects.filter(recipe=obj).count()


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    list_filter = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug',)


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe',)


@admin.register(IngredientsInRecipe)
class IngredientsInRecipeAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount',)
