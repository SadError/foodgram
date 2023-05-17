from django.contrib import admin

from .models import Ingredient, Recipe, RecipeIngredient, ShoppingCart, Tag


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'favorites_amount')
    list_filter = ('name', 'author', 'tags',)
    filter_horizontal = ('ingredients',)
    inlines = [RecipeIngredientInline,]

    def favorites_amount(self, obj):
        return obj.favorited.count()


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    list_filter = ('name',)


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag)
admin.site.register(RecipeIngredient)
admin.site.register(ShoppingCart)
