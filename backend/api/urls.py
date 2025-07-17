from django.urls import path, include
from rest_framework import routers
from .views import (
    health, RegisterView, LoginView, logout, oauth_stub, user_dashboard, billing_stub,
    CodeNestViewSet, VersionViewSet, RatingViewSet, FeedbackViewSet, FavoriteViewSet, IntegrationViewSet, SubscriptionViewSet,
)

router = routers.DefaultRouter()
router.register(r'nests', CodeNestViewSet, basename='nest')
router.register(r'versions', VersionViewSet, basename='version')
router.register(r'ratings', RatingViewSet, basename='rating')
router.register(r'feedback', FeedbackViewSet, basename='feedback')
router.register(r'favorites', FavoriteViewSet, basename='favorite')
router.register(r'integrations', IntegrationViewSet, basename='integration')
router.register(r'subscriptions', SubscriptionViewSet, basename='subscription')

urlpatterns = [
    path('health/', health, name='Health'),
    path('auth/register/', RegisterView.as_view(), name='Register'),
    path('auth/login/', LoginView.as_view(), name='Login'),
    path('auth/oauth/', oauth_stub, name='OAuthStub'),
    path('auth/logout/', logout, name='Logout'),
    path('dashboard/', user_dashboard, name='UserDashboard'),
    path('billing/', billing_stub, name='BillingStub'),
    path('', include(router.urls))
]
