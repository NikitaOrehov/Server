from flask import Flask, jsonify, request
import os

app = Flask(__name__)

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
        # ��������� POST ������� (��������, ���������� ������)
        print(f"Received {data}")
        return jsonify({'status': 'success', 'message': 'Data received!'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Render ����������� ��������� ����
    app.run(debug=False, host='0.0.0.0', port=port)
