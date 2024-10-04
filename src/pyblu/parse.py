from urllib.parse import unquote

from lxml import etree

from pyblu.entities import Input, PairedPlayer, SyncStatus, Status, Volume, PlayQueue, Preset
from pyblu.errors import _wrap_in_unxpected_response_error


@_wrap_in_unxpected_response_error
def parse_add_slave(response: bytes) -> list[PairedPlayer]:
    """
    :raises PlayerUnexpectedResponseError: If the response is not as expected.
    """
    # pylint: disable=c-extension-no-member
    tree = etree.fromstring(response)
    slave_elements = tree.xpath("//addSlave/slave")

    return [PairedPlayer(ip=x.attrib["id"], port=int(x.attrib["port"])) for x in slave_elements]


@_wrap_in_unxpected_response_error
def parse_sync_status(response: bytes) -> SyncStatus:
    """
    :raises PlayerUnexpectedResponseError: If the response is not as expected.
    """
    # pylint: disable=c-extension-no-member
    tree = etree.fromstring(response)

    master: PairedPlayer | None = None
    master_elements = tree.xpath("//SyncStatus/master")
    if master_elements:
        master_element = master_elements[0]
        master_ip = master_element.text
        master_port = master_element.attrib["port"]
        master = PairedPlayer(ip=master_ip, port=int(master_port))

    slaves: list[PairedPlayer] | None = None
    slave_elements = tree.xpath("//SyncStatus/slave")
    if slave_elements:
        slaves = [PairedPlayer(ip=x.attrib["id"], port=int(x.attrib["port"])) for x in slave_elements]

    sync_status_elements = tree.xpath("//SyncStatus")
    assert len(sync_status_elements) == 1, "SyncStatus element not found or multiple found"
    sync_status_element = sync_status_elements[0]

    sync_status = SyncStatus(
        etag=sync_status_element.attrib["etag"],
        id=sync_status_element.attrib["id"],
        mac=sync_status_element.attrib["mac"],
        name=sync_status_element.attrib["name"],
        image=sync_status_element.attrib["icon"],
        initialized=sync_status_element.attrib.get("initialized") == "true",
        group=sync_status_element.attrib.get("group"),
        master=master,
        slaves=slaves,
        zone=sync_status_element.attrib.get("zone"),
        zone_master=sync_status_element.attrib.get("zoneMaster") == "true",
        zone_slave=sync_status_element.attrib.get("zoneMaster") == "true",
        brand=sync_status_element.attrib["brand"],
        model=sync_status_element.attrib["model"],
        model_name=sync_status_element.attrib["modelName"],
        mute_volume_db=float(sync_status_element.attrib["muteDb"]) if "muteDb" in sync_status_element.attrib else None,
        mute_volume=int(sync_status_element.attrib["muteVolume"]) if "muteVolume" in sync_status_element.attrib else None,
        volume_db=float(sync_status_element.attrib["db"]),
        volume=int(sync_status_element.attrib["volume"]),
    )

    return sync_status


@_wrap_in_unxpected_response_error
def parse_status(response: bytes) -> Status:
    """
    :raises PlayerUnexpectedResponseError: If the response is not as expected.
    """
    # pylint: disable=c-extension-no-member
    tree = etree.fromstring(response)
    status_elements = tree.xpath("//status")

    assert len(status_elements) == 1, "Status element not found or multiple found"
    status_element = status_elements[0]

    name = status_element.findtext("name")
    if name is None:
        name = status_element.findtext("title1")
    artist = status_element.findtext("artist")
    if artist is None:
        artist = status_element.findtext("title2")
    album = status_element.findtext("album")
    if album is None:
        album = status_element.findtext("title3")

    status = Status(
        etag=status_element.attrib["etag"],
        input_id=status_element.findtext("inputId"),
        service=status_element.findtext("service"),
        state=status_element.findtext("state"),
        shuffle=status_element.findtext("shuffle") == "1",
        album=album,
        artist=artist,
        name=name,
        image=status_element.findtext("image"),
        volume=int(status_element.findtext("volume")),
        volume_db=float(status_element.findtext("db")),
        mute=status_element.findtext("mute") == "1",
        mute_volume=int(status_element.findtext("muteVolume")) if status_element.findtext("muteVolume") else None,
        mute_volume_db=float(status_element.findtext("muteDb")) if status_element.findtext("muteDb") else None,
        seconds=float(status_element.findtext("secs")),
        total_seconds=float(status_element.findtext("totlen")) if status_element.findtext("totlen") else None,
        can_seek=status_element.findtext("canSeek") == "1",
        sleep=int(status_element.findtext("sleep")) if status_element.findtext("sleep") else 0,
        group_name=status_element.findtext("groupName"),
        group_volume=int(status_element.findtext("groupVolume")) if status_element.findtext("groupVolume") else None,
        indexing=status_element.findtext("indexing") == "1",
        stream_url=status_element.findtext("streamUrl"),
    )

    return status


@_wrap_in_unxpected_response_error
def parse_volume(response: bytes) -> Volume:
    """
    :raises PlayerUnexpectedResponseError: If the response is not as expected.
    """
    # pylint: disable=c-extension-no-member
    tree = etree.fromstring(response)
    volume_elements = tree.xpath("//volume")

    assert len(volume_elements) == 1, "Volume element not found or multiple found"
    volume_element = volume_elements[0]

    volume = Volume(
        volume=int(volume_element.text),
        db=float(volume_element.attrib["db"]),
        mute=volume_element.attrib.get("mute") == "1",
    )

    return volume


@_wrap_in_unxpected_response_error
def parse_play_queue(response: bytes) -> PlayQueue:
    """
    :raises PlayerUnexpectedResponseError: If the response is not as expected.
    """
    # pylint: disable=c-extension-no-member
    tree = etree.fromstring(response)
    playlist_elements = tree.xpath("//playlist")

    assert len(playlist_elements) == 1, "Playlist element not found or multiple found"
    playlist_element = playlist_elements[0]

    play_queue = PlayQueue(
        id=playlist_element.attrib["id"],
        modified=playlist_element.attrib.get("modified") == "1",
        length=int(playlist_element.attrib["length"]),
        shuffle=playlist_element.attrib.get("shuffle") == "1",
    )

    return play_queue


@_wrap_in_unxpected_response_error
def parse_presets(response: bytes) -> list[Preset]:
    """
    :raises PlayerUnexpectedResponseError: If the response is not as expected.
    """
    # pylint: disable=c-extension-no-member
    tree = etree.fromstring(response)
    preset_elements = tree.xpath("//presets/preset")

    presets = [
        Preset(
            name=x.attrib["name"],
            id=int(x.attrib["id"]),
            url=x.attrib["url"],
            image=x.attrib.get("image"),
            volume=int(x.attrib.get("volume")) if x.attrib.get("volume") else None,
        )
        for x in preset_elements
    ]

    return presets


@_wrap_in_unxpected_response_error
def parse_state(response: bytes) -> str:
    """
    :raises PlayerUnexpectedResponseError: If the response is not as expected.
    """
    # pylint: disable=c-extension-no-member
    tree = etree.fromstring(response)
    state_elements = tree.xpath("//state")

    assert len(state_elements) == 1, "State element not found or multiple found"
    state_element = state_elements[0]

    return state_element.text


@_wrap_in_unxpected_response_error
def parse_sleep(response: bytes) -> int:
    """
    :raises PlayerUnexpectedResponseError: If the response is not as expected.
    """
    # pylint: disable=c-extension-no-member
    tree = etree.fromstring(response)
    sleep_elements = tree.xpath("//sleep")

    assert len(sleep_elements) == 1, "Sleep element not found or multiple found"
    sleep_element = sleep_elements[0]

    return int(sleep_element.text) if sleep_element.text else 0


@_wrap_in_unxpected_response_error
def parse_inputs(response: bytes) -> list[Input]:
    """
    :raises PlayerUnexpectedResponseError: If the response is not as expected.
    """
    # pylint: disable=c-extension-no-member
    tree = etree.fromstring(response)
    input_elements = tree.xpath("//radiotime/item")

    inputs = [
        Input(
            id=x.attrib["id"],
            text=x.attrib["text"],
            image=x.attrib["image"],
            url=unquote(x.attrib["URL"]),
        )
        for x in input_elements
    ]

    return inputs
