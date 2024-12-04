import random
from math import radians, cos, sin, sqrt, atan2
import json
import heapq
from collections import defaultdict


def safe_float(value):
    try:
        return float(value) if value else 0.0  # If the value is empty or None, return 0.0
    except ValueError:
        return 0.0  # Return a default value of 0.0 for invalid numbers


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
            "rating": safe_float(record.get("ratings", "")),  # Use safe_float to handle empty or invalid ratings
            "fb_page": record.get("fb_page_url", "N/A"),
            "location_url": record.get("location_url", "N/A"),
            "time_availability": record.get("time", "N/A"),
            "min_price": int(record.get("min_price", 0)),
            "max_price": int(record.get("max_price", 0))
        }
        food_stores.append(store)
        stores_by_type[store["type"].lower()].append(store)

    return food_stores, stores_by_type


# Generate random rider data and save to JSON file
def generate_riders():
    first_names = ["Juan", "Maria", "Jose", "Anna", "Pedro", "Luis", "Carmen", "Elena"]
    last_names = ["Dela Cruz", "Santos", "Garcia", "Reyes", "Flores", "Torres", "Ramos", "Morales"]

    riders = []
    for i in range(10):
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
        location = (random.uniform(13.7800, 13.7900), random.uniform(121.0650, 121.0750))
        proximity = calculate_distance((13.7859177, 121.0706258), location)
        phone_number = f"+63{random.randint(900000000, 999999999)}"  # Generate random Philippine number
        riders.append({
            "name": name,
            "location": location,
            "proximity": round(proximity, 2),
            "availability": random.choice([True, False]),
            "phone_number": phone_number  # Add phone number to rider's data
        })

        with open('riders.json', 'w', encoding='utf-8') as f:
            json.dump(riders, f, indent=4)

        return riders

    # Load riders data from JSON file
    def load_riders():
        with open('riders.json', 'r', encoding='utf-8') as f:
            return json.load(f)


# Function to calculate distance between two coordinates using Haversine formula
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


# Function to handle user input with validation
def get_user_input():
    print("Ride&Dine: Welcome to the Integrated Dining and Logistics Recommendation System!")

    while True:
        try:
            budget = float(input("Enter your budget (e.g., 200): "))
            if budget <= 0:
                raise ValueError("Budget must be a positive number.")
            break
        except ValueError as e:
            print(f"Invalid input. {e}. Please try again.")

    while True:
        preferred_time = input("What time do you prefer to eat? (HH:MM in 24-hour format): ")
        if len(preferred_time) == 5 and preferred_time[2] == ":" and preferred_time[:2].isdigit() and preferred_time[
                                                                                                      3:].isdigit():
            hours, minutes = map(int, preferred_time.split(":"))
            if 0 <= hours < 24 and 0 <= minutes < 60:
                break
            else:
                print("Invalid time format. Please enter a valid time between 00:00 and 23:59.")
        else:
            print("Invalid input format. Please use the HH:MM format.")

    while True:
        try:
            proximity_range = float(input("Choose proximity range (in km, e.g., 0.5 for 500m): "))
            if proximity_range <= 0:
                raise ValueError("Proximity must be a positive number.")
            break
        except ValueError as e:
            print(f"Invalid input. {e}. Please try again.")

    while True:
        cuisine_type = input("Choose your preferred cuisine type (e.g., Asian restaurant, Bakery/Pastries, etc.): ")
        if cuisine_type.strip():
            break
        else:
            print("Cuisine type cannot be empty. Please try again.")

    return budget, preferred_time, proximity_range, cuisine_type


# Recommend food stores based on user input with optimization
def recommend_stores(food_stores, stores_by_type, budget, time, proximity, cuisine):
    # Use pre-indexed stores by type for faster lookup
    recommendations = []
    cuisine = cuisine.lower()
    if cuisine in stores_by_type:
        # Filter by proximity and budget in the relevant cuisine category
        for store in stores_by_type[cuisine]:
            if store["proximity"] <= proximity and store["min_price"] <= budget <= store["max_price"]:
                recommendations.append(store)
    return recommendations

# Find available rider nearest to the location
def find_rider(riders, location):
    available_riders = [rider for rider in riders if rider["availability"]]

    # Create a heap based on proximity
    heap = []
    for rider in available_riders:
        proximity = rider["proximity"]
        heapq.heappush(heap, (proximity, rider))  # Push the (proximity, rider) tuple

    # Extract the closest rider if available
    return heapq.heappop(heap)[1] if heap else None


# Main program with retry logic
def main():
    food_stores, stores_by_type = load_food_stores()
    riders = generate_riders()

    while True:
        budget, time, proximity, cuisine = get_user_input()
        recommended_stores = recommend_stores(food_stores, stores_by_type, budget, time, proximity, cuisine)

        if recommended_stores:
            print("\nHere are your recommended food stores:")
            for i, store in enumerate(recommended_stores):
                print(
                    f"{i + 1}. {store['name']} - {store['type']} - {store['rating'] if store['rating'] else 'No rating'} stars - {store['proximity']} km away")

            while True:
                try:
                    choice = int(input("\nChoose a food store (Enter the number): "))
                    if 1 <= choice <= len(recommended_stores):
                        break
                    else:
                        print(f"Invalid choice. Please select a number between 1 and {len(recommended_stores)}.")
                except ValueError:
                    print("Invalid input. Please enter a valid number.")

            chosen_store = recommended_stores[choice - 1]
            print(f"\nYou chose {chosen_store['name']}")
            print(f"Location: {chosen_store['location_url']}")
            print(f"Facebook Page: {chosen_store['fb_page'] if chosen_store['fb_page'] else 'N/A'}")
            print(f"Rating: {chosen_store['rating'] if chosen_store['rating'] else 'No rating'} stars")
            print(f"Proximity: {chosen_store['proximity']} km")
            print(f"Time Availability: {chosen_store['time_availability'] if chosen_store['time_availability'] else 'N/A'}")

            need_rider = input("\nDo you need a rider to go to the place? (yes/no): ")
            if need_rider.lower() == "yes":
                rider = find_rider(riders, (13.7859177, 121.0706258))
                if rider:
                    print(f"\nRider {rider['name']} will assist you! \nCurrent location: {rider['proximity']} km away.")
                    print(f"Rider's contact number: {rider['phone_number']}")
                    print("\nAll set! You're ready to Ride&Dine!")
                else:
                    print("\nNo riders are currently available.")
            else:
                print("\nAll set! You're ready to Ride&Dine!")

            break

        else:
            print("\nNo food stores match your preferences.")
            try_again = input("Do you want to try again? (yes/no): ").strip().lower()
            if try_again != "yes":
                print("Thank you for using Ride&Dine! Goodbye!")
                break


if __name__ == "__main__":
    main()