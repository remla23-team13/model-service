import sqlite3
import json

conn = sqlite3.connect('restaurant.db')

cursor = conn.cursor()

# create table restaurants if not exists
cursor.execute("""
    CREATE TABLE IF NOT EXISTS restaurants (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT NOT NULL
    )
""")

## insert restaurants
cursor.execute("""
    INSERT INTO restaurants (name, description)
    VALUES ('KFC',
    'Fried Chicken')
""")

cursor.execute("""
    INSERT INTO restaurants (name, description)
    VALUES ('Maccas',
    'shitty fast food')
""")

cursor.execute("""
    INSERT INTO restaurants (name, description)
    VALUES ('Burgy',
    'shitty fast food again')
""")


# create table reviews if not exists
cursor.execute("""
    CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        restaurant_id INTEGER,
        description TEXT NOT NULL,
        FOREIGN KEY (restaurant_id) REFERENCES restaurants (id)
    )
""")

cursor.execute("""
    INSERT INTO reviews (restaurant_id, description)
    VALUES (1,
    'I love KFC')
""")

cursor.execute("""
    INSERT INTO reviews (restaurant_id, description)
    VALUES (1,
    'I hate KFC')
""")

cursor.execute("""
    INSERT INTO reviews (restaurant_id, description)
    VALUES (2,
    'I love Maccas')
""")
cursor.execute("""
    INSERT INTO reviews (restaurant_id, description)
    VALUES (2,
    'I hate Maccas')
""")

def get_restaurant(restaurant_id):
    cursor.execute("SELECT * FROM restaurants WHERE id=?", (restaurant_id,))
    restaurant = cursor.fetchone()
    columns = [column[0] for column in cursor.description]  # Get the column names from the cursor
    restaurant_json = {}
    for i, value in enumerate(restaurant):
        restaurant_json[columns[i]] = value
    return restaurant_json

def get_restaurants():
    cursor.execute("SELECT * FROM restaurants")
    restaurants = cursor.fetchall()
    columns = [column[0] for column in cursor.description]  # Get the column names from the cursor
    restaurants_json = []
    for restaurant in restaurants:
        restaurant_json = {}
        for i, value in enumerate(restaurant):
            restaurant_json[columns[i]] = value
        restaurants_json.append(restaurant_json)
    return restaurants_json


def get_reviews(restaurant_id):
    #retrieve the name of the restaurant
    cursor.execute("SELECT name FROM restaurants WHERE id=?", (restaurant_id,))
    restaurant_name = cursor.fetchone()[0]
    cursor.execute("SELECT * FROM reviews WHERE restaurant_id=?", (restaurant_id,))
    reviews = cursor.fetchall()
    columns = [column[0] for column in cursor.description]  # Get the column names from the cursor
    reviews_json = []
    for review in reviews:
        review_json = {}
        for i, value in enumerate(review):
            review_json[columns[i]] = value
        reviews_json.append(review_json)
    return dict(restaurant_name=restaurant_name, reviews=reviews_json)

def insert_review(restaurant_id, description):
    cursor.execute("""
        INSERT INTO reviews (description, restaurant_id)
        VALUES (?, ?)
    """, (description, restaurant_id))
    conn.commit()


