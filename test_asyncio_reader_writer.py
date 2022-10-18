import asyncio
import json
import random

import serial_asyncio
import zmq as zmq
from zmq.asyncio import Context, Poller


async def open_serial_connection():
    return await serial_asyncio.open_serial_connection(url='/dev/ttyACM0', baudrate=115200)


async def zmq_receiver(ctx: Context, url: str) -> None:
    """receive messages with polling"""
    pull = ctx.socket(zmq.PULL)
    pull.connect(url)
    poller = Poller()
    poller.register(pull, zmq.POLLIN)
    while True:
        events = await poller.poll()
        if pull in dict(events):
            # print("recving", events)
            msg = await pull.recv_multipart()
            dict_received = json.loads(msg[0].decode("utf-8"))
            print('received via zmq', dict_received)

            try:
                target_temp = dict_received["target-temp"]
                await write_serial_string(writer, target_temp)
            except KeyError as err_info:
                print(f"{err_info} not received" )


async def read_serial_line(reader):
    while True:
        line = await reader.readline()
        print(str(line, 'utf-8'))


async def write_serial_string(writer, temp: float):
    # while True:
    # target_temp = random.randrange(10, 30)
    string_to_write = '<' + str(temp) + '>'
    print(f"writing {string_to_write} to serial")
    writer.write(string_to_write.encode())
    await asyncio.sleep(0)


if __name__ == "__main__":

    url = 'tcp://127.0.0.1:5555'

    ctx = Context.instance()

    loop = asyncio.get_event_loop()

    try:
        reader, writer = loop.run_until_complete(open_serial_connection())

        receiver_task = loop.create_task(zmq_receiver(ctx, url))

        # writer_task = loop.create_task(write_serial_string(writer))
        reader_task = loop.create_task(read_serial_line(reader))

        loop.run_forever()

    except KeyboardInterrupt:
        print("Stopping loop")
        loop.stop()
    finally:
        print("Closing loop")
        loop.close()
