from django.core.management import BaseCommand

from help.models import Help


class Command(BaseCommand):
    def handle(self, *args, **options):
        Help.tree_objects.rebuild()