from sqlalchemy import String, Column

from .h_base import HBase, Base
from sqlalchemy import Integer, String, TIMESTAMP, SMALLINT, BOOLEAN, Column, ForeignKey, UnicodeText, BigInteger, \
    Binary, Float
from sqlalchemy.dialects.postgresql import BIGINT, INTEGER, JSONB


class Progress(Base, HBase):
    __tablename__ = 'progress'

    id = Column(String(36), nullable=False, primary_key=True)
    action = Column(String(50), nullable=False, default='')
    cr_tm = Column(TIMESTAMP, nullable=True)
    comment = Column(String(50), nullable=False, default='')
    data = Column(JSONB, nullable=False, default={})




