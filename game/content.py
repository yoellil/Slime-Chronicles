"""Narrative, encounter, ally, and balance data for Slime Chronicles."""

HERO = {
    "id": "rimuru",
    "name": "Rimuru",
    "title": "The Nameless Slime",
    "route": "The Devouring Path",
    "resource": "magicules",
    "resource_label": "Magicules",
    "ability": "Predator",
    "ability_text": "Weakened creatures can be devoured, while defeated monsters may choose to become allies.",
    "base": {"hp": 32, "mana": 18, "attack": 3, "defense": 1, "speed": 4},
}

# ============================================================
# Action types:
#   "timed"   — one-shot timed action (existing behaviour)
#   "loop"    — runs indefinitely in the background until stopped
#   "instant" — instantly trades one resource for another
#   "upgrade" — permanently increases caps/stats/abilities
#   "next"    — story checkpoint requiring resource accumulation
# ============================================================

ACTIONS = {
    # --- Timed actions (existing) ---
    "gather_dew": {"id": "gather_dew", "name": "Gather Cave Dew", "description": "Absorb mineral-rich water from the cavern walls.", "type": "timed", "duration": 3, "difficulty": "Simple", "xp": 3, "magicules": 3, "insight": 0, "heal": 3},
    "analyze_moss": {"id": "analyze_moss", "name": "Analyze Glowing Moss", "description": "Ask the inner voice to identify a simple organism.", "type": "timed", "duration": 6, "difficulty": "Measured", "xp": 6, "magicules": 2, "insight": 2, "heal": 0},
    "shape_body": {"id": "shape_body", "name": "Practice Shapeshifting", "description": "Learn to harden, stretch, and reform your slime body.", "type": "timed", "duration": 9, "difficulty": "Demanding", "xp": 9, "magicules": 2, "insight": 1, "heal": 0, "training": "attack"},
    "follow_roar": {"id": "follow_roar", "name": "Follow the Distant Roar", "description": "Trace the overwhelming presence deeper into the cave.", "type": "timed", "duration": 11, "difficulty": "Demanding", "xp": 12, "magicules": 4, "insight": 2, "heal": 0},
    "silent_scout": {"id": "silent_scout", "name": "Scout Through Vibrations", "description": "Map nearby tunnels without revealing your presence.", "type": "timed", "duration": 13, "difficulty": "Complex", "xp": 14, "magicules": 3, "insight": 4, "heal": 0},
    "magicule_circulation": {"id": "magicule_circulation", "name": "Learn Magicule Circulation", "description": "Practice Veldora's method for moving energy through your body.", "type": "timed", "duration": 15, "difficulty": "Complex", "xp": 18, "magicules": 7, "insight": 3, "heal": 5, "training": "mana"},
    "talk_goblins": {"id": "talk_goblins", "name": "Talk with the Goblins", "description": "Learn names, fears, skills, and what the village needs most.", "type": "timed", "duration": 7, "difficulty": "Social", "xp": 8, "magicules": 1, "insight": 4, "heal": 0, "friendship": {"goblin_village": 1}},
    "train_allies": {"id": "train_allies", "name": "Train with Your Allies", "description": "Practice coordinated attacks with the active party.", "type": "timed", "duration": 18, "difficulty": "Intense", "xp": 22, "magicules": 4, "insight": 2, "heal": 0, "party_training": True},

    # --- Loop actions (background, run until stopped) ---
    "rest_loop": {"id": "rest_loop", "name": "Rest", "description": "Recover HP and Mana continuously in the background.", "type": "loop", "interval": 5, "xp": 1, "magicules": 0, "heal": 4, "mana_regen": 3, "unlock_level": 1},
    "farmwork": {"id": "farmwork", "name": "Farmwork", "description": "Tend the village fields for steady gold and magicules.", "type": "loop", "interval": 8, "xp": 2, "magicules": 2, "gold": 1, "unlock_level": 2},
    "meditation": {"id": "meditation", "name": "Meditation", "description": "Focus your mind to generate Insight and recover Mana.", "type": "loop", "interval": 10, "xp": 3, "insight": 1, "mana_regen": 2, "unlock_level": 3},
    "hunting": {"id": "hunting", "name": "Hunting", "description": "Hunt small game for gold and occasional research.", "type": "loop", "interval": 12, "xp": 4, "gold": 2, "research": 1, "unlock_level": 4},
    "worship": {"id": "worship", "name": "Worship", "description": "Offer prayers to the Great Sage for passive XP and magicules.", "type": "loop", "interval": 15, "xp": 5, "magicules": 3, "unlock_level": 5},
    "village_building": {"id": "village_building", "name": "Village Building", "description": "Construct homes, walls, and workshops for the goblin village.", "type": "loop", "interval": 12, "xp": 4, "magicules": 3, "gold": 2, "unlock_level": 6},
    "blacksmithing": {"id": "blacksmithing", "name": "Blacksmithing", "description": "Forge weapons and tools with the dwarves.", "type": "loop", "interval": 14, "xp": 5, "gold": 3, "magicules": 2, "unlock_level": 8},
    "diplomacy": {"id": "diplomacy", "name": "Diplomacy", "description": "Strengthen ties with neighboring nations.", "type": "loop", "interval": 18, "xp": 6, "insight": 2, "friendship": {"tempest_federation": 1}, "unlock_level": 10},

    # --- Instant actions (instant resource trades) ---
    "get_motivated": {"id": "get_motivated", "name": "Get Motivated!", "description": "Convert 5 Focus into 3 Magicules instantly.", "type": "instant", "focus_cost": 5, "magicules": 3, "cooldown": 10, "unlock_level": 1},
    "quick_trade": {"id": "quick_trade", "name": "Quick Trade", "description": "Trade 10 gold for 4 Magicules instantly.", "type": "instant", "gold_cost": 10, "magicules": 4, "cooldown": 15, "unlock_level": 2},
    "scavenge": {"id": "scavenge", "name": "Scavenge", "description": "Search the area for instant gold and insight.", "type": "instant", "focus_cost": 3, "gold": 2, "insight": 1, "cooldown": 20, "unlock_level": 3},
    "devour": {"id": "devour", "name": "Devour", "description": "Use Predator to consume stored magicules for instant power.", "type": "instant", "magicules_cost": 15, "xp": 10, "cooldown": 30, "unlock_level": 4},
    "negotiate": {"id": "negotiate", "name": "Negotiate", "description": "Use diplomacy to instantly gain gold from trade agreements.", "type": "instant", "focus_cost": 8, "gold": 8, "insight": 2, "cooldown": 25, "unlock_level": 6},

    # --- Upgrade actions (permanent stat increases) ---
    "expand_body": {"id": "expand_body", "name": "Expand Body", "description": "Permanently increase Max HP by 10.", "type": "upgrade", "cost": {"magicules": 25}, "effect": {"max_hp": 10}, "unlock_level": 2},
    "deepen_mana": {"id": "deepen_mana", "name": "Deepen Mana Pool", "description": "Permanently increase Max Mana by 5.", "type": "upgrade", "cost": {"magicules": 20}, "effect": {"max_mana": 5}, "unlock_level": 2},
    "harden_body": {"id": "harden_body", "name": "Harden Body", "description": "Permanently increase Attack by 1.", "type": "upgrade", "cost": {"magicules": 30}, "effect": {"attack": 1}, "unlock_level": 3},
    "reinforce_defense": {"id": "reinforce_defense", "name": "Reinforce Defense", "description": "Permanently increase Defense by 1.", "type": "upgrade", "cost": {"magicules": 35}, "effect": {"defense": 1}, "unlock_level": 4},
    "expand_party": {"id": "expand_party", "name": "Expand Party", "description": "Increase active party slots by 1 (max 5).", "type": "upgrade", "cost": {"magicules": 50, "gold": 20}, "effect": {"party_slots": 1}, "unlock_level": 5},
    "passive_slot": {"id": "passive_slot", "name": "Unlock Passive Slot", "description": "Add a passive party slot for stat bonuses.", "type": "upgrade", "cost": {"magicules": 40, "gold": 15}, "effect": {"passive_slots": 1}, "unlock_level": 4},
    "unique_skill": {"id": "unique_skill", "name": "Awaken Unique Skill", "description": "Unlock a unique skill slot for powerful abilities.", "type": "upgrade", "cost": {"magicules": 100, "insight": 10}, "effect": {"unique_skill_slots": 1}, "unlock_level": 6},
    "ultimate_skill": {"id": "ultimate_skill", "name": "Awaken Ultimate Skill", "description": "Unlock an ultimate skill slot for god-like abilities.", "type": "upgrade", "cost": {"magicules": 300, "insight": 30}, "effect": {"ultimate_skill_slots": 1}, "unlock_level": 10},

    # --- Next actions (story checkpoints) ---
    "next_escape": {"id": "next_escape", "name": "Escape the Sealed Cave", "description": "Gather 50 Magicules to break through the cave's exit barrier.", "type": "next", "cost": {"magicules": 50}, "story_phase": "seek_dragon", "unlock_level": 1},
    "next_village": {"id": "next_village", "name": "Establish the Village", "description": "Gather 100 Magicules and 30 Gold to formalize the goblin village.", "type": "next", "cost": {"magicules": 100, "gold": 30}, "story_phase": "protect_village", "unlock_level": 3},
    "next_dwargon": {"id": "next_dwargon", "name": "Journey to Dwargon", "description": "Gather 150 Magicules and 50 Gold to fund the journey to the Dwarf Kingdom.", "type": "next", "cost": {"magicules": 150, "gold": 50}, "story_phase": "dwarf_kingdom", "unlock_level": 4},
    "next_orc_lord": {"id": "next_orc_lord", "name": "Prepare for the Orc Lord", "description": "Gather 250 Magicules and 100 Gold to arm the village against the Orc Lord.", "type": "next", "cost": {"magicules": 250, "gold": 100}, "story_phase": "orc_lord_arc", "unlock_level": 5},
    "next_lizardmen": {"id": "next_lizardmen", "name": "Forge the Lizardmen Alliance", "description": "Gather 300 Magicules and 150 Gold to cement the alliance.", "type": "next", "cost": {"magicules": 300, "gold": 150}, "story_phase": "lizardmen_alliance", "unlock_level": 6},
    "next_tempest": {"id": "next_tempest", "name": "Found the Tempest Federation", "description": "Gather 500 Magicules and 200 Gold to establish the nation.", "type": "next", "cost": {"magicules": 500, "gold": 200}, "story_phase": "tempest_federation", "unlock_level": 7},
    "next_falmuth": {"id": "next_falmuth", "name": "Open Relations with Falmuth", "description": "Gather 800 Magicules and 300 Gold to establish trade with the human kingdom.", "type": "next", "cost": {"magicules": 800, "gold": 300}, "story_phase": "falmuth_relations", "unlock_level": 8},
    "next_demon_lord": {"id": "next_demon_lord", "name": "Awaken as a Demon Lord", "description": "Gather 1500 Magicules and 500 Gold to undergo the Harvest Festival.", "type": "next", "cost": {"magicules": 1500, "gold": 500}, "story_phase": "demon_lord_awakening", "unlock_level": 10},
    "next_walpurgis": {"id": "next_walpurgis", "name": "Attend Walpurgis", "description": "Gather 2500 Magicules and 800 Gold to attend the Demon Lord council.", "type": "next", "cost": {"magicules": 2500, "gold": 800}, "story_phase": "walpurgis", "unlock_level": 12},
    "next_farmus": {"id": "next_farmus", "name": "Defeat the Farmus Invasion", "description": "Gather 4000 Magicules and 1200 Gold to repel the human invasion.", "type": "next", "cost": {"magicules": 4000, "gold": 1200}, "story_phase": "farmus_invasion", "unlock_level": 14},
    "next_harvest": {"id": "next_harvest", "name": "Harvest Festival", "description": "Gather 6000 Magicules and 2000 Gold to undergo the Harvest Festival.", "type": "next", "cost": {"magicules": 6000, "gold": 2000}, "story_phase": "harvest_festival", "unlock_level": 16},
    "next_epilogue": {"id": "next_epilogue", "name": "The Nation Thrives", "description": "Gather 10000 Magicules and 5000 Gold to complete the founding of Tempest.", "type": "next", "cost": {"magicules": 10000, "gold": 5000}, "story_phase": "epilogue", "unlock_level": 20},
}

SKILLS = [
    {"id": "slime_strike", "name": "Slime Strike", "description": "A simple body blow. Reliable, but deliberately modest.", "level": 1, "mana": 0, "power": 0.9},
    {"id": "sticky_thread", "name": "Sticky Thread", "description": "Bind the target and pierce part of its defense.", "level": 2, "mana": 3, "power": 1.35, "pierce": 0.35},
    {"id": "water_blade", "name": "Water Blade", "description": "A compressed edge of water with strong armor penetration.", "level": 4, "mana": 5, "power": 1.7, "pierce": 0.6},
    {"id": "predator", "name": "Predator", "description": "Devour a creature below 25% health for extra Magicules.", "level": 6, "mana": 8, "power": 0, "execute": 0.25},
    {"id": "black_lightning", "name": "Black Lightning", "description": "Veldora's signature attack — devastating dark lightning.", "level": 8, "mana": 12, "power": 2.5, "pierce": 0.4},
    {"id": "hellfire", "name": "Hellfire", "description": "A torrent of demonic flame that burns through armor.", "level": 10, "mana": 15, "power": 3.0, "pierce": 0.5},
    {"id": "beelzebub", "name": "Beelzebub", "description": "The ultimate skill of gluttony — devour anything.", "level": 12, "mana": 20, "power": 4.0, "execute": 0.4},
    {"id": "azathoth", "name": "Azathoth", "description": "The ultimate skill of void — erase existence itself.", "level": 16, "mana": 30, "power": 6.0, "execute": 0.5},
]

ALLIES = {
    "cave_bat": {"id": "cave_bat", "name": "Echo Bat", "species": "Cave Bat", "role": "Scout", "attack": 2, "defense": 0, "support": "Keen Echo: slightly improves party speed."},
    "acid_slug": {"id": "acid_slug", "name": "Melu", "species": "Acid Slug", "role": "Debuffer", "attack": 2, "defense": 1, "support": "Corrosive Trail: weakens enemy armor."},
    "armored_spider": {"id": "armored_spider", "name": "Needle", "species": "Armored Spider", "role": "Guardian", "attack": 2, "defense": 2, "support": "Silk Guard: adds party defense."},
    "cave_centipede": {"id": "cave_centipede", "name": "Carapace", "species": "Armored Centipede", "role": "Vanguard", "attack": 4, "defense": 3, "support": "Many-Legged Charge: adds attack and defense."},
    "horned_rabbit": {"id": "horned_rabbit", "name": "Piko", "species": "Horned Rabbit", "role": "Striker", "attack": 4, "defense": 0, "support": "Sudden Lunge: adds party attack."},
    "direwolf": {"id": "direwolf", "name": "Ranga's Kin", "species": "Direwolf", "role": "Hunter", "attack": 5, "defense": 1, "support": "Pack Hunt: grows stronger beside other allies."},
    "forest_lizard": {"id": "forest_lizard", "name": "Seki", "species": "Forest Lizard", "role": "Skirmisher", "attack": 3, "defense": 2, "support": "Scale Screen: adds balanced protection."},
    "fang_captain": {"id": "fang_captain", "name": "Ranga", "species": "Tempest Wolf", "role": "Pack Leader", "attack": 7, "defense": 3, "support": "Tempest Howl: greatly strengthens the party."},
    "marsh_frog": {"id": "marsh_frog", "name": "Gama", "species": "Giant Marsh Frog", "role": "Controller", "attack": 4, "defense": 2, "support": "Binding Tongue: disrupts enemy attacks."},
    # --- New allies from the anime ---
    "gobta": {"id": "gobta", "name": "Gobta", "species": "Goblin", "role": "Scout", "attack": 3, "defense": 1, "support": "Goblin Cunning: improves scouting and speed."},
    "rigurd": {"id": "rigurd", "name": "Rigurd", "species": "Goblin", "role": "Commander", "attack": 4, "defense": 2, "support": "Goblin Command: boosts party coordination."},
    "hakuro": {"id": "hakuro", "name": "Hakuro", "species": "Kijin", "role": "Swordmaster", "attack": 8, "defense": 4, "support": "Sword Saint: greatly increases party attack."},
    "shion": {"id": "shion", "name": "Shion", "species": "Kijin", "role": "Berserker", "attack": 9, "defense": 3, "support": "Berserk Strength: massive attack boost."},
    "shuna": {"id": "shuna", "name": "Shuna", "species": "Kijin", "role": "Support", "attack": 4, "defense": 3, "support": "Divine Protection: boosts party defense and healing."},
    "benimaru": {"id": "benimaru", "name": "Benimaru", "species": "Kijin", "role": "Flame General", "attack": 10, "defense": 4, "support": "Flame Control: powerful attack and defense boost."},
    "souei": {"id": "souei", "name": "Souei", "species": "Kijin", "role": "Shadow Assassin", "attack": 8, "defense": 3, "support": "Shadow Step: greatly improves speed and evasion."},
    "gabiru": {"id": "gabiru", "name": "Gabiru", "species": "Lizardman", "role": "Dragon Knight", "attack": 7, "defense": 4, "support": "Dragon Blood: boosts attack and defense."},
    "geld": {"id": "geld", "name": "Geld", "species": "Orc", "role": "Tank", "attack": 6, "defense": 8, "support": "Orc Wall: massive defense boost."},
    "diablo": {"id": "diablo", "name": "Diablo", "species": "Primordial Demon", "role": "Demon Lord", "attack": 12, "defense": 6, "support": "Primordial Power: massive all-stat boost."},
    "veldora": {"id": "veldora", "name": "Veldora", "species": "Storm Dragon", "role": "True Dragon", "attack": 15, "defense": 8, "support": "Storm Dragon: overwhelming power."},
}

ZONES = {
    "sealed_cave": {
        "id": "sealed_cave", "name": "Sealed Cave", "subtitle": "Five encounters between you and the thunderous voice", "total_encounters": 5,
        "enemies": [
            {"name": "Cave Bat", "ally_id": "cave_bat", "strength": 4, "hp": 13, "attack": 2, "defense": 0, "xp": 5, "gold": 1, "magicules": 2, "research": 1},
            {"name": "Acid Slug", "ally_id": "acid_slug", "strength": 6, "hp": 17, "attack": 3, "defense": 1, "xp": 7, "gold": 2, "magicules": 3, "research": 2},
            {"name": "Armored Spider", "ally_id": "armored_spider", "strength": 7, "hp": 20, "attack": 3, "defense": 2, "xp": 8, "gold": 2, "magicules": 3, "research": 2},
        ],
        "boss": {"name": "Armored Centipede", "ally_id": "cave_centipede", "strength": 13, "hp": 39, "attack": 5, "defense": 2, "xp": 22, "gold": 6, "magicules": 8, "research": 5},
    },
    "forest_road": {
        "id": "forest_road", "name": "Forest Road", "subtitle": "Five encounters on the road to the goblin village", "total_encounters": 5,
        "enemies": [
            {"name": "Horned Rabbit", "ally_id": "horned_rabbit", "strength": 8, "hp": 24, "attack": 4, "defense": 1, "xp": 10, "gold": 3, "magicules": 4, "research": 2},
            {"name": "Direwolf Scout", "ally_id": "direwolf", "strength": 10, "hp": 29, "attack": 5, "defense": 2, "xp": 12, "gold": 4, "magicules": 5, "research": 3},
            {"name": "Forest Lizard", "ally_id": "forest_lizard", "strength": 11, "hp": 32, "attack": 5, "defense": 3, "xp": 13, "gold": 4, "magicules": 5, "research": 3},
        ],
        "boss": {"name": "Fang Captain", "ally_id": "fang_captain", "strength": 19, "hp": 64, "attack": 8, "defense": 4, "xp": 35, "gold": 12, "magicules": 12, "research": 8},
    },
    "lizard_marsh": {
        "id": "lizard_marsh", "name": "Lizard Marsh", "subtitle": "A repeatable expedition beyond the safety of the village", "total_encounters": 5,
        "enemies": [
            {"name": "Giant Marsh Frog", "ally_id": "marsh_frog", "strength": 13, "hp": 38, "attack": 6, "defense": 3, "xp": 16, "gold": 5, "magicules": 6, "research": 4},
            {"name": "Mud Crawler", "ally_id": None, "strength": 14, "hp": 42, "attack": 6, "defense": 4, "xp": 17, "gold": 6, "magicules": 7, "research": 4},
            {"name": "Poison Newt", "ally_id": None, "strength": 15, "hp": 39, "attack": 7, "defense": 3, "xp": 18, "gold": 6, "magicules": 7, "research": 5},
        ],
        "boss": {"name": "Marsh Basilisk", "ally_id": None, "strength": 24, "hp": 82, "attack": 10, "defense": 5, "xp": 48, "gold": 16, "magicules": 16, "research": 12},
    },
    "ancient_ruins": {
        "id": "ancient_ruins", "name": "Ancient Ruins", "subtitle": "A dangerous, artifact-filled ruin — six encounters of growing peril", "total_encounters": 6,
        "enemies": [
            {"name": "Dust Wight", "ally_id": None, "strength": 12, "hp": 36, "attack": 5, "defense": 2, "xp": 18, "gold": 6, "magicules": 5, "research": 5},
            {"name": "Clockwork Scarab", "ally_id": None, "strength": 14, "hp": 40, "attack": 6, "defense": 3, "xp": 20, "gold": 7, "magicules": 6, "research": 6},
            {"name": "Stone Golemling", "ally_id": None, "strength": 16, "hp": 48, "attack": 7, "defense": 5, "xp": 24, "gold": 9, "magicules": 8, "research": 7},
            {"name": "Relic Guardian", "ally_id": None, "strength": 18, "hp": 56, "attack": 8, "defense": 6, "xp": 28, "gold": 11, "magicules": 10, "research": 8},
        ],
        "boss": {"name": "Ruins Sentinel", "ally_id": None, "strength": 28, "hp": 120, "attack": 12, "defense": 8, "xp": 80, "gold": 28, "magicules": 28, "research": 20},
    },
    # --- New zones from the anime ---
    "dwargon": {
        "id": "dwargon", "name": "Dwarf Kingdom Dwargon", "subtitle": "The mountain kingdom of the dwarves — six encounters of steel and stone", "total_encounters": 6,
        "enemies": [
            {"name": "Dwarf Guard", "ally_id": None, "strength": 15, "hp": 45, "attack": 7, "defense": 5, "xp": 22, "gold": 8, "magicules": 8, "research": 6},
            {"name": "Iron Golem", "ally_id": None, "strength": 17, "hp": 55, "attack": 8, "defense": 7, "xp": 26, "gold": 10, "magicules": 10, "research": 7},
            {"name": "Mountain Troll", "ally_id": None, "strength": 19, "hp": 60, "attack": 9, "defense": 5, "xp": 30, "gold": 12, "magicules": 12, "research": 8},
        ],
        "boss": {"name": "Dwarf King Gazel", "ally_id": None, "strength": 30, "hp": 140, "attack": 14, "defense": 10, "xp": 100, "gold": 40, "magicules": 40, "research": 25},
    },
    "orc_territory": {
        "id": "orc_territory", "name": "Orc Territory", "subtitle": "The Orc Lord's domain — seven encounters of overwhelming hunger", "total_encounters": 7,
        "enemies": [
            {"name": "Orc Warrior", "ally_id": None, "strength": 18, "hp": 55, "attack": 8, "defense": 4, "xp": 28, "gold": 10, "magicules": 10, "research": 7},
            {"name": "Orc Berserker", "ally_id": None, "strength": 20, "hp": 65, "attack": 10, "defense": 4, "xp": 32, "gold": 12, "magicules": 12, "research": 8},
            {"name": "Orc Shaman", "ally_id": None, "strength": 22, "hp": 50, "attack": 9, "defense": 5, "xp": 35, "gold": 14, "magicules": 14, "research": 9},
        ],
        "boss": {"name": "Orc Lord Geld", "ally_id": "geld", "strength": 35, "hp": 180, "attack": 16, "defense": 12, "xp": 150, "gold": 60, "magicules": 60, "research": 35},
    },
    "lizardmen_territory": {
        "id": "lizardmen_territory", "name": "Lizardmen Territory", "subtitle": "The marshlands of the lizardmen — six encounters of scales and fangs", "total_encounters": 6,
        "enemies": [
            {"name": "Lizardman Warrior", "ally_id": None, "strength": 20, "hp": 60, "attack": 9, "defense": 5, "xp": 30, "gold": 12, "magicules": 12, "research": 8},
            {"name": "Lizardman Spearman", "ally_id": None, "strength": 22, "hp": 55, "attack": 10, "defense": 5, "xp": 34, "gold": 14, "magicules": 14, "research": 9},
            {"name": "Lizardman Shaman", "ally_id": None, "strength": 24, "hp": 50, "attack": 10, "defense": 6, "xp": 38, "gold": 16, "magicules": 16, "research": 10},
        ],
        "boss": {"name": "Lizardman Chief Gabiru", "ally_id": "gabiru", "strength": 38, "hp": 200, "attack": 18, "defense": 12, "xp": 180, "gold": 70, "magicules": 70, "research": 40},
    },
    "tempest_forest": {
        "id": "tempest_forest", "name": "Great Jura Forest", "subtitle": "The vast forest of Tempest — eight encounters of wild danger", "total_encounters": 8,
        "enemies": [
            {"name": "Forest Wyrm", "ally_id": None, "strength": 25, "hp": 70, "attack": 11, "defense": 6, "xp": 40, "gold": 16, "magicules": 16, "research": 10},
            {"name": "Giant Bear", "ally_id": None, "strength": 27, "hp": 80, "attack": 12, "defense": 7, "xp": 45, "gold": 18, "magicules": 18, "research": 11},
            {"name": "Forest Treant", "ally_id": None, "strength": 29, "hp": 90, "attack": 10, "defense": 10, "xp": 50, "gold": 20, "magicules": 20, "research": 12},
        ],
        "boss": {"name": "Forest Guardian", "ally_id": None, "strength": 45, "hp": 250, "attack": 20, "defense": 15, "xp": 250, "gold": 100, "magicules": 100, "research": 50},
    },
    "falmuth": {
        "id": "falmuth", "name": "Kingdom of Falmuth", "subtitle": "The human kingdom — seven encounters of political and martial danger", "total_encounters": 7,
        "enemies": [
            {"name": "Falmuth Knight", "ally_id": None, "strength": 28, "hp": 75, "attack": 12, "defense": 8, "xp": 45, "gold": 20, "magicules": 20, "research": 12},
            {"name": "Falmuth Mage", "ally_id": None, "strength": 30, "hp": 60, "attack": 13, "defense": 6, "xp": 50, "gold": 22, "magicules": 22, "research": 13},
            {"name": "Royal Guard", "ally_id": None, "strength": 32, "hp": 85, "attack": 14, "defense": 10, "xp": 55, "gold": 25, "magicules": 25, "research": 14},
        ],
        "boss": {"name": "Falmuth King", "ally_id": None, "strength": 50, "hp": 300, "attack": 22, "defense": 15, "xp": 300, "gold": 150, "magicules": 150, "research": 60},
    },
    "demon_lord_domain": {
        "id": "demon_lord_domain", "name": "Demon Lord's Domain", "subtitle": "The dark realm of the Demon Lords — ten encounters of ultimate peril", "total_encounters": 10,
        "enemies": [
            {"name": "Demon Knight", "ally_id": None, "strength": 35, "hp": 100, "attack": 15, "defense": 10, "xp": 70, "gold": 30, "magicules": 30, "research": 15},
            {"name": "Demon General", "ally_id": None, "strength": 40, "hp": 120, "attack": 18, "defense": 12, "xp": 85, "gold": 35, "magicules": 35, "research": 18},
            {"name": "Demon Lord's Herald", "ally_id": None, "strength": 45, "hp": 140, "attack": 20, "defense": 14, "xp": 100, "gold": 40, "magicules": 40, "research": 20},
        ],
        "boss": {"name": "Demon Lord Clayman", "ally_id": None, "strength": 60, "hp": 400, "attack": 25, "defense": 18, "xp": 500, "gold": 200, "magicules": 200, "research": 80},
    },
}

# ============================================================
# Research & Summoning
# Each enemy type has a research cost to summon as a permanent ally.
# ============================================================
RESEARCH_COSTS = {
    "cave_bat": 5,
    "acid_slug": 8,
    "armored_spider": 10,
    "cave_centipede": 15,
    "horned_rabbit": 12,
    "direwolf": 15,
    "forest_lizard": 15,
    "fang_captain": 25,
    "marsh_frog": 20,
    "gobta": 15,
    "rigurd": 20,
    "hakuro": 40,
    "shion": 50,
    "shuna": 45,
    "benimaru": 60,
    "souei": 50,
    "gabiru": 55,
    "geld": 70,
    "diablo": 100,
    "veldora": 150,
}

# ============================================================
# Prestige — Dark Ritual
# Soft reset that converts progress into Habit Points & Inspiration.
# ============================================================
DARK_RITUAL = {
    "min_level": 5,
    "habit_per_level": 1,
    "inspiration_per_10_levels": 1,
    "description": "Sacrifice your current rank to gain permanent multipliers through Habits and Astral upgrades.",
}

# ============================================================
# Astral World Upgrades (spend Inspiration)
# ============================================================
ASTRAL_UPGRADES = {
    "doppelganger": {
        "id": "doppelganger", "name": "Doppelganger", "description": "Run a Loop Action and a Dungeon simultaneously.",
        "cost": 3, "max_level": 1, "effect": "dual_activity",
    },
    "soul_amplifier": {
        "id": "soul_amplifier", "name": "Soul Amplifier", "description": "+10% Magicules from all sources per level.",
        "cost": 2, "max_level": 5, "effect": "magicule_multiplier", "per_level": 0.10,
    },
    "eternal_insight": {
        "id": "eternal_insight", "name": "Eternal Insight", "description": "+1 Insight per level from all actions.",
        "cost": 2, "max_level": 5, "effect": "insight_bonus", "per_level": 1,
    },
    "golden_touch": {
        "id": "golden_touch", "name": "Golden Touch", "description": "+10% Gold from all sources per level.",
        "cost": 2, "max_level": 5, "effect": "gold_multiplier", "per_level": 0.10,
    },
    "predator_essence": {
        "id": "predator_essence", "name": "Predator Essence", "description": "+5% Attack per level.",
        "cost": 3, "max_level": 5, "effect": "attack_multiplier", "per_level": 0.05,
    },
    "unbreakable_slime": {
        "id": "unbreakable_slime", "name": "Unbreakable Slime", "description": "+5% Max HP per level.",
        "cost": 3, "max_level": 5, "effect": "hp_multiplier", "per_level": 0.05,
    },
    "great_sage": {
        "id": "great_sage", "name": "Great Sage", "description": "Unlock the Great Sage — +1 Insight and +5% XP per level.",
        "cost": 4, "max_level": 3, "effect": "great_sage", "per_level": 0.05,
    },
    "ragnarok": {
        "id": "ragnarok", "name": "Ragnarok", "description": "Unlock Veldora's power — +10% Attack and +10% Max HP per level.",
        "cost": 5, "max_level": 3, "effect": "ragnarok", "per_level": 0.10,
    },
}

# ============================================================
# Reincarnation Classes
# ============================================================
REINCARNATION_CLASSES = {
    "warrior": {
        "id": "warrior", "name": "Warrior", "description": "A martial path focused on raw attack power.",
        "base_bonus": {"attack": 3, "max_hp": 15},
        "per_reincarnation": {"attack": 1, "max_hp": 5},
    },
    "sorcerer": {
        "id": "sorcerer", "name": "Sorcerer", "description": "A magical path focused on mana and skills.",
        "base_bonus": {"max_mana": 10, "attack": 1},
        "per_reincarnation": {"max_mana": 3, "attack": 1},
    },
    "tamer": {
        "id": "tamer", "name": "Tamer", "description": "A bond-focused path that strengthens allies.",
        "base_bonus": {"max_hp": 8, "defense": 2},
        "per_reincarnation": {"max_hp": 3, "defense": 1},
    },
    "demon_lord": {
        "id": "demon_lord", "name": "Demon Lord", "description": "A path of overwhelming power and authority.",
        "base_bonus": {"attack": 5, "max_hp": 20, "max_mana": 10},
        "per_reincarnation": {"attack": 2, "max_hp": 8, "max_mana": 3},
    },
    "true_dragon": {
        "id": "true_dragon", "name": "True Dragon", "description": "The ultimate path — become a being of primordial power.",
        "base_bonus": {"attack": 8, "max_hp": 30, "max_mana": 15, "defense": 3},
        "per_reincarnation": {"attack": 3, "max_hp": 10, "max_mana": 5, "defense": 1},
    },
}

# ============================================================
# Sin System
# ============================================================
SINS = {
    "gluttony": {
        "id": "gluttony", "name": "Gluttony", "description": "Consume food drops automatically for stat modifiers.",
        "unlock_level": 8,
    },
    "sloth": {
        "id": "sloth", "name": "Sloth", "description": "Loop actions become more efficient.",
        "unlock_level": 10,
    },
    "greed": {
        "id": "greed", "name": "Greed", "description": "Gold gains are amplified.",
        "unlock_level": 12,
    },
    "pride": {
        "id": "pride", "name": "Pride", "description": "XP gains are amplified.",
        "unlock_level": 14,
    },
    "envy": {
        "id": "envy", "name": "Envy", "description": "Research gains are amplified.",
        "unlock_level": 16,
    },
    "wrath": {
        "id": "wrath", "name": "Wrath", "description": "Attack power is amplified in combat.",
        "unlock_level": 18,
    },
    "lust": {
        "id": "lust", "name": "Lust", "description": "Recruitment chances are amplified.",
        "unlock_level": 20,
    },
}

# ============================================================
# Story Nodes — The full Tensei Shitara Slime Datta Ken arc
# ============================================================
STORY_NODES = {
    # ========== PROLOGUE: AWAKENING ==========
    "inner_voice": {
        "id": "inner_voice", "speaker": "Unknown Voice", "eyebrow": "PROLOGUE · A VOICE WITHOUT A BODY", "title": "Consciousness in the dark",
        "text": "You awaken without hands, lungs, or sight. A calm voice lists impossible abilities inside your mind. It waits for your first question.", "next_phase": "first_steps",
        "options": [
            {"id": "ask_guidance", "label": "“Tell me what I am.”", "description": "Trust the voice and learn through analysis.", "reply": "Answer: Slime. Unique constitution confirmed. Analysis assistance is available.", "result": "Analysis becomes part of your earliest survival strategy.", "unlock_actions": ["analyze_moss"], "branch": "Analytical"},
            {"id": "test_body", "label": "Test the strange new body", "description": "Learn through instinct and physical experimentation.", "reply": "Your body bends, rebounds, and reforms without pain. The voice records every result.", "result": "Shapeshifting becomes your first deliberate discipline.", "unlock_actions": ["shape_body"], "branch": "Instinctive"},
        ],
    },
    "distant_roar": {
        "id": "distant_roar", "speaker": "Distant Voice", "eyebrow": "CHAPTER I · SOMETHING CALLS", "title": "Thunder beneath the mountain",
        "text": "After learning to move and feed, you feel a presence so vast that the entire cave seems to breathe with it. A lonely, arrogant roar demands to know who is creeping through its prison.", "next_phase": "seek_dragon",
        "options": [
            {"id": "answer_boldly", "label": "“Just a slime. Who are you?”", "description": "Answer openly and follow the voice directly.", "reply": "The roar becomes delighted laughter. ‘A slime with manners! Come closer, tiny one!’", "result": "The direct path into the Sealed Cave opens.", "unlock_actions": ["follow_roar"], "unlock_zones": ["sealed_cave"], "branch": "Bold"},
            {"id": "approach_carefully", "label": "Stay silent and investigate", "description": "Map the danger before revealing yourself.", "reply": "The voice keeps talking anyway, loudly criticizing your attempt at stealth.", "result": "Careful scouting reveals a safer route into the Sealed Cave.", "unlock_actions": ["silent_scout"], "unlock_zones": ["sealed_cave"], "branch": "Cautious"},
        ],
    },
    "meet_veldora": {
        "id": "meet_veldora", "speaker": "Veldora, the Storm Dragon", "eyebrow": "CHAPTER I · THE PRISONER", "title": "A dragon who wants a friend",
        "text": "Beyond the fifth guardian waits Veldora, sealed behind a shining barrier. His power is terrifying. His attempt at casual conversation is even more obvious than his loneliness.", "next_phase": "learn_from_friend",
        "options": [
            {"id": "offer_friendship", "label": "Offer friendship without conditions", "description": "Treat the feared dragon as a person first.", "reply": "Veldora freezes, then declares your friendship a legendary alliance that future ages will celebrate.", "result": "Veldora shares a method for circulating magicules and calls you his sworn friend.", "unlock_actions": ["magicule_circulation"], "friendship": {"veldora": 3}, "branch": "Sworn Friend"},
            {"id": "make_pact", "label": "Propose a pact to break the seal", "description": "Build trust around a shared objective.", "reply": "The dragon approves of your ambition. He agrees to teach you while you search for an answer together.", "result": "Veldora teaches magicule circulation and becomes your research partner.", "unlock_actions": ["magicule_circulation"], "friendship": {"veldora": 2}, "branch": "Research Pact"},
        ],
    },
    "veldora_analysis": {
        "id": "veldora_analysis", "speaker": "Veldora, the Storm Dragon", "eyebrow": "CHAPTER I · THE GREAT SAGE", "title": "Analyzing the Storm Dragon",
        "text": "Veldora suggests you analyze his unique skills. The Great Sage within you begins to work, cataloguing the Storm Dragon's immense power. This will take time, but the rewards are beyond imagination.", "next_phase": "learn_from_friend",
        "options": [
            {"id": "analyze_veldora", "label": "Analyze Veldora's skills", "description": "Spend time understanding the dragon's power.", "reply": "The Great Sage begins its work. Veldora's skills are vast and complex.", "result": "You begin to understand the Storm Dragon's abilities.", "unlock_actions": ["analyze_moss"], "friendship": {"veldora": 1}, "branch": "Scholar"},
            {"id": "ask_about_world", "label": "Ask about the outside world", "description": "Learn about the world beyond the cave.", "reply": "Veldora describes a world of monsters, humans, and Demon Lords.", "result": "You gain insight into the world's politics and dangers.", "insight": 5, "branch": "Inquisitive"},
        ],
    },
    "escape_cave": {
        "id": "escape_cave", "speaker": "Veldora, the Storm Dragon", "eyebrow": "CHAPTER I · THE ESCAPE", "title": "Breaking the seal",
        "text": "With Veldora's power analyzed and stored within you, the time has come to break the seal. Veldora's consciousness will reside within you while his body remains sealed. The barrier shatters as you devour the seal itself.", "next_phase": "first_steps",
        "options": [
            {"id": "devour_seal", "label": "Devour the seal", "description": "Use Predator to consume the barrier.", "reply": "The seal dissolves into your body. Veldora's voice echoes from within: ‘I'm counting on you, partner!’", "result": "Veldora's consciousness joins you. The cave exit is open.", "grant_ally": "veldora", "friendship": {"veldora": 5}, "branch": "Liberator"},
        ],
    },

    # ========== CHAPTER II: THE GOBLIN VILLAGE ==========
    "goblin_encounter": {
        "id": "goblin_encounter", "speaker": "Goblin Elder", "eyebrow": "CHAPTER II · PEOPLE OF THE FOREST", "title": "A village asks for help",
        "text": "Outside the cave, armed goblins surround you—then immediately kneel. Their elder explains that direwolves have begun hunting the village. They need strength, but they also need someone willing to listen.", "next_phase": "protect_village",
        "options": [
            {"id": "listen_first", "label": "Sit with them and hear every concern", "description": "Earn trust through patience before promising anything.", "reply": "The elder introduces the families one by one. Fear slowly gives way to cautious laughter.", "result": "Conversation with the village becomes a repeatable action, and the Forest Road opens.", "unlock_actions": ["talk_goblins"], "unlock_zones": ["forest_road"], "friendship": {"goblin_village": 3}, "branch": "Listener"},
            {"id": "promise_protection", "label": "Promise to defeat the direwolves", "description": "Give the frightened village immediate certainty.", "reply": "The elder bows with relief. Several young goblins volunteer to guide you through the forest.", "result": "Ally training and the Forest Road become available.", "unlock_actions": ["train_allies"], "unlock_zones": ["forest_road"], "friendship": {"goblin_village": 2}, "branch": "Protector"},
            {"id": "befriend_scout", "label": "Befriend a traveling scout", "description": "Spend time listening and offer food to a nervous scout.", "reply": "The scout brightens and decides to stick around.", "result": "A scout joins your side and teaches scouting tricks.", "grant_ally": "cave_bat", "unlock_actions": ["talk_goblins"], "friendship": {"goblin_village": 1}, "branch": "Scout"},
        ],
    },
    "wolf_decision": {
        "id": "wolf_decision", "speaker": "Fang Captain", "eyebrow": "CHAPTER II · AFTER THE HOWL", "title": "Victory does not decide the future",
        "text": "The direwolf captain lowers his head after the fifth encounter. The surviving pack waits for your judgment. The goblins want safety; the wolves want a leader strong enough to follow.", "next_phase": "chapter_one_complete",
        "options": [
            {"id": "unite_them", "label": "Invite the wolves into the village", "description": "Turn former enemies into neighbors and allies.", "reply": "The captain accepts a new name: Ranga. Goblin cheers mingle uneasily with wolf howls.", "result": "Ranga joins automatically. Joint training and the Lizard Marsh expedition unlock.", "unlock_actions": ["train_allies", "talk_goblins"], "unlock_zones": ["lizard_marsh"], "grant_ally": "fang_captain", "friendship": {"goblin_village": 2, "direwolf_pack": 3}, "branch": "Unifier"},
            {"id": "separate_peace", "label": "Grant the pack its own territory", "description": "Create peace without forcing either people together.", "reply": "The captain accepts your boundary and offers scouts whenever you call.", "result": "A direwolf scout joins. Joint training and the Lizard Marsh expedition unlock.", "unlock_actions": ["train_allies", "talk_goblins"], "unlock_zones": ["lizard_marsh"], "grant_ally": "direwolf", "friendship": {"goblin_village": 2, "direwolf_pack": 2}, "branch": "Mediator"},
        ],
    },
    "gobta_meeting": {
        "id": "gobta_meeting", "speaker": "Gobta", "eyebrow": "CHAPTER II · A CURIOUS GOBLIN", "title": "The goblin who wants to be strong",
        "text": "A young goblin named Gobta approaches you with a determined look. He's not the strongest, but he's clever and eager to prove himself. He asks to learn from you.", "next_phase": "protect_village",
        "options": [
            {"id": "train_gobta", "label": "Take Gobta as a student", "description": "Teach the young goblin the ways of combat.", "reply": "Gobta's eyes shine with determination. He trains harder than anyone.", "result": "Gobta joins your party as a scout.", "grant_ally": "gobta", "friendship": {"goblin_village": 1}, "branch": "Teacher"},
            {"id": "encourage", "label": "Encourage him to train with others", "description": "Let him grow alongside his fellow goblins.", "reply": "Gobta nods and joins the training group. He improves steadily.", "result": "The goblin village grows stronger as a whole.", "friendship": {"goblin_village": 2}, "branch": "Community"},
        ],
    },
    "rigurd_pledge": {
        "id": "rigurd_pledge", "speaker": "Rigurd", "eyebrow": "CHAPTER II · THE ELDER'S PLEDGE", "title": "A leader's loyalty",
        "text": "Rigurd, the goblin elder, kneels before you. He pledges the entire village's loyalty to you, asking only that you protect them and lead them into a better future.", "next_phase": "protect_village",
        "options": [
            {"id": "accept_pledge", "label": "Accept the village's loyalty", "description": "Become the leader of the goblin village.", "reply": "Rigurd smiles with relief. The goblins cheer your name.", "result": "Rigurd joins as your commander. The village is now under your protection.", "grant_ally": "rigurd", "friendship": {"goblin_village": 3}, "branch": "Leader"},
            {"id": "humble_accept", "label": "Accept humbly as an equal", "description": "Lead without demanding fealty.", "reply": "Rigurd is moved by your humility. The goblins respect you even more.", "result": "Rigurd joins as a friend and advisor.", "grant_ally": "rigurd", "friendship": {"goblin_village": 4}, "branch": "Friend"},
        ],
    },

    # ========== CHAPTER III: THE DWARF KINGDOM ==========
    "dwarf_kingdom": {
        "id": "dwarf_kingdom", "speaker": "Dwarf Merchant", "eyebrow": "CHAPTER III · THE MOUNTAIN KINGDOM", "title": "The road to Dwargon",
        "text": "A traveling dwarf merchant tells you of the great mountain kingdom of Dwargon, where the dwarves forge weapons of legend. He offers to guide you there — for a price.", "next_phase": "dwarf_kingdom",
        "options": [
            {"id": "hire_guide", "label": "Hire the merchant as a guide", "description": "Pay for safe passage to Dwargon.", "reply": "The merchant grins and leads you through the mountain passes.", "result": "The path to Dwargon opens.", "unlock_zones": ["dwargon"], "branch": "Pragmatic"},
            {"id": "travel_alone", "label": "Travel alone through the mountains", "description": "Face the dangers of the mountain road yourself.", "reply": "You navigate the treacherous passes, fighting off mountain beasts.", "result": "You arrive at Dwargon stronger from the journey.", "unlock_zones": ["dwargon"], "branch": "Independent"},
        ],
    },
    "meet_gazel": {
        "id": "meet_gazel", "speaker": "King Gazel Dwargo", "eyebrow": "CHAPTER III · THE DWARF KING", "title": "An audience with the king",
        "text": "King Gazel Dwargo, the ruler of Dwargon, studies you with sharp eyes. He has heard of the slime who leads monsters. He wants to know what you want from his kingdom.", "next_phase": "dwarf_kingdom",
        "options": [
            {"id": "seek_alliance", "label": "Seek a formal alliance", "description": "Propose a trade and defense agreement.", "reply": "Gazel strokes his beard thoughtfully. ‘An alliance with a slime... interesting.’", "result": "Trade relations with Dwargon are established.", "friendship": {"dwargon": 3}, "branch": "Diplomat"},
            {"id": "seek_blacksmiths", "label": "Request blacksmith training", "description": "Ask for dwarven smiths to teach your people.", "reply": "Gazel agrees to send smiths to your village in exchange for resources.", "result": "Blacksmithing becomes available as a loop action.", "unlock_actions": ["blacksmithing"], "friendship": {"dwargon": 2}, "branch": "Craftsman"},
            {"id": "prove_strength", "label": "Challenge the dwarven champion", "description": "Show your strength to earn respect.", "reply": "The dwarven champion steps forward. The crowd roars.", "result": "You prove your strength and earn the dwarves' respect.", "friendship": {"dwargon": 2}, "branch": "Warrior"},
        ],
    },
    "kaijin_meeting": {
        "id": "kaijin_meeting", "speaker": "Kaijin", "eyebrow": "CHAPTER III · THE MASTER SMITH", "title": "A smith's dream",
        "text": "Kaijin, a master dwarf smith, approaches you. He's heard of your village and dreams of forging weapons for a new nation. He asks to join you.", "next_phase": "dwarf_kingdom",
        "options": [
            {"id": "welcome_kaijin", "label": "Welcome Kaijin to the village", "description": "Accept the master smith into your community.", "reply": "Kaijin's hammer rings with joy. He begins work immediately.", "result": "Kaijin joins your village. Blacksmithing improves.", "friendship": {"dwargon": 2}, "branch": "Welcoming"},
            {"id": "ask_for_help", "label": "Ask Kaijin to train your people", "description": "Have him teach the goblins the art of smithing.", "reply": "Kaijin takes on apprentices. The forge fires burn bright.", "result": "Goblins learn blacksmithing. Village production increases.", "friendship": {"goblin_village": 2, "dwargon": 1}, "branch": "Teacher"},
        ],
    },

    # ========== CHAPTER IV: THE ORC LORD ==========
    "orc_lord_approach": {
        "id": "orc_lord_approach", "speaker": "Scout", "eyebrow": "CHAPTER IV · THE HUNGER", "title": "The Orc Lord's army",
        "text": "A scout rushes in with dire news. The Orc Lord's army is marching toward the forest, consuming everything in its path. The goblins and dwarves look to you for leadership.", "next_phase": "orc_lord_arc",
        "options": [
            {"id": "prepare_defense", "label": "Prepare the village's defenses", "description": "Fortify the village and train the defenders.", "reply": "Walls rise, weapons are forged, and warriors train day and night.", "result": "The village is fortified. The Orc Territory opens.", "unlock_zones": ["orc_territory"], "branch": "Defender"},
            {"id": "seek_allies", "label": "Seek allies against the Orc Lord", "description": "Send envoys to neighboring powers.", "reply": "Envoys return with promises of support from Dwargon and the lizardmen.", "result": "Allies are secured. The Orc Territory opens.", "unlock_zones": ["orc_territory"], "friendship": {"dwargon": 1, "lizardmen": 1}, "branch": "Diplomat"},
        ],
    },
    "orc_lord_defeat": {
        "id": "orc_lord_defeat", "speaker": "Orc Lord Geld", "eyebrow": "CHAPTER IV · THE FINAL BATTLE", "title": "The Orc Lord's end",
        "text": "The Orc Lord Geld stands before you, his body wracked with endless hunger. He was once a noble leader, corrupted by the Demon Lord Clayman's manipulation. He begs for release.", "next_phase": "orc_lord_arc",
        "options": [
            {"id": "devour_geld", "label": "Devour the Orc Lord", "description": "End his suffering and absorb his power.", "reply": "Geld's body dissolves into yours. His voice whispers: ‘Thank you... for ending this.’", "result": "You absorb the Orc Lord's power. His people are freed from his control.", "grant_ally": "geld", "branch": "Merciful"},
            {"id": "spare_geld", "label": "Try to save him", "description": "Refuse to kill him and seek another way.", "reply": "Geld's eyes widen. ‘You would... spare me?’", "result": "Geld is freed from Clayman's control and joins you.", "grant_ally": "geld", "friendship": {"orc_people": 3}, "branch": "Compassionate"},
        ],
    },

    # ========== CHAPTER V: THE LIZARDMEN ==========
    "lizardmen_meeting": {
        "id": "lizardmen_meeting", "speaker": "Gabiru", "eyebrow": "CHAPTER V · SCALES AND FANGS", "title": "The Lizardmen's pride",
        "text": "The lizardmen of the marshlands have heard of your victory over the Orc Lord. Their chief, Gabiru, is proud and skeptical. He demands to see your strength before considering an alliance.", "next_phase": "lizardmen_alliance",
        "options": [
            {"id": "duel_gabiru", "label": "Accept Gabiru's challenge", "description": "Prove your strength in single combat.", "reply": "Gabiru's spear flashes. Your body flows around it. He falls, impressed.", "result": "Gabiru acknowledges your strength and joins you.", "grant_ally": "gabiru", "friendship": {"lizardmen": 3}, "branch": "Challenger"},
            {"id": "offer_gifts", "label": "Offer gifts of alliance", "description": "Show goodwill through diplomacy.", "reply": "Gabiru is surprised by your generosity. The lizardmen accept your offer.", "result": "The lizardmen alliance is formed.", "friendship": {"lizardmen": 3}, "branch": "Diplomat"},
        ],
    },

    # ========== CHAPTER VI: THE KIJIN ==========
    "kijin_arrival": {
        "id": "kijin_arrival", "speaker": "Hakuro", "eyebrow": "CHAPTER VI · THE ONI", "title": "The Kijin's vengeance",
        "text": "Five powerful oni — Hakuro, Shion, Shuna, Benimaru, and Souei — arrive at your village. They were the guardians of the ogre village, destroyed by the Orc Lord. They seek vengeance and a new purpose.", "next_phase": "tempest_federation",
        "options": [
            {"id": "offer_shelter", "label": "Offer them a home", "description": "Give the Kijin a place to belong.", "reply": "Benimaru bows. ‘We will serve you, Lord Rimuru.’", "result": "The Kijin join your village.", "grant_ally": "benimaru", "friendship": {"kijin": 3}, "branch": "Shelter"},
            {"id": "offer_vengeance", "label": "Help them avenge their people", "description": "Promise to help them find justice.", "reply": "The Kijin's eyes burn with purpose. They pledge their blades to you.", "result": "The Kijin join as warriors seeking justice.", "grant_ally": "hakuro", "friendship": {"kijin": 3}, "branch": "Vengeance"},
        ],
    },
    "kijin_names": {
        "id": "kijin_names", "speaker": "Benimaru", "eyebrow": "CHAPTER VI · THE NAMING", "title": "Giving the Kijin names",
        "text": "The Kijin ask you to name them, granting them power through the act of naming. This is a sacred bond in the monster world — one that will tie their fates to yours forever.", "next_phase": "tempest_federation",
        "options": [
            {"id": "name_them", "label": "Name the Kijin", "description": "Grant them power through naming.", "reply": "Power surges through the Kijin as you name them. They grow stronger.", "result": "The Kijin are greatly empowered. Shion, Shuna, and Souei join.", "grant_ally": "shion", "friendship": {"kijin": 5}, "branch": "Namer"},
            {"id": "let_them_choose", "label": "Let them choose their own names", "description": "Respect their autonomy.", "reply": "The Kijin are moved by your respect. They choose names that honor you.", "result": "The Kijin join with deep loyalty.", "grant_ally": "shuna", "friendship": {"kijin": 4}, "branch": "Respectful"},
        ],
    },

    # ========== CHAPTER VII: THE TEMPEST FEDERATION ==========
    "tempest_founding": {
        "id": "tempest_founding", "speaker": "Rigurd", "eyebrow": "CHAPTER VII · A NEW NATION", "title": "The birth of Tempest",
        "text": "With goblins, dwarves, lizardmen, and Kijin united, the time has come to formally establish your nation. Rigurd proposes a name: the Jura Tempest Federation.", "next_phase": "tempest_federation",
        "options": [
            {"id": "accept_name", "label": "Accept the name Tempest", "description": "Found the Jura Tempest Federation.", "reply": "The name echoes through the forest. A nation is born.", "result": "The Tempest Federation is founded. Village building improves.", "unlock_actions": ["village_building"], "friendship": {"tempest_federation": 5}, "branch": "Founder"},
            {"id": "suggest_own", "label": "Suggest your own name", "description": "Choose a different name for the nation.", "reply": "The council considers your suggestion and agrees.", "result": "The nation is founded under your chosen name.", "friendship": {"tempest_federation": 4}, "branch": "Visionary"},
        ],
    },
    "diablo_summon": {
        "id": "diablo_summon", "speaker": "Diablo", "eyebrow": "CHAPTER VII · THE PRIMORDIAL", "title": "A demon's devotion",
        "text": "A primordial demon appears before you, drawn by your immense magicule output. He kneels and declares his eternal devotion. His name is Diablo, and he will serve no one else.", "next_phase": "tempest_federation",
        "options": [
            {"id": "accept_diablo", "label": "Accept Diablo's service", "description": "Welcome the primordial demon into your ranks.", "reply": "Diablo's smile is radiant. ‘I shall serve you for eternity, Lord Rimuru.’", "result": "Diablo joins your party. A truly powerful ally.", "grant_ally": "diablo", "branch": "Accepting"},
            {"id": "test_diablo", "label": "Test Diablo's loyalty", "description": "Challenge him to prove his devotion.", "reply": "Diablo defeats every challenger effortlessly, then returns to your side.", "result": "Diablo proves his worth and joins you.", "grant_ally": "diablo", "friendship": {"diablo": 3}, "branch": "Testing"},
        ],
    },

    # ========== CHAPTER VIII: FALMUTH ==========
    "falmuth_contact": {
        "id": "falmuth_contact", "speaker": "Falmuth Envoy", "eyebrow": "CHAPTER VIII · THE HUMAN KINGDOM", "title": "First contact with Falmuth",
        "text": "An envoy from the Kingdom of Falmuth arrives, demanding tribute and threatening military action if the monster nation refuses. The envoy's arrogance is palpable.", "next_phase": "falmuth_relations",
        "options": [
            {"id": "negotiate", "label": "Negotiate peacefully", "description": "Try to establish diplomatic relations.", "reply": "The envoy sneers but agrees to relay your terms.", "result": "Trade relations with Falmuth are tentatively established.", "friendship": {"falmuth": 1}, "branch": "Diplomat"},
            {"id": "stand_firm", "label": "Refuse the demands", "description": "Stand up to the human kingdom's threats.", "reply": "The envoy leaves in a huff, promising consequences.", "result": "Falmuth is angered but respects your resolve.", "friendship": {"falmuth": -1}, "branch": "Defiant"},
        ],
    },
    "falmuth_betrayal": {
        "id": "falmuth_betrayal", "speaker": "Souei", "eyebrow": "CHAPTER VIII · THE BETRAYAL", "title": "Shion's fate",
        "text": "Souei returns with terrible news. Falmuth has launched a surprise invasion. Shion and many of your people have been killed. The village is in flames.", "next_phase": "farmus_invasion",
        "options": [
            {"id": "rage", "label": "Let your rage consume you", "description": "Unleash your full power upon the invaders.", "reply": "Your magicules explode outward. The sky darkens. The invaders tremble.", "result": "You slaughter the Falmuth army. Your power is revealed to the world.", "branch": "Wrathful"},
            {"id": "grieve", "label": "Grieve and plan", "description": "Channel your pain into strategy.", "reply": "You hold Shion's body and make a silent vow. This will not be forgotten.", "result": "You plan a calculated response. The Falmuth invasion is repelled.", "branch": "Calculating"},
        ],
    },
    "shion_revival": {
        "id": "shion_revival", "speaker": "Great Sage", "eyebrow": "CHAPTER VIII · THE MIRACLE", "title": "A miracle of will",
        "text": "Your grief and determination awaken a unique power. The Great Sage analyzes Shion's soul and finds a way to restore her — through the power of your unique skill, you can rewrite her fate.", "next_phase": "farmus_invasion",
        "options": [
            {"id": "revive_shion", "label": "Revive Shion", "description": "Use your unique power to bring her back.", "reply": "Shion's eyes flutter open. ‘Rimuru... I knew you'd come for me.’", "result": "Shion is revived, stronger than before.", "grant_ally": "shion", "branch": "Miraculous"},
        ],
    },

    # ========== CHAPTER IX: DEMON LORD ==========
    "harvest_festival": {
        "id": "harvest_festival", "speaker": "Great Sage", "eyebrow": "CHAPTER IX · THE HARVEST FESTIVAL", "title": "Awakening as a Demon Lord",
        "text": "The Great Sage announces that you have accumulated enough magicules to undergo the Harvest Festival. This will transform you into a True Demon Lord, granting immense power — but it will also change you forever.", "next_phase": "demon_lord_awakening",
        "options": [
            {"id": "undergo_festival", "label": "Undergo the Harvest Festival", "description": "Accept the transformation into a Demon Lord.", "reply": "Power floods through you. The world trembles at your awakening.", "result": "You become a True Demon Lord. Your power is immense.", "branch": "Ascendant"},
            {"id": "delay", "label": "Delay the transformation", "description": "Wait until you are truly ready.", "reply": "The Great Sage acknowledges your caution. The power waits.", "result": "You postpone the transformation to prepare further.", "branch": "Patient"},
        ],
    },
    "walpurgis": {
        "id": "walpurgis", "speaker": "Demon Lord Council", "eyebrow": "CHAPTER IX · THE COUNCIL OF DEMON LORDS", "title": "Walpurgis",
        "text": "As a Demon Lord, you are summoned to Walpurgis — the council of Demon Lords. Clayman, the one who orchestrated the Orc Lord and Falmuth attacks, sits among them. The time for reckoning has come.", "next_phase": "walpurgis",
        "options": [
            {"id": "confront_clayman", "label": "Confront Clayman directly", "description": "Expose his schemes before the council.", "reply": "Clayman's mask of composure cracks. The council watches with interest.", "result": "Clayman is exposed. The council turns against him.", "branch": "Confrontational"},
            {"id": "play_patient", "label": "Play the long game", "description": "Gather evidence and strike at the right moment.", "reply": "You observe the council, learning their politics and weaknesses.", "result": "You gain insight into the Demon Lord council's dynamics.", "insight": 10, "branch": "Patient"},
        ],
    },
    "clayman_defeat": {
        "id": "clayman_defeat", "speaker": "Clayman", "eyebrow": "CHAPTER IX · THE PUPPET MASTER", "title": "Clayman's end",
        "text": "Clayman, cornered and desperate, reveals his true power. He was never a true Demon Lord — just a puppet of the mysterious 'Moderate Harlequin Alliance'. But his puppetry ends here.", "next_phase": "walpurgis",
        "options": [
            {"id": "devour_clayman", "label": "Devour Clayman", "description": "End him and absorb his power.", "reply": "Clayman's screams echo as he is consumed. The council is silent.", "result": "Clayman is destroyed. Your power grows.", "branch": "Devourer"},
            {"id": "expose_him", "label": "Expose his true nature", "description": "Reveal that he was never a true Demon Lord.", "reply": "The council examines Clayman and finds the truth. He is stripped of his title.", "result": "Clayman is disgraced and destroyed by the council.", "branch": "Revealer"},
        ],
    },

    # ========== CHAPTER X: THE FARMUS INVASION ==========
    "farmus_invasion": {
        "id": "farmus_invasion", "speaker": "Herald", "eyebrow": "CHAPTER X · THE INVASION", "title": "The human army marches",
        "text": "The Kingdom of Falmuth, manipulated by Clayman's remnants, launches a full-scale invasion of Tempest. Thousands of soldiers march toward your nation.", "next_phase": "farmus_invasion",
        "options": [
            {"id": "lead_defense", "label": "Lead the defense personally", "description": "Take command of the battlefield.", "reply": "Your presence on the battlefield turns the tide. The invaders break.", "result": "The Falmuth invasion is repelled.", "branch": "Commander"},
            {"id": "delegate", "label": "Let your generals lead", "description": "Trust your commanders to handle the defense.", "reply": "Benimaru, Shion, and the others lead the defense brilliantly.", "result": "The invasion is repelled with minimal losses.", "friendship": {"tempest_federation": 3}, "branch": "Trusting"},
        ],
    },
    "falmuth_peace": {
        "id": "falmuth_peace", "speaker": "Falmuth King", "eyebrow": "CHAPTER X · THE AFTERMATH", "title": "A kingdom's surrender",
        "text": "The Falmuth King, defeated and humbled, begs for mercy. His kingdom lies at your mercy. The world watches to see what kind of Demon Lord you will be.", "next_phase": "harvest_festival",
        "options": [
            {"id": "show_mercy", "label": "Show mercy to Falmuth", "description": "Spare the kingdom and demand reparations.", "reply": "The king weeps with relief. The world takes note of your mercy.", "result": "Falmuth becomes a vassal state. Trade relations are established.", "friendship": {"falmuth": 3}, "branch": "Merciful"},
            {"id": "demand_submission", "label": "Demand total submission", "description": "Make an example of the kingdom.", "reply": "The king signs a treaty of total submission. The world trembles.", "result": "Falmuth is subjugated. Your reputation as a Demon Lord grows.", "friendship": {"falmuth": -2}, "branch": "Dominant"},
        ],
    },

    # ========== EPILOGUE ==========
    "epilogue": {
        "id": "epilogue", "speaker": "Narrator", "eyebrow": "EPILOGUE · LEGENDS ARE WRITTEN", "title": "The story settles",
        "text": "The Jura Tempest Federation stands as a beacon of coexistence between monsters and humans. Veldora's consciousness stirs within you, ready for the next adventure. Your legend has only just begun.", "next_phase": "epilogue",
        "options": [
            {"id": "reflect", "label": "Take stock of your companions", "description": "Remember what you gained and who you lost.", "reply": "Memories pour forth; friendships are measured in small moments.", "result": "A gentle ending scene unfolds.", "branch": "Reflective"},
            {"id": "look_forward", "label": "Look toward the future", "description": "Consider what lies beyond the horizon.", "reply": "Veldora's voice echoes: ‘There's always another adventure, partner.’", "result": "The story continues beyond this chapter.", "branch": "Forward-looking"},
        ],
    },
}

# ============================================================
# Story Objectives
# ============================================================
STORY_OBJECTIVES = {
    "awakening": "Answer the mysterious voice inside your mind.",
    "first_steps": "Complete any 3 actions and learn how your slime body survives.",
    "seek_dragon": "Complete one five-encounter expedition through the Sealed Cave.",
    "learn_from_friend": "Complete Magicule Circulation twice to prepare an escape.",
    "protect_village": "Complete one five-encounter expedition through the Forest Road.",
    "chapter_one_complete": "Build a party, strengthen friendships, and explore the Lizard Marsh while Chapter III is written.",
    "dwarf_kingdom": "Journey to Dwargon and establish relations with the dwarves.",
    "orc_lord_arc": "Defeat the Orc Lord and free his people from Clayman's control.",
    "lizardmen_alliance": "Forge an alliance with the lizardmen of the marshlands.",
    "tempest_federation": "Found the Jura Tempest Federation and unite all monster races.",
    "falmuth_relations": "Establish diplomatic relations with the Kingdom of Falmuth.",
    "demon_lord_awakening": "Undergo the Harvest Festival and awaken as a True Demon Lord.",
    "walpurgis": "Attend the Demon Lord council and confront Clayman.",
    "farmus_invasion": "Repel the Falmuth invasion and secure your nation's future.",
    "harvest_festival": "Complete the Harvest Festival and cement your power.",
    "epilogue": "See how your choices reshape the world and your legend.",
}

# ============================================================
# Side Quests
# ============================================================
STORY_NODES.update({
    "lost_lantern": {
        "id": "lost_lantern",
        "speaker": "Cave Child",
        "eyebrow": "SIDE QUEST · A SMALL LIGHT",
        "title": "A lost lantern",
        "text": "A small goblin child drops a crude lantern deep in a side tunnel. They ask for help retrieving it before nightfall.",
        "next_phase": "chapter_one_complete",
        "options": [
            {"id": "retrieve", "label": "Search the side tunnel", "description": "A short search to show goodwill.", "reply": "You return with the charred lantern; the child's gratitude lingers.", "result": "A modest reward and a new friend; the goblin village remembers small kindnesses.", "friendship": {"goblin_village": 1}, "branch": "Good Samaritan"},
            {"id": "ignore", "label": "Ignore the child's plea", "description": "Time is short; you have larger goals.", "reply": "The child's eyes narrow but the village forgives with time.", "result": "A small regret lingers.", "branch": "Practical"},
        ],
    },
    "herbalist": {
        "id": "herbalist",
        "speaker": "Herbalist",
        "eyebrow": "SIDE QUEST · REMEDIES",
        "title": "Foraging for herbs",
        "text": "An elderly herbalist asks for help gathering dew and moss to replenish a salve for injured villagers.",
        "next_phase": "chapter_one_complete",
        "options": [
            {"id": "gather", "label": "Help gather herbs", "description": "Spend time to harvest vital ingredients.", "reply": "Your careful touch surprises the herbalist; a balm is brewed.", "result": "Max HP increases slightly and the herbalist offers healing tips.", "unlock_actions": ["gather_dew"], "branch": "Helper"},
            {"id": "decline_help", "label": "Decline politely", "description": "You can't spare the time.", "reply": "The herbalist understands but your conscience persistently nudges you.", "result": "No immediate reward.", "branch": "Busy"},
        ],
    },
    "bridge_repair": {
        "id": "bridge_repair",
        "speaker": "Bridge Foreman",
        "eyebrow": "SIDE QUEST · FIX THE ROAD",
        "title": "A broken bridge",
        "text": "A bridge along the Forest Road is damaged. Repairing it will make travel safer and win favor with merchants.",
        "next_phase": "protect_village",
        "options": [
            {"id": "repair", "label": "Help repair the bridge", "description": "Use your body to patch the crossing.", "reply": "The river calms; merchants sigh in relief.", "result": "Trade improves and a merchant contact is grateful.", "friendship": {"merchant_guild": 1}, "branch": "Builder"},
            {"id": "bypass", "label": "Find another route", "description": "Avoid the work and find a safer path.", "reply": "You find a hidden ford but the bridge remains broken for others.", "result": "No reward but a small shortcut is learned.", "branch": "Pathfinder"},
        ],
    },
    "merchant_offer": {
        "id": "merchant_offer",
        "speaker": "Traveling Merchant",
        "eyebrow": "SIDE QUEST · A DEAL TO MAKE",
        "title": "A merchant's offer",
        "text": "A merchant offers to trade useful trinkets for stories and favors. Helping them could grant unique items.",
        "next_phase": "alliance_paths",
        "options": [
            {"id": "trade_stories", "label": "Trade stories for goods", "description": "Share tales of your exploits.", "reply": "Your stories enthrall the merchant; rare goods are exchanged.", "result": "Receive a small trinket and a new contact.", "unlock_actions": [], "friendship": {"merchant_guild": 1}, "branch": "Storyteller"},
            {"id": "take_loan", "label": "Accept a risky loan", "description": "Take immediate gold in exchange for future favor.", "reply": "You receive coin; the merchant's smile is complicated.", "result": "You gain gold but a new obligation may follow.", "branch": "Opportunist"},
        ],
    },
    "bandit_contract": {
        "id": "bandit_contract",
        "speaker": "Mercenary Captain",
        "eyebrow": "SIDE QUEST · WORK FOR HIRE",
        "title": "A contract against bandits",
        "text": "A captain asks you to clear a bandit camp. Successful work earns pay and reputation among fighters.",
        "next_phase": "alliance_paths",
        "options": [
            {"id": "accept", "label": "Take the contract", "description": "Fight for coin and fame.", "reply": "You rout the bandits; the captain nods in approval.", "result": "Receive gold and mercenary friendship.", "friendship": {"mercenary_captain": 1}, "branch": "Contractor"},
            {"id": "refuse_contract", "label": "Refuse the work", "description": "You prefer not to be a hired blade.", "reply": "The captain shrugs; other opportunities remain.", "result": "No immediate change.", "branch": "Independent"},
        ],
    },
    "pond_rescue": {
        "id": "pond_rescue",
        "speaker": "Fisher",
        "eyebrow": "SIDE QUEST · A DROWNING",
        "title": "A trapped fish-folk",
        "text": "A fish-folk is trapped beneath tangled roots in a marsh pool. Freeing them could earn a unique ally.",
        "next_phase": "lizard_marsh",
        "options": [
            {"id": "rescue", "label": "Free the fish-folk", "description": "Use care and patience to liberate them.", "reply": "They sing a strange melody and promises of aid follow.", "result": "A water-friendly ally offers future help.", "grant_ally": "marsh_frog", "branch": "Rescuer"},
            {"id": "leave", "label": "Leave them be", "description": "You must press on.", "reply": "The pool remains silent as you go.", "result": "No reward.", "branch": "Practical"},
        ],
    },
    "ruins_cipher": {
        "id": "ruins_cipher",
        "speaker": "Ruins Echo",
        "eyebrow": "SIDE QUEST · BROKEN RIDDLE",
        "title": "A riddle carved in stone",
        "text": "At the Ancient Ruins you find a broken inscription. Deciphering it might reveal a shortcut or a secret treasure.",
        "next_phase": "alliance_paths",
        "options": [
            {"id": "decipher", "label": "Study the inscription", "description": "Use insight to understand the glyphs.", "reply": "Lines of meaning stitch together; a hidden chamber is hinted.", "result": "Gain Insight and hints toward an artifact.", "unlock_actions": ["analyze_moss"], "branch": "Scholar"},
            {"id": "press_on", "label": "Ignore the glyphs", "description": "Danger waits deeper in the ruin.", "reply": "You continue, but the stone's whisper haunts you.", "result": "No immediate effect.", "branch": "Bold"},
        ],
    },
    "ancient_relic": {
        "id": "ancient_relic",
        "speaker": "Ruins Keeper",
        "eyebrow": "SIDE QUEST · A TINY POWER",
        "title": "A hidden relic",
        "text": "Within a side chamber, a small relic hums with potential. It may grant a lasting bonus if used wisely.",
        "next_phase": "alliance_paths",
        "options": [
            {"id": "claim", "label": "Claim the relic", "description": "Accept the responsibility and its gift.", "reply": "The relic warms; small power flows through you.", "result": "Gain a permanent small HP and Mana bonus.", "branch": "Bearer"},
            {"id": "seal", "label": "Seal it away", "description": "Leave power undisturbed.", "reply": "The relic rests, unknown to most.", "result": "A secret remains.", "branch": "Custodian"},
        ],
    },
    "mercenary_trial": {
        "id": "mercenary_trial",
        "speaker": "Drill Sergeant",
        "eyebrow": "SIDE QUEST · TRIAL BY FIRE",
        "title": "A mercenary's trial",
        "text": "To gain the mercenaries' respect, you must complete a trial: endurance, cunning, or leadership.",
        "next_phase": "alliance_paths",
        "options": [
            {"id": "endurance", "label": "Endurance trial", "description": "Withstand a barrage and prove toughness.", "reply": "You endure and the mercenaries nod in respect.", "result": "Gain a mercenary friendship boost.", "friendship": {"mercenary_captain": 1}, "branch": "Endurer"},
            {"id": "lead", "label": "Leadership trial", "description": "Organize others and succeed.", "reply": "Your plans work; the band recognizes your mind.", "result": "Unlock training opportunities.", "unlock_actions": ["train_allies"], "branch": "Leader"},
        ],
    },
    "hidden_library": {
        "id": "hidden_library",
        "speaker": "Archivist",
        "eyebrow": "SIDE QUEST · DUSTY PAGES",
        "title": "A hidden library",
        "text": "A scholar in the capital hints at an overlooked alcove of old scrolls; studying them could grant new techniques.",
        "next_phase": "journey_to_capital",
        "options": [
            {"id": "study", "label": "Study the scrolls", "description": "Spend time in quiet research.", "reply": "Fragments of lore assemble into applied knowledge.", "result": "Unlock a research action and grant Insight.", "unlock_actions": ["analyze_moss"], "branch": "Scholar"},
            {"id": "shelve", "label": "Leave them undisturbed", "description": "Tomes sometimes hide curses.", "reply": "The scrolls remain, their secrets intact.", "result": "No immediate reward.", "branch": "Cautious"},
        ],
    },
    # --- New side quests from the anime ---
    "goblin_feast": {
        "id": "goblin_feast",
        "speaker": "Goblin Cook",
        "eyebrow": "SIDE QUEST · A FEAST FOR ALL",
        "title": "The great goblin feast",
        "text": "The goblins want to celebrate their new home with a grand feast. They need rare ingredients from the forest.",
        "next_phase": "protect_village",
        "options": [
            {"id": "hunt_feast", "label": "Hunt for rare ingredients", "description": "Venture into the forest for exotic game.", "reply": "You return with enough food to feed the entire village.", "result": "The feast is a success. Village morale soars.", "friendship": {"goblin_village": 2}, "branch": "Provider"},
            {"id": "donate_gold", "label": "Donate gold for supplies", "description": "Let the merchants handle the shopping.", "reply": "The merchants deliver everything needed for the feast.", "result": "The feast is a success. The village is grateful.", "friendship": {"goblin_village": 1, "merchant_guild": 1}, "branch": "Patron"},
        ],
    },
    "dwarf_weapon": {
        "id": "dwarf_weapon",
        "speaker": "Kaijin",
        "eyebrow": "SIDE QUEST · THE MASTERPIECE",
        "title": "A weapon worthy of legend",
        "text": "Kaijin wants to forge a legendary weapon for you. He needs rare ores from the deepest mines of Dwargon.",
        "next_phase": "dwarf_kingdom",
        "options": [
            {"id": "mine_ore", "label": "Mine the rare ores", "description": "Descend into the deep mines yourself.", "reply": "You return with gleaming ores that make Kaijin's eyes shine.", "result": "Kaijin forges a powerful weapon for you.", "friendship": {"dwargon": 2}, "branch": "Miner"},
            {"id": "buy_ore", "label": "Purchase the ores", "description": "Pay the dwarven merchants for the materials.", "reply": "The merchants deliver the ores. Kaijin begins his work.", "result": "Kaijin forges a powerful weapon for you.", "friendship": {"dwargon": 1, "merchant_guild": 1}, "branch": "Buyer"},
        ],
    },
    "kijin_training": {
        "id": "kijin_training",
        "speaker": "Hakuro",
        "eyebrow": "SIDE QUEST · THE SWORD SAINT",
        "title": "Training with the Sword Saint",
        "text": "Hakuro offers to train you in the way of the sword. His techniques are ancient and powerful.",
        "next_phase": "tempest_federation",
        "options": [
            {"id": "train_sword", "label": "Train with Hakuro", "description": "Learn the ancient sword techniques.", "reply": "Hakuro's blade moves like water. You learn quickly.", "result": "Your attack power increases permanently.", "branch": "Student"},
            {"id": "watch", "label": "Watch and learn", "description": "Observe Hakuro's techniques from afar.", "reply": "You study his movements carefully, absorbing what you can.", "result": "You gain insight into combat techniques.", "insight": 5, "branch": "Observer"},
        ],
    },
    "shion_cooking": {
        "id": "shion_cooking",
        "speaker": "Shion",
        "eyebrow": "SIDE QUEST · THE COOKING DISASTER",
        "title": "Shion's cooking",
        "text": "Shion insists on cooking for you. Her food is... an experience. You must find a way to survive her culinary enthusiasm.",
        "next_phase": "tempest_federation",
        "options": [
            {"id": "eat_bravely", "label": "Eat her cooking bravely", "description": "Face the culinary challenge head-on.", "reply": "You eat Shion's cooking. Your body shudders. You survive.", "result": "Shion is overjoyed. Your max HP increases from the ordeal.", "branch": "Brave"},
            {"id": "teach_cooking", "label": "Teach Shion to cook", "description": "Show her the basics of cooking.", "reply": "Shion takes notes seriously. Her next attempt is... slightly better.", "result": "Shion improves her cooking. Village morale improves.", "friendship": {"kijin": 2}, "branch": "Teacher"},
        ],
    },
    "diablo_errand": {
        "id": "diablo_errand",
        "speaker": "Diablo",
        "eyebrow": "SIDE QUEST · THE DEMON'S ERRAND",
        "title": "Diablo's request",
        "text": "Diablo asks to accompany you on a mission. He claims it's for your protection, but you suspect he just wants to show off.",
        "next_phase": "tempest_federation",
        "options": [
            {"id": "bring_diablo", "label": "Bring Diablo along", "description": "Let the demon accompany you.", "reply": "Diablo obliterates every threat before you can even react.", "result": "The mission is completed effortlessly. Diablo is pleased.", "friendship": {"diablo": 2}, "branch": "Companion"},
            {"id": "send_alone", "label": "Send Diablo alone", "description": "Let him handle it by himself.", "reply": "Diablo returns within minutes, mission complete.", "result": "Diablo proves his efficiency. The mission is done.", "friendship": {"diablo": 1}, "branch": "Delegator"},
        ],
    },
})

def hero_public() -> dict:
    return {key: value for key, value in HERO.items() if key != "base"} | {"stats": dict(HERO["base"])}

def recruitment_chance(strength: int) -> float:
    """Stronger creatures are more difficult to persuade after battle."""
    return round(max(0.04, min(0.32, 0.36 - (strength * 0.015))), 3)