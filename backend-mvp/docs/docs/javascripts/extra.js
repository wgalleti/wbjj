// JavaScript customizado para wBJJ Documentation

document.addEventListener('DOMContentLoaded', function() {
    // Inicializar funcionalidades
    initializeEnhancements();
    initializeAnalytics();
    initializeInteractivity();
});

/**
 * Funcionalidades de melhoria da experiência
 */
function initializeEnhancements() {
    // Adicionar indicadores de loading para links externos
    addExternalLinkIndicators();

    // Melhorar navegação com scroll spy
    initializeScrollSpy();

    // Adicionar animações aos elementos
    initializeAnimations();

    // Adicionar funcionalidade de cópia para código
    enhanceCodeBlocks();
}

/**
 * Adicionar indicadores para links externos
 */
function addExternalLinkIndicators() {
    const externalLinks = document.querySelectorAll('a[href^="http"]:not([href*="' + location.hostname + '"])');

    externalLinks.forEach(link => {
        link.setAttribute('target', '_blank');
        link.setAttribute('rel', 'noopener noreferrer');

        // Adicionar ícone de link externo
        if (!link.querySelector('.external-link-icon')) {
            const icon = document.createElement('span');
            icon.className = 'external-link-icon';
            icon.innerHTML = ' ↗';
            icon.style.fontSize = '0.8em';
            icon.style.opacity = '0.7';
            link.appendChild(icon);
        }
    });
}

/**
 * Navegação com scroll spy
 */
function initializeScrollSpy() {
    const headers = document.querySelectorAll('h2, h3, h4, h5, h6');
    const navLinks = document.querySelectorAll('.md-nav__link');

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const id = entry.target.id;

                // Remover classe ativa de todos os links
                navLinks.forEach(link => link.classList.remove('active'));

                // Adicionar classe ativa ao link correspondente
                const activeLink = document.querySelector(`.md-nav__link[href="#${id}"]`);
                if (activeLink) {
                    activeLink.classList.add('active');
                }
            }
        });
    }, {
        rootMargin: '-20% 0px -80% 0px'
    });

    headers.forEach(header => {
        if (header.id) {
            observer.observe(header);
        }
    });
}

/**
 * Animações de entrada
 */
function initializeAnimations() {
    const animateElements = document.querySelectorAll('.grid.cards > div, table, .highlight, .admonition');

    const animationObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.animation = 'fadeInUp 0.6s ease-out';
                animationObserver.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.1
    });

    animateElements.forEach(element => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(20px)';
        animationObserver.observe(element);
    });
}

/**
 * Melhorar blocos de código
 */
function enhanceCodeBlocks() {
    const codeBlocks = document.querySelectorAll('pre code');

    codeBlocks.forEach(codeBlock => {
        const pre = codeBlock.parentElement;

        // Adicionar botão de cópia se não existir
        if (!pre.querySelector('.copy-button')) {
            const copyButton = document.createElement('button');
            copyButton.className = 'copy-button';
            copyButton.innerHTML = '📋';
            copyButton.title = 'Copiar código';
            copyButton.style.cssText = `
                position: absolute;
                top: 0.5rem;
                right: 0.5rem;
                background: rgba(0, 0, 0, 0.7);
                color: white;
                border: none;
                border-radius: 4px;
                padding: 0.25rem 0.5rem;
                cursor: pointer;
                font-size: 0.8rem;
                opacity: 0.8;
                transition: opacity 0.2s ease;
            `;

            copyButton.addEventListener('click', () => {
                navigator.clipboard.writeText(codeBlock.textContent).then(() => {
                    copyButton.innerHTML = '✅';
                    setTimeout(() => {
                        copyButton.innerHTML = '📋';
                    }, 2000);
                });
            });

            pre.style.position = 'relative';
            pre.appendChild(copyButton);
        }
    });
}

/**
 * Analytics e tracking (opcional)
 */
function initializeAnalytics() {
    // Tracking de cliques em links importantes
    const importantLinks = document.querySelectorAll('a[href*="api.md"], a[href*="docker.md"], a[href*="context.md"]');

    importantLinks.forEach(link => {
        link.addEventListener('click', function() {
            if (typeof gtag !== 'undefined') {
                gtag('event', 'documentation_click', {
                    'page_title': this.textContent,
                    'page_location': this.href
                });
            }
        });
    });

    // Tracking de tempo na página
    let startTime = Date.now();

    window.addEventListener('beforeunload', function() {
        const timeOnPage = Math.round((Date.now() - startTime) / 1000);

        if (typeof gtag !== 'undefined' && timeOnPage > 10) {
            gtag('event', 'page_engagement', {
                'page_title': document.title,
                'time_on_page': timeOnPage
            });
        }
    });
}

/**
 * Funcionalidades interativas
 */
function initializeInteractivity() {
    // Adicionar tooltips para ícones
    addTooltips();

    // Melhorar tabelas com funcionalidades de ordenação
    enhanceTables();

    // Adicionar funcionalidade de busca avançada
    enhanceSearch();
}

/**
 * Adicionar tooltips
 */
function addTooltips() {
    const iconElements = document.querySelectorAll('.twemoji, .md-icon');

    iconElements.forEach(icon => {
        if (icon.alt && !icon.title) {
            icon.title = icon.alt;
        }
    });
}

/**
 * Melhorar tabelas
 */
function enhanceTables() {
    const tables = document.querySelectorAll('table');

    tables.forEach(table => {
        // Adicionar classe para melhor estilização
        table.classList.add('enhanced-table');

        // Tornar tabelas responsivas
        if (!table.parentElement.classList.contains('table-wrapper')) {
            const wrapper = document.createElement('div');
            wrapper.className = 'table-wrapper';
            wrapper.style.overflowX = 'auto';
            table.parentNode.insertBefore(wrapper, table);
            wrapper.appendChild(table);
        }
    });
}

/**
 * Melhorar busca
 */
function enhanceSearch() {
    const searchInput = document.querySelector('.md-search__input');

    if (searchInput) {
        // Adicionar shortcuts de teclado
        document.addEventListener('keydown', function(e) {
            // Ctrl/Cmd + K para focar na busca
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                searchInput.focus();
            }

            // ESC para limpar busca
            if (e.key === 'Escape' && document.activeElement === searchInput) {
                searchInput.value = '';
                searchInput.blur();
            }
        });

        // Placeholder dinâmico
        const placeholders = [
            'Buscar na documentação...',
            'Ex: "multitenancy", "JWT", "Docker"...',
            'Pressione Ctrl+K para buscar...'
        ];

        let placeholderIndex = 0;
        setInterval(() => {
            if (document.activeElement !== searchInput) {
                searchInput.placeholder = placeholders[placeholderIndex];
                placeholderIndex = (placeholderIndex + 1) % placeholders.length;
            }
        }, 3000);
    }
}

/**
 * Funcionalidades para modo escuro/claro
 */
function initializeThemeToggle() {
    const themeToggle = document.querySelector('[data-md-component="palette"]');

    if (themeToggle) {
        themeToggle.addEventListener('change', function() {
            // Salvar preferência
            const isDark = document.body.getAttribute('data-md-color-scheme') === 'slate';
            localStorage.setItem('theme-preference', isDark ? 'dark' : 'light');

            // Analytics
            if (typeof gtag !== 'undefined') {
                gtag('event', 'theme_change', {
                    'theme': isDark ? 'dark' : 'light'
                });
            }
        });
    }
}

/**
 * Melhorias de performance
 */
function initializePerformanceOptimizations() {
    // Lazy loading para imagens
    const images = document.querySelectorAll('img');

    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    if (img.dataset.src) {
                        img.src = img.dataset.src;
                        img.removeAttribute('data-src');
                    }
                    imageObserver.unobserve(img);
                }
            });
        });

        images.forEach(img => {
            if (img.src && !img.complete) {
                imageObserver.observe(img);
            }
        });
    }
}

// Inicializar todas as funcionalidades quando a página carregar
window.addEventListener('load', function() {
    initializeThemeToggle();
    initializePerformanceOptimizations();
});

// Reinicializar funcionalidades quando navegar (SPA)
document.addEventListener('DOMContentLoaded', function() {
    // Observer para mudanças no conteúdo (navegação SPA)
    const contentObserver = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                // Reinicializar funcionalidades para novo conteúdo
                setTimeout(() => {
                    initializeEnhancements();
                    initializeInteractivity();
                }, 100);
            }
        });
    });

    const content = document.querySelector('.md-content');
    if (content) {
        contentObserver.observe(content, {
            childList: true,
            subtree: true
        });
    }
});

// Adicionar console easter egg
console.log(`
🥋 wBJJ - Sistema de Gestão para Academias de Jiu-Jitsu

📚 Documentação: ${window.location.origin}
🔗 GitHub: https://github.com/wbjj/backend
🐳 Docker: https://hub.docker.com/r/wbjj/backend

Desenvolvido com ❤️ usando Django + DRF + Material for MkDocs
`);
