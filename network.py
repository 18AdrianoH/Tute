# so we can talk
import socket
import threading

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
# might actually need more for game-state? oh no!
# 1<<12 = 4096
# 1<<14 ~= 1K bits (one Kb)
MESSAGE_SIZE = 1<<14 # recommended to be a power of 2 so you can do 1 << n for 2^n
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
def encrypt(message, key):
    encrypted_message = key.encrypt(
        message,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return encrypted_message

# message must be in bytes and will come out as bytes
def decrypt(encrypted_message, key):
    message = key.decrypt(
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
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_ip = server_ip
        self.server_port = server_port

        self.player_id = player_id

        # assymetric encryption 
        self.public_key, self.private_key = gen_keys()
        self.server_public_key = None

        self.connect()
        # yay!
        print('connected')
    
    # message must be bytes
    # inner is encrypt with your pub, decrypt with my priv (so mitm can't listen)
    # outer is encrypt with my pri, decrypt with your pub (so mitm can't speak)
    def encrypt(self, message):
        enc = encrypt(message, self.server_public_key)
        return encrypt(enc, self.private_key)

    def decrypt(self, encrypted_message):
        dec = decrypt(encrypted_message, self.private_key)
        return decrypt(dec, self.server_public_key)

    # connects to the server and does the key exchange
    def connect(self):
        try:
            self.socket.connect((self.server_ip, self.server_port))
        except Exception as exc:
            raise exc

        recieved = None
        while not recieved:
           recieved = self.socket.recv(MESSAGE_SIZE)
        
        if recieved[:5] != b'HELLO':
            raise TypeError('No Hello')
        # else do the key exchange

        message = 'CONNECT,' + self.player_id + ','
        message = message.encode('utf-8')
        message = message + serialize_public_key(self.public_key)

        # send the master a message to connect
        # remember that we only talk to the master on this socket so no need to sendto
        self.socket.send(message)

        # wait for a response
        recieved = None
        while not recieved:
            recieved = self.socket.recv(MESSAGE_SIZE)
        
        if recieved[:9] != b'CONNECTED':
            raise TypeError('No connected')
        # else
        self.server_public_key = recieved.split(b',')[1]
    
    def quit(self):
        self.socket.close()
    
    def send(self, datas):
        for data in datas:
            enc = self.encrypt(data.encode('utf-8'))
            try:
                self.socket.send(enc)
            except socket.error as err:
                raise err

    def listen(self):
        message = self.socket.recv(MESSAGE_SIZE)
        print(message)
        message = self.decrypt(message).decode('utf-8')
        print(message)
        return message

# for the future this has to be explicitely event driven, it's too hard to think of it otherwise

# the master manages the game using Tute datastructures
#
# master response to CONNECT from player
# CONNECTED <server_public_key>
#
# Master has to use sendto instead of send to use proper encryption
# 
# messages to server are 
# CONNECT <username> (with a private key for the master network module)
# PLAY <card> <player id>
# REVEAL <card> <player id> # reveal-won is the same as reveal, we will just check both
# CYCLE
class Master:
    def __init__(self, server_ip, server_port):
        self.public_key, self.private_key = gen_keys()

        self.server_ip = server_ip
        self.server_port = server_port

        # maps player_ids to player public key
        # info has 
        # ['id'] = player_id
        # ['connection'] = connection (socket object)
        # ['pub'] = public key object
        # and 
        # address_info[address] = info
        self.address_info = {}

        self.socket = None

        try:
            self.bind()
        except TypeError as te:
            # ports are unsigned 16-bit integers, so the largest port is 65535
            print('Port should be a numerical port and server_ip should be an IP address (maybe DNS).')
            raise te
        
        self.establish_connections()
        print('established all four connections')
    
    # assuming that server_ip and server_port are legitimate and usable it will try to bind
    def bind(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.bind((self.server_ip, self.server_port))
            self.socket.listen(MAX_CONNECTIONS)
        except socket.error as socket_error:
            raise socket_error # later we might want to handle it some other way
    
    # async key_exchange that is done with each player
    def key_exchange(self, connection, address):
        connection.send('HELLO'.encode('utf-8'))

        message = None
        while not message:
            message = connection.recv(MESSAGE_SIZE)
        
        if message[:7] != b'CONNECT':
            raise TypeError('Wrong Connect message recieved')
        # else

        # create the response message handshake
        send_message = 'CONNECTED,'.encode('utf-8')
        send_message += serialize_public_key(self.public_key)
        connection.send(send_message)

        # update data structures
        splt = message.split(b',')
        id_bits = splt[1]
        pub = splt[2]

        self.address_info[address] = {}
        self.address_info[address]['id'] = id_bits.decode('utf-8')
        self.address_info[address]['pub'] = deserialize_public_key(pub)
        self.address_info[address]['connection'] = connection

        print('connected with ' + self.address_info[address]['id'])

    # establishes the connections with each player by sending hello and then key exchanging
    # remember TCP guarantees delivery
    def establish_connections(self):
        connections = 0
        while connections < MAX_CONNECTIONS:
            print('.')
            try:
                # connect to a new individual
                connection, address = self.socket.accept()
                self.key_exchange(connection, address) # lol it can only do one at a time
                connections += 1
            except ConnectionAbortedError as err: # race condition connect after quitting
                raise err
        return

    # message must be bytes
    # inner is encrypt with your pub, decrypt with my priv (so mitm can't listen)
    # outer is encrypt with my pri, decrypt with your pub (so mitm can't speak)
    def encrypt(self, message, address):
        player_public_key = self.address_info[address]['pub']

        enc = encrypt(message, player_public_key)
        enc = encrypt(enc, self.private_key)
        return enc

    def decrypt(self, encrypted_message, address):
        player_public_key = self.address_info[address]['pub']

        dec = decrypt(encrypted_message, self.private_key)
        dec = decrypt(dec, player_public_key)
        return dec
    
    def send_state(self, serialized_game_json):
        data = game_json.encode('utf-8')
        data = self.encrypt(data)

        for address, info in self.address_info.items():
            self.address_info[address]['connection'].send(data)
    
    # you can use recvfrom or like me you can just use the connection with each player
    def listen(self):
        # a list of (player_id, message)
        messages_recieved = []
        for address, info in self.address_info.items():
            data = self.address_info[address]['connection'].recv(MESSAGE_SIZE)
            data = self.decrypt(data).decode('utf-8') # it's bits
            messages_recieved.append((self.address_info[address]['id'], data))
        return messages_recieved