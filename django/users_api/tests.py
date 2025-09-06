import json

from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import ContentType, Permission, Group
from django.conf import settings

from jwt_authentication.utils import JWTUtils

User = get_user_model()

class UsersApiTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.visible_groups_filter_settings = ['PATIENT', 'DOCTOR', 'KAPAL LAUT']

    def test_signup_success(self):
        fake_content_type, _ = ContentType.objects.get_or_create(
            app_label='myapp',
            model='fakemodel',
        )

        fake_permission, _ = Permission.objects.get_or_create(
            codename='can_do_something_awesome',
            name='Can do something awesome',
            content_type=fake_content_type,
        )

        fake_group, _ = Group.objects.get_or_create(name='SOMEONE')
        fake_group.permissions.add(fake_permission)

        data = {"username": "test1", "password": "password", "role": "SOMEONE"}
        response = self.client.post(reverse("signup"), json.dumps(data), content_type="application/json")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["user"], {"id": 1, "username": "test1"})
        self.assertEqual(response.json()["status"], "created")
        new_user = User.objects.get(id=response.json()["user"]["id"])
        self.assertIsNotNone(new_user)
        self.assertEqual(new_user.username, "test1")
        self.assertTrue(new_user.has_perm('myapp.can_do_something_awesome'))

    def test_signup_failed_role_request_body_invalid(self):
        data = {"password": "test1"}
        response = self.client.post(reverse("signup"), json.dumps(data), content_type="application/json")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "Data Invalid")
        self.assertIn("username must be set", response.json()["message"])
        self.assertEqual(response.json()["status"], "bad-request")

    def test_signup_failed_role_not_exist(self):
        data = {"username": "test1", "password": "password", "role": "SOMEONE"}
        response = self.client.post(reverse("signup"), json.dumps(data), content_type="application/json")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "Data Invalid")
        self.assertEqual(response.json()["message"], "invalid role")
        self.assertEqual(response.json()["status"], "bad-request")

    def test_show_user_success(self):
        fake_group, _ = Group.objects.get_or_create(name='PATIENT')
        current_user = User.objects.create_user(username='test1')
        current_user.groups.add(fake_group)

        with override_settings(VISIBLE_GROUPS_FILTER=self.visible_groups_filter_settings):
            headers = { "Authorization": f"Bearer {JWTUtils.generate_tokens(current_user)}" }
            response = self.client.get(reverse("user-detail", kwargs={'user_id': current_user.id}),
                                       content_type="application/json", headers=headers)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["user"], {"id": 1, "username": "test1", "roles": [fake_group.name]})
        self.assertEqual(response.json()["status"], "success")

    def test_show_other_user_success(self):
        fake_group, _ = Group.objects.get_or_create(name='PATIENT')
        existing_user = User.objects.create_user(username='test1')
        existing_user.groups.add(fake_group)
        current_user = User.objects.create_user(username='test2')

        with override_settings(VISIBLE_GROUPS_FILTER=self.visible_groups_filter_settings):
            headers = { "Authorization": f"Bearer {JWTUtils.generate_tokens(current_user)}" }
            response = self.client.get(reverse("user-detail", kwargs={'user_id': existing_user.id}),
                                       content_type="application/json", headers=headers)


        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["user"], {"id": existing_user.id, "username": existing_user.username, "roles": [fake_group.name]})
        self.assertEqual(response.json()["status"], "success")

    def test_show_other_user_not_found(self):
        current_user = User.objects.create_user(username='test2')

        headers = { "Authorization": f"Bearer {JWTUtils.generate_tokens(current_user)}" }
        response = self.client.get(reverse("user-detail", kwargs={'user_id': 184762}),
                                   content_type="application/json", headers=headers)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["error"], "User Not Found")
        self.assertEqual(response.json()["status"], "not-found")

    def test_update_current_user_success(self):
        current_user = User.objects.create_user(username='test2')

        headers = { "Authorization": f"Bearer {JWTUtils.generate_tokens(current_user)}" }
        data = {"username": "test2_updated"}
        response = self.client.put(reverse("user-detail", kwargs={'user_id': current_user.id}), json.dumps(data),
                                   content_type="application/json", headers=headers)

        self.assertEqual(response.status_code, 200)
        user = User.objects.filter(id=current_user.id).first()
        self.assertEqual(response.json()["user"], {"id": current_user.id, "username": user.username})
        self.assertEqual(response.json()["status"], "success")
        self.assertEqual(user.username, "test2_updated")

    def test_update_another_user_not_allowed(self):
        current_user = User.objects.create_user(username='test2')
        existing_user = User.objects.create_user(username='test3')

        headers = { "Authorization": f"Bearer {JWTUtils.generate_tokens(current_user)}" }
        data = {"username": "test3_updated"}
        response = self.client.put(reverse("user-detail", kwargs={'user_id': existing_user.id}), json.dumps(data),
                                   content_type="application/json", headers=headers)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["error"], "Unauthorized")
        user = User.objects.filter(id=existing_user.id).first()
        self.assertEqual(user.username, "test3")

    def test_delete_user_success(self):
        current_user = User.objects.create_user(username='test2')

        headers = { "Authorization": f"Bearer {JWTUtils.generate_tokens(current_user)}" }
        response = self.client.delete(reverse("user-detail", kwargs={'user_id': current_user.id}),
                                   content_type="application/json", headers=headers)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["user"], {"id": current_user.id, "username": current_user.username})
        self.assertEqual(response.json()["status"], "deleted")
        deleted_user = User.objects.filter(id=response.json()["user"]["id"]).first()
        self.assertIsNone(deleted_user)

    def test_delete_another_user_not_allowed(self):
        current_user = User.objects.create_user(username='test2')
        existing_user = User.objects.create_user(username='test3')

        headers = { "Authorization": f"Bearer {JWTUtils.generate_tokens(current_user)}" }
        response = self.client.delete(reverse("user-detail", kwargs={'user_id': existing_user.id}),
                                   content_type="application/json", headers=headers)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["error"], "Unauthorized")
        deleted_user = User.objects.filter(id=existing_user.id).first()
        self.assertIsNotNone(deleted_user)
