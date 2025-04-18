import array
from http.client import FAILED_DEPENDENCY
from flask import Flask, jsonify, request, render_template,  jsonify
import psycopg2
from urllib.parse import urlparse
import os
import socket
import threading

from psycopg2.sql import NULL

app = Flask(__name__)


HOST = '0.0.0.0'
HTTP_PORT = 8000
TCP_PORT = 65432

tcp_clients = []
tcp_client_addresses = {}



DATABASE_URL = os.environ.get('DATABASE_URL') 

url = urlparse(DATABASE_URL)
dbname = url.path[1:]
user = url.username
password = url.password
host = url.hostname
port = url.port


try:
    conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
    print("connect to database successly")

except psycopg2.Error as e:
    print(f"Error connecting to or interacting with the database: {e}")

print("Hello from code")



def handle_tcp_connection(conn, addr):
    print(f"connect TCP client: {addr}")
    tcp_clients.append(conn)
    tcp_client_addresses[conn] = addr

    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            message = data.decode()
            print(f"Received from {addr}: {message}")

            for client in tcp_clients:
                    try:
                        client.sendall(data)
                    except:
                        remove_tcp_client(client)

    except Exception as e:
        print(f"Error in process TCP client {addr}: {e}")
    finally:
        remove_tcp_client(conn)
        print(f"TCP client {addr} disconnect")


def remove_tcp_client(client):
    if client in tcp_clients:
        tcp_clients.remove(client)
        del tcp_client_addresses[client]

        #hello


def start_tcp_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, TCP_PORT))
        s.listen()
        print(f"TCP server listen on {HOST}:{TCP_PORT}")

        while True:
            conn, addr = s.accept()
            thread = threading.Thread(target=handle_tcp_connection, args=(conn, addr))
            thread.daemon = True
            thread.start()




@app.route('/')
def hello_world():
    return 'Hello from Render!'

@app.route('/api/data', methods=['GET', 'POST'])
def get_data():
    print("get data")
    if request.method == 'GET':
        data = {'message': 'This is data from the Render server!'}
        return jsonify(data)
    elif request.method == 'POST':
        data = request.get_json()
        print(f"Received {data}")
        return jsonify({'status': 'success', 'message': 'Data received!'})

@app.route('/api/data/user/login/<login>', methods=['GET'])
def get_password(login):
    print("get password")
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

@app.route('/api/data/user/info/<login>', methods=['GET', 'POST'])
def info(login):
    if request.method == 'GET':
        try:
            curs = conn.cursor()
            curs.execute("SELECT u.name, u.surname, u.databirth, u.phone, u.location, u.exp_alc, u.record, u.id, u.fav_alc, c.linex, c.liney, c.histogramma, c.circules FROM users u RIGHT JOIN charts c ON u.id = c.id WHERE u.login = %s;", (login,))
            res = curs.fetchone()
            answer = {
                'name': res[0].strip(),
                'surname': res[1].strip(),
                'databirth': res[2],
                'phone': res[3],
                'location': res[4],
                'exp_alc': res[5], 
                'record': res[6],
                'fav_alc' : res[8],
                'login' : login,
                'linex' : res[9],
                'liney' : res[10],
                'histogramma' : res[11],
                'circules' : res[12],
                'id' : res[7]
                }
            _id = res[7]
            curs.execute("SELECT pred FROM PREDILECTION WHERE id = %s", (_id,))
            res = curs.fetchall()
            predilection = [i[0].strip() for i in res]
            answer['pred'] = predilection
            curs.execute("SELECT event FROM achievements WHERE id = %s", (_id,))
            res = curs.fetchall()
            achievements = [i[0].strip() for i in res]
            answer['achiev'] = achievements
            curs.execute('SELECT * FROM chats WHERE id_person_1 = %s OR id_person_2 = %s', (_id, _id))
            res = curs.fetchall()
            chats = {}
            for i in res:
                print("number chat: %s", i[0])
                chat = []
                chat.append(i[1])
                chat.append(i[2])
                curs.execute('SELECT id_message, id_send, text, data FROM message WHERE id_chat = %s', (i[0],))
                messages = curs.fetchall()
                for j in messages:
                    print("message: %s", j)
                    chat.append(j)
                chats[i[0]] = chat
            answer['chats'] = chats

            return answer
        except psycopg2.Error as e:
            print(f"Database query error: {e}")
            return jsonify({'error': 'Database error'}), 500
    if request.method == 'POST':
        data = request.get_json()
        try:
            curs = conn.cursor()
            date = data.get('databirth')
            exp_alc = data.get('exp_alc')
            record = data.get('record')
            if date == "":
                date = None
            if record == "":
                record = None
            if exp_alc == "":
                exp_alc = None
            arrayPred = data.get('pred')
            arrayAchiev = data.get('achiev')
            curs.execute("SELECT id FROM users WHERE login = %s", (login, ))
            _id = curs.fetchone()[0]           
            curs.execute("UPDATE users SET name = %s, surname = %s, login = %s, phone = %s, location = %s, exp_alc = %s, record = %s, fav_alc = %s WHERE login = %s", 
                         (data.get('name'), data.get('surname'), data.get('login'), data.get('phone'), data.get('location'), data.get('exp_alc'), record, data.get('fav_alc'), login))                                     
            curs.execute("DELETE FROM predilection WHERE id = %s", (_id, ))
            curs.execute("INSERT INTO predilection (id, pred) VALUES (%s, %s), (%s, %s), (%s, %s), (%s, %s)", (_id, arrayPred[0], _id, arrayPred[1], _id, arrayPred[2], _id, arrayPred[3]))
            curs.execute("DELETE FROM achievements WHERE id = %s", (_id, ))
            curs.execute("INSERT INTO achievements (id, event) VALUES (%s, %s), (%s, %s), (%s, %s), (%s, %s)", (_id, arrayAchiev[0], _id, arrayAchiev[1], _id, arrayAchiev[2], _id, arrayAchiev[3]))
            conn.commit()
            return jsonify({'er' : 'ok'})
        except psycopg2.Error as e:
            print(f"Database query error: {e}")
            return jsonify({'error': 'Database error'}), 500




if __name__ == '__main__':
    tcp_thread = threading.Thread(target=start_tcp_server)
    tcp_thread.daemon = True
    tcp_thread.start()

    print(f"Flask HTTP server listen on {HOST}:{HTTP_PORT}")

    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port, use_reloader=False)
