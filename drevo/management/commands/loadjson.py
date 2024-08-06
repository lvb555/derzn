from django.core.management.base import BaseCommand
from django.core.management import call_command
from pathlib import Path


class Command(BaseCommand):
    help = 'load db from json'

    def handle(self, *args, **options):
        dump_file = options['dump_file']
        if not dump_file:
            self.stdout.write(self.style.WARNING('No dump file provided'))
            return

        if not Path(dump_file).exists():
            self.stdout.write(self.style.ERROR(f'Dump file {dump_file} not found'))
            return

        self.stdout.write(self.style.SUCCESS(f'load db from json {dump_file}'))
        params = {
            'exclude': ['admin.logentry', 'drevo.ip', 'drevo.visits', 'drevo.browsinghistory'],
            'verbosity': 3
        }

        call_command('loaddata', dump_file, **params)

    def add_arguments(self, parser):
        parser.add_argument('dump_file', type=str, help='JSON file with dump')
