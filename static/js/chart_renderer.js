const ChartRenderer = (() => {
    let chartInstance = null;

    function buildConstantSeries(length, value) {
        return new Array(length).fill(value);
    }

    function render(canvasEl, seriesPayload, options) {
        options = options || {};
        const thresholdValue = options.thresholdValue;
        const metricLabel = options.metricLabel || 'Valor';

        const labels = seriesPayload.n_indices.map((n) => `n=${n}`);

        const datasets = [
            {
                label: 'Recursivo',
                data: seriesPayload.recursive_terms,
                borderColor: '#3b82f6',
                backgroundColor: 'rgba(59, 130, 246, 0.08)',
                borderWidth: 2.5,
                pointRadius: 1.5,
                tension: 0.15,
                fill: false
            },
            {
                label: 'Explícito (cerrado)',
                data: seriesPayload.explicit_terms,
                borderColor: '#10b981',
                borderDash: [7, 4],
                borderWidth: 2,
                pointRadius: 0,
                tension: 0.15,
                fill: false
            },
            {
                label: 'Telemetría (con ruido)',
                data: seriesPayload.telemetry_terms,
                borderColor: 'rgba(245, 158, 11, 0.85)',
                borderWidth: 1,
                pointRadius: 0,
                tension: 0.25,
                fill: false
            }
        ];

        if (thresholdValue !== null && thresholdValue !== undefined && !Number.isNaN(thresholdValue)) {
            datasets.push({
                label: 'Umbral de capacidad',
                data: buildConstantSeries(labels.length, thresholdValue),
                borderColor: '#ef4444',
                borderWidth: 1.5,
                borderDash: [3, 3],
                pointRadius: 0,
                fill: false
            });
        }

        if (chartInstance) {
            chartInstance.destroy();
        }

        chartInstance = new Chart(canvasEl.getContext('2d'), {
            type: 'line',
            data: { labels, datasets },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: { mode: 'index', intersect: false },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        backgroundColor: '#1a2436',
                        borderColor: '#253247',
                        borderWidth: 1
                    }
                },
                scales: {
                    x: {
                        grid: { color: 'rgba(255,255,255,0.05)' },
                        ticks: { color: '#8fa1bb', maxTicksLimit: 14 }
                    },
                    y: {
                        grid: { color: 'rgba(255,255,255,0.05)' },
                        ticks: { color: '#8fa1bb' },
                        title: { display: true, text: metricLabel, color: '#8fa1bb' }
                    }
                }
            }
        });

        return chartInstance;
    }

    function destroy() {
        if (chartInstance) {
            chartInstance.destroy();
            chartInstance = null;
        }
    }

    return { render, destroy };
})();

window.ChartRenderer = ChartRenderer;
