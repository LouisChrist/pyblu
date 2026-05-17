import pytest

from pyblu import PairedPlayer
from pyblu.errors import PlayerBrowseError
from pyblu.parse import (
    parse_add_follower,
    parse_browse_result,
    parse_presets,
    parse_status,
    parse_sync_status,
)


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


def test_parse_browse_root_menu():
    data = """<browse type="menu">
  <item browseKey="playlists" text="Playlists" image="/images/icon_playlists.png" type="link"></item>
  <item playURL="/Play?url=Capture%3Abluez%3Abluetooth" text="Bluetooth" image="/images/bluetooth.png" type="audio" inputType="bluetooth"></item>
  <item browseKey="ServiceA:" text="Service A" image="/images/service_a.png" type="link"></item>
</browse>"""

    result = parse_browse_result(data)

    assert result.type == "menu"
    assert result.service is None
    assert result.service_name is None
    assert result.next_key is None
    assert result.parent_key is None
    assert not result.categories
    assert len(result.items) == 3

    playlists, bluetooth, service_a = result.items

    assert playlists.type == "link"
    assert playlists.text == "Playlists"
    assert playlists.browse_key == "playlists"
    assert playlists.play_url is None
    assert playlists.input_type is None

    assert bluetooth.type == "audio"
    assert bluetooth.text == "Bluetooth"
    assert bluetooth.play_url == "Capture:bluez:bluetooth"
    assert bluetooth.browse_key is None
    assert bluetooth.input_type == "bluetooth"

    assert service_a.type == "link"
    assert service_a.browse_key == "ServiceA:"
    assert service_a.play_url is None


def test_parse_browse_empty_list():
    data = """<browse type="playlists"></browse>"""

    result = parse_browse_result(data)

    assert result.type == "playlists"
    assert not result.items
    assert not result.categories


def test_parse_browse_service_menu():
    data = """<browse serviceIcon="/icons/service_a.png" serviceName="Service A" service="ServiceA" type="items">
  <item browseKey="ServiceA:browse/category-one" text="Category One" image="/icons/cat1.png" type="link"></item>
  <item browseKey="ServiceA:browse/category-two" text="Category Two" image="/icons/cat2.png" type="link"></item>
</browse>"""

    result = parse_browse_result(data)

    assert result.type == "items"
    assert result.service == "ServiceA"
    assert result.service_name == "Service A"
    assert result.service_icon == "/icons/service_a.png"
    assert len(result.items) == 2
    assert result.items[0].browse_key == "ServiceA:browse/category-one"
    assert result.items[1].text == "Category Two"


def test_parse_browse_categories_ignore_context_menu():
    data = """<browse serviceName="Generic" type="items">
  <category text="Group One">
    <item playURL="/Play?url=Service%3Astream-1&amp;title=Station+One&amp;image=http%3A%2F%2Fexample.com%2Fcover.jpg"
          text="Station One" text2="Artist One" image="http://example.com/cover.jpg" type="audio">
      <contextMenu>
        <item actionURL="/Action?id=1" text="Action" type="favourite-add"></item>
      </contextMenu>
    </item>
    <item playURL="/Play?url=Service%3Astream-2" text="Station Two" image="http://example.com/cover2.jpg" type="audio"></item>
  </category>
  <category text="Group Two">
    <item playURL="/Play?url=Service%3Astream-3" text="Station Three" image="http://example.com/cover3.jpg" type="audio"></item>
  </category>
</browse>"""

    result = parse_browse_result(data)

    assert result.type == "items"
    assert result.service_name == "Generic"
    assert not result.items
    assert len(result.categories) == 2

    group_one, group_two = result.categories

    assert group_one.text == "Group One"
    assert len(group_one.items) == 2
    assert group_one.items[0].text == "Station One"
    assert group_one.items[0].text2 == "Artist One"
    assert group_one.items[0].play_url == "Service:stream-1"
    assert group_one.items[1].play_url == "Service:stream-2"

    assert group_two.text == "Group Two"
    assert len(group_two.items) == 1
    assert group_two.items[0].play_url == "Service:stream-3"


def test_parse_browse_pagination():
    data = """<browse type="items" nextKey="Service:opaque-next-page-key" parentKey="Service:opaque-parent-key">
  <item playURL="/Play?url=Service%3Astream-1" text="Item One" type="audio"></item>
</browse>"""

    result = parse_browse_result(data)

    assert result.next_key == "Service:opaque-next-page-key"
    assert result.parent_key == "Service:opaque-parent-key"
    assert len(result.items) == 1


def test_parse_browse_non_play_action_url_returns_none():
    # Service-specific items use /Add?service=...&playnow=1 rather than /Play?url=X.
    # The library exposes play_url=None for those — the caller cannot stream them via play_url().
    data = """<browse type="albums">
  <item playURL="/Add?service=Generic&amp;albumid=12345&amp;playnow=1" text="Album One" type="album"></item>
</browse>"""

    result = parse_browse_result(data)

    assert result.items[0].play_url is None


def test_parse_browse_error_response():
    data = """<error>
  <message>Invalid key</message>
  <detail>key was not recognised</detail>
  <detail>retry from root</detail>
</error>"""

    with pytest.raises(PlayerBrowseError) as exc_info:
        parse_browse_result(data)

    assert "Invalid key" in str(exc_info.value)
    assert exc_info.value.details == ["key was not recognised", "retry from root"]
