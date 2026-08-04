import json
import requests

response = requests.get("https://valorant-api.com/v1/maps")
response.raise_for_status()

maps = response.json()["data"]

# Keep only the fields you need
maps = [
    {
        "displayName": m["displayName"],
        "splash": m["splash"]
    }
    for m in maps
    # Ignore non-playable maps like The Range
    if m["displayName"] not in ["The Range", "Basic Training"]
]

# Sort alphabetically (optional)
maps.sort(key=lambda m: m["displayName"])

with open("data/maps.json", "w", encoding="utf-8") as f:
    json.dump(maps, f, indent=4)

print("Saved", len(maps), "maps to data/maps.json")