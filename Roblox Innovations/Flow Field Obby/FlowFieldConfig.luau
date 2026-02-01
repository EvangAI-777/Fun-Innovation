--[[
    FlowFieldConfig.luau
    ModuleScript -- place in ReplicatedStorage

    Shared configuration for the Flow Field Obby.
    Both server and client read from this so everything stays in sync.
]]

local Config = {}

-- World bounds (studs). The field is a cube centered at origin.
Config.WorldSize = 800

-- Platform settings
Config.PlatformCount = 120
Config.PlatformBaseSize = Vector3.new(12, 2, 12)
Config.PlatformMaterial = Enum.Material.SmoothPlastic
Config.PlatformColor = Color3.fromRGB(40, 50, 70)
Config.PlatformTransparency = 0.15

-- Checkpoint settings (checkpoints are stationary anchor points)
Config.CheckpointCount = 8
Config.CheckpointSize = Vector3.new(16, 3, 16)
Config.CheckpointColor = Color3.fromRGB(0, 200, 120)
Config.CheckpointMaterial = Enum.Material.Neon

-- Noise parameters for the 3D flow field
Config.NoiseScale = 0.008         -- Lower = smoother, larger-scale currents
Config.NoiseSpeed = 0.12          -- How fast the field evolves over time
Config.FlowStrength = 18          -- Base movement speed (studs/sec)

-- Difficulty scaling: as platforms get farther from origin, things get harder
Config.DifficultyRadius = 400     -- Distance at which max difficulty kicks in
Config.MaxNoiseScale = 0.025      -- Noise scale at max difficulty (choppier)
Config.MinPlatformScale = 0.45    -- Platform shrinks to this fraction at max difficulty
Config.MaxFlowStrength = 35       -- Flow strength at max difficulty

-- Turbulence thresholds (magnitude of flow vector)
Config.CalmThreshold = 8          -- Below this = calm zone
Config.TurbulentThreshold = 22    -- Above this = turbulent zone

-- Particle emitter settings (visual flow indicators on platforms)
Config.ParticleLifetime = NumberRange.new(0.4, 1.2)
Config.ParticleRate = 25
Config.ParticleSpeed = NumberRange.new(4, 12)
Config.ParticleSize = NumberSequence.new({
    NumberSequenceKeypoint.new(0, 0.3),
    NumberSequenceKeypoint.new(0.5, 0.15),
    NumberSequenceKeypoint.new(1, 0),
})
Config.ParticleTransparency = NumberSequence.new({
    NumberSequenceKeypoint.new(0, 0.4),
    NumberSequenceKeypoint.new(1, 1),
})
Config.ParticleColor = ColorSequence.new(
    Color3.fromRGB(100, 160, 255),
    Color3.fromRGB(40, 80, 180)
)

-- Respawn settings
Config.FallThreshold = -50        -- Y position below which player respawns
Config.SpawnPosition = Vector3.new(0, 20, 0)

-- Camera settings (client-side)
Config.TurbulentShakeIntensity = 1.5
Config.TurbulentFOVBoost = 8      -- Added to default FOV in turbulent zones

-- HUD
Config.HideUIKey = Enum.KeyCode.H

return Config
