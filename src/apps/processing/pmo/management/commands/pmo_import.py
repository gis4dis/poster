import logging
import os
from contextlib import closing
from django.utils import timezone

from django.core.management.base import BaseCommand
from django.conf import settings
from ftplib import FTP

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Import data from PMO stations.'

    def add_arguments(self, parser):
        parser.add_argument('filename', nargs='*', type=str, default=None)

    def handle(self, *args, **options):
        remote_filenames = options['filename']
        self.stdout.write(str(remote_filenames))

        if not remote_filenames:
            self.stdout.write("No filenames specified")
            return

        for remote_filename in remote_filenames:
            if not remote_filename:
                self.stdout.write("No filename specified")
                return

            if not settings.PMO_FTP or type(settings.PMO_FTP) != dict or not settings.IMPORT_ROOT:
                self.stdout.write("Can't read PMO settings. Check you configuration")
                return

            local_filedir = os.path.join(settings.IMPORT_ROOT, "providers/PMO", str(timezone.now().strftime("%Y%m%d-%H%M%S")))
            local_filename = os.path.join(local_filedir,  remote_filename)

            with closing(FTP(**settings.PMO_FTP)) as ftp:
                try:
                    os.makedirs(local_filedir, 0o770, exist_ok=True)

                    with open(local_filename, 'wb') as f:
                        res = ftp.retrbinary('RETR %s' % remote_filename, f.write)

                        if not res.startswith('226 Transfer complete'):
                            self.stdout.write('Downloaded of file {0} is not compile.'.format(remote_filename))
                            os.remove(local_filename)
                            return None

                    self.stderr.write("File {} was successfully downloaded to {}".format(remote_filename, local_filename))
                    return local_filename

                except Exception as e:
                    self.stderr.write('Error during download from FTP! {}'.format(e))
