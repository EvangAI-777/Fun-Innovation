--[[
	StoryServer.luau
	Script → ServerScriptService

	Living Story RPG server.
	- Builds the town on startup
	- Loads / saves per-player personality + memories via DataStore
	- Computes world mood from aggregate player personalities
	- Handles dialogue requests: resolves templates, applies trait
	  changes, stores memories
	- Periodically recalculates and broadcasts world state
]]

local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local DataStoreService = game:GetService("DataStoreService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ServerStorage = game:GetService("ServerStorage")

local StoryConfig = require(ReplicatedStorage:WaitForChild("StoryConfig"))
local DialogueManager = require(ServerStorage:WaitForChild("DialogueManager"))

------------------------------------------------------------------------
-- DataStore
------------------------------------------------------------------------
local dataStore = DataStoreService:GetDataStore(StoryConfig.DataStoreKey)

------------------------------------------------------------------------
-- RemoteEvents / RemoteFunctions
------------------------------------------------------------------------
local dialogueRequest = Instance.new("RemoteFunction")
dialogueRequest.Name = "DialogueRequest"
dialogueRequest.Parent = ReplicatedStorage

local choiceEvent = Instance.new("RemoteEvent")
choiceEvent.Name = "DialogueChoiceEvent"
choiceEvent.Parent = ReplicatedStorage

local worldStateEvent = Instance.new("RemoteEvent")
worldStateEvent.Name = "WorldStateEvent"
worldStateEvent.Parent = ReplicatedStorage

local personalityEvent = Instance.new("RemoteEvent")
personalityEvent.Name = "PersonalityEvent"
personalityEvent.Parent = ReplicatedStorage

------------------------------------------------------------------------
-- Player data
------------------------------------------------------------------------
-- playerData[player] = {personality = {}, memories = {}, visitedNPCs = {}, choiceCount = 0, name = ""}
local playerData = {}

local function loadPlayerData(player: Player): table
	local data = {
		personality = {},
		memories = {},
		visitedNPCs = {},
		choiceCount = 0,
		name = player.Name,
	}

	-- Copy defaults
	for trait, val in StoryConfig.DefaultPersonality do
		data.personality[trait] = val
	end

	-- Try loading from DataStore
	local success, saved = pcall(function()
		return dataStore:GetAsync("player_" .. player.UserId)
	end)

	if success and saved then
		if saved.personality then
			for trait, val in saved.personality do
				data.personality[trait] = val
			end
		end
		if saved.memories then
			data.memories = saved.memories
		end
		if saved.visitedNPCs then
			data.visitedNPCs = saved.visitedNPCs
		end
		if saved.choiceCount then
			data.choiceCount = saved.choiceCount
		end
		if saved.name then
			data.name = saved.name
		end
	end

	return data
end

local function savePlayerData(player: Player)
	local data = playerData[player]
	if not data then return end

	local toSave = {
		personality = data.personality,
		memories = data.memories,
		visitedNPCs = data.visitedNPCs,
		choiceCount = data.choiceCount,
		name = data.name,
	}

	pcall(function()
		dataStore:SetAsync("player_" .. player.UserId, toSave)
	end)
end

------------------------------------------------------------------------
-- World mood computation
------------------------------------------------------------------------
local currentMood = StoryConfig.DefaultMood

local function computeWorldMood()
	-- Aggregate all online players' traits
	local traitSums = {}
	for _, trait in StoryConfig.Traits do
		traitSums[trait] = 0
	end

	local playerCount = 0
	for _, data in playerData do
		playerCount = playerCount + 1
		for trait, val in data.personality do
			traitSums[trait] = (traitSums[trait] or 0) + val
		end
	end

	if playerCount == 0 then
		currentMood = StoryConfig.DefaultMood
		return
	end

	-- Average each trait
	local traitAvgs = {}
	for trait, sum in traitSums do
		traitAvgs[trait] = sum / playerCount
	end

	-- Find the dominant collective trait
	local bestTrait = nil
	local bestAvg = 0
	for trait, avg in traitAvgs do
		if avg > bestAvg then
			bestTrait = trait
			bestAvg = avg
		end
	end

	-- Check if any mood threshold is met
	for _, moodDef in StoryConfig.WorldMoods do
		if moodDef.dominantTrait == bestTrait and bestAvg >= moodDef.threshold then
			currentMood = moodDef
			DialogueManager.applyWorldMood(moodDef)
			return
		end
	end

	-- No mood threshold met — use default
	currentMood = StoryConfig.DefaultMood
	DialogueManager.applyWorldMood(StoryConfig.DefaultMood)
end

------------------------------------------------------------------------
-- Dialogue handling
------------------------------------------------------------------------

-- Client requests a dialogue node
dialogueRequest.OnServerInvoke = function(player: Player, npcId: string, nodeId: string)
	local data = playerData[player]
	if not data then return nil end

	-- Find NPC definition
	local npcDef = nil
	for _, def in StoryConfig.NPCs do
		if def.id == npcId then
			npcDef = def
			break
		end
	end
	if not npcDef then return nil end

	-- Determine if player has visited this NPC before
	local hasVisited = false
	for _, visited in data.visitedNPCs do
		if visited == npcId then
			hasVisited = true
			break
		end
	end

	-- Get the dialogue node
	local node = DialogueManager.getNode(npcDef.dialogueKey, nodeId, hasVisited)
	if not node then return nil end

	-- Build player data for template resolution
	local templateData = {
		name = data.name,
		dominantTrait = DialogueManager.getDominantTrait(data.personality),
		memories = data.memories,
	}

	-- Resolve text templates
	local resolvedText = DialogueManager.resolveNodeText(node, templateData)

	-- Build choices (strip trait info for client)
	local clientChoices = {}
	if node.choices then
		for i, choice in node.choices do
			table.insert(clientChoices, {
				index = i,
				text = choice.text,
			})
		end
	end

	return {
		text = resolvedText,
		choices = clientChoices,
		isEnd = node.isEnd or false,
		npcName = npcDef.name,
		npcDescription = npcDef.description,
	}
end

-- Client makes a dialogue choice
choiceEvent.OnServerEvent:Connect(function(player: Player, npcId: string, nodeId: string, choiceIndex: number)
	local data = playerData[player]
	if not data then return end

	-- Find NPC definition
	local npcDef = nil
	for _, def in StoryConfig.NPCs do
		if def.id == npcId then
			npcDef = def
			break
		end
	end
	if not npcDef then return end

	-- Get the node and choice
	local hasVisited = false
	for _, visited in data.visitedNPCs do
		if visited == npcId then
			hasVisited = true
			break
		end
	end

	local node = DialogueManager.getNode(npcDef.dialogueKey, nodeId, hasVisited)
	if not node or not node.choices then return end

	local choice = node.choices[choiceIndex]
	if not choice then return end

	-- Apply trait changes from the choice
	if choice.traits then
		for trait, amount in choice.traits do
			data.personality[trait] = (data.personality[trait] or 0) + amount
		end
	end
	data.choiceCount = data.choiceCount + 1

	-- Store memory from the choice
	if choice.memory and #data.memories < StoryConfig.MaxMemories then
		table.insert(data.memories, choice.memory)
	end

	-- Get the next node to check for node-level traits and memory
	local nextNode = nil
	if choice.nextNode then
		local tree = StoryConfig.DialogueTrees[npcDef.dialogueKey]
		if tree then
			nextNode = tree[choice.nextNode]
		end
	end

	-- Apply traits from the destination node itself
	if nextNode and nextNode.traits then
		for trait, amount in nextNode.traits do
			data.personality[trait] = (data.personality[trait] or 0) + amount
		end
	end

	-- Store memory from the destination node
	if nextNode and nextNode.memory and #data.memories < StoryConfig.MaxMemories then
		table.insert(data.memories, nextNode.memory)
	end

	-- Mark NPC as visited
	if not hasVisited then
		table.insert(data.visitedNPCs, npcId)
	end

	-- Send updated personality to client
	personalityEvent:FireClient(player, data.personality, data.choiceCount, data.memories)
end)

------------------------------------------------------------------------
-- Build world
------------------------------------------------------------------------
local townFolder = DialogueManager.buildTown()

------------------------------------------------------------------------
-- Player lifecycle
------------------------------------------------------------------------
local function onPlayerAdded(player: Player)
	local data = loadPlayerData(player)
	playerData[player] = data

	-- Send initial personality state to client
	player.CharacterAdded:Connect(function()
		task.wait(1)
		if playerData[player] then
			personalityEvent:FireClient(player, data.personality, data.choiceCount, data.memories)
			worldStateEvent:FireClient(player, currentMood.name or "Neutral", currentMood.npcGreeting or "")
		end
	end)

	-- Recompute world mood with new player
	computeWorldMood()
end

local function onPlayerRemoving(player: Player)
	savePlayerData(player)
	playerData[player] = nil
	-- Recompute world mood after player leaves
	task.defer(computeWorldMood)
end

Players.PlayerAdded:Connect(onPlayerAdded)
Players.PlayerRemoving:Connect(onPlayerRemoving)

-- Handle players already in the game
for _, player in Players:GetPlayers() do
	task.spawn(onPlayerAdded, player)
end

-- Save all on shutdown
game:BindToClose(function()
	for player in playerData do
		savePlayerData(player)
	end
end)

------------------------------------------------------------------------
-- Auto-save loop
------------------------------------------------------------------------
task.spawn(function()
	while true do
		task.wait(StoryConfig.AutoSaveInterval)
		for player in playerData do
			task.spawn(savePlayerData, player)
		end
	end
end)

------------------------------------------------------------------------
-- World state update loop
------------------------------------------------------------------------
task.spawn(function()
	while true do
		task.wait(StoryConfig.WorldStateUpdateRate)
		computeWorldMood()

		-- Broadcast current mood to all clients
		for _, player in Players:GetPlayers() do
			worldStateEvent:FireClient(player, currentMood.name or "Neutral", currentMood.npcGreeting or "")
		end
	end
end)

print("[StoryServer] Living Story RPG started. Town built. DataStore ready.")
