from flask import Flask, render_template, send_file
import io
import matplotlib
matplotlib.use('Agg')  # Use a non-interactive backend
import matplotlib.pyplot as plt

app = Flask(__name__)

# Dummy data for demonstration
jobs = ['Job A', 'Job B', 'Job C', 'Job D']
profit_margins = [0.20, 0.35, 0.15, 0.50]

@app.route('/')
def data_analysis():
    # Calculate average profit margin for forecast (example)
    avg_margin = sum(profit_margins) / len(profit_margins)
    return render_template('data_analysis.html', jobs=jobs, profit_margins=profit_margins, avg_margin=avg_margin)

@app.route('/analysis_chart.png')
def analysis_chart():
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

if __name__ == '__main__':
    print("Starting Data Analysis & Business Intelligence Demo on http://127.0.0.1:5000")
    app.run(debug=True)

