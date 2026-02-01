--[[
    CreatureManager.luau
    ModuleScript -- place in ServerStorage

    Builds terrain, NPC plants, NPC creatures, and handles
    NPC AI behaviors (wander, seek, flee, hunt). Also provides
    utility functions for ecosystem health calculations.
]]

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Config = require(ReplicatedStorage:WaitForChild("EcosystemConfig"))

local Manager = {}

------------------------------------------------------------------------
-- ID generation
------------------------------------------------------------------------

local idCounter = 0

function Manager.generateId(): string
    idCounter += 1
    return "eco_" .. tostring(os.time()) .. "_" .. tostring(idCounter)
end

------------------------------------------------------------------------
-- Helper: make a Part
------------------------------------------------------------------------

local function makePart(props: { [string]: any }): Part
    local part = Instance.new("Part")
    part.Anchored = true
    part.CanCollide = if props.CanCollide ~= nil then props.CanCollide else true
    part.Size = props.Size or Vector3.new(1, 1, 1)
    part.Position = props.Position or Vector3.zero
    part.Color = props.Color or Color3.new(1, 1, 1)
    part.Material = props.Material or Enum.Material.SmoothPlastic
    part.TopSurface = Enum.SurfaceType.Smooth
    part.BottomSurface = Enum.SurfaceType.Smooth
    part.Name = props.Name or "Part"
    part.Parent = props.Parent
    return part
end

------------------------------------------------------------------------
-- Helper: SurfaceGui text
------------------------------------------------------------------------

local function makeSurfaceText(parent: Part, face: Enum.NormalId, text: string, textSize: number, textColor: Color3?)
    local gui = Instance.new("SurfaceGui")
    gui.Face = face
    gui.SizingMode = Enum.SurfaceGuiSizingMode.PixelsPerStud
    gui.PixelsPerStud = 40
    gui.Parent = parent

    local label = Instance.new("TextLabel")
    label.Size = UDim2.new(1, 0, 1, 0)
    label.BackgroundTransparency = 1
    label.TextColor3 = textColor or Color3.new(1, 1, 1)
    label.Text = text
    label.TextScaled = false
    label.TextSize = textSize
    label.Font = Enum.Font.BuilderSansBold
    label.TextWrapped = true
    label.TextXAlignment = Enum.TextXAlignment.Center
    label.TextYAlignment = Enum.TextYAlignment.Center
    label.Parent = gui
end

------------------------------------------------------------------------
-- Build terrain (biome grid)
------------------------------------------------------------------------

function Manager.buildTerrain(): Folder
    local folder = Instance.new("Folder")
    folder.Name = "EcosystemTerrain"
    folder.Parent = workspace

    local worldSize = Config.WorldSize
    local tileSize = Config.BiomeTileSize
    local tilesPerSide = math.floor(worldSize / tileSize)
    local halfWorld = worldSize / 2

    -- Use noise to assign biomes to tiles
    local noiseSeed = math.random(0, 10000)

    for tx = 0, tilesPerSide - 1 do
        for tz = 0, tilesPerSide - 1 do
            local centerX = -halfWorld + tx * tileSize + tileSize / 2
            local centerZ = -halfWorld + tz * tileSize + tileSize / 2

            -- Sample noise to pick biome
            local noiseVal = math.noise(tx * 0.3 + noiseSeed, tz * 0.3 + noiseSeed)
            -- Map noise (-0.5 to 0.5 roughly) to biome index
            local biomeIndex
            if noiseVal < -0.15 then
                biomeIndex = 4 -- Wetland
            elseif noiseVal < 0.05 then
                biomeIndex = 1 -- Forest
            elseif noiseVal < 0.25 then
                biomeIndex = 2 -- Plains
            else
                biomeIndex = 3 -- Desert
            end

            local biome = Config.Biomes[biomeIndex]

            -- Small height variation
            local heightNoise = math.noise(tx * 0.5 + noiseSeed * 2, tz * 0.5 + noiseSeed * 2) * 3

            local tile = makePart({
                Name = "Tile_" .. tx .. "_" .. tz,
                Size = Vector3.new(tileSize, Config.BiomeTileHeight, tileSize),
                Position = Vector3.new(centerX, heightNoise, centerZ),
                Color = biome.color,
                Material = biome.material,
                Parent = folder,
            })

            tile:SetAttribute("Biome", biome.name)
            tile:SetAttribute("BiomeIndex", biomeIndex)
            tile:SetAttribute("PlantDensity", biome.plantDensity)
            tile:SetAttribute("SpeedModifier", biome.speedModifier)
        end
    end

    -- Spawn sign in center
    local sign = makePart({
        Name = "EcosystemSign",
        Size = Vector3.new(16, 4, 0.5),
        Position = Vector3.new(0, 15, 0),
        Color = Color3.fromRGB(40, 40, 45),
        Material = Enum.Material.Slate,
        Parent = folder,
    })
    makeSurfaceText(sign, Enum.NormalId.Front, "ECOSYSTEM SURVIVAL", 50, Color3.fromRGB(200, 220, 255))
    makeSurfaceText(sign, Enum.NormalId.Back, "ECOSYSTEM SURVIVAL", 50, Color3.fromRGB(200, 220, 255))

    -- Spawn location
    local spawn = Instance.new("SpawnLocation")
    spawn.Anchored = true
    spawn.CanCollide = false
    spawn.Transparency = 1
    spawn.Size = Vector3.new(8, 1, 8)
    spawn.Position = Vector3.new(0, Config.SpawnHeight, 0)
    spawn.Parent = folder

    -- Lighting: outdoor natural
    local lighting = game:GetService("Lighting")
    lighting.ClockTime = 14
    lighting.Brightness = 2.5
    lighting.Ambient = Color3.fromRGB(60, 65, 60)
    lighting.OutdoorAmbient = Color3.fromRGB(100, 110, 100)

    local atmosphere = Instance.new("Atmosphere")
    atmosphere.Density = 0.3
    atmosphere.Offset = 0.2
    atmosphere.Color = Color3.fromRGB(180, 200, 180)
    atmosphere.Decay = Color3.fromRGB(150, 160, 140)
    atmosphere.Glare = 0.3
    atmosphere.Haze = 2
    atmosphere.Parent = lighting

    return folder
end

------------------------------------------------------------------------
-- Get random position on terrain
------------------------------------------------------------------------

function Manager.randomWorldPosition(): Vector3
    local half = Config.WorldSize / 2
    local x = math.random() * Config.WorldSize - half
    local z = math.random() * Config.WorldSize - half
    return Vector3.new(x, 3, z)
end

------------------------------------------------------------------------
-- Build a plant NPC
------------------------------------------------------------------------

function Manager.buildPlant(position: Vector3, parent: Folder): (Part, any)
    local id = Manager.generateId()

    local plant = makePart({
        Name = "Plant_" .. id,
        Size = Config.PlantSize,
        Position = position + Vector3.new(0, Config.PlantSize.Y / 2, 0),
        Color = Config.PlantColor,
        Material = Config.PlantMaterial,
        CanCollide = false,
        Parent = parent,
    })

    -- Glow top
    local glow = makePart({
        Name = "Glow",
        Size = Config.PlantSize * 0.5,
        Position = plant.Position + Vector3.new(0, Config.PlantSize.Y * 0.3, 0),
        Color = Config.PlantGlowColor,
        Material = Enum.Material.Neon,
        CanCollide = false,
        Parent = parent,
    })

    -- Weld glow to plant
    local weld = Instance.new("WeldConstraint")
    weld.Part0 = plant
    weld.Part1 = glow
    weld.Parent = plant

    plant:SetAttribute("EntityId", id)
    plant:SetAttribute("EntityType", "plant")

    local data = {
        id = id,
        type = "plant",
        part = plant,
        glowPart = glow,
        energy = 20 + math.random() * 20,
        age = 0,
        mature = false,
        position = position,
    }

    return plant, data
end

------------------------------------------------------------------------
-- Build an NPC creature (herbivore or predator)
------------------------------------------------------------------------

function Manager.buildNPCCreature(species: string, position: Vector3, parent: Folder): (Model, any)
    local id = Manager.generateId()
    local isPredator = (species == "predator")

    local bodySize = if isPredator then Config.NPCPredatorSize else Config.NPCHerbivoreSize
    local bodyColor = if isPredator then Config.NPCPredatorColor else Config.NPCHerbivoreColor

    local model = Instance.new("Model")
    model.Name = (if isPredator then "Predator_" else "Herbivore_") .. id

    -- Body
    local body = makePart({
        Name = "Body",
        Size = bodySize,
        Position = position + Vector3.new(0, bodySize.Y / 2 + 1, 0),
        Color = bodyColor,
        Material = Enum.Material.SmoothPlastic,
        CanCollide = false,
        Parent = model,
    })

    -- Head (smaller part at front)
    local headSize = bodySize * 0.5
    local head = makePart({
        Name = "Head",
        Size = headSize,
        Position = body.Position + Vector3.new(0, bodySize.Y * 0.2, bodySize.Z * 0.4),
        Color = bodyColor,
        Material = Enum.Material.SmoothPlastic,
        CanCollide = false,
        Parent = model,
    })

    local headWeld = Instance.new("WeldConstraint")
    headWeld.Part0 = body
    headWeld.Part1 = head
    headWeld.Parent = body

    -- Eyes (two small white parts)
    for _, side in { -1, 1 } do
        local eye = makePart({
            Name = "Eye",
            Size = Vector3.new(0.4, 0.4, 0.4),
            Position = head.Position + Vector3.new(side * headSize.X * 0.3, headSize.Y * 0.15, headSize.Z * 0.4),
            Color = Color3.new(1, 1, 1),
            Material = Enum.Material.Neon,
            CanCollide = false,
            Parent = model,
        })
        local eyeWeld = Instance.new("WeldConstraint")
        eyeWeld.Part0 = head
        eyeWeld.Part1 = eye
        eyeWeld.Parent = head
    end

    -- Predator: red spikes on back
    if isPredator then
        for i = 1, 3 do
            local spike = makePart({
                Name = "Spike" .. i,
                Size = Vector3.new(0.6, 1.5, 0.6),
                Position = body.Position + Vector3.new(0, bodySize.Y * 0.5, -bodySize.Z * 0.1 + (i - 2) * 1.5),
                Color = Color3.fromRGB(255, 100, 80),
                Material = Enum.Material.Neon,
                CanCollide = false,
                Parent = model,
            })
            local spikeWeld = Instance.new("WeldConstraint")
            spikeWeld.Part0 = body
            spikeWeld.Part1 = spike
            spikeWeld.Parent = body
        end
    end

    model.PrimaryPart = body
    body:SetAttribute("EntityId", id)
    body:SetAttribute("EntityType", species)

    model.Parent = parent

    local specStats = if isPredator then Config.Species.predator else Config.Species.herbivore
    local data = {
        id = id,
        type = species,
        model = model,
        body = body,
        energy = specStats.startEnergy + math.random() * 20,
        maxEnergy = specStats.maxEnergy,
        position = position,
        velocity = Vector3.new((math.random() - 0.5) * 4, 0, (math.random() - 0.5) * 4),
        wanderAngle = math.random() * math.pi * 2,
        huntCooldown = 0,
        age = 0,
    }

    return model, data
end

------------------------------------------------------------------------
-- NPC AI: Herbivore behavior
------------------------------------------------------------------------

function Manager.updateNPCHerbivore(data: any, plants: { any }, predators: { any }, dt: number)
    data.age += 1
    data.energy -= Config.NPC.energyDecayHerbivore

    -- Find nearest plant
    local nearestPlant = nil
    local nearestPlantDist = math.huge
    for _, plant in plants do
        local dist = (plant.position - data.position).Magnitude
        if dist < nearestPlantDist then
            nearestPlantDist = dist
            nearestPlant = plant
        end
    end

    -- Find nearest predator
    local nearestPred = nil
    local nearestPredDist = math.huge
    for _, pred in predators do
        local dist = (pred.position - data.position).Magnitude
        if dist < nearestPredDist then
            nearestPredDist = dist
            nearestPred = pred
        end
    end

    local visionRange = Config.Species.herbivore.visionRange
    local speed = Config.NPC.herbivoreWanderSpeed
    local targetDir = Vector3.new(math.cos(data.wanderAngle), 0, math.sin(data.wanderAngle))

    if nearestPred and nearestPredDist < visionRange then
        -- Flee
        local fleeDir = (data.position - nearestPred.position).Unit
        targetDir = Vector3.new(fleeDir.X, 0, fleeDir.Z)
        speed = Config.NPC.herbivoreFleeSpeed
    elseif nearestPlant and nearestPlantDist < visionRange and data.energy < 70 then
        -- Seek food
        local seekDir = (nearestPlant.position - data.position).Unit
        targetDir = Vector3.new(seekDir.X, 0, seekDir.Z)
        speed = Config.NPC.herbivoreSeekSpeed
    else
        -- Wander
        data.wanderAngle += (math.random() - 0.5) * 0.5
        targetDir = Vector3.new(math.cos(data.wanderAngle), 0, math.sin(data.wanderAngle))
        speed = Config.NPC.herbivoreWanderSpeed * 0.6
    end

    -- Apply movement
    data.velocity = targetDir * speed
    data.position = data.position + data.velocity * dt

    -- Wrap around world
    local half = Config.WorldSize / 2
    if data.position.X > half then data.position = Vector3.new(-half, data.position.Y, data.position.Z) end
    if data.position.X < -half then data.position = Vector3.new(half, data.position.Y, data.position.Z) end
    if data.position.Z > half then data.position = Vector3.new(data.position.X, data.position.Y, -half) end
    if data.position.Z < -half then data.position = Vector3.new(data.position.X, data.position.Y, half) end

    -- Keep on terrain
    data.position = Vector3.new(data.position.X, 3, data.position.Z)

    -- Eat plant if close enough
    local eatTarget = nil
    if nearestPlant and nearestPlantDist < Config.Species.herbivore.eatRange then
        eatTarget = nearestPlant
        data.energy = math.min(data.energy + Config.NPC.plantEnergyValue, data.maxEnergy)
    end

    -- Move model
    if data.model and data.body then
        local lookDir = data.velocity
        if lookDir.Magnitude > 0.1 then
            data.body.CFrame = CFrame.new(data.position + Vector3.new(0, data.body.Size.Y / 2, 0), data.position + Vector3.new(0, data.body.Size.Y / 2, 0) + lookDir)
        else
            data.body.Position = data.position + Vector3.new(0, data.body.Size.Y / 2, 0)
        end
    end

    return eatTarget
end

------------------------------------------------------------------------
-- NPC AI: Predator behavior
------------------------------------------------------------------------

function Manager.updateNPCPredator(data: any, herbivores: { any }, dt: number)
    data.age += 1
    data.energy -= Config.NPC.energyDecayPredator
    if data.huntCooldown > 0 then
        data.huntCooldown -= dt
    end

    -- Find nearest herbivore (NPC or player-represented)
    local nearestPrey = nil
    local nearestPreyDist = math.huge
    for _, herb in herbivores do
        local dist = (herb.position - data.position).Magnitude
        if dist < nearestPreyDist then
            nearestPreyDist = dist
            nearestPrey = herb
        end
    end

    local visionRange = Config.Species.predator.visionRange
    local speed = Config.NPC.predatorWanderSpeed
    local targetDir = Vector3.new(math.cos(data.wanderAngle), 0, math.sin(data.wanderAngle))

    if nearestPrey and nearestPreyDist < visionRange * 1.2 then
        -- Hunt
        local huntDir = (nearestPrey.position - data.position).Unit
        targetDir = Vector3.new(huntDir.X, 0, huntDir.Z)
        speed = Config.NPC.predatorHuntSpeed * (if data.energy < 30 then 1.3 else 1.0)
    else
        -- Wander
        data.wanderAngle += (math.random() - 0.5) * 0.3
        targetDir = Vector3.new(math.cos(data.wanderAngle), 0, math.sin(data.wanderAngle))
    end

    data.velocity = targetDir * speed
    data.position = data.position + data.velocity * dt

    -- Wrap
    local half = Config.WorldSize / 2
    if data.position.X > half then data.position = Vector3.new(-half, data.position.Y, data.position.Z) end
    if data.position.X < -half then data.position = Vector3.new(half, data.position.Y, data.position.Z) end
    if data.position.Z > half then data.position = Vector3.new(data.position.X, data.position.Y, -half) end
    if data.position.Z < -half then data.position = Vector3.new(data.position.X, data.position.Y, half) end

    data.position = Vector3.new(data.position.X, 3, data.position.Z)

    -- Eat prey if close enough and off cooldown
    local eatTarget = nil
    if nearestPrey and nearestPreyDist < Config.Species.predator.eatRange and data.huntCooldown <= 0 then
        eatTarget = nearestPrey
        data.energy = math.min(data.energy + Config.Species.predator.eatGain, data.maxEnergy)
        data.huntCooldown = Config.Species.predator.huntCooldown
    end

    -- Move model
    if data.model and data.body then
        local lookDir = data.velocity
        if lookDir.Magnitude > 0.1 then
            data.body.CFrame = CFrame.new(data.position + Vector3.new(0, data.body.Size.Y / 2, 0), data.position + Vector3.new(0, data.body.Size.Y / 2, 0) + lookDir)
        else
            data.body.Position = data.position + Vector3.new(0, data.body.Size.Y / 2, 0)
        end
    end

    return eatTarget
end

------------------------------------------------------------------------
-- Check NPC reproduction
------------------------------------------------------------------------

function Manager.canReproduce(data: any): boolean
    if data.energy < Config.NPC.npcReproductionThreshold then return false end
    if math.random() > Config.NPC.npcReproductionChance then return false end
    return true
end

------------------------------------------------------------------------
-- Ecosystem health score (0-100)
------------------------------------------------------------------------

function Manager.calculateEcosystemHealth(plantCount: number, herbCount: number, predCount: number): number
    local plantRatio = plantCount / Config.NPC.maxPlants
    local herbRatio = herbCount / Config.NPC.maxHerbivores
    local predRatio = predCount / Config.NPC.maxPredators

    -- Score based on distance from ideal ratios
    local plantScore = 1 - math.abs(plantRatio - Config.HealthMetrics.idealPlantRatio) * 2
    local herbScore = 1 - math.abs(herbRatio - Config.HealthMetrics.idealHerbRatio) * 2
    local predScore = 1 - math.abs(predRatio - Config.HealthMetrics.idealPredRatio) * 2

    -- Bonus for diversity (all three types present)
    local diversityBonus = 0
    if plantCount > 0 and herbCount > 0 and predCount > 0 then
        diversityBonus = 10
    end

    -- Penalty for extinction
    local extinctionPenalty = 0
    if plantCount == 0 then extinctionPenalty += 20 end
    if herbCount == 0 then extinctionPenalty += 20 end
    if predCount == 0 then extinctionPenalty += 15 end

    local raw = (math.max(0, plantScore) * 35 + math.max(0, herbScore) * 35 + math.max(0, predScore) * 30) + diversityBonus - extinctionPenalty
    return math.clamp(math.floor(raw), 0, 100)
end

------------------------------------------------------------------------
-- Ecosystem health label
------------------------------------------------------------------------

function Manager.healthLabel(score: number): string
    if score >= 80 then return "Thriving" end
    if score >= 60 then return "Stable" end
    if score >= 40 then return "Stressed" end
    if score >= 20 then return "Declining" end
    return "Collapsing"
end

return Manager
