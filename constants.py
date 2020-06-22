# some networking constants
DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 10000

# 2^12 = 256 bytes
RECV = 1 << 14

KEYF = 'server.key'
SIGF = 'server.cert'
SSL_DAYS = '1000'

SSL_COMMAND = [
    'openssl',
    'req',
    '-x509',
    '-newkey',
    'rsa:2048',
    '-keyout',
    KEYF,
    '-nodes',
    '-out',
    SIGF,
    '-sha256',
    '-days',
    SSL_DAYS
]
