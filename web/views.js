"use strict";
/* Views: pure HTML builders for the Your Chronicle style layout. They read the globals declared in app.js. */

const meter = (value, max, cls = "") => `<div class="meter ${cls}"><i style="width:${pct(value, max)}%"></i></div>`;
const bar = (label, value, max, cls, extra = "") => `<div class="bar-row"><div><span>${esc(label)}${extra}</span><b class="num">${fmt(value)} / ${fmt(max)}</b></div>${meter(value, max, cls)}</div>`;

/* ---------------------------------------------------------------- top bar, status, tabs, log */
function topHTML() {
  const s = state;
  const [, name, chap] = JOURNEY[phaseIndex(s.story_phase)] || ["", "The chronicle", ""];
  return `
    <div class="brand"><span class="brand-mark">CR</span><span class="name">Chronicles of Reincarnation</span></div>
    <div class="objective" title="${esc(s.story_objective)}"><span class="obj-label">${esc(chap)}${chap ? " · " : ""}${esc(name)}</span><span class="obj-text">${esc(s.story_objective)}</span></div>
    <div class="obj-pct" title="Chapter progress"><div class="meter thin"><i style="width:${s.chronicle_progress}%"></i></div><b class="num">${s.chronicle_progress}%</b></div>
    <div class="top-right">
      <button class="iconbtn" data-act="sound" aria-label="${muted ? "Turn sound on" : "Turn sound off"}" title="Sound">${icon(muted ? "mute" : "sound")}</button>
      <div class="menu-wrap">
        <button class="iconbtn" data-act="menu" aria-label="Menu" aria-expanded="${menuOpen}">${icon("menu")}</button>
        ${menuOpen ? `<div class="menu" role="menu"><button data-act="newgame" role="menuitem">${icon("close", 18)}<span>New chronicle (erases this save)</span></button></div>` : ""}
      </div>
    </div>`;
}

function sideHTML() {
  const s = state;
  const kv = (label, value, extra = "") => `<div ${extra}><dt>${label}</dt><dd class="num">${value}</dd></div>`;
  const resRows = Object.entries(RES).map(([k, r]) => `<div class="res-row ${r.cls}" data-res="${k}"><dt>${icon(r.icon, 16)}${r.label}</dt><dd class="num">${fmt(s[k])}</dd></div>`).join("");
  const extraRes = [s.habit_points ? kv("Habit Points", fmt(s.habit_points)) : "", s.inspiration ? kv("Inspiration", fmt(s.inspiration)) : ""].join("");
  const peak = Math.max(10, ...Object.values(s.traits));
  const paths = Object.entries(s.paths).map(([k, p]) => `<div class="path-row ${s.dominant_path === k ? "lead" : ""}" title="${esc(p.blurb)}"><span>${esc(p.name)}</span>${meter(s.traits[k], peak, "thin")}<b class="num">${s.traits[k]}</b></div>`).join("");
  const rest = !s.dungeon_run && s.gold >= s.rest_cost && (s.hp < s.max_hp || s.mana < s.max_mana);
  return `
    <section class="panel who-card">
      <div class="who-art">${heroArt(s.level, s.reincarnations, 52)}</div>
      <div class="who-text"><h2>Rimuru</h2><div class="muted">${esc(s.hero.title)}</div><div class="muted">${esc(s.alignment)}${s.reincarnation_class ? " · " + esc(cap(s.reincarnation_class)) : ""}</div></div>
      <div class="who-lvl"><span>Level <b>${s.level}</b></span><span class="num muted">${fmt(s.xp)} / ${fmt(s.xp_next)} XP</span></div>
      ${meter(s.xp, s.xp_next, "xp thin")}
    </section>
    <section class="panel"><h3>Vitals</h3>
      ${bar("Vitality", s.hp, s.max_hp, "hp")}${bar("Mana", s.mana, s.max_mana, "mp")}${bar("Focus", s.focus, s.max_focus, "focus", ` <span class="muted" data-focus-next></span>`)}
      <button class="btn sm block" data-act="rest" ${rest ? "" : "disabled"}>${icon("moon", 16)} Rest · ${s.rest_cost} gold</button>
    </section>
    <section class="panel"><h3>Status</h3><dl class="kv">${kv("Attack", s.attack)}${kv("Defense", s.defense)}${kv("Speed", s.speed)}${kv("Party bonus", `+${s.party_bonus.attack} / +${s.party_bonus.defense}`)}</dl></section>
    <section class="panel"><h3>Resources</h3><dl class="kv">${resRows}${extraRes}</dl></section>
    <section class="panel"><h3>Path <span class="muted">${s.dominant_path ? esc(s.paths[s.dominant_path].name) : "unwritten"}</span></h3>${paths}</section>`;
}

const NAV = [
  ["actions", "Action", "clock"], ["loops", "Loop", "infinity"], ["instant", "Instant", "bolt"], ["upgrades", "Upgrade", "up"], null,
  ["expeditions", "Dungeon", "map"], ["companions", "Monster", "people"], ["sins", "Sin", "skull"], null,
  ["story", "Story", "book"], ["journey", "Journey", "flag"], ["ascension", "Rebirth", "crown"],
];
function badge(id) {
  const s = state;
  switch (id) {
    case "story": return s.available_stories.length ? `<span class="count">${s.available_stories.length}</span>` : "";
    case "journey": { const n = nextCheckpoint(); return n && n.ready ? `<span class="count">!</span>` : ""; }
    case "upgrades": { const n = s.upgrade_actions.filter((u) => canAfford(u.cost) && !upgradeMaxed(u)).length; return n ? `<span class="count soft">${n}</span>` : ""; }
    case "companions": { const n = s.summonable_allies.filter((a) => a.can_afford).length; return n ? `<span class="count">${n}</span>` : ""; }
    case "loops": { const n = Object.keys(s.loop_state || {}).length; return n ? `<span class="count soft">${n}</span>` : ""; }
    case "actions": { const n = (s.action_queue || []).reduce((t, q) => t + q.count, 0) + (s.activity ? 1 : 0); return n ? `<span class="count soft">${n}</span>` : ""; }
    default: return "";
  }
}
function tabsHTML() {
  const items = NAV.map((n, i) => n === null ? `<span class="tab-sep" data-key="sep-${i}"></span>`
    : `<button class="tab" data-act="go" data-tab="${n[0]}" data-key="tab-${n[0]}" ${tab === n[0] ? 'aria-current="page"' : ""}>${n[1]}${badge(n[0])}</button>`).join("");
  const battle = state.battle ? `<button class="tab battle" data-act="go" data-tab="battle" data-key="tab-battle" ${tab === "battle" ? 'aria-current="page"' : ""}>${icon("swords", 16)} Battle</button><span class="tab-sep" data-key="sep-b"></span>` : "";
  return battle + items;
}
function logHTML() {
  const lines = [...state.log].reverse().map((e) => {
    const t = new Date(e.time * 1000).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit", hour12: false });
    return `<div class="log-line ${esc(e.kind)} ${e.text.startsWith("Auto:") ? "dim" : ""}"><time>${t}</time><span>${esc(e.text)}</span></div>`;
  }).join("");
  return `<div class="panel-head"><h3>Chronicle</h3><span class="muted">newest first</span></div><div class="log-scroll">${lines}</div>`;
}

/* ---------------------------------------------------------------- shared bits */
const hasDoppel = () => (state.astral_upgrades || []).find((u) => u.id === "doppelganger")?.level > 0;
const pageHead = (title, hint, aside = "") => `<div class="page-head"><div><h2>${esc(title)}</h2><p>${esc(hint)}</p></div>${aside ? `<div class="aside">${aside}</div>` : ""}</div>`;
const canAfford = (cost = {}) => Object.entries(cost).every(([k, v]) => (state[k] || 0) >= v);
const costText = (cost = {}) => Object.entries(cost).map(([k, v]) => `<span class="cost ${(state[k] || 0) >= v ? "ok" : "short"}">${fmt(v)} ${resLabel(k)}</span>`).join("");
const rw = (list) => list.filter(Boolean).map(([cls, text]) => `<span class="rw ${cls}">${esc(text)}</span>`).join("");
const empty = (title, text) => `<div class="empty"><strong>${esc(title)}</strong>${esc(text)}</div>`;
const lockedOf = (type) => (state.locked_actions || []).filter((a) => a.type === type).sort((x, y) => x.unlock_level - y.unlock_level).slice(0, 3);
const teaser = (a) => `<div class="row locked" data-key="t-${a.id}"><div class="row-ico">${icon("lock", 18)}</div><div class="row-main"><div class="row-name">${esc(a.name)}</div><div class="row-desc">${esc(a.description)}</div></div><div class="row-info"></div><div class="row-act"><span class="muted">Level ${a.unlock_level}</span></div></div>`;
const upgradeMaxed = (u) => (u.effect.party_slots && state.max_party_slots >= 5) || (u.effect.passive_slots && state.max_passive_slots >= 4);

/** One line in a list: icon, name, small text, numbers, and a button. A `fill` is a live progress bar behind the row. */
function row({ key, ico, name, sub = "", desc = "", info = "", act = "", cls = "", fill = "", attrs = "" }) {
  return `<div class="row ${cls}" data-key="${key}" ${attrs}>${fill}<div class="row-ico">${ico}</div><div class="row-main"><div class="row-name">${name}</div>${sub ? `<div class="row-sub">${sub}</div>` : ""}${desc ? `<div class="row-desc">${esc(desc)}</div>` : ""}</div><div class="row-info">${info}</div><div class="row-act">${act}</div></div>`;
}
const fillBar = (t0, t1, now = 0) => `<i class="fill" data-t0="${t0}" data-t1="${t1}" style="width:${now}%"></i>`;

function stageHTML() {
  if (tab === "battle" && state.battle) return `<div class="page">${arenaHTML()}</div>`;
  const pages = { actions: actionsPage, loops: loopsPage, instant: instantPage, upgrades: upgradesPage, companions: companionsPage, sins: sinsPage, expeditions: expeditionsPage, story: storyPage, journey: journeyPage, ascension: ascensionPage };
  const waiting = state.available_stories[0];
  const callout = waiting && tab !== "story" ? `<div class="callout" data-key="callout">${icon("book", 18)}<span>A conversation is waiting: <b>${esc(waiting.title)}</b></span><button class="btn sm" data-act="go" data-tab="story">Open Story</button></div>` : "";
  return `<div class="page">${callout}${(pages[tab] || actionsPage)()}</div>`;
}

/* ---------------------------------------------------------------- Action */
function actionsPage() {
  const s = state;
  const queued = (id) => (s.action_queue || []).filter((q) => q.id === id).reduce((t, q) => t + q.count, 0);
  const blocked = !!s.battle || !!s.pending_story;
  const rows = s.actions.map((a) => {
    const running = s.activity?.action_id === a.id;
    const unit = a.cost_type === "mana" ? "Mana" : "Focus";
    const short = s[a.cost_type || "focus"] < a.cost;
    const q = queued(a.id);
    const repeat = s.auto_action === a.id;
    const traits = Object.entries(a.traits || {}).map(([k, v]) => `<span class="rw r-path">${esc(s.paths[k].name)} +${v}</span>`).join("");
    const info = rw([["r-xp", `+${a.xp} XP`], a.resource ? ["r-mag", `+${a.resource} ${s.resource_label}`] : null, a.insight ? ["r-ins", `+${a.insight} Insight`] : null, a.heal ? ["r-hp", `+${a.heal} HP`] : null]) + traits;
    const sub = `${a.duration}s · <span class="${short ? "short" : ""}">${a.cost} ${unit}</span>${a.training ? ` · trains ${a.training === "attack" ? "Attack" : "Mana"}` : ""}${a.party_training ? " · needs an ally" : ""}${q ? ` · <span class="queue-pill">${q}</span> queued` : ""}`;
    const act = `${running ? `<span class="num remain"><b data-remain-to="${s.activity.ends_at}">${Math.ceil(s.activity.remaining)}s</b></span><button class="btn sm danger" data-act="cancel" title="Cancel and refund">${icon("close", 14)}</button>`
      : `<button class="btn sm ${repeat ? "on" : "ghost"}" data-act="repeat" data-id="${a.id}" title="Repeat this action automatically" aria-pressed="${repeat}">${icon("infinity", 16)}</button><button class="btn sm" data-act="action" data-id="${a.id}" data-count="5" ${short || blocked ? "disabled" : ""}>×5</button><button class="btn sm" data-act="action" data-id="${a.id}" data-count="10" ${short || blocked ? "disabled" : ""}>×10</button>`}`;
    return row({
      key: `a-${a.id}`, ico: tile(a.id), name: esc(a.name), sub, desc: a.description, info, act,
      cls: `${running ? "is-running" : ""} ${short || blocked ? "is-off" : "is-click"} ${repeat ? "is-repeat" : ""}`,
      fill: running ? fillBar(s.activity.started_at, s.activity.ends_at, s.activity.progress) : "",
      attrs: short || blocked || running ? "" : `role="button" tabindex="0" data-act="action" data-id="${a.id}" data-count="1"`,
    });
  }).join("");
  return `${pageHead("Action", "Click an action to run it. Mental work spends Mana (loops restore it), the rest spends Focus. Use ∞ to repeat one for you.", `Focus ${s.focus}/${s.max_focus} · Mana ${s.mana}/${s.max_mana}`)}<div class="rows">${rows || empty("Nothing to do yet", "Answer the voice in your mind to discover your first actions.")}</div>`;
}

/* ---------------------------------------------------------------- Loop */
function loopsPage() {
  const s = state;
  const blocked = !!s.dungeon_run && !hasDoppel();
  const rows = s.loops.map((l) => {
    const rt = (s.loop_state || {})[l.id];
    const info = rw([
      l.magicules ? ["r-mag", `+${l.magicules} Magicules`] : null, l.gold ? ["r-gold", `+${l.gold} Gold`] : null, l.insight ? ["r-ins", `+${l.insight} Insight`] : null,
      l.research ? ["r-res", `+${l.research} Research`] : null, l.heal ? ["r-hp", `+${l.heal} HP`] : null, l.mana_regen ? ["r-mp", `+${l.mana_regen} Mana`] : null, l.xp ? ["r-xp", `+${l.xp} XP`] : null,
    ]) + Object.entries(l.traits || {}).map(([k, v]) => `<span class="rw r-path">${esc(s.paths[k].name)} +${v}</span>`).join("");
    return row({
      key: `l-${l.id}`, ico: tile(l.id), name: esc(l.name), sub: `every ${l.interval}s${l.active ? " · running" : ""}`, desc: l.description, info,
      cls: l.active ? "is-running" : blocked ? "is-off" : "",
      fill: l.active && rt ? fillBar(rt.next_tick - l.interval, rt.next_tick) : "",
      act: l.active ? `<button class="btn sm danger" data-act="loop-stop" data-id="${l.id}">Stop</button>` : `<button class="btn sm primary" data-act="loop-start" data-id="${l.id}" ${blocked ? "disabled" : ""}>Start</button>`,
    });
  }).join("");
  const note = hasDoppel() ? "Doppelganger lets loops run during dungeons too." : "Loops run in the background beside your tasks and are how Mana comes back. They cannot be started mid-dungeon until Doppelganger.";
  return `${pageHead("Loop", note, `Running ${Object.keys(s.loop_state || {}).length}`)}<div class="rows">${rows}${lockedOf("loop").map(teaser).join("")}</div>`;
}

/* ---------------------------------------------------------------- Instant */
function instantPage() {
  const s = state;
  const rows = s.instant_actions.map((a) => {
    const costs = [a.focus_cost ? `${a.focus_cost} Focus` : "", a.gold_cost ? `${fmt(a.gold_cost)} Gold` : "", a.magicules_cost ? `${fmt(a.magicules_cost)} Magicules` : ""].filter(Boolean);
    const afford = s.focus >= (a.focus_cost || 0) && s.gold >= (a.gold_cost || 0) && s.magicules >= (a.magicules_cost || 0);
    const cd = a.cooldown_remaining > 0;
    const until = nowSec() + a.cooldown_remaining;
    const info = rw([a.magicules ? ["r-mag", `+${a.magicules} Magicules`] : null, a.gold ? ["r-gold", `+${a.gold} Gold`] : null, a.insight ? ["r-ins", `+${a.insight} Insight`] : null, a.xp ? ["r-xp", `+${a.xp} XP`] : null])
      + Object.entries(a.traits || {}).map(([k, v]) => `<span class="rw r-path">${esc(s.paths[k].name)} +${v}</span>`).join("");
    return row({
      key: `i-${a.id}`, ico: tile(a.id), name: esc(a.name), sub: `${costs.join(" + ") || "free"} · ${a.cooldown}s cooldown`, desc: a.description, info, cls: cd || !afford ? "is-off" : "",
      act: `<button class="btn sm primary" data-act="instant" data-id="${a.id}" data-afford="${afford ? 1 : 0}" ${cd ? `data-cd-to="${until}"` : ""} ${cd || !afford ? "disabled" : ""}>${cd ? a.cooldown_remaining + "s" : "Use"}</button>`,
    });
  }).join("");
  return `${pageHead("Instant", "Trade one resource for another right now. Each has a short cooldown.")}<div class="rows">${rows}${lockedOf("instant").map(teaser).join("")}</div>`;
}

/* ---------------------------------------------------------------- Upgrade */
const EFFECT = { max_hp: "Max HP", max_mana: "Max Mana", attack: "Attack", defense: "Defense", party_slots: "active party slot", passive_slots: "passive slot", unique_skill_slots: "Unique Skill slot", ultimate_skill_slots: "Ultimate Skill slot" };
function upgradesPage() {
  const s = state;
  const rows = s.upgrade_actions.map((u) => {
    const maxed = upgradeMaxed(u);
    const fx = Object.entries(u.effect).map(([k, v]) => `+${v} ${EFFECT[k] || cap(k)}`).join(", ");
    const preview = u.effect.unique_skill_slots || u.effect.ultimate_skill_slots;
    return row({
      key: `u-${u.id}`, ico: tile(u.id), name: esc(u.name), sub: `${u.purchased ? `owned ×${u.purchased}` : "not owned"}${preview ? " · reserved for future skills" : ""}`, desc: u.description,
      info: rw([["r-mag", fx]]) + costText(u.cost), cls: !canAfford(u.cost) || maxed ? "is-off" : "",
      act: `<button class="btn sm primary" data-act="upgrade" data-id="${u.id}" ${!canAfford(u.cost) || maxed ? "disabled" : ""}>${maxed ? "Max" : "Buy"}</button>`,
    });
  }).join("");
  return `${pageHead("Upgrade", "Permanent boosts. They last until the Dark Ritual or a rebirth.")}<div class="rows">${rows || (lockedOf("upgrade").length ? "" : empty("No upgrades yet", "Reach level 2 to start shaping your body."))}${lockedOf("upgrade").map(teaser).join("")}</div>`;
}

/* ---------------------------------------------------------------- Monster (party and summons) */
function companionsPage() {
  const s = state;
  const slots = `<div class="slotbar"><div><span>Active</span><b>${s.active_party.length}/${s.max_party_slots}</b></div><div><span>Passive</span><b>${s.passive_party.length}/${s.max_passive_slots}</b></div><div><span>Bonus</span><b>+${s.party_bonus.attack} ATK · +${s.party_bonus.defense} DEF</b></div><div><span>Research</span><b>${fmt(s.research)}</b></div></div>`;
  const allyRow = (a) => {
    const status = a.active ? `<span class="tag teal">Active</span>` : a.passive ? `<span class="tag violet">Passive</span>` : `<span class="tag">Reserve</span>`;
    return row({
      key: `p-${a.id}`, ico: `<span class="portrait">${creature(a.species + " " + a.name, { size: 40 })}</span>`, name: `${esc(a.name)} ${status}`, sub: `${esc(a.species)} · ${esc(a.role)} · Lv ${a.level} · bond ${a.bond}`, desc: a.support,
      info: `<span class="rw">ATK ${a.attack}</span><span class="rw">DEF ${a.defense}</span>`,
      act: `<button class="btn sm ${a.active || a.passive ? "" : "primary"}" data-act="party" data-id="${a.id}" ${s.dungeon_run ? "disabled" : ""}>${a.active ? "Bench" : a.passive ? "Remove" : "Deploy"}</button>`,
    });
  };
  const summon = [...s.summonable_allies].sort((x, y) => x.cost - y.cost);
  return `${pageHead("Monster", "Allies join through the story, by being recruited after a fight, or by Research. Active allies add Attack and Defense; passive ones add a smaller share.")}${slots}
    <div class="rows">${s.party.map(allyRow).join("") || empty("No allies yet", "Beaten monsters sometimes ask to join. Research can summon more.")}</div>
    <h3 class="subhead">Summon <span class="muted">${fmt(s.research)} Research</span></h3>
    <div class="rows">${summon.map((a) => row({
      key: `s-${a.id}`, ico: `<span class="portrait">${creature(a.species + " " + a.name, { size: 40 })}</span>`, name: esc(a.name), sub: `${esc(a.species)} · ${esc(a.role)}`,
      info: `<span class="cost ${a.can_afford ? "ok" : "short"}">${a.cost} Research</span>`, cls: a.can_afford ? "" : "is-off",
      act: `<button class="btn sm primary" data-act="summon" data-id="${a.id}" ${a.can_afford ? "" : "disabled"}>Summon</button>`,
    })).join("") || empty("Everyone has answered", "Every creature you can summon is already with you.")}</div>`;
}

/* ---------------------------------------------------------------- Sin */
function sinsPage() {
  const s = state;
  const rows = s.sins.map((x) => {
    const cost = 10 * x.level;
    const now = Math.round(x.per_level * x.level * 100);
    const next = Math.round(x.per_level * (x.level + 1) * 100);
    return row({
      key: `sin-${x.id}`, ico: tile(x.id), name: esc(x.name), sub: x.unlocked ? `level ${x.level} · +${now}% now, +${next}% next` : `unlocks at level ${x.unlock_level}`, desc: x.description,
      info: x.unlocked ? `<span class="cost ${s.magicules >= cost ? "ok" : "short"}">${fmt(cost)} Magicules</span>` : "", cls: x.unlocked ? "is-running" : x.can_unlock ? "" : "locked",
      act: x.unlocked ? `<button class="btn sm primary" data-act="sin-level" data-id="${x.id}" ${s.magicules >= cost ? "" : "disabled"}>Strengthen</button>` : `<button class="btn sm primary" data-act="sin-unlock" data-id="${x.id}" ${x.can_unlock ? "" : "disabled"}>Awaken</button>`,
    });
  }).join("");
  return `${pageHead("Sin", "Awaken a sin to amplify one kind of gain. Each level costs more Magicules than the last.")}<div class="rows">${rows}</div>`;
}

/* ---------------------------------------------------------------- Dungeon */
function expeditionsPage() {
  const s = state;
  const lowHp = s.hp < s.max_hp * 0.5;
  const pausing = !!s.activity && !hasDoppel();
  const zones = [...s.zones].sort((a, b) => Number(b.unlocked) - Number(a.unlocked));
  const rows = zones.map((z) => {
    const pips = Array.from({ length: z.total_encounters }, (_, i) => `<i class="${i === z.total_encounters - 1 ? "boss on" : "on"}"></i>`).join("");
    const rep = autoDungeon === z.id;
    return row({
      key: `z-${z.id}`, ico: `<span class="portrait">${z.unlocked ? creature(z.boss, { size: 40 }) : icon("lock", 20)}</span>`, name: esc(z.name), sub: z.unlocked ? `boss ${esc(z.boss)} · cleared ${z.runs}×${z.runs ? ` · enemies ×${(1 + z.runs * 0.08).toFixed(2)}` : ""}` : "opens as the story unfolds", desc: z.unlocked ? z.subtitle : "",
      info: `<div class="pips">${pips}</div>`, cls: z.unlocked ? "" : "locked",
      act: z.unlocked ? `<button class="btn sm ${rep ? "on" : "ghost"}" data-act="autozone" data-id="${z.id}" title="Run this dungeon again and again" aria-pressed="${rep}">${icon("infinity", 16)}</button><button class="btn sm primary" data-act="zone" data-id="${z.id}" ${s.battle ? "disabled" : ""}>Enter</button>` : `<span class="muted">Sealed</span>`,
    });
  }).join("");
  return `${pageHead("Dungeon", "Battles run automatically. Step in to choose skills and targets, or let them play. Enemies grow 8% tougher with each clear. ∞ repeats a dungeon.", `${s.total_victories} victories · ${s.total_runs} cleared`)}
    ${pausing ? `<div class="callout">${icon("clock", 18)}<span>${esc(s.activity.name)} will pause while you are in a dungeon and its cost is refunded.</span></div>` : ""}
    ${lowHp ? `<div class="callout danger">${icon("heart", 18)}<span>Vitality is ${s.hp} of ${s.max_hp}. Rest first.</span><button class="btn sm" data-act="rest">Rest · ${s.rest_cost} gold</button></div>` : ""}
    <div class="rows">${rows}</div>`;
}

/* ---------------------------------------------------------------- Story */
function storyPage() {
  const s = state;
  const bonds = Object.entries(s.friendships || {});
  const top = Math.max(10, ...bonds.map(([, v]) => Math.abs(v)));
  const branches = Object.values(s.branches || {});
  const waiting = s.available_stories.map((n) => row({
    key: `st-${n.id}`, ico: `<span class="tile tone-gold">${icon("speech", 20)}</span>`, name: esc(n.title), sub: `${esc(n.eyebrow)} · ${esc(n.speaker)}`, desc: n.text.length > 170 ? n.text.slice(0, 167) + "..." : n.text,
    act: `<button class="btn sm gold" data-act="story" data-id="${n.id}" ${s.battle ? "disabled" : ""} title="${s.battle ? "Finish the dungeon first" : s.activity ? "Your task pauses and its cost is refunded" : ""}">Begin</button>`,
  })).join("");
  return `${pageHead("Story", "Conversations shape who follows you. What you do between them decides which ones open.")}
    <h3 class="subhead">Waiting <span class="muted">${s.available_stories.length}</span></h3>
    <div class="rows">${waiting || empty("No conversations waiting", "New ones appear as you explore, fight and grow. The Journey tab shows the next checkpoint.")}</div>
    ${bonds.length ? `<h3 class="subhead">Bonds</h3><div class="stack">${bonds.map(([k, v]) => `<div class="bond-row"><span>${esc(FRIENDS[k] || cap(k))}</span>${meter(Math.max(0, v), top, v < 0 ? "hp thin" : "thin")}<b class="num">${v > 0 ? "+" : ""}${v}</b></div>`).join("")}</div>` : ""}
    ${branches.length ? `<h3 class="subhead">Your choices</h3><div class="chips">${branches.map((b) => `<span class="tag gold">${esc(b)}</span>`).join("")}</div>` : ""}
    <h3 class="subhead">Past conversations <span class="muted">${s.story_history.length}</span></h3>
    <div class="stack">${[...s.story_history].reverse().map((h) => `<div class="quote"><span class="who">${esc(h.speaker)}</span><span class="did">You chose: ${esc(h.choice)}</span><span class="said">${esc(h.reply)}</span></div>`).join("") || `<p class="muted">Nothing yet.</p>`}</div>`;
}

/* ---------------------------------------------------------------- Journey */
function nextCheckpoint() {
  const s = state;
  const here = phaseIndex(s.story_phase);
  const list = s.next_actions.filter((a) => !a.completed && phaseIndex(a.story_phase) > here).sort((x, y) => phaseIndex(x.story_phase) - phaseIndex(y.story_phase));
  const a = list[0];
  return a ? { ...a, ready: a.can_afford && s.level >= a.unlock_level } : null;
}
function journeyPage() {
  const s = state;
  const here = phaseIndex(s.story_phase);
  const next = nextCheckpoint();
  const rows = JOURNEY.map(([phase, name, chap], i) => {
    const cp = s.next_actions.find((a) => a.story_phase === phase);
    const state_ = i < here ? "done" : i === here ? "now" : "future";
    const mark = state_ === "done" ? icon("check", 18) : state_ === "now" ? icon("flag", 18) : icon("lock", 16);
    const isNext = cp && next && next.id === cp.id;
    const lvlShort = cp && s.level < cp.unlock_level;
    return row({
      key: `j-${phase}`, ico: `<span class="tile ${state_ === "done" ? "tone-teal" : state_ === "now" ? "tone-gold" : ""}">${mark}</span>`, name: esc(name), sub: `${esc(chap)}${state_ === "now" ? " · you are here" : ""}`,
      desc: state_ === "now" ? s.story_objective : cp && i > here ? cp.description : "",
      info: cp && i > here ? costText(cp.cost) + `<span class="muted">level ${cp.unlock_level}</span>` : "", cls: state_ === "done" ? "is-done" : state_ === "future" ? (isNext ? "" : "locked") : "is-running",
      act: cp && i > here ? `<button class="btn sm primary" data-act="next" data-id="${cp.id}" ${isNext && cp.can_afford && !lvlShort ? "" : "disabled"}>${isNext ? "Complete" : "Later"}</button>` : "",
    });
  }).join("");
  return `${pageHead("Journey", "The main story, chapter by chapter. Checkpoints cost resources and open the next regions and conversations.", `${s.chronicle_progress}% of this chapter`)}<div class="rows">${rows}</div>`;
}

/* ---------------------------------------------------------------- Rebirth */
function ascensionPage() {
  const s = state;
  const r = s.dark_ritual;
  const bonus = Math.round(2 * s.habit_points);
  const astral = s.astral_upgrades.map((u) => row({
    key: `as-${u.id}`, ico: tile(u.id), name: esc(u.name), sub: `<span class="astral-pips">${Array.from({ length: u.max_level }, (_, i) => `<i class="${i < u.level ? "on" : ""}"></i>`).join("")}</span>`, desc: u.description,
    info: `<span class="cost ${u.can_afford ? "ok" : "short"}">${u.cost} Inspiration</span>`, cls: u.maxed || !u.can_afford ? "is-off" : "",
    act: `<button class="btn sm primary" data-act="astral" data-id="${u.id}" ${u.maxed || !u.can_afford ? "disabled" : ""}>${u.maxed ? "Max" : "Awaken"}</button>`,
  })).join("");
  const classes = Object.entries(s.reincarnation_classes).map(([id, c]) => row({
    key: `rc-${id}`, ico: tile(id), name: esc(c.name), sub: s.reincarnation_class === id ? "your class" : `+${Object.entries(c.per_reincarnation).map(([k, v]) => `${v} ${EFFECT[k] || cap(k)}`).join(", ")} per rebirth`, desc: c.description,
    info: rw(Object.entries(c.base_bonus).map(([k, v]) => ["r-mag", `+${v} ${EFFECT[k] || cap(k)}`])), cls: s.reincarnation_class === id ? "is-running" : "",
    act: `<button class="btn sm danger" data-act="reincarnate" data-id="${id}" data-name="${esc(c.name)}" ${s.can_reincarnate && !s.dungeon_run && !s.activity ? "" : "disabled"}>${s.can_reincarnate ? "Reincarnate" : "Level 10"}</button>`,
  })).join("");
  return `${pageHead("Rebirth", "Reset on purpose to grow faster. The Dark Ritual is a soft reset; Reincarnation is deeper and starts you over as a chosen class.", `${s.habit_points} Habit · ${s.inspiration} Inspiration${s.reincarnations ? ` · reborn ×${s.reincarnations}` : ""}`)}
    <div class="rows">${row({
      key: "ritual", ico: `<span class="tile tone-gold">${icon("flame", 22)}</span>`, name: "Dark Ritual", sub: "soft reset", desc: `${r.description} Resets level, stats, resources, upgrades and loops. Keeps allies, story, Habit Points, Inspiration and Astral upgrades. Each Habit Point adds 2% to Magicule, Gold and XP gains (now +${bonus}%).`,
      info: `<span class="rw r-gold">+${r.habit_gain} Habit</span><span class="rw r-ins">+${r.inspiration_gain} Inspiration</span>`,
      act: `<button class="btn sm gold" data-act="ritual" ${r.can_perform && !s.activity && !s.dungeon_run ? "" : "disabled"}>${r.can_perform ? "Perform" : `Level ${r.min_level}`}</button>`,
    })}</div>
    <h3 class="subhead">Astral World <span class="muted">spend Inspiration</span></h3><div class="rows">${astral}</div>
    <h3 class="subhead">Reincarnation <span class="muted">also resets allies and bonds</span></h3><div class="rows">${classes}</div>`;
}

/* ---------------------------------------------------------------- dock (right) */
function dockHTML() {
  const s = state;
  const queue = (s.action_queue || []).map((q) => `<span>${esc(q.name)}<b>×${q.count}</b></span>`).join("");
  const repeat = s.auto_action ? `<div class="inline-hint">${icon("infinity", 14)} Repeating <b>${esc(s.actions.find((a) => a.id === s.auto_action)?.name || "")}</b></div>` : "";
  const now = s.activity
    ? `<div class="now-row">${tile(s.activity.action_id, "clock", 20)}<div><div class="nm">${esc(s.activity.name)}</div><div class="sub"><b data-remain-to="${s.activity.ends_at}">${Math.ceil(s.activity.remaining)}s</b> left</div></div><button class="btn sm ghost" data-act="cancel" aria-label="Cancel action">${icon("close", 16)}</button></div>
       <div class="meter live thick"><i data-t0="${s.activity.started_at}" data-t1="${s.activity.ends_at}" style="width:${s.activity.progress}%"></i></div>${queue ? `<div class="queue">${queue}</div>` : ""}${repeat}`
    : s.battle ? `<p class="inline-hint">In battle at ${esc(s.dungeon_run?.zone_name || "a dungeon")}.</p>`
    : `<p class="inline-hint">Idle. Click an action and it keeps going while you are away.</p>${repeat}`;
  const loops = s.loops.filter((l) => l.active && s.loop_state?.[l.id]).map((l) => `<div class="loop-mini" data-key="lm-${l.id}"><span>${esc(l.name)}</span><button class="btn sm ghost" data-act="loop-stop" data-id="${l.id}">Stop</button><div class="meter live thin"><i data-t0="${s.loop_state[l.id].next_tick - l.interval}" data-t1="${s.loop_state[l.id].next_tick}" style="width:0%"></i></div></div>`).join("");
  const party = s.party.filter((a) => a.active || a.passive).map((a) => `<div class="ally-mini" data-key="am-${a.id}"><span class="portrait">${creature(a.species + " " + a.name, { size: 28 })}</span><span>${esc(a.name)}</span><span class="muted">Lv ${a.level}${a.passive ? " · passive" : ""}</span></div>`).join("");
  return `
    <section class="panel" data-key="now"><h3>Current</h3>${now}</section>
    ${loops ? `<section class="panel" data-key="loops"><h3>Loops</h3>${loops}</section>` : ""}
    <section class="panel" data-key="party"><h3>Party <span class="muted">${s.active_party.length}/${s.max_party_slots}</span></h3>${party || `<p class="inline-hint">No allies in your party yet.</p>`}</section>`;
}

/* ---------------------------------------------------------------- arena */
const targetIndex = () => {
  const foes = state.battle?.enemies || [];
  if (selectedFoe !== null && foes[selectedFoe]?.hp > 0) return selectedFoe;
  const i = foes.findIndex((f) => f.hp > 0);
  return i < 0 ? 0 : i;
};
function arenaHTML() {
  const s = state;
  const b = s.battle;
  const run = s.dungeon_run || {};
  const foes = b.enemies;
  const tgt = targetIndex();
  const pips = Array.from({ length: b.total_encounters }, (_, i) => `<i class="${i === b.total_encounters - 1 ? "boss " : ""}${i < b.encounter ? "on" : ""}"></i>`).join("");
  const foeCards = foes.map((f, i) => {
    const owned = f.ally_id && s.allies[f.ally_id];
    const first = foes.findIndex((x) => x.hp > 0) === i;
    const tag = f.ally_id && !owned && f.hp > 0 ? `<span class="recruit">${first && b.recruit_chance ? `May join: ${b.recruit_chance}%` : "May join you"}</span>` : "";
    return `
      <div class="foe ${f.hp <= 0 ? "dead" : ""} ${i === tgt && f.hp > 0 ? "target" : ""} ${b.boss ? "boss" : ""}" role="button" tabindex="${f.hp > 0 ? 0 : -1}" data-act="foe" data-i="${i}" data-foe="${i}" data-key="f-${i}-${esc(f.name)}" aria-label="Target ${esc(f.name)}">
        ${creature(f.name, { cls: "foe-art" })}
        <div class="nm">${esc(f.name)}</div>
        <div class="st"><span>ATK ${f.attack}</span><span>DEF ${f.defense}</span></div>
        ${meter(f.hp, f.max_hp, "hp")}<div class="hp-n">${f.hp} / ${f.max_hp}</div>${tag}
      </div>`;
  }).join("");
  const party = s.party.filter((a) => a.active).map((a) => `<div class="mini" title="${esc(a.name)}">${creature(a.species + " " + a.name, { size: 36 })}</div>`).join("");
  const skills = s.skills.map((k, i) => {
    const t = foes[tgt];
    const dis = !k.unlocked || s.mana < k.mana || !t || t.hp <= 0;
    const bits = [k.power ? `×${k.power}` : "", k.pierce ? `pierce ${Math.round(k.pierce * 100)}%` : "", k.execute ? `finisher <${Math.round(k.execute * 100)}%` : ""].filter(Boolean).join(" · ");
    return `
      <button class="skill ${k.mana === 0 ? "free" : ""}" data-act="skill" data-id="${k.id}" data-key="k-${k.id}" title="${esc(k.description)}" ${dis ? "disabled" : ""}>
        <div class="skill-top"><strong>${esc(k.name)}</strong><kbd>${i + 1}</kbd></div>
        <div class="cost-line">${k.unlocked ? (k.mana ? `${k.mana} Mana` : "Free") : `Level ${k.level}`}${bits ? " · " + bits : ""}</div>
      </button>`;
  }).join("");
  return `
    <div class="arena">
      <div class="arena-head">
        <div><p class="kicker">${esc(run.zone_name || "Dungeon")} · Encounter ${b.encounter} of ${b.total_encounters}${b.boss ? " · Boss" : ""}</p><h2>${foes.length > 1 ? `A band of ${foes.length}` : esc(foes[0].name)}</h2><div class="pips" style="margin-top:6px">${pips}</div></div>
        <div class="controls"><label class="switch"><input type="checkbox" data-act="auto" ${auto ? "checked" : ""}> Auto-battle</label><button class="btn danger" data-act="flee">Withdraw</button></div>
      </div>
      <div class="field">
        <svg class="cave" viewBox="0 0 800 340" preserveAspectRatio="none" aria-hidden="true"><path d="M0 0h800v34l-30 36-26-52-42 62-34-50-40 44-46-66-38 54-44-40-48 58-34-62-42 54-46-44-44 60-34-48-40 44z" fill="#0d1319"/><path d="M0 0h800v18l-60 20-40-30-60 34-50-26-70 28-40-30-80 34-60-28-70 22-60-18-50 22-60-24z" fill="#0a0f14"/></svg>
        <div class="floor"></div>
        <div class="side-hero"><div class="hero-slot" data-hero>${heroArt(s.level, s.reincarnations, 120)}</div>${party ? `<div class="party">${party}</div>` : ""}
          <div class="vit">${bar("Vitality", s.hp, s.max_hp, "hp")}${bar("Mana", s.mana, s.max_mana, "mp")}</div></div>
        <div class="foes">${foeCards}</div>
      </div>
      <div class="skills">${skills}</div>
    </div>`;
}
