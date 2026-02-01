--[[
    VerseConfig.luau
    ModuleScript -- place in ReplicatedStorage

    Shared configuration for Verse Engine Skywriting.
]]

local Config = {}

-- Sky text settings
Config.TextHeight = 120           -- Base Y height where poems appear above the player
Config.DriftSpeed = 4             -- Studs/sec upward drift
Config.LetterSpacing = 3.5        -- Studs between letter parts
Config.LineSpacing = 6            -- Studs between lines of a poem
Config.MaxPoemWidth = 200         -- Studs; lines wrap if wider

-- Poem lifetime
Config.FadeInDuration = 1.5       -- Seconds to fade in
Config.HoldDuration = 18          -- Seconds at full visibility
Config.FadeOutDuration = 8        -- Seconds to fade out and dissolve
Config.MaxActivePoems = 15        -- Per server; oldest dissolve early if exceeded

-- Particle settings for letter rendering
Config.LetterPartSize = Vector3.new(2, 2.5, 0.3)
Config.LetterMaterial = Enum.Material.Neon
Config.LetterTransparency = 0.1

-- Particle trail behind each letter as it drifts
Config.TrailLifetime = NumberRange.new(0.8, 2)
Config.TrailRate = 6
Config.TrailSpeed = NumberRange.new(0.5, 1.5)
Config.TrailSize = NumberSequence.new({
    NumberSequenceKeypoint.new(0, 0.4),
    NumberSequenceKeypoint.new(1, 0),
})
Config.TrailTransparency = NumberSequence.new({
    NumberSequenceKeypoint.new(0, 0.3),
    NumberSequenceKeypoint.new(0.5, 0.6),
    NumberSequenceKeypoint.new(1, 1),
})

-- Voice colors (each voice has a distinct color for its sky text)
Config.VoiceColors = {
    melancholic = Color3.fromRGB(100, 130, 200),
    hopeful     = Color3.fromRGB(255, 210, 100),
    surreal     = Color3.fromRGB(180, 100, 220),
    observational = Color3.fromRGB(160, 210, 170),
    fierce      = Color3.fromRGB(240, 80, 80),
}

-- Trail colors match voice but slightly shifted
Config.VoiceTrailColors = {
    melancholic = ColorSequence.new(Color3.fromRGB(80, 110, 180), Color3.fromRGB(40, 60, 120)),
    hopeful     = ColorSequence.new(Color3.fromRGB(255, 230, 140), Color3.fromRGB(200, 160, 60)),
    surreal     = ColorSequence.new(Color3.fromRGB(160, 80, 200), Color3.fromRGB(100, 40, 160)),
    observational = ColorSequence.new(Color3.fromRGB(140, 200, 150), Color3.fromRGB(80, 140, 90)),
    fierce      = ColorSequence.new(Color3.fromRGB(240, 100, 60), Color3.fromRGB(180, 40, 40)),
}

-- World settings
Config.SpawnPosition = Vector3.new(0, 5, 0)
Config.GroundSize = Vector3.new(400, 1, 400)
Config.GroundColor = Color3.fromRGB(20, 25, 35)

-- Cooldown between poem generations per player (seconds)
Config.GenerationCooldown = 5

-- Forms available
Config.Forms = {"poem", "haiku", "couplet", "fragment"}

-- Voices available
Config.Voices = {"melancholic", "hopeful", "surreal", "observational", "fierce"}

-- Voice descriptions (for the selection GUI)
Config.VoiceDescriptions = {
    melancholic   = "loss, memory, weight",
    hopeful       = "growth, light, opening",
    surreal       = "strange, shifting, dreamlike",
    observational = "quiet, still, noticing",
    fierce        = "sharp, urgent, alive",
}

return Config
