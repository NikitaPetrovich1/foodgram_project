from django.urls import path, include
from rest_framework import routers

from .views import TagsViewSet, IngredientViewSet, RecipeViewSet
from subscriptions.views import SubscribeView, SubscriptionViewSet

router = routers.DefaultRouter()

router.register('tags', TagsViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('users/subscriptions/', SubscriptionViewSet.as_view()),
    path('users/<int:pk>/subscribe/', SubscribeView.as_view()),
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
