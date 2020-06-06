import socket

"""
This class is used exclusively by client.py
"""
class Network:
    def __init__(self):
        # followed a tutorial and I think I might change the structure a bit
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = "10.0.0.211" ## TODO remove this hard-coded nonsense
        self.port = 5555
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
    
    def send(self, data):
        try:
            self.client.send(data.encode(encoding='utf-8')) # data is a string lul
        except socket.error as err:
            print(err)
        return self.client.recv(2048).decode()

# remember for these two that a ^ b ^ a = a ^ a ^ b = b
def encrypt(key, val):
    assert len(key) == len(val), 'Key must be as long as value to encrypt'
    return key ^ val # bitwise xor
def decrypt(key, val):
    assert len(key) == len(val), 'Key must be as long as value to decrypt'
    return key ^ value