import re
import html
import datetime

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Numeric, Column, SmallInteger, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


Base = declarative_base()

class Provider(Base):
    __tablename__ = "main_provider"

    id = Column(Integer, primary_key=True)

    name = Column(String(32), default='')
    referral = Column(String(255), default='')
    host = Column(String(255), default='')
    promo_code = Column(String(32), default='')

    dt_created = Column(DateTime(timezone=True), default=func.now())
    dt_updated = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())


class Plan(Base):
    __tablename__ = "main_plan"

    id = Column(Integer, primary_key=True)

    provider_id = Column(Integer, ForeignKey('main_provider.id'))
    provider = relationship(Provider)
    name = Column(String(32), default='')

    price = Column(Numeric(precision=12, scale=2))
    period = Column(SmallInteger())
    currency_code = Column(String(4))
    currency_symb = Column(String(4))

    cores = Column(SmallInteger())

    disk = Column(Integer())
    disk_unit = Column(String(4))

    ram = Column(Integer())
    ram_unit = Column(String(4))

    bandwidth = Column(Integer(), default='')
    bandwidth_unit = Column(String(4), default='')

    speed = Column(Integer(), default='')
    speed_unit = Column(String(4), default='')

    platform = Column(String(32), default='')

    url = Column(String(255), default='')
    # backup = Column(SmallInteger())
    # route_optimize = Column(String(128))

    dt_created = Column(DateTime(timezone=True), default=func.now())
    dt_updated = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())

