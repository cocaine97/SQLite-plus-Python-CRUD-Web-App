from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base,Restaurant,MenuItem


engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSC = sessionmaker(bind = engine)
session = DBSC()


#item = session.query(MenuItem).all()

def res_data():
    data = session.query(Restaurant).all()
    return data

def res_add(x):
    naam = str(x)
    temp = Restaurant(name=naam)
    session.add(temp)
    session.commit()

def res_edit(idd,naam):
    temp = session.query(Restaurant).filter_by(id=idd).one()
    temp.name = naam
    session.commit()
