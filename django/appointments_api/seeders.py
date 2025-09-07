from django.contrib.auth.models import Permission, Group, User
from django.contrib.contenttypes.models import ContentType
from django.db import transaction

class PermissionSeeder:
    @staticmethod
    def create_crud_permissions(content_type):
        permissions = {}

        for action in ['add', 'view', 'change', 'delete']:
            codename = f"{action}_{content_type.model}"
            name = f"Can {action} {content_type.model}"
            perm, _ = Permission.objects.get_or_create(
                    codename=codename,
                    name=name,
                    content_type=content_type
            )
            permissions[codename] = perm

        return permissions

    @staticmethod
    @transaction.atomic
    def seed_all():
        admin_group, _ = Group.objects.get_or_create(name='Admin')
        doctor_group, _ = Group.objects.get_or_create(name='Doctor')
        patient_group, _ = Group.objects.get_or_create(name='Patient')
        service_ct, _ = ContentType.objects.get_or_create(
                app_label='appointments_api',
                model='service'
        )
        appointment_ct, _ = ContentType.objects.get_or_create(
                app_label='appointments_api',
                model='appointment'
        )
        service_permissions = PermissionSeeder.create_crud_permissions(service_ct)
        appointment_permissions = PermissionSeeder.create_crud_permissions(appointment_ct)

        admin_group.permissions.set([*service_permissions.values()])
        doctor_group.permissions.set([*service_permissions.values()])
        patient_group.permissions.set([service_permissions["view_service"], *appointment_permissions.values()])

        return {
                "content_types": [service_ct],
                "permissions": [*service_permissions.values()],
                "groups": [admin_group, doctor_group, patient_group],
        }

