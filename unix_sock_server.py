import asyncio

UNIX_SOCKET_PATH = './unix_sock'


class EchoServer:
    async def listen(self, reader, writer):
        while True:
            data = await reader.read(128)
            if data:
                print(f'received {data}')
                writer.write(data)
                await writer.drain()
                print(f'sent {data}')
            else:
                print('closing')
                writer.close()
                return


async def serve(srv: asyncio.base_events.Server):
    async with srv:
        await srv.serve_forever()


def main():
    event_loop = asyncio.get_event_loop()
    echo_server = EchoServer()
    srv = event_loop.run_until_complete(
        asyncio.start_unix_server(echo_server.listen, UNIX_SOCKET_PATH)
    )
    try:
        event_loop.run_until_complete(serve(srv))
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
