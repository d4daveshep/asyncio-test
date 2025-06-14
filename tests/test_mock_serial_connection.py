import pytest
import json
import asyncio
import serial_asyncio


# Example functions that write to serial port
async def send_command_to_device(command, port="/dev/ttyACM0", baudrate=115200):
    """Send a single command to the device and return the response."""
    reader, writer = await serial_asyncio.open_serial_connection(
        url=port, baudrate=baudrate
    )

    try:
        # Send the command
        command_bytes = (json.dumps(command) + "\n").encode()
        writer.write(command_bytes)
        await writer.drain()  # Wait for data to be sent

        # Read the response
        response_line = await reader.readline()
        response = json.loads(response_line.decode("utf-8").strip())

        return response
    finally:
        writer.close()


async def send_multiple_commands(commands, port="/dev/ttyACM0", baudrate=115200):
    """Send multiple commands and collect all responses."""
    reader, writer = await serial_asyncio.open_serial_connection(
        url=port, baudrate=baudrate
    )

    responses = []
    try:
        for cmd in commands:
            # Send command
            command_bytes = (json.dumps(cmd) + "\n").encode()
            writer.write(command_bytes)
            await writer.drain()

            # Read response
            response_line = await reader.readline()
            response = json.loads(response_line.decode("utf-8").strip())
            responses.append(response)

            # Small delay between commands
            await asyncio.sleep(0.1)

        return responses
    finally:
        writer.close()


async def configure_device_settings(settings, port="/dev/ttyACM0", baudrate=115200):
    """Send configuration settings to device and verify they were applied."""
    reader, writer = await serial_asyncio.open_serial_connection(
        url=port, baudrate=baudrate
    )

    try:
        # Send configuration command
        config_command = {"action": "configure", "settings": settings}

        command_bytes = (json.dumps(config_command) + "\n").encode()
        writer.write(command_bytes)
        await writer.drain()

        # Read acknowledgment
        response_line = await reader.readline()
        response = json.loads(response_line.decode("utf-8").strip())

        if response.get("status") != "ok":
            raise ValueError(f"Configuration failed: {response}")

        return response

    finally:
        writer.close()


# Test cases for writing to serial port
@pytest.mark.asyncio
async def test_send_single_command(mock_serial_connection):
    """Test sending a single command to the device."""
    command = {"action": "get_status", "id": "cmd_001"}

    response = await send_command_to_device(command)

    # Verify the connection was opened
    mock_serial_connection["open_connection"].assert_called_once_with(
        url="/dev/ttyACM0", baudrate=115200
    )

    # Verify the command was written correctly
    expected_bytes = (json.dumps(command) + "\n").encode()
    mock_serial_connection["writer"].write.assert_called_once_with(expected_bytes)

    # Verify drain was called to ensure data was sent
    mock_serial_connection["writer"].drain.assert_called_once()

    # Verify the response
    assert response == mock_serial_connection["expected_responses"][0]

    # Verify connection was closed
    mock_serial_connection["writer"].close.assert_called_once()


@pytest.mark.asyncio
async def test_send_multiple_commands(mock_serial_connection):
    """Test sending multiple commands in sequence."""
    commands = [
        {"action": "get_status", "id": "cmd_001"},
        {"action": "reset", "id": "cmd_002"},
    ]

    responses = await send_multiple_commands(commands)

    # Verify connection was opened once
    mock_serial_connection["open_connection"].assert_called_once()

    # Verify both commands were written
    assert mock_serial_connection["writer"].write.call_count == 2

    # Check the actual data that was written
    write_calls = mock_serial_connection["writer"].write.call_args_list

    expected_first_write = (json.dumps(commands[0]) + "\n").encode()
    expected_second_write = (json.dumps(commands[1]) + "\n").encode()

    assert write_calls[0][0][0] == expected_first_write
    assert write_calls[1][0][0] == expected_second_write

    # Verify drain was called for each command
    assert mock_serial_connection["writer"].drain.call_count == 2

    # Verify responses
    expected_responses = mock_serial_connection["expected_responses"][:2]
    assert responses == expected_responses


@pytest.mark.asyncio
async def test_configure_device_settings(mock_serial_connection):
    """Test sending configuration settings to device."""
    settings = {
        "temperature_threshold": 25.0,
        "humidity_threshold": 60.0,
        "reporting_interval": 30,
    }

    response = await configure_device_settings(settings)

    # Verify the configuration command was constructed correctly
    expected_command = {"action": "configure", "settings": settings}
    expected_bytes = (json.dumps(expected_command) + "\n").encode()

    mock_serial_connection["writer"].write.assert_called_once_with(expected_bytes)

    # Verify response handling
    assert response == mock_serial_connection["expected_responses"][0]


@pytest.mark.asyncio
async def test_write_with_custom_port_and_baudrate(mock_serial_connection):
    """Test that custom port and baudrate parameters are passed correctly."""
    command = {"action": "test"}
    custom_port = "/dev/ttyACM0"
    custom_baudrate = 115200

    await send_command_to_device(command, port=custom_port, baudrate=custom_baudrate)

    # Verify the connection was opened with custom parameters
    mock_serial_connection["open_connection"].assert_called_once_with(
        url=custom_port, baudrate=custom_baudrate
    )


@pytest.mark.asyncio
async def test_write_error_handling(mock_serial_connection):
    """Test error handling when device returns error response."""
    # Configure mock to return an error response
    error_response = {"status": "error", "message": "invalid command"}
    mock_serial_connection["reader"].readline.side_effect = [
        (json.dumps(error_response) + "\r\n").encode()
    ]

    settings = {"invalid_setting": "bad_value"}

    # This should raise an error due to the error response
    with pytest.raises(ValueError, match="Configuration failed"):
        await configure_device_settings(settings)


@pytest.mark.asyncio
async def test_writer_drain_called_properly(mock_serial_connection):
    """Test that writer.drain() is called to ensure data transmission."""
    command = {"action": "ping"}

    await send_command_to_device(command)

    # Verify that drain was called after write
    assert mock_serial_connection["writer"].drain.called

    # Check the order: write should be called before drain
    write_call_order = []

    def track_write(*args):
        write_call_order.append("write")

    def track_drain():
        write_call_order.append("drain")

    # Reset and reconfigure mocks to track call order
    mock_serial_connection["writer"].write.side_effect = track_write
    mock_serial_connection["writer"].drain.side_effect = track_drain

    await send_command_to_device(command)

    # Verify the order
    assert write_call_order == ["write", "drain"]


# Example of testing binary data writes
@pytest.mark.asyncio
async def test_write_binary_data(mock_serial_connection):
    """Test writing binary data instead of JSON."""

    async def send_binary_command(data_bytes, port="/dev/ttyACM0"):
        reader, writer = await serial_asyncio.open_serial_connection(
            url=port, baudrate=115200
        )
        try:
            writer.write(data_bytes)
            await writer.drain()
            response = await reader.readline()
            return response
        finally:
            writer.close()

    binary_data = b"\x01\x02\x03\x04\x05"

    await send_binary_command(binary_data)

    # Verify the binary data was written correctly
    mock_serial_connection["writer"].write.assert_called_with(binary_data)
