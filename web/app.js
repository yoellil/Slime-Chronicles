const app = document.querySelector("#app");
const toast = document.querySelector("#toast");
let state = null;
let selectedCharacter = "rimuru";
let busy = false;
let autoTimer = null;
let refreshTimer = null;
// currently selected enemy index (0-based) in multi-enemy encounters
let selectedEnemyIndex = null;


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

function actionRow(action) {
  const running = state.activity && state.activity.action_id === action.id;
  const disabled = state.focus < action.cost || !!state.battle || running;
  const progressHtml = running
    ? `<div class="action-progress">${meter(state.activity.progress, 100, 'progress', action.name)}<div class="small">${state.activity.remaining}s remaining</div></div>`
    : "";
  const buttons = running
    ? `<div class="action-buttons"><button class="action-cancel" data-cancel>Cancel</button></div>`
    : `<div class="action-buttons"><button class="action-button" data-action="${escapeHtml(action.id)}" data-count="1" ${disabled ? "disabled" : ""}>×1</button><button class="action-button" data-action="${escapeHtml(action.id)}" data-count="5" ${disabled ? "disabled" : ""}>×5</button></div>`;
  return `
    <article class="action-item">
      <div>
        <strong>${escapeHtml(action.name)}</strong>
        <p>${escapeHtml(action.description)}</p>
        <div class="action-cost">${action.cost} Focus · +${action.xp} XP · +${action.resource} ${escapeHtml(state.resource_label)}</div>
        ${progressHtml}
      </div>
      ${buttons}
    </article>`;
}

function storyRow(story) {
  return `<article class="story-item"><div><strong>${escapeHtml(story.title)}</strong><p>${escapeHtml(story.text || story.subtitle || '')}</p></div><div><button class="story-start" data-story="${escapeHtml(story.id)}">Start</button></div></article>`;
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
    <div class="battle-stage"><div class="enemy-sigil" aria-label="Enemy sigil"></div></div>
    <div class="enemy-info">
      <div class="enemy-title"><strong>${escapeHtml(current.name || title)}</strong><span>${escapeHtml(subtitle)}</span></div>
      ${bar("Enemy vitality", current.hp || 0, current.max_hp || 1, "hp")}
      ${enemies.length > 1 ? `<div class="enemy-list">${enemies.map((e, i) => `<button class="enemy-list-item${(selectedEnemyIndex === i) ? ' selected' : ''}" data-target="${i}">${escapeHtml(e.name)} (${e.hp}/${e.max_hp})</button>`).join("")}</div>` : ""}
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

