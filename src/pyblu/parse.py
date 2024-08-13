from typing import Any, TypeVar, Callable

from lxml import etree

from pyblu.entities import PairedPlayer, SyncStatus, Status, Volume, PlayQueue, Preset

# pylint: disable=invalid-name
T = TypeVar("T")


def chained_get_optional(data: dict[str, Any], *keys, _map: Callable[[str], T] | None = None, default: T | None = None) -> T | None:
    """Get a value from a nested dictionary.
    If the value is not found, return the default value.
    Map the value to a different type using the _map function.
    """
    local_data = data
    for key in keys[:-1]:
        nested_data = local_data.get(key)
        if not isinstance(nested_data, dict):
            return default

        local_data = nested_data

    last_key = keys[-1]
    value = local_data.get(last_key)

    if _map is not None and value is not None:
        return _map(value)

    return value if value is not None else default


def chained_get(data: dict[str, Any], *keys, _map: Callable[[str], T] | None = None, default: T | None = None) -> T:
    """Get a value from a nested dictionary.
    If the value is not found, raise a KeyError.
    Map the value to a different type using the _map function.
    """
    value = chained_get_optional(data, *keys, _map=_map, default=default)
    if value is None:
        raise KeyError(f"Key '{keys[-1]}' not found")

    return value


def parse_slave_list(slaves_raw: Any) -> list[PairedPlayer] | None:
    match slaves_raw:
        case {"@id": ip, "@port": port}:
            return [PairedPlayer(ip=ip, port=int(port))]
        case [*slaves_raw_match]:
            return [PairedPlayer(ip=slave["@id"], port=int(slave["@port"])) for slave in slaves_raw_match]  # type: ignore
        case _:
            return None


def parse_sync_status(response_dict: dict[str, Any]) -> SyncStatus:
    master_ip: str | None = chained_get_optional(response_dict, "SyncStatus", "master", "#text")
    master_port: str | None = chained_get_optional(response_dict, "SyncStatus", "master", "@port")
    master = PairedPlayer(ip=master_ip, port=int(master_port)) if master_ip and master_port else None

    slaves_raw: Any = chained_get_optional(response_dict, "SyncStatus", "slave")
    slaves = parse_slave_list(slaves_raw)

    sync_status = SyncStatus(
        etag=chained_get(response_dict, "SyncStatus", "@etag"),
        id=chained_get(response_dict, "SyncStatus", "@id"),
        mac=chained_get(response_dict, "SyncStatus", "@mac"),
        name=chained_get(response_dict, "SyncStatus", "@name"),
        image=chained_get(response_dict, "SyncStatus", "@icon"),
        initialized=chained_get_optional(response_dict, "SyncStatus", "@initialized") == "true",
        group=chained_get_optional(response_dict, "SyncStatus", "@group"),
        master=master,
        slaves=slaves,
        zone=chained_get_optional(response_dict, "SyncStatus", "@zone"),
        zone_master=chained_get_optional(response_dict, "SyncStatus", "@zoneMaster") == "true",
        zone_slave=chained_get_optional(response_dict, "SyncStatus", "@zoneSlave") == "true",
        brand=chained_get(response_dict, "SyncStatus", "@brand"),
        model=chained_get(response_dict, "SyncStatus", "@model"),
        model_name=chained_get(response_dict, "SyncStatus", "@modelName"),
        mute_volume_db=chained_get_optional(response_dict, "SyncStatus", "@muteDb", _map=float),
        mute_volume=chained_get_optional(response_dict, "SyncStatus", "@muteVolume", _map=int),
        volume_db=chained_get(response_dict, "SyncStatus", "@db", _map=float),
        volume=chained_get(response_dict, "SyncStatus", "@volume", _map=int),
    )

    return sync_status


def parse_status(response_dict: dict[str, Any]) -> Status:
    name = chained_get_optional(response_dict, "status", "name")
    if name is None:
        name = chained_get_optional(response_dict, "status", "title1")
    artist = chained_get_optional(response_dict, "status", "artist")
    if artist is None:
        artist = chained_get_optional(response_dict, "status", "title2")
    album = chained_get_optional(response_dict, "status", "album")
    if album is None:
        album = chained_get_optional(response_dict, "status", "title3")

    status = Status(
        etag=chained_get(response_dict, "status", "@etag"),
        input_id=chained_get_optional(response_dict, "status", "inputId"),
        service=chained_get_optional(response_dict, "status", "service"),
        state=chained_get(response_dict, "status", "state"),
        shuffle=chained_get_optional(response_dict, "status", "shuffle") == "1",
        album=album,
        artist=artist,
        name=name,
        image=chained_get_optional(response_dict, "status", "image"),
        volume=chained_get(response_dict, "status", "volume", _map=int),
        volume_db=chained_get(response_dict, "status", "db", _map=float),
        mute=chained_get_optional(response_dict, "status", "mute") == "1",
        mute_volume=chained_get_optional(response_dict, "status", "muteVolume", _map=int),
        mute_volume_db=chained_get_optional(response_dict, "status", "muteDb", _map=float),
        seconds=chained_get(response_dict, "status", "secs", _map=int),
        total_seconds=chained_get_optional(response_dict, "status", "totlen", _map=float),
        can_seek=chained_get_optional(response_dict, "status", "canSeek") == "1",
        sleep=chained_get(response_dict, "status", "sleep", _map=int, default=0),
        group_name=chained_get_optional(response_dict, "status", "groupName"),
        group_volume=chained_get_optional(response_dict, "status", "groupVolume", _map=int),
        indexing=chained_get_optional(response_dict, "status", "indexing") == "1",
        stream_url=chained_get_optional(response_dict, "status", "streamUrl"),
    )

    return status


def parse_volume(response: str) -> Volume:
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


def parse_play_queue(response: str) -> PlayQueue:
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


def parse_presets(response: str) -> list[Preset]:
    tree = etree.fromstring(response)
    preset_elements = tree.xpath("//presets/preset")

    presets = [
        Preset(
            name=x.attrib["name"],
            id=int(x.attrib["id"]),
            url=x.attrib["url"],
            image=x.attrib["image"],
            volume=int(x.attrib.get("volume")) if x.attrib.get("volume") else None,
        )
        for x in preset_elements
    ]

    return presets
