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

# 2048 bits is 256 bytes
KEY_SIZE = 1 << 11 # 2048

def gen_keys():
    private_key = rsa.generate_private_key(
            public_exponent=65537, # they recommend this unless you have a reason to do otherwise
            key_size=KEY_SIZE, # extra extra secure lol
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
    public_key.verify(
        signature,
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

# encrypt with a public key
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

# decrypt with a private key
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

# serialize a public key with PEM
def serialize_key(public_key):
    pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return pem

# acquire an object who's properties are the same as the original public key
def deserialize_key(pem):
    public_key = serialization.load_pem_public_key(
        pem,
        backend=default_backend()
    )
    return public_key