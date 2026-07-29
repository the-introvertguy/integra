"""
Flask Application for Numerical Integration Calculator
Provides web routes and API endpoints for Trapezoidal and Simpson's 1/3 Rules.
"""

from flask import Flask, render_template, request, jsonify
import sys
import os

from integration import trapezoidal_rule, simpson_one_third, evaluate_function

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})


@app.route('/api/calculate', methods=['POST'])
def calculate():
    try:
        data = request.get_json(force=True)
        if not data:
            return jsonify({'success': False, 'error': 'No input data provided.'}), 400

        method = data.get('method', 'trapezoidal')
        theme = data.get('theme', 'dark')
        f_str = data.get('function', '').strip()
        a_raw = data.get('a')
        b_raw = data.get('b')
        n_raw = data.get('n')

        # Validate presence of fields
        if not f_str:
            return jsonify({'success': False, 'error': 'Please enter a valid mathematical function f(x).'}), 400

        if a_raw is None or str(a_raw).strip() == '':
            return jsonify({'success': False, 'error': 'Lower limit (a) is required.'}), 400

        if b_raw is None or str(b_raw).strip() == '':
            return jsonify({'success': False, 'error': 'Upper limit (b) is required.'}), 400

        if n_raw is None or str(n_raw).strip() == '':
            return jsonify({'success': False, 'error': 'Number of intervals (n) is required.'}), 400

        # Parse numeric types
        try:
            a = float(a_raw)
        except ValueError:
            return jsonify({'success': False, 'error': f"Invalid lower limit value '{a_raw}'. Must be a number."}), 400

        try:
            b = float(b_raw)
        except ValueError:
            return jsonify({'success': False, 'error': f"Invalid upper limit value '{b_raw}'. Must be a number."}), 400

        try:
            n = int(n_raw)
        except ValueError:
            return jsonify({'success': False, 'error': f"Invalid number of intervals '{n_raw}'. Must be an integer."}), 400

        if n <= 0:
            return jsonify({'success': False, 'error': 'Number of intervals (n) must be greater than 0.'}), 400

        if method == 'simpson':
            if n % 2 != 0:
                return jsonify({
                    'success': False,
                    'error': f"Validation Error: Simpson's 1/3 Rule requires an EVEN number of intervals. You entered n = {n}. Please enter an even number like 2, 4, 6, 8, or 10."
                }), 400
            result = simpson_one_third(f_str, a, b, n, theme=theme)
        else:
            result = trapezoidal_rule(f_str, a, b, n, theme=theme)

        return jsonify({'success': True, 'data': result})

    except ValueError as ve:
        return jsonify({'success': False, 'error': str(ve)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': f"An error occurred during calculation: {str(e)}"}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    print(f"Starting Numerical Integration Flask app on http://0.0.0.0:{port}")
    app.run(host='0.0.0.0', port=port, debug=True)
