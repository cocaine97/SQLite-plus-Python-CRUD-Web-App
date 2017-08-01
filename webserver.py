from flask import Flask,render_template,url_for,request,redirect,flash,jsonify
from flask import session as login_session
import string,random
import queries as q


app = Flask(__name__)
@app.route('/login')
def login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(32))
    login_session['state']=state
    return render_template('login.html')
@app.route('/')
@app.route('/restaurants')
def names():
    res_data = q.res_data()
    return render_template('main_page.html',res_data=res_data)
@app.route('/restaurants/new',methods=['GET','POST'])
def addRestaurant():
    if(request.method=='POST'):
        name = request.form['name']
        q.res_add(name)
        flash("{} added to database successfully!".format(name))
        return redirect(url_for('names'))
    return render_template('add_res.html')
@app.route('/restaurants/<int:res_id>/edit',methods=['GET','POST'])
def editRestaurant(res_id):
    res_name = q.res_name(res_id)
    if(request.method=="POST"):
        new_name = request.form['res_new_name']
        if(new_name == '' or new_name == res_name):
            new_name = res_name
            flash('No changes made to {}'.format(new_name))
            return redirect(url_for('names'))
        else:
            q.res_edit(res_id,new_name)
            flash('{} renamed to {} successfully'.format(res_name,new_name))
            return redirect(url_for('names'))
    res_id = res_id
    return render_template('edit_res.html',res_id=res_id,res_name=res_name)

@app.route('/restaurants/<int:res_id>/delete',methods=['GET','POST'])
def deleteRestaurant(res_id):
    res_name = q.res_name(res_id)
    if(request.method=="POST"):
        q.res_delete(res_id)
        flash("{} removed successfully".format(res_name))
        return redirect(url_for('names'))
    return render_template('delete_res.html',res_id=res_id,res_name=res_name)
@app.route('/restaurants/<int:res_id>/menu/')
def menu(res_id):
    r_id = res_id
    menu_data = q.item_data(r_id)
    flag = menu_data.first()
    res_name = q.res_name(r_id)
    #print(menu_data)
    return render_template('menu.html',menu_data=menu_data,res_name=res_name,r_id=r_id,flag=flag)

@app.route('/restaurants/<int:res_id>/menu/create/',methods=['GET','POST'])
def newMenuItem(res_id):
    if(request.method=="POST"):
        item_name = request.form['name']
        item_price = request.form['price']
        item_desc = request.form['desc']
        if(item_price == ''):
            item_price = 'Empty'
        if(item_desc == ''):
            item_desc = 'Empty'
        q.item_add(res_id,item_name,item_price,item_desc)
        flash('{} created!'.format(item_name))
        return redirect(url_for('menu',res_id=res_id))

    res_name = q.res_name(res_id)
    return render_template('create.html',res_id=res_id,res_name=res_name)

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
            if(item_name == item_old.name and item_price == item_old.price and item_desc == item_old.description):
                flash_changes = "No changes made to {} .".format(item_name)
            else:
                flash_changes = "Changes saved successfully!"

        q.item_edit(res_id,menu_id,item_name,item_price,item_desc)
        flash(flash_changes)
        return redirect(url_for('menu',res_id=res_id))

    res_name = q.res_name(res_id)
    res_menu_data = q.item_data_p(res_id,menu_id)
    return render_template('edit_menu.html',res_id=res_id,menu_id=menu_id,res_name=res_name,res_menu_data=res_menu_data)

@app.route('/restaurants/<int:res_id>/menu/<int:menu_id>/delete/',methods=['GET','POST'])
def deleteMenuItem(res_id,menu_id):
    if(request.method=="POST"):
        item_name = q.item_data_p(res_id,menu_id).name
        q.item_delete(res_id,menu_id)
        flash("{} removed.".format(item_name))

        return redirect(url_for('menu',res_id=res_id,menu_id=menu_id))
    res_name = q.res_name(res_id)
    item_name = q.item_data_p(res_id,menu_id).name
    return render_template('delete_menu.html',res_name=res_name,item_name=item_name,res_id=res_id,menu_id=menu_id)

    #JSON Routes ---
@app.route('/restaurants/<int:res_id>/menu/JSON')
def res_menu_JSON(res_id):
    #res_data = q.res_data_p(res_id)
    item_data = q.item_data(res_id)
    return jsonify(MenuItem = [item.serialize for item in item_data])

@app.route('/restaurants/<int:res_id>/menu/<int:menu_id>/JSON')
def res_menu_p_JSON(res_id,menu_id):
    item_data = q.item_data_p(res_id,menu_id)
    return jsonify(MenuItem = [item_data.serialize])

if(__name__ == "__main__"):
    app.secret_key = "dfg12345"
    app.debug = True
    app.run(host="0.0.0.0",port = 5000)
