/**
 * Script principal pour l'application EducInfo
 * Ce fichier contient les fonctionnalités JavaScript communes à toute l'application
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialisation du mode sombre
    initDarkMode();
    
    // Initialisation de la gestion des messages flash
    initFlashMessages();
    
    // Initialisation du formatage de la date et heure
    initDateTime();

    // Initialisation de la barre d'état
    initStatusBar();
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
    let lastMinute = -1; // Pour suivre si la minute a changé
    
    // Mettre à jour l'heure avec animation
    const updateClock = () => {
        const timeElement = document.getElementById('time');
        if (timeElement) {
            const now = new Date();
            const hours = now.getHours().toString().padStart(2, '0');
            const minutes = now.getMinutes().toString().padStart(2, '0');
            const seconds = now.getSeconds().toString().padStart(2, '0');
            
            // Mettre à jour l'heure avec les secondes
            timeElement.textContent = `${hours}:${minutes}:${seconds}`;
            
            // Ajouter une animation lorsque la minute change
            if (lastMinute !== -1 && lastMinute !== now.getMinutes()) {
                timeElement.classList.add('pulse-animation');
                setTimeout(() => {
                    timeElement.classList.remove('pulse-animation');
                }, 1000);
            }
            
            // Mettre à jour la dernière minute
            lastMinute = now.getMinutes();
        }
    };
    
    // Mettre à jour la date
    const updateDate = () => {
        const dateElement = document.getElementById('date');
        if (dateElement) {
            const now = new Date();
            const options = { weekday: 'long', day: 'numeric', month: 'long' };
            const dateStr = now.toLocaleDateString('fr-FR', options);
            dateElement.textContent = dateStr.charAt(0).toUpperCase() + dateStr.slice(1);
        }
    };
    
    // Mettre à jour immédiatement
    updateClock();
    updateDate();
    
    // Mettre à jour toutes les secondes pour être plus précis
    setInterval(updateClock, 1000);
    
    // Mettre à jour la date une fois par jour à minuit
    const midnight = new Date();
    midnight.setHours(24, 0, 0, 0);
    const timeUntilMidnight = midnight - new Date();
    
    setTimeout(() => {
        updateDate();
        // Ensuite, mettre à jour quotidiennement
        setInterval(updateDate, 86400000);
    }, timeUntilMidnight);
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