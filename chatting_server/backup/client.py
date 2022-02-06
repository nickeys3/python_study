from http import client
import socket
import select
import errno
import sys
import threading

HEADER_LENGTH = 10
IP = "127.0.0.1"
PORT = 8080

class Client:
    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((IP, PORT))
        self.client_socket.setblocking(False)

        self.my_username = input("Username: ")
        username = self.my_username.encode('utf-8')
        self.username_header = f"{len(username):<{HEADER_LENGTH}}".encode('utf-8')
        
        self.client_socket.send(self.username_header + username)

        self.thread = threading.Thread(target=self.sendMsg)
        self.thread.daemon = True

    def run(self):
        self.thread.start()

        while True:
            try:
                while True: # receive things
                    username_header = self.client_socket.recv(HEADER_LENGTH)
                    if not len(username_header):
                        print("connection closed by the server")
                        sys.exit()

                    username_length = int(username_header.decode('utf-8').strip())
                    username = self.client_socket.recv(username_length).decode('utf-8')

                    message_header = self.client_socket.recv(HEADER_LENGTH)
                    message_length = int(message_header.decode('utf-8').strip())
                    message = self.client_socket.recv(message_length).decode('utf-8')

                    print("\r" + f"{username} > {message}")
                    sys.stdout.flush()
                    print(f"{self.my_username} > ", end='')
                    sys.stdout.flush()

            except IOError as e:
                if e.errno != errno.EAGAIN or e.errno != errno.EWOULDBLOCK:
                    print('Reading error', str(e))
                    sys.exit()
                continue

            except Exception as ge:
                print('General error', str(ge))
                sys.exit()

    def sendMsg(self):
        while True:
            message = input(f"{self.my_username} > ")

            if message:
                message = message.encode('utf-8')
                message_header = f"{len(message) :< {HEADER_LENGTH}}".encode('utf-8')
                self.client_socket.send(message_header + message)

client = Client()
client.run()