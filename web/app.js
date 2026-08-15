const app = document.querySelector("#app");
const toast = document.querySelector("#toast");
let state = null;
let selectedCharacter = "rimuru";
let busy = false;
let autoTimer = null;
let refreshTimer = null;
// currently selected enemy index (0-based) in multi-enemy encounters
let selectedEnemyIndex = null;
// animation frame id for a smooth action progress bar
let activityAnimId = null;

// Animate the progress bar smoothly based on activity.started_at and activity.ends_at
function animateActivityProgress() {
  // cancel previous animation if any
  if (activityAnimId) {
    cancelAnimationFrame(activityAnimId);
    activityAnimId = null;
  }
  if (!state || !state.activity) return;
  const span = document.querySelector('.meter.progress > span');
  if (!span) return;
  const startsAt = state.activity.started_at * 1000; // convert to ms
  const endsAt = state.activity.ends_at * 1000;
  const duration = Math.max(1, endsAt - startsAt);

  function frame() {
    const now = Date.now();
    const elapsed = Math.max(0, Math.min(duration, now - startsAt));
    const pct = Math.round((elapsed / duration) * 100);
    span.style.setProperty('--value', pct + '%');
    // continue until the endsAt has passed
    if (now < endsAt) {
      activityAnimId = requestAnimationFrame(frame);
    } else {
      // ensure final state reached
      span.style.setProperty('--value', '100%');
      activityAnimId = null;
    }
  }
  // start the animation loop
  activityAnimId = requestAnimationFrame(frame);
}


const escapeHtml = (value) =>
  String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");

const clampPercent = (value, maximum) =>
  Math.max(0, Math.min(100, maximum ? (value / maximum) * 100 : 0));

async function api(path, payload) {
  const options = payload === undefined
    ? { headers: { Accept: "application/json" } }
    : {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        body: JSON.stringify(payload),
      };
  const response = await fetch(path, options);
  const result = await response.json();
  if (!response.ok) throw new Error(result.error || "The chronicle resisted that action.");
  return result;
}

function showError(message) {
  toast.textContent = message;
  toast.classList.add("visible");
  window.clearTimeout(showError.timer);
  showError.timer = window.setTimeout(() => toast.classList.remove("visible"), 3200);
}

async function mutate(path, payload = {}) {
  if (busy) return;
  busy = true;
  try {
    state = await api(path, payload);
    render();
  } catch (error) {
    showError(error.message);
  } finally {
    busy = false;
  }
}

function render() {
  stopAutoIfNeeded();
  if (!state?.started) {
    document.body.classList.remove("route-rimuru", "route-diablo");
    renderLanding();
    return;
  }
  document.body.classList.toggle("route-diablo", state.character === "diablo");
  document.body.classList.toggle("route-rimuru", state.character === "rimuru");
  renderGame();
  if (state.pending_choice) renderChoice();
  // start or refresh the smooth activity progress animator so the bar moves continuously
  animateActivityProgress();
  // play any battle events received from the server (one-time playback)
  if (state?.battle?.events && state.battle.events.length) {
    playBattleEvents(state.battle.events);
    // mark events as played locally so they are not replayed on re-render
    state.battle._played = (state.battle._played || new Set());
    state.battle.events.forEach(e => state.battle._played.add(e.id));
    // clear events array in the in-memory state so future renders don't re-run animation
    state.battle.events = [];
  }
}

// keep a global set of played event ids to avoid double-playing after state refreshes
const _playedBattleEventIds = new Set();

function playBattleEvents(events) {
  if (!Array.isArray(events) || !events.length) return;
  events.forEach((evt, i) => {
    if (!evt || !evt.id || _playedBattleEventIds.has(evt.id)) return;
    // schedule each event with a slight delay for readable playback
    setTimeout(() => {
      _playedBattleEventIds.add(evt.id);
      switch (evt.type) {
        case 'skill':
          showDamagePopup(evt.target, '-' + evt.damage);
          break;
        case 'attack':
          // enemy attack shows damage on player (use profile orb)
          showDamagePopup(null, '-' + evt.damage, true);
          break;
        case 'defeat':
          showPopupText(evt.target, (evt.name || 'Enemy') + ' defeated');
          break;
        case 'recruit':
          showPopupText(null, 'Ally recruited: ' + evt.ally_id);
          break;
        case 'expedition_complete':
          showPopupText(null, 'Expedition complete — ' + evt.zone);
          break;
        case 'encounter_advance':
          showPopupText(null, 'Next encounter: ' + evt.next);
          break;
        case 'expedition_failed':
          showPopupText(null, 'Expedition failed — ' + evt.zone);
          break;
        default:
          // ignore unknown events for now
          break;
      }
    }, i * 220);
  });
}

function showPopupText(targetIndex, text, isPlayer) {
  const container = isPlayer ? document.querySelector('.profile-orb') : (document.querySelector(`.enemy-list-item[data-target="${targetIndex}"] .enemy-icon`) || document.querySelector('.enemy-sigil'));
  if (!container) return;
  const el = document.createElement('div');
  el.className = 'damage-pop';
  el.textContent = text;
  container.style.position = container.style.position || 'relative';
  container.appendChild(el);
  // position after layout so offsetWidth/Height are available
  requestAnimationFrame(() => {
    const cw = container.clientWidth;
    const ch = container.clientHeight;
    const ew = el.offsetWidth;
    const eh = el.offsetHeight;
    el.style.left = `${Math.max(6, Math.round((cw - ew) / 2))}px`;
    el.style.top = `${Math.max(6, Math.round(ch * 0.08))}px`;
    el.style.transform = '';
  });
  setTimeout(() => el.remove(), 1200);
}

function showDamagePopup(targetIndex, text, isPlayer) {
  const container = isPlayer ? document.querySelector('.profile-orb') : (document.querySelector(`.enemy-list-item[data-target="${targetIndex}"] .enemy-icon`) || document.querySelector('.enemy-sigil'));
  if (!container) return;
  const el = document.createElement('div');
  el.className = 'damage-pop';
  el.textContent = text;
  container.style.position = container.style.position || 'relative';
  container.appendChild(el);
  requestAnimationFrame(() => {
    const cw = container.clientWidth;
    const ch = container.clientHeight;
    const ew = el.offsetWidth;
    const eh = el.offsetHeight;
    el.style.left = `${Math.max(6, Math.round((cw - ew) / 2))}px`;
    el.style.top = `${Math.max(6, Math.round(ch * 0.18))}px`;
    el.style.transform = '';
  });
  setTimeout(() => el.remove(), 1200);
}

function renderLanding() {
  const characters = state?.characters || [];
  app.innerHTML = `
    <section class="origin-screen">
      <nav class="origin-nav">
        <div class="wordmark"><span class="wordmark-mark">CR</span> Chronicles of Reincarnation</div>
        <span class="fan-label">Unofficial Python-powered fan prototype</span>
      </nav>
      <header class="origin-heading">
        <p class="eyebrow">A NEW WORLD REMEMBERS EVERY CHOICE</p>
        <h1>Choose your <em>origin.</em></h1>
        <p>Two souls. Two power fantasies. Two histories that may one day collide. Your first decision changes the resources you gather, the skills you master, and the story the world records.</p>
      </header>
      <div class="origin-grid">
        ${characters.map((character, index) => characterCard(character, index)).join("")}
      </div>
      <div class="origin-action">
        <button class="primary-button" id="begin-chronicle">Begin ${escapeHtml(characters.find((item) => item.id === selectedCharacter)?.route || "Chronicle")}</button>
      </div>
    </section>`;

  app.querySelectorAll(".origin-card").forEach((card) => {
    card.addEventListener("click", () => {
      selectedCharacter = card.dataset.character;
      renderLanding();
    });
  });
  app.querySelector("#begin-chronicle")?.addEventListener("click", () =>
    mutate("/api/new-game", { character: selectedCharacter })
  );
}

function characterCard(character, index) {
  const selected = character.id === selectedCharacter;
  const sigil = character.id === "rimuru" ? "slime" : "demon";
  return `
    <button class="origin-card ${escapeHtml(character.id)} ${selected ? "selected" : ""}" data-character="${escapeHtml(character.id)}" aria-pressed="${selected}">
      <div class="origin-visual"><span class="sigil ${sigil}" aria-hidden="true"></span></div>
      <div class="origin-copy">
        <span class="origin-number">0${index + 1} / ${escapeHtml(character.route)}</span>
        <h2>${escapeHtml(character.name)}</h2>
        <span class="origin-title">${escapeHtml(character.title)}</span>
        <p>${escapeHtml(character.intro)}</p>
        <div class="origin-ability">
          <strong>${escapeHtml(character.ability)}</strong>
          <span>${escapeHtml(character.ability_text)}</span>
        </div>
      </div>
    </button>`;
}

function renderGame() {
  const info = state.character_info;
  const glyph = state.character === "rimuru" ? "水" : "黒";
  app.innerHTML = `
    <section class="game-shell">
      <nav class="game-nav">
        <div class="wordmark"><span class="wordmark-mark">CR</span> Chronicles</div>
        <div class="nav-center"><span class="save-dot"></span> Auto-saved locally · ${escapeHtml(info.route)}</div>
        <button class="ghost-button" id="new-chronicle">New Chronicle</button>
      </nav>
      <div class="game-layout">
        <aside class="panel profile-panel">
          <div class="profile-orb"><span class="profile-glyph">${glyph}</span></div>
          <div class="profile-details">
            <div class="profile-name">
              <p class="eyebrow">${escapeHtml(info.route)}</p>
              <h1>${escapeHtml(info.name)}</h1>
              <p>${escapeHtml(info.title)} · ${escapeHtml(state.alignment)}</p>
            </div>
            <div class="level-row"><strong>Level ${state.level}</strong><span>${state.xp} / ${state.xp_next} XP</span></div>
            ${meter(state.xp, state.xp_next, "xp", "Experience")}
            <div class="stat-block">
              ${bar("Vitality", state.hp, state.max_hp, "hp")}
              ${bar("Mana", state.mana, state.max_mana, "mana")}
              ${bar("Focus", state.focus, state.max_focus, "focus")}
            </div>
            <div class="stat-grid">
              <div><strong>${state.attack}</strong><span>Attack</span></div>
              <div><strong>${state.defense}</strong><span>Defense</span></div>
              <div><strong>${state.speed}</strong><span>Speed</span></div>
            </div>
            <div class="resource-grid">
              <div><strong>${state[state.resource_key]}</strong><span>${escapeHtml(state.resource_label)}</span></div>
              <div><strong>${state.insight}</strong><span>Insight</span></div>
              <div><strong>${state.gold}</strong><span>Gold</span></div>
            </div>
            <div class="route-ability">
              <strong>${escapeHtml(info.ability)}</strong>
              <p>${escapeHtml(info.ability_text)}</p>
            </div>
          </div>
        </aside>

        <section class="panel center-panel">
          <header class="chronicle-head">
            <div>
              <p class="eyebrow">CHAPTER I · THE FIRST THRESHOLD</p>
              <h2>${state.character === "rimuru" ? "Beneath the sealed world" : "A whisper beyond the abyss"}</h2>
            </div>
            <div class="progress-seal" title="Chapter progress">${state.chronicle_progress}%</div>
          </header>
          <section class="actions-section">
            <div class="section-title"><h3>Available actions</h3><span>Focus restores every ${state.focus_recovery_seconds}s</span></div>
            <div class="action-list">${state.actions.map(actionRow).join("")}</div>
          </section>
          <section class="stories-section">
            <div class="section-title"><h3>Stories</h3><span>Discovered but not yet started</span></div>
            <div class="story-list">${(state.available_stories || []).map(s => storyRow(s)).join("")}</div>
          </section>
          <section class="log-section">
            <div class="section-title"><h3>Living chronicle</h3><span>${state.total_victories} victories recorded</span></div>
            <div class="log-list">${[...state.log].reverse().map(logEntry).join("")}</div>
          </section>
          <section class="regions-section">
            <div class="section-title"><h3>Regions</h3><span>Defeat 5 foes to reveal each boss</span></div>
            <div class="regions">${state.zones.map(regionCard).join("")}</div>
          </section>
        </section>

        <aside class="panel battle-panel">
          ${battlePanel()}
        </aside>
      </div>
    </section>`;
  bindGameEvents();
}

function meter(value, max, type, label) {
  return `<div class="meter ${type}" role="progressbar" aria-label="${escapeHtml(label)}" aria-valuemin="0" aria-valuemax="${max}" aria-valuenow="${value}"><span style="--value:${clampPercent(value, max)}%"></span></div>`;
}

function bar(label, value, max, type) {
  return `<div><div class="bar-label"><span>${escapeHtml(label)}</span><b>${value} / ${max}</b></div>${meter(value, max, type, label)}</div>`;
}

function svgForAction(id) {
  const icons = {
    gather_dew: '<svg width="42" height="42" viewBox="0 0 128 128" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Gather dew"><rect width="128" height="128" rx="22" fill="#0d1515"/><circle cx="64" cy="64" r="36" fill="#132a2c" stroke="#5dd9c7" stroke-width="3" opacity="0.8"/><path d="M64 24c-18 21-28 34-28 48 0 16 12 28 28 28s28-12 28-28c0-14-10-27-28-48Z" fill="#8ff2df"/><path d="M64 38c-8 13-16 22-16 29 0 9 7 16 16 16s16-7 16-16c0-7-8-16-16-29Z" fill="#dffdf6" opacity="0.42"/><path d="M52 88c7 5 13 8 12 17M76 88c-7 6-13 9-12 17" stroke="#9cf7e6" stroke-width="5" stroke-linecap="round" opacity="0.8"/></svg>',
    analyze_moss: '<svg width="42" height="42" viewBox="0 0 128 128" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Analyze moss"><rect width="128" height="128" rx="22" fill="#0d1320"/><circle cx="64" cy="64" r="34" fill="#14263f" stroke="#7aa7ff" stroke-width="3"/><path d="M40 66c8-20 20-30 34-30 15 0 26 8 34 24-6 4-10 7-15 10-9-8-18-11-30-10-7 1-14 4-23 6Z" fill="#67a6ff" opacity="0.8"/><path d="M44 74c10-7 20-10 32-8 9 1 17 5 25 12" stroke="#dce9ff" stroke-width="5" stroke-linecap="round" fill="none"/><circle cx="46" cy="72" r="5" fill="#dce9ff"/><path d="M78 38l15 27M85 38l19 13M68 45l18 23" stroke="#dce9ff" stroke-width="4" stroke-linecap="round" opacity="0.7"/></svg>',
    shape_body: '<svg width="42" height="42" viewBox="0 0 128 128" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Shape body"><rect width="128" height="128" rx="22" fill="#171611"/><circle cx="64" cy="52" r="22" fill="#f1c574"/><path d="M34 95c8-20 24-30 30-30s22 10 30 30" fill="#f1c574" opacity="0.9"/><path d="M54 36c6-13 18-18 30-14" stroke="#ffd994" stroke-width="4" stroke-linecap="round" fill="none" opacity="0.8"/><path d="M36 54c8-15 18-21 28-23" stroke="#ffd994" stroke-width="4" stroke-linecap="round" fill="none" opacity="0.5"/><path d="M92 54c-8-15-18-21-28-23" stroke="#ffd994" stroke-width="4" stroke-linecap="round" fill="none" opacity="0.5"/></svg>',
    silent_scout: '<svg width="42" height="42" viewBox="0 0 128 128" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Silent scout"><rect width="128" height="128" rx="22" fill="#0b1415"/><circle cx="64" cy="64" r="30" fill="#1b2d2b" stroke="#8de0d0" stroke-width="3"/><path d="M64 26c-20 0-36 16-36 38s16 38 36 38 36-16 36-38-16-38-36-38Z" fill="#172a2a" stroke="#8de0d0" stroke-width="3"/><circle cx="64" cy="64" r="9" fill="#8de0d0"/><path d="M64 18v18M64 110v18M18 64h18M92 64h18" stroke="#8de0d0" stroke-width="4" stroke-linecap="round" opacity="0.8"/></svg>',
    talk_goblins: '<svg width="42" height="42" viewBox="0 0 128 128" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Talk to goblins"><rect width="128" height="128" rx="22" fill="#171612"/><path d="M28 38h52c12 0 22 10 22 22v15c0 12-10 22-22 22H58l-16 14v-14H28c-12 0-22-10-22-22V60c0-12 10-22 22-22Z" fill="#f5d081" opacity="0.15" stroke="#f5d081" stroke-width="4"/><path d="M40 58h32M40 74h22" stroke="#f5d081" stroke-width="5" stroke-linecap="round"/><circle cx="96" cy="52" r="18" fill="#f5d081" opacity="0.8"/><path d="M89 49l7 7 14-15" stroke="#171612" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    magicule_circulation: '<svg width="42" height="42" viewBox="0 0 128 128" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Magicule circulation"><rect width="128" height="128" rx="22" fill="#0d1618"/><circle cx="64" cy="64" r="34" fill="#112a2d" stroke="#8fe7d3" stroke-width="3"/><path d="M64 25v18M64 85v18M25 64h18M85 64h18" stroke="#8fe7d3" stroke-width="5" stroke-linecap="round"/><circle cx="64" cy="64" r="11" fill="#8fe7d3" opacity="0.95"/><path d="M42 42l12 12M86 86l12 12M42 86l12-12M86 42l12-12" stroke="#c8fff1" stroke-width="4" stroke-linecap="round" opacity="0.7"/></svg>',
    train_allies: '<svg width="42" height="42" viewBox="0 0 128 128" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Train allies"><rect width="128" height="128" rx="22" fill="#17140f"/><path d="M28 92c8-20 22-30 36-30s28 10 36 30" fill="#f0c974" opacity="0.18" stroke="#f0c974" stroke-width="4"/><circle cx="46" cy="54" r="12" fill="#f0c974"/><circle cx="64" cy="50" r="12" fill="#f0c974"/><circle cx="82" cy="54" r="12" fill="#f0c974"/><path d="M36 40l10 12M92 40l-10 12" stroke="#f0c974" stroke-width="4" stroke-linecap="round" opacity="0.8"/><path d="M54 98l10-18 10 18" stroke="#f7df9d" stroke-width="5" stroke-linecap="round" stroke-linejoin="round" fill="none"/></svg>',
    default: '<svg width="42" height="42" viewBox="0 0 128 128" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Default action"><rect width="128" height="128" rx="22" fill="#10181a"/><circle cx="64" cy="64" r="28" fill="#26363a" stroke="#9eb8bd" stroke-width="3"/><path d="M64 36v56M36 64h56" stroke="#9eb8bd" stroke-width="6" stroke-linecap="round" opacity="0.8"/></svg>'
  };
  return icons[id] || icons.default;
}

function svgForStory(story) {
  const id = String(story?.id || "");
  const isCave = /cave|marsh|deep|grotto|tunnel/i.test(id);
  const isVillage = /village|goblin|forest|road|camp/i.test(id);
  const isRuins = /ruin|ancient|temple|crypt|sentinel/i.test(id);
  if (isCave) {
    return '<svg width="46" height="46" viewBox="0 0 128 128" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Cave story"><rect width="128" height="128" rx="18" fill="#0e1115"/><path d="M16 88c20-26 31-38 48-38 17 0 31 12 48 38v18H16V88Z" fill="#203440"/><path d="M30 84c8-18 18-26 34-26s26 8 34 26" stroke="#7fe5d4" stroke-width="5" fill="none" stroke-linecap="round"/><circle cx="64" cy="48" r="10" fill="#7fe5d4" opacity="0.8"/></svg>';
  }
  if (isRuins) {
    return '<svg width="46" height="46" viewBox="0 0 128 128" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Ruins story"><rect width="128" height="128" rx="18" fill="#120f14"/><path d="M22 92h84L94 36H34l-12 56Z" fill="#2a2135" stroke="#d9b56d" stroke-width="3"/><path d="M46 92V58h32v34M30 92V66h12v26M86 92V66h12v26" stroke="#d9b56d" stroke-width="4" fill="none"/><circle cx="64" cy="50" r="10" fill="#d9b56d" opacity="0.8"/></svg>';
  }
  if (isVillage) {
    return '<svg width="46" height="46" viewBox="0 0 128 128" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Village story"><rect width="128" height="128" rx="18" fill="#0d1410"/><path d="M20 90h88v18H20z" fill="#1a2d24"/><path d="M34 90V56l28-24 28 24v34" fill="#20372d" stroke="#8fe7d3" stroke-width="3"/><path d="M48 90V68h32v22" fill="#8fe7d3" opacity="0.18"/><path d="M60 43h8v12h-8z" fill="#8fe7d3" opacity="0.8"/></svg>';
  }
  return '<svg width="46" height="46" viewBox="0 0 128 128" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Story default"><rect width="128" height="128" rx="18" fill="#0d1416"/><rect x="24" y="24" width="80" height="80" rx="16" fill="#14222d" stroke="#7fe5d4" stroke-width="3"/><path d="M38 46h52M38 64h44M38 82h34" stroke="#7fe5d4" stroke-width="5" stroke-linecap="round"/><circle cx="86" cy="82" r="10" fill="#7fe5d4" opacity="0.8"/></svg>';
}

function actionRow(action) {
  const running = state.activity && state.activity.action_id === action.id;
  const disabled = state.focus < action.cost || !!state.battle || running;
  // compute queued count for this action from aggregated queue provided by server
  const queueCount = (state.action_queue || []).reduce((sum, item) => sum + (item.id === action.id ? item.count : 0), 0);
  const progressHtml = running
    ? `<div class="action-progress">${meter(state.activity.progress, 100, 'progress', action.name)}</div>`
    : "";
  const queuedBadge = queueCount > 0 ? `<span class="queued-badge">${queueCount}</span>` : "";
  const buttons = running
    ? `<div class="action-buttons"><button class="action-cancel" data-cancel>Cancel</button></div>`
    : `<div class="action-buttons">${queuedBadge}<button class="action-button" data-action="${escapeHtml(action.id)}" data-count="1" ${disabled ? "disabled" : ""}>×1</button><button class="action-button" data-action="${escapeHtml(action.id)}" data-count="5" ${disabled ? "disabled" : ""}>×5</button></div>`;
  return `
    <article class="action-item action-card" data-action-id="${escapeHtml(action.id)}">
      ${queueCount > 0 ? `<span class="card-queued">${queueCount}</span>` : ""}
      <div class="action-art">${svgForAction(action.id)}</div>
      <div class="action-content">
        <div class="action-header">
          <strong>${escapeHtml(action.name)}</strong>
          <div class="action-meta"><span class="action-cost">${action.cost} Focus</span><span class="action-reward">+${action.resource} ${escapeHtml(state.resource_label)}</span></div>
        </div>
        <p class="action-desc">${escapeHtml(action.description)}</p>
        <div class="action-footer">
          ${progressHtml}
          <div class="action-controls">${buttons}</div>
        </div>
      </div>
    </article>`;
}

function storyRow(story) {
  const icon = svgForStory(story);
  return `
    <article class="story-item">
      <div class="story-left">${icon}</div>
      <div class="story-main"><strong>${escapeHtml(story.title)}</strong><p>${escapeHtml(story.text || story.subtitle || '')}</p></div>
      <div class="story-right"><button class="story-start" data-story="${escapeHtml(story.id)}">Start</button></div>
    </article>`;
}

function enemySigilSvg(name = "Enemy") {
  const lower = String(name).toLowerCase();
  const isSpider = /spider|fang|web|crawler/i.test(lower);
  const isLizard = /lizard|serpent|basilisk|reptile/i.test(lower);
  const isGoblin = /goblin|wolf|orc|bandit/i.test(lower);
  const isBoss = /boss|sentinel|guardian|captain|centipede|basilisk/i.test(lower);

  if (isSpider) {
    return `<div class="enemy-sigil" aria-label="Spider enemy"><svg viewBox="0 0 160 160" xmlns="http://www.w3.org/2000/svg"><rect width="160" height="160" fill="transparent"/><g fill="none" stroke="#ef8674" stroke-width="6" stroke-linecap="round" stroke-linejoin="round">
      <circle cx="80" cy="82" r="26" fill="#221415" stroke="#ef8674"/><circle cx="80" cy="82" r="8" fill="#ef8674"/>
      <path d="M26 56L48 64M134 56L112 64M26 104L48 96M134 104L112 96M58 32L66 54M102 32L94 54M58 128L66 106M102 128L94 106"/>
      <path d="M54 96L40 118M106 96L120 118M54 64L38 44M106 64L122 44"/>
    </g></svg></div>`;
  }

  if (isLizard) {
    return `<div class="enemy-sigil" aria-label="Lizard enemy"><svg viewBox="0 0 160 160" xmlns="http://www.w3.org/2000/svg"><rect width="160" height="160" fill="transparent"/><g fill="none" stroke="#ef8674" stroke-width="6" stroke-linecap="round" stroke-linejoin="round">
      <path d="M32 90c12-28 24-42 48-42s36 14 48 42c-8 18-24 30-48 30s-40-12-48-30Z" fill="#1c1719"/>
      <path d="M44 66l18-20M116 66l-18-20M58 44l8 18M102 44l-8 18"/>
      <circle cx="62" cy="86" r="6" fill="#ef8674"/><circle cx="98" cy="86" r="6" fill="#ef8674"/>
      <path d="M68 104l12 14 12-14"/>
    </g></svg></div>`;
  }

  if (isGoblin) {
    return `<div class="enemy-sigil" aria-label="Goblin enemy"><svg viewBox="0 0 160 160" xmlns="http://www.w3.org/2000/svg"><rect width="160" height="160" fill="transparent"/><g fill="none" stroke="#ef8674" stroke-width="6" stroke-linecap="round" stroke-linejoin="round">
      <path d="M54 102l-20-20 26-28 30 10 20-10 26 28-20 20H54Z" fill="#1f1718"/>
      <circle cx="66" cy="76" r="5" fill="#ef8674"/><circle cx="94" cy="76" r="5" fill="#ef8674"/>
      <path d="M66 98h28"/>
    </g></svg></div>`;
  }

  if (isBoss) {
    return `<div class="enemy-sigil boss" aria-label="Boss enemy"><svg viewBox="0 0 160 160" xmlns="http://www.w3.org/2000/svg"><rect width="160" height="160" fill="transparent"/><g fill="none" stroke="#f4c08d" stroke-width="6" stroke-linecap="round" stroke-linejoin="round">
      <path d="M80 24L120 52L102 118H58L40 52L80 24Z" fill="#241a16"/>
      <path d="M80 46V106M52 64h56M52 96h56"/>
      <circle cx="80" cy="78" r="8" fill="#f4c08d"/>
    </g></svg></div>`;
  }

  return `<div class="enemy-sigil" aria-label="Enemy sigil"><svg viewBox="0 0 160 160" xmlns="http://www.w3.org/2000/svg"><rect width="160" height="160" fill="transparent"/><g fill="none" stroke="#ef8674" stroke-width="6" stroke-linecap="round" stroke-linejoin="round">
    <path d="M80 22L118 56L102 120H58L42 56L80 22Z" fill="#1b181b"/>
    <path d="M80 48v52M52 76h56M58 44l22 18 22-18"/>
    <circle cx="80" cy="82" r="8" fill="#ef8674"/>
  </g></svg></div>`;
}

// small thumb SVG used inside enemy lists to avoid font-rendering issues
function enemyThumbSvg(name) {
  const lower = String(name || '').toLowerCase();
  let color = '#ef8674';
  if (/lizard|basilisk|reptile|serpent/i.test(lower)) color = '#f4c08d';
  if (/goblin|wolf|orc|bandit/i.test(lower)) color = '#8de0d0';
  return `<svg class="enemy-thumb" width="36" height="36" viewBox="0 0 160 160" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><rect width="160" height="160" fill="transparent"/><g fill="none" stroke="${color}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"><circle cx="80" cy="80" r="36" fill="#0f1416" stroke="${color}"/><path d="M64 68c6-6 12-8 24-6" stroke="${color}" stroke-width="4" stroke-linecap="round"/><circle cx="70" cy="84" r="4" fill="${color}"/><circle cx="96" cy="84" r="4" fill="${color}"/></g></svg>`;
}

function logEntry(item) {
  return `<div class="log-entry ${escapeHtml(item.kind)}">${escapeHtml(item.text)}</div>`;
}

function regionCard(zone) {
  const label = zone.boss_defeated ? "Explore again" : zone.boss_ready ? `Challenge ${zone.boss}` : "Enter region";
  const progress = zone.boss_defeated ? "Boss defeated" : `${Math.min(zone.clears, zone.target)} / ${zone.target} sightings`;
  return `
    <article class="region-card ${zone.unlocked ? "" : "locked"}">
      <strong>${escapeHtml(zone.name)}</strong>
      <p>${escapeHtml(zone.subtitle)}</p>
      <div class="region-progress"><span>${escapeHtml(progress)}</span>${zone.boss_defeated ? "<span>✓</span>" : ""}</div>
      <button class="zone-button" data-zone="${escapeHtml(zone.id)}" ${!zone.unlocked || !!state.battle ? "disabled" : ""}>${escapeHtml(label)}</button>
    </article>`;
}

function battlePanel() {
  const battle = state.battle;
  if (!battle) {
    return `
      <header class="battle-head"><p class="eyebrow">ENCOUNTER</p><div class="battle-head-row"><h2>The path is quiet</h2></div></header>
      <div class="battle-stage"><div class="enemy-empty"><div class="empty-mark"></div><strong>No active enemy</strong><p>Choose an unlocked region to hunt, grow stronger, and advance its boss meter.</p></div></div>
      <div class="enemy-info"><div class="enemy-title"><strong>Combat preparation</strong><span>Ready</span></div></div>
      <div class="skill-list">${state.skills.map(skillPreview).join("")}</div>
      <div class="battle-tools"><button class="ghost-button" id="rest-button">Rest · ${state.level * 2} gold</button></div>`;
  }

  // support grouped encounters: pick the current target and show summary
  const enemies = Array.isArray(battle.enemies) ? battle.enemies : [];
  const current = state.battle && state.battle.current_target ? state.battle.current_target : (enemies.find(e => e.hp > 0) || enemies[0] || {});
  const title = enemies.length > 1 ? `Band of ${enemies.length}` : (current.name || "Unknown")
  const subtitle = current.level ? `Level ${current.level}${battle.boss ? " · Boss" : ""}` : (battle.boss ? "Boss" : "")

  return `
    <header class="battle-head">
      <p class="eyebrow">${battle.boss ? "REGION BOSS" : "ENCOUNTER"} · TURN ${battle.turn}</p>
      <div class="battle-head-row"><h2>${escapeHtml(title)}</h2><label class="auto-label"><input type="checkbox" id="auto-combat" /> Auto</label></div>
    </header>
    <div class="battle-stage">${enemySigilSvg(current.name || title)}</div>
    <div class="enemy-info">
      <div class="enemy-title"><strong>${escapeHtml(current.name || title)}</strong><span>${escapeHtml(subtitle)}</span></div>
      ${bar("Enemy vitality", current.hp || 0, current.max_hp || 1, "hp")}
      ${enemies.length > 1 ? `<div class="enemy-list">${enemies.map((e, i) => `<button class="enemy-list-item${(selectedEnemyIndex === i) ? ' selected' : ''}" data-target="${i}"><span class="enemy-icon">${enemyThumbSvg(e.name)}</span><span class="enemy-label">${escapeHtml(e.name)}</span><span class="enemy-hp">${e.hp}/${e.max_hp}</span></button>`).join("")}</div>` : ""}
    </div>
    <div class="skill-list">${state.skills.map(skillButton).join("")}</div>
    <div class="battle-tools"><button class="ghost-button" id="flee-button">Withdraw</button></div>`;
}

function skillPreview(skill) {
  const status = skill.unlocked ? `${skill.mana} Mana` : `Unlocks Lv. ${skill.level}`;
  return `<button class="skill-button" disabled><span><strong>${escapeHtml(skill.name)}</strong><span>${escapeHtml(skill.description)}</span></span><b class="skill-cost">${status}</b></button>`;
}

function skillButton(skill) {
  const resourceCost = skill.resource_cost ? ` · ${skill.resource_cost} ${state.resource_label}` : "";
  const disabled = !skill.unlocked || state.mana < skill.mana || (skill.resource_cost || 0) > state[state.resource_key];
  const status = skill.unlocked ? `${skill.mana} Mana${resourceCost}` : `Unlocks Lv. ${skill.level}`;
  return `<button class="skill-button" data-skill="${escapeHtml(skill.id)}" ${disabled ? "disabled" : ""}><span><strong>${escapeHtml(skill.name)}</strong><span>${escapeHtml(skill.description)}</span></span><b class="skill-cost">${escapeHtml(status)}</b></button>`;
}

function bindGameEvents() {
  app.querySelectorAll("[data-action]").forEach((button) =>
    button.addEventListener("click", () => mutate("/api/action", { action: button.dataset.action, count: Number(button.dataset.count) }))
  );
  app.querySelectorAll("[data-zone]").forEach((button) =>
    button.addEventListener("click", () => mutate("/api/combat/start", { zone: button.dataset.zone }))
  );
  app.querySelectorAll("[data-skill]").forEach((button) =>
    button.addEventListener("click", () => {
      // include the selected enemy index when sending the combat turn
      mutate("/api/combat/turn", { skill: button.dataset.skill, target: selectedEnemyIndex });
    })
  );
  app.querySelectorAll(".enemy-list-item").forEach((btn) => btn.addEventListener("click", (e) => {
    const idx = Number(btn.dataset.target);
    if (Number.isNaN(idx)) return;
    selectedEnemyIndex = idx;
    render();
  }));
  app.querySelectorAll("[data-cancel]").forEach((btn) => btn.addEventListener("click", () => mutate("/api/action/cancel")));
  app.querySelectorAll(".story-start").forEach((btn) => btn.addEventListener("click", () => mutate("/api/story/start", { node: btn.dataset.story })));
  app.querySelector("#flee-button")?.addEventListener("click", () => mutate("/api/combat/flee"));
  app.querySelector("#rest-button")?.addEventListener("click", () => mutate("/api/rest"));
  app.querySelector("#auto-combat")?.addEventListener("change", (event) => toggleAuto(event.target.checked));
  app.querySelector("#new-chronicle")?.addEventListener("click", async () => {
    if (window.confirm("Erase this local save and choose a new origin?")) await mutate("/api/reset");
  });
}

function renderChoice() {
  const choice = state.pending_choice;
  const overlay = document.createElement("div");
  overlay.className = "choice-overlay";
  overlay.innerHTML = `
    <article class="choice-card">
      <p class="eyebrow">${escapeHtml(choice.eyebrow)}</p>
      <h2>${escapeHtml(choice.title)}</h2>
      <p>${escapeHtml(choice.text)}</p>
      <div class="choice-options">
        ${choice.options.map((option) => `<button class="choice-button" data-choice="${escapeHtml(option.id)}"><strong>${escapeHtml(option.label)}</strong><span>${escapeHtml(option.description)}</span></button>`).join("")}
      </div>
    </article>`;
  overlay.querySelectorAll("[data-choice]").forEach((button) =>
    button.addEventListener("click", () => mutate("/api/choice", { choice: button.dataset.choice }))
  );
  app.appendChild(overlay);
}

function toggleAuto(enabled) {
  window.clearInterval(autoTimer);
  autoTimer = null;
  if (!enabled || !state?.battle) return;
  autoTimer = window.setInterval(async () => {
    if (busy || !state?.battle) return stopAutoIfNeeded();
    const usable = [...state.skills].reverse().find((skill) =>
      skill.unlocked && state.mana >= skill.mana && (skill.resource_cost || 0) <= state[state.resource_key]
    );
    if (usable) {
      // auto-select a target: prefer lowest hp alive
      const enemies = Array.isArray(state.battle.enemies) ? state.battle.enemies : [];
      const alive = enemies.filter(e => e.hp > 0);
      let targetIdx = selectedEnemyIndex;
      if (alive.length) {
        // choose lowest HP enemy index
        let minHp = Infinity; let minIdx = 0;
        enemies.forEach((e, i) => { if (e.hp > 0 && e.hp < minHp) { minHp = e.hp; minIdx = i; } });
        targetIdx = minIdx;
      } else {
        targetIdx = selectedEnemyIndex;
      }
      await mutate("/api/combat/turn", { skill: usable.id, target: targetIdx });
    }
  }, 720);
}

function stopAutoIfNeeded() {
  if (state?.battle) return;
  window.clearInterval(autoTimer);
  autoTimer = null;
}

async function refreshState() {
  if (busy || !state?.started || state.battle) return;
  try {
    state = await api("/api/state");
    render();
  } catch (_) {
    // A temporary local-server pause should not interrupt the player with alerts.
  }
}

async function boot() {
  try {
    state = await api("/api/state");
    render();
    refreshTimer = window.setInterval(refreshState, 2000);
  } catch (error) {
    app.innerHTML = `<section class="loading-screen"><p class="eyebrow">THE PYTHON SERVER IS ASLEEP</p><p>${escapeHtml(error.message)}</p></section>`;
  }
}

boot();

