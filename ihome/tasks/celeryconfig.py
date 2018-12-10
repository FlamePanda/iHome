# celery配置文件

## Broker settings.
BROKER_URL = 'redis://127.0.0.1:6379/1'

## Using the database to store task state and results.
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/2'

