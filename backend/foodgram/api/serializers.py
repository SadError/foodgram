from drf_extra_fields.fields import Base64ImageField
from recipes.models import Favorite, Ingredient, Recipe, RecipeIngredient, Tag
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from users.models import Subscribers, User

from djoser.serializers import UserCreateSerializer, UserSerializer


class UserSignUpSerializer(UserCreateSerializer):
    """Сериализатор для регистрации пользователей."""
    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'password')


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для списка избранных рецептов"""
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class UsersSerializer(UserSerializer):
    """Сериализатор списка пользователей."""
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    def get_is_subscribed(self, obj):
        return (
            self.context.get('request').user.is_authenticated
            and Subscribers.objects.filter(user=self.context['request'].user,
                                           author=obj).exists()
        )

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name',
                  'is_subscribed',)


class SubscribersSerializer(serializers.ModelSerializer):
    """Сериализатор списка подписок пользователя."""
    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        serializer = FavoriteSerializer(recipes, many=True, read_only=True)
        return serializer.data

    def get_is_subscribed(self, obj):
        return obj.id in self.context['subscriptions']

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name',
                  'is_subscribed',
                  'recipes', 'recipes_count')


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор подписки/отписки на пользователя."""
    class Meta:
        model = Subscribers
        fields = ('author', 'user')

    def validate(self, data):
        request = self.context.get('request')
        user = request.user
        author = data.get('author')
        if Subscribers.objects.filter(author=author, user=user).exists():
            raise ValidationError(
                detail='Вы уже подписаны на этого пользователя.',
                code=status.HTTP_400_BAD_REQUEST
            )
        if user == author:
            raise ValidationError(
                detail='Вы не можете подписаться на самого себя.',
                code=status.HTTP_400_BAD_REQUEST
            )
        return data

    def to_representation(self, instance):
        return SubscribersSerializer(
            instance.author,
            context=self.context
        ).data


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов"""
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для представления ингредиентов в списке рецептов"""
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
        fields = ('id', 'name', 'measurement_unit', 'amount')


class IngredientCreateInRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для списка ингредиентов при создании рецепта"""
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField(write_only=True, min_value=1)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания/редактирования рецепта"""
    ingredients = IngredientCreateInRecipeSerializer(many=True)
    image = Base64ImageField(use_url=True)

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        RecipeIngredient.objects.bulk_create([
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient['id'],
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
                    ingredient=ingredient['id'],
                    amount=ingredient['amount']
                )
                for ingredient in ingredients
            ]
            RecipeIngredient.objects.bulk_create(
                create_ingredients
            )
        return super().update(instance, validated_data)

    def to_representation(self, obj):
        """Возвращаем прдеставление в таком же виде, как и GET-запрос."""
        self.fields.pop('ingredients')
        representation = super().to_representation(obj)
        representation['ingredients'] = RecipeIngredientSerializer(
            RecipeIngredient.objects.filter(recipe=obj).all(), many=True
        ).data
        return representation

    class Meta:
        model = Recipe
        fields = (
            'name', 'image', 'text', 'ingredients', 'tags', 'cooking_time'
        )
        read_only_fields = ('author',)


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для списка рецептов"""
    ingredients = RecipeIngredientSerializer(many=True, read_only=True,
                                             source='recipeingredients')
    author = UsersSerializer(read_only=True)
    tags = TagSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        return (request and request.user.is_authenticated
                and Favorite.objects.filter(
                    recipe=obj, user=request.user).exists())

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return (
            request.user.is_authenticated
            and request.user.cart.filter(recipe=obj).exists()
        )

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'name', 'image', 'text', 'cooking_time', 'is_in_shopping_cart'
        )


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для списка ингредиентов"""
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')
