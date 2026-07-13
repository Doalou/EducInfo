/**
 * EducInfo - Logique de la barre de statut et initialisation globale.
 * Gere l'horloge, la meteo, le theme, le plein ecran et les messages flash.
 */
(function () {
    'use strict';

    // Lire la configuration depuis les data-attributes du body
    var body = document.body;
    var apiWeather = body.dataset.apiWeather || '';
    var apiUpdates = body.dataset.apiUpdates || '';
    var apiTransports = body.dataset.apiTransports || '';
    var weatherEnabled = body.dataset.weatherEnabled === 'true';

    window.EducInfo = {
        config: {
            updateIntervals: { clock: 1000, weather: 600000, data: 30000 },
            api: { weather: apiWeather, updates: apiUpdates, transports: apiTransports },
            theme: localStorage.getItem('theme') || 'auto'
        },
        utils: {
            debounce: function (func, wait) {
                var timeout;
                return function () {
                    var args = arguments;
                    var context = this;
                    clearTimeout(timeout);
                    timeout = setTimeout(function () { func.apply(context, args); }, wait);
                };
            },
            formatTime: function (date) {
                return date.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
            },
            formatDate: function (date) {
                return date.toLocaleDateString('fr-FR', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
            }
        }
    };

    window.addEventListener('error', function (e) {
        console.warn('Erreur JavaScript:', e.error);
    });

    document.addEventListener('DOMContentLoaded', function () {
        initializeTheme();
        initializeClock();
        if (weatherEnabled) initializeWeather();
        initializeFullscreen();
        initializeRefreshButton();
        initializeFlashMessages();
    });

    function initializeTheme() {
        var themeToggle = document.getElementById('theme-toggle');
        var html = document.documentElement;

        if (window.EducInfo.config.theme === 'dark' ||
            (window.EducInfo.config.theme === 'auto' && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
            html.classList.add('dark');
            if (themeToggle) themeToggle.setAttribute('aria-pressed', 'true');
        }

        if (themeToggle) {
            themeToggle.addEventListener('click', function () {
                var isDark = html.classList.contains('dark');
                if (isDark) {
                    html.classList.remove('dark');
                    localStorage.setItem('theme', 'light');
                    this.setAttribute('aria-pressed', 'false');
                } else {
                    html.classList.add('dark');
                    localStorage.setItem('theme', 'dark');
                    this.setAttribute('aria-pressed', 'true');
                }
                this.setAttribute('aria-label', isDark ? 'Theme clair active' : 'Theme sombre active');
            });
        }

        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function (e) {
            if (localStorage.getItem('theme') === 'auto') {
                html.classList.toggle('dark', e.matches);
            }
        });
    }

    function initializeRefreshButton() {
        var btn = document.getElementById('refresh-page');
        if (!btn) return;
        btn.addEventListener('click', function () {
            this.style.transform = 'rotate(360deg)';
            this.style.transition = 'transform 0.5s ease-in-out';
            setTimeout(function () { window.location.reload(); }, 500);
        });
    }

    function initializeClock() {
        function updateClock() {
            var now = new Date();
            var timeEl = document.getElementById('current-time');
            var dateEl = document.getElementById('current-date');
            if (timeEl) timeEl.textContent = window.EducInfo.utils.formatTime(now);
            if (dateEl) dateEl.textContent = window.EducInfo.utils.formatDate(now);
        }
        updateClock();
        setInterval(updateClock, window.EducInfo.config.updateIntervals.clock);
    }

    function initializeWeather() {
        function updateWeather() {
            fetch(window.EducInfo.config.api.weather)
                .then(function (r) { return r.json(); })
                .then(function (data) {
                    if (data.error) return;
                    var el = function (id) { return document.getElementById(id); };
                    if (el('weather-icon') && data.emoji) el('weather-icon').textContent = data.emoji;
                    if (el('weather-temp') && data.temperature) el('weather-temp').textContent = data.temperature + '\u00B0C';
                    if (el('weather-desc') && data.description) el('weather-desc').textContent = data.description;
                    if (el('weather-feels') && data.feels_like) el('weather-feels').textContent = data.feels_like + '\u00B0C';
                    if (el('weather-humidity') && data.humidity) el('weather-humidity').textContent = data.humidity + '%';
                    if (el('weather-aqi') && data.aqi) {
                        el('weather-aqi').textContent = data.aqi.label;
                        el('weather-aqi').style.color = data.aqi.color;
                    }
                })
                .catch(function () {
                    var temp = document.getElementById('weather-temp');
                    var desc = document.getElementById('weather-desc');
                    if (temp) temp.textContent = '--\u00B0C';
                    if (desc) desc.textContent = 'Non disponible';
                });
        }
        updateWeather();
        setInterval(updateWeather, window.EducInfo.config.updateIntervals.weather);
    }

    function initializeFullscreen() {
        var btn = document.getElementById('fullscreen-toggle');
        if (!btn) return;
        btn.addEventListener('click', function () {
            var self = this;
            if (!document.fullscreenElement) {
                document.documentElement.requestFullscreen().then(function () {
                    self.setAttribute('aria-pressed', 'true');
                }).catch(function () {});
            } else {
                document.exitFullscreen().then(function () {
                    self.setAttribute('aria-pressed', 'false');
                });
            }
        });
        document.addEventListener('fullscreenchange', function () {
            btn.setAttribute('aria-pressed', (!!document.fullscreenElement).toString());
        });
    }

    function initializeFlashMessages() {
        document.querySelectorAll('.flash-message').forEach(function (msg) {
            if (msg.dataset.severity !== 'error') {
                setTimeout(function () {
                    msg.style.animation = 'slideOut 0.3s ease-in forwards';
                    setTimeout(function () { msg.remove(); }, 300);
                }, 5000);
            }
        });
    }

    document.addEventListener('keydown', function (e) {
        if (e.key === 'F11') {
            e.preventDefault();
            var btn = document.getElementById('fullscreen-toggle');
            if (btn) btn.click();
        }
    });
})();
