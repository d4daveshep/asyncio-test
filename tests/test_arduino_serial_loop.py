import pytest
import asyncio
import serial_asyncio
from asyncio import Queue

from myasync.arduino_serial_loop import (
    read_from_arduino,
    write_to_database,
    handle_arduino_commands,
)


@pytest.mark.asyncio
async def test_main(mock_serial_connection):
    # Create queues for inter-task communication
    db_queue = Queue()
    command_queue = Queue()

    # Open serial connection to Arduino
    reader, writer = await serial_asyncio.open_serial_connection(
        url="/dev/ttyUSB0",  # Adjust for your Arduino port
        baudrate=9600,
    )

    # Create and run all tasks concurrently
    tasks = [
        asyncio.create_task(read_from_arduino(reader, db_queue)),
        asyncio.create_task(write_to_database(db_queue)),
        asyncio.create_task(handle_arduino_commands(writer, command_queue)),
    ]

    try:
        # Example: Add a command to the queue
        await command_queue.put("LED_ON")

        # Run all tasks concurrently
        await asyncio.gather(*tasks)
    except KeyboardInterrupt:
        print("Shutting down...")
        for task in tasks:
            task.cancel()
        writer.close()
