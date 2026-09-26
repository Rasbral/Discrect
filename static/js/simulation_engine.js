(() => {
    const DEFAULT_ORDER2 = { coefficients: [1.2, -0.2], initial_conditions: [120, 140] };

    const els = {};

    document.addEventListener('DOMContentLoaded', () => {
        cacheElements();
        bindEvents();
        checkEngineStatus();
        loadPresets();
        renderDynamicInputs(2, DEFAULT_ORDER2.coefficients, DEFAULT_ORDER2.initial_conditions);
        runSimulation();
    });

    function cacheElements() {
        els.engineStatus = document.getElementById('engine-status');
        els.presetSelect = document.getElementById('preset-select');
        els.btnLoadPreset = document.getElementById('btn-load-preset');
        els.btnRandom = document.getElementById('btn-random');
        els.btnSimulate = document.getElementById('btn-simulate');
        els.orderSelect = document.getElementById('order-select');
        els.coefContainer = document.getElementById('coefficients-inputs');
        els.icContainer = document.getElementById('initial-conditions-inputs');
        els.nTerms = document.getElementById('n-terms-input');
        els.capacityThreshold = document.getElementById('capacity-threshold-input');
        els.metricType = document.getElementById('metric-type-input');
        els.unit = document.getElementById('unit-input');
        els.repetitions = document.getElementById('repetitions-input');
        els.noiseLevel = document.getElementById('noise-level-input');
        els.controlError = document.getElementById('control-panel-error');

        els.mathPanel = document.getElementById('math-solution-panel');
        els.chartEmptyState = document.getElementById('chart-empty-state');
        els.chartCanvas = document.getElementById('capacity-chart');
    }

    function bindEvents() {
        els.orderSelect.addEventListener('change', () => {
            renderDynamicInputs(getOrder());
        });
        els.btnSimulate.addEventListener('click', runSimulation);
        els.btnRandom.addEventListener('click', loadRandomScenario);
        els.btnLoadPreset.addEventListener('click', loadSelectedPreset);
    }

  
    async function checkEngineStatus() {
        try {
            const res = await fetch('/api/status');
            const data = await res.json();
            els.engineStatus.className = 'status-pill status-pill--online';
            els.engineStatus.innerHTML = `<span class="status-pill__dot"></span> ${data.message}`;
        } catch (err) {
            els.engineStatus.className = 'status-pill status-pill--error';
            els.engineStatus.innerHTML = '<span class="status-pill__dot"></span> Motor no disponible';
        }
    }


    async function loadPresets() {
        try {
            const res = await fetch('/api/presets');
            const data = await res.json();
            if (!data.success) return;
            data.presets.forEach((preset) => {
                const opt = document.createElement('option');
                opt.value = preset.id;
                opt.textContent = preset.name;
                els.presetSelect.appendChild(opt);
            });
        } catch (err) {
            showToast('No se pudieron cargar los escenarios predefinidos.');
        }
    }

    async function loadSelectedPreset() {
        const presetId = els.presetSelect.value;
        if (!presetId) {
            showToast('Selecciona primero un escenario predefinido.');
            return;
        }
        await fetchScenarioAndApply(`/api/random-scenario?preset=${encodeURIComponent(presetId)}`);
    }

    async function loadRandomScenario() {
        const order = getOrder();
        await fetchScenarioAndApply(`/api/random-scenario?order=${order}`);
    }

    async function fetchScenarioAndApply(url) {
        try {
            els.btnRandom.disabled = true;
            const res = await fetch(url);
            const data = await res.json();
            if (!data.success) {
                showToast(data.error || 'No se pudo generar el escenario.');
                return;
            }
            applyScenario(data.scenario);
            await runSimulation();
        } catch (err) {
            showToast('Error de red al solicitar el escenario.');
        } finally {
            els.btnRandom.disabled = false;
        }
    }

    function applyScenario(scenario) {
        els.orderSelect.value = String(scenario.order);
        renderDynamicInputs(scenario.order, scenario.coefficients, scenario.initial_conditions);
        els.capacityThreshold.value = scenario.capacity_threshold ?? '';
        els.metricType.value = scenario.metric_type || 'vCPU Cores';
        els.unit.value = scenario.unit || 'cores';
    }


    function getOrder() {
        return parseInt(els.orderSelect.value, 10) || 2;
    }

    function renderDynamicInputs(order, coefficients, initialConditions) {
        els.coefContainer.innerHTML = '';
        els.icContainer.innerHTML = '';

        for (let i = 0; i < order; i++) {
            const coefInput = document.createElement('input');
            coefInput.type = 'number';
            coefInput.step = 'any';
            coefInput.id = `coef-${i}`;
            coefInput.placeholder = `c${i + 1}`;
            coefInput.value = coefficients && coefficients[i] !== undefined ? coefficients[i] : (i === 0 ? 1 : 0);
            els.coefContainer.appendChild(coefInput);

            const icInput = document.createElement('input');
            icInput.type = 'number';
            icInput.step = 'any';
            icInput.id = `ic-${i}`;
            icInput.placeholder = `a${i}`;
            icInput.value = initialConditions && initialConditions[i] !== undefined ? initialConditions[i] : 100;
            els.icContainer.appendChild(icInput);
        }
    }

    function collectPayload() {
        const order = getOrder();
        const coefficients = [];
        const initialConditions = [];

        for (let i = 0; i < order; i++) {
            coefficients.push(parseFloat(document.getElementById(`coef-${i}`).value));
            initialConditions.push(parseFloat(document.getElementById(`ic-${i}`).value));
        }

        const capacityRaw = els.capacityThreshold.value;

        return {
            order,
            coefficients,
            initial_conditions: initialConditions,
            n_terms: parseInt(els.nTerms.value, 10) || 20,
            capacity_threshold: capacityRaw === '' ? null : parseFloat(capacityRaw),
            metric_type: els.metricType.value || 'vCPU Cores',
            unit: els.unit.value || 'cores',
            repetitions: parseInt(els.repetitions.value, 10) || 300,
            noise_level: parseFloat(els.noiseLevel.value) || 0.035
        };
    }


    async function runSimulation() {
        hideError();
        const payload = collectPayload();

        if (payload.coefficients.some(Number.isNaN) || payload.initial_conditions.some(Number.isNaN)) {
            showError('Revisa los coeficientes y condiciones iniciales: contienen valores no numéricos.');
            return;
        }

        setLoading(true);
        try {
            const res = await fetch('/api/solve', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await res.json();

            if (!data.success) {
                showError(data.error || 'Error desconocido al resolver la recurrencia.');
                return;
            }

            renderChart(data);
            renderMathPanel(data.math_solution);
            renderMetricsCards(data.cloudops_diagnosis, data.validation, payload);
            renderBenchmark(data.benchmark);
        } catch (err) {
            showError('No se pudo contactar al servidor Flask. ¿Está corriendo app.py?');
        } finally {
            setLoading(false);
        }
    }

    function setLoading(isLoading) {
        els.btnSimulate.disabled = isLoading;
        els.btnSimulate.textContent = isLoading ? 'Calculando…' : '▶ Ejecutar simulación';
    }

    function showError(message) {
        els.controlError.textContent = message;
        els.controlError.hidden = false;
    }

    function hideError() {
        els.controlError.hidden = true;
    }

    function showToast(message) {
        const container = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = 'toast';
        toast.textContent = message;
        container.appendChild(toast);
        setTimeout(() => toast.remove(), 4000);
    }


    function renderChart(data) {
        els.chartEmptyState.hidden = true;
        ChartRenderer.render(els.chartCanvas, data.series, {
            thresholdValue: data.inputs.capacity_threshold,
            metricLabel: `${data.inputs.metric_type} (${data.inputs.unit})`
        });
    }


    function renderMathPanel(solution) {
        els.mathPanel.hidden = false;
        document.getElementById('math-char-poly').textContent = `${solution.characteristic_polynomial_text}`;
        document.getElementById('math-solution-type').textContent = formatSolutionType(solution.solution_type);
        document.getElementById('math-explicit-formula').textContent = solution.explicit_formula_text;

        const rootsBody = document.querySelector('#roots-table tbody');
        rootsBody.innerHTML = '';
        solution.roots.forEach((r) => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>r<sub>${r.index}</sub></td>
                <td>${r.display}</td>
                <td>${r.modulus.toFixed(4)}</td>
                <td>${r.multiplicity}</td>
                <td>${r.type === 'complex' ? 'Compleja' : 'Real'}</td>
            `;
            rootsBody.appendChild(row);
        });

        const constBody = document.querySelector('#constants-table tbody');
        constBody.innerHTML = '';
        solution.constants.forEach((c) => {
            const row = document.createElement('tr');
            row.innerHTML = `<td>${c.name}</td><td>${c.formatted}</td>`;
            constBody.appendChild(row);
        });

        const stepsList = document.getElementById('steps-list');
        stepsList.innerHTML = '';
        solution.steps.forEach((step) => {
            const li = document.createElement('li');
            li.textContent = step.latex;
            stepsList.appendChild(li);
        });
    }

    function formatSolutionType(type) {
        const map = {
            order1: 'Orden 1',
            order2_distinct: 'Orden 2 · Raíces reales distintas',
            order2_double: 'Orden 2 · Raíz real doble',
            order2_complex: 'Orden 2 · Raíces complejas conjugadas',
            order3_distinct: 'Orden 3 · Tres raíces reales distintas',
            order3_double: 'Orden 3 · Raíz doble + simple',
            order3_triple: 'Orden 3 · Raíz triple',
            order3_complex: 'Orden 3 · Raíz real + par complejo'
        };
        return map[type] || type;
    }

    const REGIME_LABELS = {
        CONVERGENT: 'Convergente',
        EQUILIBRIUM: 'Equilibrio',
        GROWTH: 'Crecimiento',
        DIVERGENT: 'Divergente'
    };

    function renderMetricsCards(diagnosis, validation, inputs) {
        document.getElementById('metric-regime-value').textContent = REGIME_LABELS[diagnosis.regime] || diagnosis.regime;
        const badge = document.getElementById('metric-regime-badge');
        badge.textContent = diagnosis.status.replaceAll('_', ' ');
        badge.className = `badge badge--${diagnosis.alert_level}`;

        document.getElementById('metric-health-value').textContent = `${diagnosis.health_score} / 100`;
        document.getElementById('metric-health-bar').style.width = `${diagnosis.health_score}%`;

        document.getElementById('metric-growth-value').textContent = `${diagnosis.growth_rate_pct.toFixed(2)}%`;
        document.getElementById('metric-dominant-root').textContent = `Raíz dominante |r|: ${diagnosis.dominant_root_modulus.toFixed(4)}`;

        const osc = diagnosis.oscillation_report;
        document.getElementById('metric-oscillation-value').textContent = osc.has_oscillations ? 'Sí' : 'No';
        document.getElementById('metric-oscillation-period').textContent = osc.period_weeks
            ? `Periodo: ${osc.period_weeks} semanas`
            : 'Sin ciclo detectado';

        const cap = diagnosis.capacity_report;
        document.getElementById('metric-capacity-label').textContent = `Capacidad (${inputs.metric_type})`;
        if (cap.threshold !== null && cap.threshold !== undefined) {
            document.getElementById('metric-capacity-value').textContent = `${cap.peak_headroom_pct.toFixed(1)}%`;
            document.getElementById('metric-capacity-hint').textContent = cap.threshold_exceeded
                ? `⚠️ Saturación en la semana n=${cap.saturation_week}`
                : `Pico: ${cap.peak_value} ${inputs.unit} · dentro del umbral`;
        } else {
            document.getElementById('metric-capacity-value').textContent = '—';
            document.getElementById('metric-capacity-hint').textContent = 'Sin umbral configurado';
        }

        document.getElementById('metric-validation-value').textContent = `${validation.match_percentage}%`;
        document.getElementById('metric-validation-hint').textContent = validation.is_valid
            ? `Coincidencia exacta en ${validation.total_terms} términos`
            : `Error máx.: ${validation.max_absolute_error}`;
    }


    function renderBenchmark(benchmark) {
        const rec = benchmark.recursive;
        const exp = benchmark.explicit;
        const comp = benchmark.comparison;

        document.getElementById('bench-rec-avg').textContent = `${rec.avg_latency_us} µs`;
        document.getElementById('bench-exp-avg').textContent = `${exp.avg_latency_us} µs`;

        const maxLatency = Math.max(rec.avg_latency_us, exp.avg_latency_us) || 1;
        document.getElementById('bench-bar-recursive').style.width = `${(rec.avg_latency_us / maxLatency) * 100}%`;
        document.getElementById('bench-bar-explicit').style.width = `${(exp.avg_latency_us / maxLatency) * 100}%`;

        document.getElementById('bench-faster-method').textContent = comp.faster_method === 'explicit' ? 'El método explícito' : 'El método recursivo';
        document.getElementById('bench-speedup').textContent = comp.series_speedup;
        document.getElementById('bench-nth-speedup').textContent = comp.nth_term_speedup;

        document.getElementById('bench-rec-avg-td').textContent = rec.avg_latency_us;
        document.getElementById('bench-rec-min-td').textContent = rec.min_latency_us;
        document.getElementById('bench-rec-max-td').textContent = rec.max_latency_us;
        document.getElementById('bench-rec-std-td').textContent = rec.std_latency_us;
        document.getElementById('bench-rec-complexity-td').textContent = rec.time_complexity;

        document.getElementById('bench-exp-avg-td').textContent = exp.avg_latency_us;
        document.getElementById('bench-exp-min-td').textContent = exp.min_latency_us;
        document.getElementById('bench-exp-max-td').textContent = exp.max_latency_us;
        document.getElementById('bench-exp-std-td').textContent = exp.std_latency_us;
        document.getElementById('bench-exp-complexity-td').textContent = exp.time_complexity;
    }
})();
