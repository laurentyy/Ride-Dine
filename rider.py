import random
import json
from utils import calculate_distance

def generate_riders():
    first_names = ["Juan", "Maria", "Jose", "Anna", "Pedro", "Luis", "Carmen", "Elena"]
    last_names = ["Dela Cruz", "Santos", "Garcia", "Reyes", "Flores", "Torres", "Ramos", "Morales"]

    riders = []
    for i in range(10):
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
        location = (random.uniform(13.7800, 13.7900), random.uniform(121.0650, 121.0750))
        proximity = calculate_distance((13.7859177, 121.0706258), location)
        phone_number = f"+63{random.randint(900000000, 999999999)}"
        riders.append({
            "name": name,
            "location": location,
            "proximity": round(proximity, 2),
            "availability": random.choice([True, False]),
            "phone_number": phone_number
        })
        with open('riders.json', 'w', encoding='utf-8') as f:
            json.dump(riders, f, indent=4)

        return riders

    # Load riders data from JSON file
def load_riders():
    with open('riders.json', 'r', encoding='utf-8') as f:
        return json.load(f)
