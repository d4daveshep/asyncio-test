import pytest
import json
from unittest.mock import patch, AsyncMock, MagicMock


@pytest.fixture
def mock_serial_connection():
    """Fixture to create a mock serial connection for read/write operations."""
    mock_reader = AsyncMock()
    mock_writer = MagicMock()

    # Mock the close method and other writer methods
    mock_writer.close = MagicMock()
    mock_writer.write = MagicMock()
    mock_writer.drain = (
        AsyncMock()
    )  # drain() is async and waits for write buffer to empty

    # Sample JSON responses that might come back after writing commands
    json_responses = [
        {"status": "ok", "command_id": "cmd_001"},
        {"status": "ok", "command_id": "cmd_002"},
        {"status": "error", "message": "invalid command", "command_id": "cmd_003"},
    ]

    # Convert responses to bytes with newlines
    response_bytes = [(json.dumps(resp) + "\r\n").encode() for resp in json_responses]

    # Configure readline to return different responses
    mock_reader.readline.side_effect = response_bytes

    # Patch the serial connection
    patcher = patch("serial_asyncio.open_serial_connection", new=AsyncMock())
    mock_open = patcher.start()
    mock_open.return_value = (mock_reader, mock_writer)

    yield {
        "reader": mock_reader,
        "writer": mock_writer,
        "open_connection": mock_open,
        "expected_responses": json_responses,
    }

    patcher.stop()
