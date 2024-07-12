import io
import logging
from tempfile import TemporaryDirectory
from datetime import datetime

from django.core.management import call_command
from django.http import FileResponse
from django.contrib.auth.decorators import user_passes_test

from drevo.templatetags.has_group import has_group

logger = logging.getLogger('django')


@user_passes_test(lambda u: u.is_superuser or has_group(u, 'Readers'))
def get_dump(request):
    filename = f'dump_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.json'

    with TemporaryDirectory() as temp_dir_name:
        dump_filepath = f'{temp_dir_name}/{filename}'
        params = {
            # используем естественные ключи
            'use_natural_foreign_keys': True,
            'use_natural_primary_keys': True,
            # исключаем лишние таблицы
            'exclude': ['auth.permission',
                        'contenttypes',
                        'sessions.session',
                        'admin.logentry',
                        'drevo.ip', 'drevo.visits', 'drevo.browsinghistory'],
            'indent': 4,
            'output': dump_filepath
        }

        call_command('dumpdata', **params)
        logging.info(f'is dumped {dump_filepath}')

        with open(dump_filepath, 'rb') as dump:
            dump_in_memory = io.BytesIO(dump.read())
            return FileResponse(dump_in_memory,
                                as_attachment=True,
                                filename=filename)
