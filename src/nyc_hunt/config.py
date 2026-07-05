"""Load and validate config.toml. All user specs live there, nothing hardcoded."""
import tomllib
from dataclasses import dataclass, field
from pathlib import Path


class ConfigError(Exception):
    pass


@dataclass
class Search:
    name: str
    max_price: int
    beds_min: float = 0
    beds_max: float = 99
    baths_min: float = 0


@dataclass
class Email:
    enabled: bool = False
    to: str = ""
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""


@dataclass
class Config:
    move_in: str = ""
    no_fee_preferred: bool = True
    commute_anchor: str = ""
    searches: list[Search] = field(default_factory=list)
    tier1: list[str] = field(default_factory=list)
    tier2: list[str] = field(default_factory=list)
    email: Email = field(default_factory=Email)

    def search_by_name(self, name: str) -> Search | None:
        return next((s for s in self.searches if s.name == name), None)


def load(path: str | Path) -> Config:
    raw = tomllib.loads(Path(path).read_text())
    searches = []
    for s in raw.get("search", []):
        if "name" not in s or "max_price" not in s:
            raise ConfigError(f"[[search]] needs name and max_price: {s}")
        searches.append(Search(
            name=s["name"],
            max_price=int(s["max_price"]),
            beds_min=float(s.get("beds_min", 0)),
            beds_max=float(s.get("beds_max", 99)),
            baths_min=float(s.get("baths_min", 0)),
        ))
    if not searches:
        raise ConfigError("config needs at least one [[search]] block")
    hunt, areas, em = raw.get("hunt", {}), raw.get("areas", {}), raw.get("email", {})
    return Config(
        move_in=hunt.get("move_in", ""),
        no_fee_preferred=hunt.get("no_fee_preferred", True),
        commute_anchor=hunt.get("commute_anchor", ""),
        searches=searches,
        tier1=areas.get("tier1", []),
        tier2=areas.get("tier2", []),
        email=Email(
            enabled=em.get("enabled", False),
            to=em.get("to", ""),
            smtp_host=em.get("smtp_host", "smtp.gmail.com"),
            smtp_port=int(em.get("smtp_port", 587)),
            smtp_user=em.get("smtp_user", ""),
        ),
    )
