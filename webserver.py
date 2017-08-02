from flask import Flask,render_template,url_for,request,redirect,flash,jsonify,make_response
from flask import session as login_session
import string,random
import queries as q
from oauth2client.client import flow_from_clientsecrets,FlowExchangeError
import httplib2,json,requests


CLIENT_ID = json.loads(open('client_secrets.json','r').read())['web']['client_id']
app = Flask(__name__)
# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("You are now logged in as %s" % login_session['username'])
    print "done!"
    return output


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response
@app.route('/')
@app.route('/restaurants')
def names():
    res_data = q.res_data()
    flag=0
    if('username' in login_session):
        username = login_session['username']
        url = "#"
        flag=1
    else:
        username = "Log In"
        url = url_for('showLogin')
    return render_template('main_page.html',res_data=res_data,username=username,loggedin=flag,url=url)
@app.route('/restaurants/new',methods=['GET','POST'])
def addRestaurant():
    if 'username' not in login_session:
        return redirect('/login')
    if(request.method=='POST'):
        name = request.form['name']
        q.res_add(name)
        flash("{} added to database successfully!".format(name))
        return redirect(url_for('names'))
    return render_template('add_res.html')
@app.route('/restaurants/<int:res_id>/edit',methods=['GET','POST'])
def editRestaurant(res_id):
    if 'username' not in login_session:
        return redirect('/login')
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
    if 'username' not in login_session:
        return redirect('/login')
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
    if 'username' not in login_session:
        return redirect('/login')
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
    if 'username' not in login_session:
        return redirect('/login')
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
    if 'username' not in login_session:
        return redirect('/login')
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
