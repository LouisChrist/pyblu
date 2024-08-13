import xmltodict

from pyblu import PairedPlayer
from pyblu._parse import parse_slave_list, parse_status


def test_parse_slave_list_no_slave():
    slaves_raw = {}
    slaves = parse_slave_list(slaves_raw)
    assert slaves is None


def test_parse_slave_list_single_element():
    slaves_raw = [
        {
            "@id": "1.1.1.1",
            "@port": "11000",
        }
    ]

    slaves = parse_slave_list(slaves_raw)

    assert slaves == [
        PairedPlayer(ip="1.1.1.1", port=11000),
    ]


def test_parse_slave_list_multiple_elements():
    slaves_raw = [
        {
            "@id": "1.1.1.1",
            "@port": "11000",
        },
        {
            "@id": "2.2.2.2",
            "@port": "11000",
        },
    ]

    slaves = parse_slave_list(slaves_raw)

    assert slaves == [
        PairedPlayer(ip="1.1.1.1", port=11000),
        PairedPlayer(ip="2.2.2.2", port=11000),
    ]


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
            
            <secs>10</secs>
            <totlen>100</totlen>
            <canSeek>1</canSeek>
            
            <sleep/>
            
            <groupName>Group</groupName>
            <groupVolume>20</groupVolume>
            
            <indexing>1</indexing>
            <streamUrl>RadioParadise:/0:4</streamUrl>
        </status>"""

    response_dict = xmltodict.parse(data)

    status = parse_status(response_dict)

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
            
            <secs>10</secs>
            <totlen>100</totlen>
            <canSeek>1</canSeek>
            
            <sleep>15</sleep>
            
            <groupName>Group</groupName>
            <groupVolume>20</groupVolume>
            
            <indexing>1</indexing>
            <streamUrl>RadioParadise:/0:4</streamUrl>
        </status>"""

    response_dict = xmltodict.parse(data)

    status = parse_status(response_dict)

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

    response_dict = xmltodict.parse(data)

    status = parse_status(response_dict)

    assert status.name == "Track Name"
    assert status.album == "Album Name"
    assert status.artist == "Artist Name"
