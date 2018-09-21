from art.utils import listify

config_keys = {
    "dest": str,
    "file_map": lambda ents: [FileMapEntry.parse(ent) for ent in ents],
    "prepare": listify,
    "ref": str,
    "repo_url": str,
    "wrap": str,
}


class FileMapEntry:
    def __init__(self, source, strip=0, rename=()):
        self.source = source
        self.strip = int(strip)
        self.rename = list(rename)

    @classmethod
    def parse(cls, data_dict):
        return cls(
            source=data_dict["source"],
            strip=data_dict.get("strip", 0),
            rename=[(d["from"], d["to"]) for d in data_dict.get("rename", ())],
        )


class ArtConfig:
    def __init__(self):
        self.work_dir = None
        self.dest = None
        self.name = None
        self.repo_url = None
        self.ref = None
        self.prepare = []
        self.file_map = []
        self.wrap = None

    def update_from(self, data):
        for key, cast in config_keys.items():
            if key in data:
                setattr(self, key, cast(data[key]))
