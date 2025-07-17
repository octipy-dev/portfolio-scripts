from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def crm():
    """
    Shows a list of leads, simulating a simple CRM system.
    In a real system, you'd have forms to update status,
    track interactions, etc.
    """
    leads = [
        {"name": "Alice", "email": "alice@example.com", "status": "new"},
        {"name": "Bob", "email": "bob@example.com", "status": "contacted"},
        {"name": "Charlie", "email": "charlie@example.com", "status": "converted"}
    ]
    return render_template('crm.html', leads=leads)

if __name__ == '__main__':
    print("Starting CRM & Lead Management Demo on http://127.0.0.1:5000")
    app.run(debug=True)

