import socket

"""
This class is used exclusively by client.py
"""
class Network:
    def __init__(self):
        # followed a tutorial and I think I might change the structure a bit
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = "10.0.0.211"
        self.port = 5555
        self.id = self.connect()

    def connect(self):
        try:
            self.client.connect((self.server, self.port))
        except Exception as exc:
            print("Failed to Connect, exception information below.")
            print(str(exc))
        return self.client.recv(2048).decode(encoding="utf-8")
    
    def quit(self):
        self.client.close()
    
    def send(self, data):
        try:
            self.client.send(data.encode(encoding="utf-8")) # data is a string lul
        except socket.error as err:
            print(err)
        return self.client.recv(2048).decode()