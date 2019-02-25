import asyncio

MESSAGES = [
    b'hello,',
    b' world',
    b'!',
]
UNIX_SOCKET_PATH = './unix_sock'


async def echo_client(addr, messages):
    print(f'connecting to:{addr}')
    reader, writer = await asyncio.open_unix_connection(addr)
    for msg in messages:
        writer.write(msg)
        print(f'sending data:{msg}')
    if writer.can_write_eof():
        writer.write_eof()
    await writer.drain()

    while True:
        data = await reader.read(128)
        if data:
            print(f'received data:{data}')
        else:
            writer.close()
            return


def main():
    event_loop = asyncio.get_event_loop()
    try:
        event_loop.run_until_complete(
            echo_client(UNIX_SOCKET_PATH, MESSAGES)
        )
    finally:
        event_loop.close()


if __name__ == '__main__':
    main()
