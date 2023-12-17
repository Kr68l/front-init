import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for
import socket
import json

app = Flask(__name__)

static_path = os.path.join(os.path.dirname(__file__), 'static')
app._static_folder = static_path

storage_path = os.path.join(os.path.dirname(__file__), 'storage')
data_file = os.path.join(storage_path, 'data.json')

if not os.path.exists(storage_path):
    os.makedirs(storage_path)
if not os.path.exists(data_file):
    with open(data_file, 'w') as f:
        json.dump({}, f)

UDP_IP = '127.0.0.1'
UDP_PORT = 5000

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/message', methods=['GET', 'POST'])
def message():
    if request.method == 'POST':
        username = request.form['username']
        message_text = request.form['message']

        data = {
            "datetime": str(datetime.now()),
            "username": username,
            "message": message_text
        }
        sock.sendto(json.dumps(data).encode(), (UDP_IP, UDP_PORT))

        return redirect(url_for('index'))

    return render_template('message.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html'), 404


def udp_server():
    while True:
        data, addr = sock.recvfrom(1024)
        message_data = json.loads(data.decode())

        with open(data_file, 'r') as f:
            all_data = json.load(f)

        all_data[message_data['datetime']] = {
            'username': message_data['username'],
            'message': message_data['message']
        }

        with open(data_file, 'w') as f:
            json.dump(all_data, f)


if __name__ == '__main__':
    import threading
    udp_thread = threading.Thread(target=udp_server)
    udp_thread.start()
    app.run(port=3000, debug=True)