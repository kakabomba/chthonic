from .h_base import HBase, Base
import re
from application import app

from sqlalchemy import Integer, String, TIMESTAMP, SMALLINT, BOOLEAN, Column, ForeignKey, UnicodeText, BigInteger, \
    Binary, Float
from sqlalchemy.dialects.postgresql import BIGINT, INTEGER
from sqlalchemy.orm import relationship, remote
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy import inspect

import urllib.request

import time
from stem.control import Controller
from stem import Signal
import requests
from bs4 import BeautifulSoup

import socks
import socket

from functools import wraps
import errno
import os
import signal


class TimeoutError(Exception):
    pass


def timeout(seconds=10, error_message=os.strerror(errno.ETIME)):
    def decorator(func):
        def _handle_timeout(signum, frame):
            raise TimeoutError(error_message)

        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result

        return wraps(func)(wrapper)

    return decorator


@timeout(30)
def get_page_via_tor(get_url):
    controller = None
    temp = None
    try:
        controller = Controller.from_port(port=9151)
        temp = socket.socket
        socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9150)
        socket.socket = socks.socksocket
        controller.authenticate()
        controller.signal(Signal.NEWNYM)
        r = requests.get(get_url)
        ret = r.content
    except Exception as e:
        if temp:
            socket.socket = temp
        if controller:
            controller.close()
        raise e

    socket.socket = temp
    if controller:
        controller.close()
    return ret


def get_page(url):
    trying = 1
    maxtry = 10
    while trying <= maxtry:
        try:
            print('page requested `%s`' % (url,))
            ret = get_page_via_tor(url).decode("utf-8")
            print('page given')
            return ret
        except Exception as e:
            print("Error `%s` getting url `%s`, trying `%s` of `%s`" % (e, url, trying, maxtry))
            trying += 1
            time.sleep(1)

            # with urllib.request.urlopen(url) as response:
            #     html = response.read()
            # return html.decode("utf-8")
    print("Give up getting url: `%s`. empty string returned" % (url,))
    return False


class Connection(Base, HBase):
    __tablename__ = 'connection'

    follower_id = Column(String(63), ForeignKey('listener.id'), primary_key=True, nullable=False)
    followee_id = Column(String(63), ForeignKey('listener.id'), primary_key=True, nullable=False)
    # status = Column(Integer, nullable=False)


    # follower = relationship(Listener, primaryjoin=(follower_id == Listener.id), backref='followers')
    # followee = relationship(Listener, primaryjoin=(followee_id == Listener.id), backref='followees')


class Listener(Base, HBase):
    __tablename__ = 'listener'

    id = Column(String(63), nullable=False, primary_key=True)
    name = Column(String(1000))
    last_error = Column(String(1000))
    md_tm = Column(TIMESTAMP, nullable=True)
    cr_tm = Column(TIMESTAMP, nullable=True)
    connection_followers = Column(Integer, nullable=True)
    connection_followees = Column(Integer, nullable=True)

    # trad about relationship in sqlalchemy
    followers = relationship("Listener",
                             secondary=Connection.__table__,
                             primaryjoin=id == Connection.followee_id,
                             secondaryjoin=id == Connection.follower_id,
                             collection_class=attribute_mapped_collection('id'))

    followees = relationship("Listener",
                             secondary=Connection.__table__,
                             primaryjoin=id == Connection.follower_id,
                             secondaryjoin=id == Connection.followee_id,
                             collection_class=attribute_mapped_collection('id'))

    # followers_rel = relationship("Listener", secondary=lambda: Connection)
    # followees_rel = relationship("Listener", secondary=lambda: Connection)

    # followers = association_proxy('followers_rel', 'id')
    # followees = association_proxy('followees_rel', 'id')

    # followers = relationship("Connection", primaryjoin= id == Connection.followee_id,
    #                          collection_class=attribute_mapped_collection('id'))
    # followees = relationship("Connection", primaryjoin= id == Connection.follower_id,
    #                          collection_class=attribute_mapped_collection('id.'))

    # followers = []
    # following = []

    def parse_profile(self):
        pass

    def add_if_not_exists(self, listener_id, commit=False):
        if listener_id in self.followers:
            return self.followers[listener_id]

        if listener_id in self.followees:
            return self.followees[listener_id]

        ret = app.db.query(Listener).filter_by(id=listener_id).first()

        if not ret:
            ret = Listener(id=listener_id)
            app.db.add(ret)
            if commit:
                app.db.commit()

        return ret

    def get_connections(self, typeofconnection='followers'):

        page = 1
        pages = 1
        added = []
        deleted = []

        if self.connection_followees is None:
            self.connection_followees = 0

        if self.connection_followers is None:
            self.connection_followers = 0

        while page <= pages:

            page_url = "http://www.last.fm/user/" + self.id + '/' + typeofconnection + (
            '' if page == 1 else ('?page=%s' % (page,)))

            # grabbing page
            html = get_page(page_url)

            if not html:
                self.last_error = 'page `%s` not given' % (page_url,)
                html = ''

            print("Grabbing page `%s` of `%s`" % (page, pages))

            # parsing number of pages to grap
            search_for_pages = re.search('<li class="pages">\s+Page\s+\d+\s+of\s+(\d+)\s+</li>', html, re.M)

            if search_for_pages and search_for_pages.groups(1):
                pages = int(search_for_pages.groups(1)[0])

                "\naaaa\naaaaaaaa\naaa"

            # usernames
            names = re.findall(
                    '^<li class="user-list-item">.*?<div class="username">.*?<a href="/user/([^"]+)"', html,
                    re.M | re.DOTALL)

            for name in names:
                if typeofconnection == 'followers':
                    self.connection_followers += 1
                    if name not in self.followers:
                        self.followers[name] = self.add_if_not_exists(name)
                        state = inspect(self.followers[name])
                        if not state.persistent:
                            added.append(name)
                else:
                    self.connection_followees += 1
                    if name not in self.followees:
                        self.followees[name] = self.add_if_not_exists(name)
                        state = inspect(self.followees[name])
                        if not state.persistent:
                            added.append(name)

            page += 1

        # print("Listeners added `%s`, Old %s: `%s`, Added %s: `%s`, removed %s: `%s`" %
        #       (new_listeners, typeofconnection, len(self.followers) - new_connection,
        #        typeofconnection, new_connection, typeofconnection, deleted_connections))

        return {'added': added,
                # list(set(a) & set(b))
                'existed': list(
                        set(self.followers.keys() if typeofconnection == 'followers' else self.followees.keys()) - set(
                                added)),
                'deleted': deleted}

    def grab(self):
        return {'followers': self.get_connections(typeofconnection='followers'),
                'followees': self.get_connections(typeofconnection='following')}




        # profile = urllib.request.urlopen("http://www.last.fm/user/" + self.uid)

        # following = urllib.request.urlopen("http://www.last.fm/user/" + self.uid)
