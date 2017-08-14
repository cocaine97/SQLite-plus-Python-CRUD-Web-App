from flask import Flask, render_template, url_for, request
from flask import session as login_session, redirect, flash
from flask import jsonify, make_response
import string
import random
import queries as q
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests
from twilio.rest import Client


CLIENT_ID = json.loads(
    open('/var/www/catalog/client_secrets.json', 'r').read())['web']['client_id']
app = Flask(__name__)
app.secret_key = "super secret key"
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
        oauth_flow = flow_from_clientsecrets('/var/www/catalog/client_secrets.json', scope='')
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
        response = make_response(json.dumps(
            'Current user is already connected.'),
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
    flag = q.user_check(data['email'])
    if not flag:
        q.user_add(login_session['username'],
                   login_session['email'], login_session['picture'])
    login_session['user_id'] = q.user_data(login_session['email']).id
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius:'
    '150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("You are now logged in as %s" % login_session['username'])
    print "done!"
    return output


# Code for disconnecting user
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('Current user nt connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']  # noqa
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
        flash("Successfully logged out!")
        return redirect(url_for('names'))
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))  # noqa
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/')
@app.route('/restaurants')
def names():
    res_data = q.res_data()
    flag = 0
    # Checking if the user is logged in
    # Loads different buttons on the nav
    # Depending upon the state
    if('username' in login_session):
        username = login_session['username']
        url = "#"
        flag = 1
        c_user = login_session['user_id']
    else:
        username = "Log In"
        url = url_for('showLogin')
    if(flag == 1):
        return render_template('main_page.html', c_user=c_user,
                               res_data=res_data, username=username,
                               loggedin=flag, url=url)
    else:
        return render_template('main_page.html', res_data=res_data,
                               username=username, loggedin=flag,
                               url=url)


# Code for creating a restaurant
@app.route('/restaurants/new', methods=['GET', 'POST'])
def addRestaurant():
    if 'username' not in login_session:
        return redirect('/login')
    if(request.method == 'POST'):
        name = request.form['name']
        res_owner = login_session['user_id']
        q.res_add(name, res_owner)
        flash("{} added to database successfully!".format(name))
        return redirect(url_for('names'))
    return render_template('add_res.html')


# Code for editing a restaurant
@app.route('/restaurants/<int:res_id>/edit', methods=['GET', 'POST'])
def editRestaurant(res_id):
    if 'username' not in login_session:
        return redirect('/login')
    # Checking if it's the owner that's
    # Trying to edit the restaurant
    res_owner = q.res_owner_id(res_id)
    if(res_owner != login_session['user_id']):
            return "Access Denied"
    res_name = q.res_name(res_id)
    if(request.method == "POST"):
        new_name = request.form['res_new_name']
    # Checks if the fields were left empty
        if(new_name == '' or new_name == res_name):
            new_name = res_name
            flash('No changes made to {}'.format(new_name))
            return redirect(url_for('names'))
        else:
            q.res_edit(res_id, new_name)
            flash('{} renamed to {} successfully'.format(res_name, new_name))
            return redirect(url_for('names'))
    res_id = res_id
    return render_template('edit_res.html', res_id=res_id, res_name=res_name)


# Code for deleting a restaurant
@app.route('/restaurants/<int:res_id>/delete', methods=['GET', 'POST'])
def deleteRestaurant(res_id):
    if 'username' not in login_session:
        return redirect('/login')
    # Checks if it's the owner thats
    # Trying to delete the restaurant
    res_owner = q.res_owner_id(res_id)
    if(res_owner != login_session['user_id']):
            return "Access Denied"
    res_name = q.res_name(res_id)
    if(request.method == "POST"):
        q.res_delete(res_id)
        flash("{} removed successfully".format(res_name))
        return redirect(url_for('names'))
    return render_template('delete_res.html', res_id=res_id, res_name=res_name)


# Code for displaying the menu page
@app.route('/restaurants/<int:res_id>/menu/')
def menu(res_id):
    menu_data = q.item_data(res_id)
    res_owner = q.res_owner_id(res_id)
    loggedIN = 0
    owner_flag = 0
    # Checking if user is logged in
    if('username' in login_session):
        loggedIN = 1
        c_user = login_session['user_id']
        # Checking if user is the owner
        if(res_owner == login_session['user_id']):
            owner_flag = 1
    r_id = res_id

    # Distinguishing between different foods
    # To be displayed in groups
    menu_entree = q.item_by_course(r_id, "Entree")
    menu_dessert = q.item_by_course(r_id, "Dessert")
    menu_appetizer = q.item_by_course(r_id, "Appetizer")
    menu_beverage = q.item_by_course(r_id, "Beverage")
    print(menu_entree)
    entree_flag = 0
    dessert_flag = 0
    appetizer_flag = 0
    beverage_flag = 0
    # Hides the "Type" of food if not present
    if(menu_entree.first() is not None):
        entree_flag = 1
    if(menu_dessert.first() is not None):
        dessert_flag = 1
    if(menu_beverage.first() is not None):
        beverage_flag = 1
    if(menu_appetizer.first() is not None):
        appetizer_flag = 1
    print(appetizer_flag)
    flag = menu_data.first()
    res_name = q.res_name(res_id)
    if(loggedIN):
        # Loads if the user is the owner of the restaurant
        return render_template('menu.html', owner_flag=owner_flag,
                               c_user=c_user, entree=menu_entree,
                               dessert=menu_dessert,
                               appetizer=menu_appetizer,
                               beverage=menu_beverage,
                               app_flag=appetizer_flag,
                               bev_flag=beverage_flag,
                               ent_flag=entree_flag,
                               des_flag=dessert_flag,
                               res_name=res_name, r_id=res_id,
                               flag=flag, loggedIN=loggedIN)
    else:
        # Loads if user isn't the owner
        return render_template('menu.html', entree=menu_entree,
                               dessert=menu_dessert,
                               appetizer=menu_appetizer,
                               beverage=menu_beverage,
                               app_flag=appetizer_flag,
                               bev_flag=beverage_flag,
                               ent_flag=entree_flag,
                               des_flag=dessert_flag,
                               res_name=res_name,
                               r_id=res_id,
                               flag=flag,
                               loggedIN=loggedIN)


# Code for adding a new menu item
@app.route('/restaurants/<int:res_id>/menu/create/', methods=['GET', 'POST'])
def newMenuItem(res_id):
    if 'username' not in login_session:
        return redirect('/login')
    if(request.method == "POST"):
        item_name = request.form['name']
        item_price = request.form['price']
        item_desc = request.form['desc']
        item_course = request.form['course']
        item_owner = login_session['user_id']
        res_name = q.res_name(res_id)
        res_owner = q.res_owner_id(res_id)
        owner_email = q.user_email(res_owner)
        dfg = "dfg31197@gmail.com"
        if(item_price == ''):
            item_price = 'Empty'
        if(item_desc == ''):
            item_desc = 'Empty'
        q.item_add(res_id, item_name, item_price,
                   item_desc, item_course, item_owner)
        # Checks if someone other than me added menu item
        if(owner_email == dfg and login_session['user_id'] != res_owner):
            # Your Account SID from twilio.com/console
            account_sid = "AC7daf180961514118e4b7b8c1c6fae576"
            # Your Auth Token from twilio.com/console
            auth_token = "c3f639dc94b32d51dd30068456675864"

            client = Client(account_sid, auth_token)
            # Fires a message to my phone that someone added a menu item
            # To my restaurant
            # Could have added this for all users but storing phone numbers
            # Seemed kinda risky
            message = client.messages.create(
                to="+919779467318",
                from_="+12407165865",
                body="{} has added {} to"
                     "your restaurant {} !".format(login_session['username'],
                                                   item_name, res_name))

            print(message.sid)
        flash('{} created!'.format(item_name))
        return redirect(url_for('menu', res_id=res_id))

    res_name = q.res_name(res_id)
    return render_template('create.html', res_id=res_id, res_name=res_name)


# Code for editing a menu item
@app.route('/restaurants/<int:res_id>/menu/<int:menu_id>/edit/',
           methods=['GET', 'POST'])
def editMenuItem(res_id, menu_id):
    if 'username' not in login_session:
        return redirect('/login')
    # Checking if you created the item
    item_owner = q.item_owner_id(res_id, menu_id)
    # Checking if you're the restaurant owner
    res_owner = q.res_owner_id(res_id)
    if(res_owner != login_session['user_id'] and item_owner != login_session['user_id']):  # noqa
        return "Access Denied"
    if(request.method == "POST"):
        item_name = request.form['name']
        item_price = request.form['price']
        item_desc = request.form['desc']
        item_course = request.form['course']
        item_old = q.item_data_p(res_id, menu_id)
        # If fields are submitted empty, the old data stays put
        if(item_name == '' or item_price == '' or item_desc == ''):
            if(item_name == ''):
                item_name = item_old.name
            if(item_price == ''):
                item_price = item_old.price
            if(item_desc == ''):
                item_desc = item_old.description
            if(item_name == item_old.name and item_price == item_old.price and item_desc == item_old.description and item_old.course == item_course):  # noqa
                flash_changes = "No changes made to {} .".format(item_name)
            else:
                flash_changes = "Changes saved successfully"
        else:
            flash_changes = "Changes saved successfully!"

        q.item_edit(res_id, menu_id, item_name,
                    item_price, item_desc, item_course)
        flash(flash_changes)
        return redirect(url_for('menu', res_id=res_id))

    res_name = q.res_name(res_id)
    res_menu_data = q.item_data_p(res_id, menu_id)
    return render_template('edit_menu.html', res_id=res_id, menu_id=menu_id,
                           res_name=res_name, res_menu_data=res_menu_data)


# Code for deleting a menu item
@app.route('/restaurants/<int:res_id>/menu/<int:menu_id>/delete/', methods=['GET', 'POST'])  # noqa
def deleteMenuItem(res_id, menu_id):
    if 'username' not in login_session:
        return redirect('/login')
    item_owner = q.item_owner_id(res_id, menu_id)
    if(item_owner != login_session['user_id']):
        return "Access Denied"

    if(request.method == "POST"):
        item_name = q.item_data_p(res_id, menu_id).name
        q.item_delete(res_id, menu_id)
        flash("{} removed.".format(item_name))

        return redirect(url_for('menu', res_id=res_id, menu_id=menu_id))
    res_name = q.res_name(res_id)
    item_name = q.item_data_p(res_id, menu_id).name
    return render_template('delete_menu.html', res_name=res_name,
                           item_name=item_name, res_id=res_id, menu_id=menu_id)

# JSON Routes ---
# Nothing too fancy here, users who aren't logged in
# Cannot access the endpoints


@app.route('/restaurants/<int:res_id>/menu/JSON')
def res_menu_JSON(res_id):
    if('username' not in login_session):
        return redirect('/login')
    item_data = q.item_data(res_id)
    return jsonify(MenuItem=[item.serialize for item in item_data])


@app.route('/restaurants/JSON')
def res_JSON():
    if('username' not in login_session):
        return redirect('/login')
    res_data = q.res_data()
    return jsonify(Restaurant=[res.serialize for res in res_data])


@app.route('/restaurants/<int:res_id>/menu/<int:menu_id>/JSON')
def res_menu_p_JSON(res_id, menu_id):
    if('username' not in login_session):
        return redirect('/login')
    item_data = q.item_data_p(res_id, menu_id)
    return jsonify(MenuItem=[item_data.serialize])

if(__name__ == "__main__"):
    app.debug = True
    app.run(host="0.0.0.0", port=5000)
