--[[
    FlowFieldServer.luau
    Script -- place in ServerScriptService

    The heart of the Flow Field Obby. Generates platforms and checkpoints,
    then runs a Heartbeat loop that moves every platform according to a 3D
    Perlin noise flow field. The field evolves over time so the path is
    never the same twice.

    Checkpoints are the ONLY stationary objects in the entire experience.
]]

local RunService = game:GetService("RunService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ServerStorage = game:GetService("ServerStorage")

local Config = require(ReplicatedStorage:WaitForChild("FlowFieldConfig"))
local PlatformGenerator = require(ServerStorage:WaitForChild("PlatformGenerator"))

------------------------------------------------------------------------
-- Remote events for client communication
------------------------------------------------------------------------

local remotes = Instance.new("Folder")
remotes.Name = "FlowFieldRemotes"
remotes.Parent = ReplicatedStorage

local checkpointReachedEvent = Instance.new("RemoteEvent")
checkpointReachedEvent.Name = "CheckpointReached"
checkpointReachedEvent.Parent = remotes

local respawnEvent = Instance.new("RemoteEvent")
respawnEvent.Name = "PlayerRespawn"
respawnEvent.Parent = remotes

local flowDataEvent = Instance.new("RemoteEvent")
flowDataEvent.Name = "FlowData"
flowDataEvent.Parent = remotes

------------------------------------------------------------------------
-- Flow field math
------------------------------------------------------------------------

-- Time offset for noise evolution
local timeOffset = 0

--[[
    Sample the 3D flow field at a world position.
    Returns a Vector3 representing the flow direction and magnitude.

    Uses three orthogonal noise samples (one per axis) with offset seeds
    so X, Y, Z flows are independent. The result is a curl-like field
    that naturally creates streams and eddies.
]]
local function sampleFlowField(position: Vector3, noiseScale: number): Vector3
    local px = position.X * noiseScale
    local py = position.Y * noiseScale
    local pz = position.Z * noiseScale
    local t = timeOffset

    -- Three noise channels with different seed offsets
    local fx = math.noise(px, py + 100, pz + t)
        - math.noise(px, py - 100, pz + t)
    local fy = math.noise(px + 200, py, pz + t)
        - math.noise(px - 200, py, pz + t)
    local fz = math.noise(px + 300, py + 300, pz + t)
        - math.noise(px - 300, py - 300, pz + t)

    return Vector3.new(fx, fy * 0.4, fz)  -- Dampen vertical to keep platforms reachable
end

--[[
    Get the noise scale for a position based on distance from origin.
    Farther out = higher frequency = choppier, harder to predict.
]]
local function getLocalNoiseScale(position: Vector3): number
    local dist = Vector3.new(position.X, 0, position.Z).Magnitude
    local alpha = math.clamp(dist / Config.DifficultyRadius, 0, 1)
    return Config.NoiseScale + (Config.MaxNoiseScale - Config.NoiseScale) * alpha
end

--[[
    Get the flow strength for a position based on distance from origin.
]]
local function getLocalFlowStrength(position: Vector3): number
    local dist = Vector3.new(position.X, 0, position.Z).Magnitude
    local alpha = math.clamp(dist / Config.DifficultyRadius, 0, 1)
    return Config.FlowStrength + (Config.MaxFlowStrength - Config.FlowStrength) * alpha
end

------------------------------------------------------------------------
-- World generation
------------------------------------------------------------------------

-- Generate all platforms
local platformPositions = PlatformGenerator.generatePlatformPositions()
local platforms: { Part } = {}

for i, pos in ipairs(platformPositions) do
    local platform = PlatformGenerator.createPlatform(pos, i)
    table.insert(platforms, platform)
end

-- Generate checkpoints
local checkpointPositions = PlatformGenerator.generateCheckpointPositions()
local checkpoints: { Part } = {}

for i, pos in ipairs(checkpointPositions) do
    local checkpoint = PlatformGenerator.createCheckpoint(pos, i)
    table.insert(checkpoints, checkpoint)
end

-- Spawn platform (stationary, at origin, where players start)
local spawnPlatform = Instance.new("Part")
spawnPlatform.Name = "SpawnPlatform"
spawnPlatform.Size = Vector3.new(24, 3, 24)
spawnPlatform.Position = Config.SpawnPosition - Vector3.new(0, 5, 0)
spawnPlatform.Anchored = true
spawnPlatform.CanCollide = true
spawnPlatform.Material = Enum.Material.Neon
spawnPlatform.Color = Color3.fromRGB(255, 255, 255)
spawnPlatform.TopSurface = Enum.SurfaceType.Smooth
spawnPlatform.BottomSurface = Enum.SurfaceType.Smooth
spawnPlatform.Parent = workspace

-- Set spawn location
local spawnLocation = Instance.new("SpawnLocation")
spawnLocation.Size = Vector3.new(20, 1, 20)
spawnLocation.Position = Config.SpawnPosition - Vector3.new(0, 3, 0)
spawnLocation.Anchored = true
spawnLocation.CanCollide = false
spawnLocation.Transparency = 1
spawnLocation.Parent = workspace

------------------------------------------------------------------------
-- Player checkpoint tracking
------------------------------------------------------------------------

local playerCheckpoints: { [Player]: number } = {}

local function onPlayerAdded(player: Player)
    playerCheckpoints[player] = 0

    player.CharacterAdded:Connect(function(character)
        -- Wait for humanoid root part
        local hrp = character:WaitForChild("HumanoidRootPart", 5)
        if not hrp then return end

        -- If they have a checkpoint, teleport there
        local cpIndex = playerCheckpoints[player]
        if cpIndex and cpIndex > 0 and checkpoints[cpIndex] then
            task.wait(0.1)
            hrp.CFrame = checkpoints[cpIndex].CFrame + Vector3.new(0, 5, 0)
        end
    end)
end

local function onPlayerRemoving(player: Player)
    playerCheckpoints[player] = nil
end

Players.PlayerAdded:Connect(onPlayerAdded)
Players.PlayerRemoving:Connect(onPlayerRemoving)

-- Handle existing players (in case script loads late)
for _, player in ipairs(Players:GetPlayers()) do
    task.spawn(onPlayerAdded, player)
end

------------------------------------------------------------------------
-- Checkpoint touch detection
------------------------------------------------------------------------

for _, checkpoint in ipairs(checkpoints) do
    checkpoint.Touched:Connect(function(hit)
        local character = hit.Parent
        if not character then return end
        local player = Players:GetPlayerFromCharacter(character)
        if not player then return end

        local cpIndex = checkpoint:FindFirstChild("CheckpointIndex")
        if not cpIndex then return end

        local current = playerCheckpoints[player] or 0
        if cpIndex.Value > current then
            playerCheckpoints[player] = cpIndex.Value
            checkpointReachedEvent:FireClient(player, cpIndex.Value, Config.CheckpointCount)
        end
    end)
end

------------------------------------------------------------------------
-- Fall detection and respawn
------------------------------------------------------------------------

local function checkFall(player: Player, character: Model)
    local hrp = character:FindFirstChild("HumanoidRootPart")
    if not hrp then return end

    if hrp.Position.Y < Config.FallThreshold then
        local cpIndex = playerCheckpoints[player] or 0
        local respawnPos: Vector3

        if cpIndex > 0 and checkpoints[cpIndex] then
            respawnPos = checkpoints[cpIndex].Position + Vector3.new(0, 5, 0)
        else
            respawnPos = Config.SpawnPosition
        end

        hrp.CFrame = CFrame.new(respawnPos)
        hrp.AssemblyLinearVelocity = Vector3.zero
        respawnEvent:FireClient(player, cpIndex)
    end
end

------------------------------------------------------------------------
-- Main Heartbeat loop
------------------------------------------------------------------------

RunService.Heartbeat:Connect(function(dt: number)
    timeOffset += dt * Config.NoiseSpeed

    -- Move every platform according to the flow field
    for _, platform in ipairs(platforms) do
        local pos = platform.Position
        local noiseScale = getLocalNoiseScale(pos)
        local flowStrength = getLocalFlowStrength(pos)
        local flow = sampleFlowField(pos, noiseScale)

        -- Normalize and apply strength
        local mag = flow.Magnitude
        if mag > 0.001 then
            local direction = flow / mag
            local velocity = direction * flowStrength * dt

            -- Move platform
            platform.CFrame = platform.CFrame + velocity

            -- Orient particle emitter to flow direction
            local emitter = platform:FindFirstChild("FlowParticles")
            if emitter then
                -- Convert world flow direction to local space for emission
                local localDir = platform.CFrame:VectorToObjectSpace(direction)
                -- ParticleEmitter doesn't have a direct direction property,
                -- so we rotate the part slightly to bias emission. Instead,
                -- we adjust speed based on local flow magnitude.
                emitter.Speed = NumberRange.new(
                    math.clamp(mag * 6, 2, 8),
                    math.clamp(mag * 14, 6, 20)
                )
            end

            -- Send flow magnitude to clients for camera/VFX (throttled per platform)
            -- We only send aggregate data, not per-platform
        end

        -- Keep platforms within world bounds (soft wrap)
        local halfWorld = Config.WorldSize / 2
        local px = pos.X
        local py = pos.Y
        local pz = pos.Z

        if math.abs(px) > halfWorld then
            px = -px * 0.8
        end
        if py < -20 then
            py = 40
        elseif py > 80 then
            py = 10
        end
        if math.abs(pz) > halfWorld then
            pz = -pz * 0.8
        end

        if px ~= pos.X or py ~= pos.Y or pz ~= pos.Z then
            platform.Position = Vector3.new(px, py, pz)
        end
    end

    -- Check for fallen players
    for _, player in ipairs(Players:GetPlayers()) do
        local character = player.Character
        if character then
            checkFall(player, character)
        end
    end

    -- Broadcast flow data near each player for client-side VFX (every 6 frames)
    if math.floor(timeOffset * 100) % 6 == 0 then
        for _, player in ipairs(Players:GetPlayers()) do
            local character = player.Character
            if not character then continue end
            local hrp = character:FindFirstChild("HumanoidRootPart")
            if not hrp then continue end

            local pos = hrp.Position
            local noiseScale = getLocalNoiseScale(pos)
            local flow = sampleFlowField(pos, noiseScale)
            flowDataEvent:FireClient(player, flow.Magnitude)
        end
    end
end)

print("[FlowFieldObby] Server initialized -- " .. #platforms .. " platforms, " .. #checkpoints .. " checkpoints")
