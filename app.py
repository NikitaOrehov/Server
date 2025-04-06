from flask import Flask, jsonify, request
import psycopg2
from urllib.parse import urlparse
import os

app = Flask(__name__)



DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://kinro:FBIYZJrnNRSBP9q0yeHGvr8iCKa8K9wk@dpg-cvp6c8idbo4c73bb9hk0-a.oregon-postgres.render.com/data_h57p') 

url = urlparse(DATABASE_URL)
dbname = url.path[1:]
user = url.username
password = url.password
host = url.hostname
port = url.port


try:
    conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)

except psycopg2.Error as e:
    print(f"Error connecting to or interacting with the database: {e}")



@app.route('/')
def hello_world():
    return 'Hello from Render!'

@app.route('/api/data', methods=['GET', 'POST'])
def get_data():
    if request.method == 'GET':
        data = {'message': 'This is data from the Render server!'}
        return jsonify(data)
    elif request.method == 'POST':
        data = request.get_json()
        print(f"Received {data}")
        return jsonify({'status': 'success', 'message': 'Data received!'})

@app.route('/api/data/user/login/<login>', methods=['GET'])
def get_password(login):
    try:
        curs = conn.cursor()
        curs.execute("SELECT password FROM users WHERE login = %s", (login,))
        password = curs.fetchone()

        curs.close()

        if password:
            return jsonify({'password': password[0]})
        else:
            return jsonify({'error': 'User not found'}), 403

    except psycopg2.Error as e:
        print(f"Database query error: {e}")
        return jsonify({'error': 'Database error'}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
