from djoser.serializers import (UserCreateSerializer,
                                UserSerializer,
                                ValidationError)
from rest_framework.serializers import (CharField,
                                        EmailField,
                                        RegexField,
                                        SerializerMethodField)

from subscriptions_app.models import Subscription
from users_app.constants import (EMAIL_MAX_LENGTH,
                                 FIRST_NAME_LENGTH,
                                 LAST_NAME_LENGTH,
                                 PASSWORD_MAX_LENGTH,
                                 USERNAME_MAX_LENGTH)
from users_app.models import User


class UserCreateSerializer(UserCreateSerializer):
    """
    Кастомный сериализатор создания нового пользователя.
    Проверяется уникальность логина или почты, а также зарезервированного
    имени 'me'. Также проверяется соответствие длине имени, фамилии и паролю.
    """
    username = RegexField(
        regex=r'^[\w.@+-]+$',
        max_length=USERNAME_MAX_LENGTH,
        required=True,
    )

    email = EmailField(
        max_length=EMAIL_MAX_LENGTH,
        required=True,
    )
    password = CharField(
        max_length=PASSWORD_MAX_LENGTH,
        required=True,
        write_only=True,
    )
    first_name = CharField(
        max_length=FIRST_NAME_LENGTH,
        required=True,
    )
    last_name = CharField(
        max_length=LAST_NAME_LENGTH,
        required=True,
    )

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name', 'password'
        )

    def validate_username(self, value):
        """
        Валидация имени пользователя.
        Использовать имя 'me' в качестве username запрещено.
        """
        if value == 'me':
            raise ValidationError({
                'username': 'Имя пользователя "me" запрещено.'
            }
            )
        return value

    def validate(self, attrs):
        """
        Валидация имени пользователя и email.
        Проверяем, что пользователь с таким именем или email не существует.
        """
        username = attrs.get('username')
        email = attrs.get('email')

        if User.objects.filter(username=username).exists():
            raise ValidationError({
                'username': 'Пользователь с таким именем уже зарегистрирован'
            }
            )
        elif User.objects.filter(email=email).exists():
            raise ValidationError({
                'email': 'Пользователь с такой почтой уже зарегистрирован'
            }
            )

        return attrs


class UserSerializer(UserSerializer):
    """
    Djoser-сериализатор пользователя.
    """
    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')

        return not request or (
            not request.user.is_anonymous
            and Subscription.objects.filter(
                user=request.user,
                author=obj).exists()
        )
