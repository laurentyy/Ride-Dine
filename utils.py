from math import radians, cos, sin, sqrt, atan2

def safe_float(value):
    try:
        return float(value) if value else 0.0  # If the value is empty or None, return 0.0
    except ValueError:
        return 0.0  # Return a default value of 0.0 for invalid numbers

def calculate_distance(coord1, coord2):
    R = 6371  # Radius of the Earth in km
    lat1, lon1 = radians(coord1[0]), radians(coord1[1])
    lat2, lon2 = radians(coord2[0]), radians(coord2[1])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    return distance
