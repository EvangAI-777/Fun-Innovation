--[[
    SkywritingServer.luau
    Script -- place in ServerScriptService

    Handles poem generation requests, creates 3D skywriting text from
    Parts with SurfaceGui labels, drifts them upward, and dissolves
    them over time. Manages the poem lifecycle and enforces cooldowns.
]]

local RunService = game:GetService("RunService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Config = require(ReplicatedStorage:WaitForChild("VerseConfig"))
local PoetryEngine = require(ReplicatedStorage:WaitForChild("PoetryEngine"))

------------------------------------------------------------------------
-- Remote events
------------------------------------------------------------------------

local remotes = Instance.new("Folder")
remotes.Name = "VerseRemotes"
remotes.Parent = ReplicatedStorage

local requestPoemEvent = Instance.new("RemoteEvent")
requestPoemEvent.Name = "RequestPoem"
requestPoemEvent.Parent = remotes

local poemCreatedEvent = Instance.new("RemoteEvent")
poemCreatedEvent.Name = "PoemCreated"
poemCreatedEvent.Parent = remotes

------------------------------------------------------------------------
-- World setup
------------------------------------------------------------------------

-- Ground plane
local ground = Instance.new("Part")
ground.Name = "SkywritingGround"
ground.Size = Config.GroundSize
ground.Position = Vector3.new(0, 0, 0)
ground.Anchored = true
ground.CanCollide = true
ground.Material = Enum.Material.SmoothPlastic
ground.Color = Config.GroundColor
ground.TopSurface = Enum.SurfaceType.Smooth
ground.BottomSurface = Enum.SurfaceType.Smooth
ground.Parent = workspace

-- Spawn location
local spawnLocation = Instance.new("SpawnLocation")
spawnLocation.Size = Vector3.new(12, 1, 12)
spawnLocation.Position = Config.SpawnPosition
spawnLocation.Anchored = true
spawnLocation.CanCollide = false
spawnLocation.Transparency = 1
spawnLocation.Parent = workspace

-- Poems folder
local poemsFolder = Instance.new("Folder")
poemsFolder.Name = "SkyPoems"
poemsFolder.Parent = workspace

------------------------------------------------------------------------
-- Poem tracking
------------------------------------------------------------------------

type ActivePoem = {
    model: Model,
    createdAt: number,
    state: string,       -- "fadein" | "hold" | "fadeout" | "done"
    voice: string,
    parts: { Part },
    labels: { TextLabel },
}

local activePoems: { ActivePoem } = {}
local playerCooldowns: { [Player]: number } = {}

------------------------------------------------------------------------
-- Skywriting: create 3D text in the sky
------------------------------------------------------------------------

--[[
    Build a 3D poem in the sky above the given world position.
    Each line of the poem is a Part with a SurfaceGui TextLabel
    on the front face, plus a particle emitter for the trailing effect.
]]
local function createSkyPoem(lines: {string}, voice: string, worldPos: Vector3): ActivePoem
    local color = Config.VoiceColors[voice] or Color3.fromRGB(200, 200, 200)
    local trailColor = Config.VoiceTrailColors[voice]
        or ColorSequence.new(Color3.fromRGB(180, 180, 180))

    local model = Instance.new("Model")
    model.Name = "SkyPoem_" .. voice
    model.Parent = poemsFolder

    local parts: { Part } = {}
    local labels: { TextLabel } = {}

    -- Calculate the vertical starting position
    local baseY = worldPos.Y + Config.TextHeight
    local baseX = worldPos.X
    local baseZ = worldPos.Z

    for i, line in lines do
        -- Skip empty lines (stanza breaks) but preserve spacing
        if line == "" then continue end

        -- Create the Part that holds the text
        -- Width scales with line length
        local textWidth = math.max(#line * Config.LetterSpacing, 20)
        local partWidth = math.min(textWidth, Config.MaxPoemWidth)

        local part = Instance.new("Part")
        part.Name = "Line_" .. i
        part.Size = Vector3.new(partWidth, Config.LetterPartSize.Y, Config.LetterPartSize.Z)
        part.Position = Vector3.new(baseX, baseY + (i - 1) * -Config.LineSpacing, baseZ)
        part.Anchored = true
        part.CanCollide = false
        part.Transparency = 1  -- The Part itself is invisible; text is on the SurfaceGui
        part.Material = Config.LetterMaterial

        -- Face the text outward on the front face, and also the back so it's readable from both sides
        -- Front SurfaceGui
        local surfaceGui = Instance.new("SurfaceGui")
        surfaceGui.Name = "FrontText"
        surfaceGui.Face = Enum.NormalId.Front
        surfaceGui.SizingMode = Enum.SurfaceGuiSizingMode.PixelsPerStud
        surfaceGui.PixelsPerStud = 24
        surfaceGui.LightInfluence = 0
        surfaceGui.Brightness = 1.5
        surfaceGui.Parent = part

        local textLabel = Instance.new("TextLabel")
        textLabel.Size = UDim2.new(1, 0, 1, 0)
        textLabel.BackgroundTransparency = 1
        textLabel.Text = line
        textLabel.TextColor3 = color
        textLabel.TextSize = 42
        textLabel.Font = Enum.Font.BuilderSansBold
        textLabel.TextScaled = false
        textLabel.TextTransparency = 1  -- Start invisible, fade in
        textLabel.TextXAlignment = Enum.TextXAlignment.Center
        textLabel.TextYAlignment = Enum.TextYAlignment.Center
        textLabel.Parent = surfaceGui

        -- Back SurfaceGui (mirrored so readable from behind too)
        local backGui = Instance.new("SurfaceGui")
        backGui.Name = "BackText"
        backGui.Face = Enum.NormalId.Back
        backGui.SizingMode = Enum.SurfaceGuiSizingMode.PixelsPerStud
        backGui.PixelsPerStud = 24
        backGui.LightInfluence = 0
        backGui.Brightness = 1.5
        backGui.Parent = part

        local backLabel = Instance.new("TextLabel")
        backLabel.Size = UDim2.new(1, 0, 1, 0)
        backLabel.BackgroundTransparency = 1
        backLabel.Text = line
        backLabel.TextColor3 = color
        backLabel.TextSize = 42
        backLabel.Font = Enum.Font.BuilderSansBold
        backLabel.TextScaled = false
        backLabel.TextTransparency = 1
        backLabel.TextXAlignment = Enum.TextXAlignment.Center
        backLabel.TextYAlignment = Enum.TextYAlignment.Center
        backLabel.Parent = backGui

        -- Particle trail
        local emitter = Instance.new("ParticleEmitter")
        emitter.Name = "Trail"
        emitter.Lifetime = Config.TrailLifetime
        emitter.Rate = Config.TrailRate
        emitter.Speed = Config.TrailSpeed
        emitter.Size = Config.TrailSize
        emitter.Transparency = Config.TrailTransparency
        emitter.Color = trailColor
        emitter.EmissionDirection = Enum.NormalId.Top
        emitter.SpreadAngle = Vector2.new(15, 15)
        emitter.LockedToPart = false
        emitter.Parent = part

        -- Glow
        local light = Instance.new("PointLight")
        light.Color = color
        light.Brightness = 0  -- Fades in with text
        light.Range = 15
        light.Parent = part

        part.Parent = model
        table.insert(parts, part)
        table.insert(labels, textLabel)
        table.insert(labels, backLabel)
    end

    local poem: ActivePoem = {
        model = model,
        createdAt = os.clock(),
        state = "fadein",
        voice = voice,
        parts = parts,
        labels = labels,
    }

    return poem
end

------------------------------------------------------------------------
-- Poem lifecycle (fade in, hold, fade out, cleanup)
------------------------------------------------------------------------

local function updatePoems(dt: number)
    local now = os.clock()
    local toRemove = {}

    for i, poem in activePoems do
        local age = now - poem.createdAt

        if poem.state == "fadein" then
            local alpha = math.clamp(age / Config.FadeInDuration, 0, 1)
            for _, label in poem.labels do
                label.TextTransparency = 1 - alpha
            end
            for _, part in poem.parts do
                local light = part:FindFirstChildOfClass("PointLight")
                if light then light.Brightness = alpha * 0.8 end
            end
            if alpha >= 1 then
                poem.state = "hold"
            end

        elseif poem.state == "hold" then
            local holdAge = age - Config.FadeInDuration
            if holdAge >= Config.HoldDuration then
                poem.state = "fadeout"
            end

        elseif poem.state == "fadeout" then
            local fadeAge = age - Config.FadeInDuration - Config.HoldDuration
            local alpha = math.clamp(fadeAge / Config.FadeOutDuration, 0, 1)
            for _, label in poem.labels do
                label.TextTransparency = alpha
            end
            for _, part in poem.parts do
                local light = part:FindFirstChildOfClass("PointLight")
                if light then light.Brightness = (1 - alpha) * 0.8 end
                local emitter = part:FindFirstChild("Trail")
                if emitter and alpha > 0.5 then
                    emitter.Rate = math.floor(Config.TrailRate * (1 - alpha) * 2)
                end
            end
            if alpha >= 1 then
                poem.state = "done"
            end

        elseif poem.state == "done" then
            table.insert(toRemove, i)
        end

        -- Drift upward constantly
        for _, part in poem.parts do
            part.CFrame = part.CFrame + Vector3.new(0, Config.DriftSpeed * dt, 0)
        end
    end

    -- Cleanup finished poems (iterate backwards to preserve indices)
    for j = #toRemove, 1, -1 do
        local idx = toRemove[j]
        local poem = activePoems[idx]
        if poem.model then
            poem.model:Destroy()
        end
        table.remove(activePoems, idx)
    end
end

------------------------------------------------------------------------
-- Enforce max active poems (oldest dissolve early)
------------------------------------------------------------------------

local function enforceMaxPoems()
    local excess = #activePoems - Config.MaxActivePoems
    for i = 1, excess do
        local oldest = activePoems[i]
        if oldest and oldest.state ~= "fadeout" and oldest.state ~= "done" then
            oldest.state = "fadeout"
            oldest.createdAt = os.clock() - Config.FadeInDuration - Config.HoldDuration
        end
    end
end

------------------------------------------------------------------------
-- Handle poem requests from clients
------------------------------------------------------------------------

requestPoemEvent.OnServerEvent:Connect(function(player: Player, voice: string, form: string)
    -- Validate inputs
    local validVoice = false
    for _, v in Config.Voices do
        if v == voice then validVoice = true break end
    end
    local validForm = false
    for _, f in Config.Forms do
        if f == form then validForm = true break end
    end
    if not validVoice or not validForm then return end

    -- Check cooldown
    local now = os.clock()
    if playerCooldowns[player] and now - playerCooldowns[player] < Config.GenerationCooldown then
        return
    end
    playerCooldowns[player] = now

    -- Get player position
    local character = player.Character
    if not character then return end
    local hrp = character:FindFirstChild("HumanoidRootPart")
    if not hrp then return end

    -- Generate the poem
    local result = PoetryEngine.generate(form, voice)

    -- Create skywriting above the player
    local poem = createSkyPoem(result.lines, result.voice, hrp.Position)
    table.insert(activePoems, poem)
    enforceMaxPoems()

    -- Notify all clients
    poemCreatedEvent:FireAllClients(player.Name, result.voice, result.lines)
end)

------------------------------------------------------------------------
-- Player cleanup
------------------------------------------------------------------------

Players.PlayerRemoving:Connect(function(player)
    playerCooldowns[player] = nil
end)

------------------------------------------------------------------------
-- Main loop
------------------------------------------------------------------------

RunService.Heartbeat:Connect(updatePoems)

print("[VerseEngineSkywriting] Server initialized")
