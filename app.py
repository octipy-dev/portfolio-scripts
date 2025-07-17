import os
import re
import io
import random
import openai
import matplotlib
matplotlib.use('Agg')  # For non-interactive environments
import matplotlib.pyplot as plt
from flask import Flask, render_template, request, jsonify, send_file, url_for
from geopy.geocoders import Nominatim
from estimating import app as estimating_app

# Set OpenAI API key (ensure you have a valid key in your environment)
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

# --------------------------
# 1) HOME ROUTE
# --------------------------
@app.route('/')
def home():
    """Landing Page"""
    return render_template('home.html')

# --------------------------
# 2) ESTIMATING & QUOTING
# --------------------------
@app.route('/estimating', methods=['GET', 'POST'])
def estimating():
    estimate = {}
    if request.method == 'POST':
        # -- Gather standard fields --
        job_description = request.form.get('job_description', '')
        job_id = request.form.get('job_id', '')
        client_name = request.form.get('client_name', '')
        client_email = request.form.get('client_email', '')
        client_phone = request.form.get('client_phone', '')
        client_address = request.form.get('client_address', '')

        employment_type = request.form.get('employment_type', '1099')
        foreman_selected = (request.form.get('foreman') == 'yes')
        foreman_rate_type = request.form.get('foreman_rate_type', 'hourly')

        # -- Parse Foreman fields --
        try:
            foreman_rate = float(request.form.get('foreman_rate', '0'))
        except ValueError:
            foreman_rate = 0.0
        try:
            foreman_hours = float(request.form.get('foreman_hours', '0'))
        except ValueError:
            foreman_hours = 0.0

        # -- Crew members --
        try:
            crew_count = int(request.form.get('crew_count', '1'))
        except ValueError:
            crew_count = 1

        # For each crew member, parse rate/hours from the dynamic fields (crew_rate_1, crew_hours_1, etc.)
        crew_details = []
        for i in range(1, crew_count + 1):
            rate_key = f'crew_rate_{i}'
            hours_key = f'crew_hours_{i}'
            try:
                rate = float(request.form.get(rate_key, '0'))
            except ValueError:
                rate = 0.0
            try:
                hours = float(request.form.get(hours_key, '0'))
            except ValueError:
                hours = 0.0
            crew_details.append((rate, hours))

        # -- Materials & Overhead & Extras --
        try:
            materials_cost = float(request.form.get('materials_cost', '0'))
        except ValueError:
            materials_cost = 0.0
        try:
            overhead_percent = float(request.form.get('overhead_percent', '0'))
        except ValueError:
            overhead_percent = 0.0
        try:
            extra_cost = float(request.form.get('extra_cost', '0'))
        except ValueError:
            extra_cost = 0.0
        try:
            profit_goal_percent = float(request.form.get('profit_goal_percent', '0'))
        except ValueError:
            profit_goal_percent = 0.0

        # -- Compute labor --
        foreman_cost = 0.0
        if foreman_selected:
            if foreman_rate_type == 'hourly':
                foreman_cost = foreman_rate * foreman_hours
            else:
                # Flat rate
                foreman_cost = foreman_rate

        total_crew_labor = sum(rate * hours for (rate, hours) in crew_details)
        total_labor_cost = foreman_cost + total_crew_labor

        # Factor in W2 payroll tax if selected (7.65%)
        if employment_type == 'w2':
            total_labor_cost *= 1.0765

        # -- Compute overhead & profit --
        overhead_cost = (overhead_percent / 100.0) * (materials_cost + total_labor_cost)
        base_cost = materials_cost + total_labor_cost + overhead_cost + extra_cost
        profit_amount = (profit_goal_percent / 100.0) * base_cost
        total_cost = base_cost + profit_amount

        # -- Build final estimate dict --
        estimate = {
            "job_description": job_description,
            "job_id": job_id,
            "client_name": client_name,
            "client_email": client_email,
            "client_phone": client_phone,
            "client_address": client_address,
            "employment_type": employment_type,
            "foreman_selected": foreman_selected,
            "foreman_rate_type": foreman_rate_type,
            "foreman_rate": foreman_rate,
            "foreman_hours": foreman_hours,
            "crew_count": crew_count,
            "crew_details": crew_details,
            "materials_cost": materials_cost,
            "overhead_percent": overhead_percent,
            "extra_cost": extra_cost,
            "profit_goal_percent": profit_goal_percent,
            "overhead_cost": overhead_cost,
            "profit_amount": profit_amount,
            "total_labor_cost": total_labor_cost,
            "total_cost": total_cost
        }

    return render_template('estimating.html', estimate=estimate)


# --------------------------
# 3) OPERATIONS & WORKFLOW
# --------------------------
@app.route('/operations')
def operations():
    """Operations & Workflow"""
    jobs_schedule = {
        "2025-03-20": ["Job A - Exterior Painting", "Job B - Interior Painting"],
        "2025-03-21": ["Job C - Commercial Office Painting"]
    }
    crew_availability = {
        "Crew 1": True,
        "Crew 2": False,
        "Crew 3": True
    }
    gps_data = {
        "Crew 1": (40.7128, -74.0060),
        "Crew 3": (40.7138, -74.0050)
    }
    return render_template('operations.html',
                           jobs_schedule=jobs_schedule,
                           crew_availability=crew_availability,
                           gps_data=gps_data)

# --------------------------
# 4) CRM & LEAD MANAGEMENT
# --------------------------
@app.route('/crm')
def crm():
    """CRM & Lead Management"""
    dummy_leads = [
        {"name": "John Doe", "email": "john@example.com", "status": "New"},
        {"name": "Jane Smith", "email": "jane@example.com", "status": "Contacted"},
        {"name": "Alice Johnson", "email": "alice@example.com", "status": "Qualified"}
    ]
    return render_template('crm.html', leads=dummy_leads)

# --------------------------
# 5) DATA ANALYSIS & BUSINESS INTELLIGENCE
# --------------------------
@app.route('/data-analysis')
def data_analysis():
    """Data Analysis & Business Intelligence"""
    jobs = ['Job A', 'Job B', 'Job C', 'Job D']
    profit_margins = [0.20, 0.35, 0.15, 0.50]
    avg_margin = sum(profit_margins) / len(profit_margins)
    return render_template('data_analysis.html',
                           jobs=jobs,
                           profit_margins=profit_margins,
                           avg_margin=avg_margin)

@app.route('/analysis_chart.png')
def analysis_chart():
    """Dynamically generate a chart for data analysis"""
    jobs = ['Job A', 'Job B', 'Job C', 'Job D']
    profit_margins = [0.20, 0.35, 0.15, 0.50]
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(jobs, profit_margins, color='skyblue')
    ax.set_title("Profit Margins per Job")
    ax.set_xlabel("Jobs")
    ax.set_ylabel("Profit Margin")
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close(fig)
    return send_file(buf, mimetype='image/png')

# --------------------------
# 6) INVENTORY & SUPPLY CHAIN MANAGEMENT
# --------------------------
@app.route('/inventory')
def inventory():
    """Inventory & Supply Chain Management"""
    inventory_data = {
        "Paint (gal)": 100,
        "Brushes": 50,
        "Rollers": 40
    }
    thresholds = {
        "Paint (gal)": 80,
        "Brushes": 30,
        "Rollers": 25
    }
    reorder_list = [item for item, qty in inventory_data.items() if qty < thresholds[item]]
    return render_template('inventory.html',
                           inventory=inventory_data,
                           thresholds=thresholds,
                           reorder_list=reorder_list)

# --------------------------
# 7) AI CHATBOT DEMO
# --------------------------
conversation_history = [
    {
        "role": "system",
        "content": (
            "You are a helpful painting consultant. "
            "You can output text lists like '1)' or '-' if you want. "
            "This code will convert them to HTML bullet lists automatically."
        )
    }
]

def parse_bullets_to_html(text):
    """
    Converts lines starting with a bullet or number into HTML bullet list items.
    """
    lines = text.split('\n')
    in_list = False
    html_chunks = []
    bullet_pattern = re.compile(r'^(?:\d+\)|[-\*\u2022])\s+')

    for line in lines:
        stripped = line.strip()
        if bullet_pattern.match(stripped):
            if not in_list:
                html_chunks.append('<ul>')
                in_list = True
            item = bullet_pattern.sub('', stripped)
            html_chunks.append(f'<li>{item}</li>')
        else:
            if in_list:
                html_chunks.append('</ul>')
                in_list = False
            if stripped:
                html_chunks.append(f'{stripped}<br>')
            else:
                html_chunks.append('<br>')
    if in_list:
        html_chunks.append('</ul>')
    return ''.join(html_chunks)

# GET route for Chatbot UI
@app.route('/chatbot')
def chatbot_ui():
    return render_template('chatbot.html')

# POST route for Chatbot responses
@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '')
    conversation_history.append({"role": "user", "content": user_message})
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=conversation_history,
        temperature=0.7
    )
    assistant_text = response['choices'][0]['message']['content']
    assistant_html = parse_bullets_to_html(assistant_text)
    conversation_history.append({"role": "assistant", "content": assistant_text})
    return jsonify({"assistant": assistant_html})

# --------------------------
# 8) CONTRACT BUILDER
# --------------------------
@app.route('/contract-builder')
def contract_builder():
    """Contract Builder"""
    return render_template('contract.html')

# --------------------------
# 9) ADDRESS GEOCODER & CONDITION CHART
# --------------------------
# Set up Nominatim for geocoding
geolocator = Nominatim(user_agent="address_app_demo")
latest_scraped_data = {}

def scrape_public_records(address):
    """
    Placeholder for data fetching.
    Returns dummy condition ratings for various categories on a 1–10 scale.
    """
    return {
        "Siding": random.randint(1, 10),
        "Trim": random.randint(1, 10),
        "Doors": random.randint(1, 10),
        "Decks": random.randint(1, 10),
        "Interior Permits": random.randint(1, 10)
    }

@app.route('/address-geocoder', methods=['GET', 'POST'])
def address_geocoder():
    result = None
    error = None
    if request.method == 'POST':
        address = request.form.get('address', '')
        if address:
            try:
                # Geocode the address (or zipcode) using Nominatim
                location = geolocator.geocode(address)
                if location:
                    result = {
                        'address': location.address,
                        'latitude': location.latitude,
                        'longitude': location.longitude
                    }
                    global latest_scraped_data
                    latest_scraped_data = scrape_public_records(address)
                else:
                    error = "Address not found. Please enter a valid U.S. address or zipcode."
            except Exception as e:
                error = f"An error occurred: {e}"
    return render_template('address.html', result=result, error=error)

@app.route('/condition_chart.png')
def condition_chart():
    """
    Generates a bar chart of the latest condition data.
    Draws a horizontal dotted line at value 5 (50% threshold on a 1–10 scale).
    """
    if not latest_scraped_data:
        fig, ax = plt.subplots(figsize=(1, 1))
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        return send_file(buf, mimetype='image/png')
    categories = list(latest_scraped_data.keys())
    values = list(latest_scraped_data.values())
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(categories, values, color='skyblue')
    ax.set_ylim([0, 10])
    ax.set_ylabel("Condition Rating")
    ax.set_title("Condition Threshold by Category")
    ax.axhline(y=5, color='gray', linestyle='--', label='50% Threshold')
    ax.legend()
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close(fig)
    return send_file(buf, mimetype='image/png')

# --------------------------
# RUN THE FLASK APP
# --------------------------
if __name__ == '__main__':
    print("Starting Flask Multi-Demo App on http://127.0.0.1:5000")
    app.run(debug=True)

