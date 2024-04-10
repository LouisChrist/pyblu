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


async def test_sync_status():
    with aioresponses() as mocked:
        mocked.get(
            "http://node:11000/SyncStatus",
            status=200,
            body="""
        <SyncStatus icon="/images/players/N125_nt.png" muteDb="-18" muteVolume="30"
        db="-17" modelName="NODE" model="N130"
        brand="Bluesound" initialized="true" id="1.1.1.1:11000" mac="00:11:22:33:44:55" volume="29" 
        name="Node" etag="707" schemaVersion="34" syncStat="707" class="streamer"
        group="Node +2" zone="Desk" zoneMaster="true" zoneSlave="true">
          <pairWithSub/>
          <bluetoothOutput/>
          <master port="11000">192.168.1.100</master>
          <slave port="11000" id="192.168.1.153"/>
          <slave port="11000" id="192.168.1.234"/>
        </SyncStatus>
        """,
        )
        async with BluOSDevice("node") as client:
            sync_status = await client.sync_status()

        mocked.assert_called_once()

        assert sync_status.etag == "707"
        assert sync_status.sync_stat == "707"
        assert sync_status.id == "1.1.1.1:11000"
        assert sync_status.mac == "00:11:22:33:44:55"
        assert sync_status.name == "Node"
        assert sync_status.icon_url == "/images/players/N125_nt.png"
        assert sync_status.initialized
        assert sync_status.group == "Node +2"
        assert sync_status.master == "192.168.1.100:11000"
        assert sync_status.slaves == ["192.168.1.153:11000", "192.168.1.234:11000"]
        assert sync_status.zone == "Desk"
        assert sync_status.zone_master
        assert sync_status.zone_slave
        assert sync_status.brand == "Bluesound"
        assert sync_status.model == "N130"
        assert sync_status.model_name == "NODE"
        assert sync_status.mute_volume_db == -18
        assert sync_status.mute_volume == 30
        assert sync_status.volume_db == -17
        assert sync_status.volume == 29
        assert sync_status.schema_version == 34

async def test_sync_status_one_slave():
    with aioresponses() as mocked:
        mocked.get(
            "http://node:11000/SyncStatus",
            status=200,
            body="""
        <SyncStatus>
          <slave port="11000" id="1.1.1.1"/>
        </SyncStatus>
        """,
        )

        async with BluOSDevice("node") as client:
            sync_status = await client.sync_status()

        mocked.assert_called_once()

        assert sync_status.slaves == ["1.1.1.1:11000"]
