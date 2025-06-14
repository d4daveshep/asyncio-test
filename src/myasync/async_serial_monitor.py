import asyncio
import serial_asyncio


async def simple_monitor(port: str, baudrate: int = 115200):
    """Simple async Arduino monitor"""
    try:
        # Open connection
        reader, writer = await serial_asyncio.open_serial_connection(
            url=port, baudrate=baudrate
        )
        print(f"Connected to {port}")

        # Reading loop
        while True:
            data: bytes = await reader.readline()
            if data:
                message: str = data.decode("utf-8").strip()
                print(f"Arduino: {message}")

                # Example: Echo back or send commands
                if message == "PING":
                    writer.write(b"PONG\n")
                    await writer.drain()

    except KeyboardInterrupt:
        print("\nStopping...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if writer:
            writer.close()
            await writer.wait_closed()


# Run it
if __name__ == "__main__":
    asyncio.run(simple_monitor("/dev/ttyACM0"))  # Replace with your port
