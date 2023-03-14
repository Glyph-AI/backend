from sqlalchemy_utils import create_database, database_exists
import os


def init_database_func():
    url = os.environ["DATABASE_URL"]
    if not database_exists(url):
        print("DATABASE NOT FOUND")
        create_database(url)


if __name__ == '__main__':
    init_database_func()
