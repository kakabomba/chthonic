from application import app
from model.listener import Listener, Connection
from model.progress import Progress
import time
from sqlalchemy.sql import func

# ret = Listener.add_if_not_exists(app.state['grab_user'], True)

while True:
    less_followee = app.engine.execute("WITH time_span as (SELECT count(*), extract(epoch from min(cr_tm)) as mint, extract(epoch from max(cr_tm))+1 as maxt FROM listener WHERE connection_followees is NULL) SELECT * FROM time_span, listener WHERE cr_tm > to_timestamp(time_span.mint + (time_span.maxt - time_span.mint)* random()) LIMIT 1").fetchone()
    # less_followee = app.db.query(Listener.id).filter(Listener.connection_followees == None). \
    #     outerjoin(Connection, Connection.followee_id == Listener.id). \
    #     group_by(Listener.id). \
    #     order_by(func.count(Connection.followee_id).desc()).first()
    less_followee = app.db.query(Listener).filter_by(id=less_followee.id).one()
    # most_followee = app.db.query(Connection.follower_id)\
    #     .group_by(Connection.follower_id).order_by(func.count(Connection.followee_id).desc()).limit(100).all()
    print('Selected listener `%s` for grabbing with least followees' % (less_followee.id,))
    listener_stat = less_followee.grab()
    app.db.commit()
    # connections_stat = app.db.query(func.count(Connection.followee_id),
    #                                 func.count(func.distinct(Connection.follower_id)),
    #                                 func.count(func.distinct(Connection.followee_id))).one()

    new_listeners = listener_stat['followers']['added']
    for added_followee in listener_stat['followees']['added']:
        if added_followee not in listener_stat['followers']['added']:
            new_listeners.append(added_followee)

    data = {'listener_id': less_followee.id,
            'new_listeners': len(new_listeners),
            'add_followers': len(listener_stat['followers']['added']),
            'add_followees': len(listener_stat['followees']['added']),
            'exd_followers': len(listener_stat['followers']['existed']),
            'exd_followees': len(listener_stat['followees']['existed']),
            'del_followers': len(listener_stat['followers']['deleted']),
            'del_followees': len(listener_stat['followees']['deleted']),
            'total_listeners': app.db.query(func.count(Listener.id)).scalar(),
            'total_connections': 1, # connections_stat[0],
            'total_followers': 1, #connections_stat[1],
            'total_followees': 1, #connections_stat[2]
            }

    print(data)

    [print(line) for line in open('/proc/self/status') if 'VmPeak' in line]


    app.db.add(Progress(action='grab_listener_and_connections', data=data))

    app.db.commit()
