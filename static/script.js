/**
 * Numerical Integration Calculator - Frontend Controller
 * Handles Tab Switching, Form Validation, Asynchronous Calculation API, Dark/Light Theme,
 * and Comprehensive LaTeX Math Rendering via KaTeX.
 */

document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const tabTrapezoidal = document.getElementById('tab-trapezoidal');
    const tabSimpson = document.getElementById('tab-simpson');
    const methodInput = document.getElementById('method-input');
    const methodTitle = document.getElementById('method-title');
    const methodDesc = document.getElementById('method-desc');
    const nValidationTag = document.getElementById('n-validation-tag');

    const form = document.getElementById('integration-form');
    const funcInput = document.getElementById('func-input');
    const aInput = document.getElementById('a-input');
    const bInput = document.getElementById('b-input');
    const nInput = document.getElementById('n-input');
    const calculateBtn = document.getElementById('calculate-btn');
    const btnText = calculateBtn.querySelector('.btn-text');
    const btnSpinner = calculateBtn.querySelector('.btn-spinner');

    const errorBanner = document.getElementById('error-banner');
    const errorMessage = document.getElementById('error-message');

    const resultsContainer = document.getElementById('results-container');
    const resMethodTag = document.getElementById('res-method-tag');
    const resExecTime = document.getElementById('res-exec-time');
    const resValue = document.getElementById('res-value');
    const resFunc = document.getElementById('res-func');
    const resInterval = document.getElementById('res-interval');
    const resStepSize = document.getElementById('res-step-size');
    const resIntervalsCnt = document.getElementById('res-intervals-cnt');

    const resFormulaBox = document.getElementById('res-formula-box');
    const resStepsList = document.getElementById('res-steps-list');

    const simpsonSumsCard = document.getElementById('simpson-sums-card');
    const resOddSum = document.getElementById('res-odd-sum');
    const resEvenSum = document.getElementById('res-even-sum');

    const resTableBody = document.getElementById('res-table-body');
    const resTableFoot = document.getElementById('res-table-foot');

    const graphCard = document.getElementById('graph-card');
    const resPlotImg = document.getElementById('res-plot-img');

    const presetBtns = document.querySelectorAll('.chip-btn');

    // Modal Elements & Handlers
    const infoToggleBtn = document.getElementById('info-toggle-btn');
    const aboutModal = document.getElementById('about-modal');
    const aboutModalClose = document.getElementById('about-modal-close');

    function openAboutModal() {
        if (aboutModal) {
            aboutModal.classList.remove('hidden');
            document.body.style.overflow = 'hidden';
        }
    }

    function closeAboutModal() {
        if (aboutModal) {
            aboutModal.classList.add('hidden');
            document.body.style.overflow = '';
        }
    }

    if (infoToggleBtn) {
        infoToggleBtn.addEventListener('click', openAboutModal);
    }

    if (aboutModalClose) {
        aboutModalClose.addEventListener('click', closeAboutModal);
    }

    if (aboutModal) {
        aboutModal.addEventListener('click', (e) => {
            if (e.target === aboutModal) {
                closeAboutModal();
            }
        });
    }

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && aboutModal && !aboutModal.classList.contains('hidden')) {
            closeAboutModal();
        }
    });

    // Theme Elements
    const themeToggleBtn = document.getElementById('theme-toggle-btn');
    const themeIconSun = document.getElementById('theme-icon-sun');
    const themeIconMoon = document.getElementById('theme-icon-moon');
    const themeToggleText = document.getElementById('theme-toggle-text');

    let currentTheme = localStorage.getItem('app-theme') || 'dark';

    /**
     * Applies theme ('dark' or 'light') across DOM and saves to localStorage.
     */
    function applyTheme(theme) {
        currentTheme = theme;
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('app-theme', theme);

        if (theme === 'light') {
            themeIconSun.classList.remove('hidden');
            themeIconMoon.classList.add('hidden');
            themeToggleText.textContent = 'Light';
        } else {
            themeIconSun.classList.add('hidden');
            themeIconMoon.classList.remove('hidden');
            themeToggleText.textContent = 'Dark';
        }
    }

    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', () => {
            const nextTheme = currentTheme === 'dark' ? 'light' : 'dark';
            applyTheme(nextTheme);

            // Re-render plot if results are currently visible
            if (!resultsContainer.classList.contains('hidden')) {
                form.dispatchEvent(new Event('submit'));
            }
        });
    }

    applyTheme(currentTheme);

    // Method configurations
    const METHODS = {
        trapezoidal: {
            id: 'trapezoidal',
            title: 'Trapezoidal Rule Setup',
            desc: 'Integrate continuous functions using linear trapezoidal summation.',
            tagText: 'Trapezoidal Rule',
            nTag: 'n > 0',
            validateN: (n) => n > 0
        },
        simpson: {
            id: 'simpson',
            title: "Simpson's 1/3 Rule Setup",
            desc: "Integrate functions using parabolic sub-interval approximations. Requires an even number of intervals.",
            tagText: "Simpson's 1/3 Rule",
            nTag: 'n MUST BE EVEN',
            validateN: (n) => n > 0 && n % 2 === 0
        }
    };

    // Tab Switching Logic
    function switchTab(methodKey) {
        const config = METHODS[methodKey];
        if (!config) return;

        methodInput.value = config.id;
        methodTitle.textContent = config.title;
        methodDesc.textContent = config.desc;
        nValidationTag.textContent = config.nTag;

        if (methodKey === 'trapezoidal') {
            tabTrapezoidal.classList.add('active');
            tabTrapezoidal.setAttribute('aria-selected', 'true');
            tabSimpson.classList.remove('active');
            tabSimpson.setAttribute('aria-selected', 'false');
        } else {
            tabSimpson.classList.add('active');
            tabSimpson.setAttribute('aria-selected', 'true');
            tabTrapezoidal.classList.remove('active');
            tabTrapezoidal.setAttribute('aria-selected', 'false');

            // Automatically round up to next even number if odd
            let currentN = parseInt(nInput.value, 10);
            if (isNaN(currentN) || currentN <= 0) {
                nInput.value = 6;
            } else if (currentN % 2 !== 0) {
                nInput.value = currentN + 1;
            }
        }

        hideError();
    }

    tabTrapezoidal.addEventListener('click', () => switchTab('trapezoidal'));
    tabSimpson.addEventListener('click', () => switchTab('simpson'));

    // Preset Example Buttons
    presetBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            if (btn.dataset.expr) funcInput.value = btn.dataset.expr;
            if (btn.dataset.a) aInput.value = btn.dataset.a;
            if (btn.dataset.b) bInput.value = btn.dataset.b;
            if (btn.dataset.n) {
                let nVal = parseInt(btn.dataset.n, 10);
                if (methodInput.value === 'simpson' && nVal % 2 !== 0) {
                    nVal += 1;
                }
                nInput.value = nVal;
            }
            hideError();
            updateLiveMathPreview();
        });
    });

    const mathLivePreview = document.getElementById('math-live-preview');
    const mathToolbar = document.getElementById('math-toolbar');

    /**
     * Helper to render KaTeX into an HTML element.
     */
    function renderKaTeX(latexStr, container, displayMode = false) {
        if (!container) return;
        if (window.katex) {
            try {
                katex.render(latexStr, container, {
                    displayMode: displayMode,
                    throwOnError: false
                });
                return;
            } catch (err) {
                console.error('KaTeX rendering error:', err);
            }
        }
        container.textContent = latexStr;
    }

    /**
     * Initializes static LaTeX headers (Table headers, Sum titles).
     */
    function initStaticMathHeaders() {
        renderKaTeX('i', document.getElementById('th-i'));
        renderKaTeX('x_i', document.getElementById('th-xi'));
        renderKaTeX('f(x_i)', document.getElementById('th-fxi'));
        renderKaTeX('c_i', document.getElementById('th-ci'));
        renderKaTeX('c_i \\cdot f(x_i)', document.getElementById('th-cifxi'));
        renderKaTeX('\\left(\\sum f(x_{\\text{odd}})\\right)', document.getElementById('res-odd-sum-katex'));
        renderKaTeX('\\left(\\sum f(x_{\\text{even}})\\right)', document.getElementById('res-even-sum-katex'));
    }

    /**
     * Converts user math expression (ASCII or LaTeX) into clean LaTeX string for KaTeX rendering.
     * Accurately converts expressions like `x^2 + 3 ^ x - log(1/x)`.
     */
    function convertToLatex(expr) {
        if (!expr || !expr.trim()) return '';
        let str = expr.trim();

        // If it's already LaTeX
        if (str.includes('\\') || (str.includes('{') && str.includes('}'))) {
            return str;
        }

        // Clean whitespace around powers ^
        str = str.replace(/\s*\^\s*/g, '^');

        // Handle functions with parentheses e.g. log(1/x), sin(2*x), sqrt(x)
        const funcs = ['sin', 'cos', 'tan', 'asin', 'acos', 'atan', 'sinh', 'cosh', 'tanh', 'exp', 'log', 'ln', 'sqrt'];
        funcs.forEach(f => {
            const latexF = (f === 'log' || f === 'ln') ? '\\ln' : (f === 'sqrt' ? '\\sqrt' : '\\' + f);
            const reg = new RegExp('\\b' + f + '\\s*\\(([^)]+)\\)', 'gi');
            str = str.replace(reg, (match, inner) => {
                // convert fractions inside functions e.g. 1/x -> \frac{1}{x}
                let innerLatex = inner.replace(/(\b[a-zA-Z0-9\^\+\-]+\b|\([^\)]+\))\s*\/\s*(\b[a-zA-Z0-9\^\+\-]+\b|\([^\)]+\))/g, (m, p1, p2) => {
                    let num = p1.trim().replace(/^\((.*)\)$/, '$1');
                    let den = p2.trim().replace(/^\((.*)\)$/, '$1');
                    return `\\frac{${num}}{${den}}`;
                });
                if (f === 'sqrt') {
                    return `\\sqrt{${innerLatex}}`;
                }
                return `${latexF}\\left(${innerLatex}\\right)`;
            });
        });

        // Handle standalone fractions e.g. 1 / (1 + x^2) or 1/x
        str = str.replace(/(\b[a-zA-Z0-9\^\+\-]+\b|\([^\)]+\))\s*\/\s*(\b[a-zA-Z0-9\^\+\-]+\b|\([^\)]+\))/g, (match, p1, p2) => {
            let num = p1.trim().replace(/^\((.*)\)$/, '$1');
            let den = p2.trim().replace(/^\((.*)\)$/, '$1');
            return `\\frac{${num}}{${den}}`;
        });

        // Handle powers x^2, 3^x, (x+1)^2
        str = str.replace(/([a-zA-Z0-9\)]+)\^([a-zA-Z0-9]+|\([^\)]+\))/g, (match, base, exp) => {
            let cleanExp = exp.replace(/^\((.*)\)$/, '$1');
            return `${base}^{${cleanExp}}`;
        });

        // Replace pi
        str = str.replace(/\bpi\b/gi, '\\pi');

        // Replace * with \cdot
        str = str.replace(/\*/g, ' \\cdot ');

        return str;
    }

    /**
     * Updates the live math preview in real time as the user types.
     */
    function updateLiveMathPreview() {
        if (!mathLivePreview) return;
        const val = funcInput.value.trim();
        if (!val) {
            mathLivePreview.innerHTML = '<span style="color: var(--text-muted); font-style: italic;">f(x) = ...</span>';
            return;
        }

        const latexStr = convertToLatex(val);
        renderKaTeX(`f(x) = ${latexStr}`, mathLivePreview, false);
    }

    // Attach Live Input Listeners
    if (funcInput) {
        funcInput.addEventListener('input', updateLiveMathPreview);
        funcInput.addEventListener('keyup', updateLiveMathPreview);

        // Smart key handling: typing / on selected text converts to fraction
        funcInput.addEventListener('keydown', (e) => {
            if (e.key === '/') {
                const start = funcInput.selectionStart;
                const end = funcInput.selectionEnd;
                const text = funcInput.value;

                if (start !== end) {
                    e.preventDefault();
                    const selected = text.slice(start, end);
                    const replacement = `(${selected}) / ()`;
                    funcInput.value = text.slice(0, start) + replacement + text.slice(end);
                    funcInput.setSelectionRange(start + replacement.length - 1, start + replacement.length - 1);
                    updateLiveMathPreview();
                }
            }
        });
    }

    // Desmos Quick Math Toolbar buttons handler
    if (mathToolbar) {
        mathToolbar.addEventListener('click', (e) => {
            const btn = e.target.closest('.math-tool-btn');
            if (!btn) return;

            const mathType = btn.getAttribute('data-math');
            const start = funcInput.selectionStart || funcInput.value.length;
            const end = funcInput.selectionEnd || funcInput.value.length;
            const text = funcInput.value;
            const selected = text.slice(start, end);

            let insertText = '';
            let cursorOffset = 0;

            switch (mathType) {
                case 'frac':
                    insertText = selected ? `(${selected}) / ()` : `1 / ()`;
                    cursorOffset = insertText.length - 1;
                    break;
                case 'power':
                    insertText = selected ? `(${selected})^2` : `^2`;
                    cursorOffset = insertText.length;
                    break;
                case 'sqrt':
                    insertText = selected ? `sqrt(${selected})` : `sqrt(x)`;
                    cursorOffset = insertText.length;
                    break;
                case 'sin':
                    insertText = selected ? `sin(${selected})` : `sin(x)`;
                    cursorOffset = insertText.length;
                    break;
                case 'cos':
                    insertText = selected ? `cos(${selected})` : `cos(x)`;
                    cursorOffset = insertText.length;
                    break;
                case 'tan':
                    insertText = selected ? `tan(${selected})` : `tan(x)`;
                    cursorOffset = insertText.length;
                    break;
                case 'exp':
                    insertText = selected ? `exp(${selected})` : `exp(x)`;
                    cursorOffset = insertText.length;
                    break;
                case 'log':
                    insertText = selected ? `ln(${selected})` : `ln(x)`;
                    cursorOffset = insertText.length;
                    break;
                case 'pi':
                    insertText = `pi`;
                    cursorOffset = 2;
                    break;
            }

            funcInput.value = text.slice(0, start) + insertText + text.slice(end);
            funcInput.focus();
            funcInput.setSelectionRange(start + cursorOffset, start + cursorOffset);
            updateLiveMathPreview();
        });
    }

    // Initialize static math headers & live preview on load
    initStaticMathHeaders();
    updateLiveMathPreview();

    // Form Submission
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        hideError();

        const method = methodInput.value;
        const funcStr = funcInput.value.trim();
        const aVal = parseFloat(aInput.value);
        const bVal = parseFloat(bInput.value);
        const nVal = parseInt(nInput.value, 10);

        // Client-side quick validation
        if (!funcStr) {
            showError('Please enter a mathematical function expression.');
            return;
        }

        if (isNaN(aVal)) {
            showError('Please enter a valid numeric value for lower limit (a).');
            return;
        }

        if (isNaN(bVal)) {
            showError('Please enter a valid numeric value for upper limit (b).');
            return;
        }

        if (isNaN(nVal) || nVal <= 0) {
            showError('Number of intervals (n) must be a positive integer.');
            return;
        }

        if (method === 'simpson' && nVal % 2 !== 0) {
            showError(`Validation Error: Simpson's 1/3 Rule requires an EVEN number of intervals (n). You entered n = ${nVal}. Please change n to an even number (e.g., ${nVal + 1}).`);
            return;
        }

        // Send AJAX Calculation Request
        setLoading(true);

        try {
            const response = await fetch('/api/calculate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    method: method,
                    function: funcStr,
                    a: aVal,
                    b: bVal,
                    n: nVal,
                    theme: currentTheme
                })
            });

            const result = await response.json();

            if (!response.ok || !result.success) {
                showError(result.error || 'Failed to perform integration calculation.');
                resultsContainer.classList.add('hidden');
            } else {
                renderResults(result.data);
            }
        } catch (err) {
            showError('Network error occurred while connecting to calculation server.');
            resultsContainer.classList.add('hidden');
        } finally {
            setLoading(false);
        }
    });

    // UI Helper Functions
    function setLoading(isLoading) {
        if (isLoading) {
            calculateBtn.disabled = true;
            btnText.textContent = 'Calculating...';
            btnSpinner.classList.remove('hidden');
        } else {
            calculateBtn.disabled = false;
            btnText.textContent = 'Calculate Definite Integral';
            btnSpinner.classList.add('hidden');
        }
    }

    function showError(msg) {
        errorMessage.textContent = msg;
        errorBanner.classList.remove('hidden');
        errorBanner.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    function hideError() {
        errorBanner.classList.add('hidden');
        errorMessage.textContent = '';
    }

    // Render Results Cards with Full LaTeX Integration
    function renderResults(data) {
        hideError();

        // Primary Hero Meta
        resMethodTag.textContent = data.method;
        resExecTime.textContent = `${data.execution_time_ms} ms`;
        resValue.textContent = data.formatted_result;

        // Render Function in LaTeX on Hero card
        const latexFunc = convertToLatex(data.function);
        renderKaTeX(`f(x) = ${latexFunc}`, resFunc);

        resInterval.textContent = `[${data.a}, ${data.b}]`;
        resStepSize.textContent = data.h.toFixed(6);
        resIntervalsCnt.textContent = data.n;

        // Mathematical Formula in LaTeX
        if (data.formula_latex) {
            renderKaTeX(data.formula_latex, resFormulaBox, true);
        } else {
            resFormulaBox.innerHTML = data.formula_html;
        }

        // Steps List
        resStepsList.innerHTML = '';
        data.steps.forEach(step => {
            const li = document.createElement('li');
            li.textContent = step;
            resStepsList.appendChild(li);
        });

        // Simpson's Odd/Even Sums
        if (data.method.includes("Simpson")) {
            simpsonSumsCard.classList.remove('hidden');
            resOddSum.textContent = data.odd_sum !== undefined ? data.odd_sum.toFixed(6) : '0.000000';
            resEvenSum.textContent = data.even_sum !== undefined ? data.even_sum.toFixed(6) : '0.000000';
        } else {
            simpsonSumsCard.classList.add('hidden');
        }

        // Discretization Table Rows
        resTableBody.innerHTML = '';
        let totalWeighted = 0;

        data.table.forEach(row => {
            totalWeighted += row.weighted;
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td class="col-center">${row.index}</td>
                <td>${row.x.toFixed(6)}</td>
                <td>${row.fx.toFixed(6)}</td>
                <td class="col-center"><span class="tag-badge">${row.coefficient}</span></td>
                <td>${row.weighted.toFixed(6)}</td>
            `;
            resTableBody.appendChild(tr);
        });

        // Discretization Table Foot Totals in LaTeX
        resTableFoot.innerHTML = `
            <tr>
                <td colspan="4" style="text-align: right; padding-right: 1rem;">Total Weighted Sum (<span id="foot-total-katex"></span>):</td>
                <td>${totalWeighted.toFixed(6)}</td>
            </tr>
        `;
        renderKaTeX('\\sum c_i f(x_i)', document.getElementById('foot-total-katex'));

        // Graph Card Title / Description in LaTeX
        const graphFuncElement = document.getElementById('graph-func-latex');
        if (graphFuncElement) {
            renderKaTeX(`f(x) = ${latexFunc}`, graphFuncElement);
        }

        // Plot Image
        if (data.plot_b64) {
            graphCard.classList.remove('hidden');
            resPlotImg.src = data.plot_b64;
        } else {
            graphCard.classList.add('hidden');
        }

        resultsContainer.classList.remove('hidden');
        resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
});
