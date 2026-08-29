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
    path("farms/", FarmListCreateAPIView.as_view(), name="farm-list"),
    path("farms/<int:pk>/", FarmDetailAPIView.as_view(), name="farm-detail"),
    path("farms/<int:pk>/summary/", farm_summary, name="farm-summary"),
    path("farmers/", FarmerProfileListCreateAPIView.as_view(), name="farmer-list"),
    path("cows/", CowListCreateAPIView.as_view(), name="cow-list"),
    path("activities/", CowActivityListCreateAPIView.as_view(), name="activity-list"),
    path("milk/", MilkRecordListCreateAPIView.as_view(), name="milk-list"),
    path("milk/summary/", milk_summary, name="milk-summary"),
]
