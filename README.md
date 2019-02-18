# Item Catalog Project
## Purpose
Udacily Full Stack Web Developer Nanodegree Program project #2 by [Slava Balashov](mailto:slavabal@gmail.com ).

## Description
This project implements a web site for managing items in the catalog with an API endpoint that provides Catalog content on JSON format.
The project utilizes Flask framework with SQLAlchemy on SQLite DB.

The project provides CRUD functionaliaty for managing items for loggen in users and readonly access for not-loggedin users.

Third party (Google) authentication & autorization service is used instead of implenenting it's own authentication & authorization spec.

## Prerequisites and configuration

### Application settings

- `app_globals.py` file contains settings for Flask `APP_HOST` and `APP_PORT` to run the application on. 
The default settings are:
`APP_PORT = 5000`
`APP_HOST = '0.0.0.0'`

- `DB_PATH` specifies Database name for the application

- `SHOW_NUMBER_OF_LATEST_ITEMS` specifies the number of recent items to show on the top catalog page

- `CLIENT_ID` specifies the value for Google OAUTH. See below 

### The Database setup
- This project provides `db_content_init.py` file to restage database content for the testing.
- Execute for following command to purge the database and create new content from scratch including categories and a set of items:
```python
$ python db_content_init.py
```

### Authentication & Authorization Setup
- Authentication and Authorization relies on the code examples provided in the "Servers, Authorization and CRUD" section of the Udacity nanodegree and requires similar setup.
- You need to login into Google Developers console at https://console.developers.google.com/
- create an application
- create credentials for "web application" type providing:
    - Authorized Javascript origins `http://localhost:5000` or your server name & port
    - Authorized redirect URIs
        - `http://localhost:5000/gconnect` and
        - `http://localhost:5000/login`
- download JSON file, rename it to `client_secrets.json` and place it into the project folder
- place your Client ID value in the `data-clientid="..."` line of the `login.html` file
- Note: `client_secrets.json` provided with the project have private data removed. Your `Client ID` and `Client Secret` values must be provided for this file to work.

## Running the Project
- Start for server
    ```python
    $ python project.py
    ```
- Open your browser to http://localhost:5000 for the project home page

## Expected Behavior
- "Home" / "Item Catalog App" link always shows in the top left corner and takes you to the home page
- Login / Logout button in the top right allows for the used to login or to disconnect
### Not-logged-in mode
- Home page 
    - shows list of categories on the left and list of the recently added items on the right
    - items have names of the categories they belong to next to them
    - Items are clickable and take you to the item page 
    - Categories are clickable and take you to the Category page.

- Item page
    - shows item description and OK button to go back to the Catalog page

- Category page
        - Current Category is selected on the left
        - Items in the current category are listed on the right
        - number of items in the category is shown in next to the category name on the right side
        - items are clickable and take you to the item page

- Login button
    - takes you to the login page with the link to currently available OAUTH provuders (currently only Google SignIn button is available)
    - After clicking on Google signin button another window opens up and allows user to login using Google account
    - "success" flash message with the user name shows if login was successful 
    - that takes the system to the "logged in" mode

### Logged-in mode
- Home page 
    - Same as withon login, but with two additional buttons at the bottom of the categories list:
        - `Add new item` takes you to the screen to add new item
        - `JSON` (download) - returns the entire catalog as JSON 

- Item page
    - shows item description and OK button to go back to the Catalog page
    - Edit button takes you to the screen where item properties can be adjusted. current category is selected in the list of categories.
    - Delete button takes to the prompt for removing item from the Database.
    note: you can rerun `db_content_init.py` to recreate original set of items and categories.

- Category page
        - same as for non-logged in mode

- Logout button
    - disconnects / logs out the user 
    - takes the system to the "non-logged-in" mode



