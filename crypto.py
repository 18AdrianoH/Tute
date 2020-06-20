# a useless file that would benefit from being replaced with OpenSSL

# generate
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
# serialiation for handshake
from cryptography.hazmat.primitives import serialization
# encrypt/decrypt
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
# signing
from cryptography.hazmat.primitives.asymmetric import utils
# symmetric encryption
from cryptography.fernet import Fernet

# 2048 bits is 256 bytes
ASYM_KEY_SIZE = 1 << 11 # one kilo-bit

def gen_keys_asym():
    private_key = rsa.generate_private_key(
            public_exponent=65537, # they recommend this unless you have a reason to do otherwise
            key_size=ASYM_KEY_SIZE, # extra extra secure lol
            backend=default_backend()
        )
    return private_key.public_key(), private_key

# sign with a private key
def sign(message, key):
    signature = key.sign(
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return signature

# verify with a public key
# if it does not verify then it raises an InvalidSignature exception
def verify(message, signature, key):
    key.verify(
        signature,
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

# encrypt with a public key
def encrypt_asym(message, key):
    encrypted_message = key.encrypt(
        message,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return encrypted_message

# decrypt with a private key
def decrypt_asym(encrypted_message, key):
    message = key.decrypt(
        encrypted_message,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return message

# serialize a public key with PEM
def serialize_key_asym(public_key):
    pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return pem

# acquire an object who's properties are the same as the original public key
def deserialize_key_asym(pem):
    public_key = serialization.load_pem_public_key(
        pem,
        backend=default_backend()
    )
    return public_key

# for symmetric encryption
# https://nitratine.net/blog/post/encryption-and-decryption-in-python/
# for asymmetric encryption
# https://nitratine.net/blog/post/asymmetric-encryption-and-decryption-in-python/

# fuck it looks like I'm doing symmetric keys now because the messages are too big >:(

# first exchange public keys
# then send a symmetric encryption key (AES) along with a signature, encrypt the AES key
# now both communicate by sending information over AES which has no limit on size

# this would require a little more statefullness which I'm willing to sacrifice for my MVP

# note that in the documentation it says that Fernet uses AES CBC 128 bit with HMAC SHA256 for auth
# AES 128 bit is around the same security of 256 because of an error (too linear) in 256
# and CBC is kinda sucky because you can't parallelize but whatever good enough for my game lol

# this returns a bytes object that you can use to spawn a Fernet key object
def gen_key_sym():
    return Fernet.generate_key()

# using key object
def encrypt_sym(msg, key_ob):
    return key_ob.encrypt(msg)
# using key object
def decrypt_sym(enc, key_ob):
    return key_ob.decrypt(enc)

# no serialization really needed since you use gen_key_sym() to create it, you just need to remember it

def sym_ob(sym):
    return Fernet(sym)