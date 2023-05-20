#!/bin/sh
if [ $IS_WORKER = "true" ];
then
    echo "RUNNING WORKER"
    echo $(celery --app=app.worker worker --loglevel=info & uvicorn --factory app.main:create_app --host 0.0.0.0)
else
    echo "BOOTING APP"
    echo $(python app/database_setup.py)
    echo $(alembic upgrade head)
    if [ $ENVIRONMENT = "development"];
    then
        uvicorn --factory app.main:create_app --reload --host 0.0.0.0
    else
        uficorn --factory app.main:create_app --host 0.0.0.0
    fi
fi