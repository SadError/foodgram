from rest_framework.routers import DefaultRouter

from django.urls import include, path

from .views import RecipeViewSet, IngredientViewSet, TagViewSet

router = DefaultRouter()
router.register(r'recipes', RecipeViewSet)
router.register(r'ingredients', IngredientViewSet)
router.register(r'tags', TagViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
