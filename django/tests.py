from django.test import TestCase, Client
from django.urls import reverse

class APITest(TestCase):

    def setUp(self):
        self.client = Client()

    def test_ping_endpoint_returns_ok_status(self):
        """
        Tests that the /ping/ endpoint returns a 200 OK status and the correct JSON response.
        """
        response = self.client.get(reverse('ping'))

        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.json(), {"ping": "pong"})
