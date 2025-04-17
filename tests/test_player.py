from urllib.parse import quote

from aioresponses import aioresponses
import pytest

from pyblu import Player, PairedPlayer
from pyblu.entities import Preset, Input


async def test_skip():
    with aioresponses() as mocked:
        mocked.get("http://node:11000/Skip", status=200)
        async with Player("node") as client:
            await client.skip()

        mocked.assert_called_once()


async def test_back():
    with aioresponses() as mocked:
        mocked.get("http://node:11000/Back", status=200)
        async with Player("node") as client:
            await client.back()

        mocked.assert_called_once()


async def test_play():
    with aioresponses() as mocked:
        mocked.get("http://node:11000/Play", status=200, body="<state>playing</state>")
        async with Player("node") as client:
            state = await client.play()

        assert state == "playing"
        mocked.assert_called_once()


async def test_pause():
    with aioresponses() as mocked:
        mocked.get("http://node:11000/Pause", status=200, body="<state>paused</state>")
        async with Player("node") as client:
            state = await client.pause()

        assert state == "paused"
        mocked.assert_called_once()


async def test_stop():
    with aioresponses() as mocked:
        mocked.get("http://node:11000/Stop", status=200, body="<state>stopped</state>")
        async with Player("node") as client:
            state = await client.stop()

        assert state == "stopped"
        mocked.assert_called_once()


async def test_volume():
    with aioresponses() as mocked:
        mocked.get("http://node:11000/Volume", status=200, body="<volume db='-20.0' mute='1'>10</volume>")
        async with Player("node") as client:
            volume = await client.volume()

        mocked.assert_called_once()

        assert volume.volume == 10
        assert volume.db == -20.0
        assert volume.mute


async def test_volume_unmute():
    with aioresponses() as mocked:
        mocked.get("http://node:11000/Volume?mute=0", status=200, body="<volume db='-20.0' mute='0'>10</volume>")
        async with Player("node") as client:
            volume = await client.volume(mute=False)

        mocked.assert_called_once()

        assert volume.volume == 10
        assert volume.db == -20.0
        assert not volume.mute


async def test_status():
    with aioresponses() as mocked:
        mocked.get(
            "http://node:11000/Status",
            status=200,
            body="""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <status etag="4e266c9fbfba6d13d1a4d6ff4bd2e1e6">
            <state>playing</state>
            <shuffle>1</shuffle>
            
            <inputId>input-1</inputId>
            <service>Capture</service>
            
            <image>Image</image>
            
            <name>Name</name>
            <artist>Artist</artist>
            <album>Album</album>
            
            <volume>10</volume>
            <db>-20.1</db>
            
            <mute>1</mute>
            <muteVolume>20</muteVolume>
            <muteDb>-20.1</muteDb>
            
            <secs>10</secs>
            <totlen>100</totlen>
            <canSeek>1</canSeek>
            
            <sleep>15</sleep>
            
            <groupName>Group</groupName>
            <groupVolume>20</groupVolume>
            
            <indexing>1</indexing>
            <streamUrl>RadioParadise:/0:4</streamUrl>
        </status>
        """,
        )
        async with Player("node") as client:
            status = await client.status()

        mocked.assert_called_once()

        assert status.etag == "4e266c9fbfba6d13d1a4d6ff4bd2e1e6"
        assert status.state == "playing"
        assert status.shuffle
        assert status.input_id == "input-1"
        assert status.service == "Capture"
        assert status.image == "Image"

        assert status.album == "Album"
        assert status.artist == "Artist"
        assert status.name == "Name"

        assert status.volume == 10
        assert status.volume_db == -20.1
        assert status.mute
        assert status.mute_volume == 20
        assert status.mute_volume_db == -20.1
        assert status.seconds == 10
        assert status.total_seconds == 100.0
        assert status.can_seek

        assert status.sleep == 15

        assert status.group_name == "Group"
        assert status.group_volume == 20
        assert status.indexing

        assert status.stream_url == "RadioParadise:/0:4"


async def test_status_timeout_missconfigured():
    async with Player("node") as client:
        with pytest.raises(ValueError, match="poll_timeout has to be smaller than timeout"):
            await client.status(etag="4e266c9fbfba6d13d1a4d6ff4bd2e1e6")


async def test_status_long_polling():
    with aioresponses() as mocked:
        mocked.get(
            "http://node:11000/Status?etag=4e266c9fbfba6d13d1a4d6ff4bd2e1e6&timeout=5",
            status=200,
            body="""<status etag="4e266c9fbfba6d13d1a4d6ff4bd2e1e6">
            <state>playing</state>
            <shuffle>1</shuffle>
            
            <inputId>input-1</inputId>
            <service>Capture</service>
            
            <image>Image</image>
            
            <name>Name</name>
            <artist>Artist</artist>
            <album>Album</album>
            
            <volume>10</volume>
            <db>-20.1</db>
            
            <mute>1</mute>
            <muteVolume>20</muteVolume>
            <muteDb>-20.1</muteDb>
            
            <secs>10</secs>
            <totlen>100</totlen>
            <canSeek>1</canSeek>
            
            <sleep>15</sleep>
            
            <groupName>Group</groupName>
            <groupVolume>20</groupVolume>
            
            <indexing>1</indexing>
            <streamUrl>RadioParadise:/0:4</streamUrl>
        </status>""",
        )

        async with Player("node") as client:
            await client.status(etag="4e266c9fbfba6d13d1a4d6ff4bd2e1e6", poll_timeout=5, timeout=10)

        mocked.assert_called_once()


async def test_sync_status():
    with aioresponses() as mocked:
        mocked.get(
            "http://node:11000/SyncStatus",
            status=200,
            body="""
        <SyncStatus icon="/images/players/N125_nt.png" muteDb="-18.1" muteVolume="30"
        db="-17.1" modelName="NODE" model="N130"
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
        async with Player("node") as client:
            sync_status = await client.sync_status()

        mocked.assert_called_once()

        assert sync_status.etag == "707"
        assert sync_status.id == "1.1.1.1:11000"
        assert sync_status.mac == "00:11:22:33:44:55"
        assert sync_status.name == "Node"
        assert sync_status.image == "/images/players/N125_nt.png"
        assert sync_status.initialized
        assert sync_status.group == "Node +2"
        assert sync_status.leader == PairedPlayer(ip="192.168.1.100", port=11000)
        assert sync_status.followers == [PairedPlayer(ip="192.168.1.153", port=11000), PairedPlayer(ip="192.168.1.234", port=11000)]
        assert sync_status.zone == "Desk"
        assert sync_status.zone_leader
        assert sync_status.zone_follower
        assert sync_status.brand == "Bluesound"
        assert sync_status.model == "N130"
        assert sync_status.model_name == "NODE"
        assert sync_status.mute_volume_db == -18.1
        assert sync_status.mute_volume == 30
        assert sync_status.volume_db == -17.1
        assert sync_status.volume == 29


async def test_sync_status_one_follower():
    with aioresponses() as mocked:
        mocked.get(
            "http://node:11000/SyncStatus",
            status=200,
            body="""
        <SyncStatus icon="/images/players/N125_nt.png" muteDb="-18.1" muteVolume="30"
        db="-17.1" modelName="NODE" model="N130"
        brand="Bluesound" initialized="true" id="1.1.1.1:11000" mac="00:11:22:33:44:55" volume="29" 
        name="Node" etag="707" schemaVersion="34" syncStat="707" class="streamer"
        group="Node +2" zone="Desk" zoneMaster="true" zoneSlave="true">
          <pairWithSub/>
          <bluetoothOutput/>
          <master port="11000">192.168.1.100</master>
          <slave port="11000" id="192.168.1.153"/>
        </SyncStatus>
        """,
        )

        async with Player("node") as client:
            sync_status = await client.sync_status()

        mocked.assert_called_once()

        assert sync_status.followers == [
            PairedPlayer(ip="192.168.1.153", port=11000),
        ]


async def test_sync_status_timeout_missconfigured():
    async with Player("node") as client:
        with pytest.raises(ValueError, match="poll_timeout has to be smaller than timeout"):
            await client.sync_status(etag="4e266c9fbfba6d13d1a4d6ff4bd2e1e6")


async def test_sync_status_long_polling():
    with aioresponses() as mocked:
        mocked.get(
            "http://node:11000/SyncStatus?etag=4e266c9fbfba6d13d1a4d6ff4bd2e1e6&timeout=5",
            status=200,
            body="""
        <SyncStatus icon="/images/players/N125_nt.png" muteDb="-18.1" muteVolume="30"
        db="-17.1" modelName="NODE" model="N130"
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

        async with Player("node") as client:
            await client.sync_status(etag="4e266c9fbfba6d13d1a4d6ff4bd2e1e6", poll_timeout=5, timeout=10)

        mocked.assert_called_once()


async def test_add_follower():
    with aioresponses() as mocked:
        mocked.get(
            "http://node:11000/AddSlave?slave=1.1.1.1&port=11000",
            status=200,
            body="""
                    <addSlave>
                        <slave id="1.1.1.1" port="11000"/>
                    </addSlave>
                    """,
        )

        async with Player("node") as client:
            followers = await client.add_follower("1.1.1.1", 11000)

        mocked.assert_called_once()

        assert followers == [
            PairedPlayer(ip="1.1.1.1", port=11000),
        ]


async def test_add_followers():
    with aioresponses() as mocked:
        mocked.get(
            "http://node:11000/AddSlave?slaves=1.1.1.1,2.2.2.2&ports=11000,11000",
            status=200,
            body="""
                    <addSlave>
                        <slave id="1.1.1.1" port="11000"/>
                        <slave id="2.2.2.2" port="11000"/>
                    </addSlave>
                    """,
        )

        async with Player("node") as client:
            followers = await client.add_followers(
                [
                    PairedPlayer(ip="1.1.1.1", port=11000),
                    PairedPlayer(ip="2.2.2.2", port=11000),
                ]
            )

        mocked.assert_called_once()

        assert followers == [
            PairedPlayer(ip="1.1.1.1", port=11000),
            PairedPlayer(ip="2.2.2.2", port=11000),
        ]


async def test_remove_follower():
    with aioresponses() as mocked:
        mocked.get(
            "http://node:11000/RemoveSlave?slave=1.1.1.1&port=11000",
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

        async with Player("node") as client:
            sync_status = await client.remove_follower("1.1.1.1", 11000)

        mocked.assert_called_once()

        assert sync_status.etag == "707"
        assert sync_status.id == "1.1.1.1:11000"
        assert sync_status.mac == "00:11:22:33:44:55"
        assert sync_status.name == "Node"
        assert sync_status.image == "/images/players/N125_nt.png"
        assert sync_status.initialized
        assert sync_status.group == "Node +2"
        assert sync_status.leader == PairedPlayer(ip="192.168.1.100", port=11000)
        assert sync_status.followers == [PairedPlayer(ip="192.168.1.153", port=11000), PairedPlayer(ip="192.168.1.234", port=11000)]
        assert sync_status.zone == "Desk"
        assert sync_status.zone_leader
        assert sync_status.zone_follower
        assert sync_status.brand == "Bluesound"
        assert sync_status.model == "N130"
        assert sync_status.model_name == "NODE"
        assert sync_status.mute_volume_db == -18
        assert sync_status.mute_volume == 30
        assert sync_status.volume_db == -17
        assert sync_status.volume == 29


async def test_remove_followers():
    with aioresponses() as mocked:
        mocked.get(
            "http://node:11000/RemoveSlave?slaves=1.1.1.1,2.2.2.2&ports=11000,11000",
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

        async with Player("node") as client:
            sync_status = await client.remove_followers(
                [
                    PairedPlayer(ip="1.1.1.1", port=11000),
                    PairedPlayer(ip="2.2.2.2", port=11000),
                ]
            )

        mocked.assert_called_once()

        assert sync_status.etag == "707"
        assert sync_status.id == "1.1.1.1:11000"
        assert sync_status.mac == "00:11:22:33:44:55"
        assert sync_status.name == "Node"
        assert sync_status.image == "/images/players/N125_nt.png"
        assert sync_status.initialized
        assert sync_status.group == "Node +2"
        assert sync_status.leader == PairedPlayer(ip="192.168.1.100", port=11000)
        assert sync_status.followers == [PairedPlayer(ip="192.168.1.153", port=11000), PairedPlayer(ip="192.168.1.234", port=11000)]
        assert sync_status.zone == "Desk"
        assert sync_status.zone_leader
        assert sync_status.zone_follower
        assert sync_status.brand == "Bluesound"
        assert sync_status.model == "N130"
        assert sync_status.model_name == "NODE"
        assert sync_status.mute_volume_db == -18
        assert sync_status.mute_volume == 30
        assert sync_status.volume_db == -17
        assert sync_status.volume == 29


async def test_shuffle():
    with aioresponses() as mocked:
        mocked.get(
            "http://node:11000/Shuffle?shuffle=1",
            status=200,
            body="""
        <playlist id="1" modified="1" length="23" shuffle="1"/>
        """,
        )
        async with Player("node") as client:
            play_queue = await client.shuffle(shuffle=True)

        mocked.assert_called_once()

        assert play_queue.id == "1"
        assert play_queue.modified
        assert play_queue.length == 23
        assert play_queue.shuffle


async def test_clear():
    with aioresponses() as mocked:
        mocked.get(
            "http://node:11000/Clear",
            status=200,
            body="""
        <playlist id="1" modified="0" length="0"/>
        """,
        )
        async with Player("node") as client:
            play_queue = await client.clear()

        mocked.assert_called_once()

        assert play_queue.id == "1"
        assert not play_queue.modified
        assert play_queue.length == 0
        assert not play_queue.shuffle


async def test_play_url():
    with aioresponses() as mocked:
        mocked.get(
            f"http://node:11000/Play?url={quote('Spotify:play')}",
            status=200,
            body="""
        <state>playing</state>
        """,
        )
        async with Player("node") as client:
            play_state = await client.play_url("Spotify:play")

        mocked.assert_called_once()

        assert play_state == "playing"


async def test_sleep_timer():
    with aioresponses() as mocked:
        mocked.get(
            "http://node:11000/Sleep",
            status=200,
            body="""
        <sleep>15</sleep>
        """,
        )
        async with Player("node") as client:
            sleep_time = await client.sleep_timer()

        mocked.assert_called_once()

        assert sleep_time == 15


async def test_sleep_timer_reset():
    with aioresponses() as mocked:
        mocked.get(
            "http://node:11000/Sleep",
            status=200,
            body="""
        <sleep/>
        """,
        )
        async with Player("node") as client:
            sleep_time = await client.sleep_timer()

        mocked.assert_called_once()

        assert sleep_time == 0


async def test_presets():
    with aioresponses() as mocked:
        mocked.get(
            "http://node:11000/Presets",
            status=200,
            body="""
        <presets prid="2">
          <preset url="Spotify:play" id="1" name="My preset" image="/Sources/images/SpotifyIcon.png"/>
          <preset url="Spotify:play" id="2" name="Second" volume="10" image="/Sources/images/SpotifyIcon.png"/>
        </presets>
        """,
        )
        async with Player("node") as client:
            presets = await client.presets()

        mocked.assert_called_once()

        assert presets == [
            Preset(id=1, name="My preset", url="Spotify:play", volume=None, image="/Sources/images/SpotifyIcon.png"),
            Preset(id=2, name="Second", url="Spotify:play", volume=10, image="/Sources/images/SpotifyIcon.png"),
        ]


async def test_presets_only_one():
    with aioresponses() as mocked:
        mocked.get(
            "http://node:11000/Presets",
            status=200,
            body="""
        <presets prid="2">
          <preset url="Spotify:play" id="1" name="My preset" image="/Sources/images/SpotifyIcon.png"/>
        </presets>
        """,
        )
        async with Player("node") as client:
            presets = await client.presets()

        mocked.assert_called_once()

        assert presets == [
            Preset(id=1, name="My preset", url="Spotify:play", volume=None, image="/Sources/images/SpotifyIcon.png"),
        ]


async def test_preset_empty():
    with aioresponses() as mocked:
        mocked.get(
            "http://node:11000/Presets",
            status=200,
            body="""
        <presets prid="6">
        </presets>
        """,
        )
        async with Player("node") as client:
            presets = await client.presets()

        mocked.assert_called_once()

        assert presets == []


async def test_load_preset():
    with aioresponses() as mocked:
        mocked.get(
            "http://node:11000/Preset?id=1",
            status=200,
            body="""
        <state>stream</state>
        """,
        )
        async with Player("node") as client:
            await client.load_preset(1)

        mocked.assert_called_once()


async def test_inputs():
    with aioresponses() as mocked:
        mocked.get(
            "http://node:11000/RadioBrowse?service=Capture",
            status=200,
            body="""
        <radiotime service="Capture">
          <item typeIndex="bluetooth-1" playerName="Node" text="Bluetooth" inputType="bluetooth" URL="Capture%3Abluez%3Abluetooth" image="/images/BluetoothIcon.png" type="audio"/>
          <item typeIndex="arc-1" playerName="Node" text="HDMI ARC" inputType="arc" id="input2" URL="Capture%3Ahw%3Aimxspdif%2C0%2F1%2F25%2F2%3Fid%3Dinput2" image="/images/capture/ic_tv.png" type="audio"/>
          <item playerName="Node" text="Spotify" id="Spotify" URL="Spotify%3Aplay" image="/Sources/images/SpotifyIcon.png" serviceType="CloudService" type="audio"/>
        </radiotime>
        """,
        )
        async with Player("node") as client:
            inputs = await client.inputs()

        mocked.assert_called_once()

        assert inputs == [
            Input(id=None, text="Bluetooth", image="/images/BluetoothIcon.png", url="Capture:bluez:bluetooth"),
            Input(id="input2", text="HDMI ARC", image="/images/capture/ic_tv.png", url="Capture:hw:imxspdif,0/1/25/2?id=input2"),
            Input(id="Spotify", text="Spotify", image="/Sources/images/SpotifyIcon.png", url="Spotify:play"),
        ]


async def test_inputs_only_one():
    with aioresponses() as mocked:
        mocked.get(
            "http://node:11000/RadioBrowse?service=Capture",
            status=200,
            body="""
        <radiotime service="Capture">
          <item typeIndex="bluetooth-1" playerName="Node" text="Bluetooth" inputType="bluetooth" id="input3" URL="Capture%3Abluez%3Abluetooth" image="/images/BluetoothIcon.png" type="audio"/>
        </radiotime>
        """,
        )
        async with Player("node") as client:
            inputs = await client.inputs()

        mocked.assert_called_once()

        assert inputs == [
            Input(id="input3", text="Bluetooth", image="/images/BluetoothIcon.png", url="Capture:bluez:bluetooth"),
        ]
