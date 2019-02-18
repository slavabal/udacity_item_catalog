#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import json
#
# Gobal application settings
#
SHOW_NUMBER_OF_LATEST_ITEMS = 10

# Database Name
DB_PATH = 'sqlite:///ItemCatalog.db'

# Flash Address and Port to run on
APP_PORT = 5000
APP_HOST = '0.0.0.0'

# google API keys - requires json file in the current folder
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
