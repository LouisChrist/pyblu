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

    seconds: float | None
    """Current playback position in seconds"""
    total_seconds: float | None
    """Total track length in seconds"""
    can_seek: bool
    """True if the current track can be seeked"""

    sleep: int
    """Sleep timer in minutes. 0 means the sleep timer is off."""

    group_name: str | None
    """Name of the group the player is in. Only present on leader."""
    group_volume: int | None
    """Volume level of the group. Only present on leader. Range is 0-100."""

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
    leader: PairedPlayer | None
    """Player leading the group. Only present if the player is grouped and not leader itself"""
    followers: list[PairedPlayer] | None
    """List of following players. Only present if the player is leader of a group"""

    zone: str | None
    """Name of the zone the player is in. Zones are fixed groups."""
    zone_leader: bool | None
    """True if the player is the leader of the zone, false otherwise"""
    zone_follower: bool | None
    """True if the player is a follower in the zone, false otherwise"""

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
    id: str | None
    """Unique id of the input"""
    text: str | None
    """User friendly name of the input"""
    image: str
    """URL of the input image"""
    url: str
    """URL to play the input. Can be passed to *play_url*"""


@dataclass
class BrowseItem:
    type: str
    """Item type. Common values are "link" (descend with *browse_key*), "audio" (playable), "album", "track",
    "artist", "playlist", "folder", "section", "text". The list is open — treat unknown values as a display hint only."""
    text: str | None
    """Primary label."""
    text2: str | None
    """Secondary label (e.g. artist when the item is an album)."""
    image: str | None
    """Icon or artwork URL."""
    play_url: str | None
    """Stream URL extracted from the item's *playURL* attribute. Pass to *Player.play_url* to play it.
    *None* if the item is not directly playable or uses a non-/Play action URL (e.g. service-specific /Add)."""
    browse_key: str | None
    """Opaque key. Pass to *Player.browse* to descend into this item. *None* if the item is a leaf."""
    input_type: str | None
    """Input kind for items that represent a physical input (e.g. "bluetooth", "arc", "spdif"). Usually only set on the root menu."""


@dataclass
class BrowseCategory:
    text: str | None
    """Category heading."""
    next_key: str | None
    """Opaque key for the next page of items in this category. Pass to *Player.browse*."""
    parent_key: str | None
    """Opaque key for navigating up from this category. Pass to *Player.browse*."""
    items: list[BrowseItem]
    """Items in this category."""


@dataclass
class BrowseResult:
    type: str
    """Result list type. Common values are "menu", "items", "albums", "tracks", "playlists", "sections", "folders"."""
    service: str | None
    """Service id (e.g. "TuneIn", "Deezer"). Not for UI display."""
    service_name: str | None
    """Human-readable service name, suitable for UI."""
    service_icon: str | None
    """URL of an icon for the service."""
    next_key: str | None
    """Opaque key for the next page of results. Pass to *Player.browse*."""
    parent_key: str | None
    """Opaque key for navigating up the hierarchy. Pass to *Player.browse*."""
    items: list[BrowseItem]
    """Top-level items. Empty when the response is grouped into *categories*."""
    categories: list[BrowseCategory]
    """Categories. Empty unless the response groups items under headings."""
