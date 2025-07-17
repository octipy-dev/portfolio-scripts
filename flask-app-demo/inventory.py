from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def inventory_management():
    """
    Shows a list of inventory items, thresholds,
    and whether a reorder is needed.
    """
    # Dummy data
    inventory = {
        "Paint (gal)": 100,
        "Brushes": 50,
        "Rollers": 40
    }
    thresholds = {
        "Paint (gal)": 80,
        "Brushes": 30,
        "Rollers": 25
    }

    # Simulate checking reorder status
    reorder_list = []
    for item, qty in inventory.items():
        if qty < thresholds[item]:
            reorder_list.append(item)

    return render_template('inventory.html',
                           inventory=inventory,
                           thresholds=thresholds,
                           reorder_list=reorder_list)

if __name__ == '__main__':
    print("Starting Inventory & Supply Chain Management Demo on http://127.0.0.1:5000")
    app.run(debug=True)
