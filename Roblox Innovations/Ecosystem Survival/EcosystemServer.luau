--[[
    EcosystemServer.luau
    Script -- place in ServerScriptService

    Server-side simulation for Ecosystem Survival.
    Runs the NPC AI loop, manages player species/energy,
    handles eating and reproduction, tracks population,
    and maintains the ecosystem health leaderboard.
]]

local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ServerStorage = game:GetService("ServerStorage")

local Config = require(ReplicatedStorage:WaitForChild("EcosystemConfig"))
local Manager = require(ServerStorage:WaitForChild("CreatureManager"))

------------------------------------------------------------------------
-- Remote events
------------------------------------------------------------------------

local remotes = Instance.new("Folder")
remotes.Name = "EcosystemRemotes"
remotes.Parent = ReplicatedStorage

local chooseSpeciesEvent = Instance.new("RemoteEvent")
chooseSpeciesEvent.Name = "ChooseSpecies"
chooseSpeciesEvent.Parent = remotes

local playerStatsEvent = Instance.new("RemoteEvent")
playerStatsEvent.Name = "PlayerStats"
playerStatsEvent.Parent = remotes

local eatActionEvent = Instance.new("RemoteEvent")
eatActionEvent.Name = "EatAction"
eatActionEvent.Parent = remotes

local reproduceActionEvent = Instance.new("RemoteEvent")
reproduceActionEvent.Name = "ReproduceAction"
reproduceActionEvent.Parent = remotes

local sprintEvent = Instance.new("RemoteEvent")
sprintEvent.Name = "SprintState"
sprintEvent.Parent = remotes

local populationEvent = Instance.new("RemoteEvent")
populationEvent.Name = "PopulationUpdate"
populationEvent.Parent = remotes

local eventLogEvent = Instance.new("RemoteEvent")
eventLogEvent.Name = "EventLog"
eventLogEvent.Parent = remotes

local playerDiedEvent = Instance.new("RemoteEvent")
playerDiedEvent.Name = "PlayerDied"
playerDiedEvent.Parent = remotes

------------------------------------------------------------------------
-- World containers
------------------------------------------------------------------------

local npcFolder = Instance.new("Folder")
npcFolder.Name = "EcosystemNPCs"
npcFolder.Parent = workspace

------------------------------------------------------------------------
-- NPC state tables
------------------------------------------------------------------------

local plantData: { [string]: any } = {}      -- id -> plant data
local herbivoreData: { [string]: any } = {}   -- id -> NPC herbivore data
local predatorData: { [string]: any } = {}    -- id -> NPC predator data

------------------------------------------------------------------------
-- Player state
------------------------------------------------------------------------

local playerState: { [number]: {
    species: string?,
    energy: number,
    maxEnergy: number,
    sprinting: boolean,
    huntCooldown: number,
    alive: boolean,
} } = {}

------------------------------------------------------------------------
-- Build terrain
------------------------------------------------------------------------

Manager.buildTerrain()

------------------------------------------------------------------------
-- Spawn initial NPCs
------------------------------------------------------------------------

local function spawnInitialNPCs()
    -- Plants
    for _ = 1, Config.NPC.plantCount do
        local pos = Manager.randomWorldPosition()
        local _, data = Manager.buildPlant(pos, npcFolder)
        plantData[data.id] = data
    end

    -- NPC Herbivores
    for _ = 1, Config.NPC.herbivoreCount do
        local pos = Manager.randomWorldPosition()
        local _, data = Manager.buildNPCCreature("herbivore", pos, npcFolder)
        herbivoreData[data.id] = data
    end

    -- NPC Predators
    for _ = 1, Config.NPC.predatorCount do
        local pos = Manager.randomWorldPosition()
        local _, data = Manager.buildNPCCreature("predator", pos, npcFolder)
        predatorData[data.id] = data
    end
end

spawnInitialNPCs()

------------------------------------------------------------------------
-- Helper: count table entries
------------------------------------------------------------------------

local function countTable(t): number
    local n = 0
    for _ in t do n += 1 end
    return n
end

------------------------------------------------------------------------
-- Helper: collect values as array
------------------------------------------------------------------------

local function tableValues(t): { any }
    local arr = {}
    for _, v in t do
        table.insert(arr, v)
    end
    return arr
end

------------------------------------------------------------------------
-- Helper: get all herbivore positions (NPCs + players)
------------------------------------------------------------------------

local function getAllHerbivorePositions(): { any }
    local all = {}
    for _, data in herbivoreData do
        table.insert(all, data)
    end
    -- Add player herbivores
    for userId, state in playerState do
        if state.species == "herbivore" and state.alive then
            local player = Players:GetPlayerByUserId(userId)
            if player and player.Character then
                local hrp = player.Character:FindFirstChild("HumanoidRootPart")
                if hrp then
                    table.insert(all, {
                        id = "player_" .. userId,
                        type = "herbivore",
                        position = hrp.Position,
                        isPlayer = true,
                        userId = userId,
                    })
                end
            end
        end
    end
    return all
end

local function getAllPredatorPositions(): { any }
    local all = {}
    for _, data in predatorData do
        table.insert(all, data)
    end
    for userId, state in playerState do
        if state.species == "predator" and state.alive then
            local player = Players:GetPlayerByUserId(userId)
            if player and player.Character then
                local hrp = player.Character:FindFirstChild("HumanoidRootPart")
                if hrp then
                    table.insert(all, {
                        id = "player_" .. userId,
                        type = "predator",
                        position = hrp.Position,
                        isPlayer = true,
                        userId = userId,
                    })
                end
            end
        end
    end
    return all
end

------------------------------------------------------------------------
-- Remove an NPC entity
------------------------------------------------------------------------

local function removeEntity(data: any)
    if data.type == "plant" then
        if data.part then data.part:Destroy() end
        if data.glowPart then data.glowPart:Destroy() end
        plantData[data.id] = nil
    elseif data.type == "herbivore" then
        if data.model then data.model:Destroy() end
        herbivoreData[data.id] = nil
    elseif data.type == "predator" then
        if data.model then data.model:Destroy() end
        predatorData[data.id] = nil
    end
end

------------------------------------------------------------------------
-- Simulation: NPC AI tick
------------------------------------------------------------------------

local simAccum = 0
local plantAccum = 0
local popAccum = 0

RunService.Heartbeat:Connect(function(dt)
    simAccum += dt
    plantAccum += dt
    popAccum += dt

    -- NPC AI tick
    if simAccum >= Config.SimTickRate then
        simAccum = 0
        local tickDt = Config.SimTickRate

        local allPlants = tableValues(plantData)
        local allPredators = getAllPredatorPositions()
        local allHerbivores = getAllHerbivorePositions()

        -- Update NPC herbivores
        local deadPlants = {}
        local herbsToRemove = {}

        for id, data in herbivoreData do
            local eatenPlant = Manager.updateNPCHerbivore(data, allPlants, allPredators, tickDt)
            if eatenPlant and not eatenPlant.isPlayer then
                deadPlants[eatenPlant.id] = true
            end
            if data.energy <= 0 then
                table.insert(herbsToRemove, id)
            end
        end

        -- Update NPC predators
        local deadHerbs = {}
        local predsToRemove = {}

        for id, data in predatorData do
            local eatenHerb = Manager.updateNPCPredator(data, allHerbivores, tickDt)
            if eatenHerb and not eatenHerb.isPlayer then
                deadHerbs[eatenHerb.id] = true
            end
            if data.energy <= 0 then
                table.insert(predsToRemove, id)
            end
        end

        -- Remove dead entities
        for plantId in deadPlants do
            if plantData[plantId] then
                removeEntity(plantData[plantId])
            end
        end
        for _, herbId in herbsToRemove do
            if herbivoreData[herbId] then
                removeEntity(herbivoreData[herbId])
            end
        end
        for _, herbId in deadHerbs do
            if herbivoreData[herbId] then
                removeEntity(herbivoreData[herbId])
            end
        end
        for _, predId in predsToRemove do
            if predatorData[predId] then
                removeEntity(predatorData[predId])
            end
        end

        -- NPC reproduction
        local newHerbs = {}
        for _, data in herbivoreData do
            if Manager.canReproduce(data) and countTable(herbivoreData) + #newHerbs < Config.NPC.maxHerbivores then
                data.energy -= Config.NPC.npcReproductionCost
                local offset = Vector3.new((math.random() - 0.5) * 20, 0, (math.random() - 0.5) * 20)
                table.insert(newHerbs, data.position + offset)
            end
        end
        for _, pos in newHerbs do
            local _, newData = Manager.buildNPCCreature("herbivore", pos, npcFolder)
            herbivoreData[newData.id] = newData
        end

        local newPreds = {}
        for _, data in predatorData do
            if Manager.canReproduce(data) and countTable(predatorData) + #newPreds < Config.NPC.maxPredators then
                data.energy -= Config.NPC.npcReproductionCost
                local offset = Vector3.new((math.random() - 0.5) * 20, 0, (math.random() - 0.5) * 20)
                table.insert(newPreds, data.position + offset)
            end
        end
        for _, pos in newPreds do
            local _, newData = Manager.buildNPCCreature("predator", pos, npcFolder)
            predatorData[newData.id] = newData
        end
    end

    -- Plant growth tick
    if plantAccum >= Config.PlantTickRate then
        plantAccum = 0

        -- Age plants
        for _, data in plantData do
            data.age += 1
            data.energy += 0.1

            -- Grow visually
            if data.age > Config.NPC.plantMaturityAge and not data.mature then
                data.mature = true
                if data.part then
                    data.part.Size = Config.MaturePlantSize
                end
            end
        end

        -- Plant reproduction
        local plantCount = countTable(plantData)
        if plantCount < Config.NPC.maxPlants then
            local newPlants = {}
            for _, data in plantData do
                if data.mature and math.random() < Config.NPC.plantGrowthRate then
                    local angle = math.random() * math.pi * 2
                    local dist = 15 + math.random() * 25
                    local newPos = data.position + Vector3.new(math.cos(angle) * dist, 0, math.sin(angle) * dist)
                    -- Clamp to world
                    local half = Config.WorldSize / 2
                    newPos = Vector3.new(
                        math.clamp(newPos.X, -half, half),
                        3,
                        math.clamp(newPos.Z, -half, half)
                    )
                    table.insert(newPlants, newPos)
                    if plantCount + #newPlants >= Config.NPC.maxPlants then break end
                end
            end
            for _, pos in newPlants do
                local _, newData = Manager.buildPlant(pos, npcFolder)
                plantData[newData.id] = newData
            end
        end

        -- Emergency seeding
        if countTable(plantData) < Config.EmergencyPlantThreshold then
            for _ = 1, Config.EmergencyPlantSpawn do
                local pos = Manager.randomWorldPosition()
                local _, newData = Manager.buildPlant(pos, npcFolder)
                plantData[newData.id] = newData
            end
            eventLogEvent:FireAllClients("Emergency plant seeding triggered!")
        end
    end

    -- Player energy decay
    for userId, state in playerState do
        if state.species and state.alive then
            local specData = Config.Species[state.species]
            if specData then
                local decay = specData.energyDecayRate * dt
                if state.sprinting then
                    decay += specData.sprintEnergyDrain * dt
                end
                state.energy -= decay
                if state.huntCooldown > 0 then
                    state.huntCooldown -= dt
                end

                -- Death check
                if state.energy <= 0 then
                    state.energy = 0
                    state.alive = false
                    local player = Players:GetPlayerByUserId(userId)
                    if player then
                        playerDiedEvent:FireClient(player)
                        eventLogEvent:FireAllClients(player.Name .. " (" .. state.species .. ") ran out of energy!")

                        -- Respawn after delay
                        task.delay(Config.RespawnDelay, function()
                            if playerState[userId] then
                                playerState[userId].energy = specData.startEnergy
                                playerState[userId].alive = true
                                playerState[userId].huntCooldown = 0
                                -- Teleport to random position
                                if player.Character then
                                    local hrp = player.Character:FindFirstChild("HumanoidRootPart")
                                    if hrp then
                                        local pos = Manager.randomWorldPosition()
                                        hrp.CFrame = CFrame.new(pos + Vector3.new(0, Config.SpawnHeight, 0))
                                    end
                                end
                            end
                        end)
                    end
                end

                -- Send stats to player
                local player = Players:GetPlayerByUserId(userId)
                if player then
                    playerStatsEvent:FireClient(player, state.energy, state.maxEnergy, state.huntCooldown, state.alive)
                end
            end
        end
    end

    -- Population broadcast
    if popAccum >= Config.PopulationCheckRate then
        popAccum = 0

        local pCount = countTable(plantData)
        local hCount = countTable(herbivoreData)
        local prCount = countTable(predatorData)

        -- Count players by species
        local playerHerbs = 0
        local playerPreds = 0
        for _, state in playerState do
            if state.species == "herbivore" and state.alive then playerHerbs += 1 end
            if state.species == "predator" and state.alive then playerPreds += 1 end
        end

        local health = Manager.calculateEcosystemHealth(pCount, hCount + playerHerbs, prCount + playerPreds)
        local healthLabel = Manager.healthLabel(health)

        populationEvent:FireAllClients(pCount, hCount + playerHerbs, prCount + playerPreds, health, healthLabel)

        -- Log significant events
        if hCount == 0 and prCount > 0 then
            eventLogEvent:FireAllClients("NPC herbivores extinct! Predators starving...")
        elseif prCount == 0 and hCount > 0 then
            eventLogEvent:FireAllClients("NPC predators extinct! Herbivore boom incoming...")
        end
    end
end)

------------------------------------------------------------------------
-- Remote: Choose species
------------------------------------------------------------------------

chooseSpeciesEvent.OnServerEvent:Connect(function(player, species)
    if type(species) ~= "string" then return end
    if species ~= "herbivore" and species ~= "predator" then return end

    local specData = Config.Species[species]
    if not specData then return end

    playerState[player.UserId] = {
        species = species,
        energy = specData.startEnergy,
        maxEnergy = specData.maxEnergy,
        sprinting = false,
        huntCooldown = 0,
        alive = true,
    }

    -- Set player character color to match species
    if player.Character then
        for _, part in player.Character:GetDescendants() do
            if part:IsA("BasePart") and part.Name ~= "HumanoidRootPart" then
                part.Color = specData.color
            end
        end

        -- Set walk speed
        local humanoid = player.Character:FindFirstChildOfClass("Humanoid")
        if humanoid then
            humanoid.WalkSpeed = specData.baseSpeed
        end
    end

    eventLogEvent:FireAllClients(player.Name .. " joined as " .. specData.name)
end)

------------------------------------------------------------------------
-- Remote: Sprint state
------------------------------------------------------------------------

sprintEvent.OnServerEvent:Connect(function(player, isSprinting)
    local state = playerState[player.UserId]
    if not state or not state.species or not state.alive then return end

    state.sprinting = (isSprinting == true)

    local specData = Config.Species[state.species]
    if player.Character then
        local humanoid = player.Character:FindFirstChildOfClass("Humanoid")
        if humanoid then
            if state.sprinting then
                humanoid.WalkSpeed = specData.baseSpeed * specData.sprintMultiplier
            else
                humanoid.WalkSpeed = specData.baseSpeed
            end
        end
    end
end)

------------------------------------------------------------------------
-- Remote: Eat action
------------------------------------------------------------------------

eatActionEvent.OnServerEvent:Connect(function(player)
    local state = playerState[player.UserId]
    if not state or not state.species or not state.alive then return end

    local character = player.Character
    if not character then return end
    local hrp = character:FindFirstChild("HumanoidRootPart")
    if not hrp then return end

    local playerPos = hrp.Position
    local specData = Config.Species[state.species]

    if state.species == "herbivore" then
        -- Find nearest plant within eat range
        local nearestId = nil
        local nearestDist = math.huge
        for id, data in plantData do
            local dist = (data.position - playerPos).Magnitude
            if dist < nearestDist then
                nearestDist = dist
                nearestId = id
            end
        end

        if nearestId and nearestDist < specData.eatRange then
            state.energy = math.min(state.energy + specData.eatGain, state.maxEnergy)
            removeEntity(plantData[nearestId])
        end

    elseif state.species == "predator" then
        if state.huntCooldown > 0 then return end

        -- Find nearest NPC herbivore within eat range
        local nearestId = nil
        local nearestDist = math.huge
        for id, data in herbivoreData do
            local dist = (data.position - playerPos).Magnitude
            if dist < nearestDist then
                nearestDist = dist
                nearestId = id
            end
        end

        if nearestId and nearestDist < specData.eatRange then
            state.energy = math.min(state.energy + specData.eatGain, state.maxEnergy)
            state.huntCooldown = specData.huntCooldown
            removeEntity(herbivoreData[nearestId])
            eventLogEvent:FireAllClients(player.Name .. " caught a herbivore!")
        end
    end
end)

------------------------------------------------------------------------
-- Remote: Reproduce action
------------------------------------------------------------------------

reproduceActionEvent.OnServerEvent:Connect(function(player)
    local state = playerState[player.UserId]
    if not state or not state.species or not state.alive then return end

    local specData = Config.Species[state.species]
    if state.energy < specData.reproductionThreshold then return end

    local character = player.Character
    if not character then return end
    local hrp = character:FindFirstChild("HumanoidRootPart")
    if not hrp then return end

    local offset = Vector3.new((math.random() - 0.5) * Config.ReproduceNPCSpawnOffset * 2, 0, (math.random() - 0.5) * Config.ReproduceNPCSpawnOffset * 2)
    local spawnPos = hrp.Position + offset
    spawnPos = Vector3.new(spawnPos.X, 3, spawnPos.Z)

    state.energy -= specData.reproductionCost

    if state.species == "herbivore" then
        if countTable(herbivoreData) < Config.NPC.maxHerbivores then
            local _, newData = Manager.buildNPCCreature("herbivore", spawnPos, npcFolder)
            herbivoreData[newData.id] = newData
            eventLogEvent:FireAllClients(player.Name .. " spawned a new herbivore!")
        end
    elseif state.species == "predator" then
        if countTable(predatorData) < Config.NPC.maxPredators then
            local _, newData = Manager.buildNPCCreature("predator", spawnPos, npcFolder)
            predatorData[newData.id] = newData
            eventLogEvent:FireAllClients(player.Name .. " spawned a new predator!")
        end
    end
end)

------------------------------------------------------------------------
-- Player lifecycle
------------------------------------------------------------------------

local function onPlayerAdded(player: Player)
    playerState[player.UserId] = {
        species = nil,
        energy = 0,
        maxEnergy = 100,
        sprinting = false,
        huntCooldown = 0,
        alive = false,
    }

    -- Re-color character when it loads
    player.CharacterAdded:Connect(function(character)
        local state = playerState[player.UserId]
        if state and state.species then
            task.wait(0.5)
            local specData = Config.Species[state.species]
            for _, part in character:GetDescendants() do
                if part:IsA("BasePart") and part.Name ~= "HumanoidRootPart" then
                    part.Color = specData.color
                end
            end
            local humanoid = character:FindFirstChildOfClass("Humanoid")
            if humanoid then
                humanoid.WalkSpeed = specData.baseSpeed
            end
        end
    end)
end

local function onPlayerRemoving(player: Player)
    playerState[player.UserId] = nil
end

Players.PlayerAdded:Connect(onPlayerAdded)
Players.PlayerRemoving:Connect(onPlayerRemoving)

for _, player in Players:GetPlayers() do
    task.spawn(onPlayerAdded, player)
end

print("[Ecosystem] Server initialized")
