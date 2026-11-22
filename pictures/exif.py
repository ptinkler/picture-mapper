"""Read the GPS position out of a photo's EXIF data."""

from __future__ import annotations

from decimal import Decimal
from typing import IO

from PIL import ExifTags, Image, UnidentifiedImageError

GPS_LATITUDE_REF, GPS_LATITUDE, GPS_LONGITUDE_REF, GPS_LONGITUDE = 1, 2, 3, 4


def _degrees(dms: tuple, ref: str, negative: str) -> Decimal:
    degrees, minutes, seconds = (Decimal(str(float(part))) for part in dms)
    value = degrees + minutes / 60 + seconds / 3600
    return -value if ref == negative else value


def gps_position(file: IO[bytes]) -> tuple[Decimal, Decimal] | None:
    """Return ``(latitude, longitude)`` rounded to six places, or ``None`` if the photo has none."""
    try:
        with Image.open(file) as image:
            gps = image.getexif().get_ifd(ExifTags.IFD.GPSInfo)
    except (UnidentifiedImageError, OSError, SyntaxError, ValueError):
        return None
    finally:
        file.seek(0)
    try:
        latitude = _degrees(gps[GPS_LATITUDE], gps[GPS_LATITUDE_REF], "S")
        longitude = _degrees(gps[GPS_LONGITUDE], gps[GPS_LONGITUDE_REF], "W")
    except (KeyError, TypeError, ValueError, ZeroDivisionError, ArithmeticError):
        return None
    if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):  # noqa: PLR2004
        return None
    quantum = Decimal("0.000001")
    return latitude.quantize(quantum), longitude.quantize(quantum)
