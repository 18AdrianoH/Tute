import asyncio
import ssl
import string
import random

from tute import deserialize

from gui import Interface

READ_LEN = 1 << 14 # one kilobit
RAND_NAME_LEN = 16
DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 5555

# say hello to the server providing information about player id
# server will say hello back
async def hello():
    pass

# given the server's public key, spub, ask for the state of the game
async def get(host, port):
    reader, writer = await asyncio.open_connection(
        host, 
        port
        )

    plain = b'GET,'
    enc = encrypt_sym(plain, symob) +  b',' + idu
    writer.write(enc)

    response = await reader.read(READ_LEN)
    # recieves a json representation of the game state
    spain = decrypt_sym(response, symob)
    spains = spain.split(b',')
    verify(idu, spains[-1], spub) # they'll send us back a signature with our name
    state = deserialize(spains[0])

    writer.close()
    return state

# sends a message, but does not inquire into state
async def send(message, host, port, id:
    reader, writer = await asyncio.open_connection(
        host, 
        port
        )
    data = message.encode('utf-8') + b',' + id.encode('utf-8')

    writer.write(data)
    # TODO add a wait for a response because otherwise we can get a race condition
    writer.close()

async def run():
    # the user provides the server creds
    print(f'please enter the server\'s host (blank for {DEFAULT_HOST}).')
    host = input()
    print(f'please enter the port you wish to bind to on the server (blank for {DEFAULT_PORT})')
    port = input()

    if host == '':
        host = DEFAULT_HOST
    
    if port == '':
        port = DEFAULT_PORT
    else:
        port = int(port)

    print(f'please enter your id (blank for a random id of length {RAND_NAME_LEN})')
    id = input()

    if id == '':
       letters = string.ascii_lowercase
       id = ''.join(random.choice(letters) for i in range(RAND_NAME_LEN))

    # TODO make this work
    success = await hello()
    assert success # or ask for a different name
    
    print('Getting initial game state...')
    state = await get(host, port, id,)

    print('done, running...')
    running = True

    gui = Interface(id, state)
    
    while running:
        gui.execute_actions()

        query = gui.request
        gui.request = None # ready to take in a new query (don't repeat!)
        if query == 'QUIT':
            running = False
        else:
            if not query is None:
                await send(query, host, port, id)

            state = await get(host, port)
            gui.update(state)
            gui.draw()

asyncio.run(run())