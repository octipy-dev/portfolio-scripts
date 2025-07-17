import requests
import polars as pl
import numpy as np
import matplotlib
matplotlib.use("TkAgg")  # Or "Qt5Agg" if you have PyQt installed
import matplotlib.pyplot as plt
import random
from io import BytesIO
from PIL import Image

# ------------------------------------------------------------------------------------
# 1) Nominatim Search: Get multiple addresses in Crystal Lake, Illinois
# ------------------------------------------------------------------------------------
def get_crystal_lake_addresses(limit=15):
    """
    Query Nominatim for addresses within or near Crystal Lake, IL.
    The 'limit' parameter controls how many results we want back.
    """
    base_url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": "Crystal Lake, IL, USA",  # Force the search to be in Crystal Lake, IL
        "format": "json",
        "addressdetails": 1,
        "limit": limit
    }
    headers = {"User-Agent": "DemoApp/1.0 (example@example.com)"}

    response = requests.get(base_url, params=params, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print("Error from Nominatim:", response.text)
        return []

# ------------------------------------------------------------------------------------
# 2) Retrieve a static map image from Wikimedia (Optional)
# ------------------------------------------------------------------------------------
def get_wikimedia_static_map(lat, lon, zoom=14, width=600, height=400):
    """
    Get a static map image from Wikimedia Maps. Not satellite imagery, just standard map.
    """
    url = f"https://maps.wikimedia.org/img/osm-intl,{zoom},{lat},{lon},{width}x{height}.png"
    response = requests.get(url)
    if response.status_code == 200:
        return Image.open(BytesIO(response.content))
    else:
        print("Error fetching map from Wikimedia:", response.text)
        return None

# ------------------------------------------------------------------------------------
# 3) Placeholder for pulling building permit data from public records
# ------------------------------------------------------------------------------------
def get_permit_data(address):
    """
    DEMO-ONLY:
    Randomly generate 'permit' data for illustration.
    In reality, you'd connect to a local government portal or database.
    """
    # For demonstration, randomly decide if there's a recent permit
    has_permit = random.choice([True, False])
    if has_permit:
        permit_type = random.choice(["Roof Replacement", "Basement Remodel", "Siding Repair", "Deck Addition"])
        permit_date = f"202{random.randint(0, 3)}-0{random.randint(1, 9)}-1{random.randint(1, 9)}"
        return f"{permit_type} (Issued on {permit_date})"
    else:
        return "No recent permits found"

# ------------------------------------------------------------------------------------
# 4) Exponential Decay to simulate condition of various house elements
# ------------------------------------------------------------------------------------
def decay_function(initial_value, decay_rate, time):
    return initial_value * np.exp(-decay_rate * time)

# ------------------------------------------------------------------------------------
# MAIN
# ------------------------------------------------------------------------------------
if __name__ == "__main__":
    # 4.1) Pull addresses from Nominatim specifically for Crystal Lake, IL
    addresses_data = get_crystal_lake_addresses(limit=15)
    if not addresses_data:
        print("No addresses found in Crystal Lake, IL.")
        exit()

    # Ask the user for a snippet of the address they want
    desired_address_str = input(
        "Enter part of the address to filter for (e.g. 'Crystal Lake, McHenry County, Illinois, 60014, United States'): "
    )

    # Filter the list of addresses to those containing the user-provided string
    filtered_data = [addr for addr in addresses_data if desired_address_str in addr["display_name"]]

    if not filtered_data:
        print(f"No addresses containing '{desired_address_str}' were found.")
        exit()

    # Overwrite addresses_data with only the filtered results
    addresses_data = filtered_data

    # 4.2) Create rows for each address, with condition data for Siding, Doors, Trim, Interior
    rows = []
    repair_threshold = 50.0

    for entry in addresses_data:
        lat = float(entry["lat"])
        lon = float(entry["lon"])
        display_name = entry["display_name"]

        # We'll do 4 sub-rows for Siding, Doors, Trim, Interior
        for element in ["Siding", "Doors", "Trim", "Interior Remodel"]:
            age = random.randint(1, 30)       # 1 to 30 years
            decay_rate = random.uniform(0.01, 0.06)
            initial_condition = 100
            current_condition = decay_function(initial_condition, decay_rate, age)
            needs_repair = current_condition < repair_threshold

            permit_info = get_permit_data(display_name)

            rows.append({
                "address": display_name,
                "lat": lat,
                "lon": lon,
                "element": element,
                "age": age,
                "decay_rate": decay_rate,
                "current_condition": current_condition,
                "needs_repair": needs_repair,
                "permit_info": permit_info
            })

    # Create a Polars DataFrame
    df = pl.DataFrame(rows)

    # Print out the data for debugging
    print("Sample House-Element Data for Crystal Lake, IL:")
    print(df)

    # 4.4) Group by address and plot a bar chart for each
    grouped = df.group_by("address").agg([
        pl.col("lat").first().alias("lat"),
        pl.col("lon").first().alias("lon"),
        pl.col("element"),
        pl.col("current_condition"),
        pl.col("needs_repair"),
        pl.col("permit_info")
    ])

    # Convert to pandas for simpler iteration
    grouped_pandas = grouped.to_pandas()

    # Plot each address in filtered_data
    for idx, row in grouped_pandas.iterrows():
        address = row["address"]
        lat_val = row["lat"]
        lon_val = row["lon"]

        elements = row["element"]
        conditions = row["current_condition"]
        repairs = row["needs_repair"]
        permits = row["permit_info"]

        # Create a bar chart
        fig, ax = plt.subplots(figsize=(8, 5))
        x_positions = np.arange(len(elements))
        bar_colors = ["red" if r else "green" for r in repairs]

        ax.bar(x_positions, conditions, color=bar_colors)
        ax.axhline(y=repair_threshold, color='blue', linestyle='--', label='Repair Threshold')

        ax.set_xticks(x_positions)
        ax.set_xticklabels(elements, rotation=45)
        ax.set_ylim(0, 110)
        ax.set_ylabel("Current Condition")
        ax.set_title(f"Condition of House Elements\n{address}")
        ax.legend()

        plt.tight_layout()
        plt.show()

        # Print permit info in console
        print(f"\nAddress: {address}")
        for e, p in zip(elements, permits):
            print(f" - {e} Permits: {p}")

        # Optional: show a static map for each address
        map_image = get_wikimedia_static_map(lat_val, lon_val, zoom=14, width=600, height=400)
        if map_image:
            plt.figure(figsize=(6, 6))
            plt.imshow(map_image)
            plt.title(f"Map of {address}")
            plt.axis('off')
            plt.show()



