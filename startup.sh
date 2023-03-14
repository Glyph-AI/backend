echo "Booting Application"

echo $(python app/database_setup.py)
# echo $(alembic upgrade head)
uvicorn --factory app.main:create_app --reload --host 0.0.0.0