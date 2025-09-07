import json

from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import ContentType, Permission, Group
from django.conf import settings

from jwt_authentication.utils import JWTUtils
from .seeders import PermissionSeeder
from .models import Service

User = get_user_model()

class ServicesApiTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.seed_data = PermissionSeeder.seed_all()
        cls.admin_group, cls.doctor_group, cls.patient_group = cls.seed_data["groups"]

    def setUp(self):
        self.client = Client()

    def test_create_service_success(self):
        doctor_group = ServicesApiTests.doctor_group
        doctor = User.objects.create_user(username='doctor1')
        doctor.groups.add(doctor_group)

        data = {"name": "Service 1", "address": "New Jersey", "doctor_id": doctor.id}
        headers = { "Authorization": f"Bearer {JWTUtils.generate_tokens(doctor)}" }
        response = self.client.post(
                reverse("create_service"), json.dumps(data),
                content_type="application/json", headers=headers
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["service"], {
            "id": 1, "name": "Service 1", "address": "New Jersey",
            "doctor": {"id": doctor.id, "username": doctor.username}
        })
        self.assertEqual(response.json()["status"], "created")
        service = Service.objects.get(id=response.json()["service"]["id"])
        self.assertIsNotNone(service)
        self.assertEqual(service.name, "Service 1")
        self.assertEqual(service.address, "New Jersey")

    def test_create_service_unauthorized(self):
        patient_group = ServicesApiTests.patient_group
        patient = User.objects.create_user(username='patient1')
        patient.groups.add(patient_group)

        data = {"name": "Service 1", "address": "New Jersey", "doctor_id": 21371}
        headers = { "Authorization": f"Bearer {JWTUtils.generate_tokens(patient)}" }
        response = self.client.post(
                reverse("create_service"), json.dumps(data),
                content_type="application/json", headers=headers
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["error"], "Permission Denied")
        self.assertEqual(response.json()["status"], "forbidden")

    def test_create_doctor_not_found(self):
        admin_group = ServicesApiTests.admin_group
        admin = User.objects.create_user(username='admin1')
        admin.groups.add(admin_group)

        data = {"name": "Service 1", "address": "New Jersey", "doctor_id": 123213}
        headers = { "Authorization": f"Bearer {JWTUtils.generate_tokens(admin)}" }
        response = self.client.post(
                reverse("create_service"), json.dumps(data),
                content_type="application/json", headers=headers
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["error"], "Data Invalid")
        self.assertEqual(response.json()["message"], "Doctor not found")
        self.assertEqual(response.json()["status"], "not-found")

    def test_index_service_success(self):
        doctor_group = ServicesApiTests.doctor_group
        doctor = User.objects.create_user(username='doctor1')
        doctor.groups.add(doctor_group)
        patient_group = ServicesApiTests.patient_group
        patient = User.objects.create_user(username='patient1')
        patient.groups.add(patient_group)
        service1 = Service.objects.create(
                name="service1", address="New Jersey", doctor=doctor
        )
        service2 = Service.objects.create(
                name="service2", address="New Jersey", doctor=doctor
        )
        service3 = Service.objects.create(
                name="service3", address="New Jersey", doctor=doctor
        )

        headers = { "Authorization": f"Bearer {JWTUtils.generate_tokens(patient)}" }
        response = self.client.get(
                reverse("show_all_services"),
                content_type="application/json", headers=headers
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["services"], [
            {
                "id": service.id, "name": service.name, "address": service.address,
                "doctor": {"id": service.doctor.id, "username": service.doctor.username}
            } for service in [service1, service2, service3]
        ])
        self.assertEqual(response.json()["status"], "success")

    def test_show_service_success(self):
        doctor_group = ServicesApiTests.doctor_group
        doctor = User.objects.create_user(username='doctor1')
        doctor.groups.add(doctor_group)
        patient_group = ServicesApiTests.patient_group
        patient = User.objects.create_user(username='patient1')
        patient.groups.add(patient_group)
        service = Service.objects.create(
                name="service1", address="New Jersey", doctor=doctor
        )

        headers = { "Authorization": f"Bearer {JWTUtils.generate_tokens(patient)}" }
        response = self.client.get(
                reverse("show_service", kwargs={"service_id": service.id}),
                content_type="application/json", headers=headers
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["service"], {
            "id": service.id, "name": service.name, "address": service.address,
            "doctor": {"id": doctor.id, "username": doctor.username}
        })
        self.assertEqual(response.json()["status"], "success")

    def test_show_service_not_found(self):
        patient_group = ServicesApiTests.patient_group
        patient = User.objects.create_user(username='patient1')
        patient.groups.add(patient_group)

        headers = { "Authorization": f"Bearer {JWTUtils.generate_tokens(patient)}" }
        response = self.client.get(
                reverse("show_service", kwargs={"service_id": 123123}),
                content_type="application/json", headers=headers
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["error"], "Not Found")
        self.assertEqual(response.json()["status"], "not-found")

    def test_update_service_success(self):
        doctor_group = ServicesApiTests.doctor_group
        doctor = User.objects.create_user(username='doctor1')
        doctor.groups.add(doctor_group)
        service = Service.objects.create(
                name="service1", address="New Jersey", doctor=doctor
        )

        data = {"name": "Updated", "address": "Updated"}
        headers = { "Authorization": f"Bearer {JWTUtils.generate_tokens(doctor)}" }
        response = self.client.put(
                reverse("update_service", kwargs={"service_id": service.id}), json.dumps(data),
                content_type="application/json", headers=headers
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["service"], {
            "id": service.id, "name": "Updated", "address": "Updated",
            "doctor": {"id": doctor.id, "username": doctor.username}
        })
        self.assertEqual(response.json()["status"], "updated")

    def test_delete_service_success(self):
        doctor_group = ServicesApiTests.doctor_group
        doctor = User.objects.create_user(username='doctor1')
        doctor.groups.add(doctor_group)
        service = Service.objects.create(
                name="service1", address="New Jersey", doctor=doctor
        )
        service_id = service.id

        headers = { "Authorization": f"Bearer {JWTUtils.generate_tokens(doctor)}" }
        response = self.client.delete(
                reverse("delete_service", kwargs={"service_id": service.id}),
                content_type="application/json", headers=headers
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["service"], {
            "id": service.id, "name": service.name, "address": service.address
        })
        self.assertEqual(response.json()["status"], "deleted")
        self.assertFalse(Service.objects.filter(id=service_id).exists())
        self.assertTrue(User.objects.filter(id=doctor.id).exists())
