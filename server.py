import asyncio
import ssl
import subprocess
import os

from tute import Tute
from tute import serialize

DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 5555

# 2^12 = 256 bytes
READ_LEN = 1 << 14

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

game = Tute()
peers = {}

async def handle(reader, writer):
    global READ_LEN
    global game
    global peers # ignores anyone who's not in the game

    data = await reader.read(READ_LEN)
    addr = writer.get_extra_info('peername')

    #print(f'Received {data!r} from {addr!r}')

    datas = data.split(b',')
    query_type = datas[0]
    id = datas[1].decode('utf-8')

    if query_type == b'HELLO':
        
        game.add_player(id)
        peers[id] = None # values not used for now lol
        print('added ' + id)

        if len(game.player_order) >= 4:
            game.increment_state() # start the game basically

    if id in peers:
        # get request (want to know the state of the game)
        if query_type == b'GET':
            print('processing GET')

            state = serialize(game)
            writer.write(state)
            await writer.drain()
        # state change (want to request to do something)
        else:
            print(f'Message was of type {query_type} by {id}')
            if query_type == b'CYCLE':
                game.increment_state()

            else:
                card = datas[1].decode('utf-8')
                if query_type == b'REVEAL':
                    if card in game.player_cards[id]:
                        game.reveal_card(id, card)
                        print('revealed a card!')
                    elif card in game.player_won_cards[id]:
                        game.reveal_won_card(id, card)
                        print('revealed a won card!')
                    
                elif query_type == b'PLAY':
                    if card in game.player_cards[id]:
                        game.play_card(id, card)
                        print(f'{id} played {card}!')

    await writer.drain()
    writer.close()

async def main():
    print('please enter your host and then port')
    host = input()
    port = input()

    if host == '':
        host = DEFAULT_HOST
    
    if port == '':
        port = DEFAULT_PORT
    else:
        port = int(port)

    # create certs if necessary and use em (key encrypts, cert verifies)
    print('checking for your key and cert files... they last a day and may need to be replaced')
    print('want to replace them if they exist? y/n')
    nf = input()
    if nf == 'Y' or nf == 'y':
        if os.path.isfile(KEYF):
            os.remove(KEYF)
        if os.path.isfile(SIGF):
            os.remove(SIGF)
    try:
        assert os.path.isfile(KEYF) and os.path.isfile(SIGF)
    except AssertionError as ae:
        subprocess.call(SSL_COMMAND)
    
    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_context.check_hostname = False
    ssl_context.load_cert_chain(SIGF, KEYF)

    # run the server with our server handle function
    server = await asyncio.start_server(
        handle, 
        host, 
        port,
        ssl=ssl_context
        )

    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')

    async with server:
        await server.serve_forever() # can be stopped with server.shutdown

if __name__ == '__main__':
    asyncio.run(main())