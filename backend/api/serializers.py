import base64

from django.core.files.base import ContentFile
from django.db import transaction
from rest_framework import serializers

from recipes.models import (Favorite, Ingredient, IngredientsInRecipe, Recipe,
                            Tag)
from users.serializers import CustomUserSerializer

TIME_TO_COOKING_MIN = 1
TIME_TO_COOKING_MAX = 32000
M_I = 1


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class TagField(serializers.SlugRelatedField):

    def to_representation(self, value):
        request = self.context.get('request')
        context = {'request': request}
        serializer = TagSerializer(value, context=context)

        return serializer.data


class IngredientsInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(
        source='ingredient.id'
    )
    name = serializers.ReadOnlyField(
        source='ingredient.name'
    )
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientsInRecipe
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):

        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='photo.' + ext)

        return super().to_internal_value(data)


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagField(
        queryset=Tag.objects.all(),
        slug_field='id',
        many=True,
    )
    author = CustomUserSerializer(
        read_only=True
    )
    ingredients = IngredientsInRecipeSerializer(
        source='ingredient_in_recipe',
        many=True,
        read_only=True,
    )
    image = serializers.ReadOnlyField(
        source='image.url'
    )
    is_favorited = serializers.SerializerMethodField(
        method_name='get_is_favorited'
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='get_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = (
            'tags',
            'author',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
            'id',
            'ingredients',
        )

    def get_is_favorited(self, obj):
        request = self.context.get('request')

        if not request or request.user.is_anonymous:
            return False

        return Favorite.objects.filter(
            user=request.user,
            recipe=obj
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')

        if not request or request.user.is_anonymous:
            return False

        return request.user.shopping_cart.filter(recipe=obj).exists()


class IngredientAddSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientsInRecipe
        fields = ('id', 'amount')

    def validate_amount(self, value):
        if value < TIME_TO_COOKING_MIN:
            raise serializers.ValidationError('Минимальное значение: 1')
        if value > TIME_TO_COOKING_MAX:
            raise serializers.ValidationError('Максимальное значение: 32000')
        return value


class RecipeAddSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    ingredients = IngredientAddSerializer(
        many=True
    )
    author = CustomUserSerializer(
        read_only=True
    )
    image = Base64ImageField(
        use_url=True
    )
    name = serializers.CharField(
        required=False
    )
    text = serializers.CharField(
        required=False
    )
    cooking_time = serializers.IntegerField(
        min_value=TIME_TO_COOKING_MIN,
        max_value=TIME_TO_COOKING_MAX
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'name',
            'ingredients',
            'image',
            'text',
            'cooking_time',
            'author',
        )

    def to_representation(self, instance):
        serializer = RecipeSerializer(instance)

        return serializer.data

    def add_ingredients(self, ingredients, recipe):
        ingredients_to_create = []
        for ingredient in ingredients:
            amount = ingredient['amount']
            ingredient_id = ingredient['id']
            ingredients_to_create.append(
                IngredientsInRecipe(recipe=recipe, ingredient=ingredient_id,
                                    amount=amount)
            )

        IngredientsInRecipe.objects.bulk_create(ingredients_to_create)

    @transaction.atomic
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        recipe.save()
        self.add_ingredients(ingredients, recipe)

        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')

        if ingredients is not None:
            instance.ingredients.clear()

        self.add_ingredients(ingredients, instance)
        instance.tags.clear()
        instance.tags.set(tags)

        return super().update(instance, validated_data)

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')

        if not ingredients:
            raise serializers.ValidationError('Необходимо указать ингредиент')

        ingredients_list = []

        for item in ingredients_list:
            name = item['id']

            if name in ingredients_list:
                raise serializers.ValidationError('Такой ингредиент уже есть')
            ingredients_list.append(name)

            if int(item['amount']) <= 0:
                raise serializers.ValidationError({
                    'item': ('Количество ингредиента должно '
                             'быть больше 0')
                }
                )

        return data

    def validate_tags(self, value):
        tags = value

        if not tags:
            raise serializers.ValidationError(
                'Необходимо выбрать хотя бы один тег!'
            )

        if len(tags) != len(set(tags)):
            raise serializers.ValidationError(
                'Теги должны быть уникальными'
            )

        return value


class RecipeSmallSerializer(serializers.ModelSerializer):
    image = serializers.ReadOnlyField(
        source='image.url'
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )
