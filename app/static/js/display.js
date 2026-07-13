"use strict";

const shell = document.querySelector("[data-display-endpoint]");
const endpoint = shell.dataset.displayEndpoint;
const el = (id) => document.getElementById(id);
const DAYS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi"];
const STATUS_LABELS = {
  fresh: "Actualisé",
  stale: "Donnée précédente",
  unavailable: "Indisponible",
  disabled: "Masqué",
  demo: "Démonstration",
};
const REFRESH_INTERVAL = 60_000;
let refreshTimer;

function node(tag, className, text) {
  const item = document.createElement(tag);
  if (className) item.className = className;
  if (text !== undefined) item.textContent = text;
  return item;
}

function lineBadge(item) {
  const namespace = "http://www.w3.org/2000/svg";
  const badge = document.createElementNS(namespace, "svg");
  badge.setAttribute("class", "line-pill");
  badge.setAttribute("viewBox", "0 0 48 34");
  badge.setAttribute("role", "img");
  badge.setAttribute("aria-label", `Ligne ${item.line}`);
  const validColor = (value, fallback) => /^#[0-9A-F]{6}$/i.test(value || "") ? value : fallback;
  const background = document.createElementNS(namespace, "rect");
  background.setAttribute("width", "48");
  background.setAttribute("height", "34");
  background.setAttribute("fill", validColor(item.line_color, "#1646D8"));
  const label = document.createElementNS(namespace, "text");
  label.setAttribute("x", "24");
  label.setAttribute("y", "22");
  label.setAttribute("text-anchor", "middle");
  label.setAttribute("fill", validColor(item.line_text_color, "#FFFFFF"));
  label.textContent = item.line;
  badge.append(background, label);
  return badge;
}

function replace(id, children) {
  const target = el(id);
  target.classList.remove("skeleton");
  target.replaceChildren(...children);
}

function empty(message) { return [node("p", "empty", message)]; }

function renderAbsences(data) {
  replace("absences", DAYS.map((day) => {
    const card = node("div", "day-card");
    card.append(node("strong", "", day), node("span", "day-count", `${data[day].length}`));
    const list = node("div", "teacher-list");
    (data[day].length ? data[day] : [{teacher: "Tous présents"}]).forEach((item) => list.append(node("span", data[day].length ? "" : "ok", item.teacher)));
    card.append(list);
    return card;
  }));
}

function renderWeather(source) {
  el("weather-freshness").textContent = STATUS_LABELS[source.status] || source.status;
  if (!source.data) return replace("weather", empty("Météo indisponible"));
  const box = node("div", "weather-now");
  box.append(node("span", "weather-icon", source.data.icon), node("strong", "weather-temp", `${source.data.temperature}°`));
  box.append(node("p", "", source.data.description), node("small", "", `${source.data.city} · Humidité ${source.data.humidity}%`));
  replace("weather", [box]);
}

function renderMenu(items) {
  el("menu-count").textContent = `${items.length} élément${items.length > 1 ? "s" : ""}`;
  replace("menu", items.length ? items.map((item) => {
    const row = node("div", "list-row");
    const content = node("div", "row-content");
    content.append(node("strong", "", item.name), node("small", "", item.description || item.category_label));
    row.append(node("span", "list-icon", item.category_icon), content);
    return row;
  }) : empty("Aucun menu aujourd’hui"));
}

function renderTransport(source) {
  el("transport-freshness").textContent = STATUS_LABELS[source.status] || source.status;
  const arrivals = source.data?.arrivals || [];
  replace("transport", arrivals.length ? arrivals.map((item) => {
    const row = node("div", "transport-row");
    row.append(lineBadge(item), node("span", "destination", item.destination), node("strong", "minutes", item.minutes === 0 ? "Maintenant" : `${item.minutes} min`));
    return row;
  }) : empty(source.status === "disabled" ? "Widget désactivé" : "Aucun passage disponible"));
}

function renderEvents(items) {
  replace("events", items.length ? items.map((item) => {
    const row = node("div", "list-row event-row");
    const date = new Date(`${item.date}T12:00:00`);
    const content = node("div", "row-content");
    content.append(node("strong", "", item.title));
    if (item.description) content.append(node("small", "", item.description));
    row.append(node("time", "event-date", date.toLocaleDateString("fr-FR", {day:"2-digit", month:"short"})), content);
    return row;
  }) : empty("Aucun événement à venir"));
}

async function refresh() {
  clearTimeout(refreshTimer);
  try {
    const response = await fetch(endpoint, {
      cache: "no-store",
      headers: {Accept: "application/json"},
      signal: AbortSignal.timeout(10000),
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();
    shell.classList.toggle("theme-dark", data.site.theme === "dark");
    el("site-name").textContent = data.site.name;
    renderAbsences(data.absences); renderWeather(data.weather); renderMenu(data.menu); renderTransport(data.transport); renderEvents(data.events);
    el("last-update").textContent = `Actualisé à ${new Date(data.generated_at).toLocaleTimeString("fr-FR", {hour:"2-digit", minute:"2-digit"})}`;
  } catch (error) {
    // Les modules conservent leur dernière valeur lisible jusqu'au prochain essai.
  } finally {
    refreshTimer = setTimeout(refresh, REFRESH_INTERVAL);
  }
}

function tick() {
  const now = new Date();
  el("clock-time").textContent = now.toLocaleTimeString("fr-FR", {hour:"2-digit", minute:"2-digit"});
  el("clock-date").textContent = now.toLocaleDateString("fr-FR", {weekday:"long", day:"numeric", month:"long"});
}

tick(); refresh(); setInterval(tick, 1000);

document.addEventListener("visibilitychange", () => {
  if (document.visibilityState === "visible") refresh();
});

el("fullscreen").addEventListener("click", async () => {
  if (document.fullscreenElement) await document.exitFullscreen();
  else await document.documentElement.requestFullscreen();
});
