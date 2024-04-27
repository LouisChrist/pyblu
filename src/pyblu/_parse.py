from typing import Any, TypeAlias, TypeVar, Callable

from pyblu._entities import PairedPlayer, SyncStatus, Status, Volume, PlayQueue, Preset

# pylint: disable=invalid-name
T: TypeAlias = TypeVar("T")


def chained_get(data: dict[str, Any], *keys, _map: Callable[[str], T] = lambda x: x, default: T | None = None) -> T | None:
    """Get a value from a nested dictionary.
    If the value is not found, return the default value.
    Map the value to a different type using the _map function.
    """
    local_data = data
    for key in keys:
        local_data = local_data.get(key)
        if not local_data:
            return default

    return _map(local_data)


def parse_slave_list(slaves_raw: list[dict[str, str]]) -> list[PairedPlayer] | None:
    match slaves_raw:
        case {"@id": ip, "@port": port}:
            return [PairedPlayer(ip=ip, port=int(port))]
        case [*slaves_raw]:
            return [PairedPlayer(ip=slave["@id"], port=int(slave["@port"])) for slave in slaves_raw]
        case _:
            return None


def parse_sync_status(response_dict: dict[str, Any]) -> SyncStatus:
    master_ip = chained_get(response_dict, "SyncStatus", "master", "#text")
    master_port = chained_get(response_dict, "SyncStatus", "master", "@port")
    master = PairedPlayer(ip=master_ip, port=int(master_port)) if master_ip and master_port else None

    slaves_raw = chained_get(response_dict, "SyncStatus", "slave")
    slaves = parse_slave_list(slaves_raw)

    sync_status = SyncStatus(
        etag=chained_get(response_dict, "SyncStatus", "@etag"),
        id=chained_get(response_dict, "SyncStatus", "@id"),
        mac=chained_get(response_dict, "SyncStatus", "@mac"),
        name=chained_get(response_dict, "SyncStatus", "@name"),
        image=chained_get(response_dict, "SyncStatus", "@icon"),
        initialized=chained_get(response_dict, "SyncStatus", "@initialized") == "true",
        group=chained_get(response_dict, "SyncStatus", "@group"),
        master=master,
        slaves=slaves,
        zone=chained_get(response_dict, "SyncStatus", "@zone"),
        zone_master=chained_get(response_dict, "SyncStatus", "@zoneMaster") == "true",
        zone_slave=chained_get(response_dict, "SyncStatus", "@zoneSlave") == "true",
        brand=chained_get(response_dict, "SyncStatus", "@brand"),
        model=chained_get(response_dict, "SyncStatus", "@model"),
        model_name=chained_get(response_dict, "SyncStatus", "@modelName"),
        mute_volume_db=chained_get(response_dict, "SyncStatus", "@muteDb", _map=float),
        mute_volume=chained_get(response_dict, "SyncStatus", "@muteVolume", _map=int),
        volume_db=chained_get(response_dict, "SyncStatus", "@db", _map=float),
        volume=chained_get(response_dict, "SyncStatus", "@volume", _map=int),
    )

    return sync_status


def parse_status(response_dict: dict[str, Any]) -> Status:
    name = chained_get(response_dict, "status", "name")
    if name is None:
        name = chained_get(response_dict, "status", "title1")
    artist = chained_get(response_dict, "status", "artist")
    if artist is None:
        artist = chained_get(response_dict, "status", "title2")
    album = chained_get(response_dict, "status", "album")
    if album is None:
        album = chained_get(response_dict, "status", "title3")

    status = Status(
        etag=chained_get(response_dict, "status", "@etag"),
        input_id=chained_get(response_dict, "status", "inputId"),
        service=chained_get(response_dict, "status", "service"),
        state=chained_get(response_dict, "status", "state"),
        shuffle=chained_get(response_dict, "status", "shuffle") == "1",
        album=album,
        artist=artist,
        name=name,
        image=chained_get(response_dict, "status", "image"),
        volume=chained_get(response_dict, "status", "volume", _map=int),
        volume_db=chained_get(response_dict, "status", "db", _map=float),
        mute=chained_get(response_dict, "status", "mute") == "1",
        mute_volume=chained_get(response_dict, "status", "muteVolume", _map=int),
        mute_volume_db=chained_get(response_dict, "status", "muteDb", _map=float),
        seconds=chained_get(response_dict, "status", "secs", _map=int),
        total_seconds=chained_get(response_dict, "status", "totlen", _map=float),
        can_seek=chained_get(response_dict, "status", "canSeek") == "1",
        sleep=chained_get(response_dict, "status", "sleep", _map=int, default=0),
        group_name=chained_get(response_dict, "status", "groupName"),
        group_volume=chained_get(response_dict, "status", "groupVolume", _map=int),
        indexing=chained_get(response_dict, "status", "indexing") == "1",
    )

    return status


def parse_volume(response_dict: dict[str, Any]) -> Volume:
    volume = Volume(
        volume=chained_get(response_dict, "volume", "#text", _map=int),
        db=chained_get(response_dict, "volume", "@db", _map=float),
        mute=chained_get(response_dict, "volume", "@mute") == "1",
    )

    return volume


def parse_play_queue(response_dict: dict[str, Any]) -> PlayQueue:
    play_queue = PlayQueue(
        id=chained_get(response_dict, "playlist", "@id"),
        modified=chained_get(response_dict, "playlist", "@modified") == "1",
        length=chained_get(response_dict, "playlist", "@length", _map=int),
        shuffle=chained_get(response_dict, "playlist", "@shuffle") == "1",
    )

    return play_queue


def parse_presets(response_dict: dict[str, Any]) -> list[Preset]:
    presets_raw = chained_get(response_dict, "presets", "preset")
    if not presets_raw:
        return []

    if not isinstance(presets_raw, list):
        presets_raw = [presets_raw]

    presets = [
        Preset(
            name=chained_get(x, "@name"),
            id=chained_get(x, "@id", _map=int),
            url=chained_get(x, "@url"),
            image=chained_get(x, "@image"),
            volume=chained_get(x, "@volume", _map=int),
        )
        for x in presets_raw
    ]

    return presets
