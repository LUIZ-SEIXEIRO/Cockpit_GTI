// H:\glpi-spaguas\frontend\abas\00_roteador_abas.js

window.currentTab = 'dashboards';

window.switchTab = function(tabId, updateHash = true) {
    // 1. Oculta todas as views e remove marcação do menu
    document.querySelectorAll('.tab-view').forEach(view => {
        view.classList.remove('active');
    });
    document.querySelectorAll('.sidebar-menu .nav-item').forEach(nav => {
        nav.classList.remove('active');
    });

    // 2. Exibe a view selecionada e marca o menu lateral correspondente
    const activeView = document.getElementById('view-' + tabId);
    if (activeView) {
        activeView.classList.add('active');
    } else {
        console.warn(`Aviso: A view 'view-${tabId}' não foi encontrada no DOM.`);
        return;
    }

    const activeNav = document.querySelector(`.sidebar-menu .nav-item[data-tab="${tabId}"]`);
    if (activeNav) {
        activeNav.classList.add('active');
    }

    window.currentTab = tabId;

    // Atualiza o hash do URL sem recarregar a página
    if (updateHash && window.location.hash !== '#' + tabId) {
        window.location.hash = tabId;
    }

    // 3. Dispara o gatilho de inicialização exclusivo da aba (Lazy Loading lógico)
    const initFunctionName = 'initAba_' + tabId;
    if (typeof window[initFunctionName] === 'function') {
        window[initFunctionName]();
    }
};

// Controle da Sidebar Retrátil
window.toggleSidebar = function() {
    document.getElementById('sidebar').classList.toggle('collapsed');
};

// Inicialização baseada no Hash do URL ao carregar a página (ou fallback para dashboards)
window.addEventListener('DOMContentLoaded', () => {
    const hash = window.location.hash.replace('#', '');
    if (hash && document.getElementById('view-' + hash)) {
        window.switchTab(hash, false);
    } else {
        window.switchTab('dashboards', false);
    }
});

// Ouve alterações manuais no URL (ex: alterar o hash no browser ou botões histórico)
window.addEventListener('hashchange', () => {
    const hash = window.location.hash.replace('#', '');
    if (hash && document.getElementById('view-' + hash) && hash !== window.currentTab) {
        window.switchTab(hash, false);
    }
});