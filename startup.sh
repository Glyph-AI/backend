#!/bin/sh
env_constant="development"
echo "BOOTING APP"
echo $(python app/database_setup.py)
echo $(alembic upgrade head)
if [ "$ENVIRONMENT" = "development" ]; then
    echo "IN DEVELOPMENT"
    uvicorn --factory app.main:create_app --reload --host 0.0.0.0
else
    uvicorn --factory app.main:create_app --host 0.0.0.0 --workers 8
fi