from dataclasses import dataclass


@dataclass
class URL:
    url: str


@dataclass
class Extra:
    owner: str
    language_stats: dict[str, str]


class Result(URL):
    extra: Extra | None = None
