/**
 * Gestionnaire du Mode TV pour EducInfo
 * Optimisé pour l'affichage sur écrans larges avec mise à jour temps réel intelligente
 */

class TVModeManager {
    constructor() {
        this.isActive = false;
        this.clockInterval = null;
        this.refreshInterval = null;
        this.refreshIndicatorTimeout = null;
        this.isFullscreen = false;
        this.refreshInProgress = false;
        this.errorCount = 0;
        this.maxErrors = 3;
        this.refreshCounter = 0;
        
        // Configuration optimisée pour l'affichage temps réel
        this.config = {
            refreshIntervals: {
                weather: 30000,      // 30 secondes (données moins critiques)
                transport: 15000,    // 15 secondes (données temps réel critiques)
                default: 30000       // 30 secondes par défaut
            },
            clockUpdateInterval: 1000,   // 1 seconde pour l'horloge
            errorRetryDelay: 5000,      // 5 secondes avant retry
            maxConsecutiveErrors: 3      // Nombre max d'erreurs consécutives
        };
    }

    init() {
        console.log('🖥️ Mode TV initialisé');
        this.isActive = true;
        this.errorCount = 0;
        
        // Initialisation de l'interface
        this.startClock();
        this.setupEventListeners();
        this.startAutoRefresh();
        this.updateDateTime();
        
        // Optimisations pour l'affichage TV
        this.optimizeForTV();
        
        // Gestion de la visibilité pour économiser les ressources
        this.setupVisibilityChange();
        
        // Affichage du statut initial
        this.showSystemStatus('Mode TV activé • Affichage optimisé pour écrans larges');
    }

    startClock() {
        this.updateClock();
        this.clockInterval = setInterval(() => this.updateClock(), this.config.clockUpdateInterval);
    }

    updateClock() {
        try {
            const now = new Date();
            const options = {
                timeZone: 'Europe/Paris',
                hour12: false
            };
            
            // Mise à jour de l'horloge principal
            const timeElement = document.querySelector('.tv-time');
            if (timeElement) {
                timeElement.textContent = now.toLocaleTimeString('fr-FR', {
                    ...options,
                    hour: '2-digit',
                    minute: '2-digit',
                    second: '2-digit'
                });
            }
            
            // Mise à jour de la date
            const dateElement = document.querySelector('.tv-date');
            if (dateElement) {
                dateElement.textContent = now.toLocaleDateString('fr-FR', {
                    ...options,
                    weekday: 'long',
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                });
            }
            
            // Effet de clignotement pour les secondes (toutes les 1s)
            const timeDisplay = document.querySelector('.tv-time');
            if (timeDisplay && now.getSeconds() % 2 === 0) {
                timeDisplay.style.opacity = '0.9';
                setTimeout(() => {
                    if (timeDisplay) timeDisplay.style.opacity = '1';
                }, 100);
            }
            
        } catch (error) {
            console.warn('Erreur mise à jour horloge TV:', error);
        }
    }

    startAutoRefresh() {
        // Mise à jour initiale des données
        this.refreshData();
        
        // Intervalles différenciés selon le type de données
        this.refreshInterval = setInterval(() => {
            this.refreshData();
        }, this.config.refreshIntervals.default);
        
        // Intervalle spécialisé pour les transports (plus fréquent)
        this.transportRefreshInterval = setInterval(() => {
            this.refreshTransportData();
        }, this.config.refreshIntervals.transport);
    }

    async refreshData() {
        if (this.refreshInProgress) {
            console.log('⏳ Refresh déjà en cours, skip');
            return;
        }
        
        this.refreshInProgress = true;
        this.refreshCounter++;
        
        try {
            console.log(`🔄 Refresh données TV #${this.refreshCounter}`);
            this.showRefreshIndicator();
            
            // Refresh parallèle des différents widgets
            const refreshPromises = [];
            
            // Météo (moins fréquent)
            if (this.refreshCounter % 2 === 0) { // Toutes les 2 fois
                refreshPromises.push(this.refreshWeatherData());
            }
            
            // Données statiques (moins fréquentes)
            if (this.refreshCounter % 4 === 0) { // Toutes les 4 fois
                refreshPromises.push(this.refreshStaticData());
            }
            
            await Promise.allSettled(refreshPromises);
            this.errorCount = 0; // Reset du compteur d'erreurs
            
        } catch (error) {
            console.error('Erreur lors du refresh TV:', error);
            this.handleRefreshError(error);
        } finally {
            this.refreshInProgress = false;
            this.hideRefreshIndicator();
        }
    }

    async refreshWeatherData() {
        try {
            const response = await fetch('/get_weather', {
                method: 'GET',
                headers: {
                    'Cache-Control': 'no-cache',
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            const data = await response.json();
            this.updateWeatherDisplay(data);
            
        } catch (error) {
            console.warn('Erreur refresh météo:', error);
            this.showErrorInWidget('weather', 'Erreur météo');
        }
    }

    async refreshTransportData() {
        try {
            const response = await fetch('/get_transports', {
                method: 'GET',
                headers: {
                    'Cache-Control': 'no-cache',
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            const data = await response.json();
            this.updateTransportDisplay(data);
            
        } catch (error) {
            console.warn('Erreur refresh transport:', error);
            this.showErrorInWidget('transport', 'Erreur transport');
        }
    }

    async refreshStaticData() {
        try {
            const response = await fetch('/get_updates', {
                method: 'GET',
                headers: {
                    'Cache-Control': 'no-cache',
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            const data = await response.json();
            this.updateStaticWidgets(data);
            
        } catch (error) {
            console.warn('Erreur refresh données statiques:', error);
        }
    }

    updateWeatherDisplay(data) {
        const weatherContainer = document.querySelector('.tv-weather');
        if (!weatherContainer) return;
        
        if (data.success) {
            weatherContainer.innerHTML = `
                <div class="flex items-center space-x-3">
                    <span class="text-4xl">${data.emoji}</span>
                    <div>
                        <div class="text-2xl font-bold">${data.display_text}</div>
                        <div class="text-lg text-gray-600 dark:text-gray-300">${data.display_details}</div>
                    </div>
                </div>
            `;
            weatherContainer.classList.remove('error');
        } else {
            this.showErrorInWidget('weather', data.error || 'Données météo indisponibles');
        }
    }

    updateTransportDisplay(data) {
        const transportContainer = document.querySelector('.tv-transport-list');
        if (!transportContainer) return;
        
        if (data.success && data.arrivals && data.arrivals.length > 0) {
            const arrivalsHtml = data.arrivals.slice(0, 6).map(arrival => `
                <div class="tv-transport-item flex items-center justify-between p-4 rounded-lg ${arrival.time_left_class}">
                    <div class="tv-transport-info flex items-center space-x-4">
                        <span class="text-2xl">${arrival.transport_icon}</span>
                        <div>
                            <div class="tv-transport-line font-bold text-xl">${arrival.line_name}</div>
                            <div class="tv-transport-destination text-lg">${arrival.destination_display}</div>
                        </div>
                    </div>
                    <div class="tv-transport-time text-right">
                        <div class="text-2xl font-bold ${arrival.time_left_class}">${arrival.time_left_text}</div>
                        <div class="text-sm opacity-75">${arrival.realtime_indicator}</div>
                    </div>
                </div>
            `).join('');
            
            transportContainer.innerHTML = arrivalsHtml;
            transportContainer.classList.remove('error');
        } else {
            const errorMsg = data.error || 'Aucun passage prévu';
            transportContainer.innerHTML = `
                <div class="tv-empty-state text-center py-8">
                    <div class="tv-empty-icon text-6xl mb-4">🚌</div>
                    <div class="text-xl">${errorMsg}</div>
                </div>
            `;
        }
    }

    updateStaticWidgets(data) {
        // Mise à jour des absences
        if (data.absences) {
            this.updateAbsencesDisplay(data.absences);
        }
        
        // Mise à jour des événements
        if (data.events) {
            this.updateEventsDisplay(data.events);
        }
        
        // Mise à jour du menu
        if (data.menu) {
            this.updateMenuDisplay(data.menu);
        }
    }

    updateAbsencesDisplay(absences) {
        const absencesContainer = document.querySelector('.absences-grid');
        if (!absencesContainer) return;
        
        const jours = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi'];
        const joursHtml = jours.map(jour => {
            const absencesJour = absences.filter(abs => abs[jour]);
            return `
                <div class="day-column">
                    <div class="day-name">${jour.charAt(0).toUpperCase() + jour.slice(1)}</div>
                    <div class="absence-list">
                        ${absencesJour.length > 0 
                            ? absencesJour.map(abs => `<div class="teacher-absent">${abs.professeur}</div>`).join('')
                            : '<div class="no-absence"><span style="font-size: 2.5rem;">✅</span><span>Tous présents</span></div>'
                        }
                    </div>
                </div>
            `;
        }).join('');
        
        absencesContainer.innerHTML = joursHtml;
    }

    updateEventsDisplay(events) {
        const eventsContainer = document.querySelector('.events-list');
        if (!eventsContainer) return;
        
        if (events.length > 0) {
            const eventsHtml = events.slice(0, 5).map(event => `
                <div class="event-item">
                    <div class="event-title">${event.title}</div>
                    <div class="event-date">📅 ${event.date_formatted || event.date}</div>
                    ${event.description ? `<div class="event-description">${event.description}</div>` : ''}
                </div>
            `).join('');
            eventsContainer.innerHTML = eventsHtml;
        } else {
            eventsContainer.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">📅</div>
                    <div class="empty-message">Aucun événement prévu</div>
                </div>
            `;
        }
    }

    updateMenuDisplay(menu) {
        const menuContainer = document.querySelector('.menu-categories');
        if (!menuContainer) return;
        
        const categories = {
            1: { name: 'Entrée', icon: '🥗' },
            2: { name: 'Plat principal', icon: '🍖' },
            3: { name: 'Fromage', icon: '🧀' },
            4: { name: 'Dessert', icon: '🍦' }
        };
        
        if (menu.length > 0) {
            const categoriesHtml = Object.entries(categories).map(([catId, cat]) => {
                const items = menu.filter(item => item.category == catId);
                if (items.length === 0) return '';
                return `
                    <div class="menu-category">
                        <div class="category-name">${cat.icon} ${cat.name}</div>
                        ${items.map(item => `
                            <div class="menu-item">
                                ${item.icons || ''} ${item.name}
                            </div>
                          `).join('')
                        }
                    </div>
                `;
            }).join('');
            
            menuContainer.innerHTML = categoriesHtml || `
                <div class="empty-state">
                    <div class="empty-icon">🍴</div>
                    <div class="empty-message">Menu non disponible aujourd'hui</div>
                </div>
            `;
        } else {
            menuContainer.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">🍴</div>
                    <div class="empty-message">Menu non disponible aujourd'hui</div>
                </div>
            `;
        }
    }

    showRefreshIndicator() {
        const indicator = document.querySelector('.refresh-indicator');
        if (indicator) {
            indicator.style.display = 'block';
            indicator.classList.add('animate-spin');
        }
        
        // Auto-hide après 3 secondes max
        this.refreshIndicatorTimeout = setTimeout(() => {
            this.hideRefreshIndicator();
        }, 3000);
    }

    hideRefreshIndicator() {
        const indicator = document.querySelector('.refresh-indicator');
        if (indicator) {
            indicator.style.display = 'none';
            indicator.classList.remove('animate-spin');
        }
        
        if (this.refreshIndicatorTimeout) {
            clearTimeout(this.refreshIndicatorTimeout);
            this.refreshIndicatorTimeout = null;
        }
    }

    showErrorInWidget(widgetType, message) {
        const widget = document.querySelector(`.tv-${widgetType}`);
        if (widget) {
            widget.innerHTML = `
                <div class="error-state text-center py-4">
                    <div class="text-red-500 text-lg">❌ ${message}</div>
                </div>
            `;
            widget.classList.add('error');
        }
    }

    handleRefreshError(error) {
        this.errorCount++;
        console.error(`Erreur refresh #${this.errorCount}:`, error);
        
        if (this.errorCount >= this.maxErrors) {
            this.showSystemStatus('Problème de connexion • Vérifiez votre réseau', 'error');
            
            // Attendre avant de réessayer
            setTimeout(() => {
                this.errorCount = Math.max(0, this.errorCount - 1);
            }, this.config.errorRetryDelay);
        }
    }

    showSystemStatus(message, type = 'info') {
        const statusBar = document.querySelector('.tv-status-bar .tv-system-status');
        if (statusBar) {
            const icon = type === 'error' ? '⚠️' : 'ℹ️';
            statusBar.innerHTML = `${icon} ${message}`;
            statusBar.className = `tv-system-status ${type}`;
            
            // Auto-hide après 5 secondes pour les messages d'info
            if (type === 'info') {
                setTimeout(() => {
                    if (statusBar.textContent.includes(message)) {
                        statusBar.innerHTML = '';
                    }
                }, 5000);
            }
        }
    }

    optimizeForTV() {
        // Optimisations CSS pour l'affichage TV
        document.body.style.overflow = 'hidden';
        document.body.style.cursor = 'none';
        
        // Augmenter la taille des polices pour la lisibilité à distance
        const style = document.createElement('style');
        style.textContent = `
            .tv-mode {
                font-size: 1.1em;
                line-height: 1.4;
            }
            .tv-mode .tv-card {
                border-width: 2px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            }
            .tv-mode .tv-time {
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }
        `;
        document.head.appendChild(style);
        
        // Désactiver la sélection de texte
        document.addEventListener('selectstart', e => e.preventDefault());
    }

    setupEventListeners() {
        // Gestion des raccourcis clavier
        document.addEventListener('keydown', (e) => {
            switch(e.key) {
                case 'F11':
                    e.preventDefault();
                    this.toggleFullscreen();
                    break;
                case 'Escape':
                    if (this.isFullscreen) {
                        this.exitFullscreen();
                    }
                    break;
                case 'F5':
                    e.preventDefault();
                    this.forceRefresh();
                    break;
                case ' ': // Espace pour pause/play
                    e.preventDefault();
                    this.toggleAutoRefresh();
                    break;
            }
        });
        
        // Gestion du clic sur les boutons
        document.addEventListener('click', (e) => {
            if (e.target.matches('.tv-fullscreen-btn')) {
                this.toggleFullscreen();
            } else if (e.target.matches('.tv-refresh-btn')) {
                this.forceRefresh();
            }
        });
    }

    setupVisibilityChange() {
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.pauseUpdates();
            } else {
                this.resumeUpdates();
            }
        });
    }

    async toggleFullscreen() {
        try {
            if (!document.fullscreenElement) {
                await document.documentElement.requestFullscreen();
                this.isFullscreen = true;
            } else {
                await document.exitFullscreen();
                this.isFullscreen = false;
            }
            this.updateFullscreenUI();
        } catch (error) {
            console.warn('Erreur fullscreen:', error);
        }
    }

    async exitFullscreen() {
        try {
            if (document.fullscreenElement) {
                await document.exitFullscreen();
                this.isFullscreen = false;
                this.updateFullscreenUI();
            }
        } catch (error) {
            console.warn('Erreur sortie fullscreen:', error);
        }
    }

    updateFullscreenUI() {
        const btn = document.querySelector('.tv-fullscreen-btn');
        if (btn) {
            btn.innerHTML = this.isFullscreen ? '🗗 Quitter plein écran' : '🗖 Plein écran';
            btn.title = this.isFullscreen ? 'Quitter le plein écran (Echap)' : 'Plein écran (F11)';
        }
    }

    forceRefresh() {
        console.log('🔄 Refresh forcé par l\'utilisateur');
        this.showSystemStatus('Mise à jour forcée des données...');
        this.refreshData();
    }

    toggleAutoRefresh() {
        if (this.refreshInterval) {
            this.pauseUpdates();
            this.showSystemStatus('Pause automatique activée', 'info');
        } else {
            this.resumeUpdates();
            this.showSystemStatus('Reprise des mises à jour', 'info');
        }
    }

    pauseUpdates() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
        if (this.transportRefreshInterval) {
            clearInterval(this.transportRefreshInterval);
            this.transportRefreshInterval = null;
        }
        console.log('⏸️ Mises à jour pausées');
    }

    resumeUpdates() {
        if (!this.refreshInterval && this.isActive) {
            this.startAutoRefresh();
            console.log('▶️ Mises à jour reprises');
        }
    }

    updateDateTime() {
        // Mise à jour immédiate de la date/heure
        this.updateClock();
    }

    cleanup() {
        console.log('🧹 Nettoyage du mode TV');
        
        this.isActive = false;
        
        // Arrêt des intervalles
        if (this.clockInterval) {
            clearInterval(this.clockInterval);
            this.clockInterval = null;
        }
        
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
        
        if (this.transportRefreshInterval) {
            clearInterval(this.transportRefreshInterval);
            this.transportRefreshInterval = null;
        }
        
        if (this.refreshIndicatorTimeout) {
            clearTimeout(this.refreshIndicatorTimeout);
            this.refreshIndicatorTimeout = null;
        }
        
        // Retour aux styles normaux
        document.body.style.overflow = '';
        document.body.style.cursor = '';
        
        // Sortir du plein écran si nécessaire
        if (this.isFullscreen) {
            this.exitFullscreen();
        }
    }
}

// Instance globale
let tvManager = null;

// Initialisation du mode TV
function initTVMode() {
    if (!tvManager) {
        tvManager = new TVModeManager();
    }
    tvManager.init();
}

// Nettoyage du mode TV
function cleanupTVMode() {
    if (tvManager) {
        tvManager.cleanup();
        tvManager = null;
    }
}

// Export pour utilisation globale
window.TVModeManager = TVModeManager;
window.initTVMode = initTVMode;
window.cleanupTVMode = cleanupTVMode; 