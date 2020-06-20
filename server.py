import asyncio
from tute import Tute
from tute import serialize

from crypto import gen_keys()
from crypto import read
from crypto import write
from crypto import deserialize_public_key
from crypto import serialize_public_key

host = '10.0.0.211'
port = 5555
handshook = False

game = Tute()

async def handshake():
    pass

async def handle_echo(reader, writer):
    data = await reader.read(100)
    message = data.decode()
    addr = writer.get_extra_info('peername')

    print(f"Received {message!r} from {addr!r}")

    print(f"Send: {message!r}")
    writer.write(data)
    await writer.drain()

    print("Close the connection")
    writer.close()

async def main():
    server = await asyncio.start_server(
        handle_echo, host, port)

    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')

    async with server:
        await server.serve_forever()
        # stop with server.shutdown

asyncio.run(main())