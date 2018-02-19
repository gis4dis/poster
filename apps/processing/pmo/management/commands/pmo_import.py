import logging
import os
from contextlib import closing
from tempfile import TemporaryFile
from urllib.parse import ParseResult

from django.core.files.storage import default_storage
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
                continue

            if not settings.APPLICATION_PMO_FTP_URL or type(settings.APPLICATION_PMO_FTP_URL) != ParseResult or not settings.IMPORT_ROOT:
                self.stdout.write("Can't read PMO settings. Check you configuration")
                continue

            file_dir_path = os.path.normpath(settings.IMPORT_ROOT + '/apps.processing.pmo/' + str(timezone.now().strftime("%Y%m%d")))
            file_path = os.path.normpath(file_dir_path + "/" + remote_filename)

            with closing(FTP(host=settings.APPLICATION_PMO_FTP_URL.hostname,
                             user=settings.APPLICATION_PMO_FTP_URL.username,
                             passwd=settings.APPLICATION_PMO_FTP_URL.password,
                             )) as ftp:

                try:
                    gen_name = default_storage.generate_filename(file_path)

                    with TemporaryFile() as f:
                        res = ftp.retrbinary('RETR %s' % remote_filename, f.write)

                        f.seek(0)
                        default_storage.save(gen_name, f)
                        if not res.startswith('226 Transfer complete'):
                            self.stderr.write('Download of file {0} is not complete.'.format(remote_filename))
                            # default_storage.delete(gen_name)
                            continue

                    self.stdout.write("File {} was successfully downloaded to {}".format(remote_filename, gen_name))
                    continue

                except Exception as e:
                    self.stderr.write('Error during download from FTP! {}'.format(e))
