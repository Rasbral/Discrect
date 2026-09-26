(() => {
    const CASE_LABELS = {
        distinct_real: 'Raíces reales distintas',
        double_real: 'Raíz real doble',
        complex_conjugate: 'Raíces complejas conjugadas',
        three_distinct_real: 'Tres raíces reales distintas',
        double_real_and_single: 'Raíz de multiplicidad 2 y una simple',
        triple_real: 'Raíz triple',
        complex_and_real: 'Una raíz real y un par complejo conjugado'
    };

    let theoryData = null;

    document.addEventListener('DOMContentLoaded', async () => {
        const content = document.getElementById('tutorial-content');
        const navButtons = document.querySelectorAll('.tutorial-nav__item');

        try {
            const res = await fetch('/api/docs/theory');
            theoryData = await res.json();
            renderOrder(1);
        } catch (err) {
            content.innerHTML = '<p class="error-text">No se pudo cargar la teoría desde el servidor.</p>';
            return;
        }

        navButtons.forEach((btn) => {
            btn.addEventListener('click', () => {
                navButtons.forEach((b) => b.classList.remove('is-active'));
                btn.classList.add('is-active');
                renderOrder(parseInt(btn.dataset.order, 10));
            });
        });
    });

    function renderOrder(orderNumber) {
        const content = document.getElementById('tutorial-content');
        const orderData = theoryData.orders.find((o) => o.order === orderNumber);
        if (!orderData) {
            content.innerHTML = '<p class="empty-state">Sin datos para este orden.</p>';
            return;
        }

        let html = `<h2 class="panel__title">${orderData.name}</h2>`;
        html += `<h3>Relación de recurrencia</h3>`;
        html += `<div class="formula-block">${orderData.equation}</div>`;
        html += `<h3>Ecuación característica</h3>`;
        html += `<div class="formula-block">${orderData.characteristic_eq}</div>`;

        if (orderData.explicit_form) {
            html += `<h3>Fórmula explícita</h3>`;
            html += `<div class="formula-block">${orderData.explicit_form}</div>`;
        }

        if (orderData.cases && orderData.cases.length) {
            html += `<h3>Casos según la naturaleza de las raíces</h3>`;
            orderData.cases.forEach((c) => {
                const label = CASE_LABELS[c.type] || c.type;
                html += `<p><strong>${label}</strong></p>`;
                html += `<div class="formula-block">${c.formula}</div>`;
            });
        }

        html += `<p class="metric-card__hint">
            Prueba estos coeficientes en el <a href="/">Dashboard</a> y observa cómo la
            gráfica recursiva y la explícita coinciden término a término.
        </p>`;

        content.innerHTML = html;
    }
})();
