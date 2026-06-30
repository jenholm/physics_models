"""Sector state representation for inflationary domains."""

from dataclasses import dataclass, field
from typing import Optional, Any


@dataclass
class Sector:
    """State of an inflationary sector / pocket universe."""
    phi: float
    pi: float = 0.0
    V: Optional[float] = None
    vacuum: Optional[int] = None
    N: float = 0.0
    parent: Optional["Sector"] = None
    sector_id: int = 0
    theta: Optional[dict] = None

    def __post_init__(self):
        if self.V is None:
            self.V = self.phi**2  # placeholder, updated externally

    def to_dict(self) -> dict:
        return {
            "phi": self.phi,
            "pi": self.pi,
            "V": self.V,
            "vacuum": self.vacuum,
            "N": self.N,
            "parent_id": self.parent.sector_id if self.parent else None,
            "sector_id": self.sector_id,
            "theta": self.theta,
        }
