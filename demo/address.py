#!/usr/bin/env python3
"""
geocoder_app.py

Flask application that geocodes a user-provided address via Google Maps API
and displays a bar chart of simulated condition ratings.

Features:
  - UI prompt for Google API key via form.
  - Address lookup form and result display with latitude/longitude.
  - Dynamic PNG bar chart generated with matplotlib.
  - CLI flags for host, port, and debug mode.

Dependencies:
    flask
    googlemaps
    matplotlib

Install prerequisites:
    pip install flask googlemaps matplotlib

Template requirement:
    Create a Jinja2 template at `templates/address.html`:
      - A form POSTing to `/` with inputs named "address" and "google_api_key".
      - Display of `error` or `result` variables.
      - IMG tag pointing to `/condition_chart.png` and embed Maps JS using `{{ google_api_key }}`.

Usage:
    python geocoder_app.py --host 0.0.0.0 --port 5000 --debug
"""
import io
import random
import logging
import argparse

from flask import Flask, render_template, request, send_file
import googlemaps
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for charts
import matplotlib.pyplot as plt

# Configure logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
# Global storage for the latest simulated condition data\ nlatest_condition_data = {}

def fetch_condition_data(address: str) -> dict:
    """
    Simulate fetching public records; returns random ratings 1-10.
    """
    categories = ["Siding", "Trim", "Doors", "Decks", "Interior Permits"]
    return {cat: random.randint(1, 10) for cat in categories}

@app.route('/', methods=['GET', 'POST'])
def address_geocoder():
    """
    Handle address input form, perform geocoding using the user-provided API key,
    and trigger data simulation.
    """
    error = None
    result = None
    # Grab the API key from the form input, stays blank on GET
    google_api_key = request.form.get('google_api_key', '').strip()

    if request.method == 'POST':
        if not google_api_key:
            error = "Google API key is required."
        else:
            try:
                gmaps = googlemaps.Client(key=google_api_key)
            except Exception as e:
                logging.exception("Invalid Google API key")
                error = f"Invalid API key: {e}"
        if not error:
            address = request.form.get('address', '').strip()
            if not address:
                error = "Please enter a non-empty address."
            else:
                try:
                    geocode_result = gmaps.geocode(address)
                except Exception as e:
                    logging.exception("Error calling geocoding API")
                    error = f"Geocoding service error: {e}"
                else:
                    if not geocode_result:
                        error = "Address not found."
                    else:
                        loc = geocode_result[0]['geometry']['location']
                        formatted = geocode_result[0].get('formatted_address', address)
                        result = {
                            'address': formatted,
                            'latitude': loc['lat'],
                            'longitude': loc['lng']
                        }
                        global latest_condition_data
                        latest_condition_data = fetch_condition_data(address)

    return render_template(
        'address.html',
        # Pass back the key so the form input stays populated
        google_api_key=google_api_key,
        error=error,
        result=result
    )

@app.route('/condition_chart.png')
def condition_chart():
    """
    Generate a bar chart of the latest condition data as PNG.
    """
    fig, ax = plt.subplots(figsize=(6, 4))
    if latest_condition_data:
        cats = list(latest_condition_data.keys())
        vals = list(latest_condition_data.values())
        ax.bar(cats, vals)
        ax.set_ylim(0, 10)
        ax.set_ylabel('Condition Rating')
        ax.set_title('Condition Ratings by Category')
        ax.axhline(5, linestyle='--', label='Threshold')
        ax.legend()
    else:
        ax.text(0.5, 0.5, 'No data available', ha='center', va='center')
        ax.axis('off')
    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close(fig)
    return send_file(buf, mimetype='image/png')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Geocoder Flask App')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind')
    parser.add_argument('--port', type=int, default=5000, help='Port to listen on')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    args = parser.parse_args()
    app.run(host=args.host, port=args.port, debug=args.debug)
