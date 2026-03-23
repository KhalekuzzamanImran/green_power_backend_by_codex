from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.accounts.models import User
from apps.accounts.serializers import MeSerializer, UserCreateSerializer, UserSerializer
from apps.audit_logs.models import AuditAction, AuditLog
from apps.core.permissions import CanManageUsers


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by("username")
    permission_classes = [CanManageUsers]

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        return UserSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        role = self.request.query_params.get("role")
        if role:
            queryset = queryset.filter(role=role)
        return queryset

    def perform_create(self, serializer):
        user = serializer.save()
        AuditLog.objects.create(
            actor=self.request.user,
            action=AuditAction.CREATE,
            target_type="User",
            target_id=str(user.id),
            description=f"Created user {user.username}",
        )

    def perform_update(self, serializer):
        user = serializer.save()
        AuditLog.objects.create(
            actor=self.request.user,
            action=AuditAction.UPDATE,
            target_type="User",
            target_id=str(user.id),
            description=f"Updated user {user.username}",
        )

    def perform_destroy(self, instance):
        AuditLog.objects.create(
            actor=self.request.user,
            action=AuditAction.DELETE,
            target_type="User",
            target_id=str(instance.id),
            description=f"Deleted user {instance.username}",
        )
        instance.delete()


@extend_schema(
    tags=["Auth"],
    summary="Get current user bootstrap payload",
    responses={200: MeSerializer},
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me_view(request):
    serializer = MeSerializer(request.user)
    return Response(serializer.data)


class DocumentedTokenObtainPairView(TokenObtainPairView):
    @extend_schema(
        tags=["Auth"],
        summary="Login and obtain JWT tokens",
        responses={
            200: OpenApiResponse(
                description="JWT token pair",
                examples=[
                    OpenApiExample(
                        "Token pair",
                        value={
                            "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.refresh",
                            "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.access",
                        },
                    )
                ],
            )
        },
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class DocumentedTokenRefreshView(TokenRefreshView):
    @extend_schema(tags=["Auth"], summary="Refresh JWT access token")
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


auth_token_obtain_pair = DocumentedTokenObtainPairView.as_view()
auth_token_refresh = DocumentedTokenRefreshView.as_view()
