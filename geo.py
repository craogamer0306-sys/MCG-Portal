import math, json, os

def haversine_m(lat1, lon1, lat2, lon2):
    R = 6371000.0
    dlat = math.radians(lat2-lat1); dlon = math.radians(lon2-lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dlon/2)**2
    return 2*R*math.asin(math.sqrt(a))

def nearest_branch(lat, lon):
    branches = json.loads(os.getenv("BRANCHES_JSON","[]"))
    best = None
    for b in branches:
        d = haversine_m(lat, lon, b["lat"], b["lon"])
        if best is None or d < best["distance_m"]:
            best = {"name": b["name"], "distance_m": d, "radius_m": b.get("radius_m", 500)}
    return best
