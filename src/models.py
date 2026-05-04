from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class MetadataReport:
    # Structured metadata analysis result.
    file_path: str
    latitude: float | None = None
    longitude: float | None = None
    device_make: str | None = None
    device_model: str | None = None
    captured_at: str | None = None
    software :str | None = None
    raw_metadata: dict[str, object] = field(default_factory=dict)


@dataclass(slots=True)
class SteganographyReport:
    # Structured hidden-data analysis result.
    file_path: str
    hidden_text: str | None = None
    detected_format: str | None = None
