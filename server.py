import asyncio
import ssl
import subprocess
import os

from tute import Tute
from tute import serialize

from constants import SIGF, KEYF, SSL_COMMAND
from constants import DEFAULT_HOST, DEFAULT_PORT
from constants import RECV

# message can be <type>, <card>, <player_id>
# if no action b'NONE,NONE,<id>'
# if cycle b'CYCLE,NONE,<id>'
# else b'REVEAL,<card>,<id>' or b'PLAY,<card>,<id>'
# response is always the same as a get response (you get the current state of the game after your edit)
game = Tute()

async def echo(reader, writer):
    global RECV
    global game
    
    address = writer.get_extra_info('peername')
    print('connection accepted')
    while True:
        data = await reader.read(RECV)
        dtype, card, id = data.split(b',')

        card_str = card.decode('utf-8')
        id_str = id.decode('utf-8')
        # only existing players can do stuff like that
        if id_str in game.player_order:
            if dtype == b'QUIT':
                print('message terminated, closing connection')
                writer.close()
                return
            # else
            if dtype == b'CYCLE':
                print('cycling')
                game.increment_state()
            elif dtype == b'REVEAL':
                if card_str in game.player_cards[id_str]:
                    print('revealing a card')
                    game.reveal_card(id_str, card_str)
                elif card_str in game.player_won_cards[id_str]:
                    print('revealing a won card')
                    game.reveal_won_card(id_str, card_str)
            elif dtype == b'PLAY':
                if card_str in game.player_cards[id_str]:
                    print('playing a card')
                    game.play_card(id_str, card_str)
        # your hello can say anything basically
        elif len(game.player_order) < 4:
            game.add_player(id_str)
        
        # we always return the state of the game (your placeholder can be NONE,NONE,NONE or something else)
        response = serialize(game)
        writer.write(response)
        await writer.drain()
    return

# when we run the server...
if __name__ == '__main__': 
    print('please enter your host and then port')
    host = input()
    port = input()

    if host == '':
        host = DEFAULT_HOST
    
    if port == '':
        port = DEFAULT_PORT
        
    if type(port) != int:
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

    SERVER_ADDRESS = (host, port)
    event_loop = asyncio.get_event_loop()

    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_context.check_hostname = False
    ssl_context.load_cert_chain(SIGF, KEYF)

    print('creating and starting server')
    factory = asyncio.start_server(echo, *SERVER_ADDRESS,
                                ssl=ssl_context)

    server = event_loop.run_until_complete(factory)

    # Enter the event loop permanently to handle all connections.
    try:
        event_loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.close()
        event_loop.run_until_complete(server.wait_closed())
        print('server closed')
        event_loop.close()