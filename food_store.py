import json
from collections import defaultdict
from utils import safe_float

def load_food_stores():
    with open('eateries.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    food_stores = []
    stores_by_type = defaultdict(list)

    for record in data:
        store = {
            "name": record.get("name", "Unknown"),
            "type": record.get("cuisine_type", "Unknown Cuisine"),
            "proximity": float(record.get("proximity", 0)) / 1000,  # Convert meters to kilometers
            "rating": safe_float(record.get("ratings", "")),
            "fb_page": record.get("fb_page_url", "N/A"),
            "location_url": record.get("location_url", "N/A"),
            "time_availability": record.get("time", "N/A"),
            "min_price": int(record.get("min_price", 0)),
            "max_price": int(record.get("max_price", 0))
        }
        food_stores.append(store)
        stores_by_type[store["type"].lower()].append(store)

    return food_stores, stores_by_type

def recommend_stores(food_stores, stores_by_type, budget, time, proximity, cuisine):
    recommendations = []
    if cuisine in stores_by_type:
        for store in stores_by_type[cuisine]:
            if store["proximity"] <= proximity and store["min_price"] <= budget <= store["max_price"]:
                recommendations.append(store)
    return recommendations
