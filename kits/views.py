from rest_framework import status
from rest_framework.generics import (
    ListCreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView
)
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsAdmin
from .models import Kit, Report
from .serializers import (
    KitListSerializer,
    KitDetailSerializer,
    KitCreateUpdateSerializer,
    ReportCreateSerializer,
    ReportAdminSerializer,
)
from .permissions import IsKitOwnerOrAdmin




class KitListCreateView(ListCreateAPIView):
    """
    GET  /api/kits/   — List kits visible to the current user.
                        Admin sees all. Regular users see only their own.
    POST /api/kits/   — Create a new kit (authenticated users).
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Kit.objects.select_related('created_by')
        if not user.is_admin:
            qs = qs.filter(created_by=user)
        return qs

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return KitCreateUpdateSerializer
        return KitListSerializer

    def create(self, request, *args, **kwargs):
        """
        Support upsert: if kit_id already exists and belongs to this user
        (or user is admin), update it instead of failing.
        """
        kit_id = request.data.get('kit_id')
        if kit_id:
            existing = Kit.objects.filter(kit_id=kit_id).first()
            if existing:
                # Check ownership
                if not request.user.is_admin and existing.created_by != request.user:
                    return Response(
                        {'detail': 'You do not own this kit.'},
                        status=status.HTTP_403_FORBIDDEN
                    )
                serializer = KitCreateUpdateSerializer(
                    existing, data=request.data, partial=True,
                    context={'request': request}
                )
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(KitDetailSerializer(existing).data, status=status.HTTP_200_OK)

        # New kit
        serializer = KitCreateUpdateSerializer(
            data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        kit = serializer.save()
        return Response(KitDetailSerializer(kit).data, status=status.HTTP_201_CREATED)


class KitDetailView(RetrieveUpdateDestroyAPIView):
    """
    GET    /api/kits/<kit_id>/   — View a kit (owner or admin).
    PATCH  /api/kits/<kit_id>/   — Edit a kit (owner or admin).
    DELETE /api/kits/<kit_id>/   — Delete a kit (owner or admin).
    """
    permission_classes = [IsAuthenticated, IsKitOwnerOrAdmin]
    queryset           = Kit.objects.all()
    lookup_field       = 'kit_id'

    def get_serializer_class(self):
        if self.request.method in ('PATCH', 'PUT'):
            return KitCreateUpdateSerializer
        return KitDetailSerializer


class KitPublicView(APIView):
    """
    GET /api/kits/view/<kit_id>/
    Public endpoint — no authentication required.
    Used by viewer.html when it scans a QR code.
    Returns only active kits.
    """
    permission_classes = [AllowAny]

    def get(self, request, kit_id):
        try:
            kit = Kit.objects.get(kit_id=kit_id, status=Kit.Status.ACTIVE)
        except Kit.DoesNotExist:
            return Response(
                {'detail': f'Kit "{kit_id}" not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        return Response(KitDetailSerializer(kit).data)




class ReportCreateView(APIView):
    """
    POST /api/kits/reports/
    No authentication required — viewers submit reports after scanning a QR.
    Matches the payload from viewer.html:
      { kit_id, reporter_nom, reporter_prenom, reporter_service, severity, message }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ReportCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {'detail': 'Report submitted successfully. An admin will review it shortly.'},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReportAdminListView(ListAPIView):
    """
    GET /api/kits/reports/admin/
    Admin only — list all reports, newest first.
    """
    permission_classes = [IsAdmin]
    serializer_class   = ReportAdminSerializer
    queryset           = Report.objects.select_related('kit').order_by('-created_at')


class ReportAdminDetailView(RetrieveUpdateDestroyAPIView):
    """
    GET/PATCH /api/kits/reports/admin/<id>/
    Admin only — view or update a report (e.g. mark as reviewed/resolved).
    """
    permission_classes = [IsAdmin]
    serializer_class   = ReportAdminSerializer
    queryset           = Report.objects.all()
