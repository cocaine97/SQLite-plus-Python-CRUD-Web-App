from flask import Flask,render_template,url_for,request,redirect
import queries as q


app = Flask(__name__)
@app.route('/')
@app.route('/restaurants')
def names():
    return "Under Construction"
@app.route('/restaurants/<int:res_id>/menu/')
def menu(res_id):
    r_id = res_id
    menu_data = q.item_data(r_id)
    res_name = q.res_name(r_id)
    return render_template('menu.html',menu_data=menu_data,res_name=res_name,r_id=r_id)

@app.route('/restaurants/<int:res_id>/menu/create/')
def newMenuItem(res_id):
    return "Create a new menu for restaurant {}".format(res_id)

@app.route('/restaurants/<int:res_id>/menu/<int:menu_id>/edit/',methods=['GET','POST'])
def editMenuItem(res_id,menu_id):
    if(request.method == "POST"):
        item_name = request.form['name']
        item_price = request.form['price']
        item_desc = request.form['desc']
        if(item_name== '' or item_price== '' or item_desc == ''):
            item_old = q.item_data_p(res_id,menu_id)
            if(item_name==''):
                item_name = item_old.name
            if(item_price == ''):
                item_price = item_old.price
            if(item_desc==''):
                item_desc = item_old.description

        q.item_edit(res_id,menu_id,item_name,item_price,item_desc)
        return redirect(url_for('menu',res_id=res_id))

    res_name = q.res_name(res_id)
    res_menu_data = q.item_data_p(res_id,menu_id)
    return render_template('edit_menu.html',res_id=res_id,menu_id=menu_id,res_name=res_name,res_menu_data=res_menu_data)

@app.route('/restaurants/<int:res_id>/menu/<int:menu_id>/delete/',methods=['GET','POST'])
def deleteMenuItem(res_id,menu_id):
    if(request.method=="POST"):
        q.item_delete(res_id,menu_id)
        return redirect(url_for('menu',res_id=res_id,menu_id=menu_id))
    res_name = q.res_name(res_id)
    item_name = q.item_data_p(res_id,menu_id).name
    return render_template('delete_menu.html',res_name=res_name,item_name=item_name,res_id=res_id,menu_id=menu_id)

if(__name__ == "__main__"):
    app.debug = True
    app.run(host="0.0.0.0",port = 5000)
