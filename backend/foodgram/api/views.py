from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from users.permissions import AuthorOrReadOnly

from .filters import IngredientFilter, RecipeFilter
from .pagination import PageLimitPagination
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeCreateUpdateSerializer,
                          RecipeIngredientSerializer, RecipeSerializer,
                          TagSerializer)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (AuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = PageLimitPagination

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return RecipeCreateUpdateSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def add_to_favorite(self, model, user, pk):
        if model.objects.filter(user=user, recipe__id=pk).exists():
            return Response({'errors': 'Рецепт уже в избранном'},
                            status=status.HTTP_400_BAD_REQUEST)
        recipe = get_object_or_404(Recipe, pk=pk)
        instance = model.objects.create(user=user, recipe=recipe)
        serializer = FavoriteSerializer(instance=instance.recipe)
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    def delete_from_favorite(self, model, user, pk):
        obj = model.objects.filter(user=user, recipe__id=pk)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'errors': 'Рецепт уже был удален'},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=[IsAuthenticated,]
    )
    def favorite(self, request, pk):
        if request.method == 'POST':
            return self.add_to_favorite(Favorite, request.user, pk)
        return self.delete_from_favorite(Favorite, request.user, pk)

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=[IsAuthenticated,]
    )
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            return self.add_to_favorite(ShoppingCart, request.user, pk)
        else:
            return self.delete_from_favorite(ShoppingCart, request.user, pk)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated, ]
    )
    def download_shopping_cart(self, request):
        """Отправка списка покупок."""
        ingredients = (
            RecipeIngredient.objects
            .filter(recipe__in_shopping_cart__user=request.user)
            .values('ingredient')
            .annotate(total_amount=Sum('amount'))
            .values_list('ingredient__name', 'total_amount',
                         'ingredient__measurement_unit')
        )
        file_list = []
        [file_list.append(
            '{} - {} {}.'.format(*ingredient)) for ingredient in ingredients]
        file = HttpResponse('Cписок покупок:\n' + '\n'.join(file_list),
                            content_type='text/plain')
        file['Content-Disposition'] = (
            'attachment; filename="shopping_list.txt"')
        return file


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None


class RecipeIngredientViewSet(viewsets.ModelViewSet):
    queryset = RecipeIngredient.objects.all()
    serializer_class = RecipeIngredientSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
