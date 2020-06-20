import asyncio

from crypto import gen_keys
from crypto import decrypt
from crypto import encrypt
from crypto import deserialize_key
from crypto import serialize_key

from tute import deserialize

READ_LEN = 1 << 12 # safe number

# return the public key deserialized from the server
async def handshake(id, host, port, pub):
    reader, writer = await asyncio.open_connection(
        host, 
        port
        )
    
    pem = serialize_key(pub)
    message = b'CONNECT,' + pem + b',' + id.encode('utf-8')
    writer.write(message)

    response = await reader.read(READ_LEN) # will read all bytes sent
    
    if response[:9] == b'CONNECTED':
        # they return 'CONNECTED,<pem>'
        return deserialize_key(response.split(b',')[1])
    # else will return None

# given the server's public key, spub, ask for the state of the game
async def get(spub, pri, host, port, id):
    reader, writer = await asyncio.open_connection(
        host, 
        port
        )
    
    plain = b'GET,' + id.encode('utf-8')
    enc = encrypt(plain, spub)
    writer.write(enc)

    response = await reader.read(READ_LEN)
    # recieves a json representation of the game state
    spain = decrypt(response, pri)
    state = deserialize(spain)

    writer.close()
    return state

# sends a message, but does not inquire into state
async def send(message, spub, host, port, id):
    reader, writer = await asyncio.open_connection(
        host, 
        port
        )
    
    plain = message.encode('utf-8') + b',' + id.encode('utf-8')
    enc = encrypt(plain, spub)

    writer.write(enc)
    writer.close()

async def run():
    host = '10.0.0.211'
    port = 5555
    pub, pri = gen_keys()

    print('starting... enter your id')
    id = input() # this is blocking but that is fine

    print('handshake...')
    spub = await handshake(id, host, port, pub)
    print('handshake done, getting state...')
    state = await get(spub, pri, host, port, id)
    print('done, running...')

    running = True
    
    while running:
        print('enter query')
        query = input()
        if query == 'q':
            running = False
        elif query == 'g':
            state = await get(spub, pri, host, port, id)
            print(state)
        else:
            await send(query, spub, host, port, id)
    
    print('finished')


asyncio.run(run())