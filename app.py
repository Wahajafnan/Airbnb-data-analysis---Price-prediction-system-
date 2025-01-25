from flask import Flask, render_template, request, jsonify
import mysql.connector
from mysql.connector import Error
import logging
app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)
def connect_db():
    try:
        connection = mysql.connector.connect(
            host="127.0.0.1",
            user="root",  
            password="admin", 
            database="ab" 
        )
        return connection
    except Error as e:
        logging.error(f"Error connecting to the database: {e}")
        return None
@app.route('/')
def index():
    conn = connect_db()
    if conn is None:
        return "Error connecting to the database.", 500
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT DISTINCT neighbourhood_group FROM project")
    neighbourhood_groups = [row['neighbourhood_group'] for row in cursor.fetchall()]
    cursor.execute("SELECT DISTINCT room_type FROM project")
    room_types = [row['room_type'] for row in cursor.fetchall()]
    conn.close()
    return render_template('index.html', neighbourhood_groups=neighbourhood_groups, room_types=room_types)
@app.route('/get_neighbourhoods', methods=['POST'])
def get_neighbourhoods():
    neighbourhood_group = request.json.get('neighbourhood_group')
    conn = connect_db()
    if conn is None:
        return jsonify([])
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT DISTINCT neighbourhood FROM project WHERE neighbourhood_group = %s", (neighbourhood_group,))
    neighbourhoods = [row['neighbourhood'] for row in cursor.fetchall()]
    conn.close()
    return jsonify(neighbourhoods)
@app.route('/search', methods=['POST'])
def search():
    neighbourhood_group = request.form.get('neighbourhood_group')
    neighbourhood = request.form.get('neighbourhood')
    room_type = request.form.get('room_type')
    conn = connect_db()
    if conn is None:
        return "Error connecting to the database.", 500
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM project WHERE neighbourhood_group = %s AND neighbourhood = %s AND room_type = %s ORDER BY price ASC"
    params = (neighbourhood_group, neighbourhood, room_type)
    logging.debug(f"Executing query: {query} with params {params}")
    cursor.execute(query, params)
    results = cursor.fetchall()
    logging.debug(f"Results fetched: {results}")
    conn.close()
    return render_template('results.html', results=results, neighbourhood=neighbourhood, room_type=room_type)
@app.route('/filter_by_price', methods=['GET'])
def filter_by_price():
    price_min = request.args.get('price_min')
    price_max = request.args.get('price_max')
    neighbourhood = request.args.get('neighbourhood')
    room_type = request.args.get('room_type')
    conn = connect_db()
    if conn is None:
        return "Error connecting to the database.", 500
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM project WHERE neighbourhood = %s AND room_type = %s"
    params = [neighbourhood, room_type]
    if price_min:
        query += " AND price >= %s"
        params.append(price_min)
    if price_max:
        query += " AND price <= %s"
        params.append(price_max)
    query += " ORDER BY price ASC"
    logging.debug(f"Executing query for price filter: {query} with params {params}")
    cursor.execute(query, params)
    results = cursor.fetchall()
    logging.debug(f"Filtered results: {results}")
    conn.close()
    return render_template('results.html', results=results, neighbourhood=neighbourhood, room_type=room_type)
if __name__ == '__main__':
    app.run(debug=True)