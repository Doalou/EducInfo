/**
 * Script principal pour l'application EducInfo
 * Ce fichier contient les fonctionnalités JavaScript communes à toute l'application
 */

// Utilitaires de performance
const Utils = {
    // Debounce function pour limiter la fréquence d'exécution
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func.apply(this, args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },
    
    // Throttle function pour limiter l'exécution
    throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        }
    },
    
    // Cache local simple avec expiration
    cache: new Map(),
    setCache(key, value, ttl = 300000) { // TTL par défaut: 5 minutes
        const expiryTime = Date.now() + ttl;
        this.cache.set(key, { value, expiryTime });
    },
    getCache(key) {
        const cached = this.cache.get(key);
        if (cached && Date.now() < cached.expiryTime) {
            return cached.value;
        }
        this.cache.delete(key);
        return null;
    },
    clearExpiredCache() {
        const now = Date.now();
        for (const [key, value] of this.cache.entries()) {
            if (now >= value.expiryTime) {
                this.cache.delete(key);
            }
        }
    }
};

// Gestionnaire principal optimisé
document.addEventListener('DOMContentLoaded', function() {
    // Initialisation avec gestion d'erreurs
    try {
        initDarkMode();
        initDateTime();
        initStatusBar();
        initFlashMessages();
        
        // Nettoyage du cache expiré toutes les 5 minutes
        setInterval(() => Utils.clearExpiredCache(), 300000);
        
    } catch (error) {
        console.error('Erreur lors de l\'initialisation:', error);
    }
});

/**
 * Initialise le mode sombre en fonction des préférences utilisateur
 */
function initDarkMode() {
    // Récupérer la préférence utilisateur depuis le localStorage
    const isDarkMode = localStorage.getItem('darkMode') === 'true';
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    // Appliquer le mode sombre si préféré ou sauvegardé
    if (isDarkMode || (prefersDark && localStorage.getItem('darkMode') === null)) {
        document.documentElement.classList.add('dark');
        updateDarkModeToggleIcons(true);
    } else {
        document.documentElement.classList.remove('dark');
        updateDarkModeToggleIcons(false);
    }
    
    // Ajouter l'écouteur d'événement pour le bouton de bascule
    const darkModeToggle = document.getElementById('darkmode-toggle');
    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', toggleDarkMode);
        
        // Ajouter une animation sur hover
        darkModeToggle.addEventListener('mouseenter', function() {
            this.classList.add('scale-110');
            setTimeout(() => this.classList.remove('scale-110'), 300);
        });
    }
    
    // Écouter les changements de préférence du système
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
        const newColorScheme = e.matches ? "dark" : "light";
        if (localStorage.getItem('darkMode') === null) {
            // Seulement changer si l'utilisateur n'a pas explicitement choisi
            if (newColorScheme === 'dark') {
                document.documentElement.classList.add('dark');
                updateDarkModeToggleIcons(true);
            } else {
                document.documentElement.classList.remove('dark');
                updateDarkModeToggleIcons(false);
            }
        }
    });
}

/**
 * Bascule entre le mode clair et le mode sombre
 */
function toggleDarkMode() {
    const isDarkMode = document.documentElement.classList.toggle('dark');
    localStorage.setItem('darkMode', isDarkMode ? 'true' : 'false');
    updateDarkModeToggleIcons(isDarkMode);
    
    // Ajouter une animation au changement
    this.classList.add('animate-spin');
    setTimeout(() => this.classList.remove('animate-spin'), 500);
    
    // Mettre à jour les styles qui peuvent nécessiter un recalcul
    document.querySelectorAll('.card-hover').forEach(card => {
        card.style.transition = 'none';
        card.offsetHeight; // Force reflow
        card.style.transition = '';
    });
}

/**
 * Met à jour les icônes du bouton de bascule du mode sombre
 * @param {boolean} isDarkMode - Indique si le mode sombre est activé
 */
function updateDarkModeToggleIcons(isDarkMode) {
    const sunIcon = document.getElementById('sun-icon');
    const moonIcon = document.getElementById('moon-icon');
    
    if (sunIcon && moonIcon) {
        if (isDarkMode) {
            sunIcon.classList.remove('hidden');
            moonIcon.classList.add('hidden');
        } else {
            sunIcon.classList.add('hidden');
            moonIcon.classList.remove('hidden');
        }
    }
}

/**
 * Initialise la gestion des messages flash avec suppression automatique
 */
function initFlashMessages() {
    const flashMessages = document.querySelectorAll('.flash-message');
    
    flashMessages.forEach(message => {
        // Ajouter la classe d'animation d'entrée
        message.classList.add('flash-message-enter');
        
        // Configurer la suppression automatique après un délai
        setTimeout(() => {
            message.classList.add('flash-message-leave');
            setTimeout(() => {
                message.remove();
            }, 300); // Durée de l'animation de sortie
        }, 5000); // Durée d'affichage
        
        // Ajouter un écouteur pour le bouton de fermeture
        const closeButton = message.querySelector('button');
        if (closeButton) {
            closeButton.addEventListener('click', () => {
                message.classList.add('flash-message-leave');
                setTimeout(() => {
                    message.remove();
                }, 300);
            });
        }
    });
}

/**
 * Initialise le formatage de la date et de l'heure
 */
function initDateTime() {
    // Horloge temps réel optimisée avec throttling
    const updateClock = Utils.throttle(() => {
        const now = new Date();
        const timeElement = document.getElementById('time');
        const dateElement = document.getElementById('date');
        
        if (timeElement) {
            timeElement.textContent = now.toLocaleTimeString('fr-FR', {
                hour: '2-digit',
                minute: '2-digit',
                hour12: false
            });
        }
        
        if (dateElement) {
            // Optimisation : ne mettre à jour la date qu'une fois par minute
            const cached = Utils.getCache('current_date');
            let formattedDate = cached;
            
            if (!formattedDate) {
                formattedDate = now.toLocaleDateString('fr-FR', {
                    day: '2-digit',
                    month: '2-digit',
                    year: 'numeric'
                });
                Utils.setCache('current_date', formattedDate, 60000); // Cache 1 minute
            }
            
            dateElement.textContent = formattedDate;
        }
    }, 1000); // Throttle à 1 seconde
    
    // Exécution immédiate puis intervalle
    updateClock();
    setInterval(updateClock, 1000);
}

/**
 * Initialise les fonctionnalités supplémentaires de la barre d'état
 */
function initStatusBar() {
    // S'assurer que la barre d'état est toujours visible
    const statusBar = document.querySelector('.status-bar');
    if (statusBar) {
        // Ajouter un effet d'apparition au chargement de la page
        statusBar.style.opacity = '0';
        statusBar.style.transform = 'translateY(10px)';
        
        setTimeout(() => {
            statusBar.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            statusBar.style.opacity = '1';
            statusBar.style.transform = 'translateY(0)';
        }, 300);
        
        // S'assurer que le padding-bottom du main est correct
        const mainElement = document.querySelector('main');
        if (mainElement) {
            const statusBarHeight = statusBar.offsetHeight;
            mainElement.style.paddingBottom = `${statusBarHeight + 16}px`; // 16px pour l'espace supplémentaire
        }
        
        // Ajuster le padding si la fenêtre est redimensionnée
        window.addEventListener('resize', () => {
            if (mainElement) {
                const statusBarHeight = statusBar.offsetHeight;
                mainElement.style.paddingBottom = `${statusBarHeight + 16}px`;
            }
        });
    }
}

/**
 * Fonction pour supprimer un message flash
 * @param {HTMLElement} element - L'élément à supprimer
 */
function removeFlashMessage(element) {
    element.classList.add('flash-message-leave');
    setTimeout(() => {
        element.remove();
    }, 300);
} 