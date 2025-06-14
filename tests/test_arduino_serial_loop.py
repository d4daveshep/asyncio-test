from myasync.arduino_serial_loop import main
from conftest import sine_wave_value
import asyncio
import serial_asyncio
import pytest


@pytest.mark.asyncio
async def test_main(mock_serial_connection):
    await main()
    pass


@pytest.mark.asyncio
async def test_mock_serial_generator_function(mock_serial_connection):
    # Open serial connection to Arduino
    reader, writer = await serial_asyncio.open_serial_connection(
        url="/dev/ttyACM0",  # Adjust for your Arduino port
        baudrate=115200,
    )

    while True:
        try:
            data = await reader.readline()
            decoded_data = data.decode("utf-8").strip()
            if decoded_data:
                print(f"Received data: {decoded_data}")
                await asyncio.sleep(0.5)
        except Exception as e:
            print(f"Error reading from Arduino: {e}")
            await asyncio.sleep(0.5)


def test_sine_wave():
    for interval in range(20):
        value = sine_wave_value(interval)
        print(f"i:{interval}, value={value:.2f}")
