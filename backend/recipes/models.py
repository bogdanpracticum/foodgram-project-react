from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from api.constants import ITEM_NAME_MAX_LEN, SLUG_MAX_LEN
from users.models import CustomUser

TIME_TO_COOKING_MIN = 1
TIME_TO_COOKING_MAX = 32000


class Tag(models.Model):
    name = models.CharField(
        max_length=10,
        unique=True,
        verbose_name='Название тега'
    )
    color = models.CharField(
        max_length=10,
        unique=True,
        verbose_name='Цвет тега'
    )
    slug = models.SlugField(
        max_length=SLUG_MAX_LEN,
        unique=True,
        verbose_name='Уникальный слаг'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['name']

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=ITEM_NAME_MAX_LEN,
        verbose_name='Название ингредиента'
    )
    measurement_unit = models.CharField(
        max_length=ITEM_NAME_MAX_LEN,
        verbose_name='Единица измерения'
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique ingredient'
            )
        ]

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(
        max_length=ITEM_NAME_MAX_LEN,
        verbose_name='Название рецепта'
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientsInRecipe',
        through_fields=('recipe', 'ingredient'),
        verbose_name='Ингредиенты',
        related_name='recipes',
        help_text='Список ингредиентов'
    )
    tags = models.ManyToManyField(
        Tag,
        db_index=True,
        verbose_name='Теги',
        related_name='recipes',
    )
    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='recipes/'
    )
    text = models.TextField(
        verbose_name='Описание рецепта'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления (мин.)',
        validators=(
            MinValueValidator(
                TIME_TO_COOKING_MIN,
                message='Время приготовления должно быть больше 1 минуты!'
            ),
            MaxValueValidator(
                TIME_TO_COOKING_MAX,
                message='Слишком большое время приготовления'
            )),
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации рецепта',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class IngredientsInRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient_in_recipe',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredients_list',
        verbose_name='Ингредиент'
    )
    amount = models.PositiveSmallIntegerField(
        validators=(
            MinValueValidator(
                TIME_TO_COOKING_MIN,
                message='Количество ингредиентов не может быть меньше 1!'),
            MaxValueValidator(
                TIME_TO_COOKING_MAX,
                message='Количество ингредиентов слишком большое'
            )),
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'
        constraints = [
            models.UniqueConstraint(
                fields=['ingredient', 'recipe'],
                name='unique_ingredient'
            )
        ]
        ordering = ['ingredient']

    def __str__(self):
        return self.name


class FavoriteAndCartAbstract(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        null=True,
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Избранное/корзина'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='%(app_label)s_%(class)s_is_unique'
            ),
        )
        abstract = True
        ordering = ['user']

    def __str__(self):
        return self.name


class ShoppingCart(FavoriteAndCartAbstract):

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        default_related_name = 'shopping_cart'
        ordering = ['name']

    def __str__(self):
        return self.name


class Favorite(FavoriteAndCartAbstract):

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        default_related_name = 'favorites'
        ordering = ['name']

    def __str__(self):
        return self.name
