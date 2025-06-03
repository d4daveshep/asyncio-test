import pytest
import asyncio
from asyncio import AbstractEventLoop, events


def test_event_loop():
    with pytest.raises(RuntimeError):
        asyncio.get_running_loop()

        loop: AbstractEventLoop = asyncio.new_event_loop()

        assert loop == asyncio.get_event_loop()
