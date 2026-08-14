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

ACTIONS = {
    "gather_dew": {"id": "gather_dew", "name": "Gather Cave Dew", "description": "Absorb mineral-rich water from the cavern walls.", "duration": 3, "difficulty": "Simple", "xp": 3, "magicules": 3, "insight": 0, "heal": 3},
    "analyze_moss": {"id": "analyze_moss", "name": "Analyze Glowing Moss", "description": "Ask the inner voice to identify a simple organism.", "duration": 6, "difficulty": "Measured", "xp": 6, "magicules": 2, "insight": 2, "heal": 0},
    "shape_body": {"id": "shape_body", "name": "Practice Shapeshifting", "description": "Learn to harden, stretch, and reform your slime body.", "duration": 9, "difficulty": "Demanding", "xp": 9, "magicules": 2, "insight": 1, "heal": 0, "training": "attack"},
    "follow_roar": {"id": "follow_roar", "name": "Follow the Distant Roar", "description": "Trace the overwhelming presence deeper into the cave.", "duration": 11, "difficulty": "Demanding", "xp": 12, "magicules": 4, "insight": 2, "heal": 0},
    "silent_scout": {"id": "silent_scout", "name": "Scout Through Vibrations", "description": "Map nearby tunnels without revealing your presence.", "duration": 13, "difficulty": "Complex", "xp": 14, "magicules": 3, "insight": 4, "heal": 0},
    "magicule_circulation": {"id": "magicule_circulation", "name": "Learn Magicule Circulation", "description": "Practice Veldora's method for moving energy through your body.", "duration": 15, "difficulty": "Complex", "xp": 18, "magicules": 7, "insight": 3, "heal": 5, "training": "mana"},
    "talk_goblins": {"id": "talk_goblins", "name": "Talk with the Goblins", "description": "Learn names, fears, skills, and what the village needs most.", "duration": 7, "difficulty": "Social", "xp": 8, "magicules": 1, "insight": 4, "heal": 0, "friendship": {"goblin_village": 1}},
    "train_allies": {"id": "train_allies", "name": "Train with Your Allies", "description": "Practice coordinated attacks with the active party.", "duration": 18, "difficulty": "Intense", "xp": 22, "magicules": 4, "insight": 2, "heal": 0, "party_training": True},
}

SKILLS = [
    {"id": "slime_strike", "name": "Slime Strike", "description": "A simple body blow. Reliable, but deliberately modest.", "level": 1, "mana": 0, "power": 0.9},
    {"id": "sticky_thread", "name": "Sticky Thread", "description": "Bind the target and pierce part of its defense.", "level": 2, "mana": 3, "power": 1.35, "pierce": 0.35},
    {"id": "water_blade", "name": "Water Blade", "description": "A compressed edge of water with strong armor penetration.", "level": 4, "mana": 5, "power": 1.7, "pierce": 0.6},
    {"id": "predator", "name": "Predator", "description": "Devour a creature below 25% health for extra Magicules.", "level": 6, "mana": 8, "power": 0, "execute": 0.25},
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
}

ZONES = {
    "sealed_cave": {
        "id": "sealed_cave", "name": "Sealed Cave", "subtitle": "Five encounters between you and the thunderous voice", "total_encounters": 5,
        "enemies": [
            {"name": "Cave Bat", "ally_id": "cave_bat", "strength": 4, "hp": 13, "attack": 2, "defense": 0, "xp": 5, "gold": 1, "magicules": 2},
            {"name": "Acid Slug", "ally_id": "acid_slug", "strength": 6, "hp": 17, "attack": 3, "defense": 1, "xp": 7, "gold": 2, "magicules": 3},
            {"name": "Armored Spider", "ally_id": "armored_spider", "strength": 7, "hp": 20, "attack": 3, "defense": 2, "xp": 8, "gold": 2, "magicules": 3},
        ],
        "boss": {"name": "Armored Centipede", "ally_id": "cave_centipede", "strength": 13, "hp": 39, "attack": 5, "defense": 2, "xp": 22, "gold": 6, "magicules": 8},
    },
    "forest_road": {
        "id": "forest_road", "name": "Forest Road", "subtitle": "Five encounters on the road to the goblin village", "total_encounters": 5,
        "enemies": [
            {"name": "Horned Rabbit", "ally_id": "horned_rabbit", "strength": 8, "hp": 24, "attack": 4, "defense": 1, "xp": 10, "gold": 3, "magicules": 4},
            {"name": "Direwolf Scout", "ally_id": "direwolf", "strength": 10, "hp": 29, "attack": 5, "defense": 2, "xp": 12, "gold": 4, "magicules": 5},
            {"name": "Forest Lizard", "ally_id": "forest_lizard", "strength": 11, "hp": 32, "attack": 5, "defense": 3, "xp": 13, "gold": 4, "magicules": 5},
        ],
        "boss": {"name": "Fang Captain", "ally_id": "fang_captain", "strength": 19, "hp": 64, "attack": 8, "defense": 4, "xp": 35, "gold": 12, "magicules": 12},
    },
    "lizard_marsh": {
        "id": "lizard_marsh", "name": "Lizard Marsh", "subtitle": "A repeatable expedition beyond the safety of the village", "total_encounters": 5,
        "enemies": [
            {"name": "Giant Marsh Frog", "ally_id": "marsh_frog", "strength": 13, "hp": 38, "attack": 6, "defense": 3, "xp": 16, "gold": 5, "magicules": 6},
            {"name": "Mud Crawler", "ally_id": None, "strength": 14, "hp": 42, "attack": 6, "defense": 4, "xp": 17, "gold": 6, "magicules": 7},
            {"name": "Poison Newt", "ally_id": None, "strength": 15, "hp": 39, "attack": 7, "defense": 3, "xp": 18, "gold": 6, "magicules": 7},
        ],
        "boss": {"name": "Marsh Basilisk", "ally_id": None, "strength": 24, "hp": 82, "attack": 10, "defense": 5, "xp": 48, "gold": 16, "magicules": 16},
    },
    "ancient_ruins": {
        "id": "ancient_ruins", "name": "Ancient Ruins", "subtitle": "A dangerous, artifact-filled ruin — six encounters of growing peril", "total_encounters": 6,
        "enemies": [
            {"name": "Dust Wight", "ally_id": None, "strength": 12, "hp": 36, "attack": 5, "defense": 2, "xp": 18, "gold": 6, "magicules": 5},
            {"name": "Clockwork Scarab", "ally_id": None, "strength": 14, "hp": 40, "attack": 6, "defense": 3, "xp": 20, "gold": 7, "magicules": 6},
            {"name": "Stone Golemling", "ally_id": None, "strength": 16, "hp": 48, "attack": 7, "defense": 5, "xp": 24, "gold": 9, "magicules": 8},
            {"name": "Relic Guardian", "ally_id": None, "strength": 18, "hp": 56, "attack": 8, "defense": 6, "xp": 28, "gold": 11, "magicules": 10},
        ],
        "boss": {"name": "Ruins Sentinel", "ally_id": None, "strength": 28, "hp": 120, "attack": 12, "defense": 8, "xp": 80, "gold": 28, "magicules": 28},
    },
}

STORY_NODES = {
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
}

STORY_OBJECTIVES = {
    "awakening": "Answer the mysterious voice inside your mind.",
    "first_steps": "Complete any 3 actions and learn how your slime body survives.",
    "seek_dragon": "Complete one five-encounter expedition through the Sealed Cave.",
    "learn_from_friend": "Complete Magicule Circulation twice to prepare an escape.",
    "protect_village": "Complete one five-encounter expedition through the Forest Road.",
    "chapter_one_complete": "Build a party, strengthen friendships, and explore the Lizard Marsh while Chapter III is written.",
}

# Extended story: a series of crossroads, alliances, and a final campaign
STORY_NODES.update({
    "crossroads": {
        "id": "crossroads",
        "speaker": "Wandering Merchant",
        "eyebrow": "CHAPTER III · A WORLD BEYOND",
        "title": "A fork in many roads",
        "text": "A traveling merchant describes three distant opportunities: the capital's libraries, a mercenary captain seeking allies, and an old ruin said to hold forgotten power.",
        "next_phase": "alliance_paths",
        "options": [
            {"id": "seek_knowledge", "label": "Search the capital's libraries", "description": "Prioritize knowledge and long-term power.", "reply": "You set your sights on scrolls and hidden tomes.", "result": "A scholarly path opens, unlocking research actions.", "unlock_actions": ["analyze_moss"], "branch": "Scholar"},
            {"id": "join_mercenaries", "label": "Answer the mercenary captain's call", "description": "Gather a band and prove your might.", "reply": "The captain grins; training and contracts follow.", "result": "Mercenary contacts offer steady work and training.", "unlock_actions": ["train_allies"], "friendship": {"mercenary_captain": 2}, "branch": "Captain"},
            {"id": "explore_ruins", "label": "Investigate the old ruin", "description": "Seek lost artifacts with immediate risk and reward.", "reply": "Dust and echoes greet you; something else stirs.", "result": "A repeatable ruin expedition is hinted at.", "unlock_zones": ["ancient_ruins"], "branch": "Ruins"},
        ],
    },
    "forge_alliance": {
        "id": "forge_alliance",
        "speaker": "Local Council",
        "eyebrow": "CHAPTER IV · TIES THAT BIND",
        "title": "A fragile pact",
        "text": "With growing renown, nearby groups ask for formal bonds. Will you cement alliances, broker trade, or refuse to be tied?",
        "next_phase": "journey_to_capital",
        "options": [
            {"id": "bind_together", "label": "Create a formal alliance", "description": "A strong promise for shared defense.", "reply": "Names are exchanged; banners are discussed.", "result": "Allied groups improve recruitment and training.", "friendship": {"goblin_village": 2, "direwolf_pack": 2}, "branch": "Allied"},
            {"id": "broker_trade", "label": "Broker trade and independence", "description": "Weave commerce without political chains.", "reply": "Merchants celebrate the practical choice.", "result": "Trade routes improve your gold income.", "friendship": {"merchant_guild": 2}, "branch": "Trader"},
            {"id": "refuse_ties", "label": "Refuse formal promises", "description": "Keep freedom at the cost of slower growth.", "reply": "Some respect your solitude; others call you distant.", "result": "You remain independent but maintain flexible options.", "branch": "Lone"},
        ],
    },
    "capital_approach": {
        "id": "capital_approach",
        "speaker": "Capital Guard",
        "eyebrow": "CHAPTER V · THE CAPITAL'S GATES",
        "title": "Gates of an old power",
        "text": "Word of your deeds reaches the capital. Guards demand proof of intent: scholarship, service, or conquest.",
        "next_phase": "prepare_final",
        "options": [
            {"id": "pledge_scholar", "label": "Pledge service to the scholar's hall", "description": "Offer discoveries in exchange for patronage.", "reply": "Scholars peer at you with both curiosity and caution.", "result": "Access to rare knowledge and potential new skills.", "unlock_actions": ["analyze_moss"], "branch": "Patron"},
            {"id": "pledge_service", "label": "Offer service to the capital guard", "description": "Earn honor and rank through deeds.", "reply": "You accept and are given small missions to prove your worth.", "result": "Official missions unlock repeatable expeditions.", "branch": "Honor"},
            {"id": "test_strength", "label": "Challenge a champion to prove your might", "description": "Show strength rather than words.", "reply": "Crowds gather; your name spreads.", "result": "A champion ally may be impressed and join later.", "friendship": {"champion": 1}, "branch": "Challenger"},
        ],
    },
    "final_campaign": {
        "id": "final_campaign",
        "speaker": "Herald",
        "eyebrow": "CHAPTER VI · THE STORMFRONT",
        "title": "A challenge for the ages",
        "text": "As alliances and choices converge, a looming threat demands a coalition. Will you lead, coordinate, or strike alone?",
        "next_phase": "epilogue",
        "options": [
            {"id": "lead_coalition", "label": "Lead a grand coalition", "description": "Unite allies into a single force.", "reply": "Banners fly together under your name.", "result": "A dramatic expedition becomes available; leadership yields rewards.", "unlock_actions": ["train_allies"], "branch": "Leader"},
            {"id": "coordinate_from_shadow", "label": "Coordinate from the shadows", "description": "Support and guide rather than lead.", "reply": "Your plans unfold exactly as intended.", "result": "Subtle benefits and special contacts are gained.", "branch": "Warden"},
            {"id": "strike_alone", "label": "Strike the heart alone", "description": "Take a solitary path aiming for a decisive strike.", "reply": "Your name becomes legend—or fallout.", "result": "Solo rewards and a different ending path.", "branch": "Solo"},
        ],
    },
    "epilogue": {
        "id": "epilogue",
        "speaker": "Narrator",
        "eyebrow": "EPILOGUE · LEGENDS ARE WRITTEN",
        "title": "The story settles",
        "text": "Your deeds echo as new songs. The choices you made shape the lands for generations.",
        "next_phase": "epilogue",
        "options": [
            {"id": "reflect", "label": "Take stock of your companions", "description": "Remember what you gained and who you lost.", "reply": "Memories pour forth; friendships are measured in small moments.", "result": "A gentle ending scene unfolds.", "branch": "Reflective"},
        ],
    },
})

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
        "speaker": "Herbalist"
        ,"eyebrow": "SIDE QUEST · REMEDIES",
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
})

STORY_OBJECTIVES.update({
    "alliance_paths": "Choose a long-term path: knowledge, mercenary work, or ruins.",
    "journey_to_capital": "Solidify alliances and prepare for broader influence.",
    "prepare_final": "Gather allies, resources, and knowledge for the final campaign.",
    "epilogue": "See how your choices reshape the world and your legend.",
})

def hero_public() -> dict:
    return {key: value for key, value in HERO.items() if key != "base"} | {"stats": dict(HERO["base"])}

def recruitment_chance(strength: int) -> float:
    """Stronger creatures are more difficult to persuade after battle."""
    return round(max(0.04, min(0.32, 0.36 - (strength * 0.015))), 3)

