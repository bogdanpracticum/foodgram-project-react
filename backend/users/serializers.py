from djoser.serializers import UserSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

import api
from users.models import CustomUser, Subscribe

MAX_RECIPES = 3


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed'
    )

    class Meta:
        model = CustomUser
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        request = self.context['request']
        if request.user.is_anonymous:
            return False
        return request.user.following.filter(author=obj).exists()


class SubscriptionSerializer(serializers.ModelSerializer):

    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed'
    )
    recipes = serializers.SerializerMethodField(
        method_name='get_recipes'
    )
    recipes_count = serializers.SerializerMethodField(
        method_name='get_recipes_count'
    )

    class Meta:
        model = CustomUser
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_is_subscribed(self, user):
        current_user = self.context.get('current_user')
        return user.follower.filter(author=current_user).exists()

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):

        recipes = obj.recipes.all()[:MAX_RECIPES]
        request = self.context.get('request')

        return api.serializers.RecipeSmallSerializer(
            recipes,
            many=True,
            context={'request': request}
        ).data


class FollowSerializer(serializers.ModelSerializer):
    queryset = CustomUser.objects.all()

    class Meta:
        model = Subscribe
        fields = ('user', 'author')
        validators = [
            UniqueTogetherValidator(
                queryset=Subscribe.objects.all(),
                fields=('user', 'author'),
                message='Такая подписка уже существует'
            )
        ]

    def to_representation(self, instance):
        request = self.context.get('request')
        return SubscriptionSerializer(
            instance.author,
            context={'request': request}
        ).data
