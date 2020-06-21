import asyncio
from tute import Tute
from tute import serialize

from crypto import gen_keys_asym

# assymetric key functionality
from crypto import decrypt_asym
from crypto import encrypt_asym
from crypto import verify
from crypto import sign

from crypto import encrypt_sym
from crypto import decrypt_sym
from crypto import sym_ob

from crypto import ASYM_KEY_SIZE

# symmetric key functionality
from crypto import deserialize_key_asym
from crypto import serialize_key_asym

# necessary since -1 or empty will hang (wait until connection closed)
READ_LEN = 1 << 12 # key size lmao
# 256 length in bytes 

game = Tute()
peers = {}
pub, pri = gen_keys_asym()

async def handle(reader, writer):
    global READ_LEN
    global game
    global peers
    global pub
    global pri
    
    print('handle')

    data = await reader.read(READ_LEN)
    addr = writer.get_extra_info('peername')

    print(f'Received {data!r} from {addr!r}')

    # handshake
    if len(data) >= 7 and data[:7] == b'CONNECT':
        print('processing CONNECT')
        _, addr_key, addr_id = data.split(b',')

        id = addr_id.decode('utf-8')

        # when we make this use AES for future communcations, need this to be a nested dict
        peers[id] = {}
        peers[id]['rsa'] = deserialize_key_asym(addr_key)

        response = b'CONNECTED,' + serialize_key_asym(pub)
        writer.write(response)
        await writer.drain()

        game.add_player(id)
        if len(game.player_order) == 4:
            game.increment_state() # start the game!
    
        
    # else we'll only respond if they have a valid username and they've signed in a valid way
    else:
        # AES handshake (lmao this is the dumbest shit ever)
        if b',,' in data and not b',,,,,,,,,,' in data:
            # it's 4 commas for low probability
            msg1, msg2 = data.split(b',,')
            msg1 = decrypt_asym(msg1, pri)
            msg2 = decrypt_asym(msg2, pri)

            # magic numbers for the win
            ln = 105

            print(msg1, msg2)

            aes1, sig1, sym, id_bits = msg1.split(b',,')
            aes2, sig2, _id_bits = msg2.split(b',,')

            if (aes1 == b'AES1' and aes2 == b'AES2' and id_bits == _id_bits):
                print('looking ok...')
                id = id_bits.decode('utf-8')
                ppub = peers[id]['rsa']
                verify(id_bits, sig1 + sig2, ppub)
                # now that we know that it was sent by the correct person and they are honest...
                peers[id]['aes'] = sym_ob(sym)
                peers[id]['aes_spawn'] = sym # probably will never use this

                response = encrypt_asym(b'RECIEVED,' + sym, ppub)
                writer.write(response)
            else:
                print('looks like the ids or headers didn\'t match!')

        else:
            # plains = <message with commas maybe>,<sig>,<id>
            _enc, name = data.split(b',,,,,,,,,,')
            id_str = name.decode('utf-8')

            plain = decrypt_sym(_enc, peers[id_str]['aes'])
            plains = plain.split(b',,,,,,,,,,')

            sig = plains[-1]

            if id_str in peers:
                ppub = peers[id_str]['rsa']
                verify(name, sig, ppub)

                # get query type
                query_type = plains[0]

                # get request
                if query_type[:3] == b'GET':
                    print('processing GET')

                    plain = serialize(game) + b',,,,,,,,,,' + sign(name, pri)
                    enc = encrypt_sym(plain, peers[id_str]['aes'])

                    writer.write(enc)
                    await writer.drain()
                # state change
                else:
                    print(f'Message was of type {query_type} by {id_str}')
                    print('telling game your request')

                    if query_type == b'CYCLE':
                        game.increment_state()
                    elif query_type == b'REVEAL':
                        card = plains[1].decode('utf-8')
                        if card in game.player_cards[id_str]:
                            game.reveal_card(id_str, card)
                            print('revealed a card!')
                        elif card in game.player_won_cards[id_str]:
                            game.reveal_won_card(id_str, card)
                            print('revealed a won card!')
                    elif query_type == b'PLAY':
                        card = plains[1].decode('utf-8')
                        if card in game.player_cards[id_str]:
                            game.play_card(id_str, card)
                            print(f'{id_str} played {card}!')
                    
                    print(f'round num {game.round_num}')
                    print(f'turn {game.turn}')
                    #print(f' {}')
                    #print(f' {}')
                    #print(f' {}')

    writer.close()

async def main():
    host = 'localhost'
    port = 5555

    server = await asyncio.start_server(
        handle, host, port)

    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')

    async with server:
        await server.serve_forever()
        # stop with server.shutdown

asyncio.run(main())