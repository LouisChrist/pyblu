from dataclasses import dataclass


@dataclass
class Status:
    etag: str
    """Cursor for long polling requests. Can be passed to next status call."""
    state: str
    """Playback state"""

    album: str
    """Album name"""
    artist: str
    """Artist name"""
    name: str
    """Track name"""
    image: str
    """URL of the album art"""

    volume: int
    """Volume level with a range of 0-100"""
    mute: bool
    """Mute status"""
    seconds: int
    """Current playback position in seconds"""
    total_seconds: float
    """Total track length in seconds"""


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
    sync_stat: str
    """Id of sync status. Changes whenever the sync status changes."""

    id: str
    """Player IP and port"""
    mac: str
    """MAC address of the player"""
    name: str
    """Name of the player"""

    icon_url: str
    """URL of the player icon"""
    initialized: bool
    """True means the player is already setup, false means the player needs to be setup"""

    group: str | None
    """Group name of the player"""
    master: PairedPlayer | None
    """Master player IP and port. Only present if the player is grouped and not master itself"""
    slaves: PairedPlayer | None
    """List of slave players. Every entry is IP and port. Only present if the player is master"""

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

    mute_volume_db: int | None
    """If the player is muted, then this is the unmuted volume level in dB"""
    mute_volume: int | None
    """If the player is muted, then this is the unmuted volume level"""

    volume_db: float
    """Volume level in dB"""
    volume: int
    """Volume level with a range of 0-100. -1 means fixed volume."""

    schema_version: int
    """Software schema version"""


@dataclass
class Volume:
    volume: int
    """Volume level with a range of 0-100"""
    db: float
    """Volume level in dB"""
    mute: bool
    """Mute status"""
