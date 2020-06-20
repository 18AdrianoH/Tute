import asyncio
from tute import Tute
from tute import serialize

from crypto import gen_keys()
from crypto import read
from crypto import write
from crypto import deserialize_key
from crypto import serialize_key

host = '10.0.0.211'
port = 5555
handshook = False

game = Tute()
peers = {}
pub, pri = gen_keys()

async def handle(reader, writer):
    global peers
    global pub
    global pri

    data = await reader.read()
    addr = writer.get_extra_info('peername')

    if addr in peers:
        ppub = peers[addr]['key']
        # get query
        msg, sig = data.split(b',')
        query = read(msg, sig, ppub, pri)

        # get request
        if query[:3] == b'GET':
            message = write(serialize(tute), ppub, pri)
            writer.write(message)
            await writer.drain()
        # state change
        else:
            print(f"Received {message!r} from {addr!r}")
    # handshake
    elif len(data) >= 7 and data[:7] == b'CONNECT':
        _, addr_key, addr_id = data.split(b',')

        peers[addr] = {}
        peers[addr]['key'] = deserialize_key(addr_key)
        peers[addr]['id'] = addr_id.decode('utf-8')

        response = b'CONNECTED,' + serialize(pub)
        writer.write(response)
        await writer.drain()

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