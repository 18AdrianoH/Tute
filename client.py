import asyncio

from crypto import gen_keys()
from crypto import read
from crypto import write
from crypto import deserialize_key
from crypto import serialize_key

from tute import deserialize

# return the public key deserialized from the server
async def handshake(id):
    reader, writer = await asyncio.open_connection(
        host, 
        port
        )
    
    pub = serialize_key(pub)
    message = b'CONNECT,' + pub + b',' + id.encode('utf-8')
    writer.write(message)


    response = await reader.read() # will read all bytes sent
    if response[:9] == 'CONNECTED':
        # they return 'CONNECTED,<pem>'
        return deserialize_key(response.split(b',')[1])
    # else will return None

# given the server's public key, spub, ask for the state of the game
async def get(spub):
    reader, writer = await asyncio.open_connection(
        host, 
        port
        )

    writer.write(write(b'GET', spub, pri))

    response = await reader.read()
    message, signature = response.split(b',')
    # recieves a json representation of the game state
    state = deserialize(read(message, signature, spub, pri))

    writer.close()
    return state

# sends a message, but does not inquire into state
async def send(message, spub):
    reader, writer = await asyncio.open_connection(
        host, 
        port
        )

    writer.write(write(message.encode('utf-8'), spub, pri))
    writer.close()

async def run():
    host = '10.0.0.211'
    port = 5555
    pub, pri = gen_keys()

    print('starting... enter your id')
    id = input() # this is blocking but that is fine

    print('handshake...')
    spub = await handshake()
    print('handshake done, getting state...')
    state = await get(spub)
    print('done, running...')

    running = True
    
    while running:
        print('enter query')
        query = input()
        if query == 'q':
            running = False
        elif query == 'g':
            state = await get(spub)
            print(state)
        else:
            await send(query, spub)
    
    print('finished')


asyncio.run(run())