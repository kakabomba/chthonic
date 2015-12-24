from .h_base import HBase, Base

from sqlalchemy import Integer, String, TIMESTAMP, SMALLINT, BOOLEAN, Column, ForeignKey, UnicodeText, BigInteger, Binary, Float
from sqlalchemy.dialects.postgresql import BIGINT, INTEGER


class State(Base, HBase):

    __tablename__ = 'state'

    val = Column(String(100), nullable=False, primary_key=True)
    var = Column(String(65535), nullable=True)
    type = Column(String(100), nullable=True)

    def __int__(self):
        Base.__init__()
        HBase.__init__()
        self.variables = self.db


state = State()