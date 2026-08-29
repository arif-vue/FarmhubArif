from decimal import Decimal

from django.db.models import Sum
from django.utils.dateparse import parse_date
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.response import Response

from authentications.models import User

from .models import Cow, CowActivity, Farm, FarmerProfile, MilkRecord
from .serializers import (
    CowActivitySerializer,
    CowSerializer,
    FarmSerializer,
    FarmerProfileSerializer,
    MilkRecordSerializer,
)


class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_super_admin)


class IsAgentOrSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and (request.user.is_super_admin or request.user.is_agent)
        )


def get_farm_queryset_for_user(user):
    if user.is_super_admin:
        return Farm.objects.all()
    if user.is_agent:
        return Farm.objects.filter(agent=user)
    if user.is_farmer:
        profile = FarmerProfile.objects.filter(user=user).select_related("farm").first()
        if profile:
            return Farm.objects.filter(id=profile.farm_id)
    return Farm.objects.none()


class FarmListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = FarmSerializer
    permission_classes = [IsAuthenticated, IsAgentOrSuperAdmin]

    def get_queryset(self):
        return get_farm_queryset_for_user(self.request.user)

    def perform_create(self, serializer):
        if self.request.user.is_agent and serializer.validated_data.get("agent") != self.request.user:
            raise PermissionError("Agents can only create farms assigned to themselves.")
        serializer.save()


class FarmDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = FarmSerializer
    permission_classes = [IsAuthenticated, IsAgentOrSuperAdmin]

    def get_queryset(self):
        return get_farm_queryset_for_user(self.request.user)


class FarmerProfileListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = FarmerProfileSerializer
    permission_classes = [IsAuthenticated, IsAgentOrSuperAdmin]

    def get_queryset(self):
        if self.request.user.is_super_admin:
            return FarmerProfile.objects.select_related("user", "farm").all()
        if self.request.user.is_agent:
            return FarmerProfile.objects.select_related("user", "farm").filter(farm__agent=self.request.user)
        return FarmerProfile.objects.none()

    def perform_create(self, serializer):
        farm = serializer.validated_data.get("farm")
        user = serializer.validated_data.get("user")
        if self.request.user.is_agent and farm.agent != self.request.user:
            raise PermissionError("You can only onboard farmers to your own farms.")
        if user.role != User.ROLE_FARMER:
            raise PermissionError("This profile is only valid for farmer users.")
        serializer.save()


class CowListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = CowSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_super_admin:
            return Cow.objects.select_related("farm", "owner").all()
        if user.is_agent:
            return Cow.objects.select_related("farm", "owner").filter(farm__agent=user)
        if user.is_farmer:
            return Cow.objects.select_related("farm", "owner").filter(owner=user)
        return Cow.objects.none()

    def perform_create(self, serializer):
        cow = serializer.save()
        if self.request.user.is_farmer and cow.owner != self.request.user:
            raise PermissionError("Farmers can only register cows they own.")


class CowActivityListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = CowActivitySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_super_admin:
            return CowActivity.objects.select_related("cow__farm", "created_by").all()
        if user.is_agent:
            return CowActivity.objects.select_related("cow__farm", "created_by").filter(cow__farm__agent=user)
        if user.is_farmer:
            return CowActivity.objects.select_related("cow__farm", "created_by").filter(cow__owner=user)
        return CowActivity.objects.none()

    def perform_create(self, serializer):
        cow = serializer.validated_data.get("cow")
        user = self.request.user
        if user.is_farmer and cow.owner != user:
            raise PermissionError("Farmers can only log activities for their own cows.")
        if user.is_agent and cow.farm.agent != user:
            raise PermissionError("Agents can only log activities for their assigned farm.")
        serializer.save(created_by=user)


class MilkRecordListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = MilkRecordSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_super_admin:
            return MilkRecord.objects.select_related("cow__farm", "created_by").all()
        if user.is_agent:
            return MilkRecord.objects.select_related("cow__farm", "created_by").filter(cow__farm__agent=user)
        if user.is_farmer:
            return MilkRecord.objects.select_related("cow__farm", "created_by").filter(cow__owner=user)
        return MilkRecord.objects.none()

    def perform_create(self, serializer):
        cow = serializer.validated_data.get("cow")
        user = self.request.user
        if user.is_farmer and cow.owner != user:
            raise PermissionError("Farmers can only record milk for their own cows.")
        if user.is_agent and cow.farm.agent != user:
            raise PermissionError("Agents can only record milk for their assigned farms.")
        serializer.save(created_by=user)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def milk_summary(request):
    queryset = MilkRecord.objects.all()
    if request.user.is_agent:
        queryset = queryset.filter(cow__farm__agent=request.user)
    elif request.user.is_farmer:
        queryset = queryset.filter(cow__owner=request.user)

    total = queryset.aggregate(total=Sum("quantity_liters"))["total"] or Decimal("0")
    return Response({"total_quantity_liters": float(total)})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def farm_summary(request, pk):
    farm = get_farm_queryset_for_user(request.user).filter(pk=pk).first()
    if farm is None:
        return Response({"detail": "Farm not found."}, status=status.HTTP_404_NOT_FOUND)

    start_date = request.query_params.get("start_date")
    end_date = request.query_params.get("end_date")
    queryset = MilkRecord.objects.filter(cow__farm=farm)

    if start_date:
        start = parse_date(start_date)
        if start:
            queryset = queryset.filter(recorded_on__gte=start)

    if end_date:
        end = parse_date(end_date)
        if end:
            queryset = queryset.filter(recorded_on__lte=end)

    total = queryset.aggregate(total=Sum("quantity_liters"))["total"] or Decimal("0")
    return Response({"farm_id": farm.id, "total_quantity_liters": float(total)})
