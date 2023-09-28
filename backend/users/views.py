from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.pagination import CustomPagination
from users.models import CustomUser, Subscribe
from users.serializers import FollowSerializer, SubscriptionSerializer


class SubscribeView(APIView):
    pagination_class = CustomPagination
    permission_classes = (IsAuthenticated,)

    def post(self, request, pk):
        author = get_object_or_404(CustomUser, pk=pk)
        user = self.request.user
        data = {'author': author.id, 'user': user.id}
        serializer = FollowSerializer(
            data=data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            data=serializer.data,
            status=status.HTTP_201_CREATED
        )

    def delete(self, request, pk):
        author = get_object_or_404(CustomUser, pk=pk)
        user = self.request.user
        subscription = get_object_or_404(
            Subscribe,
            user=user,
            author=author
        )
        subscription.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )


class SubscriptionViewSet(ListAPIView):
    serializer_class = SubscriptionSerializer
    pagination_class = CustomPagination
    permission_classes = (IsAuthenticated,)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context

    def get_queryset(self):
        return CustomUser.objects.filter(following__user=self.request.user)
