from rest_framework import serializers
from django.contrib.auth import get_user_model

from recipes.models import Recipe, Ingredient, Tag, RecipeIngredient

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор списка пользователей."""

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name',
        )


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов"""
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для представления ингредиента в рецепте"""
    name = serializers.StringRelatedField(
        source='ingredient.name'
    )
    measurement_unit = serializers.StringRelatedField(
        source='ingredient.measurement_unit'
    )
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        read_only=True,
    )

    class Meta:
        model = RecipeIngredient
        fields = ('amount', 'name', 'measurement_unit', 'id')


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания/редактирования рецепта"""
    ingredients = RecipeIngredientSerializer(many=True)

    def create(self, validated_data):
        author = self.context['request'].user
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=author, **validated_data)
        RecipeIngredient.objects.bulk_create([
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient['ingredient'],
                amount=ingredient['amount']
            )
            for ingredient in ingredients_data
        ])
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients', None)
        if ingredients is not None:
            instance.ingredients.clear()

            create_ingredients = [
                RecipeIngredient(
                    recipe=instance,
                    ingredient=ingredient['ingredient'],
                    amount=ingredient['amount']
                )
                for ingredient in ingredients
            ]
            RecipeIngredient.objects.bulk_create(
                create_ingredients
            )
        return super().update(instance, validated_data)

    class Meta:
        model = Recipe
        fields = (
            'name', 'image', 'text', 'ingredients', 'tags', 'cooking_time'
        )
        read_only_fields = ('author',)


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для списка рецептов"""
    ingredients = serializers.SerializerMethodField()
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True)

    def get_ingredients(self, obj):
        return RecipeIngredientSerializer(
            RecipeIngredient.objects.filter(recipe=obj).all(), many=True
        ).data

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'name', 'image', 'text', 'cooking_time'
        )


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для списка ингредиентов"""
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')



