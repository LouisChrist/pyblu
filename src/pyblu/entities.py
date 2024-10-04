from dataclasses import dataclass


@dataclass
class Status:
    etag: str
    """Cursor for long polling requests. Can be passed to next status call."""

    input_id: str | None
    """Unique id of the input. Is not set for radio."""
    service: str | None
    """Service id of current input. 'Capture' for regular inputs."""

    state: str
    """Playback state"""
    shuffle: bool
    """Shuffle enabled"""

    album: str | None
    """Album name"""
    artist: str | None
    """Artist name"""
    name: str | None
    """Track name"""
    image: str | None
    """URL of the album art"""

    volume: int
    """Volume level with a range of 0-100"""
    volume_db: float
    """Volume level in dB"""

    mute: bool
    """Mute status"""
    mute_volume: int | None
    """If the player is muted, then this is the unmuted volume level. Absent if the player is not muted."""
    mute_volume_db: float | None
    """If the player is muted, then this is the unmuted volume level in dB. Absent if the player is not muted."""

    seconds: float
    """Current playback position in seconds"""
    total_seconds: float | None
    """Total track length in seconds"""
    can_seek: bool
    """True if the current track can be seeked"""

    sleep: int
    """Sleep timer in minutes. 0 means the sleep timer is off."""

    group_name: str | None
    """Name of the group the player is in. Only present on master."""
    group_volume: int | None
    """Volume level of the group. Only present on master. Range is 0-100."""

    indexing: bool
    """True if the player is currently indexing."""

    stream_url: str | None
    """The presence of this element should be treated as a flag and its contents as an opaque value. 
    Seems to be present for radio stations and to be the same as the url from the matching preset(for Radio Stations)."""


@dataclass
class PairedPlayer:
    ip: str
    """IP address of the player"""
    port: int
    """Port of the player"""


@dataclass
class SyncStatus:
    etag: str
    """Cursor for long polling requests. Can be passed to next sync_status call."""

    id: str
    """Player IP and port"""
    mac: str
    """MAC address of the player"""
    name: str
    """Name of the player"""

    image: str
    """URL of the player image"""
    initialized: bool
    """True means the player is already setup, false means the player needs to be setup"""

    group: str | None
    """Group name of the player"""
    master: PairedPlayer | None
    """Master player. Only present if the player is grouped and not master itself"""
    slaves: list[PairedPlayer] | None
    """List of slave players. Only present if the player is master"""

    zone: str | None
    """Name of the zone the player is in. Zones are fixed groups."""
    zone_master: bool | None
    """True if the player is the master of the zone, false otherwise"""
    zone_slave: bool | None
    """True if the player is a slave in the zone, false otherwise"""

    brand: str
    """Brand name of the player"""
    model: str
    """Model name of the player"""
    model_name: str
    """Model name of the player"""

    mute_volume_db: float | None
    """If the player is muted, then this is the unmuted volume level in dB. Absent if the player is not muted."""
    mute_volume: int | None
    """If the player is muted, then this is the unmuted volume level. Absent if the player is not muted."""

    volume_db: float
    """Volume level in dB"""
    volume: int
    """Volume level with a range of 0-100. -1 means fixed volume."""


@dataclass
class Volume:
    volume: int
    """Volume level with a range of 0-100"""
    db: float
    """Volume level in dB"""
    mute: bool
    """Mute status"""


@dataclass
class PlayQueue:
    id: str
    """Unique id for the current play queue state. Changes whenever the play queue changes."""
    shuffle: bool
    """PlayQueue is shuffled"""
    modified: bool
    """PlayQueue was modified since it was loaded"""
    length: int
    """Number of tracks in the play queue"""


@dataclass
class Preset:
    name: str
    """Name of the preset"""
    id: int
    """Unique id of the preset"""
    url: str
    """URL of the preset. Can be used with *play_url* to play the preset"""
    image: str | None
    """URL of the preset image"""
    volume: int | None
    """Volume level with a range of 0-100. None means the volume is not set."""


@dataclass
class Input:
    id: str
    """Unique id of the input"""
    text: str
    """User friendly name of the input"""
    image: str
    """URL of the input image"""
    url: str
    """URL to play the input. Can be passed to *play_url*"""
