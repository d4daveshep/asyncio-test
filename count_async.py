import asyncio


async def count12():
    while True:
        print("One")
        await asyncio.sleep(.5)  # await cedes control back to the event loop
        print("Two")


async def count34():
    while True:
        print("Three")
        await asyncio.sleep(2)  # await cedes control back to the event loop
        print("Four")


async def main():
    await asyncio.gather(count12(), count34())  # this gathers the co-routines to be run


if __name__ == "__main__":

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    finally:
        print("Closing loop")
