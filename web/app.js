"use strict";
/* Chronicles of Reincarnation: front end. The Python engine owns every rule; this file only draws and asks. */

const { icon, tile, creature, hero: heroArt } = window.Art;
const app = document.querySelector("#app");
const overlayEl = document.querySelector("#overlay");
const toastsEl = document.querySelector("#toasts");
const fxEl = document.querySelector("#fx");

/* ---------------------------------------------------------------- utils */
const store = {
  get(key, fallback) { try { const v = localStorage.getItem("cor." + key); return v === null ? fallback : JSON.parse(v); } catch { return fallback; } },
  set(key, value) { try { localStorage.setItem("cor." + key, JSON.stringify(value)); } catch { /* storage unavailable */ } },
};
const AMP = String.fromCharCode(38);
const esc = (v) => String(v ?? "").replaceAll(AMP, AMP + "amp;").replaceAll("<", AMP + "lt;").replaceAll(">", AMP + "gt;").replaceAll('"', AMP + "quot;").replaceAll("'", AMP + "#039;");
const cap = (s) => String(s).replaceAll("_", " ").replace(/\b\w/g, (c) => c.toUpperCase());
const fmt = (n) => {
  n = Math.round(Number(n) || 0);
  if (Math.abs(n) >= 1e6) return (n / 1e6).toFixed(1) + "M";
  if (Math.abs(n) >= 1e4) return (n / 1e3).toFixed(1) + "k";
  return n.toLocaleString("en-US");
};
const pct = (v, m) => Math.max(0, Math.min(100, m ? (v / m) * 100 : 0));
const plural = (n, one, many) => `${n} ${n === 1 ? one : many || one + "s"}`;
const $ = (sel, root = document) => root.querySelector(sel);
const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];

const RES = {
  magicules: { label: "Magicules", cls: "mag", icon: "spiral", r: "r-mag" },
  gold: { label: "Gold", cls: "gold", icon: "coin", r: "r-gold" },
  insight: { label: "Insight", cls: "ins", icon: "eye", r: "r-ins" },
  research: { label: "Research", cls: "rsc", icon: "flask", r: "r-res" },
};
const resLabel = (k) => RES[k]?.label || cap(k);
const FRIENDS = { goblin_village: "Goblin village", direwolf_pack: "Direwolf pack", veldora: "Veldora", dwargon: "Dwargon", lizardmen: "Lizardmen", orc_people: "Orc people", kijin: "Kijin", tempest_federation: "Tempest Federation", falmuth: "Falmuth", merchant_guild: "Merchant guild", mercenary_captain: "Mercenaries", diablo: "Diablo" };
const DIFF_SECONDS = { Simple: 3, Measured: 6, Demanding: 10, Complex: 14, Social: 7, Intense: 18 };

const JOURNEY = [
  ["awakening", "Awakening", "Prologue"], ["first_steps", "First steps", "Prologue"],
  ["seek_dragon", "The thunder in the cave", "Chapter I"], ["learn_from_friend", "Lessons from a dragon", "Chapter I"],
  ["protect_village", "The goblin village", "Chapter II"], ["chapter_one_complete", "Pack and party", "Chapter II"],
  ["dwarf_kingdom", "The mountain kingdom", "Chapter III"], ["orc_lord_arc", "The Orc Lord", "Chapter IV"],
  ["lizardmen_alliance", "Scales and fangs", "Chapter V"], ["tempest_federation", "A nation of monsters", "Chapters VI and VII"],
  ["falmuth_relations", "The human kingdom", "Chapter VIII"], ["demon_lord_awakening", "The awakening", "Chapter IX"],
  ["walpurgis", "The council of Demon Lords", "Chapter IX"], ["farmus_invasion", "The invasion", "Chapter X"],
  ["harvest_festival", "The Harvest Festival", "Chapter X"], ["epilogue", "Legends are written", "Epilogue"],
];
const phaseIndex = (p) => JOURNEY.findIndex((j) => j[0] === p);

/* ---------------------------------------------------------------- state */
let state = null;
let prev = null;
let tab = store.get("tab", "actions");
let busy = false;
let serverOffset = 0;
let selectedFoe = null;
let auto = false;
let autoTimer = null;
let menuOpen = false;
let overlayMode = null; // 'scene' | 'confirm' | 'report' | null
let wakeTimer = null;
let shellBuilt = false;
let autoDungeon = null; // zone id repeated automatically
const playedEvents = new Set();
let eventsPrimed = false;
let muted = store.get("muted", false);

const nowSec = () => (Date.now() + serverOffset) / 1000;

/* ---------------------------------------------------------------- sound */
let audio = null;
function tone(freq, dur, type = "sine", vol = 0.05, delay = 0, slide = 0) {
  if (muted) return;
  try {
    audio = audio || new (window.AudioContext || window.webkitAudioContext)();
    if (audio.state === "suspended") audio.resume();
    const t = audio.currentTime + delay;
    const osc = audio.createOscillator();
    const gain = audio.createGain();
    osc.type = type;
    osc.frequency.setValueAtTime(freq, t);
    if (slide) osc.frequency.exponentialRampToValueAtTime(Math.max(30, freq + slide), t + dur);
    gain.gain.setValueAtTime(0.0001, t);
    gain.gain.exponentialRampToValueAtTime(vol, t + 0.01);
    gain.gain.exponentialRampToValueAtTime(0.0001, t + dur);
    osc.connect(gain).connect(audio.destination);
    osc.start(t);
    osc.stop(t + dur + 0.02);
  } catch { /* audio blocked */ }
}
function sound(name) {
  switch (name) {
    case "click": tone(560, 0.05, "triangle", 0.04); break;
    case "good": tone(523, 0.09, "triangle", 0.05); tone(784, 0.14, "triangle", 0.05, 0.08); break;
    case "hit": tone(220, 0.12, "square", 0.04, 0, -120); break;
    case "hurt": tone(150, 0.2, "sawtooth", 0.05, 0, -80); break;
    case "level": [523, 659, 784, 1047].forEach((f, i) => tone(f, 0.16, "triangle", 0.05, i * 0.09)); break;
    case "story": tone(392, 0.2, "sine", 0.05); tone(587, 0.3, "sine", 0.04, 0.12); break;
    case "error": tone(160, 0.14, "square", 0.04); break;
    case "win": [392, 523, 659, 784].forEach((f, i) => tone(f, 0.2, "triangle", 0.05, i * 0.1)); break;
    case "type": tone(900 + Math.random() * 200, 0.015, "square", 0.012); break;
    default: break;
  }
}

/* ---------------------------------------------------------------- morph (DOM diff so hover, focus, scroll and CSS transitions survive updates) */
function morph(root, html) {
  const tpl = document.createElement("template");
  tpl.innerHTML = html;
  const walker = document.createTreeWalker(tpl.content, NodeFilter.SHOW_TEXT);
  const blanks = [];
  while (walker.nextNode()) if (!walker.currentNode.nodeValue.trim()) blanks.push(walker.currentNode);
  blanks.forEach((n) => n.remove());
  morphChildren(root, tpl.content);
}
function keyOf(n) { return n.nodeType === 1 ? n.getAttribute("data-key") : null; }
function morphChildren(from, to) {
  const live = Array.from(from.childNodes);
  const keyed = new Map();
  const loose = [];
  for (const n of live) { const k = keyOf(n); if (k) keyed.set(k, n); else loose.push(n); }
  let li = 0;
  const result = [];
  for (const t of Array.from(to.childNodes)) {
    const k = keyOf(t);
    let match = null;
    if (k) { match = keyed.get(k) || null; if (match) keyed.delete(k); }
    else if (li < loose.length) match = loose[li++];
    if (match && match.nodeType === t.nodeType && match.nodeName === t.nodeName) { morphNode(match, t); result.push(match); }
    else result.push(t);
  }
  const keep = new Set(result);
  for (const n of live) if (!keep.has(n)) from.removeChild(n);
  result.forEach((n, i) => { if (from.childNodes[i] !== n) from.insertBefore(n, from.childNodes[i] || null); });
}
function morphNode(a, b) {
  if (a.nodeType !== 1) { if (a.nodeValue !== b.nodeValue) a.nodeValue = b.nodeValue; return; }
  if (a.isEqualNode(b)) return;
  const liveStyle = a.hasAttribute("data-t1");
  for (const attr of Array.from(a.attributes)) if (!b.hasAttribute(attr.name) && !(liveStyle && attr.name === "style")) a.removeAttribute(attr.name);
  for (const attr of Array.from(b.attributes)) {
    if (liveStyle && attr.name === "style") continue;
    if (a.getAttribute(attr.name) !== attr.value) a.setAttribute(attr.name, attr.value);
  }
  if (a.nodeName === "INPUT") { a.checked = b.hasAttribute("checked"); return; }
  morphChildren(a, b);
}

/* ---------------------------------------------------------------- api */
async function api(path, payload) {
  const options = payload === undefined
    ? { headers: { Accept: "application/json" } }
    : { method: "POST", headers: { "Content-Type": "application/json", Accept: "application/json" }, body: JSON.stringify(payload) };
  const response = await fetch(path, options);
  let body = null;
  try { body = await response.json(); } catch { /* non-JSON error */ }
  if (!response.ok) throw new Error(body?.error || "The chronicle stumbled. Try that again.");
  return body;
}
async function act(path, payload = {}, { sfx = "click" } = {}) {
  if (busy) return false;
  busy = true;
  try {
    setState(await api(path, payload));
    sound(sfx);
    return true;
  } catch (error) {
    toast(error.message, "error");
    sound("error");
    return false;
  } finally {
    busy = false;
  }
}
async function refreshState() {
  if (busy) return;
  try { setState(await api("/api/state")); } catch { /* local server paused; stay quiet */ }
}

function setState(next) {
  prev = state;
  state = next;
  if (state.server_time) serverOffset = state.server_time * 1000 - Date.now();
  render();
  if (prev?.started && state.started) observe(prev, state);
  primeEvents();
  maybeShowScene();
}

/* ---------------------------------------------------------------- change observer: floaters, toasts, level-ups, reports */
function observe(a, b) {
  for (const key of Object.keys(RES)) {
    const d = (b[key] || 0) - (a[key] || 0);
    if (d > 0) floatAt(`[data-res="${key}"]`, `+${fmt(d)}`, `var(--${key === "magicules" ? "slime" : key === "gold" ? "gold" : key === "insight" ? "blue" : "violet"})`);
  }
  if (b.level > a.level && b.reincarnations === a.reincarnations) levelBanner(b.level, b.level - a.level);
  const fresh = newLogs(a, b);
  let shown = 0;
  for (const entry of fresh) {
    if (shown >= 3) break;
    const t = entry.text;
    if (entry.kind === "story") { toast(t, "story", "book"); shown++; sound("story"); }
    else if (entry.kind === "growth" && !t.startsWith("EVOLUTION")) { toast(t, "good", "sparkle"); shown++; }
    else if (entry.kind === "danger" && !t.includes("retaliates")) { toast(t, "error", "skull"); shown++; }
  }
  if (!a.battle && b.battle) { tab = "battle"; selectedFoe = null; auto = true; syncAuto(); paint(); }
  if (a.battle && !b.battle) {
    auto = false; syncAuto();
    if (tab === "battle") { tab = "expeditions"; store.set("tab", tab); }
    paint();
  }
  maybeShowScene();
}
function logKey(e) { return e.time + "|" + e.text; }
function newLogs(a, b) {
  const old = a.log || [];
  const cur = b.log || [];
  if (!old.length) return cur.slice(-3);
  const last = logKey(old[old.length - 1]);
  let idx = -1;
  for (let i = cur.length - 1; i >= 0; i--) if (logKey(cur[i]) === last) { idx = i; break; }
  return idx === -1 ? cur.slice(-3) : cur.slice(idx + 1);
}

/* ---------------------------------------------------------------- toasts and floaters */
function toast(text, kind = "info", iconName = "sparkle") {
  const el = document.createElement("div");
  el.className = `toast ${kind}`;
  el.innerHTML = `${icon(kind === "error" ? "close" : iconName, 18)}<span>${esc(text)}</span>`;
  toastsEl.appendChild(el);
  while (toastsEl.children.length > 4) toastsEl.firstChild.remove();
  setTimeout(() => { el.classList.add("out"); setTimeout(() => el.remove(), 320); }, kind === "error" ? 4200 : 3400);
}
function floatAt(selector, text, color) {
  const target = $(selector);
  if (!target) return;
  const r = target.getBoundingClientRect();
  const el = document.createElement("div");
  el.className = "float-delta";
  el.style.color = color;
  el.style.left = `${r.left + r.width / 2 - 12}px`;
  el.style.top = `${r.bottom - 6}px`;
  el.textContent = text;
  fxEl.appendChild(el);
  setTimeout(() => el.remove(), 1350);
}
function levelBanner(level, gained) {
  const el = document.createElement("div");
  el.className = "levelup";
  el.innerHTML = `<strong>Level ${level}</strong>+${5 * gained} Max HP, +${2 * gained} Max Mana, +${gained} Attack`;
  document.body.appendChild(el);
  sound("level");
  setTimeout(() => el.remove(), 3100);
}

/* ---------------------------------------------------------------- shell */
function render() {
  if (!state?.started) { shellBuilt = false; renderTitle(); return; }
  if (!shellBuilt) {
    app.innerHTML = `<div class="shell"><header class="top" id="top"></header><aside class="side" id="side" aria-label="Status"></aside><main class="center"><nav class="tabs" id="tabs" aria-label="Sections"></nav><div class="stage" id="stage"></div><section class="logpanel" id="log" aria-label="Chronicle log"></section></main><aside class="dock" id="dock" aria-label="Current activity"></aside></div>`;
    shellBuilt = true;
    prev = null;
  }
  if (tab === "battle" && !state.battle) tab = "expeditions";
  paint();
}
function paint() {
  if (!shellBuilt || !state?.started) return;
  morph($("#top"), topHTML());
  morph($("#side"), sideHTML());
  morph($("#tabs"), tabsHTML());
  morph($("#stage"), stageHTML());
  morph($("#log"), logHTML());
  morph($("#dock"), dockHTML());
  scheduleWake();
}

/* ---------------------------------------------------------------- title */
function renderTitle() {
  const hero = state?.hero;
  if ($(".title-screen")) return;
  app.innerHTML = `
    <section class="title-screen">
      <div class="title-art">
        <svg class="cave" viewBox="0 0 800 600" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
          <rect width="800" height="600" fill="#07100f"/>
          <path d="M0 0h800v70l-40 50-30-80-50 90-36-70-46 60-60-100-44 90-40-60-54 80-48-90-40 70-46-80-50 100-34-60-44 70-40-50z" fill="#0d1d1c"/>
          <path d="M0 0h800v36l-60 30-40-50-60 56-50-40-70 44-40-46-80 54-60-50-70 42-60-34-50 40-60-38z" fill="#091413"/>
          <path d="M-20 600V470c120-40 220-20 320-50s200-60 300-30 160 50 220 20v190z" fill="#0c1a19"/>
          <g fill="#56e0c0"><circle cx="120" cy="420" r="3" opacity=".7"/><circle cx="640" cy="360" r="2.4" opacity=".6"/><circle cx="700" cy="480" r="3.4" opacity=".7"/><circle cx="210" cy="520" r="2.2" opacity=".5"/><circle cx="520" cy="200" r="2" opacity=".4"/></g>
          <g stroke="#2a5d52" stroke-width="3" fill="none" stroke-linecap="round"><path d="M90 470l-6-34M96 470l8-26M650 440l-4-30M660 440l10-22"/></g>
        </svg>
        <div class="slime-stage">${heroArt(1, 0, 320)}<div class="shadow"></div></div>
      </div>
      <div class="title-copy">
        <p class="kicker">A fan-made incremental RPG</p>
        <h1>Chronicles of Reincarnation</h1>
        <p class="lede">You wake in a sealed cave with no body, no name, and a calm voice listing impossible skills. Grow from a nameless slime into the founder of a nation, one choice at a time.</p>
        <ol class="opening">
          <li><span><strong>Queue actions</strong> that finish while you are away: gather, scout, train.</span></li>
          <li><span><strong>Run loops</strong> in the background and spend Magicules on permanent upgrades.</span></li>
          <li><span><strong>Fight expeditions</strong>, recruit the monsters you beat, and make the calls that shape Tempest.</span></li>
        </ol>
        <div class="title-actions">
          <button class="btn primary lg" data-act="begin">Begin the chronicle</button>
          <span class="inline-hint">Saves automatically to this browser's local database.</span>
        </div>
        ${hero ? `<p class="inline-hint"><strong>${esc(hero.ability)}.</strong> ${esc(hero.ability_text)}</p>` : ""}
        <p class="fineprint">Unofficial fan project. Not affiliated with or endorsed by the owners of <em>That Time I Got Reincarnated as a Slime</em> or <em>Your Chronicle</em>.</p>
      </div>
    </section>`;
}

/* ---------------------------------------------------------------- battle logic */
function bestSkill(targetFoe) {
  const s = state;
  const usable = s.skills.filter((k) => k.unlocked && s.mana >= k.mana);
  const finisher = usable.find((k) => k.execute && targetFoe && targetFoe.hp / targetFoe.max_hp <= k.execute);
  if (finisher) return finisher;
  return usable.filter((k) => k.power > 0).sort((a, b) => b.power - a.power)[0] || null;
}
async function useSkill(id) {
  if (!state?.battle) return;
  await act("/api/combat/turn", { skill: id, target: targetIndex() }, { sfx: "click" });
}
function syncAuto() {
  clearInterval(autoTimer);
  autoTimer = null;
  if (auto && state?.battle) autoTimer = setInterval(autoStep, 760);
}
async function autoStep() {
  if (busy || !state?.battle || overlayMode) return;
  if (state.hp / state.max_hp < 0.3) {
    auto = false; syncAuto(); paint();
    toast("Auto-battle paused: vitality is low.", "error");
    return;
  }
  const foes = state.battle.enemies;
  let low = -1;
  foes.forEach((f, i) => { if (f.hp > 0 && (low < 0 || f.hp < foes[low].hp)) low = i; });
  selectedFoe = low < 0 ? null : low;
  const pick = bestSkill(foes[low]);
  if (!pick) { auto = false; syncAuto(); paint(); toast("Auto-battle stopped: no usable skill.", "error"); return; }
  await useSkill(pick.id);
}

/* battle feedback: floaters, hit shakes, reports */
function primeEvents() {
  if (!state?.started) return;
  const events = [...(state.battle?.events || []), ...(state.last_battle_events || [])];
  if (!eventsPrimed) {
    events.forEach((e) => playedEvents.add(e.id));
    eventsPrimed = true;
    return;
  }
  let delay = 0;
  for (const e of events) {
    if (playedEvents.has(e.id)) continue;
    playedEvents.add(e.id);
    setTimeout(() => playEvent(e), delay);
    delay += 260;
  }
}
function popAt(el, text, cls) {
  if (!el) return;
  const r = el.getBoundingClientRect();
  const d = document.createElement("div");
  d.className = `dmg ${cls || ""}`;
  d.textContent = text;
  d.style.left = `${r.left + r.width / 2 - 14}px`;
  d.style.top = `${r.top + r.height * 0.25}px`;
  fxEl.appendChild(d);
  setTimeout(() => d.remove(), 1150);
}
function shake(el, cls) {
  if (!el) return;
  el.classList.remove(cls);
  void el.offsetWidth;
  el.classList.add(cls);
  setTimeout(() => el.classList.remove(cls), 360);
}
function playEvent(e) {
  switch (e.type) {
    case "skill": {
      const foe = $(`[data-foe="${e.target}"]`);
      const big = e.damage >= (state?.attack || 1) * 3;
      popAt(foe, String(e.damage), big ? "crit" : "");
      shake(foe, "hit");
      sound("hit");
      break;
    }
    case "attack": {
      const heroEl = $("[data-hero]");
      popAt(heroEl, "-" + e.damage, "hurt");
      shake(heroEl, "hero-hit");
      sound("hurt");
      break;
    }
    case "defeat": popAt($(`[data-foe="${e.target}"]`), "Defeated", "good"); break;
    case "recruit": {
      const name = state?.party?.find((a) => a.id === e.ally_id)?.name || cap(e.ally_id);
      toast(`${name} asks to join you.`, "good", "people");
      sound("good");
      break;
    }
    case "encounter_advance": toast(`Encounter ${e.next}. You recover a little.`, "info", "swords"); break;
    case "expedition_complete": showReport(true, e.zone); break;
    case "expedition_failed": showReport(false, e.zone); break;
    default: break;
  }
}
function showReport(won, zone) {
  const run = state?.last_run || {};
  const recruited = (run.recruited || []).map((id) => state?.party?.find((a) => a.id === id)?.name || cap(id));
  const lines = won
    ? [`${plural(run.victories || 0, "victory", "victories")}`, `+${fmt(run.earned_gold || 0)} Gold, +${fmt(run.earned_magicules || 0)} Magicules`, recruited.length ? `Recruited: ${recruited.join(", ")}` : "No one asked to join this time"]
    : ["You escape with half your vitality.", "Rewards already earned are kept.", "Rest, level up, and try again."];
  sound(won ? "win" : "hurt");
  if (won && autoDungeon && autoDungeon === run.zone_id) {
    toast(`${zone} cleared. Starting it again.`, "good", "trophy");
    setTimeout(repeatDungeon, 1600);
    return;
  }
  autoDungeon = null;
  openModal(`<div class="modal report"><p class="kicker">${esc(zone)}</p><h2 class="big">${won ? "Expedition cleared" : "Expedition failed"}</h2><ul>${lines.map((l) => `<li>${esc(l)}</li>`).join("")}</ul><button class="btn primary" data-close>Continue</button></div>`, "report");
}

async function repeatDungeon() {
  if (!autoDungeon || state?.battle || overlayMode) return;
  if (state.hp / state.max_hp < 0.5) { autoDungeon = null; paint(); toast("Dungeon repeat stopped: vitality is low.", "error"); return; }
  if (!(await act("/api/combat/start", { zone: autoDungeon }, { sfx: "hit" }))) { autoDungeon = null; paint(); }
}

/* ---------------------------------------------------------------- overlays */
function openModal(html, mode) {
  overlayMode = mode;
  overlayEl.className = "overlay";
  overlayEl.innerHTML = html;
  overlayEl.hidden = false;
  overlayEl.querySelector("button")?.focus();
}
function closeOverlay() {
  overlayEl.hidden = true;
  overlayEl.innerHTML = "";
  overlayMode = null;
  clearInterval(typeTimer);
  maybeShowScene();
}
overlayEl.addEventListener("click", (ev) => { if (ev.target.closest("[data-close]")) closeOverlay(); });
function confirmDialog({ title, body, ok = "Confirm", danger = false }) {
  return new Promise((resolve) => {
    openModal(`<div class="modal" role="dialog" aria-modal="true" aria-label="${esc(title)}"><h2>${esc(title)}</h2><p>${esc(body)}</p><div class="btn-row"><button class="btn" data-no>Cancel</button><button class="btn ${danger ? "danger" : "primary"}" data-yes>${esc(ok)}</button></div></div>`, "confirm");
    const done = (v) => { overlayEl.removeEventListener("click", onClick); document.removeEventListener("keydown", onKey, true); overlayEl.hidden = true; overlayEl.innerHTML = ""; overlayMode = null; resolve(v); maybeShowScene(); };
    const onClick = (ev) => { if (ev.target.closest("[data-yes]")) done(true); else if (ev.target.closest("[data-no]") || ev.target === overlayEl) done(false); };
    const onKey = (ev) => { if (ev.key === "Escape") { ev.stopPropagation(); done(false); } };
    overlayEl.addEventListener("click", onClick);
    document.addEventListener("keydown", onKey, true);
  });
}

/* ---- story scenes: several beats, questions that shape the story, then the choice and its aftermath */
let typeTimer = null;
let sceneNode = null;
let sceneSteps = [];
let sceneIdx = 0;
let sceneAnswers = {};
let sceneTyping = false;
let sceneFull = "";

function sceneArt(node) {
  const t = `${node.id} ${node.eyebrow} ${node.title} ${node.speaker}`.toLowerCase();
  if (/cave|veldora|voice|sage|prologue|marsh|pond|lantern/.test(t)) return "cave";
  if (/goblin|village|forest|wolf|feast|bridge|gobta|rigurd|kijin|tempest|merchant|herbalist|shion|hakuro|benimaru|ranga|well|foundations/.test(t)) return "village";
  if (/ruin|relic|library|orc|demon|walpurgis|clayman|falmuth|dwarf|dwargon|kaijin|gazel|harvest|diablo|invasion|reckoning/.test(t)) return "ruins";
  return "hall";
}
const faceFor = (speaker) => (speaker === "You" ? heroArt(1, 0, 84) : creature(speaker, { size: 84 }));
const pathChips = (traits) => Object.entries(traits || {}).map(([k, v]) => `<span class="tag violet">${esc(state?.paths?.[k]?.name || cap(k))} +${v}</span>`).join("");

function maybeShowScene() {
  if (overlayMode || !state?.pending_choice) return;
  showScene(state.pending_choice);
}
function showScene(node) {
  overlayMode = "scene";
  sceneNode = node;
  sceneAnswers = {};
  sceneSteps = [...(node.beats || []), { kind: "main" }];
  sceneIdx = 0;
  sound("story");
  overlayEl.className = "overlay bare";
  overlayEl.hidden = false;
  overlayEl.innerHTML = `
    <div class="scene" role="dialog" aria-modal="true" aria-label="${esc(node.title)}">
      <div class="scene-art">${Art.scene(sceneArt(node))}</div>
      <div class="scene-body"><div class="scene-card">
        <div class="scene-top"><p class="kicker">${esc(node.eyebrow)}</p><h2>${esc(node.title)}</h2></div>
        <div class="speaker"><div class="face" id="face"></div><p class="who" id="who"></p><span class="step-count" id="step-count"></span></div>
        <div class="dialog" id="dlg"><span id="dlg-text"></span><span class="skip" id="dlg-skip">Click or press Space to skip</span></div>
        <div class="options" id="opts" hidden></div>
        <div class="btn-row" id="next-row" hidden><button class="btn primary" id="scene-next">Continue</button></div>
      </div></div>
    </div>`;
  renderStep();
}
function typeText(text, done) {
  clearInterval(typeTimer);
  const el = $("#dlg-text");
  const skip = $("#dlg-skip");
  sceneFull = text;
  sceneTyping = true;
  skip.hidden = false;
  let n = 0;
  const finish = () => {
    clearInterval(typeTimer);
    el.textContent = text;
    sceneTyping = false;
    skip.hidden = true;
    done();
  };
  sceneFinish = finish;
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) { finish(); return; }
  el.textContent = "";
  typeTimer = setInterval(() => {
    n += 2;
    el.textContent = text.slice(0, n);
    if (n % 6 === 0) sound("type");
    if (n >= text.length) finish();
  }, 20);
}
let sceneFinish = () => {};
function renderStep() {
  const step = sceneSteps[sceneIdx];
  if (!step) { closeOverlay(); return; }
  const opts = $("#opts");
  const nextRow = $("#next-row");
  opts.hidden = true;
  nextRow.hidden = true;
  opts.innerHTML = "";
  $("#step-count").textContent = `${sceneIdx + 1} / ${sceneSteps.length}`;
  const speaker = step.kind === "main" ? sceneNode.speaker : step.kind === "result" ? "Result" : step.speaker;
  $("#who").textContent = step.kind === "result" ? "What changes" : speaker;
  $("#face").innerHTML = step.kind === "result" ? icon("sparkle", 44) : faceFor(speaker);
  const dlg = $("#dlg");
  dlg.classList.toggle("outcome", step.kind === "result");
  if (step.kind === "result") {
    typeText(step.text, () => {
      dlg.insertAdjacentHTML("beforeend", step.chips ? `<span class="chips" style="margin-top:12px;display:flex">${step.chips}</span>` : "");
      nextRow.hidden = false;
      $("#scene-next").dataset.close = "";
      $("#scene-next").textContent = "Continue";
      $("#scene-next").focus({ preventScroll: true });
    });
    return;
  }
  dlg.querySelectorAll(".chips").forEach((c) => c.remove());
  if (step.kind === "main") {
    typeText(sceneNode.text, () => {
      opts.innerHTML = sceneNode.options.map((o, i) => o.locked
        ? `<button class="option locked" disabled><span class="n">${icon("lock", 16)}</span><span><strong>${esc(o.label)}</strong><span class="d">${esc(o.hint || "Not open to you yet.")}</span></span></button>`
        : `<button class="option" data-choice="${esc(o.id)}" style="animation-delay:${i * 80}ms"><span class="n">${i + 1}</span><span><strong>${esc(o.label)}</strong><span class="d">${esc(o.description)}</span></span></button>`).join("");
      opts.hidden = false;
      $(".option:not(.locked)", opts)?.focus({ preventScroll: true });
    });
  } else if (step.ask) {
    typeText(step.text, () => {
      opts.innerHTML = step.options.map((o, i) => `<button class="option" data-ask="${esc(step.ask)}" data-ask-opt="${esc(o.id)}" style="animation-delay:${i * 80}ms"><span class="n">${i + 1}</span><span><strong>${esc(o.label)}</strong></span></button>`).join("");
      opts.hidden = false;
      $(".option", opts)?.focus({ preventScroll: true });
    });
  } else {
    typeText(step.text, () => { nextRow.hidden = false; $("#scene-next").focus({ preventScroll: true }); });
  }
}
function advanceScene() {
  if (sceneTyping) { sceneFinish(); return; }
  if (!$("#next-row").hidden) {
    sceneIdx += 1;
    sound("click");
    renderStep();
  }
}
function answerAsk(askId, optId) {
  const step = sceneSteps[sceneIdx];
  const opt = step.options.find((o) => o.id === optId);
  sceneAnswers[askId] = optId;
  sceneSteps.splice(sceneIdx + 1, 0, ...(opt.lines || []));
  sound("click");
  sceneIdx += 1;
  renderStep();
}
async function chooseOption(id) {
  const node = sceneNode;
  const option = node.options.find((o) => o.id === id);
  if (!option || option.locked) return;
  $$("#opts .option").forEach((b) => (b.disabled = true));
  const ok = await act("/api/choice", { choice: id, beats: sceneAnswers }, { sfx: "good" });
  if (!ok) { $$("#opts .option:not(.locked)").forEach((b) => (b.disabled = false)); return; }
  overlayMode = "scene";
  const gains = {};
  const add = (t) => Object.entries(t || {}).forEach(([k, v]) => (gains[k] = (gains[k] || 0) + v));
  node.beats.filter((b) => b.ask && sceneAnswers[b.ask]).forEach((b) => add(b.options.find((o) => o.id === sceneAnswers[b.ask])?.traits));
  add(option.traits);
  sceneSteps = [
    { speaker: node.speaker, text: option.reply },
    ...(option.aftermath || []),
    { kind: "result", text: option.result, chips: pathChips(gains) },
  ];
  sceneIdx = 0;
  renderStep();
}

/* ---------------------------------------------------------------- live updates (progress bars, countdowns) */
function live() {
  const t = nowSec();
  for (const el of $$("[data-t1]")) {
    const t0 = +el.dataset.t0, t1 = +el.dataset.t1;
    el.style.width = `${Math.max(0, Math.min(1, (t - t0) / Math.max(0.001, t1 - t0))) * 100}%`;
  }
  for (const el of $$("[data-remain-to]")) {
    const text = Math.max(0, Math.ceil(+el.dataset.remainTo - t)) + "s";
    if (el.textContent !== text) el.textContent = text;
  }
  for (const el of $$("[data-cd-to]")) {
    const left = Math.ceil(+el.dataset.cdTo - t);
    if (left > 0) { const text = left + "s"; if (el.textContent !== text) el.textContent = text; el.disabled = true; }
    else if (el.disabled && el.dataset.afford === "1") { el.disabled = false; el.textContent = "Use now"; el.removeAttribute("data-cd-to"); }
  }
  const f = $("[data-focus-next]");
  if (f && state?.focus < state?.max_focus) {
    const every = state.focus_recovery_seconds;
    const last = state._last_focus_tick || t;
    const left = Math.max(0, Math.ceil(every - ((t - last) % every)));
    const text = `+1 in ${left}s`;
    if (f.textContent !== text) f.textContent = text;
  } else if (f && f.textContent) f.textContent = "";
  requestAnimationFrame(live);
}

function scheduleWake() {
  clearTimeout(wakeTimer);
  const s = state;
  if (!s?.started) return;
  const times = [];
  if (s.activity) times.push(s.activity.ends_at);
  Object.values(s.loop_state || {}).forEach((l) => times.push(l.next_tick));
  (s.instant_actions || []).forEach((a) => { if (a.cooldown_remaining > 0) times.push(nowSec() + a.cooldown_remaining); });
  if (!times.length) return;
  const next = Math.min(...times);
  wakeTimer = setTimeout(refreshState, Math.max(300, (next - nowSec()) * 1000 + 250));
}

/* ---------------------------------------------------------------- input */
const HANDLERS = {
  begin: () => act("/api/new-game", { character: "rimuru" }, { sfx: "story" }),
  go: (el) => { tab = el.dataset.tab; if (tab !== "battle") store.set("tab", tab); menuOpen = false; paint(); $("#stage")?.scrollTo({ top: 0 }); },
  action: (el) => act("/api/action", { action: el.dataset.id, count: +el.dataset.count }),
  cancel: () => act("/api/action/cancel"),
  repeat: (el) => act("/api/action/auto", { action: el.dataset.id }, { sfx: "good" }),
  autozone: (el) => { autoDungeon = autoDungeon === el.dataset.id ? null : el.dataset.id; sound("click"); paint(); },
  "loop-start": (el) => act("/api/loop/start", { action: el.dataset.id }, { sfx: "good" }),
  "loop-stop": (el) => act("/api/loop/stop", { action: el.dataset.id }),
  instant: (el) => act("/api/instant", { action: el.dataset.id }, { sfx: "good" }),
  upgrade: (el) => act("/api/upgrade", { action: el.dataset.id }, { sfx: "good" }),
  next: (el) => act("/api/next", { action: el.dataset.id }, { sfx: "story" }),
  party: (el) => act("/api/party/toggle", { ally: el.dataset.id }),
  summon: (el) => act("/api/summon", { ally: el.dataset.id }, { sfx: "good" }),
  "sin-unlock": (el) => act("/api/sin/unlock", { sin: el.dataset.id }, { sfx: "good" }),
  "sin-level": (el) => act("/api/sin/level", { sin: el.dataset.id }, { sfx: "good" }),
  astral: (el) => act("/api/astral", { upgrade: el.dataset.id }, { sfx: "good" }),
  rest: () => act("/api/rest", {}, { sfx: "good" }),
  zone: (el) => act("/api/combat/start", { zone: el.dataset.id }, { sfx: "hit" }),
  story: (el) => act("/api/story/start", { node: el.dataset.id }),
  skill: (el) => useSkill(el.dataset.id),
  foe: (el) => { const i = +el.dataset.i; if (state.battle.enemies[i]?.hp > 0) { selectedFoe = i; sound("click"); paint(); } },
  sound: () => { muted = !muted; store.set("muted", muted); if (!muted) sound("click"); paint(); },
  menu: () => { menuOpen = !menuOpen; paint(); },
  flee: async () => {
    if (await confirmDialog({ title: "Withdraw from the expedition?", body: "Rewards you have already earned are kept, but you will have to start the expedition again.", ok: "Withdraw", danger: true })) {
      auto = false; syncAuto(); act("/api/combat/flee");
    }
  },
  newgame: async () => {
    menuOpen = false; paint();
    if (await confirmDialog({ title: "Erase this chronicle?", body: "This deletes your local save and returns you to the title screen. It cannot be undone.", ok: "Erase and restart", danger: true })) {
      prev = null; eventsPrimed = false; playedEvents.clear(); tab = "actions";
      await act("/api/reset", {});
    }
  },
  ritual: async () => {
    const r = state.dark_ritual;
    if (await confirmDialog({ title: "Perform the Dark Ritual?", body: `You return to level 1 with base stats and no resources, loops or upgrades. You gain ${r.habit_gain} Habit Points and ${r.inspiration_gain} Inspiration. Allies, story and Astral upgrades stay.`, ok: "Perform the ritual", danger: true })) act("/api/ritual", {}, { sfx: "level" });
  },
  reincarnate: async (el) => {
    if (await confirmDialog({ title: `Reincarnate as a ${el.dataset.name}?`, body: "You start over at level 1 with class bonuses. Allies and bonds are lost. Astral upgrades, Habit Points, Inspiration and story progress stay.", ok: "Reincarnate", danger: true })) act("/api/reincarnate", { class: el.dataset.id }, { sfx: "level" });
  },
};
document.addEventListener("click", (ev) => {
  const choice = ev.target.closest("[data-choice]");
  if (choice) { chooseOption(choice.dataset.choice); return; }
  const ask = ev.target.closest("[data-ask-opt]");
  if (ask) { answerAsk(ask.dataset.ask, ask.dataset.askOpt); return; }
  if (ev.target.closest("#scene-next")) { if (sceneSteps[sceneIdx]?.kind !== "result") advanceScene(); return; }
  if (ev.target.closest("#dlg") && sceneTyping) { sceneFinish(); return; }
  const el = ev.target.closest("[data-act]");
  if (!el || el.tagName === "INPUT" || el.disabled || el.classList.contains("is-off")) {
    if (menuOpen && !ev.target.closest(".menu-wrap")) { menuOpen = false; paint(); }
    return;
  }
  const fn = HANDLERS[el.dataset.act];
  if (fn) fn(el);
});
document.addEventListener("change", (ev) => {
  const el = ev.target.closest('[data-act="auto"]');
  if (!el) return;
  auto = el.checked;
  syncAuto();
  sound("click");
});
document.addEventListener("keydown", (ev) => {
  if (ev.target.closest("input, textarea")) return;
  if (ev.key === "Escape" && menuOpen) { menuOpen = false; paint(); return; }
  if ((ev.key === "Enter" || ev.key === " ") && ev.target.matches?.('[role="button"][data-act]')) { ev.preventDefault(); ev.target.click(); return; }
  if (overlayMode === "scene") {
    if (ev.key === " " || ev.key === "Enter") {
      if (sceneTyping) { ev.preventDefault(); sceneFinish(); }
      else if (!$("#next-row").hidden && sceneSteps[sceneIdx]?.kind !== "result") { ev.preventDefault(); advanceScene(); }
      return;
    }
    const n = Number(ev.key);
    if (n >= 1 && n <= 9 && !$("#opts").hidden) { const opt = $$("#opts .option")[n - 1]; if (opt && !opt.disabled) opt.click(); }
    return;
  }
  if (overlayMode) return;
  if (state?.battle && tab === "battle") {
    const n = Number(ev.key);
    if (n >= 1 && n <= state.skills.length) {
      const k = state.skills[n - 1];
      if (k.unlocked && state.mana >= k.mana) useSkill(k.id);
    }
  }
});

/* ---------------------------------------------------------------- boot */
async function boot() {
  try {
    setState(await api("/api/state"));
    requestAnimationFrame(live);
    setInterval(refreshState, 4000);
  } catch (error) {
    app.innerHTML = `<section class="boot error"><div class="boot-orb"></div><p><strong>The game server is asleep.</strong><br>${esc(error.message)}<br>Run <code>python server.py</code> and reload.</p></section>`;
  }
}
window.addEventListener("DOMContentLoaded", boot);
