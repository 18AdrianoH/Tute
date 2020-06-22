import asyncio
import ssl
import subprocess

from tute import Tute
from tute import serialize

# necessary since -1 or empty will hang (wait until connection closed)
READ_LEN = 1 << 12 # key size lmao
# 256 length in bytes 

KEYF = 'server.key'
SIGF = 'server.cert'
SSL_DAYS = '1'

SSL_COMMAND = 'openssl req -x509 -newkey rsa:2048 -keyout' + KEYF + '-nodes -out' + SIGF + '-sha256 -days' + SSHL_DAYS

game = Tute()
peers = {}

async def handle(reader, writer):
    global READ_LEN
    global game
    global peers
    
    print('handle')

    data = await reader.read(READ_LEN)
    addr = writer.get_extra_info('peername')

    print(f'Received {data!r} from {addr!r}')

    datas = data.split(b',')

    if id_str in peers:
        # get query type
        query_type = datas[0]

        # get request (want to know the state of the game)
        if query_type == b'GET':
            print('processing GET')

            state = serialize(game)
            writer.write(state)
            await writer.drain()
        # state change (want to request to do something)
        else:
            print(f'Message was of type {query_type} by {id_str}')

            if query_type == b'CYCLE':
                game.increment_state()
            else:
                card = datas[1].decode('utf-8')
                if query_type == b'REVEAL':
                    if card in game.player_cards[id_str]:
                        game.reveal_card(id_str, card)
                        print('revealed a card!')
                    elif card in game.player_won_cards[id_str]:
                        game.reveal_won_card(id_str, card)
                        print('revealed a won card!')
                    
                elif query_type == b'PLAY':
                    if card in game.player_cards[id_str]:
                        game.play_card(id_str, card)
                        print(f'{id_str} played {card}!')

    await writer.drain()
    writer.close()

async def main():
    print('please enter your host and then port')
    host = input()
    port = input()

    if host == '':
        host = 'localhost'
    
    if port == '':
        port = 5555
    else:
        port = int(port)

    try:
        assert os.isfile(KEYF) and os.isfile(SIGF)
    except AssertionError as ae:
        subprocess.run(SSL_COMMAND)
    
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

asyncio.run(main())