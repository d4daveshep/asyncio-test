import asyncio
from asyncio import Task
import time


async def say_after(delay, what):
    await asyncio.sleep(delay)
    print(what)


async def main():
    ## create some coroutine tasks
    tasks: list[Task] = [
        asyncio.create_task(say_after(1, "hello")),
        asyncio.create_task(say_after(2, "world")),
    ]

    print(f"started at {time.strftime('%X')}")

    # await task1
    # await task2

    # run the tasks concurrently
    await asyncio.gather(*tasks)

    print(f"finished at {time.strftime('%X')}")


asyncio.run(main())
