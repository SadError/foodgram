from django.contrib import admin

from .models import Tag, Ingredient, Recipe, RecipeIngredient, ShoppingCart


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient


class RecipeAdmin(admin.ModelAdmin):
    # На странице рецепта вывести общее число добавлений этого рецепта в избранное - ЕЩЕ НЕ СДЕЛАНО
    list_display = ('name', 'author',)
    list_filter = ('name', 'author', 'tags',)
    filter_horizontal = ('ingredients',)
    inlines = [RecipeIngredientInline,]


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    list_filter = ('name',)


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag)
admin.site.register(RecipeIngredient)
admin.site.register(ShoppingCart)
