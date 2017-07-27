from flask import Flask
import queries as q


app = Flask(__name__)
@app.route('/')
@app.route('/restaurants')
def names():
    res_data = q.res_data()
    res_out = ''
    for res in res_data:
        res_out += "<h1>{}</h1>".format(res.name)
    return res_out

@app.route('/restaurants/<int:res_id>/menu/')
def menu(res_id):
    menu_data = q.item_data(res_id)

    menu_out = ''
    for m in menu_data:
        menu_out += "<h2>{}</h2>".format(m.name)
        menu_out += "<h3>{}</h3>".format(m.price)
        menu_out += "<h3>{}</h3>".format(m.description)
        menu_out += "<br>"
    return menu_out

@app.route('/restaurants/<int:res_id>/menu/create/')
def newMenuItem(res_id):
    return "Create a new menu for restaurant {}".format(res_id)

@app.route('/restaurants/<int:res_id>/menu/<int:menu_id>/edit/')
def editMenuItem(res_id,menu_id):
    return "Edit {}\'s menu number {}".format(res_id,menu_id)

@app.route('/restaurants/<int:res_id>/menu/<int:menu_id>/delete/')
def deleteMenuItem(res_id,menu_id):
    return "Delete {}\'s menu number {}".format(res_id,menu_id)

if(__name__ == "__main__"):
    app.debug = True
    app.run(host="0.0.0.0",port = 5000)
