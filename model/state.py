from sqlalchemy import String, Column

from .h_base import HBase, Base


class State(Base, HBase):
    __tablename__ = 'state'

    val = Column(String(100), nullable=False, primary_key=True)
    var = Column(String(65535), nullable=True)
    type = Column(String(100), nullable=True)


