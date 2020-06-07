import socket

"""
This class is used as a sort of channel. Client.py uses it to talk to server.
Server is it's own beast.

Note to self: TCP GUARANTEES delivery. This is very useful/good.
Also it has guaranteed order.
"""
class Channel:
    def __init__(self, server_ip, server_port):
        # followed a tutorial and I think I might change the structure a bit
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = server_ip
        self.port = server_port
        self.id = self.connect()

    def connect(self):
        try:
            self.client.connect((self.server, self.port))
        except Exception as exc:
            print('Failed to Connect, exception information below.')
            print(str(exc))
        return self.client.recv(2048).decode(encoding='utf-8')
    
    def quit(self):
        self.client.close()
    
    def send(self, datas):
        for data in datas:
            try:
                self.client.send(data.encode(encoding='utf-8')) # data is a string lul
            except socket.error as err:
                print(err)
            return self.client.recv(2048).decode()