# pylint: skip-file
import asyncio

from bluos import BlueOSDevice, Status, entities


async def run():
    async with BlueOSDevice("node.home.louischrist.me") as client:
        status = await client.status()
        print(status)

        mac = await client.mac()
        print(mac)


def main():
    asyncio.run(run())


if __name__ == "__main__":
    main()
