from django_filters.rest_framework import FilterSet, NumberFilter, filters
from recipes.models import Ingredient, Recipe, Tag


class RecipeFilter(FilterSet):
    tags = filters.ModelMultipleChoiceFilter(field_name='tags__slug',
                                             to_field_name='slug',
                                             queryset=Tag.objects.all())

    is_favorited = NumberFilter(
        method='get_is_favorited'
    )
    is_in_shopping_cart = NumberFilter(
        method='get_is_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('is_favorited', 'author', 'tags', 'is_in_shopping_cart', )

    def get_is_favorited(self, queryset, name, value):
        user = self.request.user
        if value:
            return queryset.filter(favorited__user_id=user.id)
        return queryset.all()

    def get_is_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if value:
            return queryset.filter(in_shopping_cart__user_id=user.id)
        return queryset.all()


class IngredientFilter(FilterSet):
    name = filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name', )
