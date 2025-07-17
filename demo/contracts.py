from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def contract_builder():
    contract_details = None
    if request.method == 'POST':
        party_a = request.form.get('party_a', '')
        party_b = request.form.get('party_b', '')
        contract_terms = request.form.get('contract_terms', '')
        contract_date = request.form.get('contract_date', '')
        # For demonstration, simply create a dictionary of the submitted details.
        contract_details = {
            'party_a': party_a,
            'party_b': party_b,
            'contract_terms': contract_terms,
            'contract_date': contract_date
        }
        # In a real application, you might generate a PDF or perform further processing.
    return render_template('contract.html', contract_details=contract_details)

if __name__ == '__main__':
    app.run(debug=True)
