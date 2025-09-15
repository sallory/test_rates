from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class AssetDTO:
    id: int
    symbol: str

    def to_dict(self):
        return asdict(self)
