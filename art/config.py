import dataclasses
from typing import Any, Callable, Dict, List, Optional, Tuple

from art.utils import listify

config_keys: Dict[str, Callable[[Any], Any]] = {
    "dest": str,
    "file_map": lambda ents: [FileMapEntry.parse(ent) for ent in ents],
    "prepare": listify,
    "ref": str,
    "repo_url": str,
    "wrap": str,
}


@dataclasses.dataclass(frozen=True)
class FileMapEntry:
    source: str
    strip: int = 0
    rename: List[Tuple[str, str]] = dataclasses.field(default_factory=list)

    @classmethod
    def parse(cls, data_dict: dict) -> "FileMapEntry":  # type: ignore[type-arg]
        return cls(
            source=data_dict["source"],
            strip=data_dict.get("strip", 0),
            rename=[(d["from"], d["to"]) for d in data_dict.get("rename", ())],
        )


@dataclasses.dataclass()
class ArtConfig:
    work_dir: str
    dests: List[str]
    name: str
    repo_url: str
    ref: Optional[str] = None
    wrap: Optional[str] = None
    prepare: List[Any] = dataclasses.field(default_factory=list)
    file_map: List[FileMapEntry] = dataclasses.field(default_factory=list)

    def update_from(self, data: Dict[str, Any]) -> None:
        for key, cast in config_keys.items():
            if key in data:
                setattr(self, key, cast(data[key]))
