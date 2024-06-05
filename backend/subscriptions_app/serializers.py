from rest_framework import serializers

from recipes_app.models import Recipe
from recipes_app.serializers import RecipeSerializer
from subscriptions_app.models import Subscription


class SubscribeSerializer(serializers.ModelSerializer):
    """
    Сериализатор подписок.
    """
    class Meta:
        model = Subscription
        fields = ('user', 'author')

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        serializer = SubscriptionSerializer(
            instance,
            context=context
        )
        return serializer.data

    def validate(self, data):
        user = data.get('user')
        author = data.get('author')
        if user == author:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя.'
            )
        if Subscription.objects.filter(user=user, author=author).exists():
            raise serializers.ValidationError(
                'Вы уже подписаны на этого автора.'
            )
        return data


class SubscriptionSerializer(serializers.ModelSerializer):
    """
    Сериализатор предоставления данных подписок.
    """
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed'
    )
    recipes = serializers.SerializerMethodField(method_name='get_recipes')
    recipes_count = serializers.SerializerMethodField(
        method_name='get_recipes_count'
    )

    class Meta:
        model = Subscription
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

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return Subscription.objects.filter(
            author=obj.author, user=request.user
        ).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        if request.GET.get('recipes_limit'):
            recipes_limit = int(request.GET['recipes_limit'])
            queryset = Recipe.objects.filter(
                author=obj.author)[:recipes_limit]
        else:
            queryset = Recipe.objects.filter(
                author=obj.author)
        serializer = RecipeSerializer(
            queryset, read_only=True, many=True
        )
        return serializer.data

    def get_recipes_count(self, obj):
        return obj.author.recipes.count()
