from model.state import State


class Application():

    def database_uri(self, db_name='chthonic', host='localhost', username='postgres', password='q'):
        return 'postgresql+psycopg2://{username}:{password}@{host}/{db_name}'. \
            format(**{'db_name': db_name,
                      'host': host,
                      'username': username,
                      'password': password})


    def create_session(self, db_config):
        from sqlalchemy import create_engine
        from sqlalchemy.orm import scoped_session, sessionmaker

        engine = create_engine(db_config)
        sql_connection = engine.connect()
        db_session = scoped_session(sessionmaker(autocommit=False,
                                                 autoflush=False,
                                                 bind=engine))
        return (db_session, engine)

    # db = create_session(database_uri())
    # state = {i.var: i.val for i in db.query(State).all()}
    db = None
    engine = None
    state = {}

    def __init__(self):
        (self.db, self.engine) = self.create_session(self.database_uri())
        self.state = {i.var: i.val for i in self.db.query(State).all()}


app = Application()