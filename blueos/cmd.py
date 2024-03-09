import asyncio

from blueos import BlueOS, Status, entities


async def run():
    async with BlueOS("node.home.louischrist.me") as client:
        status = await client.status()
        print(status)

        mac = await client.mac()
        print(mac)


def main():
    asyncio.run(run())


if __name__ == "__main__":
    main()
