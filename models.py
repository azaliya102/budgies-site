from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Budgie(Base):
    __tablename__ = "budgies"
    budgie_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    color = Column(String)
    weight = Column(Integer)
    path = Column(String)
