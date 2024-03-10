from aioresponses import aioresponses

from bluos import BluOSDevice


async def test_skip():
    with aioresponses() as mocked:
        mocked.get("http://node:11000/Skip", status=200)
        async with BluOSDevice("node") as client:
            await client.skip()

        mocked.assert_called_once()


async def test_back():
    with aioresponses() as mocked:
        mocked.get("http://node:11000/Back", status=200)
        async with BluOSDevice("node") as client:
            await client.back()

        mocked.assert_called_once()


async def test_play():
    with aioresponses() as mocked:
        mocked.get("http://node:11000/Play", status=200, body="<state>playing</state>")
        async with BluOSDevice("node") as client:
            state = await client.play()

        assert state == "playing"
        mocked.assert_called_once()


async def test_pause():
    with aioresponses() as mocked:
        mocked.get("http://node:11000/Pause", status=200, body="<state>paused</state>")
        async with BluOSDevice("node") as client:
            state = await client.pause()

        assert state == "paused"
        mocked.assert_called_once()


async def test_stop():
    with aioresponses() as mocked:
        mocked.get("http://node:11000/Stop", status=200, body="<state>stopped</state>")
        async with BluOSDevice("node") as client:
            state = await client.stop()

        assert state == "stopped"
        mocked.assert_called_once()


async def test_volume():
    with aioresponses() as mocked:
        mocked.get("http://node:11000/Volume", status=200, body="<volume db='-20.0' mute='0'>10</volume>")
        async with BluOSDevice("node") as client:
            volume = await client.volume()

        mocked.assert_called_once()

        assert volume.volume == 10
        assert volume.db == -20.0
        assert not volume.mute


async def test_status():
    with aioresponses() as mocked:
        mocked.get(
            "http://node:11000/Status",
            status=200,
            body="""
        <status etag="4e266c9fbfba6d13d1a4d6ff4bd2e1e6">
            <state>playing</state>
            <album>Album</album>
            <artist>Artist</artist>
            <title1>Name</title1>
            <image>Image</image>
            <volume>10</volume>
            <mute>0</mute>
            <secs>10</secs>
            <totlen>100</totlen>
        </status>
        """,
        )
        async with BluOSDevice("node") as client:
            status = await client.status()

        mocked.assert_called_once()

        assert status.etag == "4e266c9fbfba6d13d1a4d6ff4bd2e1e6"
        assert status.state == "playing"
        assert status.album == "Album"
        assert status.artist == "Artist"
        assert status.name == "Name"
        assert status.image == "Image"
        assert status.volume == 10
        assert not status.mute
        assert status.seconds == 10
        assert status.total_seconds == 100.0
