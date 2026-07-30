# pylint: disable=too-many-lines

from unittest.mock import AsyncMock, MagicMock
from urllib.parse import quote

import aiohttp
from mocket import async_mocketize, Mocket
from mocket.mocks.mockhttp import Entry
from mocket.plugins.aiohttp_connector import MocketTCPConnector
import pytest

from pyblu import ContextMenuAction, Player, PairedPlayer
from pyblu.entities import Preset, Input
from pyblu.errors import PlayerBrowseError, PlayerCommandError, PlayerUnreachableError


@async_mocketize(strict_mode=True)
async def test_skip():
    Entry.single_register(Entry.GET, "http://node:11000/Skip", status=200)
    async with aiohttp.ClientSession(connector=MocketTCPConnector()) as session:
        async with Player("node", session=session) as client:
            await client.skip()

    assert len(Mocket.request_list()) == 1


@async_mocketize(strict_mode=True)
async def test_back():
    Entry.single_register(Entry.GET, "http://node:11000/Back", status=200)
    async with aiohttp.ClientSession(connector=MocketTCPConnector()) as session:
        async with Player("node", session=session) as client:
            await client.back()

    assert len(Mocket.request_list()) == 1


@async_mocketize(strict_mode=True)
async def test_play():
    Entry.single_register(Entry.GET, "http://node:11000/Play", status=200, body="<state>playing</state>")
    async with aiohttp.ClientSession(connector=MocketTCPConnector()) as session:
        async with Player("node", session=session) as client:
            state = await client.play()

    assert state == "playing"
    assert len(Mocket.request_list()) == 1


@async_mocketize(strict_mode=True)
async def test_pause():
    Entry.single_register(Entry.GET, "http://node:11000/Pause", status=200, body="<state>paused</state>")
    async with aiohttp.ClientSession(connector=MocketTCPConnector()) as session:
        async with Player("node", session=session) as client:
            state = await client.pause()

    assert state == "paused"
    assert len(Mocket.request_list()) == 1


@async_mocketize(strict_mode=True)
async def test_pause_toggle_true():
    Entry.single_register(Entry.GET, "http://node:11000/Pause?toggle=1", status=200, body="<state>playing</state>")
    async with aiohttp.ClientSession(connector=MocketTCPConnector()) as session:
        async with Player("node", session=session) as client:
            state = await client.pause(toggle=True)

    assert state == "playing"
    assert len(Mocket.request_list()) == 1


@async_mocketize(strict_mode=True)
async def test_pause_toggle_false():
    Entry.single_register(Entry.GET, "http://node:11000/Pause?toggle=0", status=200, body="<state>paused</state>")
    async with aiohttp.ClientSession(connector=MocketTCPConnector()) as session:
        async with Player("node", session=session) as client:
            state = await client.pause(toggle=False)

    assert state == "paused"
    assert len(Mocket.request_list()) == 1


@async_mocketize(strict_mode=True)
async def test_stop():
    Entry.single_register(Entry.GET, "http://node:11000/Stop", status=200, body="<state>stopped</state>")
    async with aiohttp.ClientSession(connector=MocketTCPConnector()) as session:
        async with Player("node", session=session) as client:
            state = await client.stop()

    assert state == "stopped"
    assert len(Mocket.request_list()) == 1


@async_mocketize(strict_mode=True)
async def test_volume():
    Entry.single_register(Entry.GET, "http://node:11000/Volume", status=200, body="<volume db='-20.0' mute='1'>10</volume>")
    async with aiohttp.ClientSession(connector=MocketTCPConnector()) as session:
        async with Player("node", session=session) as client:
            volume = await client.volume()

    assert len(Mocket.request_list()) == 1

    assert volume.volume == 10
    assert volume.db == -20.0
    assert volume.mute


@async_mocketize(strict_mode=True)
async def test_volume_unmute():
    Entry.single_register(Entry.GET, "http://node:11000/Volume?mute=0", status=200, body="<volume db='-20.0' mute='0'>10</volume>")
    async with aiohttp.ClientSession(connector=MocketTCPConnector()) as session:
        async with Player("node", session=session) as client:
            volume = await client.volume(mute=False)

    assert len(Mocket.request_list()) == 1

    assert volume.volume == 10
    assert volume.db == -20.0
    assert not volume.mute


@async_mocketize(strict_mode=True)
async def test_status():
    Entry.single_register(
        Entry.GET,
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
    async with aiohttp.ClientSession(connector=MocketTCPConnector()) as session:
        async with Player("node", session=session) as client:
            status = await client.status()

    assert len(Mocket.request_list()) == 1

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


@async_mocketize(strict_mode=True)
async def test_status_long_polling():
    Entry.single_register(
        Entry.GET,
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

    async with aiohttp.ClientSession(connector=MocketTCPConnector()) as session:
        async with Player("node", session=session) as client:
            await client.status(etag="4e266c9fbfba6d13d1a4d6ff4bd2e1e6", poll_timeout=5, timeout=10)

    assert len(Mocket.request_list()) == 1


@async_mocketize(strict_mode=True)
async def test_sync_status():
    Entry.single_register(
        Entry.GET,
        "http://node:11000/SyncStatus",
        status=200,
        body="""
    <SyncStatus icon="/images/players/N125_nt.png" muteDb="-18.1" muteVolume="30"
    db="-17.1" modelName="NODE" model="N130"
    brand="Bluesound" initialized="true" id="1.1.1.1:11000" mac="00:11:22:33:44:55" volume="29"
    name="Node" etag="707" schemaVersion="34" syncStat="707" class="streamer"
    group="Node +2" zone="Desk" zoneMaster="true" zoneSlave="false">
      <pairWithSub/>
      <bluetoothOutput/>
      <master port="11000">192.168.1.100</master>
      <slave port="11000" id="192.168.1.153"/>
      <slave port="11000" id="192.168.1.234"/>
    </SyncStatus>
    """,
    )
    async with aiohttp.ClientSession(connector=MocketTCPConnector()) as session:
        async with Player("node", session=session) as client:
            sync_status = await client.sync_status()

    assert len(Mocket.request_list()) == 1

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
    assert sync_status.zone_follower is False
    assert sync_status.brand == "Bluesound"
    assert sync_status.model == "N130"
    assert sync_status.model_name == "NODE"
    assert sync_status.mute_volume_db == -18.1
    assert sync_status.mute_volume == 30
    assert sync_status.volume_db == -17.1
    assert sync_status.volume == 29


@async_mocketize(strict_mode=True)
async def test_sync_status_one_follower():
    Entry.single_register(
        Entry.GET,
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

    async with aiohttp.ClientSession(connector=MocketTCPConnector()) as session:
        async with Player("node", session=session) as client:
            sync_status = await client.sync_status()

    assert len(Mocket.request_list()) == 1

    assert sync_status.followers == [
        PairedPlayer(ip="192.168.1.153", port=11000),
    ]


async def test_sync_status_timeout_missconfigured():
    async with Player("node") as client:
        with pytest.raises(ValueError, match="poll_timeout has to be smaller than timeout"):
            await client.sync_status(etag="4e266c9fbfba6d13d1a4d6ff4bd2e1e6")


@async_mocketize(strict_mode=True)
async def test_sync_status_long_polling():
    Entry.single_register(
        Entry.GET,
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

    async with aiohttp.ClientSession(connector=MocketTCPConnector()) as session:
        async with Player("node", session=session) as client:
            await client.sync_status(etag="4e266c9fbfba6d13d1a4d6ff4bd2e1e6", poll_timeout=5, timeout=10)

    assert len(Mocket.request_list()) == 1


@async_mocketize(strict_mode=True)
async def test_add_follower():
    Entry.single_register(
        Entry.GET,
        "http://node:11000/AddSlave?slave=1.1.1.1&port=11000",
        status=200,
        body="""
                <addSlave>
                    <slave id="1.1.1.1" port="11000"/>
                </addSlave>
                """,
    )

    async with aiohttp.ClientSession(connector=MocketTCPConnector()) as session:
        async with Player("node", session=session) as client:
            followers = await client.add_follower("1.1.1.1", 11000)

    assert len(Mocket.request_list()) == 1

    assert followers == [
        PairedPlayer(ip="1.1.1.1", port=11000),
    ]


@async_mocketize(strict_mode=True)
async def test_add_followers():
    Entry.single_register(
        Entry.GET,
        "http://node:11000/AddSlave?slaves=1.1.1.1,2.2.2.2&ports=11000,11000",
        status=200,
        body="""
                <addSlave>
                    <slave id="1.1.1.1" port="11000"/>
                    <slave id="2.2.2.2" port="11000"/>
                </addSlave>
                """,
    )

    async with aiohttp.ClientSession(connector=MocketTCPConnector()) as session:
        async with Player("node", session=session) as client:
            followers = await client.add_followers(
                [
                    PairedPlayer(ip="1.1.1.1", port=11000),
                    PairedPlayer(ip="2.2.2.2", port=11000),
                ]
            )

    assert len(Mocket.request_list()) == 1

    assert followers == [
        PairedPlayer(ip="1.1.1.1", port=11000),
        PairedPlayer(ip="2.2.2.2", port=11000),
    ]


@async_mocketize(strict_mode=True)
async def test_remove_follower():
    Entry.single_register(
        Entry.GET,
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

    async with aiohttp.ClientSession(connector=MocketTCPConnector()) as session:
        async with Player("node", session=session) as client:
            sync_status = await client.remove_follower("1.1.1.1", 11000)

    assert len(Mocket.request_list()) == 1

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


@async_mocketize(strict_mode=True)
async def test_remove_followers():
    Entry.single_register(
        Entry.GET,
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

    async with aiohttp.ClientSession(connector=MocketTCPConnector()) as session:
        async with Player("node", session=session) as client:
            sync_status = await client.remove_followers(
                [
                    PairedPlayer(ip="1.1.1.1", port=11000),
                    PairedPlayer(ip="2.2.2.2", port=11000),
                ]
            )

    assert len(Mocket.request_list()) == 1

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


@async_mocketize(strict_mode=True)
async def test_shuffle():
    Entry.single_register(
        Entry.GET,
        "http://node:11000/Shuffle?state=1",
        status=200,
        body="""
    <playlist id="1" modified="1" length="23" shuffle="1"/>
    """,
    )
    async with aiohttp.ClientSession(connector=MocketTCPConnector()) as session:
        async with Player("node", session=session) as client:
            play_queue = await client.shuffle(shuffle=True)

    assert len(Mocket.request_list()) == 1

    assert play_queue.id == "1"
    assert play_queue.modified
    assert play_queue.length == 23
    assert play_queue.shuffle


@async_mocketize(strict_mode=True)
async def test_clear():
    Entry.single_register(
        Entry.GET,
        "http://node:11000/Clear",
        status=200,
        body="""
    <playlist id="1" modified="0" length="0"/>
    """,
    )
    async with aiohttp.ClientSession(connector=MocketTCPConnector()) as session:
        async with Player("node", session=session) as client:
            play_queue = await client.clear()

    assert len(Mocket.request_list()) == 1

    assert play_queue.id == "1"
    assert play_queue.modified is False
    assert play_queue.length == 0
    assert play_queue.shuffle is None


@async_mocketize(strict_mode=True)
async def test_play_queue():
    Entry.single_register(
        Entry.GET,
        "http://node:11000/Playlist",
        status=200,
        body="""<playlist name="Queue" modified="1" length="1" shuffle="0" repeat="2" id="12">
          <song songid="Service:track-1" service="Service" id="0">
            <title>Track</title><art>Artist</art><alb>Album</alb><fn>Service:track-1</fn>
          </song>
        </playlist>""",
    )
    async with aiohttp.ClientSession(connector=MocketTCPConnector()) as session:
        async with Player("node", session=session) as client:
            play_queue = await client.play_queue()

    assert len(Mocket.request_list()) == 1
    assert play_queue.name == "Queue"
    assert play_queue.length == 1
    assert play_queue.repeat == 2
    assert play_queue.tracks[0].title == "Track"
    assert play_queue.tracks[0].id == 0


@async_mocketize(strict_mode=True)
async def test_play_queue_status_only():
    Entry.single_register(
        Entry.GET,
        "http://node:11000/Playlist?length=1",
        status=200,
        body="<playlist><length>3</length><id>15</id><modified>1</modified></playlist>",
    )
    async with aiohttp.ClientSession(connector=MocketTCPConnector()) as session:
        async with Player("node", session=session) as client:
            play_queue = await client.play_queue(status_only=True)

    assert len(Mocket.request_list()) == 1
    assert play_queue.id == "15"
    assert play_queue.length == 3
    assert play_queue.name is None
    assert play_queue.modified is True
    assert play_queue.shuffle is None
    assert play_queue.repeat is None
    assert play_queue.tracks == []


@async_mocketize(strict_mode=True)
async def test_play_queue_page():
    Entry.single_register(
        Entry.GET,
        "http://node:11000/Playlist?start=10&end=19",
        status=200,
        body='<playlist modified="0" length="30" id="16"><song id="10"><title>Track 10</title></song></playlist>',
    )
    async with aiohttp.ClientSession(connector=MocketTCPConnector()) as session:
        async with Player("node", session=session) as client:
            play_queue = await client.play_queue(start=10, end=19)

    assert len(Mocket.request_list()) == 1
    assert play_queue.length == 30
    assert play_queue.modified is False
    assert play_queue.shuffle is None
    assert play_queue.tracks[0].id == 10


async def test_play_queue_rejects_incomplete_or_conflicting_pagination():
    async with Player("node") as client:
        with pytest.raises(ValueError, match="start and end"):
            await client.play_queue(start=0)
        with pytest.raises(ValueError, match="status_only"):
            await client.play_queue(start=0, end=9, status_only=True)


@async_mocketize(strict_mode=True)
async def test_delete_play_queue_track():
    Entry.single_register(Entry.GET, "http://node:11000/Delete?id=9", status=200, body="<deleted>9</deleted>")
    async with aiohttp.ClientSession(connector=MocketTCPConnector()) as session:
        async with Player("node", session=session) as client:
            deleted_id = await client.delete_play_queue_track(9)

    assert len(Mocket.request_list()) == 1
    assert deleted_id == 9


@async_mocketize(strict_mode=True)
async def test_move_play_queue_track():
    Entry.single_register(Entry.GET, "http://node:11000/Move?new=8&old=2", status=200, body="<moved>moved</moved>")
    async with aiohttp.ClientSession(connector=MocketTCPConnector()) as session:
        async with Player("node", session=session) as client:
            await client.move_play_queue_track(old_position=2, new_position=8)

    assert len(Mocket.request_list()) == 1


@async_mocketize(strict_mode=True)
async def test_save_play_queue():
    Entry.single_register(Entry.GET, "http://node:11000/Save?name=Dinner+Music", status=200, body="<saved><entries>126</entries></saved>")
    async with aiohttp.ClientSession(connector=MocketTCPConnector()) as session:
        async with Player("node", session=session) as client:
            entries = await client.save_play_queue("Dinner Music")

    assert len(Mocket.request_list()) == 1
    assert entries == 126


@async_mocketize(strict_mode=True)
async def test_save_empty_play_queue():
    Entry.single_register(Entry.GET, "http://node:11000/Save?name=Empty", status=200, body="<error>empty</error>")
    async with aiohttp.ClientSession(connector=MocketTCPConnector()) as session:
        async with Player("node", session=session) as client:
            with pytest.raises(PlayerCommandError, match="Cannot save an empty play queue"):
                await client.save_play_queue("Empty")

    assert len(Mocket.request_list()) == 1


@async_mocketize(strict_mode=True)
async def test_play_url():
    Entry.single_register(
        Entry.GET,
        f"http://node:11000/Play?url={quote('Spotify:play')}",
        status=200,
        body="""
    <state>playing</state>
    """,
    )
    async with aiohttp.ClientSession(connector=MocketTCPConnector()) as session:
        async with Player("node", session=session) as client:
            play_state = await client.play_url("Spotify:play")

    assert len(Mocket.request_list()) == 1

    assert play_state == "playing"


@async_mocketize(strict_mode=True)
async def test_sleep_timer():
    Entry.single_register(
        Entry.GET,
        "http://node:11000/Sleep",
        status=200,
        body="""
    <sleep>15</sleep>
    """,
    )
    async with aiohttp.ClientSession(connector=MocketTCPConnector()) as session:
        async with Player("node", session=session) as client:
            sleep_time = await client.sleep_timer()

    assert len(Mocket.request_list()) == 1

    assert sleep_time == 15


@async_mocketize(strict_mode=True)
async def test_sleep_timer_reset():
    Entry.single_register(
        Entry.GET,
        "http://node:11000/Sleep",
        status=200,
        body="""
    <sleep/>
    """,
    )
    async with aiohttp.ClientSession(connector=MocketTCPConnector()) as session:
        async with Player("node", session=session) as client:
            sleep_time = await client.sleep_timer()

    assert len(Mocket.request_list()) == 1

    assert sleep_time == 0


@async_mocketize(strict_mode=True)
async def test_presets():
    Entry.single_register(
        Entry.GET,
        "http://node:11000/Presets",
        status=200,
        body="""
    <presets prid="2">
      <preset url="Spotify:play" id="1" name="My preset" image="/Sources/images/SpotifyIcon.png"/>
      <preset url="Spotify:play" id="2" name="Second" volume="10" image="/Sources/images/SpotifyIcon.png"/>
    </presets>
    """,
    )
    async with aiohttp.ClientSession(connector=MocketTCPConnector()) as session:
        async with Player("node", session=session) as client:
            presets = await client.presets()

    assert len(Mocket.request_list()) == 1

    assert presets == [
        Preset(id=1, name="My preset", url="Spotify:play", volume=None, image="/Sources/images/SpotifyIcon.png"),
        Preset(id=2, name="Second", url="Spotify:play", volume=10, image="/Sources/images/SpotifyIcon.png"),
    ]


@async_mocketize(strict_mode=True)
async def test_presets_only_one():
    Entry.single_register(
        Entry.GET,
        "http://node:11000/Presets",
        status=200,
        body="""
    <presets prid="2">
      <preset url="Spotify:play" id="1" name="My preset" image="/Sources/images/SpotifyIcon.png"/>
    </presets>
    """,
    )
    async with aiohttp.ClientSession(connector=MocketTCPConnector()) as session:
        async with Player("node", session=session) as client:
            presets = await client.presets()

    assert len(Mocket.request_list()) == 1

    assert presets == [
        Preset(id=1, name="My preset", url="Spotify:play", volume=None, image="/Sources/images/SpotifyIcon.png"),
    ]


@async_mocketize(strict_mode=True)
async def test_preset_empty():
    Entry.single_register(
        Entry.GET,
        "http://node:11000/Presets",
        status=200,
        body="""
    <presets prid="6">
    </presets>
    """,
    )
    async with aiohttp.ClientSession(connector=MocketTCPConnector()) as session:
        async with Player("node", session=session) as client:
            presets = await client.presets()

    assert len(Mocket.request_list()) == 1

    assert presets == []


@async_mocketize(strict_mode=True)
async def test_load_preset():
    Entry.single_register(
        Entry.GET,
        "http://node:11000/Preset?id=1",
        status=200,
        body="""
    <state>stream</state>
    """,
    )
    async with aiohttp.ClientSession(connector=MocketTCPConnector()) as session:
        async with Player("node", session=session) as client:
            await client.load_preset(1)

    assert len(Mocket.request_list()) == 1


@async_mocketize(strict_mode=True)
async def test_inputs():
    Entry.single_register(
        Entry.GET,
        "http://node:11000/RadioBrowse?service=Capture",
        status=200,
        body="""
    <radiotime service="Capture">
      <item typeIndex="bluetooth-1" playerName="Node" text="Bluetooth" inputType="bluetooth" URL="Capture%3Abluez%3Abluetooth" image="/images/BluetoothIcon.png" type="audio"/>
      <item typeIndex="arc-1" playerName="Node" text="HDMI ARC" inputType="arc" id="input2" URL="Capture%3Ahw%3Aimxspdif%2C0%2F1%2F25%2F2%3Fid%3Dinput2" image="/images/capture/ic_tv.png" type="audio"/>
      <item playerName="Node" text="Spotify" id="Spotify" URL="Spotify%3Aplay" image="/Sources/images/SpotifyIcon.png" serviceType="CloudService" type="audio"/>
      <item id="xdynamic-Source7" type="audio" inputType="analog" URL="Capture%3Ahw%3Asoundchassis%2C0%2F1%2F25%2F2%3Fid%3Dxdynamic-Source7" image="/images/capture/ic_analoginput.png"/>
    </radiotime>
    """,
    )
    async with aiohttp.ClientSession(connector=MocketTCPConnector()) as session:
        async with Player("node", session=session) as client:
            inputs = await client.inputs()

    assert len(Mocket.request_list()) == 1

    assert inputs == [
        Input(id=None, text="Bluetooth", image="/images/BluetoothIcon.png", url="Capture:bluez:bluetooth"),
        Input(id="input2", text="HDMI ARC", image="/images/capture/ic_tv.png", url="Capture:hw:imxspdif,0/1/25/2?id=input2"),
        Input(id="Spotify", text="Spotify", image="/Sources/images/SpotifyIcon.png", url="Spotify:play"),
        Input(id="xdynamic-Source7", text=None, image="/images/capture/ic_analoginput.png", url="Capture:hw:soundchassis,0/1/25/2?id=xdynamic-Source7"),
    ]


@async_mocketize(strict_mode=True)
async def test_inputs_only_one():
    Entry.single_register(
        Entry.GET,
        "http://node:11000/RadioBrowse?service=Capture",
        status=200,
        body="""
    <radiotime service="Capture">
      <item typeIndex="bluetooth-1" playerName="Node" text="Bluetooth" inputType="bluetooth" id="input3" URL="Capture%3Abluez%3Abluetooth" image="/images/BluetoothIcon.png" type="audio"/>
    </radiotime>
    """,
    )
    async with aiohttp.ClientSession(connector=MocketTCPConnector()) as session:
        async with Player("node", session=session) as client:
            inputs = await client.inputs()

    assert len(Mocket.request_list()) == 1

    assert inputs == [
        Input(id="input3", text="Bluetooth", image="/images/BluetoothIcon.png", url="Capture:bluez:bluetooth"),
    ]


def _player_with_failing_session(exc: Exception) -> Player:
    session = MagicMock()
    session.get.return_value.__aenter__ = AsyncMock(side_effect=exc)
    session.get.return_value.__aexit__ = AsyncMock(return_value=False)
    return Player("node", session=session)


async def test_get_maps_timeout_to_unreachable():
    player = _player_with_failing_session(TimeoutError())
    with pytest.raises(PlayerUnreachableError):
        await player.status()


async def test_get_maps_connection_error_to_unreachable():
    player = _player_with_failing_session(aiohttp.ClientConnectionError())
    with pytest.raises(PlayerUnreachableError):
        await player.status()


@async_mocketize(strict_mode=True)
async def test_browse_root():
    Entry.single_register(
        Entry.GET,
        "http://node:11000/Browse",
        status=200,
        body="""
        <browse type="menu">
          <item browseKey="playlists" text="Playlists" image="/images/p.png" type="link"/>
          <item playURL="/Play?url=Capture%3Abluez%3Abluetooth" text="Bluetooth" image="/images/b.png" type="audio" inputType="bluetooth"/>
        </browse>
        """,
    )
    async with aiohttp.ClientSession(connector=MocketTCPConnector()) as session:
        async with Player("node", session=session) as client:
            result = await client.browse()

    assert len(Mocket.request_list()) == 1

    assert result.type == "menu"
    assert len(result.items) == 2
    assert result.items[0].browse_key == "playlists"
    assert result.items[1].play_action_url == "/Play?url=Capture%3Abluez%3Abluetooth"
    assert result.items[1].input_type == "bluetooth"


@async_mocketize(strict_mode=True)
async def test_browse_with_key():
    Entry.single_register(
        Entry.GET,
        f"http://node:11000/Browse?key={quote('ServiceA:')}",
        status=200,
        body="""<browse type="items" serviceName="Service A"/>""",
    )
    async with aiohttp.ClientSession(connector=MocketTCPConnector()) as session:
        async with Player("node", session=session) as client:
            result = await client.browse(key="ServiceA:")

    assert len(Mocket.request_list()) == 1

    assert result.type == "items"
    assert result.service_name == "Service A"
    assert not result.items


@async_mocketize(strict_mode=True)
async def test_browse_with_inline_context_menu_items():
    Entry.single_register(
        Entry.GET,
        f"http://node:11000/Browse?key={quote('ServiceA:albums')}&withContextMenuItems=1",
        status=200,
        body="""<browse type="albums">
          <item playURL="/Add?service=ServiceA&amp;albumid=1&amp;playnow=1" text="Album" type="album">
            <contextMenu>
              <item actionURL="/Add?service=ServiceA&amp;albumid=1" text="Add" type="add-last"/>
            </contextMenu>
          </item>
        </browse>""",
    )
    async with aiohttp.ClientSession(connector=MocketTCPConnector()) as session:
        async with Player("node", session=session) as client:
            result = await client.browse(key="ServiceA:albums", with_context_menu_items=True)

    assert len(Mocket.request_list()) == 1
    assert result.items[0].context_menu == [ContextMenuAction(type="add-last", text="Add", action_url="/Add?service=ServiceA&albumid=1")]


@async_mocketize(strict_mode=True)
async def test_browse_search():
    Entry.single_register(
        Entry.GET,
        f"http://node:11000/Browse?key={quote('Airable:Search')}&q=jazz",
        status=200,
        body="""
        <browse serviceName="Radio" searchKey="Airable:Search" type="menu">
          <item browseKey="Airable:BrowseMenu/stations" text="Stations" type="link"/>
          <item browseKey="Airable:BrowseMenu/podcasts" text="Podcasts" type="link"/>
        </browse>
        """,
    )
    async with aiohttp.ClientSession(connector=MocketTCPConnector()) as session:
        async with Player("node", session=session) as client:
            result = await client.browse(key="Airable:Search", q="jazz")

    assert len(Mocket.request_list()) == 1

    assert result.search_key == "Airable:Search"
    assert len(result.items) == 2
    assert result.items[0].text == "Stations"
    assert result.items[1].browse_key == "Airable:BrowseMenu/podcasts"


@async_mocketize(strict_mode=True)
async def test_browse_error_response():
    Entry.single_register(
        Entry.GET,
        "http://node:11000/Browse?key=bad",
        status=200,
        body="<error><message>Invalid key</message><detail>not recognised</detail></error>",
    )
    async with aiohttp.ClientSession(connector=MocketTCPConnector()) as session:
        async with Player("node", session=session) as client:
            with pytest.raises(PlayerBrowseError) as exc_info:
                await client.browse(key="bad")

    assert "Invalid key" in str(exc_info.value)
    assert exc_info.value.details == ["not recognised"]


@pytest.mark.parametrize(
    "action_url",
    [
        "/Play?url=Service%3Astream-1&title=Station+One",
        "/Add?service=ServiceA&albumid=1&autofill=1",
        "/AddFavourite?service=Airable&url=opaque%3Astation%2F1",
    ],
)
@async_mocketize(strict_mode=True)
async def test_execute_action(action_url: str):
    Entry.single_register(Entry.GET, f"http://node:11000{action_url}", status=200, body="<success/>")

    async with aiohttp.ClientSession(connector=MocketTCPConnector()) as session:
        async with Player("node", session=session) as client:
            await client.execute_action(action_url)

    assert len(Mocket.request_list()) == 1


@async_mocketize(strict_mode=True)
async def test_execute_action_command_error():
    action_url = "/Add?service=ServiceA&albumid=1&playnow=1"
    Entry.single_register(
        Entry.GET,
        f"http://node:11000{action_url}",
        status=200,
        body="<error><message>Service unavailable</message></error>",
    )
    async with aiohttp.ClientSession(connector=MocketTCPConnector()) as session:
        async with Player("node", session=session) as client:
            with pytest.raises(PlayerCommandError, match="Service unavailable"):
                await client.execute_action(action_url)

    assert len(Mocket.request_list()) == 1


@async_mocketize(strict_mode=True)
async def test_context_menu():
    key = "Airable:ContextMenu/opaque?url=station%3A1&hasInfo=1"
    Entry.single_register(
        Entry.GET,
        f"http://node:11000/Browse?key={quote(key)}",
        status=200,
        body="""
        <browse type="contextMenu">
          <item actionURL="/AddFavourite?service=Airable&amp;url=opaque%3Astation%2F1" text="Favourite" type="favourite-add"/>
        </browse>
        """,
    )
    async with aiohttp.ClientSession(connector=MocketTCPConnector()) as session:
        async with Player("node", session=session) as client:
            actions = await client.context_menu(key)

    assert len(Mocket.request_list()) == 1
    assert actions == [
        ContextMenuAction(
            type="favourite-add",
            text="Favourite",
            action_url="/AddFavourite?service=Airable&url=opaque%3Astation%2F1",
        )
    ]
