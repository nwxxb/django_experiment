import json

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.conf import settings

from .utils import JWTUtils

User = get_user_model()

class JWTAuthTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_login_success(self):
        """
        Test that a valid login returns a JWT.
        """
        existing_user = User.objects.create_user(
                username='test1', password='password'
        )

        data = {"username": "test1", "password": "password"}
        response = self.client.post(reverse("login"), json.dumps(data), content_type="application/json")

        decoded_token_payload = JWTUtils.validate_token(response.json()["access_token"])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(int(decoded_token_payload["sub"]), existing_user.id)

    def test_login_non_existing_user(self):
        """
        Test that a valid login returns a JWT.
        """
        data = {"username": "test1", "password": "123"}
        response = self.client.post(reverse("login"), json.dumps(data), content_type="application/json")

        self.assertEqual(response.status_code, 401)
        self.assertNotIn("access_token", response.json())
        self.assertEqual(response.json()["error"], "Credential Invalid")

    def test_login_invalid_password(self):
        """
        Test that a valid login returns a JWT.
        """
        existing_user = User.objects.create_user(
                username='test1', password='password'
        )

        data = {"username": "test1", "password": "123"}
        response = self.client.post(reverse("login"), json.dumps(data), content_type="application/json")

        self.assertEqual(response.status_code, 401)
        self.assertNotIn("access_token", response.json())
        self.assertEqual(response.json()["error"], "Credential Invalid")
