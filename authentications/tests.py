from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class AuthenticationAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="farmer1",
            email="farmer1@example.com",
            password="StrongPass123!",
            role="farmer",
        )

    def test_register_creates_new_user(self):
        payload = {
            "username": "new_farmer",
            "email": "new_farmer@example.com",
            "password": "StrongPass123!",
            "role": "farmer",
        }

        response = self.client.post(reverse("register"), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["username"], "new_farmer")
        self.assertEqual(response.data["email"], "new_farmer@example.com")
        self.assertNotIn("password", response.data)
        self.assertTrue(User.objects.filter(username="new_farmer").exists())

    def test_login_returns_tokens(self):
        payload = {"username": "farmer1", "password": "StrongPass123!"}

        response = self.client.post(reverse("login"), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_me_returns_authenticated_user(self):
        login_response = self.client.post(
            reverse("login"),
            {"username": "farmer1", "password": "StrongPass123!"},
            format="json",
        )
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {login_response.data['access']}"
        )

        response = self.client.get(reverse("me"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "farmer1")
        self.assertEqual(response.data["email"], "farmer1@example.com")
        self.assertNotIn("password", response.data)

    def test_create_superuser_sets_super_admin_role(self):
        user = User.objects.create_superuser(
            username="adminuser",
            email="admin@example.com",
            password="StrongPass123!",
        )

        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertEqual(user.role, User.ROLE_SUPER_ADMIN)
        self.assertTrue(user.is_super_admin)

    def test_is_super_admin_works_for_existing_superuser_with_stale_role(self):
        user = User.objects.create_user(
            username="legacyadmin",
            email="legacyadmin@example.com",
            password="StrongPass123!",
            role="farmer",
            is_superuser=True,
            is_staff=True,
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_super_admin)
