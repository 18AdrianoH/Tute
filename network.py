# so we can talk
import socket

# so we can talk securely
# generate
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
# serialiation for handshake
from cryptography.hazmat.primitives import serialization
# encrypt/decrypt
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

"""
This class is used as a sort of channel. Client.py uses it to talk to server.
Server is it's own beast.

Note to self: TCP GUARANTEES delivery. This is very useful/good.
Also it has guaranteed order.

Note we would have to store to a file to make this work for disconnects and reconnects
https://nitratine.net/blog/post/asymmetric-encryption-and-decryption-in-python/
is a good tutorial I followed but not wholely

Right now if you hve to disconnect the game has to restart.

BTW where I say IP I think it's also possible to use a DNS name as well. I'm not sure but I'll try.

A note about the handshake: the way I do it I encrypt TWICE (once with my pri, once with their pub) which means that
to decrypt you always need one pub (their pub) and one pri (their pri), meaning that it's impossible to encrypt. More
importantly (because using just the pub would mean they could encrypt if they heard it, and using just the pri would mean
they could decrypt if they heard it) it means that to encrypt you need at least one of the two private keys. This is
impossible for a man in the middle because neither private key is shared.
"""

# this is basically overkill, but we need > 2048 for the very first message and it's probably ok
MESSAGE_SIZE = 4096
MAX_CONNECTIONS = 4 # maximum number of people allowed to connect

########## Methods that are shared ##########

def gen_keys():
    private_key = rsa.generate_private_key(
            public_exponent=65537, # they recommend this unless you have a reason to do otherwise
            key_size=2048, # extra extra secure lol
            backend=default_backend()
        )
    return private_key.public_key(), private_key

# message must be in bytes
def encrypt(message, public_key):
    encrypted_message = public_key.encrypt(
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

        self.connected = False
    
    # message must be bytes
    # inner is encrypt with your pub, decrypt with my priv (so mitm can't listen)
    # outer is encrypt with my pri, decrypt with your pub (so mitm can't speak)
    def encrypt(self, message):
        return encrypt(encrypt(message, self.server_public_key), self.private_key)
    def decrypt(self, encrypted_message):
        return decrypt(encrypted_message, decrypt(encrypted_message, self.private_key), self.server_public_key)

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
                self.connected = True
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

# messages to server are 

# CONNECT <username> (with a private key for the master network module)
# PLAY <card> <player id>
# REVEAL <card> <player id> # reveal-won is the same as reveal, we will just check both
# CYCLE
class Master:
    def __init__(self, server_ip, server_port):
        self.private_key, self.public_key = gen_keys()

        self.server_ip = server_ip
        self.server_port = server_port

        # maps player_ids to player public key
        self.address_public_key = {}
        self.address_player_id = {}
        self.socket = None

        try:
            self.bind()
        except TypeError as te:
            # ports are unsigned 16-bit integers, so the largest port is 65535
            print('Port should be a numerical port and server_ip should be an IP address (maybe DNS).')
            raise te
    
    # assuming that server_ip and server_port are legitimate and usable it will try to bind
    def bind(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.bind((self.server_ip, self.port))
            self.socket.listen(MAX_CONNECTIONS)
        except socket.error as socket_error:
            raise socket_error # later we might want to handle it some other way

    # message must be bytes
    # inner is encrypt with your pub, decrypt with my priv (so mitm can't listen)
    # outer is encrypt with my pri, decrypt with your pub (so mitm can't speak)
    def encrypt(self, message, address):
        player_public_key = self.address_public_key[address]

        enc = encrypt(message, player_public_key)
        enc = encrypt(enc, self.private_key)
        return enc

    def decrypt(self, encrypted_message, address):
        player_public_key = self.address_public_key[address]

        dec = decrypt(encrypted_message, self.private_key)
        dec = decrypt(dec, player_public_key)
        return dec
    
    def individual_key_exchange(player_address, player_id, player_pem):
        self.address_public_key[player_address] = deserialize_public_key(player_pem)
        self.address_player_id[player_address] = player_id

        # create the response message handshake
        message = 'CONNECTED '.encode('utf-8')
        message += serialize_public_key(self.public_key)

        self.socket.sendto(message, player_address)

        self.player_connected[player_id] = True

        return player_id # returns player_id so that we can tell Tute later
    
    def send_state(self, serialized_game_json):
        data = game_json.encode('utf-8')

        for player, address in self.player_addresses.items():
            self.socket.sendto()


    def send(self, address):
        pass
    
    # ...use recvfrom() -> (bytes, address) to get the address
    # this is so we can tell Tute which player_id made that move
    def listen(self):
        data, address = self.socket.recvfrom(MESSAGE_SIZE)

# # helper for start_listening
# def listen(self):
#     while self.running:
#         try:
#             connection, address = self.socket.accept()
#             print ('connected to {} who is using port {}'.format(address[0], str(address[1])))
#             player_thread = threading.Thread(target=self.process_response, args=(connection, address))
#             player_thread.start()
#         except ConnectionAbortedError as err:
#             # this should only be caused by a race condition where we tried to connect after quitting
#             # but before self.running was False so we still did it
#             # a better solution would involve locks but this should be fine for now
#             assert not self.running, 'Some other than the connection race condition may have occured'
#     return # threads close when you you return from a function