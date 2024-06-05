from django.shortcuts import get_object_or_404
from rest_framework import status, views
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from subscriptions_app.models import Subscription
from subscriptions_app.serializers import (SubscribeSerializer,
                                           SubscriptionSerializer
                                           )
from users_app.models import User


class SubscriptionViewSet(ListAPIView):
    """
    Вьюсет предоставления данных подписок.
    """
    serializer_class = SubscriptionSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        return user.follower.all()


class SubscribeView(views.APIView):
    """
    Вьюсет добавления или удаления подписки.
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request, pk):
        author = get_object_or_404(User, pk=pk)
        data = {'author': author.id, 'user': self.request.user.id}
        serializer = SubscribeSerializer(
            data=data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        get_object_or_404(Subscription,
                          user=self.request.user,
                          author__id=pk).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
