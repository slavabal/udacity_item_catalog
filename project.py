#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
from app_globals import *
from models import Base, Item, Category

from flask import Flask, jsonify, request, url_for, abort, g
from flask import render_template, redirect, flash
from flask import session as login_session, make_response

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import joinedload, relationship, sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.orm.exc import NoResultFound

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

import httplib2
import random
import string
import json
import requests

#
# DB Connectivity Code
#
engine = create_engine(DB_PATH)
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
app = Flask(__name__)

#
# Managing Authentication Code
#  The following blocks of code related to Google login implementation
#  are coming from "Servers, Authorization, and CRUD" Udacity course
#  projects with a little adjustments for this project's requirements
#


@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'testing':
            del login_session['username']
            flash("You have successfully been logged out.", category="info")
            return redirect(url_for('showCatalog'))
        elif login_session['provider'] == 'google':
            gdisconnect()
            flash("You have successfully been logged out.", category="info")
            return redirect(url_for('showCatalog'))
    else:
        flash("You were not logged in", category="success")
        return redirect(url_for('showCatalog'))

# Login requests
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)

# Google Authentication
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
    print("label4")
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
                    json.dumps('Current user is already connected.'), 200)
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
    login_session['email'] = data['email']
    login_session['provider'] = 'google'
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    flash("You are now logged in as %s"
          % login_session['username'], "success")
    return output


# Google authentication disconnect
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print('Access Token is None')
        response = make_response(
                json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print('In gdisconnect access token is %s', access_token)
    print('User name is: ')
    print(login_session['username'])
    url = 'https://accounts.google.com/o/oauth2/revoke?'\
        'token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print('result is ')
    print(result)
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(
                    json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response
#
# Managing Catalog Code
#

# Landing page - show catalog and recent items
@app.route("/")
@app.route("/catalog")
def showCatalog():
    categories = session.query(Category).all()
    latestItems = session.query(Item.title, Item.id,
                                Category.name.label("category_name")).join(
                    Category).order_by(Item.id.desc()).limit(
                    SHOW_NUMBER_OF_LATEST_ITEMS).all()
    if 'username' not in login_session:
        return render_template('public_catalog.html',
                               categories=categories, items=latestItems)
    else:
        return render_template('catalog.html',
                               categories=categories, items=latestItems)

# Show items for selected category
@app.route("/catalog/<category>/items")
def getCategoryItems(category):
    currentCategory = session.query(Category).filter_by(name=category).one()
    categories = session.query(Category).all()
    items = session.query(Item.title, Item.id).join(
            Category).filter(Category.id == currentCategory.id).order_by(
            Item.title).all()
    return render_template('category.html', categories=categories,
                           items=items, currentCategory=currentCategory)

# Show specific item in the category
@app.route("/catalog/<category>/<item>")
def getCategoryItem(category, item):
    currentCategory = []
    currentItem = []
    try:
        currentCategory = session.query(
                        Category).filter_by(name=category).one()
        currentItem = session.query(Item).filter_by(title=item).one()
        # handle case when item is not found or item does not belong
        # to that category
        if currentItem.category_id == currentCategory.id:
            if 'username' not in login_session:
                return render_template('public_item.html', item=currentItem)
            else:
                return render_template('item.html', item=currentItem)
        else:
            flash("Item '%s' does not match '%s' category" % (item, category),
                  category="warning")
            return redirect(url_for('showCatalog'))
    except NoResultFound:
        if currentCategory == []:
            flash("Category '%s' not found" % category, category="warning")
            return redirect(url_for('showCatalog'))
        else:
            flash("Item '%s' not found" % item, category="warning")
            return redirect(url_for('showCatalog'))

# Add new item
@app.route("/catalog/items/new", methods=['GET', 'POST'])
def newItem():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        title = "newItem"
        cat_id = -1
        description = ""
        if request.form['title']:
            title = request.form['title']
        if request.form['description']:
            description = request.form['description']
        if request.form['category']:
            cat_id = request.form['category']
        try:
            newItem = Item(title=title, description=description,
                           category_id=cat_id)
            session.add(newItem)
            session.commit()
            flash('Item %s successfully created' % title, category="success")
        except SQLAlchemyError:
            flash('Failed to create %s item' % title, category="danger")
        return redirect(url_for('showCatalog'))
    else:
        categories = session.query(Category).all()
        return render_template('newItem.html', categories=categories)

# Edit item
@app.route("/catalog/<item>/edit", methods=['GET', 'POST'])
def editItem(item):
    if 'username' not in login_session:
        return redirect('/login')
    try:
        editedItem = session.query(Item).filter_by(title=item).one()
        categories = session.query(Category).all()
        if request.method == 'POST':
            if request.form['title']:
                editedItem.title = request.form['title']
            if request.form['description']:
                editedItem.description = request.form['description']
            else:
                editedItem.description = ""
            if request.form['category']:
                editedItem.category_id = request.form['category']
            try:
                session.add(editedItem)
                session.commit()
                flash('Item %s successfully updated' % item,
                      category="success")
            except SQLAlchemyError:
                flash('Failed to update %s item' % item, category="danger")
            return redirect(url_for('showCatalog'))
        else:
            return render_template('editItem.html', item=editedItem,
                                   categories=categories)
    except NoResultFound:
        flash('Item %s not found' % item, category="warning")
        return redirect(url_for('showCatalog'))

# Delete item
@app.route("/catalog/<item>/delete", methods=['GET', 'POST'])
def deleteItem(item):
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        try:
            itemToDelete = session.query(Item).filter_by(title=item).one()
            session.delete(itemToDelete)
            session.commit()
            flash('Item %s successfully deleted' % itemToDelete.title,
                  category="success")
        except NoResultFound:
            flash('Item %s not found' % itemToDelete.title, category="warning")
        return redirect(url_for('showCatalog'))
    else:
        return render_template('deleteItem.html', item=item)

# Return catalog as JSON
@app.route("/catalog/catalog.json")
def getCatalogJSON():
    if 'username' not in login_session:
        return redirect('/login')
    categories = session.query(Category).options(
                joinedload(Category.items)).all()
    return jsonify(Category=[dict(c.serialize,
                                  Item=[i.serialize for i in c.items])
                             for c in categories])


# Main
if __name__ == '__main__':
    app.debug = True
    app.config['SECRET_KEY'] = ''.join(random.choice(
        string.ascii_uppercase + string.digits) for x in xrange(32))
    app.run(host=APP_HOST, port=APP_PORT)
