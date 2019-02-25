import asyncio
from functools import partial

import pytest

from unix_sock_server import EchoServer


def test_echo_server(event_loop, tmp_path):
    unix_sock_path = str((tmp_path / 'unix_sock').absolute())
    buf = b''
    msg = b'hello, world!'
    started = asyncio.Event()

    async def client(addr, completion):
        nonlocal buf

        await started.wait()
        reader, writer = await asyncio.open_unix_connection(
            addr, loop=event_loop
        )
        writer.write(msg)
        writer.write_eof()
        await writer.drain()

        while len(buf) < len(msg):
            data = await reader.read()
            if data:
                buf += data
        writer.close()
        completion()

    async def serve(srv):
        async with srv:
            started.set()
            await srv.serve_forever()

    def done_callback(srv):
        srv.close()

    server = EchoServer()
    srv = event_loop.run_until_complete(
        asyncio.start_unix_server(server.listen, unix_sock_path)
    )
    coros = {
        serve(srv),
        client(
            unix_sock_path,
            partial(done_callback, srv)
        ),
    }
    event_loop.run_until_complete(asyncio.wait(coros))
    assert srv.sockets == []
    assert not srv.is_serving()
    assert buf == msg
