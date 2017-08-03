import os
import sys
from sqlalchemy import Column,Integer,String,ForeignKey,create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


Base = declarative_base()

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))

class Restaurant(Base):
    __tablename__ = 'restaurant'

    id = Column(Integer,primary_key=True)
    name = Column(String(250),nullable=False)
    user_id = Column(Integer,ForeignKey('user.id'))
    user = relationship(User)

class MenuItem(Base):
    __tablename__='menu_item'

    name = Column(String(250),nullable=False)
    id = Column(Integer,primary_key=True)
    description = Column(String(500))
    price = Column(String(30),nullable=False)
    course = Column(String(250))
    restaurant = relationship(Restaurant)
    restaurant_id = Column(Integer,ForeignKey('restaurant.id'))
    user_id = Column(Integer,ForeignKey('user.id'))
    user = relationship(User)


    @property
    def serialize(self):
        return {
            'name' : self.name,
            'description' : self.description,
            'id' : self.id,
            'price' : self.price,
            'course' : self.course,
        }

engine = create_engine("sqlite:///restaurantmenu.db")
Base.metadata.create_all(engine)
