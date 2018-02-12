web: gunicorn poster:application -k gevent --log-file -

celery: celery -A poster worker -l info
celery_beat: celery -A poster beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler