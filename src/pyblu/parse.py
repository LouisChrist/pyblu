from urllib.parse import parse_qs, unquote, urlsplit

from lxml import etree

from pyblu.entities import (
    BrowseCategory,
    BrowseItem,
    BrowseResult,
    ContextMenuAction,
    Input,
    PairedPlayer,
    PlayQueue,
    PlayQueueTrack,
    Preset,
    Status,
    SyncStatus,
    Volume,
)
from pyblu.errors import PlayerBrowseError, PlayerCommandError, _wrap_in_unxpected_response_error


@_wrap_in_unxpected_response_error
def parse_add_follower(response: bytes) -> list[PairedPlayer]:
    """
    :raises PlayerUnexpectedResponseError: If the response is not as expected.
    """
    # pylint: disable=c-extension-no-member
    tree = etree.fromstring(response)
    follower_elements = tree.xpath("//addSlave/slave")

    return [PairedPlayer(ip=x.attrib["id"], port=int(x.attrib["port"])) for x in follower_elements]


@_wrap_in_unxpected_response_error
def parse_sync_status(response: bytes) -> SyncStatus:
    """
    :raises PlayerUnexpectedResponseError: If the response is not as expected.
    """
    # pylint: disable=c-extension-no-member
    tree = etree.fromstring(response)

    leader: PairedPlayer | None = None
    leader_elements = tree.xpath("//SyncStatus/master")
    if leader_elements:
        leader_element = leader_elements[0]
        leader_ip = leader_element.text
        leader_port = leader_element.attrib["port"]
        leader = PairedPlayer(ip=leader_ip, port=int(leader_port))

    followers: list[PairedPlayer] | None = None
    follower_elements = tree.xpath("//SyncStatus/slave")
    if follower_elements:
        followers = [PairedPlayer(ip=x.attrib["id"], port=int(x.attrib["port"])) for x in follower_elements]

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
        leader=leader,
        followers=followers,
        zone=sync_status_element.attrib.get("zone"),
        zone_leader=sync_status_element.attrib.get("zoneMaster") == "true",
        zone_follower=sync_status_element.attrib.get("zoneSlave") == "true",
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
        seconds=float(status_element.findtext("secs")) if status_element.findtext("secs") else None,
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


def _attribute_or_child(element: etree._Element, name: str) -> str | None:
    value = element.attrib.get(name)
    return value if value is not None else element.findtext(name)


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

    queue_id = _attribute_or_child(playlist_element, "id")
    length = _attribute_or_child(playlist_element, "length")
    assert queue_id is not None, "Playlist id not found"
    assert length is not None, "Playlist length not found"

    tracks = [
        PlayQueueTrack(
            id=int(x.attrib["id"]),
            title=x.findtext("title"),
            artist=x.findtext("art"),
            album=x.findtext("alb"),
            filename=x.findtext("fn"),
            image=x.findtext("image"),
            duration=float(duration) if (duration := x.findtext("time")) is not None else None,
            service=x.attrib.get("service"),
            song_id=x.attrib.get("songid"),
            album_id=x.attrib.get("albumid"),
            artist_id=x.attrib.get("artistid"),
        )
        for x in playlist_element.xpath("./song")
    ]

    return PlayQueue(
        id=queue_id,
        modified=_attribute_or_child(playlist_element, "modified") == "1",
        length=int(length),
        shuffle=_attribute_or_child(playlist_element, "shuffle") == "1",
        name=_attribute_or_child(playlist_element, "name"),
        repeat=int(repeat) if (repeat := _attribute_or_child(playlist_element, "repeat")) is not None else None,
        tracks=tracks,
    )


@_wrap_in_unxpected_response_error
def parse_deleted_play_queue_track(response: bytes) -> int:
    """
    :raises PlayerUnexpectedResponseError: If the response is not as expected.
    """
    # pylint: disable=c-extension-no-member
    tree = etree.fromstring(response)
    deleted_elements = tree.xpath("//deleted")

    assert len(deleted_elements) == 1, "Deleted element not found or multiple found"
    assert deleted_elements[0].text is not None, "Deleted track id not found"
    return int(deleted_elements[0].text)


@_wrap_in_unxpected_response_error
def parse_moved_play_queue_track(response: bytes) -> None:
    """
    :raises PlayerUnexpectedResponseError: If the response is not as expected.
    """
    # pylint: disable=c-extension-no-member
    tree = etree.fromstring(response)
    moved_elements = tree.xpath("//moved")

    assert len(moved_elements) == 1, "Moved element not found or multiple found"
    assert moved_elements[0].text == "moved", "Track was not moved"


@_wrap_in_unxpected_response_error
def parse_saved_play_queue(response: bytes) -> int:
    """
    :raises PlayerUnexpectedResponseError: If the response is not as expected.
    """
    # pylint: disable=c-extension-no-member
    tree = etree.fromstring(response)
    if tree.tag == "error":
        error = (tree.text or "").strip()
        message = "Cannot save an empty play queue" if error == "empty" else error or "The player rejected the save command"
        raise PlayerCommandError(message)

    entries_elements = tree.xpath("//saved/entries")

    assert len(entries_elements) == 1, "Saved entries element not found or multiple found"
    assert entries_elements[0].text is not None, "Saved entry count not found"
    return int(entries_elements[0].text)


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

    assert isinstance(state_element.text, str)

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


def _context_menu_action(x: etree._Element) -> ContextMenuAction:
    return ContextMenuAction(
        type=x.attrib["type"],
        text=x.attrib.get("text"),
        action_url=x.attrib["actionURL"],
    )


def _browse_item(x: etree._Element) -> BrowseItem:
    # The url query param is extracted from the relative /Play?url=...&title=... attribute so it can be
    # passed directly to Player.play_url. Returns None when the underlying URL is not a /Play?url=X
    # (e.g. service-specific /Add?service=...&albumid=...&playnow=1).
    play_url: str | None = None
    play_url_attr = x.attrib.get("playURL")
    if play_url_attr:
        values = parse_qs(urlsplit(play_url_attr).query, keep_blank_values=True).get("url")
        if values:
            play_url = values[0]

    return BrowseItem(
        type=x.attrib["type"],
        text=x.attrib.get("text"),
        text2=x.attrib.get("text2"),
        image=x.attrib.get("image"),
        play_url=play_url,
        browse_key=x.attrib.get("browseKey"),
        input_type=x.attrib.get("inputType"),
        context_menu_key=x.attrib.get("contextMenuKey"),
        context_menu=[_context_menu_action(y) for y in x.xpath("./contextMenu/item")],
    )


def _browse_element(response: bytes) -> etree._Element:
    tree = etree.fromstring(response)

    error_elements = tree.xpath("//error")
    if error_elements:
        error_element = error_elements[0]
        message = (error_element.findtext("message") or "").strip() or "<unknown error>"
        details = [d.text.strip() for d in error_element.findall("detail") if d.text and d.text.strip()]
        raise PlayerBrowseError(message, details)

    browse_elements = tree.xpath("//browse")
    assert len(browse_elements) == 1, "Browse element not found or multiple found"
    browse_element: etree._Element = browse_elements[0]
    return browse_element


@_wrap_in_unxpected_response_error
def parse_browse_result(response: bytes) -> BrowseResult:
    """
    :raises PlayerBrowseError: If the response is a structured <error> response from /Browse.
    :raises PlayerUnexpectedResponseError: If the response is not as expected.
    """
    # pylint: disable=c-extension-no-member
    browse_element = _browse_element(response)

    items = [_browse_item(x) for x in browse_element.xpath("./item")]
    categories = [
        BrowseCategory(
            text=x.attrib.get("text"),
            next_key=x.attrib.get("nextKey"),
            parent_key=x.attrib.get("parentKey"),
            items=[_browse_item(y) for y in x.xpath("./item")],
        )
        for x in browse_element.xpath("./category")
    ]

    browse_result = BrowseResult(
        type=browse_element.attrib["type"],
        service=browse_element.attrib.get("service"),
        service_name=browse_element.attrib.get("serviceName"),
        service_icon=browse_element.attrib.get("serviceIcon"),
        search_key=browse_element.attrib.get("searchKey"),
        next_key=browse_element.attrib.get("nextKey"),
        parent_key=browse_element.attrib.get("parentKey"),
        items=items,
        categories=categories,
    )

    return browse_result


@_wrap_in_unxpected_response_error
def parse_context_menu(response: bytes) -> list[ContextMenuAction]:
    """
    :raises PlayerBrowseError: If the response is a structured <error> response from /Browse.
    :raises PlayerUnexpectedResponseError: If the response is not as expected.
    """
    # pylint: disable=c-extension-no-member
    browse_element = _browse_element(response)
    assert browse_element.attrib["type"] == "contextMenu", "Browse response is not a context menu"

    return [_context_menu_action(x) for x in browse_element.xpath("./item")]


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
            id=x.attrib.get("id"),
            text=x.attrib.get("text"),
            image=x.attrib["image"],
            url=unquote(x.attrib["URL"]),
        )
        for x in input_elements
    ]

    return inputs
