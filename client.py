# WSS (WS over TLS) client example, with a self-signed certificate
import asyncio
import ssl
import subprocess
import os
import string
import random

from gui import Interface
from tute import deserialize

from constants import SIGF, KEYF, SSL_COMMAND
from constants import DEFAULT_HOST, DEFAULT_PORT
from constants import RECV

RAND_NAME_LEN = 16

DEFAULT_STATE = {'state' : 'WAITING'}

#b'NONE,NONE,<id>',
#b'PLAY,<card>,<id>',
#b'REVEAL<card>,<id>',
#b'CYCLE,NONE,<id>',
#b'QUIT,NONE,<id>',
async def play_client(address, gui, id):
    global RECV

    print(f'connecting to {address[0]} port {address[1]}')
    # The certificate is created with pymotw.com as the hostname,
    # which will not match when the example code runs
    # elsewhere, so disable hostname verification.
    ssl_context = ssl.create_default_context(
        ssl.Purpose.SERVER_AUTH,
    )
    ssl_context.check_hostname = False
    ssl_context.load_verify_locations('server.cert')
    reader, writer = await asyncio.open_connection(
        *address, ssl=ssl_context)

    running = True
    while running:
        gui.execute_actions()

        query = gui.request
        gui.request = None

        # if query is none we'll just ask for information
        squery = b'NONE,NONE,'+id.encode('utf-8')

        if not query is None:
            if query == 'QUIT':
                squery = b'QUIT,NONE,' + id.encode('utf-8')
                running = False
            elif query == 'CYCLE':
                squery = b'CYCLE,NONE,' + id.encode('utf-8')
            elif query[:4] == 'PLAY' or query[:6 == 'REVEAL']:
                squery = query.encode('utf-8') + b',' + id.encode('utf-8')
            
            print(f'sending {squery}')

        writer.write(squery)
        await writer.drain()
        
        if running:
            while True:
                # if no response we will fail lol
                state = await reader.read(RECV)
                if state:
                    gui.update(deserialize(state))
                    gui.draw()
                    break
    # once we exit the other while loop we are done
    writer.close()
    return

if __name__ == '__main__':
    print('enter id')
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

    # this will create the files necessary for you if you need them, but they have to be the same as the server's
    print('checking for your key and cert files... they last a day and may need to be replaced')
    print('want to replace them if they exist? y/n')
    nf = input()
    if nf == 'Y' or nf == 'y':
        if os.path.isfile(SIGF):
            os.remove(SIGF)
        if os.path.isfile(KEYF):
            os.remove(KEYF)
    try:
        assert  os.path.isfile(SIGF)
    except AssertionError as ae:
        subprocess.call(SSL_COMMAND)
    
    # here is the old launch code (from test-client times)
    address = (host, port)
    event_loop = asyncio.get_event_loop()
    
    gui = Interface(id, DEFAULT_STATE)
    try:
        event_loop.run_until_complete(
            play_client(address, gui, id)
        )
    finally:
        print('closing event loop')
        event_loop.close()