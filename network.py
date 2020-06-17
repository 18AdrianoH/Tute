import socket
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

"""
This class is used as a sort of channel. Client.py uses it to talk to server.
Server is it's own beast.

Note to self: TCP GUARANTEES delivery. This is very useful/good.
Also it has guaranteed order.

Note we would have to store to a file to make this work for disconnects and reconnects
https://nitratine.net/blog/post/asymmetric-encryption-and-decryption-in-python/
is a good tutorial I followed but not wholely

Right now if you hve to disconnect the game has to restart.
"""

# this is basically overkill, but we need > 2048 for the very first message and it's probably ok
MESSAGE_SIZE = 4096

########## Methods that are shared ##########

def gen_keys():
    private_key = rsa.generate_private_key(
            public_exponent=65537, # they recommend this unless you have a reason to do otherwise
            key_size=2048, # extra extra secure lol
            backend=default_backend()
        )

    public_key = private_key.public_key()

    return public_key, private_key

# message must be in bytes
def encrypt(message, public_key):
    encrypted = public_key.encrypt(
        message,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return encrypted_message

# message must be in bytes and will come out as bytes
def decrypt(encrypted_message, private_key):
    message = private_key.decrypt(
        encrypted_message,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return message

# serializes using PEM protocol
def serialize_public_key(public_key):
    pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return pem

# the resulting keys will not equate to the original, but their serializations are the same
# so they should be encoding/decoding the same
def deserialize_public_key(pem):
    public_key = serialization.load_pem_public_key(
        pem,
        backend=default_backend()
    )
    return public_key

###
### As a standrad we will always share the public key but not the private key (it doesn't matter by symmetry)
###


### initialization message for server
# CONNECT <player_id> <public_key>
class Channel:
    def __init__(self, server_ip, server_port, player_id):
        # followed a tutorial and I think I might change the structure a bit
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = server_ip
        self.port = server_port
        self.id = self.connect()

        self.player_id = player_id

        # assymetric encryption 
        self.public_key, self.private_key = gen_keys()

        self.server_public_key = None

    def connect(self):
        try:
            self.client.connect((self.server, self.port))
        except Exception as exc:
            print('Failed to Connect, exception information below.')
            print(str(exc))
        return self.client.recv(MESSAGE_SIZE).decode(encoding='utf-8')
    
    def key_exchange(self):
        message = 'CONNECT ' + player_id + ' '
        message = message.encode('utf-8')
        message = message + serialize_public_key(self.public_key)

        # send the master a message to connect
        # remember that we only talk to the master on this socket so no need to sendto
        self.client.send(message)

        # wait for a response
        while True:
            data = self.client.recv(MESSAGE_SIZE)
            data = data.split(b' ')
            if data[0].decode('utf-8') == 'CONNECTED':
                self.server_public_key = deserialize_public_key(data[1])
                return
            # else try again I guess
    
    def quit(self):
        self.client.close()
    
    def send(self, datas):
        for data in datas:
            try:
                self.client.send(data.encode(encoding='utf-8')) # data is a string lul
            except socket.error as err:
                print(err)
            return self.client.recv(MESSAGE_SIZE).decode() ## TODO

# the master manages the game using Tute datastructures
#
# master response to CONNECT from player
# CONNECTED <server_public_key>
#
# Master has to use sendto instead of send to use proper encryption
class Master:
    def __init__(self, ip_address):
        # maps player_ids to player public key
        self.player_public_keys = {}
        # maps player to ip, port
        self.players_addresses = {}
    
    # ...use recvfrom() -> (bytes, address) to get the address
    def individual_key_exchange(player_address, player_id, player_public_key):
        self.players_addresses[player_id] = player_address
        self.player_public_keys[player_id] = deserialize_public_key(player_public_key)

        message = 'CONNECTED '.encode('utf-8')
        message += serialize_public_key(self.public_key) #TODO not defined yet

        # not defined TODO
        self.socket.sendto(message, player_address)