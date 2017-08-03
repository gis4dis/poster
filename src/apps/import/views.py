import os
import stat
import codecs
import uuid

from django.core.exceptions import MultipleObjectsReturned
from django.http import HttpResponse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View


from poster.settings import IMPORT_ROOT, ALLOWED_EXTENSIONS

from .models import Provider, ProviderLog


@method_decorator(csrf_exempt, name='dispatch')
class ImportView(View):
    http_method_names = ['post']

    def post(self, request, code, token, file_name, ext, *args, **kwargs):
        """
        :param request:             general django request
        :param provider:            provider code
        :param token:               token used to limit load
        :param file_name:           filename passed in URL - use for storing it on disk
        :param ext:                 extension that is used for type
        :param args:                additional args (should be None)
        :param kwargs:              additional kwargs (should be None)
        :return:                    HttpResponse(status=204)
        """

        # General algorithm logic:
        #
        # Search for valid provider or return
        # Validate token (on invalid token continue but mark it as invalid!)
        # Save all stuff into file on HDD + DB
        #

        # Validate ext - we are storing the file to HDD!!!
        if ext not in ALLOWED_EXTENSIONS:
            ext = "txt"

        # Some useful dates
        now = timezone.now()
        year = str(now.strftime("%Y"))
        month = str(now.strftime("%m"))
        now_str = str(now.strftime("%Y%m%d-%H%M%S"))
        uuid4 = uuid.uuid4()

        # TODO: replace/pass this stuff to celery for BG processing

        try:
            # Get provider from DB
            provider = Provider.objects.get(code=code)
            if str(provider.token) == str(token):
                is_valid = True
                is_valid_string = "valid"
            else:
                is_valid = False
                is_valid_string = "invalid"

            # Generate dir path: /<settings.IMPORT_ROOT>/<provider>/<year>/<month>
            # Example:           /opt/app/import/abc/2017/01
            #
            file_dir_path = os.path.join(IMPORT_ROOT, code, year, month)

            # Generate filename: <%Y%m%d-%H%M%S>_(valid|invalid)_<file_name>_<uuid4>.<ext>
            # Example:           20171231-235959_valid_data_e6911354-2f49-40d3-827d-43a5015a673b.xml
            full_file_name = now_str + "_" + is_valid_string + "_" + file_name + "_" + str(uuid4) + "." + ext

            # Join paths
            file_path = os.path.join(file_dir_path, full_file_name)

            # Create provider LOG for this request
            provider_log = ProviderLog(
                provider=provider,
                is_valid=is_valid,
                content_type=str(request.content_type),
                body=str(request.body),
                file_name=file_name,
                file_path=file_path,
                ext=ext,
                received_time=now,
            )
            provider_log.save()

            # Write content to the file
            self._ensure_path(file_dir_path)
            self._write_to_file(file_path, str(request.body))

        except (MultipleObjectsReturned, Provider.DoesNotExist) as ex:
            # Invalid provider! Don't log this - excess load!
            pass

        # Finally return the Http Status 204 - No Content
        return HttpResponse(status=204)

    def _ensure_path(self, file_dir_path, mode=0o770):
        try:
            os.makedirs(file_dir_path, mode, exist_ok=True)
        except os.error as ex:
            raise ex

    def _write_to_file(self, file_path, content):
        try:
            with codecs.open(file_path, 'w', 'utf-8') as data_file:
                data_file.write(content)
            os.chmod(file_path, stat.S_IREAD | stat.S_IWRITE)
        except ValueError as ex:
            raise ex
