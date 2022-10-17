import asyncio


async def count12():
    while True:
        print("One")
        await asyncio.sleep(1)  # await cedes control back to the event loop
        print("Two")


async def count34():
    while True:
        print("Three")
        await asyncio.sleep(1)  # await cedes control back to the event loop
        print("Four")


# async def main():
#     await asyncio.gather(count12(), count34(), count12())  # this gathers the async functions to be run


if __name__ == "__main__":

    loop = asyncio.get_event_loop()
    try:
        asyncio.ensure_future(count12())
        asyncio.ensure_future(count34())
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        print("Closing loop")
        loop.close()
