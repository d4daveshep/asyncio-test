import asyncio
import random

import serial_asyncio


async def open_serial_connection():
    return await serial_asyncio.open_serial_connection(url='/dev/ttyACM0', baudrate=115200)


async def read_serial_line(reader):
    while True:
        line = await reader.readline()
        print(str(line, 'utf-8'))


async def write_serial_string(writer):
    while True:
        target_temp = random.randrange(10, 30)
        string_to_write = '<' + str(target_temp) + '>'
        print(f"writing {string_to_write}")
        writer.write(string_to_write.encode())
        await asyncio.sleep(5)


async def main(reader, writer):
    # await asyncio.gather(read_serial_line(reader), write_serial_string(writer))
    await asyncio.gather(read_serial_line(reader))


if __name__ == "__main__":

    loop = asyncio.get_event_loop()

    try:

        reader, writer = loop.run_until_complete(open_serial_connection())
        writer_task = loop.create_task(write_serial_string(writer))
        reader_task = loop.create_task(read_serial_line(reader))
        loop.run_forever()

        # asyncio.run(main(reader, writer))
    except KeyboardInterrupt:
        print("Stopping loop")
        loop.stop()
    finally:
        print("Closing loop")
        loop.close()
