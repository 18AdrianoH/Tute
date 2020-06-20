import asyncio
from tute import Tute
from tute import serialize

from crypto import gen_keys
from crypto import decrypt
from crypto import encrypt
from crypto import deserialize_key
from crypto import serialize_key

host = '10.0.0.211'
port = 5555
# necessary since -1 or empty will hang (wait until connection closed)
READ_LEN = 1 << 12 # safe number

game = Tute()
peers = {}
pub, pri = gen_keys()

async def handle(reader, writer):
    global READ_LEN
    global game
    global peers
    global pub
    global pri
    
    print('handle')

    data = await reader.read(READ_LEN)
    addr = writer.get_extra_info('peername')

    print(f"Received {data!r} from {addr!r}")

    # handshake
    if len(data) >= 7 and data[:7] == b'CONNECT':
        print('processing CONNECT')
        _, addr_key, addr_id = data.split(b',')

        peers[addr_id] = deserialize_key(addr_key)

        response = b'CONNECTED,' + serialize_key(pub)
        writer.write(response)
        await writer.drain()
    # else we'll only respond if they have a valid username and they've signed in a valid way
    else:
        # plains = <message with commas maybe>,<id>
        plain = decrypt(data, pri)
        plains = plain.split(b',')
        if plains[-1] in peers:
            ppub = peers[plains[-1]]

            # get query
            query_type = plains[0]

            # get request
            if query_type[:3] == b'GET':
                print('processing GET')

                plain = serialize(game)
                enc = encrypt(plain, ppub)

                writer.write(enc)
                await writer.drain()
            # state change
            else:
                print(f"Message was of type {query_type} by {plains[-1]}")

    writer.close()

async def main():
    server = await asyncio.start_server(
        handle, host, port)

    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')

    async with server:
        await server.serve_forever()
        # stop with server.shutdown

asyncio.run(main())