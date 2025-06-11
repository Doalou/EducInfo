/**
 * Script amélioré pour le tableau de bord administrateur EducInfo v1.2
 * Gestion moderne de la sidebar avec animations fluides
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialiser le tableau de bord moderne
    initModernDashboard();
    
    // Ajouter les écouteurs d'événements pour les confirmations
    initConfirmActions();
    
    // Initialiser l'état de la sidebar moderne
    initModernSidebar();
    
    // ⚠️ NOTE: La gestion du thème est maintenant gérée par dashboard.html
    // initThemeToggle(); - DÉSACTIVÉ pour éviter les conflits
    
    // Gérer le redimensionnement de la fenêtre avec debouncing
    window.addEventListener('resize', debounce(handleWindowResize, 150));
    
    // Initialiser les animations d'entrée
    initEntranceAnimations();
});

/**
 * Initialise le tableau de bord moderne avec toutes ses fonctionnalités
 */
function initModernDashboard() {
    // Initialiser les gestionnaires d'événements pour la navigation
    const navButtons = document.querySelectorAll('.sidebar-nav');
    
    navButtons.forEach(button => {
        // Gestionnaires de survol pour les effets visuels
        button.addEventListener('mouseenter', handleNavButtonHover);
        button.addEventListener('mouseleave', handleNavButtonLeave);
        
        // Gestionnaire de clic pour la navigation
        if (button.getAttribute('onclick')) {
            // Le onclick est déjà défini dans le HTML, on l'utilise
            button.addEventListener('click', handleNavButtonClick);
        }
    });

    // Gérer les indicateurs de statut
    initStatusIndicators();
    
    // Activer l'onglet par défaut
    showTab('overview');
}

/**
 * Gère l'effet de survol des boutons de navigation
 */
function handleNavButtonHover(e) {
    const button = e.currentTarget;
    const icon = button.querySelector('.w-12, .w-14');
    const badge = button.querySelector('.bg-red-100, .bg-emerald-100, .bg-orange-100, .bg-slate-100');
    
    // Animation de l'icône
    if (icon) {
        icon.style.transform = 'scale(1.05) translateY(-2px)';
        icon.style.transition = 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
    }
    
    // Animation du badge
    if (badge) {
        badge.style.transform = 'scale(1.1)';
        badge.style.transition = 'all 0.2s ease';
    }
    
    // Effet de parallaxe subtil
    button.style.transform = 'translateX(4px)';
    button.style.transition = 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
}

/**
 * Gère la fin du survol des boutons de navigation
 */
function handleNavButtonLeave(e) {
    const button = e.currentTarget;
    const icon = button.querySelector('.w-12, .w-14');
    const badge = button.querySelector('.bg-red-100, .bg-emerald-100, .bg-orange-100, .bg-slate-100');
    
    // Réinitialiser les transformations
    if (icon) {
        icon.style.transform = '';
    }
    
    if (badge) {
        badge.style.transform = '';
    }
    
    button.style.transform = '';
}

/**
 * Gère les clics sur les boutons de navigation
 */
function handleNavButtonClick(e) {
    const button = e.currentTarget;
    
    // Animation de clic
    button.style.transform = 'scale(0.95)';
    
    setTimeout(() => {
        button.style.transform = '';
    }, 150);
    
    // Déclencher l'effet de pulsation pour les indicateurs
    const statusDot = button.querySelector('.animate-pulse');
    if (statusDot) {
        statusDot.style.animation = 'none';
        setTimeout(() => {
            statusDot.style.animation = '';
        }, 100);
    }
}

/**
 * Affiche un onglet spécifique et masque les autres
 */
function showTab(tabName) {
    // Masquer tous les panels
    const allPanels = document.querySelectorAll('.tab-panel');
    allPanels.forEach(panel => {
        panel.classList.add('hidden');
        panel.classList.remove('active');
    });
    
    // Afficher le panel cible
    const targetPanel = document.getElementById(tabName + '-panel');
    if (targetPanel) {
        targetPanel.classList.remove('hidden');
        targetPanel.classList.add('active');
        
        // Animation d'entrée
        targetPanel.style.opacity = '0';
        targetPanel.style.transform = 'translateY(20px)';
        
        requestAnimationFrame(() => {
            targetPanel.style.transition = 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)';
            targetPanel.style.opacity = '1';
            targetPanel.style.transform = 'translateY(0)';
            
            // Nettoyer après l'animation
            setTimeout(() => {
                targetPanel.style.transition = '';
            }, 400);
        });
    }
    
    // Mettre à jour le titre de la page
    updatePageTitle(tabName);
    
    // Mettre à jour les états actifs dans la navigation
    updateActiveStates(tabName);
    
    // Fermer la sidebar sur mobile après sélection
    if (window.innerWidth < 1024) {
        const sidebar = document.getElementById('sidebar');
        if (sidebar && !sidebar.classList.contains('-translate-x-full')) {
            toggleSidebar();
        }
    }
}

/**
 * Met à jour le titre de la page selon l'onglet actif
 */
function updatePageTitle(tabName) {
    const titles = {
        'overview': { title: 'Vue d\'ensemble', subtitle: 'Tableau de bord administrateur' },
        'absences': { title: 'Gestion des Absences', subtitle: 'Professeurs absents' },
        'events': { title: 'Gestion des Événements', subtitle: 'Calendrier scolaire' },
        'cantine': { title: 'Menu de la Cantine', subtitle: 'Gestion des repas' },
        'transports': { title: 'Configuration CTS', subtitle: 'Transport public' },
        'settings': { title: 'Paramètres', subtitle: 'Configuration générale' }
    };
    
    const pageTitle = document.getElementById('page-title');
    const pageSubtitle = document.getElementById('page-subtitle');
    
    if (pageTitle && titles[tabName]) {
        // Animation de changement de titre
        pageTitle.style.opacity = '0';
        pageSubtitle.style.opacity = '0';
        
        setTimeout(() => {
            pageTitle.textContent = titles[tabName].title;
            pageSubtitle.textContent = titles[tabName].subtitle;
            
            pageTitle.style.transition = 'opacity 0.3s ease';
            pageSubtitle.style.transition = 'opacity 0.3s ease';
            pageTitle.style.opacity = '1';
            pageSubtitle.style.opacity = '1';
            
            // Nettoyer les transitions
            setTimeout(() => {
                pageTitle.style.transition = '';
                pageSubtitle.style.transition = '';
            }, 300);
        }, 150);
    }
}

/**
 * Met à jour les états actifs dans la navigation
 */
function updateActiveStates(activeTabName) {
    // Réinitialiser tous les boutons
    const allNavButtons = document.querySelectorAll('.sidebar-nav');
    allNavButtons.forEach(button => {
        button.classList.remove('active');
        button.classList.remove('bg-white', 'dark:bg-slate-800');
        button.classList.add('bg-white/30', 'dark:bg-slate-800/30');
    });
    
    // Activer le bouton correspondant
    const activeButton = document.querySelector(`[data-target="${activeTabName}"]`);
    if (activeButton) {
        activeButton.classList.add('active');
        activeButton.classList.remove('bg-white/30', 'dark:bg-slate-800/30');
        activeButton.classList.add('bg-white', 'dark:bg-slate-800');
        
        // Animation de pulsation
        activeButton.style.animation = 'pulse-once 0.6s ease-in-out';
        setTimeout(() => {
            activeButton.style.animation = '';
        }, 600);
    }
    
    // Mettre à jour la navigation mobile
    const mobileButtons = document.querySelectorAll('.md\\:hidden button[onclick*="showTab"]');
    mobileButtons.forEach(button => {
        const onclick = button.getAttribute('onclick');
        if (onclick && onclick.includes(`'${activeTabName}'`)) {
            button.classList.add('bg-gray-100', 'dark:bg-gray-700');
        } else {
            button.classList.remove('bg-gray-100', 'dark:bg-gray-700');
        }
    });
}

/**
 * Toggle la sidebar avec animations fluides
 */
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebarOverlay');
    const mainContent = document.querySelector('.main-content-area');
    
    if (!sidebar) return;
    
    const isHidden = sidebar.classList.contains('-translate-x-full');
    const isMobile = window.innerWidth < 1024;
    
    if (isHidden) {
        // Afficher la sidebar
        sidebar.classList.remove('-translate-x-full');
        
        if (isMobile) {
            // Mobile : afficher l'overlay
            if (overlay) {
                overlay.classList.add('show');
            }
        } else {
            // Desktop : ajuster le contenu principal
            if (mainContent) {
                mainContent.style.transition = 'margin-left 0.3s ease';
                mainContent.style.marginLeft = '20rem';
            }
        }
        
        // Sauvegarder l'état
        if (!isMobile) {
            localStorage.setItem('sidebarVisible', 'true');
        }
        
    } else {
        // Masquer la sidebar
        sidebar.classList.add('-translate-x-full');
        
        if (isMobile) {
            // Mobile : masquer l'overlay
            if (overlay) {
                overlay.classList.remove('show');
            }
        } else {
            // Desktop : réajuster le contenu principal
            if (mainContent) {
                mainContent.style.transition = 'margin-left 0.3s ease';
                mainContent.style.marginLeft = '0';
            }
        }
        
        // Sauvegarder l'état
        if (!isMobile) {
            localStorage.setItem('sidebarVisible', 'false');
        }
    }
    
    // Nettoyer les transitions après animation
    setTimeout(() => {
        if (mainContent) {
            mainContent.style.transition = '';
        }
    }, 300);
}

/**
 * Initialise les animations d'entrée
 */
function initEntranceAnimations() {
    // Animation d'entrée pour les éléments principaux
    const animatedElements = document.querySelectorAll('.sidebar-nav, .tab-panel');
    
    animatedElements.forEach((element, index) => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            element.style.transition = 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)';
            element.style.opacity = '1';
            element.style.transform = 'translateY(0)';
            
            setTimeout(() => {
                element.style.transition = '';
            }, 400);
        }, index * 50);
    });
}

/**
 * Initialise les indicateurs de status
 */
function initStatusIndicators() {
    const statusDots = document.querySelectorAll('.animate-pulse');
    statusDots.forEach(dot => {
        // Animation de pulsation personnalisée
        setInterval(() => {
            dot.style.transform = 'scale(1.2)';
            setTimeout(() => {
                dot.style.transform = 'scale(1)';
            }, 200);
        }, 2000);
    });
}

/**
 * Preview subtil d'un onglet (effet de parallaxe léger)
 */
function previewTab(tabName) {
    // Implémentation future pour un aperçu subtil
}

/**
 * Annule le preview d'onglet
 */
function clearTabPreview() {
    // Implémentation future
}

/**
 * Fonction de debouncing pour optimiser les performances
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Gestion du redimensionnement avec optimisations
 */
function handleWindowResize() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebarOverlay');
    const mainContent = document.querySelector('.main-content-area');
    
    if (!sidebar) return;
    
    const isMobile = window.innerWidth < 1024;
    const wasVisible = !sidebar.classList.contains('-translate-x-full');
    
    if (isMobile) {
        // Passage en mode mobile
        if (wasVisible) {
            sidebar.classList.add('-translate-x-full');
            if (overlay) overlay.classList.remove('show');
        }
        if (mainContent) mainContent.style.marginLeft = '0';
    } else {
        // Passage en mode desktop
        if (overlay) overlay.classList.remove('show');
        const savedState = localStorage.getItem('sidebarVisible');
        const shouldShow = savedState === null ? true : savedState === 'true';
        
        if (shouldShow) {
            sidebar.classList.remove('-translate-x-full');
            if (mainContent) mainContent.style.marginLeft = '20rem';
        } else {
            sidebar.classList.add('-translate-x-full');
            if (mainContent) mainContent.style.marginLeft = '0';
        }
    }
}

/**
 * Initialise les actions de confirmation
 */
function initConfirmActions() {
    // Gestionnaires pour les boutons de suppression
    const deleteButtons = document.querySelectorAll('[data-confirm]');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            const confirmMessage = this.getAttribute('data-confirm');
            if (confirmMessage && !confirm(confirmMessage)) {
                e.preventDefault();
                return false;
            }
        });
    });
    
    // Gestionnaires pour les formulaires avec confirmation
    const confirmForms = document.querySelectorAll('form[data-confirm]');
    confirmForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const confirmMessage = this.getAttribute('data-confirm');
            if (confirmMessage && !confirm(confirmMessage)) {
                e.preventDefault();
                return false;
            }
        });
    });
}

function initModernSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebarOverlay');
    const mainContent = document.querySelector('.main-content-area');
    
    if (!sidebar) return;
    
    const savedState = localStorage.getItem('sidebarVisible');
    const isMobile = window.innerWidth < 1024;
    const shouldShow = savedState === null ? !isMobile : savedState === 'true';
    
    // Configuration initiale basée sur la taille d'écran
    if (isMobile) {
        // Mobile : toujours masqué par défaut
        sidebar.classList.add('-translate-x-full');
        if (overlay) overlay.classList.remove('show');
    } else {
        // Desktop : état basé sur les préférences
        if (shouldShow) {
            sidebar.classList.remove('-translate-x-full');
            if (mainContent) mainContent.style.marginLeft = '20rem';
        } else {
            sidebar.classList.add('-translate-x-full');
            if (mainContent) mainContent.style.marginLeft = '0';
        }
    }
    
    // Gestionnaire pour l'overlay mobile
    if (overlay) {
        overlay.addEventListener('click', toggleSidebar);
    }
} 