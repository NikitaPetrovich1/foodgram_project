from django.urls import include, path
from rest_framework.routers import DefaultRouter

from recipes_app.views import (IngredientViewSet,
                               RecipeViewSet,
                               TagsViewSet)
from subscriptions_app.views import SubscribeView, SubscriptionViewSet

router_v1 = DefaultRouter()

router_v1.register('tags', TagsViewSet, basename='tags')
router_v1.register('ingredients', IngredientViewSet, basename='ingredients')
router_v1.register(r'recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('users/subscriptions/', SubscriptionViewSet.as_view()),
    path('users/<int:pk>/subscribe/', SubscribeView.as_view()),
    path('', include(router_v1.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
