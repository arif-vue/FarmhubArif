from datetime import date

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from api.models import Cow, CowActivity, Farm, MilkRecord

User = get_user_model()


class FarmDomainAPITestCase(APITestCase):
    def setUp(self):
        self.super_admin = User.objects.create_user(
            username="superadmin",
            email="superadmin@example.com",
            password="StrongPass123!",
            role="super_admin",
        )
        self.agent = User.objects.create_user(
            username="agent1",
            email="agent1@example.com",
            password="StrongPass123!",
            role="agent",
        )
        self.farmer = User.objects.create_user(
            username="farmer1",
            email="farmer1@example.com",
            password="StrongPass123!",
            role="farmer",
        )

        self.farm = Farm.objects.create(
            name="Green Valley",
            location="Riverside",
            agent=self.agent,
        )

    def test_super_admin_can_create_farm(self):
        self.client.force_authenticate(user=self.super_admin)

        payload = {"name": "North Farm", "location": "Hilltop", "agent": self.agent.id}
        response = self.client.post(reverse("farm-list"), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Farm.objects.filter(name="North Farm").count(), 1)

    def test_agent_can_only_access_assigned_farm(self):
        self.client.force_authenticate(user=self.agent)

        response = self.client.get(reverse("farm-detail", args=[self.farm.id]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Green Valley")

    def test_farmer_can_record_milk_and_total_is_calculated(self):
        self.client.force_authenticate(user=self.farmer)

        cow = Cow.objects.create(
            farm=self.farm,
            owner=self.farmer,
            tag_number="COW-001",
            breed="Holstein",
            name="Buttercup",
        )

        MilkRecord.objects.create(cow=cow, recorded_on=date.today(), quantity_liters=15.5)
        MilkRecord.objects.create(cow=cow, recorded_on=date.today(), quantity_liters=10.0)

        response = self.client.get(reverse("milk-summary"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_quantity_liters"], 25.5)

    def test_farm_summary_uses_date_range(self):
        self.client.force_authenticate(user=self.super_admin)

        cow = Cow.objects.create(
            farm=self.farm,
            owner=self.farmer,
            tag_number="COW-010",
            breed="Jersey",
            name="Sunbeam",
        )

        MilkRecord.objects.create(
            cow=cow,
            recorded_on=date(2026, 8, 1),
            quantity_liters=12.0,
        )
        MilkRecord.objects.create(
            cow=cow,
            recorded_on=date(2026, 8, 10),
            quantity_liters=8.0,
        )

        response = self.client.get(
            reverse("farm-summary", args=[self.farm.id]),
            {"start_date": "2026-08-01", "end_date": "2026-08-09"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_quantity_liters"], 12.0)
