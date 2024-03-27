from django.shortcuts import get_object_or_404
from rest_framework import status, views
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.validators import ValidationError

from users.models import User
from subscriptions.serializers import (
    SubscribeSerializer, SubscriptionSerializer
)
from subscriptions.models import Subscription


class SubscriptionViewSet(ListAPIView):
    serializer_class = SubscriptionSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        return user.follower.all()


class SubscribeView(views.APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, pk):
        user = self.request.user
        author = get_object_or_404(User, pk=pk)
        data = {'author': author.id, 'user': user.id}
        serializer = SubscribeSerializer(
            data=data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        user = self.request.user
        author = get_object_or_404(User, pk=pk)

        subscription, _ = Subscription.objects.filter(
            user=user, author=author
        ).delete()
        if not subscription:
            raise ValidationError(f'{user} не подписан {author}')

        return Response(status=status.HTTP_204_NO_CONTENT)
