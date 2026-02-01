--[[
    EcosystemConfig.luau
    ModuleScript -- place in ReplicatedStorage

    Shared configuration for the Ecosystem Survival experience.
    Species stats, NPC caps, biome definitions, energy settings,
    terrain layout, and leaderboard parameters.
]]

local Config = {}

------------------------------------------------------------------------
-- World dimensions
------------------------------------------------------------------------

Config.WorldSize = 600         -- square terrain, studs per side
Config.WorldHeight = 2         -- base terrain thickness

------------------------------------------------------------------------
-- Biomes (flat colored zones -- no Terrain service needed)
------------------------------------------------------------------------

Config.Biomes = {
    {
        name = "Forest",
        color = Color3.fromRGB(45, 100, 50),
        material = Enum.Material.Grass,
        plantDensity = 1.0,     -- multiplier for plant spawn chance
        speedModifier = 0.9,    -- movement multiplier in this biome
    },
    {
        name = "Plains",
        color = Color3.fromRGB(120, 140, 60),
        material = Enum.Material.Grass,
        plantDensity = 0.6,
        speedModifier = 1.0,
    },
    {
        name = "Desert",
        color = Color3.fromRGB(190, 170, 120),
        material = Enum.Material.Sand,
        plantDensity = 0.15,
        speedModifier = 1.0,
    },
    {
        name = "Wetland",
        color = Color3.fromRGB(60, 110, 90),
        material = Enum.Material.Mud,
        plantDensity = 0.7,
        speedModifier = 0.7,    -- slower in mud
    },
}

-- Biome grid: world is divided into a grid of biome tiles
Config.BiomeTileSize = 100     -- each biome tile is 100x100 studs
Config.BiomeTileHeight = 2

------------------------------------------------------------------------
-- Species definitions
------------------------------------------------------------------------

Config.Species = {
    herbivore = {
        name = "Herbivore",
        color = Color3.fromRGB(88, 166, 255),    -- blue
        accentColor = Color3.fromRGB(130, 200, 255),
        baseSpeed = 24,
        sprintMultiplier = 1.6,
        startEnergy = 60,
        maxEnergy = 100,
        energyDecayRate = 0.3,       -- per second
        sprintEnergyDrain = 1.2,     -- additional per second while sprinting
        eatRange = 12,
        eatGain = 25,                -- energy from eating a plant
        reproductionThreshold = 80,
        reproductionCost = 35,
        visionRange = 80,
        bodySize = Vector3.new(3, 3, 5),
    },
    predator = {
        name = "Predator",
        color = Color3.fromRGB(248, 81, 73),     -- red
        accentColor = Color3.fromRGB(255, 140, 120),
        baseSpeed = 20,
        sprintMultiplier = 1.8,
        startEnergy = 70,
        maxEnergy = 120,
        energyDecayRate = 0.4,
        sprintEnergyDrain = 1.5,
        eatRange = 14,
        eatGain = 45,                -- energy from eating a herbivore
        huntCooldown = 5,            -- seconds after a successful hunt
        reproductionThreshold = 95,
        reproductionCost = 45,
        visionRange = 100,
        bodySize = Vector3.new(4, 3.5, 6),
    },
}

------------------------------------------------------------------------
-- NPC entities
------------------------------------------------------------------------

Config.NPC = {
    plantCount = 120,            -- initial plant NPCs
    herbivoreCount = 20,         -- initial NPC herbivores
    predatorCount = 6,           -- initial NPC predators

    maxPlants = 250,
    maxHerbivores = 60,
    maxPredators = 25,

    plantGrowthRate = 0.015,     -- chance per tick a mature plant spawns a new one
    plantMaturityAge = 80,       -- ticks before a plant can reproduce
    plantEnergyValue = 25,

    herbivoreWanderSpeed = 10,
    herbivoreFleeSpeed = 18,
    herbivoreSeekSpeed = 14,

    predatorWanderSpeed = 8,
    predatorHuntSpeed = 22,

    npcReproductionThreshold = 75,
    npcReproductionCost = 30,
    npcReproductionChance = 0.01,

    energyDecayHerbivore = 0.2,
    energyDecayPredator = 0.25,
}

------------------------------------------------------------------------
-- Plants (visual)
------------------------------------------------------------------------

Config.PlantSize = Vector3.new(2, 3, 2)
Config.PlantColor = Color3.fromRGB(63, 185, 80)
Config.PlantMaterial = Enum.Material.Grass
Config.PlantGlowColor = Color3.fromRGB(100, 220, 100)

Config.MaturePlantSize = Vector3.new(3, 5, 3)

------------------------------------------------------------------------
-- NPC creature visuals
------------------------------------------------------------------------

Config.NPCHerbivoreSize = Vector3.new(2.5, 2.5, 4)
Config.NPCHerbivoreColor = Color3.fromRGB(70, 140, 220)

Config.NPCPredatorSize = Vector3.new(3.5, 3, 5)
Config.NPCPredatorColor = Color3.fromRGB(220, 70, 60)

------------------------------------------------------------------------
-- Simulation tick
------------------------------------------------------------------------

Config.SimTickRate = 0.5        -- seconds between NPC AI ticks
Config.PlantTickRate = 2.0      -- seconds between plant growth ticks
Config.PopulationCheckRate = 10  -- seconds between population logging

------------------------------------------------------------------------
-- Ecosystem health leaderboard
------------------------------------------------------------------------

Config.HealthMetrics = {
    idealPlantRatio = 0.5,       -- plants / maxPlants
    idealHerbRatio = 0.4,        -- herbivores / maxHerbivores
    idealPredRatio = 0.25,       -- predators / maxPredators
}

------------------------------------------------------------------------
-- Emergency seeding
------------------------------------------------------------------------

Config.EmergencyPlantThreshold = 10   -- if plants drop below this, seed more
Config.EmergencyPlantSpawn = 20       -- how many to spawn in emergency

------------------------------------------------------------------------
-- Player respawn
------------------------------------------------------------------------

Config.RespawnDelay = 5              -- seconds before respawn after death
Config.SpawnHeight = 10              -- Y offset for spawning above terrain

------------------------------------------------------------------------
-- Reproduction (player)
------------------------------------------------------------------------

Config.ReproduceNPCSpawnOffset = 15  -- how far from player the NPC offspring spawns

return Config
