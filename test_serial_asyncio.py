import asyncio
import serial_asyncio


# class OutputProtocol(asyncio.Protocol):
#     def connection_made(self, transport):
#         self.transport = transport
#         print('port opened', transport)
#         transport.serial.rts = False  # You can manipulate Serial object via transport
#         transport.write(b'Hello, World!\n')  # Write serial data via transport
#
#     def data_received(self, data):
#         print('data received', repr(data))
#         if b'\n' in data:
#             self.transport.close()
#
#     def connection_lost(self, exc):
#         print('port closed')
#         self.transport.loop.stop()
#
#     def pause_writing(self):
#         print('pause writing')
#         print(self.transport.get_write_buffer_size())
#
#     def resume_writing(self):
#         print(self.transport.get_write_buffer_size())
#         print('resume writing')
#
#
# loop = asyncio.get_event_loop()
# coro = serial_asyncio.create_serial_connection(loop, OutputProtocol, '/dev/ttyACM0', baudrate=115200)
# transport, protocol = loop.run_until_complete(coro)
# loop.run_forever()
# loop.close()

class InputChunkProtocol(asyncio.Protocol):
    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):
        print('data received', repr(data))

        # stop callbacks again immediately
        self.pause_reading()

    def pause_reading(self):
        # This will stop the callbacks to data_received
        self.transport.pause_reading()

    def resume_reading(self):
        # This will start the callbacks to data_received again with all data that has been received in the meantime.
        self.transport.resume_reading()


async def reader():
    transport, protocol = await serial_asyncio.create_serial_connection(loop, InputChunkProtocol, '/dev/ttyACM0', baudrate=115200)

    while True:
        await asyncio.sleep(0.1)
        protocol.resume_reading()


loop = asyncio.get_event_loop()
loop.run_until_complete(reader())
loop.close()