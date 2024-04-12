from pyblu import PairedPlayer
from pyblu._parse import parse_slave_list


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
