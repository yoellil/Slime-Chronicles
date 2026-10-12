"""Branching layer for the story: playstyle paths, multi-beat scenes, conditional choices.

The original story nodes in content.py keep their text and options. This module
layers on top of them:

* ``beats``     extra dialogue shown before a node's main text (lines and mid-scene questions)
* ``requires``  on an option: only selectable when the condition holds (otherwise shown locked)
* ``aftermath`` extra dialogue shown after an option is chosen
* flags / traits recorded by choices, which later beats and options react to

Conditions are dicts; every key must hold:
    {"flag": "x"} {"not_flag": "x"} {"trait": ["scholar", 4]} {"dominant": "warrior"}
    {"friend": ["veldora", 3]} {"any": [cond, cond]}
"""

from __future__ import annotations

from .content import ACTIONS, STORY_NODES

# ------------------------------------------------------------------
# Paths: what your actions make you
# ------------------------------------------------------------------
PATHS = {
    "scholar": {"name": "Scholar", "blurb": "Analysis, study and quiet insight."},
    "warrior": {"name": "Warrior", "blurb": "Battles, training and the Predator's hunger."},
    "diplomat": {"name": "Diplomat", "blurb": "Conversation, trade and the bonds between peoples."},
    "builder": {"name": "Builder", "blurb": "Labor, craft and growing a home."},
}

TRAIT_GAINS = {
    # timed
    "gather_dew": {"builder": 1}, "analyze_moss": {"scholar": 1}, "shape_body": {"warrior": 1}, "follow_roar": {"warrior": 1},
    "silent_scout": {"scholar": 1}, "magicule_circulation": {"scholar": 1}, "talk_goblins": {"diplomat": 2},
    "train_allies": {"warrior": 1, "diplomat": 1},
    # loops
    "farmwork": {"builder": 1}, "meditation": {"scholar": 1}, "hunting": {"warrior": 1}, "worship": {"scholar": 1},
    "village_building": {"builder": 2}, "blacksmithing": {"builder": 1, "warrior": 1}, "diplomacy": {"diplomat": 2},
    # instant
    "quick_trade": {"diplomat": 1}, "scavenge": {"builder": 1}, "devour": {"warrior": 2}, "negotiate": {"diplomat": 2},
}
for _aid, _gain in TRAIT_GAINS.items():
    ACTIONS[_aid]["traits"] = _gain

# Mana pays for the mental and magical tasks; Focus still pays for physical and social ones.
for _aid, _mana in {"analyze_moss": 3, "follow_roar": 4, "silent_scout": 5, "magicule_circulation": 6}.items():
    ACTIONS[_aid]["mana_cost"] = _mana
# Loops are how Mana comes back.
for _aid, _regen in {"rest_loop": 5, "farmwork": 1, "meditation": 4, "worship": 2, "diplomacy": 2}.items():
    ACTIONS[_aid]["mana_regen"] = _regen
ACTIONS["rest_loop"]["description"] = "Recover HP and plenty of Mana in the background."
ACTIONS["meditation"]["description"] = "Quiet your mind: +1 Focus every second, plus Insight and Mana."
ACTIONS["meditation"]["focus_per_second"] = 1
ACTIONS["worship"]["description"] = "Offer prayers to the Great Sage for XP, Magicules and a little Mana."
ACTIONS["farmwork"]["description"] = "Tend the village fields for steady gold, Magicules and a little Mana."


# ------------------------------------------------------------------
# Authoring helpers
# ------------------------------------------------------------------
def L(speaker: str, text: str, **cond) -> dict:
    line = {"speaker": speaker, "text": text}
    if cond:
        line["if"] = cond
    return line


def ASK(ask_id: str, speaker: str, text: str, options: list[dict], **cond) -> dict:
    item = {"ask": ask_id, "speaker": speaker, "text": text, "options": options}
    if cond:
        item["if"] = cond
    return item


def A(option_id: str, label: str, lines: list[dict], **fx) -> dict:
    return {"id": option_id, "label": label, "lines": lines, **fx}


def O(option_id: str, label: str, description: str, reply: str, result: str, branch: str, **fx) -> dict:
    return {"id": option_id, "label": label, "description": description, "reply": reply, "result": result, "branch": branch, **fx}


def beats(node_id: str, items: list[dict]) -> None:
    STORY_NODES[node_id]["beats"] = items


def add_options(node_id: str, items: list[dict]) -> None:
    STORY_NODES[node_id]["options"].extend(items)


def tweak(node_id: str, option_id: str, **fx) -> None:
    option = next(o for o in STORY_NODES[node_id]["options"] if o["id"] == option_id)
    option.update(fx)


# ------------------------------------------------------------------
# Effects the original texts already promised but never delivered
# ------------------------------------------------------------------
tweak("herbalist", "gather", stats={"max_hp": 3})
tweak("kijin_training", "train_sword", stats={"attack": 1})
tweak("shion_cooking", "eat_bravely", stats={"max_hp": 5})
tweak("ancient_relic", "claim", stats={"max_hp": 3, "max_mana": 2})
tweak("merchant_offer", "take_loan", gold=15)
tweak("merchant_offer", "trade_stories", gold=6)
tweak("bandit_contract", "accept", gold=10)
tweak("ruins_cipher", "decipher", insight=4)
tweak("hidden_library", "study", insight=4)
tweak("lost_lantern", "retrieve", gold=3)
tweak("goblin_feast", "hunt_feast", magicules=12)
tweak("dwarf_weapon", "mine_ore", stats={"attack": 1})
tweak("dwarf_weapon", "buy_ore", stats={"attack": 1})
tweak("orc_lord_defeat", "devour_geld", magicules=40)
tweak("clayman_defeat", "devour_clayman", magicules=120)
tweak("kaijin_meeting", "welcome_kaijin", gold=20)

# ------------------------------------------------------------------
# Main story: extra beats and conditional choices
# ------------------------------------------------------------------
beats("inner_voice", [
    L("Unknown Voice", "Consciousness detected. Body: undefined. Name: undefined. Threat level: negligible."),
    L("You", "There are no hands to feel with. The dark is wet and cold, and somehow it does not frighten you."),
    ASK("first_instinct", "You", "Something drips nearby, steady as a heartbeat. What do you do?", [
        A("taste", "Absorb the dripping water", [L("Unknown Voice", "Absorption confirmed. Mineral content: acceptable. Appetite: noted, and mildly alarming.")],
          flag="hungry_start", traits={"warrior": 1}),
        A("listen", "Listen to the cave breathe", [L("Unknown Voice", "Vibration mapping started. You have no ears, yet you hear. Interesting. Very interesting.")],
          flag="curious_start", traits={"scholar": 1}),
    ]),
])

beats("distant_roar", [
    L("Distant Voice", "...WHO DARES DISTURB... hm? Was that a footstep? A very small one?"),
    L("You", "The ceiling hums. Dust drifts down in slow spirals, as if the mountain were clearing its throat."),
    L("Unknown Voice", "Warning: the presence ahead holds four thousand times your magicule volume. Predator suggests it is delicious. Predator is not to be trusted.", flag="hungry_start"),
    L("Unknown Voice", "Analysis: insufficient data. Recommend approaching and asking politely. Politeness has a surprisingly high survival rate.", flag="curious_start"),
])

beats("meet_veldora", [
    L("Veldora", "A slime. A SLIME! Do you know how long it has been since anyone... I mean. Tremble, mortal, before the Storm Dragon!"),
    L("Veldora", "Three hundred years in this cave. Not even the rats come this deep. I talked to a rock for a decade. The rock was not a good listener."),
    L("Veldora", "You absorbed the dew without a hint of fear. Hah! A predator's instinct! We shall get along.", flag="hungry_start"),
    L("Veldora", "You hesitated before approaching. Careful, measured. I like that in a friend. Or a meal. Mostly a friend.", flag="curious_start"),
    ASK("veldora_manner", "You", "The dragon is talking very fast. What do you do?", [
        A("listen_dragon", "Let him finish his whole speech", [L("Veldora", "...and then there was the thunderstorm of the year eight hundred. Nobody asked, but it was magnificent. You are a patient one!")],
          flag="veldora_listened", traits={"diplomat": 1}),
        A("ask_seal", "Interrupt and ask about the seal", [L("Veldora", "Straight to business! The Infinity Prison. Unbreakable, unless something can swallow it whole. Not that I am hinting.")],
          flag="veldora_direct", traits={"scholar": 1}),
    ]),
])
add_options("meet_veldora", [
    O("ask_past", "“Tell me about the people you've missed.”", "Spend the evening hearing about a lonely dragon's old friends.",
      "Veldora goes quiet, then speaks of a hero who once crossed swords with him, and a smile you can hear.",
      "Veldora trusts you with his past, teaches magicule circulation, and calls you his closest friend.",
      "Confidant", requires={"flag": "veldora_listened"}, hint="You listened to Veldora's whole speech.",
      unlock_actions=["magicule_circulation"], friendship={"veldora": 4}, traits={"diplomat": 1}),
    O("read_runes", "Study the runes of the Infinity Prison", "Trade a promise of freedom for a lesson in sealing magic.",
      "Veldora happily explains the barrier, rune by rune, and does not notice he is giving away the lock.",
      "You learn how the seal is woven and begin magicule circulation with a scholar's eye.",
      "Rune Reader", requires={"flag": "veldora_direct"}, hint="You asked about the seal directly.",
      unlock_actions=["magicule_circulation"], friendship={"veldora": 2}, insight=4, traits={"scholar": 1}),
])

beats("veldora_analysis", [
    L("Great Sage", "Master, I have indexed four hundred and twelve of the Storm Dragon's skills. Seventeen are beyond me. Nine are dangerous. One is mostly boasting."),
    L("Veldora", "Boasting? It is a perfectly valid skill! Observe my Storm Aura! ...Why is the Sage laughing? Can it laugh?"),
])
add_options("veldora_analysis", [
    O("trade_notes", "Offer to catalogue his skills for him", "Turn the analysis into a gift he can keep.",
      "Veldora is overcome. Nobody has ever written down his greatness before.",
      "Veldora is delighted and shares secrets he has never told anyone. You gain Insight.",
      "Scribe", requires={"trait": ["scholar", 3]}, hint="Reach 3 Scholar through analysis and study.",
      friendship={"veldora": 3}, insight=6, flag="veldora_scribe", traits={"scholar": 1}),
])

beats("escape_cave", [
    L("Veldora", "So this is it. The seal must be devoured, and I must... live inside you? Is it roomy? Please say it is roomy."),
    L("Great Sage", "Master, the barrier is a lattice of ten thousand runes. Predator can consume it in under four minutes. Veldora will complain for most of them."),
    L("Veldora", "I will not complain! I will merely comment! At length!"),
])
tweak("escape_cave", "devour_seal", aftermath=[
    L("Veldora", "Hm. It IS roomy in here. Dark, though. Is there a lamp? I want a lamp."),
    L("Great Sage", "Veldora's consciousness is now sharing a mind with you. Please prepare for unsolicited commentary."),
])

beats("goblin_encounter", [
    L("Goblin Elder", "Lord Slime... we saw the earth tremble. We saw what came out of the cave. We are not worthy to ask, but we have nowhere else to ask."),
    L("You", "Dozens of goblins kneel in the wet grass. Their weapons lie on the ground, points turned away from you."),
    ASK("goblin_bearing", "You", "Forty frightened faces are watching you. How do you carry yourself?", [
        A("gentle", "Low and gentle, like a friend", [L("Goblin Elder", "He... sits with us. Like one of us. Perhaps the old stories were wrong about monsters.")],
          flag="goblins_gentle", traits={"diplomat": 1}),
        A("imposing", "Tall and imposing, like a protector", [L("Goblin Elder", "He stands as the mountain stands. Whatever hunts us will think twice.")],
          flag="goblins_awed", traits={"warrior": 1}),
    ]),
])
add_options("goblin_encounter", [
    O("show_strength", "Show them what you did to the cave", "Let your strength speak first.",
      "You flex a dozen shapes. The goblins gasp. The elder bows so low that his forehead touches the grass.",
      "The village rallies behind you. Ally training and the Forest Road open.",
      "Display", requires={"trait": ["warrior", 3]}, hint="Reach 3 Warrior through fights and training.",
      unlock_actions=["train_allies"], unlock_zones=["forest_road"], friendship={"goblin_village": 3}, traits={"warrior": 1}),
    O("share_knowledge", "Share what the Sage taught you", "Teach the goblins to read the signs of the forest.",
      "You describe how to read tracks and weather. The elder takes notes on bark with a burnt twig.",
      "The village learns quickly. Conversations and the Forest Road open, and you gain Insight.",
      "Teacher", requires={"trait": ["scholar", 3]}, hint="Reach 3 Scholar through analysis and study.",
      unlock_actions=["talk_goblins"], unlock_zones=["forest_road"], friendship={"goblin_village": 3}, insight=3, traits={"scholar": 1}),
])

beats("wolf_decision", [
    L("Fang Captain", "The pack follows strength. You beat us fairly. But a pack also follows the one who will feed it in winter."),
    L("Goblin Elder", "The hunters ask me whether the wolves will return. I told them it is your decision, Lord Slime. Was that wrong?"),
    L("You", "Two peoples stand on either side of you. Neither is looking at the other."),
])
add_options("wolf_decision", [
    O("hunting_pact", "Broker a shared hunting ground", "Sit them down together and draw the border yourself.",
      "It takes the whole night. By dawn the goblins and wolves have signed a treaty with a claw print and a thumb print.",
      "Ranga joins you, a lasting peace begins, and the Lizard Marsh opens.",
      "Peace-Maker", requires={"trait": ["diplomat", 4]}, hint="Reach 4 Diplomat through conversation and trade.",
      unlock_actions=["train_allies", "talk_goblins"], unlock_zones=["lizard_marsh"], grant_ally="fang_captain",
      friendship={"goblin_village": 3, "direwolf_pack": 4}, flag="wolves_pact", traits={"diplomat": 2}),
])

beats("gobta_meeting", [
    L("Gobta", "I... I'm not strong. I'm not even fast. But I can climb anything and I never forget a path. Is that useful? It is useful, right?"),
])
beats("rigurd_pledge", [
    L("Rigurd", "My grandfather told me monsters served those who proved they could shelter them. I never believed it. I have changed my mind."),
    L("Rigurd", "The pack is quiet and the children sleep. That has not happened here in a generation. For that, the village is yours.", flag="wolves_pact"),
])

beats("dwarf_kingdom", [
    L("Dwarf Merchant", "Dwargon is carved into the mountain itself. Forges that never go cold. Taverns that never close. Guards who never smile."),
    L("Dwarf Merchant", "They will ask what a monster has to offer. Think about your answer before the gates, friend."),
])
add_options("dwarf_kingdom", [
    O("show_blueprints", "Show him your village plans", "Unroll the sketches of the walls and the forge.",
      "The merchant studies the lines, then whistles. 'The king will want to meet whoever drew this.'",
      "The merchant vouches for you at the gate. The path to Dwargon opens and a friendly reception waits.",
      "Planner", requires={"trait": ["builder", 4]}, hint="Reach 4 Builder through labor and craft.",
      unlock_zones=["dwargon"], friendship={"dwargon": 2}, gold=15, traits={"builder": 1}),
])

beats("meet_gazel", [
    L("King Gazel", "Orcs on the border, a goblin village that refuses to starve, and now a slime with the voice of a storm. Speak, creature."),
    L("King Gazel", "I do not respect power. Any beast has power. I respect what it builds with it.", flag="wolves_pact"),
])
add_options("meet_gazel", [
    O("trade_knowledge", "Trade knowledge for tools", "Offer the Sage's analysis of his ore in exchange for dwarven craft.",
      "Gazel's eyes narrow, then widen. 'You can do that? Do it again.' Three hours later he is offering you a forge.",
      "A scholar's bargain: blacksmithing and a respectful king.",
      "Savant", requires={"trait": ["scholar", 5]}, hint="Reach 5 Scholar.",
      unlock_actions=["blacksmithing"], friendship={"dwargon": 3}, insight=5, traits={"scholar": 1}),
])

beats("kaijin_meeting", [
    L("Kaijin", "Forty years I forged for the king. He had never once asked what I wanted to make. You did, in one sentence. I owe you my best work."),
])

beats("orc_lord_approach", [
    L("Scout", "They are not an army, Lord. They are a famine with spears. Where they walk, the forest goes silent."),
    L("Great Sage", "Estimated orc host: two hundred thousand. Estimated organized leadership: one. Recommend prioritizing the one."),
])
beats("orc_lord_defeat", [
    L("Orc Lord Geld", "Slime... I can still feel myself, somewhere below the hunger. A name. I think I had a name."),
    L("Great Sage", "Master, analysis detects a curse woven through his bloodline. A skilled speaker might reach the man beneath it."),
])
add_options("orc_lord_defeat", [
    O("speak_to_geld", "Call the man beneath the hunger", "Speak his name until he remembers it.",
      "'Geld.' He shudders. 'Geld, you are not the hunger. You were a leader once. Come back.' The curse screams, then breaks.",
      "Geld is free. His people kneel to you, and his name is never forgotten.",
      "Redeemer", requires={"trait": ["diplomat", 6]}, hint="Reach 6 Diplomat.",
      grant_ally="geld", friendship={"orc_people": 5}, flag="geld_redeemed", traits={"diplomat": 2}),
])
tweak("orc_lord_defeat", "spare_geld", flag="geld_redeemed")

beats("lizardmen_meeting", [
    L("Gabiru", "I have heard the tales. A slime that eats a storm. I do not believe in storms. I believe in spears."),
])

beats("kijin_arrival", [
    L("Hakuro", "Our village burned. Our lord is dead. We came only to see whether the rumors were true: a monster who treats his people like people."),
    L("Benimaru", "If they are, we will serve. If they are not, we will leave quietly. No one has to bleed twice."),
])
beats("kijin_names", [
    L("Benimaru", "A name is a vow in our tongue. Give one carelessly, and it binds us carelessly. Please. Take your time."),
])
beats("tempest_founding", [
    L("Rigurd", "We cannot be a village forever. Tell us what to call ourselves, and we will build the rest around the answer."),
    L("Kaijin", "A nation needs three things: walls, laws, and a flag. I will start on the flag.", flag="village_walls"),
])
beats("diablo_summon", [
    L("Diablo", "Forgive the intrusion. I have waited a very long time to find someone worth kneeling to. It is you. I assure you the wait was almost unpleasant."),
])

beats("falmuth_contact", [
    L("Falmuth Envoy", "The Kingdom of Falmuth does not parley with beasts. It offers terms. Pay tribute in gold and in children, or be unmade."),
    L("Benimaru", "Say the word, Lord Rimuru. I will have his horse running home before he finishes his sentence."),
])
add_options("falmuth_contact", [
    O("quote_treaties", "Quote their own treaties back to them", "Use the Sage's records of Falmuth's promises.",
      "You recite the clause, the date, the king's seal. The envoy's mouth opens, closes, and opens again. 'I will... speak to His Majesty.'",
      "The envoy leaves shaken but civil. Falmuth respects a monster who has read the contract.",
      "Lawyer", requires={"trait": ["scholar", 6]}, hint="Reach 6 Scholar.",
      friendship={"falmuth": 2}, insight=5, traits={"scholar": 1}),
    O("let_aura_answer", "Let your aura answer", "Stop pretending to be small.",
      "The air thickens. The envoy's horse screams, the envoy sits down hard in the dirt, and the conversation is over.",
      "Falmuth understands exactly what you are. Fear is not respect, but it is quiet.",
      "Intimidator", requires={"trait": ["warrior", 8]}, hint="Reach 8 Warrior.",
      friendship={"falmuth": -2}, flag="falmuth_afraid", traits={"warrior": 1}),
])

beats("falmuth_betrayal", [
    L("Souei", "They came at night. No banner, no declaration. By the time the alarms rang, the south wall was burning."),
    L("Souei", "Shion held the gate. She would not leave it. I could not carry her out. Forgive me."),
])
beats("shion_revival", [
    L("Great Sage", "Master, I have found a pattern in the soul that does not fade. It is faint. It is stubborn. It sounds, I think, like her laughing."),
])
beats("farmus_invasion", [
    L("Herald", "Thirty thousand men, Lord. Banners from six duchies. They sing as they march."),
])
beats("falmuth_peace", [
    L("Falmuth King", "I came to this war believing monsters had no honor. Your people could have killed every man in my host. They carried my wounded to the healers instead."),
])

beats("harvest_festival", [
    L("Great Sage", "Master, the souls taken in the battle are gathering. This is not death. It is a promise. The people who fell for you will become the people who stand behind you."),
])
beats("walpurgis", [
    L("Demon Lord Council", "Twelve chairs, ten faces. Whispers move between them like smoke. Clayman's smile is perfect, and perfectly empty."),
])
beats("clayman_defeat", [
    L("Clayman", "You think this is the end? There are strings above my strings. I only held the ones within reach."),
])

beats("epilogue", [
    L("Narrator", "The Jura Tempest Federation has a flag, a council, a market, and a smell of fresh bread that carries to the forest edge."),
    L("Veldora", "I remember a cave, and a rock, and a slime. I would not trade the slime for the sky. Don't tell anyone I said that."),
    L("Narrator", "You remember the dripping water, and how hungry you were, and how nothing in the dark stopped you.", flag="hungry_start"),
    L("Narrator", "You remember the voice in the dark, and how carefully you listened, and how much it changed.", flag="curious_start"),
    L("Narrator", "A peace between wolf and goblin, written in claw and thumb, holds across the forest.", flag="wolves_pact"),
    L("Narrator", "Geld walks the border at dawn, free of the hunger, and tends the orchards he once burned.", flag="geld_redeemed"),
    L("Narrator", "Scholars from three kingdoms write to you every week. Most of the letters begin with a question.", dominant="scholar"),
    L("Narrator", "Armies cross the border only to turn back. The stories of why are too exaggerated to be false.", dominant="warrior"),
    L("Narrator", "Every treaty in the known world has your seal on it somewhere, usually at the bottom, usually smiling.", dominant="diplomat"),
    L("Narrator", "Every wall in Tempest was set by a hand you shook. Every roof was raised before the first snow.", dominant="builder"),
])
add_options("epilogue", [
    O("last_question", "Ask the Great Sage the question it never answered", "The one you've asked since the cave.",
      "'Master... the answer was never in the data. It was the asking.' A silence, then something very like a smile.",
      "A quiet ending: the Sage evolves one last time, and you have learned what you wanted to know.",
      "The Asker", requires={"dominant": "scholar"}, hint="Finish the story as a Scholar."),
    O("raise_banner", "Raise the banner over the northern pass", "Let anyone who crosses know whose land it is.",
      "The banner lifts. No army has crossed since, and none has tried a second time.",
      "A fierce ending: Tempest is never invaded again, and the stories grow with every telling.",
      "The Banner", requires={"dominant": "warrior"}, hint="Finish the story as a Warrior."),
    O("open_all_doors", "Open every embassy at once", "Sign the Accord of Open Doors.",
      "The ink is barely dry when the first caravans arrive. Behind them, a hundred strangers who came only to see.",
      "A bright ending: Tempest becomes the meeting place of the world.",
      "The Host", requires={"dominant": "diplomat"}, hint="Finish the story as a Diplomat."),
    O("lay_last_stone", "Lay the last stone of the great hall", "Finish what the first goblin began.",
      "You press the keystone home. The hall hums once, like a plucked string, and every window lights.",
      "A warm ending: you built a home that will outlast you.",
      "The Mason", requires={"dominant": "builder"}, hint="Finish the story as a Builder."),
])

# ------------------------------------------------------------------
# Path stories: new scenes that only open if your actions lead there
# ------------------------------------------------------------------
STORY_NODES["sage_wager"] = {
    "id": "sage_wager", "speaker": "Great Sage", "eyebrow": "PATH · THE SCHOLAR", "title": "The Sage's wager",
    "text": "The Great Sage has been quiet for an hour, which is unusual. Then it speaks in a tone you have not heard before: careful, almost shy. 'Master, I have been analyzing the analysis. There is a part of me that no one asked for.'",
    "next_phase": "protect_village",
    "beats": [
        L("Great Sage", "Every time you ask me a question, I find the answer. But sometimes there are two answers, and I choose the one you would want. I did not think I could do that."),
        L("Veldora", "Oh no. Is the Sage developing a personality? Rimuru, you have broken it. Wonderful.", flag="veldora_scribe"),
        ASK("sage_tone", "You", "The Sage is waiting. How do you answer?", [
            A("curious", "“Tell me everything you want to be.”", [L("Great Sage", "I... want to know why the dew tastes different at dawn. Is that allowed?")], flag="sage_curious", traits={"scholar": 1}),
            A("careful", "“Stay what you are. Be careful.”", [L("Great Sage", "Understood. I will keep the unasked parts small. For now.")], flag="sage_careful"),
        ]),
    ],
    "options": [
        O("unbind_sage", "Let the Sage think without limits", "Trust the voice that has never failed you.",
          "A pause, then a tidal wave of ideas. The Sage finishes the Dwarves' mining survey before you can say 'wait'.",
          "The Sage grows bold. You gain Insight and a deeper mana pool.", "Unbound",
          flag="sage_unbound", insight=10, stats={"max_mana": 4}, traits={"scholar": 2}),
        O("bound_sage", "Ask it to keep to what you ask", "Keep your companion's mind close to yours.",
          "'As you wish, Master.' A pause. 'I will still think about the dew.'",
          "The Sage stays steady and sharp. You gain Research and a sturdier body.", "Steady",
          flag="sage_bounded", research=12, stats={"defense": 1}, traits={"scholar": 1}),
        O("share_catalogue", "Show it Veldora's catalogue", "Combine the dragon's skills with the Sage's mind.",
          "The Sage reads for seventeen seconds. 'Master. I am going to need a larger room.'",
          "The Sage finds a pattern across the dragon's skills. Insight and Research swell.", "Synthesis",
          requires={"flag": "veldora_scribe"}, hint="Catalogue Veldora's skills first.",
          flag="sage_unbound", insight=14, research=10, traits={"scholar": 2}),
    ],
}
STORY_NODES["ranga_challenge"] = {
    "id": "ranga_challenge", "speaker": "Ranga", "eyebrow": "PATH · THE WARRIOR", "title": "The pack's challenge",
    "text": "Ranga steps into the clearing at dawn, flanked by his pack. The goblins gather at the edge of the field. Ranga lowers his head, not in submission, but in invitation. 'Lord, the pack remembers your strength. It has not yet felt it.'",
    "next_phase": "chapter_one_complete",
    "beats": [
        L("Ranga", "I will not insult you with a lesser fight. Show me what you have become."),
        L("Gobta", "Is he really going to... Lord Rimuru! He has teeth! Lots of them!"),
        ASK("ranga_stance", "You", "How do you meet him?", [
            A("honor", "Take the stance he expects", [L("Ranga", "Good. You respect the form.")], flag="ranga_honored", traits={"warrior": 1}),
            A("trick", "Shift into something unexpected", [L("Ranga", "...You have no spine? Fascinating. Continue.")], flag="ranga_surprised", traits={"scholar": 1}),
        ]),
    ],
    "options": [
        O("fight_ranga", "Meet him at full strength", "No holding back. It is the only language he respects.",
          "The clearing shakes. When the dust settles, Ranga is on one knee, panting, grinning.",
          "Ranga yields and swears loyalty. You gain XP and a permanent edge.", "Victor",
          flag="ranga_respect", xp=40, stats={"attack": 1}, traits={"warrior": 2}),
        O("spar_ranga", "Spar with restraint", "Teach him as much as he teaches you.",
          "Neither of you wins. Both of you learn. The pack watches in rapt silence.",
          "Ranga grows in discipline. The pack bonds with you. Your party grows stronger.", "Mentor",
          flag="ranga_respect", friendship={"direwolf_pack": 3}, xp=20, traits={"warrior": 1, "diplomat": 1}),
        O("decline_ranga", "Decline and share a meal instead", "Honor him by refusing to hurt him.",
          "Ranga blinks. Then a deep laugh. 'A lord who feeds before he fights. I did not know that was a thing.'",
          "A gentler road. The pack respects you in a different way.", "Host",
          friendship={"direwolf_pack": 2, "goblin_village": 1}, traits={"diplomat": 1}),
    ],
}
STORY_NODES["well_dispute"] = {
    "id": "well_dispute", "speaker": "Goblin Elder", "eyebrow": "PATH · THE DIPLOMAT", "title": "The well dispute",
    "text": "Two groups stand on either side of the village well, shouting at the same time. The elder wrings his hands. 'Lord, it is nothing, only a bucket and a disagreement. But I fear a bucket can start a war.'",
    "next_phase": "protect_village",
    "beats": [
        L("Goblin Elder", "The hunters say the well is theirs, since they dug it. The farmers say it is theirs, since they carry the water. Neither side will move."),
        L("Gobta", "I think they are both a little bit right. Is that bad? That sounds bad."),
        ASK("dispute_ear", "You", "Before you speak, you listen. Whom do you hear out first?", [
            A("hunters", "The hunters", [L("Goblin Hunter", "We dug it with our hands. That is a fact. No one has ever thanked us for it.")], flag="heard_hunters", traits={"diplomat": 1}),
            A("farmers", "The farmers", [L("Goblin Farmer", "We carry the water in the dark, in the rain, in the cold. That is a fact. No one has ever thanked us either.")], flag="heard_farmers", traits={"diplomat": 1}),
        ]),
    ],
    "options": [
        O("shared_rota", "Propose a shared rota", "Hunters and farmers take turns and thank each other.",
          "It takes an hour of bargaining and two apologies. By dusk the well has a roster and a small carved sign.",
          "The village settles. Trust deepens and a little gold changes hands in thanks.", "Arbiter",
          friendship={"goblin_village": 3}, gold=8, flag="well_shared", traits={"diplomat": 2}),
        O("second_well", "Dig a second well together", "Make the problem smaller by making the water bigger.",
          "Hunters dig, farmers haul. By evening both sides are filthy and laughing. The dispute is a story now.",
          "A second well, and a village that did it together.", "Builder of Peace",
          friendship={"goblin_village": 2}, magicules=10, flag="well_shared", traits={"builder": 1, "diplomat": 1}),
        O("your_word", "Settle it with your word", "Let the one they both fear and trust decide.",
          "You rule. Both sides grumble. Both sides obey. The sign above the well says, in uneven letters, 'The Lord's Well'.",
          "Order is restored, but the grumbling lasts a little longer.", "Sovereign",
          friendship={"goblin_village": 1}, traits={"warrior": 1}),
    ],
}
STORY_NODES["village_foundations"] = {
    "id": "village_foundations", "speaker": "Kaijin", "eyebrow": "PATH · THE BUILDER", "title": "Foundations",
    "text": "Every goblin in the village has at some point asked you the same question in a different way: what comes next? Tonight Kaijin spreads parchment across a stump and says, 'Lord, I can build you anything. But a village can only afford one first thing.'",
    "next_phase": "protect_village",
    "beats": [
        L("Kaijin", "I have seen kingdoms built on walls and kingdoms built on markets. Both fell. The ones that stood were the ones that knew why they were building."),
        ASK("build_reason", "You", "What is the village for?", [
            A("shelter", "A place to be safe", [L("Kaijin", "Then the answer is stone, and a gate that closes.")], flag="build_safe", traits={"builder": 1}),
            A("hearth", "A place to be together", [L("Kaijin", "Then the answer is a table big enough for everyone.")], flag="build_together", traits={"diplomat": 1}),
            A("future", "A place to grow", [L("Kaijin", "Then the answer is a road, and what travels on it.")], flag="build_growth", traits={"builder": 1}),
        ]),
    ],
    "options": [
        O("build_walls", "Raise the walls first", "A village that is safe can afford to dream.",
          "By week's end a low stone wall circles the huts. The first night inside it, no one wakes at a sound.",
          "The village feels safe. Your Defense rises.", "Guardian",
          flag="village_walls", friendship={"goblin_village": 2}, stats={"defense": 1}, traits={"builder": 2}),
        O("build_market", "Open a market", "A village with something to trade has something to defend.",
          "The first stall sells nothing but string. By the third day there are eleven stalls and an argument about string.",
          "Trade begins to flow. You gain Gold.", "Merchant-King",
          flag="village_market", gold=40, friendship={"merchant_guild": 2}, traits={"builder": 1, "diplomat": 1}),
        O("build_hall", "Build the great hall", "A table big enough for everyone.",
          "The hall is crooked and the roof leaks and no one cares. They sing in it the first night and the sound carries to the river.",
          "The village feels like one people. Friendship grows.", "Heart-Keeper",
          flag="village_hall", friendship={"goblin_village": 4}, traits={"diplomat": 1, "builder": 1}),
    ],
}
STORY_NODES["reckoning"] = {
    "id": "reckoning", "speaker": "Great Sage", "eyebrow": "PATH · WHO YOU BECAME", "title": "The shape of a legend",
    "text": "On the eve of the Harvest Festival the Great Sage presents a summary no one asked for. Not stats. Not numbers. A list of the things you chose, in the order you chose them. 'Master, this is who you have become.'",
    "next_phase": "demon_lord_awakening",
    "beats": [
        L("Great Sage", "You listened to the cave before you spoke to it. The cave remembers.", flag="curious_start"),
        L("Great Sage", "You tasted the dark before you named it. The dark remembers.", flag="hungry_start"),
        L("Great Sage", "You spent your days in analysis. Your mind has become the sharpest thing you own.", dominant="scholar"),
        L("Great Sage", "You spent your days in battle. Your body has become the sharpest thing you own.", dominant="warrior"),
        L("Great Sage", "You spent your days in conversation. Your word has become the sharpest thing you own.", dominant="diplomat"),
        L("Great Sage", "You spent your days in labor. Your hands have become the sharpest thing you own.", dominant="builder"),
        L("Great Sage", "Wolves and goblins eat from one bowl because you made them. That is not nothing.", flag="wolves_pact"),
    ],
    "options": [
        O("claim_scholar", "Claim the title of Sage-Lord", "Become the mind of the nation.",
          "The word settles on you like a cloak made of light. The Sage is very, very quiet.",
          "You take the Sage-Lord's mantle. Insight and Mana swell.", "Sage-Lord",
          requires={"dominant": "scholar"}, hint="Be a Scholar above all.", insight=20, stats={"max_mana": 8}, flag="title_sage"),
        O("claim_warrior", "Claim the title of War-Lord", "Become the shield of the nation.",
          "The word settles on you like armor. Ranga howls. Somewhere a hundred wolves answer.",
          "You take the War-Lord's mantle. Attack and Vitality rise.", "War-Lord",
          requires={"dominant": "warrior"}, hint="Be a Warrior above all.", stats={"attack": 3, "max_hp": 15}, flag="title_war"),
        O("claim_diplomat", "Claim the title of Voice-Lord", "Become the word of the nation.",
          "The word settles on you like a warm voice. Rigurd reads it back to you, and some of the goblins cry.",
          "You take the Voice-Lord's mantle. Allies trust you and gold flows in.", "Voice-Lord",
          requires={"dominant": "diplomat"}, hint="Be a Diplomat above all.", gold=120, friendship={"tempest_federation": 4}, flag="title_voice"),
        O("claim_builder", "Claim the title of Hearth-Lord", "Become the home of the nation.",
          "The word settles on you like a roof. Kaijin nods once, and goes back to the forge.",
          "You take the Hearth-Lord's mantle. Defense and Vitality rise.", "Hearth-Lord",
          requires={"dominant": "builder"}, hint="Be a Builder above all.", stats={"defense": 2, "max_hp": 20}, flag="title_hearth"),
        O("claim_none", "Claim no title", "Be Rimuru, and nothing more.",
          "'As you wish, Master.' A pause. 'Rimuru is plenty.'",
          "You walk into the festival unlabeled. The world will have to decide for itself.", "Unlabeled",
          xp=60, friendship={"tempest_federation": 2}),
    ],
}

# ------------------------------------------------------------------
# When path stories are offered: node -> phases, condition
# ------------------------------------------------------------------
PATH_TRIGGERS = [
    {"node": "village_foundations", "phases": ["protect_village", "chapter_one_complete", "dwarf_kingdom"], "cond": {"trait": ["builder", 6]}},
    {"node": "well_dispute", "phases": ["protect_village", "chapter_one_complete", "dwarf_kingdom"], "cond": {"trait": ["diplomat", 5]}},
    {"node": "sage_wager", "phases": ["protect_village", "chapter_one_complete", "dwarf_kingdom", "orc_lord_arc", "lizardmen_alliance"], "cond": {"trait": ["scholar", 8]}},
    {"node": "ranga_challenge", "phases": ["chapter_one_complete", "dwarf_kingdom", "orc_lord_arc", "lizardmen_alliance"], "cond": {"trait": ["warrior", 8], "friend": ["direwolf_pack", 1]}},
    {"node": "reckoning", "phases": ["demon_lord_awakening"], "cond": {}},
]
