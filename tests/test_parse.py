import pytest

from pyblu import ContextMenuAction, PairedPlayer, PlayQueueTrack
from pyblu.errors import PlayerBrowseError, PlayerCommandError, PlayerUnexpectedResponseError
from pyblu.parse import (
    parse_add_follower,
    parse_browse_result,
    parse_command_response,
    parse_context_menu,
    parse_deleted_play_queue_track,
    parse_moved_play_queue_track,
    parse_play_queue,
    parse_presets,
    parse_saved_play_queue,
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


def test_parse_play_queue_listing():
    data = """<playlist name="Calm Piano" modified="0" length="160" shuffle="1" repeat="2" id="1054">
      <song albumid="61483452" service="Deezer" artistid="6396188" songid="Deezer:487381362" id="25">
        <title>2002</title>
        <art>Anne-Marie</art>
        <alb>Speak Your Mind</alb>
        <time>185.5</time>
        <fn>Deezer:487381362</fn>
        <image>/Artwork?song=487381362</image>
      </song>
    </playlist>"""

    play_queue = parse_play_queue(data)

    assert play_queue.id == "1054"
    assert play_queue.name == "Calm Piano"
    assert not play_queue.modified
    assert play_queue.length == 160
    assert play_queue.shuffle
    assert play_queue.repeat == 2
    assert play_queue.tracks == [
        PlayQueueTrack(
            id=25,
            title="2002",
            artist="Anne-Marie",
            album="Speak Your Mind",
            filename="Deezer:487381362",
            image="/Artwork?song=487381362",
            duration=185.5,
            service="Deezer",
            song_id="Deezer:487381362",
            album_id="61483452",
            artist_id="6396188",
        )
    ]


def test_parse_play_queue_status():
    data = """<playlist>
      <length>13</length>
      <id>243</id>
      <name></name>
      <modified>1</modified>
    </playlist>"""

    play_queue = parse_play_queue(data)

    assert play_queue.id == "243"
    assert play_queue.name == ""
    assert play_queue.modified is True
    assert play_queue.length == 13
    assert play_queue.shuffle is None
    assert play_queue.repeat is None
    assert not play_queue.tracks


def test_parse_empty_play_queue_listing_with_optional_metadata():
    play_queue = parse_play_queue('<playlist length="0" repeat="0" shuffle="0" id="17"/>')

    assert play_queue.id == "17"
    assert play_queue.length == 0
    assert play_queue.name is None
    assert play_queue.modified is None
    assert play_queue.shuffle is False
    assert play_queue.repeat == 0
    assert not play_queue.tracks


def test_parse_play_queue_mutation_responses():
    assert parse_deleted_play_queue_track("<deleted>9</deleted>") == 9
    assert parse_moved_play_queue_track("<moved>moved</moved>") is None
    assert parse_saved_play_queue("<saved><entries>126</entries></saved>") == 126


def test_parse_save_empty_play_queue_error():
    with pytest.raises(PlayerCommandError, match="Cannot save an empty play queue"):
        parse_saved_play_queue("<error>empty</error>")


@pytest.mark.parametrize("data", [b"", b"<success/>", b"<state>play</state>", b"<playlist id='1'/>"])
def test_parse_successful_command_response(data: bytes):
    assert parse_command_response(data) is None


def test_parse_command_error_response():
    data = b"<error><message>Service unavailable</message><detail>Try again later</detail></error>"

    with pytest.raises(PlayerCommandError, match="Service unavailable: Try again later"):
        parse_command_response(data)


def test_parse_invalid_command_response():
    with pytest.raises(PlayerUnexpectedResponseError):
        parse_command_response(b"not XML")


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
    assert result.service_name is None
    assert result.search_key is None
    assert result.next_key is None
    assert result.parent_key is None
    assert not result.categories
    assert len(result.items) == 3

    playlists, bluetooth, service_a = result.items

    assert playlists.type == "link"
    assert playlists.text == "Playlists"
    assert playlists.browse_key == "playlists"
    assert playlists.play_action_url is None
    assert playlists.input_type is None
    assert playlists.duration is None
    assert playlists.is_favourite is None
    assert playlists.tracks is None

    assert bluetooth.type == "audio"
    assert bluetooth.text == "Bluetooth"
    assert bluetooth.play_action_url == "/Play?url=Capture%3Abluez%3Abluetooth"
    assert bluetooth.autoplay_action_url is None
    assert bluetooth.browse_key is None
    assert bluetooth.input_type == "bluetooth"

    assert service_a.type == "link"
    assert service_a.browse_key == "ServiceA:"
    assert service_a.play_action_url is None


def test_parse_browse_empty_list():
    data = """<browse type="playlists"></browse>"""

    result = parse_browse_result(data)

    assert result.type == "playlists"
    assert not result.items
    assert not result.categories


def test_parse_browse_service_menu():
    data = """<browse serviceIcon="/icons/service_a.png" serviceName="Service A" type="items">
  <item browseKey="ServiceA:browse/category-one" text="Category One" image="/icons/cat1.png" type="link"></item>
  <item browseKey="ServiceA:browse/category-two" text="Category Two" image="/icons/cat2.png" type="link"></item>
</browse>"""

    result = parse_browse_result(data)

    assert result.type == "items"
    assert result.service_name == "Service A"
    assert result.service_icon == "/icons/service_a.png"
    assert len(result.items) == 2
    assert result.items[0].browse_key == "ServiceA:browse/category-one"
    assert result.items[1].text == "Category Two"


def test_parse_browse_categories_with_context_menus():
    data = """<browse serviceName="Generic" type="items">
  <category text="Group One">
    <item playURL="/Play?url=Service%3Astream-1&amp;title=Station+One&amp;image=http%3A%2F%2Fexample.com%2Fcover.jpg"
          contextMenuKey="Generic:ContextMenu/opaque%2Fkey%3Fid%3D1" text="Station One" text2="Artist One"
          image="http://example.com/cover.jpg" type="audio">
      <contextMenu>
        <item actionURL="/Action?id=1&amp;value=opaque%2Fvalue" text="Action" type="favourite-add"></item>
      </contextMenu>
    </item>
    <item playURL="/Play?url=Service%3Astream-2" autoplayURL="/Play?url=Service%3Astream-2&amp;autofill=1"
          text="Station Two" image="http://example.com/cover2.jpg" type="audio"></item>
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
    assert group_one.items[0].play_action_url == "/Play?url=Service%3Astream-1&title=Station+One&image=http%3A%2F%2Fexample.com%2Fcover.jpg"
    assert group_one.items[0].autoplay_action_url is None
    assert group_one.items[0].context_menu_key == "Generic:ContextMenu/opaque%2Fkey%3Fid%3D1"
    assert group_one.items[0].context_menu == [ContextMenuAction(type="favourite-add", text="Action", action_url="/Action?id=1&value=opaque%2Fvalue")]
    assert group_one.items[1].play_action_url == "/Play?url=Service%3Astream-2"
    assert group_one.items[1].autoplay_action_url == "/Play?url=Service%3Astream-2&autofill=1"
    assert group_one.items[1].context_menu_key is None
    assert not group_one.items[1].context_menu

    assert group_two.text == "Group Two"
    assert len(group_two.items) == 1
    assert group_two.items[0].play_action_url == "/Play?url=Service%3Astream-3"


def test_parse_browse_search_key():
    data = """<browse serviceIcon="/Sources/images/BluOSRadioIcon.png" serviceName="Radio" searchKey="Airable:Search" type="items">
  <item browseKey="Airable:BrowseMenu/example" text="Most popular stations" type="link"></item>
</browse>"""

    result = parse_browse_result(data)

    assert result.service_name == "Radio"
    assert result.search_key == "Airable:Search"
    assert len(result.items) == 1
    assert result.items[0].text == "Most popular stations"


def test_parse_browse_pagination():
    data = """<browse type="items" nextKey="Service:opaque-next-page-key" parentKey="Service:opaque-parent-key">
  <item playURL="/Play?url=Service%3Astream-1" text="Item One" type="audio"></item>
</browse>"""

    result = parse_browse_result(data)

    assert result.next_key == "Service:opaque-next-page-key"
    assert result.parent_key == "Service:opaque-parent-key"
    assert len(result.items) == 1


def test_parse_browse_preserves_non_play_action_url():
    data = """<browse type="albums">
  <item playURL="/Add?service=Generic&amp;albumid=12345&amp;playnow=1" text="Album One" type="album"></item>
</browse>"""

    result = parse_browse_result(data)

    assert result.items[0].play_action_url == "/Add?service=Generic&albumid=12345&playnow=1"


def test_parse_browse_item_media_metadata():
    data = """<browse type="albums">
  <item browseKey="Tidal:MG/Tidal-Album?albumid=15425468" text="Graceland" text2="Paul Simon"
        duration="2596" tracks="11" isFavourite="true" type="album"/>
  <item text="2. Graceland" duration="291" isFavourite="false" type="track"/>
</browse>"""

    result = parse_browse_result(data)

    album, track = result.items
    assert album.duration == 2596
    assert album.is_favourite is True
    assert album.tracks == 11
    assert track.duration == 291
    assert track.is_favourite is False
    assert track.tracks is None


def test_parse_context_menu():
    data = """<browse type="contextMenu">
  <item actionURL="/AddFavourite?service=Airable&amp;url=opaque%3Avalue%2F1" text="Favourite" type="favourite-add"/>
  <item actionURL="/Add?file=episode%3A1&amp;playnow=-1&amp;where=last" text="Add last" type="queue-last"/>
</browse>"""

    actions = parse_context_menu(data)

    assert actions == [
        ContextMenuAction(
            type="favourite-add",
            text="Favourite",
            action_url="/AddFavourite?service=Airable&url=opaque%3Avalue%2F1",
        ),
        ContextMenuAction(
            type="queue-last",
            text="Add last",
            action_url="/Add?file=episode%3A1&playnow=-1&where=last",
        ),
    ]


def test_parse_empty_context_menu():
    assert parse_context_menu('<browse type="contextMenu"/>') == []


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
