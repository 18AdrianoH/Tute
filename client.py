import asyncio
import ssl
import string
import random
import os
import subprocess

from tute import deserialize

from gui import Interface

from server import SIGF, SSL_COMMAND
from server import DEFAULT_HOST, DEFAULT_PORT
from server import READ_LEN

RAND_NAME_LEN = 16

# say hello to the server providing information about player id
# server will say hello back
async def hello(host, port, ssl_context, id):
    reader, writer = await asyncio.open_connection(
        host, 
        port,
        ssl=ssl_context
        )
        
    writer.write(b'HELLO,' + id.encode('utf-8'))
    await writer.drain()
    writer.close()

    response = await reader.read(READ_LEN)
    print(response)

    #assert response == b'HELLO' # that they respond properly

# given the server's public key, spub, ask for the state of the game
async def get(host, port, ssl_context, id):
    reader, writer = await asyncio.open_connection(
        host, 
        port,
        ssl=ssl_context
        )

    data = b'GET,'+ id.encode('utf-8')
    writer.write(data)

    response = await reader.read(READ_LEN)
    state = deserialize(response)

    await writer.drain()
    writer.close()

    return state

# sends a message, but does not inquire into state
async def send(message, host, port, ssl_context, id):
    reader, writer = await asyncio.open_connection(
        host, 
        port
        )
    data = message.encode('utf-8') + b',' + id.encode('utf-8')

    writer.write(data)
    await writer.drain()
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

    print('checking for your key and cert files... they last a day and may need to be replaced')
    print('want to replace them if they exist? y/n')
    nf = input()
    if nf == 'Y' or nf == 'y':
        if os.path.isfile(SIGF):
            os.remove(SIGF)
    try:
        assert  os.path.isfile(SIGF)
    except AssertionError as ae:
        subprocess.call(SSL_COMMAND)

    ssl_context = ssl.create_default_context(
        ssl.Purpose.SERVER_AUTH,
    )
    ssl_context.check_hostname = False
    ssl_context.load_verify_locations(SIGF)
    
    await hello(host, port, ssl_context, id)

    print('Getting initial game state...')
    state = await get(host, port, ssl_context, id)

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
                await send(query, host, port, ssl_context, id)

            state = await get(host, port, ssl_context, id)
            gui.update(state)
            gui.draw()

if __name__ == '__main__':
    asyncio.run(run())