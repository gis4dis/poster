web: gunicorn poster.wsgi -k gevent --log-file - --reload
#web: "python manage.py runserver 0.0.0.0:$PORT"

celery-web: "flower -A poster --port=$PORT"
celery: celery -A poster worker -l info
celery_beat: celery -A poster beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler