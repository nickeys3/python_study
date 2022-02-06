import socket
import select # for IO multiflexing

HEADER_LENGTH = 10
IP = "127.0.0.1"
PORT = 8080

class Server:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sockets_list = [server_socket]
        clients = {}

        def __init__(self):
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #
            self.server_socket.bind((IP, PORT))
            self.server_socket.listen()

        def receive_message(self, client_socket):
            try:
                message_header = client_socket.recv(HEADER_LENGTH) # receive a header from the client

                if  not len(message_header):
                    return False

                message_length = int(message_header.decode("utf-8").strip()) # the read header is length of the message which is gonna be recevied.

                return {"header": message_header, "data": client_socket.recv(message_length)} # return message w/ header after reading the msg.
            except:
                return False
        def run(self):
            while True:
                read_sockets, _, exception_sockets = select.select(self.sockets_list, [], self.sockets_list) # '_' means "I don't care" about sockets for write
                
                for notified_socket in read_sockets:
                    if notified_socket == self.server_socket: # when someone is connected at first time
                        client_socket, client_address = self.server_socket.accept() # read the client information
                        user = self.receive_message(client_socket)
                        if user is False:
                            continue

                        self.sockets_list.append(client_socket) # 
                        self.clients[client_socket] = user # Add the user message

                        print(f"Accepted new connection from {client_address[0]}:{client_address[1]} username: {user['data'].decode('utf-8')}")

                    else: # when someone sends a message
                        message = self.receive_message(notified_socket)
                        if message is False:
                            print(f"Closed connection from {self.clients[notified_socket]['data'].decode('utf-8')}")
                            self.sockets_list.remove(notified_socket)
                            del self.clients[notified_socket]
                            continue

                        user = self.clients[notified_socket]
                        print(f"Received message from {user['data'].decode('utf-8')}: {message['data'].decode('utf-8')}")
                        
                        for client_socket in self.clients: # for all clients
                            if client_socket != notified_socket:
                                client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])

                    for notified_socket in exception_sockets:
                        self.sockets_list.remove(notified_socket)
                        del self.clients[notified_socket]

server = Server()
server.run()