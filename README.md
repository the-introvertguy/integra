# Numerical Integration Calculator

A lightweight, modern web application for an academic **Numerical Methods** course implementing:
1. **Trapezoidal Rule**
2. **Simpson's 1/3 Rule**

Designed with a minimal **Black & White** aesthetic inspired by Apple and Notion, featuring pure Python mathematical algorithm implementations, step-by-step derivation tables, and function visualization graphs.

---

## 📌 Features

- **Pure Python Math Implementation**: Numerical integration algorithms implemented manually from scratch without `numpy`, `scipy`, `sympy`, or `mpmath`.
- **Safe Mathematical Expression Evaluator**: Evaluates user-entered functions safely using standard arithmetic and Python's built-in `math` functions (`sin`, `cos`, `tan`, `exp`, `log`, `sqrt`, `abs`, `pi`, `e`).
- **Trapezoidal Rule Calculator**:
  - Calculates step size $h = (b - a) / n$.
  - Generates discretised sample points $x_i$ and $f(x_i)$.
  - Constructs detailed calculation table with coefficients $c_i$ and weighted values $c_i f(x_i)$.
  - Output breakdown steps and final numerical result.
- **Simpson's 1/3 Rule Calculator**:
  - Validates that interval count $n$ is an **even integer**.
  - Calculates Odd-index sum ($\sum f(x_{odd})$) and Even-index sum ($\sum f(x_{even})$).
  - Shows formula derivation and final definite integral estimate.
- **Geometrical Integration Graphing**:
  - Backend-generated monochrome `matplotlib` visualization displaying the target function curve, grid points, and integration sub-intervals (trapezoid polygons & parabolic segments).
- **Asynchronous SPA Interface**:
  - Smooth tab switching between methods using vanilla JavaScript and `fetch()` API without page reloads.

---

## 📐 Mathematical Formulas

### 1. Trapezoidal Rule

$$I \approx \frac{h}{2} \left[ f(x_0) + 2 \sum_{i=1}^{n-1} f(x_i) + f(x_n) \right]$$

* **Step Size**: $h = \frac{b - a}{n}$
* **Weights**: Endpoints $x_0, x_n$ weighted by $1$; interior points $x_1, \dots, x_{n-1}$ weighted by $2$.

---

### 2. Simpson's 1/3 Rule

$$I \approx \frac{h}{3} \left[ f(x_0) + 4 \sum_{i \text{ odd}} f(x_i) + 2 \sum_{i \text{ even}} f(x_i) + f(x_n) \right]$$

* **Condition**: Number of sub-intervals $n$ **must be even**.
* **Step Size**: $h = \frac{b - a}{n}$
* **Weights**: Endpoints weighted by $1$, odd-index interior points weighted by $4$, even-index interior points weighted by $2$.

---

## 📁 Folder Structure

```text
numerical-integration-calculator/
├── app.py                  # Flask web server & API endpoint routes
├── integration.py          # Pure Python numerical algorithms & expression evaluator
├── templates/
│   └── index.html          # HTML5 layout with B&W Notion/Apple design
├── static/
│   ├── style.css           # B&W CSS styling system
│   └── script.js           # Vanilla JS controller for tabs & AJAX calculation
├── metadata.json           # Application metadata configuration
├── package.json            # Node/npm process config for Cloud Run deployment
└── README.md               # Project documentation
```

---

## 🚀 Installation & Running

### Prerequisites

- Python 3.10+
- Flask (`pip install flask`)
- Matplotlib (`pip install matplotlib`)

### Running Locally

1. Clone or download the repository.
2. Install dependencies:
   ```bash
   pip install flask matplotlib
   ```
3. Run the Flask development server:
   ```bash
   python app.py
   ```
4. Open your browser and navigate to `http://localhost:3000`.
