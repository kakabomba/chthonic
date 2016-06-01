from flask import g
from sqlalchemy.ext.declarative import declarative_base, declared_attr

Base = declarative_base()

class HBase:

    # db = None

    def __init__(self):
        # self.db = g.db
        pass
        # self.db = create_session(database_uri())

