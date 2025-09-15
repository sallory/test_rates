from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class PointDTO:
    assetName: str
    time: int
    assetId: int
    value: float

    def to_dict(self):
        return asdict(self)
