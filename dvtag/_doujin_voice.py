__all__ = [
    "DoujinVoice",
]


from dataclasses import dataclass


@dataclass(frozen=True)
class DoujinVoice:
    id: str
    name: str
    circle: str
    seiyus: list[str]
    genres: list[str]
    image_url: str

    sale_date: str
    """ Format: {year}-{month}-{day} """
