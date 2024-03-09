from dataclasses import dataclass


@dataclass
class Status:
    etag: str
    state: str

    album: str
    artist: str
    name: str
    image: str

    volume: int
    mute: bool
    seconds: int
    total_seconds: float


@dataclass
class Volume:
    volume: int
    db: float
    mute: bool
