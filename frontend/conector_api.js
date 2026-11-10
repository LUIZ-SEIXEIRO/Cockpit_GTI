/**
 * Cockpit GTI — Conector Oficial de Telemetria SA-GTI (Estavel / Nativo)
 */
(function () {
    // Remove qualquer estilo injetado residual
    const tagResidual = document.getElementById('spaguas-glassmorphism-theme');
    if (tagResidual) tagResidual.remove();
    document.documentElement.removeAttribute('data-theme');
    document.body.removeAttribute('data-theme');

    async function checarStatusServico(url, timeoutMs = 2500) {
        try {
            const controller = new AbortController();
            const idTimeout = setTimeout(() => controller.abort(), timeoutMs);
            const resp = await fetch(url, { signal: controller.signal, cache: 'no-store' });
            clearTimeout(idTimeout);
            return resp.ok;
        } catch (e) {
            return false;
        }
    }

    async function atualizarTelemetria() {
        const sMariaDB = await checarStatusServico('/api/v1/mariadb/status');
        const sOllama = await checarStatusServico('/api/v1/ia/status');
        const sGlpi = await checarStatusServico('/api/v1/glpi/status');
        const sOpenProject = await checarStatusServico('/api/v1/openproject/status');
        const sNewApi = await checarStatusServico('/api/v1/newapi/status');

        const elMariaDB = document.getElementById('led-mariadb');
        const elOllama = document.getElementById('led-ollama');
        const elGlpi = document.getElementById('led-glpi');
        const elOp = document.getElementById('led-openproject');
        const elNewApi = document.getElementById('led-newapi');

        if (elMariaDB) elMariaDB.textContent = sMariaDB ? '🟢' : '🔴';
        if (elOllama) elOllama.textContent = sOllama ? '🟢' : '🔴';
        if (elGlpi) elGlpi.textContent = sGlpi ? '🟢' : '🔴';
        if (elOp) elOp.textContent = sOpenProject ? '🟢' : '🔴';
        if (elNewApi) elNewApi.textContent = sNewApi ? '🟢' : '🔴';

        const elSinc = document.getElementById('tempo-sinc');
        if (elSinc) {
            const agora = new Date();
            elSinc.textContent = agora.toLocaleTimeString('pt-BR');
        }
    }

    function montarWidgetInfra() {
        const topbar = document.querySelector('.topbar') || document.querySelector('header');
        if (!topbar) return;

        let containerInfra = document.getElementById('widget-infra-cockpit');
        if (!containerInfra) {
            containerInfra = document.createElement('div');
            containerInfra.id = 'widget-infra-cockpit';
            containerInfra.style.display = 'inline-flex';
            containerInfra.style.alignItems = 'center';
            containerInfra.style.gap = '8px';
            containerInfra.style.margin = '0 12px';
            containerInfra.style.flexShrink = '0';

            containerInfra.innerHTML = `
                <div style="display: inline-flex; align-items: center; gap: 6px; padding: 4px 10px; background: #f1f5f9; border: 1px solid #cbd5e1; border-radius: 16px; font-size: 11px; color: #334155;">
                    <span style="font-weight: 700; letter-spacing: 0.5px; color: #0f172a;">INFRA :5000</span>
                    <span id="led-mariadb" title="MariaDB (:3306)">🟢</span>
                    <span id="led-ollama" title="Ollama (:11434)">🟢</span>
                    <span id="led-glpi" title="GLPI Produção (Read-Only)">🟢</span>
                    <span id="led-openproject" title="OpenProject Produção (Trava SA-GTI)">🟢</span>
                    <span id="led-newapi" title="New API (:3001)">🟢</span>
                    <span style="color: #64748b; margin-left: 4px;">Sinc:</span>
                    <span id="tempo-sinc" style="font-weight: 600; color: #0f172a;">--:--:--</span>
                    <span id="btn-recarregar-infra" style="cursor: pointer; opacity: 0.8;" title="Recarregar Telemetria">🔄</span>
                </div>
            `;

            const elRef = topbar.querySelector('.user-profile') || topbar.querySelector('select') || null;
            if (elRef) {
                topbar.insertBefore(containerInfra, elRef);
            } else {
                topbar.appendChild(containerInfra);
            }

            document.getElementById('btn-recarregar-infra')?.addEventListener('click', atualizarTelemetria);
        }
    }

    function init() {
        montarWidgetInfra();
        atualizarTelemetria();
        setInterval(atualizarTelemetria, 15000);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
