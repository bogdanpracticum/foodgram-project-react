from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.validators import ValidationError
from rest_framework.viewsets import ReadOnlyModelViewSet

from api.filters import IngredientFilter, RecipeFilter
from api.pagination import CustomPagination
from api.permissions import IsAuthorOrAdminOnly
from api.serializers import (IngredientSerializer, RecipeAddSerializer,
                             RecipeSerializer, RecipeSmallSerializer,
                             TagSerializer)
from recipes.models import (Favorite, Ingredient, IngredientsInRecipe, Recipe,
                            ShoppingCart, Tag)


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (IngredientFilter,)
    filterset_class = IngredientFilter
    search_fields = ('^name',)


class TagViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrAdminOnly,)
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method == 'POST' or self.request.method == 'PATCH':
            return RecipeAddSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True, methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk=None):

        if request.method == 'POST':
            return self.add_recipe(Favorite, request, pk)

        if request.method == 'DELETE':
            return self.delete_recipe(Favorite, request, pk)

        return None

    @action(
        detail=True, methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):

        if request.method == 'POST':
            return self.add_recipe(ShoppingCart, request, pk)

        if request.method == 'DELETE':
            return self.delete_recipe(ShoppingCart, request, pk)

        return None

    @action(
        detail=False,
        url_path='download_shopping_cart',
        methods=['GET'],
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        ingredients = IngredientsInRecipe.objects.filter(
            recipe__shopping_cart__user=request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).order_by(
            'ingredient__name'
        ).annotate(
            ingredient_total=Sum('amount')
        )
        products = []

        for item in ingredients:
            name = item['ingredient__name']
            measurement_unit = item['ingredient__measurement_unit']
            amount = item['ingredient_total']
            products.append(f'{name} - {amount} {measurement_unit}')

        content = '\n'.join(products)
        content_type = 'text/plain, charset=utf8'
        response = HttpResponse(content, content_type=content_type)
        response['Content-Disposition'] = (
            'attachment; filename = "shopping_list.txt"'
        )

        return response

    def add_recipe(self, model, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = self.request.user

        if recipe.recipes.filter(user=user).exists():
            raise ValidationError('Такой рецепт уже добавлен')

        model.objects.create(
            recipe=recipe,
            user=user
        )
        serializer = RecipeSmallSerializer(recipe)

        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    def delete_recipe(self, model, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = self.request.user
        obj = get_object_or_404(model, recipe=recipe, user=user)
        obj.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )
