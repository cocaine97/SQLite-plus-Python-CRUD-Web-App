from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base,Restaurant,MenuItem


engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSC = sessionmaker(bind = engine)
session = DBSC()

res = session.query(Restaurant).all()
item = session.query(MenuItem).all()

def res_names():
    names = []
    for x in res:
        names.append(x.name)
    return names
