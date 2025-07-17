from flask import Flask, render_template

app = Flask(__name__)

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


if __name__ == '__main__':
    print("Starting Operations & Workflow Automation Demo on http://127.0.0.1:5000")
    app.run(debug=True)
