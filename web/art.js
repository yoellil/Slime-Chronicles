/* Procedural art: line icons and creature portraits. No external assets. */
(function () {
  const ICONS = {
    drop: "M12 3c3.5 4.5 6 7.7 6 11a6 6 0 0 1-12 0c0-3.3 2.5-6.5 6-11z",
    eye: "M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12zM12 9.5a2.5 2.5 0 1 0 0 5 2.5 2.5 0 0 0 0-5z",
    sword: "M5 19L19 5M14 5h5v5M7 15l2 2M4 20l3-3",
    shield: "M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z",
    star: "M12 3l2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1L3.2 9.5l6.1-.9z",
    leaf: "M5 19C5 10 10 5 20 4c0 10-5 15-14 15zM5 19l8-8",
    flame: "M12 3c1 4 5 5.5 5 10a5 5 0 0 1-10 0c0-2 1-3 2-4 0 2 1 3 2 3 0-3-1-6 1-9z",
    bolt: "M13 2L5 14h6l-1 8 8-12h-6z",
    paw: "M12 13c-3 0-5.5 2.2-5.5 4.5S8.5 20 12 20s5.5-.2 5.5-2.5S15 13 12 13zM6 9.5a1.6 1.6 0 1 0 0-3.2 1.6 1.6 0 0 0 0 3.2zM10 7a1.6 1.6 0 1 0 0-3.2A1.6 1.6 0 0 0 10 7zM14 7a1.6 1.6 0 1 0 0-3.2A1.6 1.6 0 0 0 14 7zM18 9.5a1.6 1.6 0 1 0 0-3.2 1.6 1.6 0 0 0 0 3.2z",
    book: "M5 4h11a3 3 0 0 1 3 3v13H8a3 3 0 0 1-3-3zM8 8h7M8 12h7",
    hammer: "M4 20l9-9M12 6l4-3 5 5-3 4-3-3z",
    coin: "M12 4a8 8 0 1 0 0 16 8 8 0 0 0 0-16zM12 8v8M9.5 10h4a1.5 1.5 0 0 1 0 3h-3a1.5 1.5 0 0 0 0 3h4",
    heart: "M12 20s-8-5-8-11a4.5 4.5 0 0 1 8-2.5A4.5 4.5 0 0 1 20 9c0 6-8 11-8 11z",
    crystal: "M12 2l6 8-6 12-6-12zM6 10h12",
    spiral: "M12 12a1.5 1.5 0 1 1 1.5 1.5A3 3 0 1 1 10.5 9.5 4.5 4.5 0 1 1 16 16a6 6 0 0 1-8-8",
    crown: "M3 8l4 4 5-7 5 7 4-4-2 11H5z",
    skull: "M12 3a8 8 0 0 0-5 14v3h10v-3a8 8 0 0 0-5-14zM9 12h.01M15 12h.01M11 17v3M13 17v3",
    home: "M3 11l9-8 9 8M5 10v10h14V10M10 20v-6h4v6",
    mountain: "M2 20l7-12 4 6 3-4 6 10z",
    people: "M9 11a3 3 0 1 0 0-6 3 3 0 0 0 0 6zM3 20c0-3.5 2.7-6 6-6s6 2.5 6 6M17 11a2.5 2.5 0 1 0 0-5M17.5 14c2.2.4 3.5 2.5 3.5 5",
    speech: "M4 5h16v11H9l-5 4z",
    moon: "M20 14A8 8 0 0 1 10 4a8 8 0 1 0 10 10z",
    up: "M12 20V5M6 11l6-6 6 6",
    gate: "M5 21V8a7 7 0 0 1 14 0v13M3 21h18M12 21v-7",
    flag: "M5 21V4M5 5h13l-3 4 3 4H5",
    compass: "M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18zM15.5 8.5l-2 5-5 2 2-5z",
    search: "M10.5 4a6.5 6.5 0 1 0 0 13 6.5 6.5 0 0 0 0-13zM15.5 15.5L21 21",
    wave: "M3 12c2-4 4-4 6 0s4 4 6 0 4-4 6 0",
    blob: "M5 16c0-6 3-10 7-10s7 4 7 10c0 2.5-3 3.5-7 3.5S5 18.5 5 16zM9.5 13h.01M14.5 13h.01",
    lotus: "M12 4c2 3 2 6 0 9-2-3-2-6 0-9zM4 10c4 0 7 2 8 6-4 0-7-2-8-6zM20 10c-4 0-7 2-8 6 4 0 7-2 8-6zM6 19h12",
    maw: "M3 9c4-3 14-3 18 0-1 7-4 10-9 10S4 16 3 9zM8 12l1.5 3L11 12l1.5 3L14 12l1.5 3L17 12",
    scroll: "M7 4h11v13a3 3 0 0 1-3 3H6a3 3 0 0 1-3-3v-1h12M7 4a3 3 0 0 0-3 3v9M9 9h6M9 13h6",
    check: "M5 12.5l4.5 4.5L19 7.5",
    lock: "M6 11h12v9H6zM8.5 11V8a3.5 3.5 0 0 1 7 0v3",
    sound: "M4 9v6h4l5 4V5L8 9zM16 9a4 4 0 0 1 0 6M18.5 6.5a8 8 0 0 1 0 11",
    mute: "M4 9v6h4l5 4V5L8 9zM17 9l5 6M22 9l-5 6",
    menu: "M4 7h16M4 12h16M4 17h16",
    close: "M6 6l12 12M18 6L6 18",
    swords: "M4 20L16 8M13 5h6v6M20 20L8 8M11 5H5v6",
    map: "M9 4L3 6v14l6-2 6 2 6-2V4l-6 2zM9 4v14M15 6v14",
    sparkle: "M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8zM18 16l.8 2.2L21 19l-2.2.8L18 22l-.8-2.2L15 19l2.2-.8z",
    clock: "M12 4a8 8 0 1 0 0 16 8 8 0 0 0 0-16zM12 8v4.5l3 1.5",
    hourglass: "M6 3h12M6 21h12M7 3c0 5 5 6 5 9s-5 4-5 9M17 3c0 5-5 6-5 9s5 4 5 9",
    flask: "M9 3h6M10 3v6l-5 9a2 2 0 0 0 1.8 3h10.4A2 2 0 0 0 19 18l-5-9V3M8 15h8",
    infinity: "M7.5 8a4 4 0 1 0 0 8c4 0 5-8 9-8a4 4 0 1 1 0 8c-4 0-5-8-9-8z",
    trophy: "M8 4h8v6a4 4 0 0 1-8 0zM8 6H4v1a4 4 0 0 0 4 4M16 6h4v1a4 4 0 0 1-4 4M12 14v4M8 20h8",
    arrow: "M5 12h14M13 6l6 6-6 6",
    plus: "M12 5v14M5 12h14",
  };

  function icon(name, size = 20, extra = "") {
    const d = ICONS[name] || ICONS.sparkle;
    return `<svg class="ico ${extra}" width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="${d}"/></svg>`;
  }

  // action id -> [icon, tone]
  const ART = {
    gather_dew: ["drop", "teal"], analyze_moss: ["eye", "blue"], shape_body: ["blob", "gold"],
    follow_roar: ["wave", "coral"], silent_scout: ["compass", "blue"], magicule_circulation: ["spiral", "teal"],
    talk_goblins: ["speech", "gold"], train_allies: ["sword", "coral"],
    rest_loop: ["moon", "blue"], farmwork: ["leaf", "teal"], meditation: ["lotus", "violet"], hunting: ["paw", "coral"],
    worship: ["star", "gold"], village_building: ["home", "gold"], blacksmithing: ["hammer", "coral"], diplomacy: ["scroll", "blue"],
    get_motivated: ["bolt", "gold"], quick_trade: ["coin", "gold"], scavenge: ["search", "teal"], devour: ["maw", "coral"], negotiate: ["scroll", "gold"],
    expand_body: ["heart", "coral"], deepen_mana: ["crystal", "blue"], harden_body: ["sword", "gold"], reinforce_defense: ["shield", "teal"],
    expand_party: ["people", "teal"], passive_slot: ["people", "violet"], unique_skill: ["star", "violet"], ultimate_skill: ["crown", "gold"],
    doppelganger: ["people", "violet"], soul_amplifier: ["spiral", "teal"], eternal_insight: ["eye", "blue"], golden_touch: ["coin", "gold"],
    predator_essence: ["maw", "coral"], unbreakable_slime: ["shield", "teal"], great_sage: ["book", "blue"], ragnarok: ["bolt", "violet"],
    gluttony: ["maw", "gold"], sloth: ["moon", "blue"], greed: ["coin", "gold"], pride: ["crown", "violet"], envy: ["eye", "teal"], wrath: ["flame", "coral"], lust: ["heart", "violet"],
    warrior: ["sword", "coral"], sorcerer: ["crystal", "blue"], tamer: ["paw", "teal"], demon_lord: ["crown", "violet"], true_dragon: ["bolt", "gold"],
  };

  function tile(id, fallback = "sparkle", size = 22) {
    const [name, tone] = ART[id] || [fallback, "teal"];
    return `<span class="tile tone-${tone}">${icon(name, size)}</span>`;
  }

  // ---------- creatures ----------
  const hash = (s) => { let h = 5381; for (let i = 0; i < s.length; i++) h = ((h << 5) + h + s.charCodeAt(i)) | 0; return Math.abs(h); };
  const hsl = (h, s, l) => `hsl(${Math.round(h) % 360} ${s}% ${l}%)`;

  const KINDS = [
    ["voice", /\b(voice|great sage|narrator|ruins echo|unknown|distant)/i],
    ["dragon", /veldora|dragon|wyrm/i],
    ["demon", /diablo|demon|clayman|harlequin/i],
    ["bat", /\bbat\b/i],
    ["spider", /spider|needle/i],
    ["centipede", /centipede|carapace/i],
    ["slug", /slug|melu|crawler/i],
    ["rabbit", /rabbit|piko/i],
    ["wolf", /wolf|ranga|fang|bear/i],
    ["frog", /frog|gama|newt/i],
    ["lizard", /lizard|basilisk|seki|gabiru|serpent/i],
    ["goblin", /goblin|gobta|rigurd/i],
    ["orc", /\borc|geld/i],
    ["treant", /treant|forest guardian/i],
    ["golem", /golem|sentinel|guardian|scarab|clockwork/i],
    ["wight", /wight|dust/i],
    ["oni", /hakuro|shion|shuna|benimaru|souei|kijin|\boni\b/i],
    ["dwarf", /dwarf|gazel|kaijin|troll/i],
    ["knight", /knight|guard|king|mage|falmuth|captain|general|mercenary|sergeant/i],
    ["human", /merchant|child|herbalist|foreman|fisher|cook|envoy|council|archivist|keeper|scout|herald/i],
    ["slime", /rimuru|slime/i],
  ];
  const BASE = {
    bat: [205, 22, 38], spider: [8, 28, 34], centipede: [24, 45, 40], slug: [92, 42, 42], rabbit: [32, 35, 62], wolf: [215, 12, 46],
    frog: [135, 38, 40], lizard: [150, 32, 38], goblin: [100, 36, 40], orc: [85, 30, 34], golem: [200, 8, 44], treant: [30, 30, 30],
    wight: [165, 6, 30], oni: [4, 55, 44], dwarf: [28, 30, 55], knight: [212, 10, 58], human: [30, 40, 58], demon: [345, 42, 36],
    dragon: [188, 40, 38], voice: [168, 50, 45], slime: [165, 55, 48],
  };
  const GLOW = { demon: "#ff7a66", wight: "#8dffe6", golem: "#8fe9ff", voice: "#d8fff6", dragon: "#ffe27a", spider: "#ff9a7a", slug: "#e9ff7a", slime: "#ff8a78" };

  function kindOf(name) {
    for (const [kind, re] of KINDS) if (re.test(name)) return kind;
    return "slime";
  }
  const eye = (x, y, r, c, p = true) => `<circle cx="${x}" cy="${y}" r="${r}" fill="${c}"/>${p ? `<ellipse cx="${x}" cy="${y}" rx="${r * 0.28}" ry="${r * 0.75}" fill="#0b1214"/>` : ""}<circle cx="${x - r * 0.3}" cy="${y - r * 0.35}" r="${r * 0.22}" fill="#fff" opacity=".85"/>`;

  const DRAW = {
    bat: ({ c, d, l, g }) => `<path d="M50 44C38 26 18 24 6 40c8-2 14 2 18 10-2 2-4 5-4 8 8-4 14-2 18 6 3-6 6-9 12-9s9 3 12 9c4-8 10-10 18-6 0-3-2-6-4-8 4-8 10-12 18-10C82 24 62 26 50 44z" fill="${d}"/><path d="M40 36l-6-16 14 8zM60 36l6-16-14 8z" fill="${c}"/><ellipse cx="50" cy="54" rx="15" ry="17" fill="${c}"/><ellipse cx="50" cy="60" rx="9" ry="10" fill="${l}" opacity=".3"/>${eye(44, 49, 3.4, g)}${eye(56, 49, 3.4, g)}<path d="M45 61l2.5 6 2.5-6zM50 61l2.5 6 2.5-6z" fill="#f4f1e6"/>`,
    spider: ({ c, d, l, g }) => `<g stroke="${d}" stroke-width="4" stroke-linecap="round" fill="none"><path d="M40 52L18 38L10 58M40 58L14 58L8 76M42 64L20 74L18 92M45 68L32 86L34 95M60 52L82 38L90 58M60 58L86 58L92 76M58 64L80 74L82 92M55 68L68 86L66 95"/></g><ellipse cx="50" cy="64" rx="19" ry="21" fill="${c}"/><path d="M50 46v38M40 54q10 6 20 0M38 66q12 8 24 0" stroke="${d}" stroke-width="2.5" fill="none"/><circle cx="50" cy="38" r="12" fill="${d}"/>${eye(45, 36, 2.8, g, false)}${eye(55, 36, 2.8, g, false)}${eye(47, 42, 1.8, g, false)}${eye(53, 42, 1.8, g, false)}<circle cx="50" cy="64" r="4" fill="${l}" opacity=".5"/>`,
    centipede: ({ c, d, l, g }) => {
      const pts = [[84, 78], [74, 70], [64, 63], [53, 59], [42, 59], [31, 63], [22, 70]];
      const body = pts.map(([x, y]) => `<path d="M${x} ${y - 14}v28" stroke="${d}" stroke-width="3" stroke-linecap="round"/><circle cx="${x}" cy="${y}" r="9" fill="${c}" stroke="${d}" stroke-width="2.5"/><circle cx="${x - 2}" cy="${y - 3}" r="3" fill="${l}" opacity=".35"/>`).join("");
      return `${body}<circle cx="14" cy="64" r="12" fill="${d}"/>${eye(10, 61, 3, g, false)}${eye(19, 61, 3, g, false)}<path d="M6 72l-5 8M13 76l-2 9M20 74l4 8" stroke="${l}" stroke-width="3" stroke-linecap="round"/>`;
    },
    slug: ({ c, d, l, g }) => `<path d="M6 80C6 62 22 50 44 50c14 0 22 6 28 14 4 5 12 6 20 6 0 7-4 10-10 10z" fill="${c}"/><path d="M6 80h84v5H6z" fill="${l}" opacity=".45"/><path d="M72 58L76 34M83 60L91 40" stroke="${c}" stroke-width="4" stroke-linecap="round"/>${eye(76, 32, 4.5, g)}${eye(91, 38, 4.5, g)}<circle cx="30" cy="62" r="3" fill="${d}" opacity=".5"/><circle cx="46" cy="58" r="2" fill="${d}" opacity=".5"/><path d="M20 88q-2 5 0 7M40 88q-2 6 0 9M58 88q-2 5 0 7" stroke="${l}" stroke-width="3" stroke-linecap="round" opacity=".8"/>`,
    rabbit: ({ c, d, l, g }) => `<path d="M34 42c-9-14-7-34 2-34s9 18 5 34zM66 42c9-14 7-34-2-34s-9 18-5 34z" fill="${c}"/><path d="M36 38c-5-10-4-24 0-24s5 12 3 24zM64 38c5-10 4-24 0-24s-5 12-3 24z" fill="${l}" opacity=".5"/><ellipse cx="50" cy="70" rx="24" ry="22" fill="${c}"/><circle cx="50" cy="50" r="19" fill="${c}"/><ellipse cx="50" cy="76" rx="14" ry="12" fill="${l}" opacity=".4"/><path d="M47 33l3-17 3 17z" fill="#f3e1b0"/>${eye(42, 49, 3.2, "#fff", false)}${eye(58, 49, 3.2, "#fff", false)}<circle cx="42" cy="49" r="1.6" fill="#10181b"/><circle cx="58" cy="49" r="1.6" fill="#10181b"/><path d="M50 55l-3 3h6z" fill="#e58a8a"/><path d="M50 58v3M46 62q4 3 8 0" stroke="${d}" stroke-width="1.6" fill="none"/>`,
    wolf: ({ c, d, l, g }) => `<path d="M20 36L26 8 42 26C46 25 54 25 58 26L74 8 80 36C86 46 84 62 72 74L50 90 28 74C16 62 14 46 20 36z" fill="${c}"/><path d="M27 30l2-14 8 10zM73 30l-2-14-8 10z" fill="${d}"/><path d="M24 44q10 4 8 14M76 44q-10 4-8 14" stroke="${d}" stroke-width="3" fill="none" opacity=".6"/><ellipse cx="50" cy="70" rx="15" ry="12" fill="${l}" opacity=".85"/><path d="M28 46l14 4-2 7-14-3zM72 46l-14 4 2 7 14-3z" fill="${g}"/><circle cx="35" cy="52" r="2" fill="#10181b"/><circle cx="65" cy="52" r="2" fill="#10181b"/><ellipse cx="50" cy="63" rx="5" ry="3.5" fill="#10181b"/><path d="M50 66v6M42 74q8 6 16 0" stroke="#10181b" stroke-width="2" fill="none"/><path d="M42 74l2 6 2-6zM54 74l2 6 2-6z" fill="#f4f1e6"/>`,
    frog: ({ c, d, l, g }) => `<ellipse cx="50" cy="66" rx="36" ry="24" fill="${c}"/><ellipse cx="50" cy="74" rx="24" ry="13" fill="${l}" opacity=".45"/><circle cx="31" cy="42" r="12" fill="${c}"/><circle cx="69" cy="42" r="12" fill="${c}"/><circle cx="31" cy="41" r="7.5" fill="${g}"/><circle cx="69" cy="41" r="7.5" fill="${g}"/><ellipse cx="31" cy="41" rx="2.4" ry="6" fill="#10181b"/><ellipse cx="69" cy="41" rx="2.4" ry="6" fill="#10181b"/><path d="M20 66q30 18 60 0" stroke="${d}" stroke-width="3" fill="none" stroke-linecap="round"/><circle cx="46" cy="58" r="1.5" fill="${d}"/><circle cx="54" cy="58" r="1.5" fill="${d}"/><circle cx="30" cy="74" r="3" fill="${d}" opacity=".5"/><circle cx="70" cy="76" r="4" fill="${d}" opacity=".5"/>`,
    lizard: ({ c, d, l, g }) => `<path d="M38 18l5-12 6 12 6-14 5 14 8-8-2 14z" fill="${d}"/><path d="M50 14l26 22 12 26-14 24-24 12-24-12-14-24 12-26z" fill="${c}"/><path d="M50 14l8 28M50 14l-8 28" stroke="${d}" stroke-width="2.5" opacity=".6"/>${eye(36, 48, 6, g)}${eye(64, 48, 6, g)}<ellipse cx="50" cy="66" rx="14" ry="10" fill="${l}" opacity=".45"/><circle cx="46" cy="62" r="1.8" fill="${d}"/><circle cx="54" cy="62" r="1.8" fill="${d}"/><path d="M38 74q12 7 24 0" stroke="${d}" stroke-width="2.5" fill="none"/><path d="M45 76l2 5 2-5zM53 76l2 5 2-5z" fill="#f4f1e6"/><path d="M30 60q4 3 8 2M70 60q-4 3-8 2" stroke="${d}" stroke-width="2" fill="none" opacity=".6"/>`,
    goblin: ({ c, d, l, g }) => `<path d="M26 50L2 36l8 26 18 4zM74 50l24-14-8 26-18 4z" fill="${c}"/><ellipse cx="50" cy="52" rx="25" ry="27" fill="${c}"/><path d="M28 36q22-12 44 0" stroke="${d}" stroke-width="4" fill="none" stroke-linecap="round"/>${eye(40, 47, 5, "#ffe27a")}${eye(60, 47, 5, "#ffe27a")}<path d="M50 52l-5 11h10z" fill="${d}" opacity=".7"/><path d="M36 68q14 12 28 0" stroke="${d}" stroke-width="3" fill="none"/><path d="M40 70l2 5 2-5zM56 70l2 5 2-5z" fill="#f4f1e6"/><path d="M22 84q28 20 56 0v14H22z" fill="#6b5a3e"/>`,
    orc: ({ c, d, l, g }) => `<path d="M14 48C14 24 30 12 50 12s36 12 36 36c0 22-12 42-36 44S14 70 14 48z" fill="${c}"/><path d="M24 36l22 10M76 36L54 46" stroke="${d}" stroke-width="6" stroke-linecap="round"/>${eye(37, 49, 3.4, "#ffd37a", false)}${eye(63, 49, 3.4, "#ffd37a", false)}<path d="M44 60q6 5 12 0v6q-6 4-12 0z" fill="${d}" opacity=".7"/><path d="M30 76q20 10 40 0" stroke="${d}" stroke-width="4" fill="none" stroke-linecap="round"/><path d="M34 77l-4-17 9 11zM66 77l4-17-9 11z" fill="#f3e8c8"/><path d="M42 12q8-8 16 0" stroke="${d}" stroke-width="5" fill="none"/>`,
    golem: ({ c, d, l, g }) => `<rect x="12" y="52" width="76" height="40" rx="6" fill="${c}"/><rect x="30" y="14" width="40" height="38" rx="5" fill="${c}"/><rect x="8" y="50" width="22" height="18" rx="4" fill="${d}"/><rect x="70" y="50" width="22" height="18" rx="4" fill="${d}"/><path d="M40 24l6 4M64 70l-8 10 6 12M20 62l10 6" stroke="${d}" stroke-width="2.5" fill="none"/><rect x="36" y="28" width="9" height="7" rx="2" fill="${g}"/><rect x="55" y="28" width="9" height="7" rx="2" fill="${g}"/><path d="M40 44h20" stroke="${d}" stroke-width="3"/><circle cx="50" cy="72" r="8" fill="none" stroke="${g}" stroke-width="2.5"/><circle cx="50" cy="72" r="3" fill="${g}"/>`,
    treant: ({ c, d, l, g }) => `<circle cx="22" cy="26" r="14" fill="${l}" opacity=".55"/><circle cx="50" cy="16" r="16" fill="${l}" opacity=".55"/><circle cx="80" cy="26" r="14" fill="${l}" opacity=".55"/><path d="M32 94C28 72 30 52 36 38 28 32 20 28 14 30c8-8 18-4 24 4 2-8 6-14 12-14s10 6 12 14c6-8 16-12 24-4-6-2-14 2-22 8 6 14 8 34 4 56z" fill="${c}"/><path d="M42 56v30M58 50v38M50 64v26" stroke="${d}" stroke-width="2.5" opacity=".55"/><path d="M38 44q5-4 10 0M52 44q5-4 10 0" stroke="${g}" stroke-width="3" fill="none" stroke-linecap="round"/><circle cx="43" cy="47" r="2.2" fill="${g}"/><circle cx="57" cy="47" r="2.2" fill="${g}"/><path d="M43 60q7 6 14 0" stroke="${d}" stroke-width="3" fill="none"/>`,
    wight: ({ c, d, l, g }) => `<path d="M50 6C26 6 14 26 14 52v42h72V52C86 26 74 6 50 6z" fill="${c}"/><ellipse cx="50" cy="50" rx="19" ry="23" fill="#0a0f11"/><circle cx="42" cy="46" r="4.5" fill="${g}"/><circle cx="58" cy="46" r="4.5" fill="${g}"/><path d="M44 66l2 6 4-6 4 6 2-6" stroke="${l}" stroke-width="2" fill="none" stroke-linejoin="round"/><path d="M14 94q8-8 14 0t14 0 14 0 14 0 14 0" stroke="${d}" stroke-width="5" fill="none"/>`,
    oni: ({ c, d, l, g, h }) => `<path d="M10 98c0-24 16-32 40-32s40 8 40 32z" fill="${hsl(h + 180, 30, 30)}"/><path d="M50 66l-10 22h20z" fill="${hsl(h + 180, 30, 20)}"/><rect x="43" y="58" width="14" height="12" rx="3" fill="#e9c9a8"/><circle cx="50" cy="44" r="20" fill="#f1d6b8"/><path d="M29 44C28 22 40 14 50 14s23 8 21 30c-5-9-11-13-21-13s-16 4-21 13z" fill="${hsl(h, 20, 18)}"/><path d="M39 24l-6-18 12 14zM61 24l6-18-12 14z" fill="#f3e1b0"/>${eye(42, 48, 3, "#2a1a1a", false)}${eye(58, 48, 3, "#2a1a1a", false)}<path d="M44 57q6 4 12 0" stroke="#a65a4a" stroke-width="2" fill="none"/><path d="M40 78h20" stroke="${l}" stroke-width="3" opacity=".7"/>`,
    dwarf: ({ c, d, l, g, h }) => `<path d="M10 98c0-22 16-30 40-30s40 8 40 30z" fill="${hsl(h, 12, 40)}"/><path d="M30 52c0 24 8 34 20 34s20-10 20-34c-6 6-12 8-20 8s-14-2-20-8z" fill="${hsl(h + 10, 55, 40)}"/><circle cx="50" cy="42" r="18" fill="#f0cfae"/><path d="M30 40c0-16 8-24 20-24s20 8 20 24z" fill="${hsl(h, 8, 42)}"/><path d="M28 40h44" stroke="${l}" stroke-width="3"/><path d="M33 52c0 20 7 30 17 30s17-10 17-30c-5 5-11 7-17 7s-12-2-17-7z" fill="${hsl(h + 10, 55, 40)}"/>${eye(43, 46, 2.6, "#2a1a1a", false)}${eye(57, 46, 2.6, "#2a1a1a", false)}<ellipse cx="50" cy="53" rx="4" ry="3.2" fill="#d99a7c"/>`,
    knight: ({ c, d, l, g, name }) => `<path d="M8 98c0-22 16-30 42-30s42 8 42 30z" fill="${d}"/><path d="M28 98c0-14 8-20 22-20s22 6 22 20z" fill="${c}"/><path d="M30 34C30 18 40 10 50 10s20 8 20 24v22c0 12-8 20-20 20s-20-8-20-20z" fill="${c}"/><rect x="33" y="36" width="34" height="8" rx="3" fill="#0d1416"/><circle cx="43" cy="40" r="2" fill="${g}"/><circle cx="57" cy="40" r="2" fill="${g}"/><path d="M50 10v26M40 52h20M42 60h16" stroke="${d}" stroke-width="2.5" fill="none" opacity=".7"/>${/king/i.test(name) ? `<path d="M30 12l6 8 7-12 7 12 7-12 7 12 6-8-3 14H33z" fill="#ecbf6a"/>` : /mage/i.test(name) ? `<path d="M26 22L50 -6l24 28z" fill="#3d4a6a"/><circle cx="50" cy="-2" r="0" /><path d="M26 22h48" stroke="#ecbf6a" stroke-width="3"/>` : `<path d="M50 10c-8-12 8-14 14-4" stroke="#d9604d" stroke-width="5" fill="none" stroke-linecap="round"/>`}`,
    human: ({ c, d, l, g, h }) => `<path d="M10 98c0-22 16-30 40-30s40 8 40 30z" fill="${hsl(h + 120, 28, 34)}"/><path d="M18 98c0-14 10-22 32-22s32 8 32 22z" fill="${hsl(h + 120, 28, 26)}" opacity=".6"/><circle cx="50" cy="44" r="19" fill="${hsl(h, 45, 70)}"/><path d="M28 46C26 22 40 12 50 12s24 10 22 34c-4-10-8-16-22-16S32 36 28 46z" fill="${hsl(h + 20, 25, 22)}"/>${eye(43, 48, 2.6, "#2a1a1a", false)}${eye(57, 48, 2.6, "#2a1a1a", false)}<path d="M44 57q6 4 12 0" stroke="#a65a4a" stroke-width="2" fill="none"/>`,
    demon: ({ c, d, l, g }) => `<path d="M30 32C16 26 10 10 16 0c4 12 14 18 24 22zM70 32c14-6 20-22 14-32-4 12-14 18-24 22z" fill="${d}"/><path d="M24 38C24 26 36 18 50 18s26 8 26 20v16c0 18-10 30-26 38C34 84 24 72 24 54z" fill="${c}"/><path d="M24 40q-12 4-14 14l16 2zM76 40q12 4 14 14l-16 2z" fill="${d}"/><path d="M32 46l14 6-3 6-14-5zM68 46l-14 6 3 6 14-5z" fill="${g}"/><path d="M36 68q14 12 28 0" stroke="#10181b" stroke-width="3" fill="none"/><path d="M40 69l2 6 2-6zM56 69l2 6 2-6z" fill="#f4f1e6"/><path d="M44 84q6 10 12 0" stroke="${d}" stroke-width="4" fill="none"/>`,
    dragon: ({ c, d, l, g }) => `<path d="M22 32L6 6l24 12zM78 32L94 6 70 18z" fill="${l}"/><path d="M20 46L2 54l18 6zM80 46l18 8-18 6z" fill="${d}"/><path d="M20 40C20 24 34 14 50 14s30 10 30 26v14c0 18-12 32-30 38C32 86 20 72 20 54z" fill="${c}"/><path d="M26 36l22 8M74 36L52 44" stroke="${d}" stroke-width="5" stroke-linecap="round"/>${eye(36, 48, 5.5, g)}${eye(64, 48, 5.5, g)}<ellipse cx="50" cy="68" rx="16" ry="12" fill="${l}" opacity=".4"/><circle cx="44" cy="66" r="2" fill="${d}"/><circle cx="56" cy="66" r="2" fill="${d}"/><path d="M38 78l4 12 5-10zM62 78l-4 12-5-10z" fill="#f4f1e6"/><path d="M52 4l-6 14h8l-4 12" stroke="${g}" stroke-width="2.5" fill="none" stroke-linejoin="round"/>`,
    voice: ({ c, d, l, g }) => `<circle cx="50" cy="50" r="42" fill="${d}"/><circle cx="50" cy="50" r="34" fill="none" stroke="${c}" stroke-width="2" opacity=".7"/><circle cx="50" cy="50" r="26" fill="${c}" opacity=".35"/><circle cx="50" cy="50" r="15" fill="${g}" opacity=".9"/><circle cx="50" cy="50" r="6" fill="#fff"/><path d="M50 4v14M50 82v14M4 50h14M82 50h14M18 18l10 10M72 72l10 10M82 18L72 28M28 72L18 82" stroke="${l}" stroke-width="2.5" stroke-linecap="round" opacity=".7"/>`,
    slime: ({ c, d, l, g }) => `<path d="M12 78c0-26 16-50 38-50s38 24 38 50c0 8-10 12-38 12S12 86 12 78z" fill="${c}"/><ellipse cx="34" cy="48" rx="9" ry="5" fill="${l}" opacity=".55" transform="rotate(-25 34 48)"/><path d="M36 54l12 6-2 6-12-4zM64 54l-12 6 2 6 12-4z" fill="${g}"/><path d="M38 76q12 8 24 0" stroke="${d}" stroke-width="3" fill="none"/>`,
  };

  function creature(name, opts = {}) {
    const n = String(name || "");
    const kind = opts.kind || kindOf(n);
    const [bh, bs, bl] = BASE[kind] || BASE.slime;
    const hh = hash(n);
    const h = bh + ((hh % 31) - 15);
    const pal = { c: hsl(h, bs, bl), d: hsl(h, Math.min(60, bs + 6), Math.max(12, bl - 20)), l: hsl(h, bs, Math.min(82, bl + 24)), g: GLOW[kind] || "#ffe27a", h, name: n };
    const size = opts.size || 96;
    return `<svg class="creature k-${kind} ${opts.cls || ""}" viewBox="0 0 100 100" width="${size}" height="${size}" role="img" aria-label="${n.replace(/"/g, "")}">${DRAW[kind](pal)}</svg>`;
  }

  // The hero slime: glossy, grows features with level.
  function hero(level = 1, reincarnations = 0, size = 120) {
    const crown = level >= 10 ? `<path d="M36 28l5 7 9-12 9 12 5-7-2 12H38z" fill="#ecbf6a" stroke="#a97d2e" stroke-width="1.5" stroke-linejoin="round"/>` : "";
    const halo = reincarnations > 0 ? `<ellipse cx="60" cy="14" rx="22" ry="6" fill="none" stroke="#ecbf6a" stroke-width="3" opacity=".9"/>` : "";
    const aura = level >= 5 ? `<circle cx="60" cy="68" r="52" fill="none" stroke="#56e0c0" stroke-width="1.5" opacity=".35" class="aura"/>` : "";
    return `<svg class="hero-slime" viewBox="0 0 120 120" width="${size}" height="${size}" role="img" aria-label="Rimuru, the slime">
      <defs><radialGradient id="slimeBody" cx="38%" cy="30%" r="80%"><stop offset="0" stop-color="#b5fff0"/><stop offset=".45" stop-color="#4fdcc0"/><stop offset="1" stop-color="#1f8f7d"/></radialGradient></defs>
      ${aura}${halo}
      <g class="slime-body">
        <path d="M14 92c0-30 18-58 46-58s46 28 46 58c0 10-14 14-46 14S14 102 14 92z" fill="url(#slimeBody)"/>
        <path d="M14 92c0 10 14 14 46 14s46-4 46-14c0 4-14 8-46 8S14 96 14 92z" fill="#17695c" opacity=".55"/>
        <ellipse cx="38" cy="58" rx="12" ry="7" fill="#fff" opacity=".6" transform="rotate(-28 38 58)"/>
        <circle cx="26" cy="74" r="2.4" fill="#fff" opacity=".5"/>
        <g class="slime-eyes"><ellipse cx="46" cy="80" rx="5.2" ry="7" fill="#0b1f1c"/><ellipse cx="74" cy="80" rx="5.2" ry="7" fill="#0b1f1c"/><circle cx="44.5" cy="77.5" r="2" fill="#fff"/><circle cx="72.5" cy="77.5" r="2" fill="#fff"/></g>
        <path d="M52 92q8 6 16 0" stroke="#0b1f1c" stroke-width="2.6" fill="none" stroke-linecap="round"/>
      </g>${crown}
    </svg>`;
  }

  // Wide backdrops for story scenes.
  const SCENES = {
    cave: `<rect width="1200" height="300" fill="#07100f"/><path d="M0 0h1200v70l-60 60-40-110-70 120-50-90-60 80-80-130-60 110-70-80-80 100-70-120-60 90-70-70-90 110-60-80-70 70z" fill="#0d1d1c"/><path d="M0 0h1200v34l-90 40-60-60-90 70-70-50-100 60-60-50-110 70-90-40-100 60-80-50-90 40-110-50z" fill="#091413"/><path d="M0 300V230c180-30 320-10 480-30s300-40 480-10 180 20 240 8v102z" fill="#0c1a19"/><g fill="#56e0c0"><path d="M170 250l14-48 14 48zM200 250l10-32 10 32z" opacity=".9"/><path d="M980 244l12-52 14 52zM1010 244l9-30 9 30z" opacity=".8"/></g><circle cx="600" cy="150" r="82" fill="none" stroke="#56e0c0" stroke-width="3" opacity=".55"/><circle cx="600" cy="150" r="58" fill="none" stroke="#56e0c0" stroke-width="2" stroke-dasharray="6 10" opacity=".45"/><path d="M600 80v140M530 150h140" stroke="#56e0c0" stroke-width="2" opacity=".3"/>`,
    village: `<rect width="1200" height="300" fill="#08130f"/><circle cx="930" cy="70" r="34" fill="#e9f2ef" opacity=".9"/><g fill="#0d231c"><path d="M0 220l50-120 50 120zM80 220l60-150 60 150zM190 220l40-100 40 100zM900 220l60-140 60 140zM1000 220l50-110 50 110zM1100 220l50-130 50 130z"/></g><path d="M0 300V236c200-14 400-8 600-4s400-12 600 0v68z" fill="#0b1a14"/><g fill="#1a2f26"><path d="M330 236v-50l50-36 50 36v50zM520 236v-40l40-30 40 30v40zM700 236v-56l54-38 54 38v56z"/></g><g fill="#ecbf6a"><rect x="372" y="200" width="16" height="22" rx="2"/><rect x="552" y="206" width="14" height="18" rx="2"/><rect x="738" y="196" width="16" height="24" rx="2"/><rect x="772" y="204" width="12" height="18" rx="2"/></g>`,
    ruins: `<rect width="1200" height="300" fill="#0b0f12"/><path d="M0 300V232c200-20 400-10 600-12s400-10 600 4v76z" fill="#11181b"/><g fill="#1b2529"><path d="M200 240V90h46v150zM330 240V130h46v110l-12 8-14-20-8 22zM830 240V100h46v140zM960 240V150h46v90z"/><path d="M200 90h176v26H200z" opacity=".0"/><path d="M246 130c40-40 84-40 130 0v-20c-46-44-90-44-130 0z"/></g><circle cx="600" cy="140" r="70" fill="none" stroke="#ecbf6a" stroke-width="2.5" opacity=".6"/><circle cx="600" cy="140" r="48" fill="none" stroke="#ecbf6a" stroke-width="1.5" stroke-dasharray="3 9" opacity=".55"/><g fill="#ecbf6a" opacity=".7"><circle cx="520" cy="70" r="2.5"/><circle cx="690" cy="96" r="2"/><circle cx="640" cy="52" r="2"/><circle cx="560" cy="200" r="2"/></g>`,
    hall: `<rect width="1200" height="300" fill="#0a1113"/><g fill="#131e22"><rect x="120" y="0" width="60" height="300"/><rect x="330" y="0" width="60" height="300"/><rect x="810" y="0" width="60" height="300"/><rect x="1020" y="0" width="60" height="300"/></g><path d="M520 0h160l60 300H460z" fill="#ecbf6a" opacity=".1"/><path d="M0 300V250h1200v50z" fill="#0f191c"/><g fill="#7a5a22"><path d="M470 0h26v120l-13 20-13-20zM704 0h26v120l-13 20-13-20z"/></g>`,
  };
  function scene(kind) {
    return `<svg viewBox="0 0 1200 300" preserveAspectRatio="xMidYMid slice" aria-hidden="true">${SCENES[kind] || SCENES.hall}</svg>`;
  }

  window.Art = { icon, tile, creature, hero, scene, kindOf, ICONS, ART };
})();
