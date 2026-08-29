from django.urls import path

from .views import (
    FarmDetailAPIView,
    FarmListCreateAPIView,
    MilkRecordListCreateAPIView,
    CowActivityListCreateAPIView,
    CowListCreateAPIView,
    FarmerProfileListCreateAPIView,
    farm_summary,
    milk_summary,
)

urlpatterns = [
    # Create and list farms assigned to agents.
    path("farms/", FarmListCreateAPIView.as_view(), name="farm-list"),

    # Retrieve, update, or delete a specific farm.
    path("farms/<int:pk>/", FarmDetailAPIView.as_view(), name="farm-detail"),

    # Total milk output for one farm across an optional date range.
    path("farms/<int:pk>/summary/", farm_summary, name="farm-summary"),

    # Manage farmer-to-farm assignments.
    path("farmers/", FarmerProfileListCreateAPIView.as_view(), name="farmer-list"),

    # Create and list cows for the authenticated user scope.
    path("cows/", CowListCreateAPIView.as_view(), name="cow-list"),

    # Record health, birth, vaccination, and general animal activities.
    path("activities/", CowActivityListCreateAPIView.as_view(), name="activity-list"),

    # Record daily milk production against each cow.
    path("milk/", MilkRecordListCreateAPIView.as_view(), name="milk-list"),

    # Total milk summary across the user's authorized scope.
    path("milk/summary/", milk_summary, name="milk-summary"),
]
