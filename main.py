from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse
import urllib.request
import mimetypes
import pathlib
import socket
import threading
import json
from datetime import datetime

class HttpHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)

        if pr_url.path == '/':
            self.send_html_file('front-init/index.html')
        elif pr_url.path == '/message':
            self.send_html_file('front-init/message.html')
        else:
            if pathlib.Path().joinpath(pr_url.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file('front-init/error.html', 404)

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as fd:
            self.wfile.write(fd.read())

    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", 'text/plain')
        self.end_headers()
        with open(f'.{self.path}', 'rb') as file:
            self.wfile.write(file.read())

    def do_POST(self):
        data = self.rfile.read(int(self.headers['Content-Length']))
        client_run(data, 'localhost', 5000)
        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()

def socket_run():
    server_socket_form = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket_form.bind(('localhost', 5000))

    try:
        while True:
            data, address_port = server_socket_form.recvfrom(1024)
            print(data, address_port)
            print(f'Received data: {data.decode()} from: {address_port}')
            data_parse = urllib.parse.unquote_plus(data.decode())
            now = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S.%f")
            data_dict = {key: value for key, value in [el.split('=') for el in data_parse.split('&')]}
            res_dict = {}
            res_dict[now] = data_dict
            with open(r'front-init/storage/data.json', 'a') as file:
                json.dump(res_dict, file)
                file.write(',\n')

    except KeyboardInterrupt:
        print(f'Destroy server')
    finally:
        server_socket_form.close()
        print("Socket port 5000 finally closed.")

def client_run(data, ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server = ip, port
    sock.sendto(data, server)
    print(f'Send data: {data.decode()} to server: {server}')
    sock.close()
    print("Client socket closed")

def run(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = ('', 3000)
    http_serv = server_class(server_address, handler_class)
    try:
        http_serv.serve_forever()
    except KeyboardInterrupt:
        http_serv.server_close()

def run_thread():
    http_server_thread = threading.Thread(target=run, args=(), daemon=True)
    socket_server_thread = threading.Thread(target=socket_run, args=(), daemon=True)
    socket_server_thread.start()
    http_server_thread.start()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Stopping threads...")

if __name__ == '__main__':
    run_thread()