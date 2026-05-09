from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .permissions import IsAdmin, IsAdminOrSelf
from .serializers import (
    UserCreateSerializer,
    UserListSerializer,
    UserDetailSerializer,
    ChangePasswordSerializer,
)

User = get_user_model()



class LoginView(TokenObtainPairView):
    """
    POST /api/auth/login/
    Body: { "email": "...", "password": "..." }
    Returns: access token, refresh token, and basic user info.
    """
    permission_classes = [AllowAny]



class LogoutView(APIView):
    """
    POST /api/auth/logout/
    Body: { "refresh": "<refresh_token>" }
    Blacklists the refresh token so it cannot be reused.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            token = RefreshToken(request.data.get('refresh'))
            token.blacklist()
            return Response({'detail': 'Logged out successfully.'}, status=status.HTTP_200_OK)
        except Exception:
            return Response({'detail': 'Invalid or expired token.'}, status=status.HTTP_400_BAD_REQUEST)


class MeView(APIView):
    """
    GET  /api/auth/me/   — return the logged-in user's profile.
    PUT  /api/auth/me/   — update own full_name (email/role are locked).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserDetailSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        serializer = UserDetailSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    """
    POST /api/auth/change-password/
    Body: { "old_password": "...", "new_password": "..." }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            request.user.set_password(serializer.validated_data['new_password'])
            request.user.save()
            return Response({'detail': 'Password updated successfully.'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class UserListCreateView(ListCreateAPIView):
    """
    GET  /api/auth/users/   — list all users (admin only).
    POST /api/auth/users/   — create a new user account (admin only).
    """
    permission_classes = [IsAdmin]
    queryset = User.objects.all().select_related('created_by')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserCreateSerializer
        return UserListSerializer

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['request'] = self.request
        return ctx


class UserDetailView(RetrieveUpdateDestroyAPIView):
    """
    GET    /api/auth/users/<id>/  — view a user (admin only).
    PATCH  /api/auth/users/<id>/  — edit a user (admin only).
    DELETE /api/auth/users/<id>/  — deactivate a user (soft-delete, admin only).
    """
    permission_classes = [IsAdmin]
    queryset = User.objects.all()
    serializer_class = UserDetailSerializer

    def destroy(self, request, *args, **kwargs):
        """Soft-delete: deactivate instead of removing from DB (preserves audit trail)."""
        user = self.get_object()
        if user == request.user:
            return Response(
                {'detail': 'You cannot deactivate your own account.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.is_active = False
        user.save()
        return Response({'detail': f'User {user.email} has been deactivated.'}, status=status.HTTP_200_OK)
