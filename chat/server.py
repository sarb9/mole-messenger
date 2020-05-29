import socket
import select

class MoleServer:

    def __init__(self, ip="127.0.0.1", port=1234, header_length=10):
        self.port = port
        self.ip = ip
        self.header_length = header_length

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.ip, self.port))
        self.server_socket.listen()

        self.sockets_list = [self.server_socket]

        self.clients = {}

    def recieve_message(self, client_socket):
        try:
            message_header = client_socket.recv(self.header_length)

            if not len(message_header):
                return False
            message_lenght = int(message_header.decode("utf-8").strip())
            return {"header": message_header, "data": client_socket.recv(message_lenght)}
        except:
            raise IOError("Could not read from input buffer.")
            return False

    def run(self):
        while True:
            print("here")
            read_sockets, _, exception_sockets = select.select(self.sockets_list, [], self.sockets_list)

            for notified_socket in read_sockets:
                if notified_socket == self.server_socket:
                    client_socket, client_address = self.server_socket.accept()

                    user = self.recieve_message(client_socket)
                    if not user:
                        continue

                    self.sockets_list.append(client_socket)
                    self.clients[client_socket] = user
                    print(f"Accepted new connection from {client_address[0]}:{client_address[1]} username: {user['data'].decode('utf8')}")

                else:
                    message = self.recieve_message(notified_socket)
                    if not message:
                        print(f"Closed connection from client {self.clients[notified_socket]['data'].decode('utf8')}")
                        self.sockets_list.remove(notified_socket)
                        del self.clients[notified_socket]
                        continue

                    user = self.clients[notified_socket]
                    print(f"recieved message from {user['data'].decode('utf8')}: {message['data'].decode('utf8')}")

                    for client_socket in self.clients:
                        if client_socket != notified_socket:
                            client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])

            for notified_socket in exception_sockets:
                self.sockets_list.remove(notified_socket)
                print(f"Closed connection from client {self.clients[notified_socket]['data'].decode('utf8')} because of exception.")
                del self.clients[notified_socket]

if __name__ == "__main__":
    server = MoleServer()
    server.run()

