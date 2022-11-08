from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission


User = get_user_model()


class Command(BaseCommand):
    def handle(self, *args, **options):
        def create_developer_if_not_exists():
            developer_login = 'developer'
            developer_password = 'developer'
            developer_email = 'geekbrains@gmail.com'

            readers_group = Group.objects.create(name='Readers')
            readers_group_permissions = Permission.objects.filter(
                codename__startswith='view_'
            )
            readers_group.permissions.set(readers_group_permissions)

            developer = User.objects.create_user(
                username=developer_login,
                password=developer_password,
                email=developer_email,
                is_active=True,
                is_staff=True,
            )
            developer.groups.add(readers_group)

        create_developer_if_not_exists()
