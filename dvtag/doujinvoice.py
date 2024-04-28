from dataclasses import dataclass

__all__ = ["DoujinVoice"]


@dataclass(frozen=True)
class DoujinVoice:
    id: str
    name: str
    image_url: str
    seiyus: list[str]
    circle: str
    genres: list[str]
    sale_date: str  # {year}-{month}-{day}
