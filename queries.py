from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base,Restaurant,MenuItem,User


engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSC = sessionmaker(bind = engine)
session = DBSC()


# ------    Restaurant Queries -------

def res_data():
    data = session.query(Restaurant).all()
    return data


def res_data_p(res_id):
    data = session.query(Restaurant).filter_by(id=res_id).one()
    return data

def res_delete(x):
    session.query(Restaurant).filter_by(id = x).\
    delete(synchronize_session='evaluate')
    session.commit()

def res_edit_name(x,new_name):
    data = session.query(Restaurant).filter_by(id=x).one()
    data.name = str(new_name)
    session.commit()

def res_name(x):
    data = session.query(Restaurant).filter_by(id=x).one()
    return data.name

def res_add(x,owner):
    naam = str(x)
    temp = Restaurant(name=naam,user_id=owner)
    session.add(temp)
    session.commit()

def res_edit(id,naam):
    temp = session.query(Restaurant).filter_by(id=id).one()
    temp.name = naam
    session.commit()

def res_owner_id(res_id):
    data = session.query(Restaurant).filter_by(id=res_id).one().user_id
    return data

# -------- MenuItem Queries --------
def item_data(x):
    data = session.query(MenuItem).filter_by(restaurant_id = x)
    return data
def item_by_course(res_id,item_course):
    item_course = str(item_course)
    data = session.query(MenuItem).filter_by(restaurant_id=res_id,course=item_course)
    return data

def item_data_p(r,m):
    data = session.query(MenuItem).filter_by(restaurant_id = r,id=m).one()
    return data

def item_add(res_id,item_name,item_price,item_desc,item_course,owner):
    data = MenuItem(restaurant_id=res_id,name=item_name,price=item_price,description=item_desc,course=item_course,user_id=owner)
    session.add(data)
    session.commit()


def item_edit(res_id,item_id,item_name,item_price,item_desc,item_course):
    data = session.query(MenuItem).filter_by(restaurant_id = res_id,id=item_id).one()
    data.name = item_name
    data.price = item_price
    data.description = item_desc
    data.course = item_course
    session.commit()

def item_delete(res_id,item_id):
    session.query(MenuItem).filter_by(restaurant_id = res_id,id=item_id).\
    delete(synchronize_session='evaluate')
    session.commit()

def item_owner_id(res_id,item_id):
    data = session.query(MenuItem).filter_by(restaurant_id=res_id,id=item_id).one().user_id
    return data

# - -   -   -   User Queries -  -   -   -   -
def user_add(name,email,picture):
    data = User(name=name,email=email,picture=picture)
    session.add(data)
    session.commit()

def user_check(email):
    flag = session.query(User).filter_by(email=email).first()
    if(flag == None):
        flag = 0
    else:
        flag = 1
    return flag

def user_data(email):
    data = session.query(User).filter_by(email=email).one()
    return data
