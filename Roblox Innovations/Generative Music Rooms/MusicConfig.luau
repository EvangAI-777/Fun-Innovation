--[[
	MusicConfig.luau
	ModuleScript → ReplicatedStorage

	Shared configuration for Generative Music Rooms.
	Six rooms, one per mood. Each room defines geometry style, scale,
	tempo, layer behaviour, and visual pulse parameters.
]]

local MusicConfig = {}

------------------------------------------------------------------------
-- World layout
------------------------------------------------------------------------
MusicConfig.HallwayWidth   = 20   -- studs between rooms
MusicConfig.RoomSize        = Vector3.new(60, 30, 60)
MusicConfig.WallThickness   = 2
MusicConfig.FloorY          = 0
MusicConfig.SpawnOffset     = Vector3.new(0, 5, 0) -- above lobby center

-- Lobby sits at origin; rooms radiate outward in a hexagonal ring
MusicConfig.LobbyRadius     = 80   -- distance from origin to room center
MusicConfig.LobbySize        = Vector3.new(40, 20, 40)

------------------------------------------------------------------------
-- Musical scales (semitone intervals from root)
------------------------------------------------------------------------
MusicConfig.Scales = {
	pentatonic  = {0, 2, 4, 7, 9},
	major       = {0, 2, 4, 5, 7, 9, 11},
	minor       = {0, 2, 3, 5, 7, 8, 10},
	dorian      = {0, 2, 3, 5, 7, 9, 10},
	phrygian    = {0, 1, 3, 5, 7, 8, 10},
	lydian      = {0, 2, 4, 6, 7, 9, 11},
	mixolydian  = {0, 2, 4, 5, 7, 9, 10},
	blues       = {0, 3, 5, 6, 7, 10},
	japanese    = {0, 1, 5, 7, 8},
	arabic      = {0, 1, 4, 5, 7, 8, 11},
}

------------------------------------------------------------------------
-- Layer definitions
-- Each layer is a logical sound channel. The server decides which
-- layers are active; the client manages Sound objects and visuals.
------------------------------------------------------------------------
MusicConfig.Layers = {
	bass       = {order = 1, baseVolume = 0.7,  fadeTime = 1.5},
	pad        = {order = 2, baseVolume = 0.5,  fadeTime = 2.0},
	melody     = {order = 3, baseVolume = 0.6,  fadeTime = 1.0},
	arp        = {order = 4, baseVolume = 0.45, fadeTime = 0.8},
	percussion = {order = 5, baseVolume = 0.55, fadeTime = 0.6},
}

------------------------------------------------------------------------
-- Room definitions  (6 rooms = 6 moods)
--
-- geometry:
--   wallStyle   – how the SoundscapeEngine builds walls
--                 "sine", "sawtooth", "square", "triangle", "noise", "flat"
--   wallPeriods – number of waveform cycles across each wall
--   ceilingOpen – if true the ceiling is omitted (open sky)
--
-- music:
--   scale       – key into MusicConfig.Scales
--   bpm         – beats per minute (visual + audio clock)
--   rootNote    – MIDI note number for the root pitch
--   layerThresholds – minimum player count to activate each layer
--
-- visuals:
--   baseColor    – room ambient colour (Color3)
--   pulseColor   – colour during beat pulse
--   pulseScale   – how much geometry scales on the beat (1 = no change)
--   particleRate – base particle emission rate
------------------------------------------------------------------------
MusicConfig.Rooms = {
	{
		name       = "Calm",
		mood       = "calm",
		geometry   = {wallStyle = "sine", wallPeriods = 2, ceilingOpen = false},
		music      = {
			scale  = "pentatonic",
			bpm    = 72,
			rootNote = 48, -- C3
			layerThresholds = {bass = 1, pad = 1, melody = 2, arp = 3, percussion = 4},
		},
		visuals    = {
			baseColor    = Color3.fromRGB(40, 60, 90),
			pulseColor   = Color3.fromRGB(70, 100, 140),
			pulseScale   = 1.03,
			particleRate = 4,
		},
	},
	{
		name       = "Dreamy",
		mood       = "dreamy",
		geometry   = {wallStyle = "sine", wallPeriods = 4, ceilingOpen = true},
		music      = {
			scale  = "lydian",
			bpm    = 64,
			rootNote = 53, -- F3
			layerThresholds = {bass = 1, pad = 1, melody = 1, arp = 3, percussion = 5},
		},
		visuals    = {
			baseColor    = Color3.fromRGB(80, 50, 120),
			pulseColor   = Color3.fromRGB(140, 90, 200),
			pulseScale   = 1.05,
			particleRate = 8,
		},
	},
	{
		name       = "Tense",
		mood       = "tense",
		geometry   = {wallStyle = "sawtooth", wallPeriods = 6, ceilingOpen = false},
		music      = {
			scale  = "phrygian",
			bpm    = 100,
			rootNote = 45, -- A2
			layerThresholds = {bass = 1, pad = 2, melody = 2, arp = 3, percussion = 3},
		},
		visuals    = {
			baseColor    = Color3.fromRGB(90, 30, 30),
			pulseColor   = Color3.fromRGB(180, 50, 50),
			pulseScale   = 1.08,
			particleRate = 6,
		},
	},
	{
		name       = "Uplifting",
		mood       = "uplifting",
		geometry   = {wallStyle = "triangle", wallPeriods = 3, ceilingOpen = true},
		music      = {
			scale  = "major",
			bpm    = 120,
			rootNote = 60, -- C4
			layerThresholds = {bass = 1, pad = 1, melody = 1, arp = 2, percussion = 2},
		},
		visuals    = {
			baseColor    = Color3.fromRGB(50, 90, 50),
			pulseColor   = Color3.fromRGB(100, 200, 100),
			pulseScale   = 1.06,
			particleRate = 10,
		},
	},
	{
		name       = "Dark",
		mood       = "dark",
		geometry   = {wallStyle = "square", wallPeriods = 8, ceilingOpen = false},
		music      = {
			scale  = "arabic",
			bpm    = 80,
			rootNote = 41, -- F2
			layerThresholds = {bass = 1, pad = 1, melody = 3, arp = 4, percussion = 4},
		},
		visuals    = {
			baseColor    = Color3.fromRGB(15, 10, 25),
			pulseColor   = Color3.fromRGB(60, 30, 80),
			pulseScale   = 1.10,
			particleRate = 3,
		},
	},
	{
		name       = "Chaos",
		mood       = "chaos",
		geometry   = {wallStyle = "noise", wallPeriods = 12, ceilingOpen = true},
		music      = {
			scale  = "blues",
			bpm    = 140,
			rootNote = 50, -- D3
			layerThresholds = {bass = 1, pad = 1, melody = 1, arp = 1, percussion = 1},
		},
		visuals    = {
			baseColor    = Color3.fromRGB(100, 70, 20),
			pulseColor   = Color3.fromRGB(255, 160, 40),
			pulseScale   = 1.15,
			particleRate = 20,
		},
	},
}

------------------------------------------------------------------------
-- Sound asset configuration
-- Users populate these with Roblox audio asset IDs from the Creator
-- Store.  The system works visually without any audio; adding IDs
-- enables the full audio-reactive experience.
------------------------------------------------------------------------
MusicConfig.SoundAssets = {
	-- Each mood maps to a table of layer → asset ID.
	-- Set an ID to "" or nil to leave that layer silent.
	calm      = {bass = "", pad = "", melody = "", arp = "", percussion = ""},
	dreamy    = {bass = "", pad = "", melody = "", arp = "", percussion = ""},
	tense     = {bass = "", pad = "", melody = "", arp = "", percussion = ""},
	uplifting = {bass = "", pad = "", melody = "", arp = "", percussion = ""},
	dark      = {bass = "", pad = "", melody = "", arp = "", percussion = ""},
	chaos     = {bass = "", pad = "", melody = "", arp = "", percussion = ""},
}

------------------------------------------------------------------------
-- Beat & timing
------------------------------------------------------------------------
MusicConfig.BeatsPerMeasure   = 4
MusicConfig.PulseDuration     = 0.12  -- seconds the visual pulse lasts
MusicConfig.CrossfadeDuration = 1.5   -- seconds to crossfade between rooms

------------------------------------------------------------------------
-- Player activity detection
------------------------------------------------------------------------
MusicConfig.Activity = {
	runSpeedThreshold  = 14,   -- studs/s to count as "running"
	jumpCooldown       = 0.4,  -- min seconds between jump events
	stillThreshold     = 2,    -- studs/s below which player counts as "still"
	stillTimeRequired  = 3.0,  -- seconds of stillness before ambient bed boost
}

------------------------------------------------------------------------
-- Visual geometry
------------------------------------------------------------------------
MusicConfig.WaveResolution    = 40    -- segments per wall for waveform geometry
MusicConfig.WaveAmplitude     = 3     -- stud amplitude for wall waveforms
MusicConfig.FloorTileSize     = 4     -- stud size of floor grid tiles
MusicConfig.FloorTileGap      = 0.3   -- stud gap between floor tiles
MusicConfig.NeonBrightness    = 2     -- Neon material glow multiplier (not a real property; used to scale light range)
MusicConfig.MaxParticleLifetime = 4   -- seconds

------------------------------------------------------------------------
-- Interaction
------------------------------------------------------------------------
MusicConfig.ScaleSelectEnabled   = true  -- let players override a room's scale
MusicConfig.MaxPlayersPerRoom    = 20

return MusicConfig
