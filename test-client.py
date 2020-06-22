# WSS (WS over TLS) client example, with a self-signed certificate

import asyncio
import ssl

from gui import Interface
from tute import deserialize

RECV = 1 << 14

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


SERVER_ADDRESS = ('localhost', 10000)

event_loop = asyncio.get_event_loop()

print('enter id')
id = input()
gui = Interface(id, DEFAULT_STATE)

try:
    event_loop.run_until_complete(
        play_client(SERVER_ADDRESS, gui, id)
    )
finally:
    print('closing event loop')
    event_loop.close()