#!/bin/sh
if [ $IS_WORKER = "true" ];
then
    echo "RUNNING WORKER"
    echo $(celery --app=app.worker worker --loglevel=info)
else
    echo "BOOTING APP"
    echo $(python app/database_setup.py)
    echo $(alembic upgrade head)
    uvicorn --factory app.main:create_app --reload --host 0.0.0.0
fi