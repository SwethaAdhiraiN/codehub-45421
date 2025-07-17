from rest_framework import viewsets, permissions, status, generics, filters
from rest_framework.response import Response
from rest_framework.decorators import api_view, action, permission_classes
from rest_framework.views import APIView
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth import get_user_model
from .models import (
    User, CodeNest, Version, Rating, Feedback, Favorite, Integration, Subscription
)
from .serializers import (
    UserSerializer, UserRegisterSerializer, LoginSerializer,
    CodeNestSerializer, VersionSerializer, RatingSerializer, FeedbackSerializer,
    FavoriteSerializer, IntegrationSerializer, SubscriptionSerializer
)
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, AllowAny

UserModel = get_user_model()


# PUBLIC_INTERFACE
@api_view(['GET'])
def health(request):
    return Response({"message": "Server is up!"})

###### AUTH ######

# PUBLIC_INTERFACE
class RegisterView(generics.CreateAPIView):
    """User email/password registration"""
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = UserRegisterSerializer

# PUBLIC_INTERFACE
class LoginView(APIView):
    """User login, returns JWT."""
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            refresh = RefreshToken.for_user(user)
            auth_login(request, user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserSerializer(user).data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# PUBLIC_INTERFACE
@api_view(['POST'])
@permission_classes([AllowAny])
def oauth_stub(request):
    """
    OAuth endpoint stub. Should be replaced with proper provider logic (Google/GitHub).
    """
    # TODO: Real OAuth logic with social-auth
    user, created = User.objects.get_or_create(username="oauth_user", defaults={"email": "oauth@example.com"})
    refresh = RefreshToken.for_user(user)
    auth_login(request, user)
    return Response({
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'user': UserSerializer(user).data
    })

# PUBLIC_INTERFACE
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """
    Logout current user.
    """
    auth_logout(request)
    return Response({"message": "Logged out"})


#### DASHBOARD ####

# PUBLIC_INTERFACE
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_dashboard(request):
    """
    User dashboard: contributions (code nests), favorites, feedbacks, subscriptions.
    """
    nests = CodeNest.objects.filter(author=request.user)
    favorites = Favorite.objects.filter(user=request.user)
    feedbacks = Feedback.objects.filter(user=request.user)
    subscriptions = Subscription.objects.filter(user=request.user)
    return Response({
        "contributions": CodeNestSerializer(nests, many=True).data,
        "favorites": FavoriteSerializer(favorites, many=True).data,
        "feedbacks": FeedbackSerializer(feedbacks, many=True).data,
        "subscriptions": SubscriptionSerializer(subscriptions, many=True).data,
    })


##### MODELS/APIS #####

# Custom permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """Allow updates only if user is owner or admin, else read-only."""
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        # Many of our models have an 'author', 'user' or 'uploader'
        if hasattr(obj, 'author') and obj.author == request.user:
            return True
        if hasattr(obj, 'user') and obj.user == request.user:
            return True
        if hasattr(obj, 'uploader') and obj.uploader == request.user:
            return True
        return request.user.is_staff


# PUBLIC_INTERFACE
class CodeNestViewSet(viewsets.ModelViewSet):
    queryset = CodeNest.objects.all().select_related('author', 'current_version').prefetch_related('ratings')
    serializer_class = CodeNestSerializer
    permission_classes = [IsOwnerOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'language', 'framework', 'category', 'tags']
    ordering_fields = ["created_at", "updated_at"]

    def perform_create(self, serializer):
        obj = serializer.save(author=self.request.user)
        # Optionally auto-set current_version to initial version (if provided)
        return obj

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def bookmark(self, request, pk=None):
        nest = self.get_object()
        Favorite.objects.get_or_create(user=request.user, nest=nest)
        return Response({"status": "bookmarked"})

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def rate(self, request, pk=None):
        nest = self.get_object()
        rating, created = Rating.objects.update_or_create(
            user=request.user, nest=nest,
            defaults={"score": request.data.get("score"), "review": request.data.get("review", "")}
        )
        return Response(RatingSerializer(rating).data)


# PUBLIC_INTERFACE
class VersionViewSet(viewsets.ModelViewSet):
    queryset = Version.objects.all().select_related('nest', 'uploader')
    serializer_class = VersionSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        return serializer.save(uploader=self.request.user)


# PUBLIC_INTERFACE
class RatingViewSet(viewsets.ModelViewSet):
    queryset = Rating.objects.all().select_related('nest', 'user')
    serializer_class = RatingSerializer
    permission_classes = [IsOwnerOrReadOnly]


# PUBLIC_INTERFACE
class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.all().select_related('user', 'nest')
    serializer_class = FeedbackSerializer
    permission_classes = [IsAuthenticated]


# PUBLIC_INTERFACE
class FavoriteViewSet(viewsets.ModelViewSet):
    queryset = Favorite.objects.all().select_related('user', 'nest')
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]

# PUBLIC_INTERFACE
class IntegrationViewSet(viewsets.ModelViewSet):
    queryset = Integration.objects.all().select_related('nest', 'version', 'added_by')
    serializer_class = IntegrationSerializer
    permission_classes = [IsOwnerOrReadOnly]


# PUBLIC_INTERFACE
class SubscriptionViewSet(viewsets.ModelViewSet):
    queryset = Subscription.objects.all().select_related('user')
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]


# PUBLIC_INTERFACE
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def billing_stub(request):
    """
    Simulated billing/subscription endpoint.
    """
    return Response({"message": "Billing features coming soon!"})
