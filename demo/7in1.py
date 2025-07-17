#!/usr/bin/env python3
"""
painting_business_demo.py

Demo Suite for Commercial Painting Business Automation:
  1. Estimating & Quoting
  2. Operations & Workflow
  3. CRM & Lead Management
  4. Data Analysis & BI
  5. Customer Portal (Flask)
  6. AI Chatbot (Flask + OpenAI)
  7. Inventory & Supply Chain

This standalone script organizes each demo into a function,
includes a runtime prompt for OpenAI API key for the chatbot demo,
and provides a clean CLI menu.

Dependencies:
    - flask
    - matplotlib
    - openai

Install prerequisites:
    pip install flask matplotlib openai

Usage:
    python painting_business_demo.py

Select a demo by entering its number; demos 5 and 6 launch a Flask server
and block until terminated (Ctrl+C to stop).
"""
import os
import sys
import matplotlib.pyplot as plt
from flask import Flask, request, jsonify, render_template
import openai

# -----------------------------------------------------------------------------
# Prompt for OpenAI API Key
# -----------------------------------------------------------------------------
def prompt_openai_key():
    """
    Prompt user to enter their OpenAI API key for testing.
    """
    key = os.getenv('OPENAI_API_KEY')
    if not key:
        key = input('Enter your OpenAI API key (or leave blank to exit): ').strip()
    if not key:
        print('No API key provided; AI Chatbot demo will not function.')
    openai.api_key = key

# -----------------------------------------------------------------------------
# Stub QuickBooks Integration (Simulation Only)
# -----------------------------------------------------------------------------
class QuickBooksAPI:
    """Simulated QuickBooks API client with stub methods."""
    def send_estimate(self, estimate_data: dict) -> bool:
        print("[QuickBooks] Sending estimate:", estimate_data)
        return True

    def send_vendor_payment(self, payment_data: dict) -> bool:
        print("[QuickBooks] Sending vendor payment:", payment_data)
        return True

# -----------------------------------------------------------------------------
# 1. Estimating & Quoting Automation Demo
# -----------------------------------------------------------------------------
def demo_estimate_and_quote():
    """Generate and dispatch a job cost estimate."""
    print("\n--- Estimating & Quoting Automation ---")
    materials = 500.00
    labor = 800.00
    overhead = 200.00
    total = materials + labor + overhead
    estimate = {
        'job': 'Exterior House Painting',
        'materials': materials,
        'labor': labor,
        'overhead': overhead,
        'total': total
    }
    print("Estimate generated:", estimate)
    QuickBooksAPI().send_estimate(estimate)

# -----------------------------------------------------------------------------
# 2. Operations & Workflow Automation Demo
# -----------------------------------------------------------------------------
def demo_operations_workflow():
    """Simulate job scheduling, crew availability, and GPS tracking."""
    print("\n--- Operations & Workflow Automation ---")
    schedule = {
        '2025-03-20': ['Job A', 'Job B'],
        '2025-03-21': ['Job C']
    }
    crew_avail = {'Crew 1': True, 'Crew 2': False, 'Crew 3': True}
    gps = {'Crew 1': (40.7128, -74.0060), 'Crew 3': (40.7138, -74.0050)}
    print("Schedule:", schedule)
    print("Crew Availability:", crew_avail)
    print("GPS Data:", gps)

# -----------------------------------------------------------------------------
# 3. CRM & Lead Management Demo
# -----------------------------------------------------------------------------
def demo_crm_lead_management():
    """List leads and simulate an email campaign."""
    print("\n--- CRM & Lead Management ---")
    leads = [
        {'name': 'Alice', 'email': 'alice@example.com', 'status': 'new'},
        {'name': 'Bob',   'email': 'bob@example.com',   'status': 'contacted'},
        {'name': 'Cara',  'email': 'cara@example.com',  'status': 'converted'}
    ]
    for lead in leads:
        print(lead)
    print("Simulating email campaign to new leads...")

# -----------------------------------------------------------------------------
# 4. Data Analysis & Business Intelligence Demo
# -----------------------------------------------------------------------------
def demo_data_analysis():
    """Plot profit margins and forecast material usage."""
    print("\n--- Data Analysis & BI ---")
    jobs = ['Job A', 'Job B', 'Job C']
    margins = [0.20, 0.35, 0.15]
    print("Plotting profit margins...")
    plt.bar(jobs, margins)
    plt.title('Profit Margins')
    plt.xlabel('Job')
    plt.ylabel('Margin')
    plt.show()
    usage = [450, 500, 480]
    forecast = sum(usage)/len(usage)
    print(f"Forecasted material usage: {forecast:.1f} units")

# -----------------------------------------------------------------------------
# 5. Customer Portal Demo (Flask)
# -----------------------------------------------------------------------------
CUSTOMER_PORTAL = Flask(__name__)
@CUSTOMER_PORTAL.route('/')
def portal_index():
    return '<h1>Customer Portal</h1><p>Jobs:</p>'

def demo_customer_portal():
    """Launches a Flask app serving a simple customer portal."""
    print("\n--- Customer Portal (Flask) ---")
    print("Visit http://127.0.0.1:5000/")
    CUSTOMER_PORTAL.run(debug=False)

# -----------------------------------------------------------------------------
# 6. AI & Chatbot Demo (Flask + OpenAI)
# -----------------------------------------------------------------------------
CHATBOT_APP = Flask(__name__)
history = [ {'role':'system','content':'You are a painting consultant.'} ]

@CHATBOT_APP.route('/', methods=['GET'])
def chatbot_ui():
    return 'Chatbot UI Placeholder'

@CHATBOT_APP.route('/chat', methods=['POST'])
def chatbot_chat():
    user_msg = request.json.get('message','')
    history.append({'role':'user','content':user_msg})
    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo', messages=history)
    content = response.choices[0].message.content
    history.append({'role':'assistant','content':content})
    return jsonify({'response': content})

def demo_chatbot():
    """Launches a Flask app for AI chatbot demo."""
    print("\n--- AI Chatbot (Flask + OpenAI) ---")
    prompt_openai_key()
    if not openai.api_key:
        print('Skipping AI Chatbot demo due to missing API key.')
        return
    print("Visit http://127.0.0.1:5000/")
    CHATBOT_APP.run(debug=True)

# -----------------------------------------------------------------------------
# 7. Inventory & Supply Chain Management Demo
# -----------------------------------------------------------------------------
def demo_inventory_supply_chain():
    """Check inventory levels and simulate reordering."""
    print("\n--- Inventory & Supply Chain ---")
    inventory = {'Paint':100, 'Brushes':50, 'Rollers':40}
    thresholds = {'Paint':80, 'Brushes':30, 'Rollers':25}
    for item, qty in inventory.items():
        if qty < thresholds[item]:
            print(f"Reorder {item} (qty={qty})")
        else:
            print(f"{item} sufficient (qty={qty})")
    QuickBooksAPI().send_vendor_payment({'vendor':'Supply Co.','amount':200.0})

# -----------------------------------------------------------------------------
# Main Menu
# -----------------------------------------------------------------------------
def main():
    while True:
        print("\nSelect a demo (1-7) or 0 to exit:")
        print("  1. Estimating & Quoting")
        print("  2. Operations & Workflow")
        print("  3. CRM & Lead Management")
        print("  4. Data Analysis & BI")
        print("  5. Customer Portal (Flask)")
        print("  6. AI Chatbot (Flask + OpenAI)")
        print("  7. Inventory & Supply Chain")
        print("  0. Exit")
        choice = input('> ').strip()
        if choice == '0':
            print('Exiting.')
            break
        demos = {
            '1': demo_estimate_and_quote,
            '2': demo_operations_workflow,
            '3': demo_crm_lead_management,
            '4': demo_data_analysis,
            '5': demo_customer_portal,
            '6': demo_chatbot,
            '7': demo_inventory_supply_chain
        }
        action = demos.get(choice)
        if action:
            action()
        else:
            print('Invalid selection.')

if __name__ == '__main__':
    main()
