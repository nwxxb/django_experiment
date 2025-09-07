from django.core.management.base import BaseCommand
from appointments_api.seeders import PermissionSeeder

class Command(BaseCommand):
    help = 'Seed content_types, permissions, groups for services and appointments'

    def handle(self, *args, **options):
        self.stdout.write('Seeding permissions and groups...')

        result = PermissionSeeder.seed_all()

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {len(result["permissions"])} permissions '
                f'and {len(result["groups"])} groups'
            )
        )
