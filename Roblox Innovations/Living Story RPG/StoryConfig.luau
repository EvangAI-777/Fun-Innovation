--[[
	StoryConfig.luau
	ModuleScript → ReplicatedStorage

	Shared configuration for the Living Story RPG.
	Defines personality traits, NPC data, dialogue trees, world state
	thresholds, and town layout.  The original Python version was a
	solo text adventure with 7 traits, memory callbacks, and branching
	endings.  This Roblox version turns the same story into a
	persistent multiplayer town.
]]

local StoryConfig = {}

------------------------------------------------------------------------
-- Town layout
------------------------------------------------------------------------
StoryConfig.TownCenter      = Vector3.new(0, 0, 0)
StoryConfig.GroundY          = 0
StoryConfig.TownRadius       = 120  -- studs from center to outermost building
StoryConfig.BuildingHeight   = 16
StoryConfig.WallThickness    = 2
StoryConfig.DoorWidth        = 6
StoryConfig.DoorHeight       = 10

------------------------------------------------------------------------
-- Personality traits  (same 7 as the original)
------------------------------------------------------------------------
StoryConfig.Traits = {
	"curious",     -- Explores, asks questions, investigates
	"cautious",    -- Hesitates, thinks first, avoids risk
	"bold",        -- Acts decisively, takes risks, confronts
	"kind",        -- Helps, empathizes, protects
	"detached",    -- Observes, stays neutral, holds back
	"honest",      -- Tells truth, direct, transparent
	"deceptive",   -- Lies, manipulates, hides
}

-- Human-readable tendency descriptions (from the original)
StoryConfig.Tendencies = {
	curious   = "one who seeks to understand",
	cautious  = "one who thinks before acting",
	bold      = "one who moves without hesitation",
	kind      = "one who cares for others",
	detached  = "one who observes from a distance",
	honest    = "one who speaks truth",
	deceptive = "one who keeps things hidden",
}

-- Default personality (all zeros)
StoryConfig.DefaultPersonality = {}
for _, trait in StoryConfig.Traits do
	StoryConfig.DefaultPersonality[trait] = 0
end

------------------------------------------------------------------------
-- World state
-- Server aggregates all online players' traits into a mood.
-- Thresholds: if the average of the dominant trait across players
-- exceeds this value, the world shifts.
------------------------------------------------------------------------
StoryConfig.WorldMoods = {
	{
		name = "Welcoming",
		dominantTrait = "kind",
		threshold = 1.5,
		skyColor   = Color3.fromRGB(135, 190, 230),
		ambientColor = Color3.fromRGB(180, 200, 170),
		fogEnd     = 400,
		brightness = 2.0,
		npcGreeting = "The town feels warm today.",
	},
	{
		name = "Tense",
		dominantTrait = "bold",
		threshold = 1.5,
		skyColor   = Color3.fromRGB(200, 140, 100),
		ambientColor = Color3.fromRGB(180, 150, 130),
		fogEnd     = 250,
		brightness = 1.5,
		npcGreeting = "There is an edge in the air.",
	},
	{
		name = "Quiet",
		dominantTrait = "cautious",
		threshold = 1.5,
		skyColor   = Color3.fromRGB(160, 170, 190),
		ambientColor = Color3.fromRGB(150, 155, 165),
		fogEnd     = 200,
		brightness = 1.2,
		npcGreeting = "The town holds its breath.",
	},
	{
		name = "Suspicious",
		dominantTrait = "deceptive",
		threshold = 1.5,
		skyColor   = Color3.fromRGB(100, 95, 110),
		ambientColor = Color3.fromRGB(120, 110, 120),
		fogEnd     = 150,
		brightness = 0.8,
		npcGreeting = "Trust is scarce here.",
	},
	{
		name = "Curious",
		dominantTrait = "curious",
		threshold = 1.5,
		skyColor   = Color3.fromRGB(170, 180, 220),
		ambientColor = Color3.fromRGB(160, 170, 200),
		fogEnd     = 350,
		brightness = 1.8,
		npcGreeting = "Questions fill the air.",
	},
}

-- Default mood when no trait dominates
StoryConfig.DefaultMood = {
	name = "Neutral",
	skyColor   = Color3.fromRGB(160, 170, 180),
	ambientColor = Color3.fromRGB(150, 150, 150),
	fogEnd     = 300,
	brightness = 1.5,
	npcGreeting = "The town is as it always is.",
}

------------------------------------------------------------------------
-- NPC definitions
-- Each NPC has a location, appearance, and a dialogue tree key.
-- Dialogue trees are defined separately below.
------------------------------------------------------------------------
StoryConfig.NPCs = {
	{
		id          = "keeper",
		name        = "The Keeper",
		role        = "Town gatekeeper",
		position    = Vector3.new(0, 0, -80),  -- town gate
		bodyColor   = Color3.fromRGB(120, 100, 80),
		shirtColor  = Color3.fromRGB(80, 70, 60),
		dialogueKey = "keeper_dialogue",
		description = "An old figure standing by the gate, watching everyone who arrives.",
	},
	{
		id          = "guide",
		name        = "The Guide",
		role        = "Crossroads wanderer",
		position    = Vector3.new(-40, 0, -20),
		bodyColor   = Color3.fromRGB(90, 110, 130),
		shirtColor  = Color3.fromRGB(60, 80, 100),
		dialogueKey = "guide_dialogue",
		description = "A hooded figure at the crossroads, pointing in every direction at once.",
	},
	{
		id          = "stranger",
		name        = "The Wounded Stranger",
		role        = "Injured traveler",
		position    = Vector3.new(35, 0, -30),
		bodyColor   = Color3.fromRGB(140, 120, 110),
		shirtColor  = Color3.fromRGB(100, 80, 70),
		dialogueKey = "stranger_dialogue",
		description = "A figure slumped against the wall, head bowed, looking exhausted.",
	},
	{
		id          = "merchant",
		name        = "The Merchant",
		role        = "Market trader",
		position    = Vector3.new(50, 0, 20),
		bodyColor   = Color3.fromRGB(150, 130, 90),
		shirtColor  = Color3.fromRGB(130, 110, 70),
		dialogueKey = "merchant_dialogue",
		description = "A sharp-eyed trader behind a market stall, weighing you with their gaze.",
	},
	{
		id          = "scholar",
		name        = "The Scholar",
		role        = "Library keeper",
		position    = Vector3.new(-50, 0, 30),
		bodyColor   = Color3.fromRGB(100, 100, 120),
		shirtColor  = Color3.fromRGB(70, 70, 100),
		dialogueKey = "scholar_dialogue",
		description = "Surrounded by stacks of books, muttering theories to no one in particular.",
	},
	{
		id          = "guardian",
		name        = "The Guardian",
		role        = "Tower sentinel",
		position    = Vector3.new(0, 0, 60),
		bodyColor   = Color3.fromRGB(80, 80, 90),
		shirtColor  = Color3.fromRGB(50, 50, 60),
		dialogueKey = "guardian_dialogue",
		description = "A tall, still figure in front of the tower door. Watching.",
	},
	{
		id          = "voice",
		name        = "The Voice",
		role        = "The presence in the tower",
		position    = Vector3.new(0, 0, 80),
		bodyColor   = Color3.fromRGB(200, 200, 210),
		shirtColor  = Color3.fromRGB(180, 180, 200),
		dialogueKey = "voice_dialogue",
		description = "A figure made of light, standing in the center of the tower.",
	},
}

------------------------------------------------------------------------
-- Buildings / landmarks
-- Defines the physical structures in the town.
------------------------------------------------------------------------
StoryConfig.Buildings = {
	{
		name     = "Town Gate",
		center   = Vector3.new(0, 0, -90),
		size     = Vector3.new(30, 14, 4),
		color    = Color3.fromRGB(100, 85, 70),
		material = Enum.Material.Cobblestone,
		hasRoof  = false,
	},
	{
		name     = "Crossroads",
		center   = Vector3.new(-40, 0, -20),
		size     = Vector3.new(20, 1, 20),
		color    = Color3.fromRGB(140, 130, 120),
		material = Enum.Material.Slate,
		hasRoof  = false,
	},
	{
		name     = "Shelter Wall",
		center   = Vector3.new(35, 0, -35),
		size     = Vector3.new(16, 10, 2),
		color    = Color3.fromRGB(110, 100, 90),
		material = Enum.Material.Cobblestone,
		hasRoof  = false,
	},
	{
		name     = "Market Stall",
		center   = Vector3.new(50, 0, 20),
		size     = Vector3.new(14, 8, 10),
		color    = Color3.fromRGB(130, 110, 70),
		material = Enum.Material.WoodPlanks,
		hasRoof  = true,
	},
	{
		name     = "Library",
		center   = Vector3.new(-50, 0, 30),
		size     = Vector3.new(20, 14, 16),
		color    = Color3.fromRGB(90, 85, 100),
		material = Enum.Material.Cobblestone,
		hasRoof  = true,
	},
	{
		name     = "The Tower",
		center   = Vector3.new(0, 0, 70),
		size     = Vector3.new(16, 30, 16),
		color    = Color3.fromRGB(60, 60, 70),
		material = Enum.Material.Cobblestone,
		hasRoof  = true,
	},
	{
		name     = "Town Square",
		center   = Vector3.new(0, 0, 0),
		size     = Vector3.new(40, 1, 40),
		color    = Color3.fromRGB(150, 140, 130),
		material = Enum.Material.Slate,
		hasRoof  = false,
	},
}

------------------------------------------------------------------------
-- Dialogue trees
--
-- Each tree is a table of nodes keyed by nodeId.
-- Node fields:
--   text       = what the NPC says (string or table of strings for multi-line)
--   choices    = list of {text, nextNode, traits, memory}
--                traits = {traitName = amount} to add on pick
--                memory = string to store in player's memory (optional)
--   condition  = optional function(personality, memories) → bool
--                if false, this node is skipped (goes to fallback)
--   fallback   = nodeId to go to if condition fails
--   isEnd      = true if this node ends the conversation
--
-- Special node IDs:
--   "start"    = entry point
--   "return"   = NPC says something short when player revisits
------------------------------------------------------------------------
StoryConfig.DialogueTrees = {

	-- ================================================================
	-- THE KEEPER — first contact, asks your "name" (symbolic)
	-- ================================================================
	keeper_dialogue = {
		start = {
			text = {
				"You've arrived.",
				"Most people pass through that gate without stopping.",
				"But you stopped. That means something.",
				"Tell me — what brings you to this place?",
			},
			choices = {
				{text = "I'm looking for answers.", nextNode = "answers", traits = {curious = 1}},
				{text = "I don't know. I just ended up here.", nextNode = "honest_arrival", traits = {honest = 1}},
				{text = "None of your business.", nextNode = "bold_arrival", traits = {bold = 1}},
				{text = "Someone sent me.", nextNode = "lie_arrival", traits = {deceptive = 1}},
			},
		},
		answers = {
			text = {
				"Answers. That's ambitious.",
				"The town has some. Not all of them are comfortable.",
				"You'll find people here who know things. Whether they'll share depends on how you ask.",
				"The crossroads is a good place to start. Or the library, if you're patient.",
			},
			memory = "told the Keeper they sought answers",
			isEnd = true,
		},
		honest_arrival = {
			text = {
				"You don't know. That's honest.",
				"Most people who come here have a story ready. You didn't bother.",
				"I respect that.",
				"Walk the town. Talk to people. Maybe you'll figure it out.",
			},
			memory = "admitted not knowing why they came",
			isEnd = true,
		},
		bold_arrival = {
			text = {
				"Ha. Direct. I like that.",
				"Or maybe I don't. Doesn't matter.",
				"The town is ahead. Do what you will.",
				"Just know — the town remembers.",
			},
			memory = "refused to explain themselves to the Keeper",
			isEnd = true,
		},
		lie_arrival = {
			text = {
				"Someone sent you. Is that so.",
				"Interesting. No one has sent anyone here in a very long time.",
				"But I won't press. Secrets have their uses.",
				"Go on, then. Do what you were 'sent' to do.",
			},
			memory = "lied to the Keeper about being sent",
			isEnd = true,
		},
		returnVisit = {
			text = {"The Keeper nods. 'Still here. Good.'"},
			isEnd = true,
		},
	},

	-- ================================================================
	-- THE GUIDE — crossroads, tests direction and instinct
	-- ================================================================
	guide_dialogue = {
		start = {
			text = {
				"Three paths. Left goes to the market. Right goes to the library.",
				"Straight ahead, the tower. But the tower is... particular about visitors.",
				"Which way interests you?",
			},
			choices = {
				{text = "What's in the tower?", nextNode = "tower_curious", traits = {curious = 1}},
				{text = "Which way is safest?", nextNode = "safe_path", traits = {cautious = 1}},
				{text = "I'll figure it out myself.", nextNode = "self_reliant", traits = {bold = 1}},
				{text = "What do you recommend?", nextNode = "kind_ask", traits = {kind = 1}},
			},
		},
		tower_curious = {
			text = {
				"The tower? That's where the Voice lives.",
				"Not everyone gets to speak with it. It depends on who you've been.",
				"The Guardian at the door decides. Impress them or... convince them.",
				"But I'd talk to the others in town first. Build a story worth telling.",
			},
			memory = "asked the Guide about the tower",
			isEnd = true,
		},
		safe_path = {
			text = {
				"Safest? Hmm. The library, probably. The Scholar doesn't bite.",
				"The market is fine too, though the Merchant drives a hard bargain.",
				"Avoid the alley by the shelter wall unless you want complications.",
				"But then again, some complications are worth having.",
			},
			memory = "asked the Guide for the safe path",
			isEnd = true,
		},
		self_reliant = {
			text = {
				"Fair enough. You don't need a guide.",
				"Just remember — the town watches. What you do here sticks.",
				"Every person you talk to remembers. Every choice leaves a mark.",
				"Good luck.",
			},
			memory = "told the Guide they'd find their own way",
			isEnd = true,
		},
		kind_ask = {
			text = {
				"My recommendation? Talk to everyone. Listen more than you speak.",
				"The Wounded Stranger by the shelter wall — they could use a kind word.",
				"Kindness isn't common here. It gets noticed.",
				"And between you and me, the Voice notices it most of all.",
			},
			memory = "asked the Guide for a recommendation",
			isEnd = true,
		},
		returnVisit = {
			text = {"The Guide gestures vaguely. 'Still finding your way? That's fine. Take your time.'"},
			isEnd = true,
		},
	},

	-- ================================================================
	-- THE WOUNDED STRANGER — the key scene from the original
	-- ================================================================
	stranger_dialogue = {
		start = {
			text = {
				"...",
				"The figure looks up. Their eyes are tired but clear.",
				"'You stopped,' they say. 'Not everyone does.'",
			},
			choices = {
				{text = "Are you alright? Can I help?", nextNode = "offer_help", traits = {kind = 2}},
				{text = "What happened to you?", nextNode = "ask_what", traits = {curious = 1}},
				{text = "I'm just passing through.", nextNode = "pass_by", traits = {detached = 1}},
				{text = "Get up. Sitting here won't help.", nextNode = "tough_love", traits = {bold = 1}},
			},
		},
		offer_help = {
			text = {
				"They look at you for a long moment.",
				"'You mean that. I can tell.'",
				"They press something into your hand — a small stone, warm to the touch.",
				"'A kindness token. The tower... respects these.'",
				"'Thank you for seeing me.'",
			},
			memory = "helped the Wounded Stranger and received the kindness token",
			traits = {kind = 1},
			isEnd = true,
		},
		ask_what = {
			text = {
				"'What happened?' They almost laugh.",
				"'The same thing that happens to everyone here eventually.'",
				"'I made choices. Some of them caught up with me.'",
				"'But I'm still here. That counts for something.'",
				"They hold out a small stone. 'Take this. You asked. That matters.'",
			},
			memory = "asked the Stranger what happened and received the stone",
			isEnd = true,
		},
		pass_by = {
			text = {
				"'I understand,' they say quietly.",
				"'Most people are just passing through.'",
				"You walk on. Their eyes follow you for a moment, then look away.",
			},
			memory = "walked past the Wounded Stranger",
			isEnd = true,
		},
		tough_love = {
			text = {
				"They flinch. Then, slowly, they stand.",
				"'You're right. Sitting here isn't doing anything.'",
				"'That's a hard way to help someone. But it worked.'",
				"They nod at you, once, and walk away.",
			},
			memory = "told the Stranger to get up",
			isEnd = true,
		},
		returnVisit = {
			text = {"The Stranger nods quietly. 'You came back. That says something.'"},
			isEnd = true,
		},
	},

	-- ================================================================
	-- THE MERCHANT — tests honesty and shrewdness
	-- ================================================================
	merchant_dialogue = {
		start = {
			text = {
				"'Ah, a customer. Or a browser. I can tell which within three sentences.'",
				"'I have information, not goods. Answers cost nothing — but the right question is expensive.'",
				"'What would you like to know?'",
			},
			choices = {
				{text = "What can you tell me about the Voice?", nextNode = "voice_info", traits = {curious = 1}},
				{text = "What's the most valuable thing in this town?", nextNode = "value_q", traits = {cautious = 1}},
				{text = "I don't trust merchants.", nextNode = "distrust", traits = {honest = 1}},
				{text = "I'll tell you what you want to hear if you tell me what I need.", nextNode = "trade_lies", traits = {deceptive = 1}},
			},
		},
		voice_info = {
			text = {
				"'The Voice? It knows things. Everything that happens in this town reaches it.'",
				"'Your choices. Your conversations. How you treated the Stranger.'",
				"'It weighs you. Not on a scale — on a story.'",
				"'Make sure yours is one worth telling.'",
			},
			memory = "asked the Merchant about the Voice",
			isEnd = true,
		},
		value_q = {
			text = {
				"'Most valuable thing? Reputation.'",
				"'In a place where everyone remembers, what people think of you IS currency.'",
				"'Be kind and doors open. Be clever and different doors open.'",
				"'Be dishonest and... well. Every door has a memory.'",
			},
			memory = "asked the Merchant about value",
			isEnd = true,
		},
		distrust = {
			text = {
				"'Ha! Honest. I appreciate that, even if it stings.'",
				"'Most people smile and lie. You just... said it.'",
				"'Tell you what — free advice, since you earned it with that honesty.'",
				"'The Guardian respects directness. Remember that at the tower.'",
			},
			memory = "was honest with the Merchant about distrust",
			traits = {honest = 1},
			isEnd = true,
		},
		trade_lies = {
			text = {
				"The Merchant's eyes narrow, then they smile.",
				"'A trade of fictions. I like your style.'",
				"'Fine. Here's what I know: the Voice can tell when you're lying.'",
				"'So can I. But I don't mind. Lies are just stories that haven't become true yet.'",
			},
			memory = "tried to trade lies with the Merchant",
			isEnd = true,
		},
		returnVisit = {
			text = {"'Back again? Business must be slow.' The Merchant smirks."},
			isEnd = true,
		},
	},

	-- ================================================================
	-- THE SCHOLAR — rewards curiosity and patience
	-- ================================================================
	scholar_dialogue = {
		start = {
			text = {
				"The Scholar looks up from a pile of books, surprised.",
				"'A visitor? Unusual. Most people skip the library.'",
				"'Are you here to learn, or just to browse the spines?'",
			},
			choices = {
				{text = "I want to understand how this place works.", nextNode = "understand", traits = {curious = 2}},
				{text = "Do you have anything useful?", nextNode = "useful", traits = {bold = 1}},
				{text = "I'm just looking around.", nextNode = "browse", traits = {detached = 1}},
				{text = "What's your story?", nextNode = "personal", traits = {kind = 1}},
			},
		},
		understand = {
			text = {
				"The Scholar's eyes light up.",
				"'Now THAT is the right question. Most people ask what to do. You asked how it works.'",
				"'This town remembers. Every choice you make is stored. Every person you talk to updates the collective memory.'",
				"'The world itself shifts based on who visits and what they do.'",
				"'Right now, the town feels the way it does because of everyone who came before you.'",
				"'And you are adding to that. Right now. With this conversation.'",
			},
			memory = "learned from the Scholar how the town works",
			traits = {curious = 1},
			isEnd = true,
		},
		useful = {
			text = {
				"'Useful?' The Scholar sighs.",
				"'Knowledge is always useful. Whether you recognize it depends on you.'",
				"'Here is something useful: the Voice responds differently to different people.'",
				"'Who you've been in this town shapes what the Voice says to you.'",
				"'That's the most useful thing I know.'",
			},
			memory = "demanded useful information from the Scholar",
			isEnd = true,
		},
		browse = {
			text = {
				"'Just looking. Fair enough.'",
				"The Scholar returns to their books.",
				"As you turn to leave, they call out:",
				"'The best discoveries happen when you're not looking for anything specific.'",
			},
			memory = "browsed the library without engaging",
			isEnd = true,
		},
		personal = {
			text = {
				"The Scholar pauses. No one has asked them that in a long time.",
				"'My story? I came here like you. Made choices. Ended up with books.'",
				"'I chose curiosity over everything else. It led me here.'",
				"'Not the worst fate. But sometimes I wonder what kindness would have looked like.'",
				"'Thank you for asking.'",
			},
			memory = "asked the Scholar about their personal story",
			traits = {kind = 1},
			isEnd = true,
		},
		returnVisit = {
			text = {"The Scholar waves a hand. 'Pull up a chair. Stay as long as you like.'"},
			isEnd = true,
		},
	},

	-- ================================================================
	-- THE GUARDIAN — blocks the tower, tests worthiness
	-- ================================================================
	guardian_dialogue = {
		start = {
			text = {
				"The Guardian stands motionless in front of the tower door.",
				"'The Voice is inside. Not everyone is permitted to enter.'",
				"'Tell me why you should.'",
			},
			choices = {
				{text = "Because I've listened. I've learned. I've been paying attention.", nextNode = "earned_it", traits = {curious = 1}},
				{text = "Because someone in this town needs help, and the Voice might know how.", nextNode = "for_others", traits = {kind = 1}},
				{text = "Step aside. I'm going in.", nextNode = "force_entry", traits = {bold = 2}},
				{text = "I don't need a reason. Open the door.", nextNode = "demand", traits = {bold = 1}},
			},
		},
		earned_it = {
			text = {
				"The Guardian studies you.",
				"'Attention. That is... uncommon.'",
				"'Most who come here are in a rush. You took the time.'",
				"A pause. The door clicks open.",
				"'Go. The Voice will know what to do with you.'",
			},
			memory = "convinced the Guardian through attentiveness",
			isEnd = true,
		},
		for_others = {
			text = {
				"The Guardian's expression shifts — almost imperceptibly.",
				"'For someone else. Not for yourself.'",
				"'That is the rarest reason anyone gives.'",
				"The door opens.",
				"'The Voice will want to meet you.'",
			},
			memory = "entered the tower to help someone else",
			traits = {kind = 1},
			isEnd = true,
		},
		force_entry = {
			text = {
				"You move toward the door. The Guardian doesn't budge.",
				"For a moment, you stare each other down.",
				"Then the Guardian steps aside.",
				"'Boldness has its own kind of permission. Go.'",
				"'But the Voice sees everything. Remember that.'",
			},
			memory = "forced past the Guardian",
			isEnd = true,
		},
		demand = {
			text = {
				"'No reason.' The Guardian considers this.",
				"'Honest, at least. Or simply impatient.'",
				"'Either way — the door is open. It was always open.'",
				"'The question was never whether you could enter. It was how you asked.'",
			},
			memory = "demanded entry without justification",
			traits = {honest = 1},
			isEnd = true,
		},
		returnVisit = {
			text = {"The Guardian nods. 'The door remains open for you.'"},
			isEnd = true,
		},
	},

	-- ================================================================
	-- THE VOICE — the climactic encounter, reflects personality
	-- Dialogue is partially dynamic; the server injects personality
	-- data into the text at runtime.  {tendency}, {memory}, and
	-- {name} are placeholder tokens replaced by StoryServer.
	-- ================================================================
	voice_dialogue = {
		start = {
			text = {
				"The tower interior is vast. You cannot see the walls. Cannot see the ceiling.",
				"Just darkness, and in the center, a soft light.",
				"A voice speaks. It comes from everywhere.",
				"'I have watched you, {name}.'",
				"'You are {tendency}.'",
				"'{memory_reflection}'",
				"'I have one question for you.'",
				"'Why are you here?'",
			},
			choices = {
				{text = "Tell the truth: I don't know.", nextNode = "voice_truth", traits = {honest = 2}},
				{text = "I'm looking for a way out.", nextNode = "voice_escape", traits = {cautious = 1}},
				{text = "I came to find you.", nextNode = "voice_confront", traits = {bold = 1}},
				{text = "Lie: someone sent me.", nextNode = "voice_lie", traits = {deceptive = 2}},
			},
		},
		voice_truth = {
			text = {
				"'You don't know,' the Voice repeats.",
				"There is no judgment in it. Just acknowledgment.",
				"'Honesty is rare here. Most who come have stories prepared.'",
				"'You gave me something real.'",
				"'{ending_truth}'",
			},
			memory = "told the Voice the truth",
			isEnd = true,
		},
		voice_escape = {
			text = {
				"'A way out,' the Voice muses.",
				"'There are many doors. You've passed through several already.'",
				"'But out? Out suggests you know what's in and what's beyond.'",
				"'Do you?'",
				"'{ending_escape}'",
			},
			memory = "told the Voice they wanted to escape",
			isEnd = true,
		},
		voice_confront = {
			text = {
				"'You came for me.'",
				"The light flickers, almost like laughter.",
				"'Bold. You have been bold since you arrived.'",
				"'Very well. Here I am. What will you do now?'",
				"'{ending_confront}'",
			},
			memory = "confronted the Voice directly",
			isEnd = true,
		},
		voice_lie = {
			text = {
				"'Sent by someone,' the Voice says.",
				"A pause.",
				"'We both know that isn't true.'",
				"'But I won't hold it against you. Deception is a kind of protection.'",
				"'What are you protecting?'",
				"'{ending_lie}'",
			},
			memory = "lied to the Voice",
			isEnd = true,
		},
		returnVisit = {
			text = {"The light pulses gently. 'You returned. The story continues.'"},
			isEnd = true,
		},
	},
}

------------------------------------------------------------------------
-- Ending text templates (injected by server based on personality)
------------------------------------------------------------------------
StoryConfig.Endings = {
	kind_dominant = {
		"The light wraps around you, warm and gentle.",
		"'Kindness is not weakness,' the Voice says. 'It is a choice.'",
		"'And you made it when no one was watching.'",
	},
	curious_dominant = {
		"The light opens outward, revealing infinite depth.",
		"'You asked questions. You looked closer.'",
		"'Most people walk through the world without seeing. You chose to see.'",
	},
	bold_dominant = {
		"The light becomes a doorway.",
		"'You didn't hesitate. You didn't flinch.'",
		"'That kind of courage has a cost, but also a gift.'",
	},
	deceptive_dominant = {
		"The light fades to a soft gray.",
		"'The stories we tell shape who we become.'",
		"'This time, no one is watching which path you take.'",
	},
	detached_dominant = {
		"The light simply illuminates a door.",
		"'You held yourself apart. There's wisdom in that. And loneliness too.'",
		"'Through there. When you're ready to be closer to things.'",
	},
	default = {
		"The light fades gently, like a sunset.",
		"'You are who you are. That is enough.'",
		"'Not everyone needs to be defined. Some people just... are.'",
	},
}

------------------------------------------------------------------------
-- DataStore keys
------------------------------------------------------------------------
StoryConfig.DataStoreKey         = "LivingStoryRPG_v1"
StoryConfig.PersonalityKey       = "personality"
StoryConfig.MemoriesKey          = "memories"
StoryConfig.VisitedNPCsKey       = "visitedNPCs"
StoryConfig.ChoiceCountKey       = "choiceCount"
StoryConfig.AutoSaveInterval     = 120  -- seconds
StoryConfig.MaxMemories          = 50

------------------------------------------------------------------------
-- Timing
------------------------------------------------------------------------
StoryConfig.TypewriterDelay     = 0.03   -- seconds per character
StoryConfig.PunctuationPause    = 0.15   -- extra delay for . ! ?
StoryConfig.LinePause           = 0.8    -- pause between dialogue lines
StoryConfig.WorldStateUpdateRate = 30    -- seconds between world mood recalc

------------------------------------------------------------------------
-- Interaction
------------------------------------------------------------------------
StoryConfig.InteractionRange    = 12     -- ProximityPrompt max distance
StoryConfig.NPCHeight           = 5.5    -- humanoid scale
StoryConfig.NPCHeadSize         = 1.2

return StoryConfig
