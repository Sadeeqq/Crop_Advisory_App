import re
from utils.exceptions import InvalidCoordinateError, InvalidDateError


def validate_coordinates(lat_str, lon_str):
    coord_pattern = r"^-?\d+(\.\d+)?$"

    if not re.match(coord_pattern, str(lat_str)) or not re.match(coord_pattern, str(lon_str)):
        raise InvalidCoordinateError('coordinates must be numeric')

    lat = float(lat_str)
    lon = float(lon_str)

    if not (-90 <= lat <= 90):
        raise InvalidCoordinateError('latitude must be between -90 and 90')

    if not (-180 <= lon <= 180):
        raise InvalidCoordinateError('longitude must be between -180 and 180')

    return lat, lon


def validate_date_format(date_str):
    date_pattern = r"^\d{4}-\d{2}-\d{2}$"
    if not re.match(date_pattern, date_str):
        raise InvalidDateError('date must be in YYYY-MM-DD format')

    return date_str
