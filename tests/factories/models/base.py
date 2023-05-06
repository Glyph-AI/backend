from tests.conftest import db_session

class BaseFactory():
    def __init__(self, db_session):
        self.db_session = db_session