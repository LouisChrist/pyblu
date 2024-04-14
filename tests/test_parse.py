import xmltodict

from pyblu import PairedPlayer
from pyblu._parse import parse_slave_list, parse_status


def test_sync_status_no_slave():
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
                <sleep/>
            </status>"""

    response_dict = xmltodict.parse(data)

    status = parse_status(response_dict)

    assert status.sleep == 0
