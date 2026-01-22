from __future__ import annotations

from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict, Field


class SolarDataPayload(BaseModel):
    timestamp: datetime = Field(...)
    client_id: str
    current: List[float]
    power: List[float]
    energy_consumption: List[float]

    model_config = ConfigDict(extra="forbid")
