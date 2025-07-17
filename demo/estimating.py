from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/estimating', methods=['GET', 'POST'])
def estimating():
    # Capture OpenAI API key to keep UI input populated
    openai_api_key = request.form.get('openai_api_key', '')

    estimate = {}
    if request.method == 'POST':
        # Gather standard fields
        job_description = request.form.get('job_description', '')
        job_id = request.form.get('job_id', '')
        client_name = request.form.get('client_name', '')
        client_email = request.form.get('client_email', '')
        client_phone = request.form.get('client_phone', '')
        client_address = request.form.get('client_address', '')

        employment_type = request.form.get('employment_type', '1099')
        foreman_selected = (request.form.get('foreman') == 'yes')
        foreman_rate_type = request.form.get('foreman_rate_type', 'hourly')

        # Foreman rates & hours
        try:
            foreman_rate = float(request.form.get('foreman_rate', '0'))
        except ValueError:
            foreman_rate = 0.0
        try:
            foreman_hours = float(request.form.get('foreman_hours', '0'))
        except ValueError:
            foreman_hours = 0.0

        # Crew details
        try:
            crew_count = int(request.form.get('crew_count', '1'))
        except ValueError:
            crew_count = 1
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

        # Costs
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

        # Compute labor
        foreman_cost = 0.0
        if foreman_selected:
            if foreman_rate_type == 'hourly':
                foreman_cost = foreman_rate * foreman_hours
            else:
                foreman_cost = foreman_rate
        total_crew_labor = sum(rate * hours for (rate, hours) in crew_details)
        total_labor_cost = foreman_cost + total_crew_labor

        # Apply W2 payroll tax if applicable
        if employment_type == 'w2':
            total_labor_cost *= 1.0765

        # Overhead & profit
        overhead_cost = (overhead_percent / 100.0) * (materials_cost + total_labor_cost)
        base_cost = materials_cost + total_labor_cost + overhead_cost + extra_cost
        profit_amount = (profit_goal_percent / 100.0) * base_cost
        total_cost = base_cost + profit_amount

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

    return render_template('estimating.html', estimate=estimate, openai_api_key=openai_api_key)


