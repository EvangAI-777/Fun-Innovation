--[[
    PlatformGenerator.luau
    ModuleScript -- place in ServerStorage

    Creates and configures platforms and checkpoints for the Flow Field Obby.
    Each platform gets a ParticleEmitter aligned to the local flow direction
    so the entire world visually streams in the direction of movement.
]]

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Config = require(ReplicatedStorage:WaitForChild("FlowFieldConfig"))

local PlatformGenerator = {}

-- Container folders (created once, reused)
local platformFolder: Folder = nil
local checkpointFolder: Folder = nil

local function ensureFolders()
    if not platformFolder then
        platformFolder = Instance.new("Folder")
        platformFolder.Name = "FlowPlatforms"
        platformFolder.Parent = workspace
    end
    if not checkpointFolder then
        checkpointFolder = Instance.new("Folder")
        checkpointFolder.Name = "Checkpoints"
        checkpointFolder.Parent = workspace
    end
end

--[[
    Create a single drifting platform at the given position.
    Returns the Part so the server can track it.
]]
function PlatformGenerator.createPlatform(position: Vector3, index: number): Part
    ensureFolders()

    local part = Instance.new("Part")
    part.Name = "FlowPlatform_" .. index
    part.Size = Config.PlatformBaseSize
    part.Position = position
    part.Anchored = true
    part.CanCollide = true
    part.Material = Config.PlatformMaterial
    part.Color = Config.PlatformColor
    part.Transparency = Config.PlatformTransparency
    part.TopSurface = Enum.SurfaceType.Smooth
    part.BottomSurface = Enum.SurfaceType.Smooth

    -- Distance from origin determines difficulty-based size scaling
    local dist = (Vector3.new(position.X, 0, position.Z)).Magnitude
    local difficultyAlpha = math.clamp(dist / Config.DifficultyRadius, 0, 1)
    local scaleFactor = 1 - (1 - Config.MinPlatformScale) * difficultyAlpha
    part.Size = Config.PlatformBaseSize * scaleFactor

    -- Particle emitter for visual flow direction (direction set each frame by server)
    local emitter = Instance.new("ParticleEmitter")
    emitter.Name = "FlowParticles"
    emitter.Lifetime = Config.ParticleLifetime
    emitter.Rate = Config.ParticleRate
    emitter.Speed = Config.ParticleSpeed
    emitter.Size = Config.ParticleSize
    emitter.Transparency = Config.ParticleTransparency
    emitter.Color = Config.ParticleColor
    emitter.LockedToPart = false
    emitter.SpreadAngle = Vector2.new(10, 10)
    emitter.Parent = part

    part.Parent = platformFolder
    return part
end

--[[
    Create a checkpoint platform. Checkpoints are stationary anchor points
    -- the ONLY things in the entire experience that don't move.
]]
function PlatformGenerator.createCheckpoint(position: Vector3, index: number): Part
    ensureFolders()

    local part = Instance.new("Part")
    part.Name = "Checkpoint_" .. index
    part.Size = Config.CheckpointSize
    part.Position = position
    part.Anchored = true
    part.CanCollide = true
    part.Material = Config.CheckpointMaterial
    part.Color = Config.CheckpointColor
    part.TopSurface = Enum.SurfaceType.Smooth
    part.BottomSurface = Enum.SurfaceType.Smooth

    -- Glow effect
    local light = Instance.new("PointLight")
    light.Color = Config.CheckpointColor
    light.Brightness = 2
    light.Range = 30
    light.Parent = part

    -- Beacon particle effect so checkpoints are visible from a distance
    local beacon = Instance.new("ParticleEmitter")
    beacon.Name = "Beacon"
    beacon.Lifetime = NumberRange.new(1, 2)
    beacon.Rate = 8
    beacon.Speed = NumberRange.new(2, 5)
    beacon.Size = NumberSequence.new({
        NumberSequenceKeypoint.new(0, 0.5),
        NumberSequenceKeypoint.new(1, 0),
    })
    beacon.Transparency = NumberSequence.new({
        NumberSequenceKeypoint.new(0, 0.2),
        NumberSequenceKeypoint.new(1, 1),
    })
    beacon.Color = ColorSequence.new(Config.CheckpointColor)
    beacon.EmissionDirection = Enum.NormalId.Top
    beacon.SpreadAngle = Vector2.new(5, 5)
    beacon.Parent = part

    -- Tag for easy lookup
    local tag = Instance.new("IntValue")
    tag.Name = "CheckpointIndex"
    tag.Value = index
    tag.Parent = part

    part.Parent = checkpointFolder
    return part
end

--[[
    Generate initial positions for all platforms, distributed through the world volume.
    Uses a loose spiral pattern outward from origin so density is roughly even
    and difficulty naturally increases with distance.
]]
function PlatformGenerator.generatePlatformPositions(): { Vector3 }
    local positions = {}
    local halfWorld = Config.WorldSize / 2
    local count = Config.PlatformCount

    for i = 1, count do
        -- Spiral outward with vertical variation
        local t = (i - 1) / count
        local radius = t * halfWorld * 0.9
        local angle = t * math.pi * 8  -- Multiple revolutions
        local x = math.cos(angle) * radius + (math.random() - 0.5) * 40
        local z = math.sin(angle) * radius + (math.random() - 0.5) * 40
        local y = 10 + math.sin(t * math.pi * 3) * 30 + (math.random() - 0.5) * 20

        table.insert(positions, Vector3.new(x, y, z))
    end

    return positions
end

--[[
    Generate checkpoint positions. Placed at increasing distances from origin
    along the spiral path so players encounter them in order.
]]
function PlatformGenerator.generateCheckpointPositions(): { Vector3 }
    local positions = {}
    local halfWorld = Config.WorldSize / 2

    for i = 1, Config.CheckpointCount do
        local t = i / (Config.CheckpointCount + 1)
        local radius = t * halfWorld * 0.85
        local angle = t * math.pi * 8
        local x = math.cos(angle) * radius
        local z = math.sin(angle) * radius
        local y = 10 + math.sin(t * math.pi * 3) * 25

        table.insert(positions, Vector3.new(x, y, z))
    end

    return positions
end

return PlatformGenerator
