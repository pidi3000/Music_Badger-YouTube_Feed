from music_feed import create_app

flask_app = create_app()
celery_app = flask_app.extensions["celery"]

# start celery worker cmd
# celery -A make_celery worker --loglevel INFO
