import os
import sys
from sqlalchemy import Column,Integer,String,ForeignKey,create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Restaurant(Base):
    __tablename__ = 'restaurant'

    id = Column(Integer,primary_key=True)
    name = Column(String(250),nullable=False)

class MenuItem(Base):
    __tablename__='menu_item'

    name = Column(String(250),nullable=False)
    id = Column(Integer,primary_key=True)
    description = Column(String(500))
    price = Column(String(30),nullable=False)
    course = Column(String(250))
    restaurant = relationship(Restaurant)
    restaurant_id = Column(Integer,ForeignKey('restaurant.id'))

engine = create_engine("sqlite:///restaurantmenu.db")
Base.metadata.create_all(engine)
