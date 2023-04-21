from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Tag(models.Model):
    name = models.CharField(max_length=128, unique=True)
    color = models.CharField(max_length=7, unique=True)
    slug = models.SlugField(unique=True)


class Ingredient(models.Model):
    name = models.CharField(max_length=128, verbose_name='Название')
    measurement_unit = models.CharField(
        max_length=128,
        verbose_name='Измерение'
    )

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    name = models.CharField(max_length=300)
    image = models.ImageField()
    text = models.TextField()
    ingredients = models.ManyToManyField(Ingredient, verbose_name='Ингридиент')
    tags = models.ManyToManyField(Tag)
    cooking_time = models.DurationField(verbose_name='Время приготовления')


class RecipeIngridient(models.Model):
    name = models.CharField(
        max_length=128,
        verbose_name='Название'
    )
    amount = models.IntegerField(
        verbose_name='Количество'
    )
    measurement_unit = models.CharField(
        max_length=128,
        verbose_name='Измерение'
        )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    ),
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингридиент'
    )
