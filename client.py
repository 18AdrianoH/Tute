import asyncio

from crypto import gen_keys_asym
from crypto import gen_key_sym

from crypto import decrypt_asym
from crypto import encrypt_asym
from crypto import verify
from crypto import sign

from crypto import deserialize_key_asym
from crypto import serialize_key_asym

from crypto import sym_ob
from crypto import encrypt_sym
from crypto import decrypt_sym

from crypto import ASYM_KEY_SIZE

from tute import deserialize

READ_LEN = 1 << 14 # one kilobit

# return the public key deserialized from the server
async def handshake(id, host, port, pub):
    reader, writer = await asyncio.open_connection(
        host, 
        port
        )
    
    pem = serialize_key_asym(pub)
    message = b'CONNECT,' + pem + b',' + id.encode('utf-8')
    writer.write(message)

    response = await reader.read(READ_LEN) # will read all bytes sent
    
    if response[:9] == b'CONNECTED':
        # they return 'CONNECTED,<pem>'
        return deserialize_key_asym(response.split(b',')[1])
    # else will return None

# provdes a message that can be authed by the server to acquire the symmetric key
async def handshake_aes(id, host, port, spub, pri, sym):
    reader, writer = await asyncio.open_connection(
        host, 
        port
        )
    id_bits = id.encode('utf-8')
    sig = sign(id_bits, pri)

    print(len(sym))

    # ln is the length of the slice that goes into the first section (one fourth)
    # 4 + n + x + n + 44 + n + i = 4 + n + 256-x + n + i
    # -> n + x + n + 44 = n + 256 - x -> 2x + n = 256 - 44 = 212 = 2x + n
    # 106 - n//2 = x, here n = 3 or 2 (depending on my luck that day), so -> 105
    ln = 105

    msg1 = b'AES1,,' + sig[:ln] + b',,' + sym + b',,' + id_bits
    msg2 = b'AES2,,' + sig[ln:] + b',,' + id_bits
    #print(msg1)
    #print(msg2)
    print('lengths work?', len(msg1), len(msg2))

    msg1 = encrypt_asym(msg1, spub)
    msg2 = encrypt_asym(msg2, spub)
    # very low chance that you get this many commas random
    # lmao I know this is a terrible solution... a better one is use SSL or worse is send twice once per
    msg = msg1 + b',,' + msg2

    writer.write(msg)
    response = await reader.read(READ_LEN)
    print(response)
    writer.close()

    return decrypt_asym(response, pri) == b'RECIEVED,' + sym

# given the server's public key, spub, ask for the state of the game
async def get(spub, pri, host, port, id, symob):
    reader, writer = await asyncio.open_connection(
        host, 
        port
        )
    idu = id.encode('utf-8')

    plain = b'GET,,,,,,,,,,' + sign(idu, pri)
    enc = encrypt_sym(plain, symob) +  b',,,,,,,,,,' + idu
    writer.write(enc)

    response = await reader.read(READ_LEN)
    # recieves a json representation of the game state
    spain = decrypt_sym(response, symob)
    spains = spain.split(b',,,,,,,,,,')
    verify(idu, spains[-1], spub) # they'll send us back a signature with our name
    state = deserialize(spains[0])

    writer.close()
    return state

# sends a message, but does not inquire into state
async def send(message, spub, pri, host, port, id, symob):
    reader, writer = await asyncio.open_connection(
        host, 
        port
        )
    idu = id.encode('utf-8')
    plain = message.encode('utf-8') + b',,,,,,,,,,' + sign(idu, pri)
    enc = encrypt_sym(plain, symob) + b',,,,,,,,,,' + idu

    writer.write(enc)
    writer.close()

async def run():
    # the user provides the server creds
    host = '10.0.0.211'
    port = 5555
    pub, pri = gen_keys_asym()

    sym = gen_key_sym()
    symob = sym_ob(sym)

    print('starting... enter your id')
    id = input() # this is blocking but that is fine

    print('handshake...')
    spub = await handshake(id, host, port, pub)
    print('handshake done, sending over AES key...')
    worked = await handshake_aes(id, host, port, spub, pri, sym)
    if not worked:
        print('failed to exchange AES keys')
        return
    print('AES arrived successfully, getting initial game state...')
    state = await get(spub, pri, host, port, id, symob)
    print('done, running...')

    running = True
    
    while running:
        print('enter query')
        query = input()
        if query == 'Q':
            running = False
        elif query == 'G':
            state = await get(spub, pri, host, port, id, symob)
            if (state['state'] == 'WAITING'):
                print(state)
            else:
                print('center', state['center'])
                print('to play', state['to play'])
                print('order', state['player order'])
                print('game suit', state['game suit'])
                print(state['players cards'][id])
                print(state['won cards'][id])
        else:
            await send(query, spub, pri, host, port, id, symob)
    
    print('finished')


asyncio.run(run())