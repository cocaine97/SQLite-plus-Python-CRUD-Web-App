# Project  : Item Catalog
___
## Pre-requisite
`Internet Connection is required`
* VM
* Vagrant
* SQLAlchemy
* Bleach
* Flask
**Click [here](https://classroom.udacity.com/nanodegrees/nd004/parts/8d3e23e1-9ab6-47eb-b4f3-d5dc7ef27bf0/modules/bc51d967-cb21-46f4-90ea-caf73439dc59/lessons/5475ecd6-cfdb-4418-85a2-f2583074c08d/concepts/14c72fe3-e3fe-4959-9c4b-467cf5b7c3a0) for a guide to setting up the pre-requisite for the project**
## Installation
* Clone the repo
* The end project is in the branch "flask"
* Run `git checkout flask`
* Run `vagrant up` and `vagrant ssh` on your terminal
* Run `python webserver.py`
* Go to `http://localhost:5000/restaurants` to get started

## Overview
* The server side coding is in the file `webserver.py`.
* Database queries are stored in form of functions in the file `queries.py` for better organized code.
* HTML files are in the `Static` folder
* Website runs on `localhost:5000/restaurants`
* `Create,Update,Delete` operations can only be done while you're logged in.
* App uses `Google OAuth2.0` for authentication

## App Functionalities and Rules
* Only `logged in users` are `allowed` to `Create Restaurant`,`Add item to Restaurants` and access `API Endpoints`
* `Flash Message` show up at `bottom` as a `fixed-navbar`. User can `hide` a `flash message` by `clicking` on it.
* One user can only `Add menu item` to other restaurants. They are `restricted` from `deleting` or `editing` other users `menu items` or `restaurants`.
* A `restaurant owner` may `edit` or `remove` any menu item from his/her `restaurant`

 **There's a `message notification` feature currently available only for the `developer` of this `project`. Try `adding` a `menu item` in the restaurant `DFG` while logged in and the dev will get a message notification on his cell saying "`YOU` added `YOUR_ITEM_NAME` to restaurant `DFG`." !**  

## API Endpoints
* `http://localhost:5000/restaurants/JSON`
* `http://localhost:5000/restaurants/RESTAURANT_ID/menu/JSON`
* `http://localhost:5000/restaurants/RESTAURANT_ID/menu/MENU_ID/JSON`
- - -
