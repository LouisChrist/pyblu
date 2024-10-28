from pyblu import PairedPlayer
from pyblu.parse import parse_add_follower, parse_presets, parse_status, parse_sync_status


def test_parse_add_follower_no_follower():
    data = """<addSlave></addSlave>"""

    followers = parse_add_follower(data)

    assert followers == []


def test_parse_add_follower_single_element():
    data = """<addSlave>
            <slave id="1.1.1.1" port="11000"/>
        </addSlave>"""

    followers = parse_add_follower(data)

    assert followers == [PairedPlayer(ip="1.1.1.1", port=11000)]


def test_parse_add_follower_multiple_elements():
    data = """<addSlave>
            <slave id="1.1.1.1" port="11000"/>
            <slave id="2.2.2.2" port="11000"/>
            </addSlave>"""

    followers = parse_add_follower(data)

    assert followers == [PairedPlayer(ip="1.1.1.1", port=11000), PairedPlayer(ip="2.2.2.2", port=11000)]


def test_parse_status():
    data = """<status etag="4e266c9fbfba6d13d1a4d6ff4bd2e1e6">
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

            <secs>10.2</secs>
            <totlen>100.3</totlen>
            <canSeek>1</canSeek>

            <sleep>15</sleep>

            <groupName>Group</groupName>
            <groupVolume>20</groupVolume>

            <indexing>1</indexing>
            <streamUrl>RadioParadise:/0:4</streamUrl>
        </status>"""

    status = parse_status(data)

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
    assert status.seconds == 10.2
    assert status.total_seconds == 100.3
    assert status.can_seek

    assert status.sleep == 15

    assert status.group_name == "Group"
    assert status.group_volume == 20
    assert status.indexing

    assert status.stream_url == "RadioParadise:/0:4"


def test_parse_status_default_sleep():
    data = """<status etag="4e266c9fbfba6d13d1a4d6ff4bd2e1e6">
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
            
            <secs>10.1</secs>
            <totlen>100.1</totlen>
            <canSeek>1</canSeek>
            
            <sleep/>
            
            <groupName>Group</groupName>
            <groupVolume>20</groupVolume>
            
            <indexing>1</indexing>
            <streamUrl>RadioParadise:/0:4</streamUrl>
        </status>"""

    status = parse_status(data)

    assert status.sleep == 0


def test_parse_status_name_album_artist():
    data = """<status etag="4e266c9fbfba6d13d1a4d6ff4bd2e1e6">
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
            
            <secs>10.2</secs>
            <totlen>100.2</totlen>
            <canSeek>1</canSeek>
            
            <sleep>15</sleep>
            
            <groupName>Group</groupName>
            <groupVolume>20</groupVolume>
            
            <indexing>1</indexing>
            <streamUrl>RadioParadise:/0:4</streamUrl>
        </status>"""

    status = parse_status(data)

    assert status.name == "Name"
    assert status.album == "Album"
    assert status.artist == "Artist"


def test_parse_status_title1_title2_title3():
    data = """<status etag="4e266c9fbfba6d13d1a4d6ff4bd2e1e6">
            <state>playing</state>
            <shuffle>1</shuffle>
            
            <inputId>input-1</inputId>
            <service>Capture</service>
            
            <image>Image</image>
            
            <title1>Track Name</title1>
            <title2>Artist Name</title2>
            <title3>Album Name</title3>
            
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
        </status>"""

    status = parse_status(data)

    assert status.name == "Track Name"
    assert status.album == "Album Name"
    assert status.artist == "Artist Name"


def test_parse_sync_status_without_leader():
    data = """<SyncStatus icon="/images/players/N125_nt.png"
        db="-17.1" modelName="NODE" model="N130"
        brand="Bluesound" initialized="true" id="1.1.1.1:11000" mac="00:11:22:33:44:55" volume="29" 
        name="Node" etag="707" schemaVersion="34" syncStat="707" class="streamer">
          <pairWithSub/>
          <bluetoothOutput/>
        </SyncStatus>"""

    sync_status = parse_sync_status(data)

    assert sync_status.brand == "Bluesound"
    assert sync_status.model == "N130"
    assert sync_status.model_name == "NODE"
    assert sync_status.image == "/images/players/N125_nt.png"
    assert sync_status.volume == 29
    assert sync_status.volume_db == -17.1
    assert sync_status.initialized is True
    assert sync_status.id == "1.1.1.1:11000"
    assert sync_status.mac == "00:11:22:33:44:55"
    assert sync_status.name == "Node"
    assert sync_status.etag == "707"
    assert sync_status.zone is None
    assert sync_status.zone_leader is False
    assert sync_status.zone_follower is False
    assert sync_status.leader is None
    assert sync_status.followers is None


def test_parse_presets():
    data = """<presets prid="2">
          <preset url="Spotify:play" id="1" name="My preset"/>
          <preset url="Spotify:play" id="2" name="Second" volume="10" image="/Sources/images/SpotifyIcon.png"/>
        </presets>"""

    presets = parse_presets(data)

    assert len(presets) == 2
    assert presets[0].url == "Spotify:play"
    assert presets[0].id == 1
    assert presets[0].name == "My preset"
    assert presets[0].image is None
    assert presets[0].volume is None

    assert presets[1].url == "Spotify:play"
    assert presets[1].id == 2
    assert presets[1].name == "Second"
    assert presets[1].image == "/Sources/images/SpotifyIcon.png"
    assert presets[1].volume == 10


def test_parse_status_optionals():
    data = """<status etag="4e266c9fbfba6d13d1a4d6ff4bd2e1e6">
            <state>playing</state>
            <shuffle>1</shuffle>
            
            <volume>10</volume>
            <db>-20.1</db>
            
            <mute>1</mute>
            
            <canSeek>1</canSeek>
            
            <sleep>15</sleep>
            
            <indexing>1</indexing>
        </status>"""

    status = parse_status(data)

    assert status.input_id is None
    assert status.service is None

    assert status.album is None
    assert status.artist is None
    assert status.name is None
    assert status.image is None

    assert status.mute_volume is None
    assert status.mute_volume_db is None

    assert status.seconds is None
    assert status.total_seconds is None

    assert status.group_name is None
    assert status.group_volume is None

    assert status.stream_url is None
