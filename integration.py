"""
Numerical Integration Module
Implements Trapezoidal Rule and Simpson's 1/3 Rule manually without external math libraries (no numpy, scipy, sympy).
Uses Python built-in arithmetic and standard math module for function evaluation.
"""

import math
import re
import io
import base64
import time

try:
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except Exception:
    HAS_MATPLOTLIB = False


def preprocess_expression(expr_str: str) -> str:
    """
    Clean and format expression string for standard Python math syntax.
    Supports raw mathematical strings (x^2 + 3*x) and LaTeX constructs (\\frac{1}{1+x^2}, \\sin(x), x^{2}).
    """
    if not expr_str or not expr_str.strip():
        raise ValueError("Function expression cannot be empty.")

    expr = expr_str.strip()

    # Pre-process LaTeX constructs if present
    if '\\' in expr or '{' in expr or '}' in expr:
        # Convert \frac{A}{B} or \dfrac{A}{B} repeatedly for nested fractions
        while re.search(r'\\d?frac\{([^{}]+)\}\{([^{}]+)\}', expr):
            expr = re.sub(r'\\d?frac\{([^{}]+)\}\{([^{}]+)\}', r'((\1)/(\2))', expr)

        # Convert \sqrt{A} -> sqrt(A)
        expr = re.sub(r'\\sqrt\{([^{}]+)\}', r'sqrt(\1)', expr)

        # Remove latex command backslashes for common functions
        expr = re.sub(r'\\(sin|cos|tan|asin|acos|atan|sinh|cosh|tanh|exp|ln|log|sqrt)', r'\1', expr)

        # LaTeX symbols
        expr = expr.replace(r'\cdot', '*').replace(r'\times', '*')
        expr = expr.replace(r'\pi', 'pi').replace(r'\e', 'e')

        # Convert remaining curly braces to parentheses
        expr = expr.replace('{', '(').replace('}', ')')

    expr = expr.lower()

    # Replace ^ with **
    expr = expr.replace('^', '**')

    # Convert ln to log
    expr = re.sub(r'\bln\b', 'log', expr)

    # Implicit multiplication: digit followed by variable x or function name or opening parenthesis
    # e.g., "3x" -> "3*x", "2sin" -> "2*sin", "4(x)" -> "4*(x)"
    expr = re.sub(r'(\d)\s*([x\(a-zA-Z])', r'\1*\2', expr)

    # Implicit multiplication: 'x' followed by digit or '(' or math function name (like sin, cos, exp)
    # e.g., "x(" -> "x*(", "x 2" -> "x*2"
    expr = re.sub(r'\b(x)\s*(\d|\()', r'\1*\2', expr)

    # Implicit multiplication: closing parenthesis followed by digit, x, or '('
    # e.g., "(x+1)(x-1)" -> "(x+1)*(x-1)", "(x+1)x" -> "(x+1)*x"
    expr = re.sub(r'(\))\s*([\dx\(a-zA-Z])', r'\1*\2', expr)

    # Fix any accidental double asterisks created by regex if any
    # Re-verify allowed characters/tokens for safety
    allowed_names = {
        'x', 'sin', 'cos', 'tan', 'asin', 'acos', 'atan',
        'sinh', 'cosh', 'tanh', 'exp', 'log', 'log10', 'sqrt',
        'abs', 'fabs', 'pi', 'e'
    }

    # Extract all identifiers to ensure no unsafe commands
    identifiers = re.findall(r'[a-zA-Z_][a-zA-Z0-9_]*', expr)
    for ident in identifiers:
        if ident not in allowed_names:
            raise ValueError(f"Unsupported variable or function: '{ident}'. Only 'x', math functions (sin, cos, tan, exp, log, sqrt, abs), and constants (pi, e) are supported.")

    return expr


def evaluate_function(expr_str: str, x_val: float) -> float:
    """
    Safely evaluate mathematical function f(x) at x = x_val using Python's math module.
    """
    clean_expr = preprocess_expression(expr_str)

    safe_dict = {
        'x': float(x_val),
        'sin': math.sin,
        'cos': math.cos,
        'tan': math.tan,
        'asin': math.asin,
        'acos': math.acos,
        'atan': math.atan,
        'sinh': math.sinh,
        'cosh': math.cosh,
        'tanh': math.tanh,
        'exp': math.exp,
        'log': math.log,
        'log10': math.log10,
        'sqrt': math.sqrt,
        'abs': abs,
        'fabs': math.fabs,
        'pi': math.pi,
        'e': math.e
    }

    try:
        result = eval(clean_expr, {"__builtins__": None}, safe_dict)
        if isinstance(result, complex):
            raise ValueError("Evaluation produced a complex number.")
        if math.isnan(result) or math.isinf(result):
            raise ValueError(f"Function evaluated to an undefined numerical value ({result}) at x = {x_val}.")
        return float(result)
    except ZeroDivisionError:
        raise ValueError(f"Division by zero occurred while evaluating f({x_val}).")
    except ValueError as ve:
        raise ValueError(f"Domain error at x = {x_val}: {ve}")
    except Exception as e:
        raise ValueError(f"Error evaluating f({x_val}): {e}")


def validate_input(expr_str: str, a: float, b: float, n: int, method_type: str = 'trapezoidal'):
    """
    Validate all numerical integration inputs.
    """
    if not isinstance(n, int) or n <= 0:
        raise ValueError("Number of intervals (n) must be a positive integer greater than 0.")

    if a == b:
        raise ValueError("Lower limit (a) and upper limit (b) cannot be equal.")

    if method_type == 'simpson' and n % 2 != 0:
        raise ValueError(f"For Simpson's 1/3 Rule, the number of intervals (n) must be an EVEN integer. Received n = {n}.")

    # Test function evaluation at endpoints and midpoint to catch syntax/domain errors early
    evaluate_function(expr_str, a)
    evaluate_function(expr_str, b)
    evaluate_function(expr_str, (a + b) / 2.0)


def generate_table(expr_str: str, a: float, b: float, n: int, method_type: str = 'trapezoidal'):
    """
    Generate step points x_i, values f(x_i), coefficients, and weighted products.
    """
    h = (b - a) / n
    table = []
    x_values = []
    y_values = []

    for i in range(n + 1):
        x_i = a + i * h
        # Prevent small floating point inaccuracies at last step
        if i == n:
            x_i = b

        y_i = evaluate_function(expr_str, x_i)
        x_values.append(x_i)
        y_values.append(y_i)

        if method_type == 'trapezoidal':
            coeff = 1 if (i == 0 or i == n) else 2
        else:  # simpson 1/3
            if i == 0 or i == n:
                coeff = 1
            elif i % 2 == 1:
                coeff = 4
            else:
                coeff = 2

        weighted_val = coeff * y_i
        table.append({
            'index': i,
            'x': x_i,
            'fx': y_i,
            'coefficient': coeff,
            'weighted': weighted_val
        })

    return h, x_values, y_values, table


def trapezoidal_rule(expr_str: str, a: float, b: float, n: int, theme: str = 'dark'):
    """
    Computes numerical integration using Trapezoidal Rule:
    I ≈ (h / 2) * [f(x_0) + 2 * sum(f(x_i)) + f(x_n)]
    """
    start_time = time.perf_counter()

    validate_input(expr_str, a, b, n, method_type='trapezoidal')
    h, x_values, y_values, table = generate_table(expr_str, a, b, n, method_type='trapezoidal')

    y_0 = y_values[0]
    y_n = y_values[-1]
    interior_sum = sum(y_values[1:-1])

    result = (h / 2.0) * (y_0 + 2.0 * interior_sum + y_n)

    execution_time_ms = (time.perf_counter() - start_time) * 1000.0

    steps = [
        f"Step Size h = (b - a) / n = ({b} - {a}) / {n} = {h:.6f}",
        f"Endpoints: f(x₀) = f({x_values[0]:.6f}) = {y_0:.6f}, f(xₙ) = f({x_values[-1]:.6f}) = {y_n:.6f}",
        f"Sum of interior values Σf(xᵢ) [i=1 to {n-1}] = {interior_sum:.6f}",
        f"Formula: I ≈ (h / 2) * [f(x₀) + 2 * Σf(xᵢ) + f(xₙ)]",
        f"Calculation: I ≈ ({h:.6f} / 2) * [{y_0:.6f} + 2 * ({interior_sum:.6f}) + {y_n:.6f}]",
        f"Final Numerical Result = {result:.8f}"
    ]

    formula_latex = r"I \approx \frac{h}{2} \left[ f(x_0) + 2 \sum_{i=1}^{n-1} f(x_i) + f(x_n) \right]"
    formula_html = 'I &approx; <span class="frac"><sup>h</sup>&frasl;<sub>2</sub></span> &times; [f(x<sub>0</sub>) + 2 &sum;<sub>i=1</sub><sup>n-1</sup> f(x<sub>i</sub>) + f(x<sub>n</sub>)]'

    plot_b64 = generate_plot(expr_str, a, b, n, method_type='trapezoidal', x_values=x_values, y_values=y_values, theme=theme)

    return {
        'method': 'Trapezoidal Rule',
        'function': expr_str,
        'a': a,
        'b': b,
        'n': n,
        'h': h,
        'result': result,
        'formatted_result': f"{result:.8f}",
        'table': table,
        'steps': steps,
        'formula_html': formula_html,
        'formula_latex': formula_latex,
        'execution_time_ms': round(execution_time_ms, 3),
        'plot_b64': plot_b64
    }


def simpson_one_third(expr_str: str, a: float, b: float, n: int, theme: str = 'dark'):
    """
    Computes numerical integration using Simpson's 1/3 Rule:
    I ≈ (h / 3) * [f(x_0) + 4 * sum(f(x_odd)) + 2 * sum(f(x_even)) + f(x_n)]
    """
    start_time = time.perf_counter()

    validate_input(expr_str, a, b, n, method_type='simpson')
    h, x_values, y_values, table = generate_table(expr_str, a, b, n, method_type='simpson')

    y_0 = y_values[0]
    y_n = y_values[-1]

    odd_indices_sum = sum(y_values[i] for i in range(1, n, 2))
    even_indices_sum = sum(y_values[i] for i in range(2, n, 2))

    result = (h / 3.0) * (y_0 + 4.0 * odd_indices_sum + 2.0 * even_indices_sum + y_n)

    execution_time_ms = (time.perf_counter() - start_time) * 1000.0

    steps = [
        f"Step Size h = (b - a) / n = ({b} - {a}) / {n} = {h:.6f}",
        f"Boundary Values: f(x₀) = {y_0:.6f}, f(xₙ) = {y_n:.6f}",
        f"Odd-index sum Σf(x_odd) = {odd_indices_sum:.6f}",
        f"Even-index sum Σf(x_even) = {even_indices_sum:.6f}",
        f"Formula: I ≈ (h / 3) * [f(x₀) + 4 * Σf(x_odd) + 2 * Σf(x_even) + f(xₙ)]",
        f"Calculation: I ≈ ({h:.6f} / 3) * [{y_0:.6f} + 4 * ({odd_indices_sum:.6f}) + 2 * ({even_indices_sum:.6f}) + {y_n:.6f}]",
        f"Final Numerical Result = {result:.8f}"
    ]

    formula_latex = r"I \approx \frac{h}{3} \left[ f(x_0) + 4 \sum_{\text{odd}} f(x_i) + 2 \sum_{\text{even}} f(x_i) + f(x_n) \right]"
    formula_html = 'I &approx; <span class="frac"><sup>h</sup>&frasl;<sub>3</sub></span> &times; [f(x<sub>0</sub>) + 4 &sum;<sub>odd</sub> f(x<sub>i</sub>) + 2 &sum;<sub>even</sub> f(x<sub>i</sub>) + f(x<sub>n</sub>)]'

    plot_b64 = generate_plot(expr_str, a, b, n, method_type='simpson', x_values=x_values, y_values=y_values, theme=theme)

    return {
        'method': "Simpson's 1/3 Rule",
        'function': expr_str,
        'a': a,
        'b': b,
        'n': n,
        'h': h,
        'result': result,
        'formatted_result': f"{result:.8f}",
        'odd_sum': odd_indices_sum,
        'even_sum': even_indices_sum,
        'table': table,
        'steps': steps,
        'formula_html': formula_html,
        'formula_latex': formula_latex,
        'execution_time_ms': round(execution_time_ms, 3),
        'plot_b64': plot_b64
    }


def generate_plot(expr_str: str, a: float, b: float, n: int, method_type: str, x_values: list, y_values: list, theme: str = 'dark'):
    """
    Generates a high-quality SVG vector plot in pure Python (no external plotting libraries required).
    Returns base64 encoded SVG data URI string. Supports dark and light themes.
    """
    try:
        width = 800
        height = 420
        margin_left = 60
        margin_right = 40
        margin_top = 50
        margin_bottom = 50

        plot_w = width - margin_left - margin_right
        plot_h = height - margin_top - margin_bottom

        # Colors based on theme
        is_light = (theme == 'light')
        bg_color = "#ffffff" if is_light else "#121212"
        grid_color = "#e5e5e5" if is_light else "#262626"
        text_color = "#111111" if is_light else "#ffffff"
        text_sub_color = "#666666" if is_light else "#a3a3a3"
        axis_color = "#a1a1aa" if is_light else "#525252"
        poly_fill = "rgba(0, 0, 0, 0.08)" if is_light else "rgba(255, 255, 255, 0.12)"
        poly_stroke = "#666666" if is_light else "#888888"
        line_stroke = "#0f0f0f" if is_light else "#ffffff"
        point_fill = "#000000" if is_light else "#ffffff"
        point_stroke = "#ffffff" if is_light else "#000000"

        # 1. Sample continuous curve
        num_samples = 200
        sample_x = []
        sample_y = []
        for k in range(num_samples):
            t = a + (b - a) * k / (num_samples - 1)
            try:
                val = evaluate_function(expr_str, t)
                sample_x.append(t)
                sample_y.append(val)
            except Exception:
                pass

        all_x = x_values + sample_x
        all_y = y_values + sample_y + [0.0]

        min_x, max_x = min(x_values), max(x_values)
        if min_x == max_x:
            max_x = min_x + 1.0

        min_y, max_y = min(all_y), max(all_y)
        y_range = max_y - min_y
        if y_range == 0:
            y_range = 1.0
        min_y -= 0.1 * y_range
        max_y += 0.1 * y_range

        def map_x(x):
            return margin_left + (x - min_x) / (max_x - min_x) * plot_w

        def map_y(y):
            return margin_top + (max_y - y) / (max_y - min_y) * plot_h

        y_zero_px = map_y(0.0)
        y_zero_px = max(margin_top, min(height - margin_bottom, y_zero_px))

        svg_parts = []
        svg_parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%" style="background-color: {bg_color}; font-family: system-ui, sans-serif;">')

        # Background card
        svg_parts.append(f'<rect width="{width}" height="{height}" fill="{bg_color}" rx="12"/>')

        # Grid lines & Axis labels
        for i in range(5):
            gx = margin_left + i * (plot_w / 4)
            val_x = min_x + i * (max_x - min_x) / 4
            svg_parts.append(f'<line x1="{gx}" y1="{margin_top}" x2="{gx}" y2="{height - margin_bottom}" stroke="{grid_color}" stroke-width="1" stroke-dasharray="3 3"/>')
            svg_parts.append(f'<text x="{gx}" y="{height - margin_bottom + 20}" fill="{text_sub_color}" font-size="11" text-anchor="middle">{val_x:.2f}</text>')

        for j in range(5):
            gy = margin_top + j * (plot_h / 4)
            val_y = max_y - j * (max_y - min_y) / 4
            svg_parts.append(f'<line x1="{margin_left}" y1="{gy}" x2="{width - margin_right}" y2="{gy}" stroke="{grid_color}" stroke-width="1" stroke-dasharray="3 3"/>')
            svg_parts.append(f'<text x="{margin_left - 10}" y="{gy + 4}" fill="{text_sub_color}" font-size="11" text-anchor="end">{val_y:.2f}</text>')

        # Main Axis Lines
        svg_parts.append(f'<line x1="{margin_left}" y1="{y_zero_px}" x2="{width - margin_right}" y2="{y_zero_px}" stroke="{axis_color}" stroke-width="1.5"/>')
        svg_parts.append(f'<line x1="{margin_left}" y1="{margin_top}" x2="{margin_left}" y2="{height - margin_bottom}" stroke="{axis_color}" stroke-width="1.5"/>')

        # Integration Shapes (Trapezoids / Simpson)
        if method_type == 'trapezoidal':
            for i in range(n):
                x1_px, y1_px = map_x(x_values[i]), map_y(y_values[i])
                x2_px, y2_px = map_x(x_values[i+1]), map_y(y_values[i+1])
                poly_pts = f"{x1_px},{y_zero_px} {x1_px},{y1_px} {x2_px},{y2_px} {x2_px},{y_zero_px}"
                svg_parts.append(f'<polygon points="{poly_pts}" fill="{poly_fill}" stroke="{poly_stroke}" stroke-width="1" stroke-dasharray="2 2"/>')
                svg_parts.append(f'<line x1="{x1_px}" y1="{y1_px}" x2="{x2_px}" y2="{y2_px}" stroke="{line_stroke}" stroke-width="1.5" stroke-dasharray="4 2"/>')
        else:  # simpson
            for i in range(0, n, 2):
                x0, x1, x2 = x_values[i], x_values[i+1], x_values[i+2]
                y0, y1, y2 = y_values[i], y_values[i+1], y_values[i+2]
                path_pts = []
                p_steps = 20
                for k in range(p_steps + 1):
                    px = x0 + (x2 - x0) * k / p_steps
                    L0 = ((px - x1) * (px - x2)) / ((x0 - x1) * (x0 - x2))
                    L1 = ((px - x0) * (px - x2)) / ((x1 - x0) * (x1 - x2))
                    L2 = ((px - x0) * (px - x1)) / ((x2 - x0) * (x2 - x1))
                    py = y0 * L0 + y1 * L1 + y2 * L2
                    path_pts.append((map_x(px), map_y(py)))

                poly_pts = [f"{map_x(x0)},{y_zero_px}"] + [f"{px},{py}" for px, py in path_pts] + [f"{map_x(x2)},{y_zero_px}"]
                poly_str = " ".join(poly_pts)
                svg_parts.append(f'<polygon points="{poly_str}" fill="{poly_fill}" stroke="{poly_stroke}" stroke-width="1"/>')

        # Continuous function curve
        if len(sample_x) > 1:
            curve_pts = [f"{map_x(sx):.1f},{map_y(sy):.1f}" for sx, sy in zip(sample_x, sample_y)]
            curve_str = "M " + " L ".join(curve_pts)
            svg_parts.append(f'<path d="{curve_str}" fill="none" stroke="{line_stroke}" stroke-width="2.5"/>')

        # Sample Points
        for xi, yi in zip(x_values, y_values):
            px, py = map_x(xi), map_y(yi)
            svg_parts.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="4" fill="{point_fill}" stroke="{point_stroke}" stroke-width="1.5"/>')

        # Title and Labels
        method_label = "Trapezoidal Rule" if method_type == 'trapezoidal' else "Simpson's 1/3 Rule"
        svg_parts.append(f'<text x="{margin_left}" y="30" fill="{text_color}" font-size="14" font-weight="bold">{method_label} Integration (n = {n})</text>')
        svg_parts.append(f'<text x="{width - margin_right}" y="30" fill="{text_sub_color}" font-size="12" text-anchor="end">f(x) = {expr_str}</text>')

        svg_parts.append('</svg>')

        svg_content = "".join(svg_parts)
        b64_svg = base64.b64encode(svg_content.encode('utf-8')).decode('utf-8')
        return f"data:image/svg+xml;base64,{b64_svg}"
    except Exception as e:
        print("SVG Generation Error:", e)
        return None
