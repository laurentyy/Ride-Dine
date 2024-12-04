import flet as ft
from food_store import load_food_stores, recommend_stores
from rider import generate_riders
from utils import calculate_distance
import heapq

# Store selected food and rider info globally
selected_store = None
selected_rider = None

# Main page for user input
def main_page(page: ft.Page):
    # Load food stores and riders data
    food_stores, stores_by_type = load_food_stores()
    riders = generate_riders()

    # UI Elements for page 1
    budget_input = ft.TextField(label="Enter your budget (e.g., 200)", autofocus=True)
    time_input = ft.TextField(label="Preferred time to eat (HH:MM)", keyboard_type=ft.KeyboardType.NUMBER)
    proximity_input = ft.TextField(label="Proximity range in km", keyboard_type=ft.KeyboardType.NUMBER)

    cuisine_dropdown = ft.Dropdown(
        label="Cuisine type",
        options=[
            ft.dropdown.Option("Fastfood"),
            ft.dropdown.Option("Steak/Barbecue restaurant"),
            ft.dropdown.Option("Family Restaurant"),
            ft.dropdown.Option("Asian restaurant"),
            ft.dropdown.Option("Chicken restaurant"),
            ft.dropdown.Option("Bakery/Pastries"),
            ft.dropdown.Option("Hamburger restaurant"),
            ft.dropdown.Option("Seafood Restaurant"),
            ft.dropdown.Option("Pizza Restaurant"),
            ft.dropdown.Option("Korean Restaurant"),
        ],
        autofocus=True
    )

    error_message = ft.Column()  # Container for error messages
    output = ft.Column()

    def validate_inputs():
        # Validate budget, time, and proximity
        errors = []

        # Budget validation (must be a positive number)
        try:
            budget = float(budget_input.value)
            if budget <= 0:
                errors.append(("budget", "Budget must be a positive number"))
        except ValueError:
            errors.append(("budget", "Please enter a valid number"))

        # Time validation (should match HH:MM format)
        preferred_time = time_input.value
        if not preferred_time or len(preferred_time) != 5 or preferred_time[2] != ":" or not preferred_time[:2].isdigit() or not preferred_time[3:].isdigit():
            errors.append(("time", "Please enter a valid time in HH:MM format"))

        # Proximity validation (must be a positive number)
        try:
            proximity = float(proximity_input.value)
            if proximity <= 0:
                errors.append(("proximity", "Proximity must be a positive number"))
        except ValueError:
            errors.append(("proximity", "Please enter a valid number"))

        return errors

    def on_submit(e):
        # Clear previous error messages
        error_message.controls.clear()

        # Validate inputs
        errors = validate_inputs()

        # If there are errors, display them
        if errors:
            for field, msg in errors:
                error_message.controls.append(ft.Text(msg, color="red"))

            # Focus on the first invalid input field
            if errors[0][0] == "budget":
                budget_input.focus()  # Correct focus method
            elif errors[0][0] == "time":
                time_input.focus()  # Correct focus method
            elif errors[0][0] == "proximity":
                proximity_input.focus()  # Correct focus method

            page.update()
            return  # Don't proceed further if there are errors

        # Proceed with store recommendations if inputs are valid
        budget = float(budget_input.value)
        preferred_time = time_input.value
        proximity = float(proximity_input.value)
        cuisine = cuisine_dropdown.value.lower()

        recommendations = recommend_stores(food_stores, stores_by_type, budget, preferred_time, proximity, cuisine)

        if recommendations:
            output.controls.clear()
            output.controls.append(ft.Text("Recommended food stores list:"))
            for i, store in enumerate(recommendations):
                # Pass store data explicitly
                output.controls.append(
                    ft.ElevatedButton(f"{store['name']} - {store['type']} - {store['rating']} stars",
                                      on_click=lambda e, store=store: on_store_select(page, store))
                )
            page.update()
        else:
            output.controls.clear()
            output.controls.append(ft.Text("No food stores match your preferences."))
            page.update()

    submit_button = ft.ElevatedButton("Submit", on_click=on_submit)

    page.add(
        budget_input,
        time_input,
        proximity_input,
        cuisine_dropdown,
        submit_button,
        error_message,  # Add error messages container to the page
        output
    )


# Store selection handler for page 2
def on_store_select(page: ft.Page, store):
    global selected_store
    selected_store = store
    print(f"Store selected: {store['name']}")  # Debugging print

    # Switch to store details page
    store_details_page(page)


# Store details page
def store_details_page(page: ft.Page):
    global selected_store

    if selected_store is None:
        page.add(ft.Text("No store selected"))
        return

    # Show selected store details (added hyperlink for urls)
    store_details = ft.Column([
        ft.Text(f"You chose {selected_store['name']}!"),
        ft.Text(f"Google Map Link:{ "" if selected_store['location_url'] else 'N/A'}"),
        ft.TextButton(text=f"Google Map", url=selected_store['location_url'], on_click=lambda _: page.launch_url(selected_store['location_url'])),
        ft.Text(f"Facebook Page: { "" if selected_store['fb_page'] else 'N/A'}"),
        ft.TextButton(text=f"Facebook Page", url= selected_store['fb_page'],  on_click=lambda _: page.launch_url(selected_store['fb_page'])),
        ft.Text(f"Rating: {selected_store['rating'] if selected_store['rating'] else 'No rating'} stars"),
        ft.Text(f"Type: {selected_store['type']}"),
        ft.Text(f"Proximity: {selected_store['proximity']} km"),
        ft.Text(f"Time Availability: {selected_store['time_availability'] if selected_store['time_availability'] else 'N/A'}"),])

    need_rider_button_yes = ft.ElevatedButton("Yes, I need a rider", on_click=lambda e: on_need_rider(page))
    need_rider_button_no = ft.ElevatedButton("No, I don't need a rider", on_click=lambda e: on_no_rider(page))

    # Clear the current page content and add store details and rider button options
    page.controls.clear()
    page.add(store_details, need_rider_button_yes, need_rider_button_no)
    page.update()


# Handle when the user needs a rider
def on_need_rider(page: ft.Page):
    global selected_store, selected_rider
    riders = generate_riders()

    # Find the nearest available rider
    if selected_store is None:
        return

    # Find a rider if needed
    nearest_rider = find_nearest_rider(riders, selected_store)

    if nearest_rider:
        selected_rider = nearest_rider
        rider_details = ft.Column([
            ft.Text(
                f"Rider: {selected_rider['name']} will assist you! \nCurrent location: {selected_rider['proximity']} km away."),
            ft.Text(f"Phone: {selected_rider['phone_number']}"),
        ])
        page.add(rider_details)
    else:
        page.add(ft.Text("No riders available."))

    page.add(ft.Text("You're ready to Ride&Dine with your rider!"))
    page.update()


# Handle when the user does not need a rider
def on_no_rider(page: ft.Page):
    page.add(ft.Text("You're ready to Ride&Dine!"))
    page.update()

def find_nearest_rider(riders, store):
    available_riders = [rider for rider in riders if rider["availability"]]

    if not available_riders:
        return None

    # Create a heap (min-heap) based on proximity
    rider_heap = []
    for rider in available_riders:
        # Calculate the distance to the store
        distance = calculate_distance(rider["location"], (13.7859177, 121.0706258))

        # Push a tuple (distance, rider) onto the heap
        heapq.heappush(rider_heap, (distance, rider))

    # The nearest rider will be the one with the smallest distance
    nearest_rider = heapq.heappop(rider_heap)[1]  # Pop the rider with the smallest distance

    return nearest_rider

# Start Flet app
def main(page: ft.Page):
    # Initial page load
    main_page(page)

# Run the app
ft.app(target=main)