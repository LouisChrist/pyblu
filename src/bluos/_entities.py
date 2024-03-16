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
class Volume:
    volume: int
    """Volume level with a range of 0-100"""
    db: float
    """Volume level in dB"""
    mute: bool
    """Mute status"""
