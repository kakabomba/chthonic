from .h_base import HBase, Base

from sqlalchemy import Integer, String, TIMESTAMP, SMALLINT, BOOLEAN, Column, ForeignKey, UnicodeText, BigInteger, Binary, Float
from sqlalchemy.dialects.postgresql import BIGINT, INTEGER


class Listener(Base, HBase):

    __tablename__ = 'listener'

    id = Column(BIGINT, nullable=False, primary_key=True)
    uid = Column(String(1000), nullable=False)
    name = Column(String(1000))


