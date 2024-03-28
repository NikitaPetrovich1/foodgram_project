from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from .models import User
from .constants import FIRST_NAME_LENGTH, LAST_NAME_LENGTH
from subscriptions.models import Subscription


class CustomUserCreateSerializer(UserCreateSerializer):
    first_name = serializers.CharField(
        max_length=FIRST_NAME_LENGTH,
        required=True
    )
    last_name = serializers.CharField(
        max_length=LAST_NAME_LENGTH,
        required=True
    )
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'password',
        )

    def validate(self, data):
        email = data['email']
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                'Пользователь с такой почтой уже зарегестрирован'
            )
        return data


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Subscription.objects.filter(
            user=request.user, author=obj
        ).exists()
