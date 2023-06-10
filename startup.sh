#!/bin/sh
env_constant="development"
if [ $IS_WORKER = "true" ]; then
    echo "RUNNING WORKER"
    if [ "$ENVIRONMENT" = "development" ]; then
        echo "IN DEVELOPMENT"
        echo $(celery --app=app.worker worker --loglevel=info)
    else
        echo $(celery --app=app.worker worker --loglevel=info & uvicorn --factory app.main:create_app --host 0.0.0.0)
    fi
    
else
    echo "BOOTING APP"
    echo $(python app/database_setup.py)
    echo $(alembic upgrade head)
    if [ "$ENVIRONMENT" = "development" ]; then
        echo "IN DEVELOPMENT"
        uvicorn --factory app.main:create_app --reload --host 0.0.0.0
    else
        uvicorn --factory app.main:create_app --host 0.0.0.0 --workers 8
    fi
fi