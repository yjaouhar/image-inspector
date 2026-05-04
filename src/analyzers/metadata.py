from __future__ import annotations

from collections.abc import Mapping

from PIL import ExifTags, Image

from models import MetadataReport


def _to_float(
    degrees: tuple[int | float, int | float, int | float]
    | tuple[tuple[int, int], tuple[int, int], tuple[int, int]]
) -> float:
    def _ratio(value: int | float | tuple[int, int]) -> float:
        # EXIF GPS values may be stored as rational numbers like (25, 1).
        if isinstance(value, tuple):
            numerator, denominator = value
            return numerator / denominator if denominator else 0.0
        return float(value)

    # Convert degrees/minutes/seconds into decimal coordinates.
    d, m, s = (_ratio(part) for part in degrees)
    return d + (m / 60.0) + (s / 3600.0)


def _normalize_gps_info(gps_info: object) -> dict[object, object] | None:
    # Pillow can expose GPS data through slightly different mapping-like objects.
    if isinstance(gps_info, Mapping):
        return dict(gps_info)

    if hasattr(gps_info, "items"):
        try:
            return dict(gps_info.items())
        except TypeError:
            return None

    return None


def _extract_gps(gps_info: Mapping[object, object] | object) -> tuple[float | None, float | None]:
    normalized = _normalize_gps_info(gps_info)
    if not normalized:
        return None, None

    # Replace numeric GPS tag ids with readable names like GPSLatitude.
    translated = {
        ExifTags.GPSTAGS.get(key, key): value
        for key, value in normalized.items()
    }

    latitude = translated.get("GPSLatitude")
    latitude_ref = translated.get("GPSLatitudeRef")
    longitude = translated.get("GPSLongitude")
    longitude_ref = translated.get("GPSLongitudeRef")

    if not latitude or not longitude:
        return None, None

    lat_value = _to_float(latitude)
    lon_value = _to_float(longitude)

    # Southern and western coordinates are represented as negative values.
    if latitude_ref == "S":
        lat_value *= -1
    if longitude_ref == "W":
        lon_value *= -1

    return lat_value, lon_value


def analyze_metadata(image_path: str) -> MetadataReport:
    with Image.open(image_path) as image:
        exif = image.getexif()

    # Translate EXIF tag ids into human-readable labels.
    translated = {
        ExifTags.TAGS.get(tag, tag): value
        for tag, value in exif.items()
    }

    latitude = None
    longitude = None

    try:
        # GPS data is stored in a dedicated EXIF IFD instead of regular tags.
        gps_ifd = exif.get_ifd(0x8825)
        if gps_ifd:
            latitude, longitude = _extract_gps(gps_ifd)
    except Exception:
        pass

    return MetadataReport(
        file_path=image_path,
        latitude=latitude,
        longitude=longitude,
        device_make=translated.get("Make"),
        device_model=translated.get("Model"),
        captured_at=translated.get("DateTimeOriginal") or translated.get("DateTime"),
        software=translated.get("Software"),
        raw_metadata={k: v for k, v in translated.items() if k != "GPSInfo"},
    )
