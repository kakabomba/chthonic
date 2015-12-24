from flask import g
from sqlalchemy.ext.declarative import declarative_base, declared_attr

Base = declarative_base()

def database_uri(db_name='chtonic', host='localhost', username='postgres', password='q'):
    return 'postgresql+psycopg2://{username}:{password}@{host}/{db_name}'. \
        format(**{'db_name': db_name,
                  'host': host,
                  'username': username,
                  'password': password})


def create_session(db_config):
    from sqlalchemy import create_engine
    from sqlalchemy.orm import scoped_session, sessionmaker

    engine = create_engine(db_config)
    g.sql_connection = engine.connect()
    db_session = scoped_session(sessionmaker(autocommit=False,
                                             autoflush=False,
                                             bind=engine))
    return db_session


class HBase:

    db = None

    def __init__(self):
        self.db = create_session(database_uri())

