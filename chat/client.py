from cryptography.fernet import Fernet
import sys
import socket
import select
import errno
import threading

class MoleClient:

    def __init__(self, ip="127.0.0.1", port=1234, header_length=10, physical_key_file="./PHYSICAL_KEY", encoding="utf8"):
        self.ip = ip
        self.port = port
        self.header_length = header_length
        self.encoding = encoding

        self.fernet = None
        with open(physical_key_file) as f:
            key = f.readline().encode(self.encoding)
            self.fernet = Fernet(key)

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.ip, self.port))
        self.client_socket.setblocking(True)

        self.username = input("Username: ")

        self.raw_send(self.username)

    def raw_send(self, data, encrypt=False):
        data = data.encode(self.encoding)
        if encrypt:
            data = self.fernet.encrypt(data)
        header = f"{len(data):<{self.header_length}}".encode(self.encoding)
        self.client_socket.send(header + data)

    def raw_recv(self, decrypt=False):
        header = self.client_socket.recv(self.header_length)
        if not len(header):
            print("MOLE: Connection closed by the server!")
            sys.exit()

        data_lenght = int(header.decode(self.encoding).strip())
        data = self.client_socket.recv(data_lenght)
        if decrypt:
            data = self.fernet.decrypt(data)

        return data.decode(self.encoding)

    def sending(self):
        while True:
            message = input(f"{self.username} > ")

            if message:
                self.raw_send(message)

    def recieving(self):
        while True:
            try:
                while True:
                    user = self.raw_recv()
                    message = self.raw_recv()

                    print()
                    print(f"{user} > {message}")
            except IOError as e:
                if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                    print("MOLE: reading error!", str(e))
                    sys.exit()
                continue
            except Exception as e:
                print("MOLE: general error!", str(e))
                sys.exit()

if __name__ == "__main__":
    client = MoleClient()

    sender = threading.Thread(target=client.sending)
    reciever = threading.Thread(target=client.recieving)

    sender.start()
    reciever.start()