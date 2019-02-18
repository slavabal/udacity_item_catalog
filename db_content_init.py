#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

#
# This code reinitializes project database.
# all existing categories/items records are removed
# and the new ones are created from scratch
#

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app_globals import DB_PATH
from models import Category, Item, Base

engine = create_engine(DB_PATH)

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

print("Removing all items...")
session.query(Item).delete()
session.commit()
print("Removing all categories...")
session.query(Category).delete()
session.commit()

print("Creating categories...")
category1 = Category(name="Soccer")
category2 = Category(name="Basketball")
category3 = Category(name="Baseball")
category4 = Category(name="Frisbee")
category5 = Category(name="Snowboarding")
category6 = Category(name="Rock Climbing")
category7 = Category(name="Foosball")
category8 = Category(name="Hockey")
session.add(category1)
session.add(category2)
session.add(category3)
session.add(category4)
session.add(category5)
session.add(category6)
session.add(category7)
session.add(category8)
session.commit()

print("Creating items...")
item1 = Item(title="Goggles", description="""Lorem ipsum dolor sit amet,
            consectetur adipisicing elit, sed do eiusmod tempor incididunt
            ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis
            nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
            consequat.""", category=category5)
item2 = Item(title="Snowboard", description="""Lorem ipsum dolor sit amet,
            consectetur adipisicing elit, sed do eiusmod tempor incididunt
            ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis
            nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
            consequat.""", category=category5)
session.add(item1)
session.add(item2)
session.commit()

# Add multiple items for long lists debugging
for x in range(50):
    item2 = Item(title="test %s" % x,
                 description="""Lorem ipsum dolor sit
        amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt
        ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud
        exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
        """, category=category2)
    session.add(item2)
    session.commit()
