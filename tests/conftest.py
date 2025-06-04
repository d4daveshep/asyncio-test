import itertools
import json
import math
from typing import Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


def sine_wave_value(interval: int) -> float:
    """
    Return floats between 19.0 and 21.0 using a sine function.
    Full cycle is split into 20 intervals.
    """
    intervals: int = 20
    while True:
        angle: float = (2 * math.pi * (interval % intervals)) / intervals
        sine_value: float = math.sin(angle)
        scaled_value: float = 20.0 + sine_value
        return scaled_value


def response_generator() -> Generator:
    """
    Generator that creates responses with sine wave values
    """
    counter: int = 0
    while True:
        response = {"interval": counter, "value": sine_wave_value(counter)}
        counter += 1
        yield (json.dumps(response) + "\r\n").encode()


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

    # Configure readline to return different responses
    mock_reader.readline.side_effect = response_generator()

    # Patch the serial connection
    patcher = patch("serial_asyncio.open_serial_connection", new=AsyncMock())
    mock_open = patcher.start()
    mock_open.return_value = (mock_reader, mock_writer)

    yield {
        "reader": mock_reader,
        "writer": mock_writer,
        "open_connection": mock_open,
        # "expected_responses": json_responses,
    }

    patcher.stop()
