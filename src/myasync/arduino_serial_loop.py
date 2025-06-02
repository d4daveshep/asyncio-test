import asyncio
import serial_asyncio
from asyncio import Queue

async def read_from_arduino(reader, db_queue):
    """Continuously read from Arduino serial port and queue data for database"""
    while True:
        try:
            data = await reader.readline()
            decoded_data = data.decode('utf-8').strip()
            if decoded_data:
                await db_queue.put(decoded_data)
        except Exception as e:
            print(f"Error reading from Arduino: {e}")
            await asyncio.sleep(1)

async def write_to_database(db_queue):
    """Process database writes from the queue"""
    while True:
        try:
            data = await db_queue.get()
            # Your database write logic here
            await write_data_to_db(data)
            db_queue.task_done()
        except Exception as e:
            print(f"Error writing to database: {e}")

async def handle_arduino_commands(writer, command_queue):
    """Process commands that need to be sent to Arduino"""
    while True:
        try:
            command = await command_queue.get()
            writer.write(f"{command}\n".encode('utf-8'))
            await writer.drain()
            command_queue.task_done()
        except Exception as e:
            print(f"Error writing to Arduino: {e}")

async def write_data_to_db(data):
    """Placeholder for your database write implementation"""
    # Your actual database code here
    await asyncio.sleep(0.01)  # Simulate async DB operation
    print(f"Wrote to DB: {data}")

async def main():
    # Create queues for inter-task communication
    db_queue = Queue()
    command_queue = Queue()
    
    # Open serial connection to Arduino
    reader, writer = await serial_asyncio.open_serial_connection(
        url='/dev/ttyUSB0',  # Adjust for your Arduino port
        baudrate=9600
    )
    
    # Create and run all tasks concurrently
    tasks = [
        asyncio.create_task(read_from_arduino(reader, db_queue)),
        asyncio.create_task(write_to_database(db_queue)),
        asyncio.create_task(handle_arduino_commands(writer, command_queue))
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
        await writer.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())