--[[
	MusicServer.luau
	Script → ServerScriptService

	Runs the Generative Music Rooms experience.
	- Builds the world on startup
	- Maintains the global beat clock
	- Tracks player positions → room assignments
	- Detects player activity (running, jumping, still)
	- Computes which layers are active per room
	- Broadcasts state to clients every beat
]]

local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ServerStorage = game:GetService("ServerStorage")

local MusicConfig = require(ReplicatedStorage:WaitForChild("MusicConfig"))
local SoundscapeEngine = require(ServerStorage:WaitForChild("SoundscapeEngine"))

------------------------------------------------------------------------
-- RemoteEvents
------------------------------------------------------------------------
local beatEvent = Instance.new("RemoteEvent")
beatEvent.Name = "MusicBeatEvent"
beatEvent.Parent = ReplicatedStorage

local stateEvent = Instance.new("RemoteEvent")
stateEvent.Name = "MusicStateEvent"
stateEvent.Parent = ReplicatedStorage

local activityEvent = Instance.new("RemoteEvent")
activityEvent.Name = "MusicActivityEvent"
activityEvent.Parent = ReplicatedStorage

------------------------------------------------------------------------
-- State
------------------------------------------------------------------------
local beatEpoch = tick()  -- server start time = beat 0
local prevBeat = 0

-- Per-player tracking
-- playerState[player] = {room = roomIndex|nil, speed = n, isJumping = bool, stillTime = n, lastPos = Vector3}
local playerState = {}

-- Per-room state
-- roomState[roomIndex] = {playerCount = n, runners = n, jumpers = n, stillPlayers = n, activeLayers = {}}
local roomState = {}

-- Room folders and centers (populated after world build)
local roomFolders = {}  -- [roomIndex] = folder
local roomCenters = {}  -- [roomIndex] = Vector3

------------------------------------------------------------------------
-- Build world
------------------------------------------------------------------------
local worldFolder = SoundscapeEngine.buildWorld()

-- Collect room data
for _, child in worldFolder:GetChildren() do
	local idxVal = child:FindFirstChild("RoomIndex")
	if idxVal then
		local idx = idxVal.Value
		roomFolders[idx] = child
		roomCenters[idx] = child:FindFirstChild("RoomCenter").Value
		roomState[idx] = {
			playerCount = 0,
			runners = 0,
			jumpers = 0,
			stillPlayers = 0,
			activeLayers = {},
		}
	end
end

------------------------------------------------------------------------
-- Broadcast the beat epoch to new clients so they can sync
------------------------------------------------------------------------
local epochEvent = Instance.new("RemoteEvent")
epochEvent.Name = "MusicEpochEvent"
epochEvent.Parent = ReplicatedStorage

------------------------------------------------------------------------
-- Player room detection
------------------------------------------------------------------------
local function getRoomForPosition(pos: Vector3): number?
	local roomSize = MusicConfig.RoomSize
	local halfX = roomSize.X / 2
	local halfZ = roomSize.Z / 2

	for idx, center in roomCenters do
		if math.abs(pos.X - center.X) <= halfX
			and math.abs(pos.Z - center.Z) <= halfZ
			and pos.Y >= center.Y
			and pos.Y <= center.Y + roomSize.Y then
			return idx
		end
	end

	return nil -- player is in lobby or between rooms
end

------------------------------------------------------------------------
-- Layer activation logic
------------------------------------------------------------------------
local function computeActiveLayers(roomIdx: number)
	local rs = roomState[roomIdx]
	local roomDef = MusicConfig.Rooms[roomIdx]
	local thresholds = roomDef.music.layerThresholds
	local active = {}

	for layerName, threshold in thresholds do
		local isActive = rs.playerCount >= threshold
		-- Activity modifiers
		if layerName == "percussion" and rs.runners > 0 then
			isActive = true  -- running always enables percussion
		end
		if layerName == "melody" and rs.jumpers > 0 then
			isActive = true  -- jumping enables melody
		end
		if layerName == "pad" and rs.stillPlayers > 0 then
			isActive = true  -- stillness enables pad
		end
		active[layerName] = isActive
	end

	rs.activeLayers = active
end

------------------------------------------------------------------------
-- Player setup / teardown
------------------------------------------------------------------------
local function onPlayerAdded(player: Player)
	playerState[player] = {
		room = nil,
		speed = 0,
		isJumping = false,
		stillTime = 0,
		lastPos = Vector3.new(0, 0, 0),
	}

	-- Send epoch so client can sync beat clock
	player.CharacterAdded:Connect(function(character)
		task.wait(0.5) -- let character load
		epochEvent:FireClient(player, beatEpoch)
	end)
end

local function onPlayerRemoving(player: Player)
	local ps = playerState[player]
	if ps and ps.room then
		local rs = roomState[ps.room]
		if rs then
			rs.playerCount = math.max(0, rs.playerCount - 1)
		end
	end
	playerState[player] = nil
end

Players.PlayerAdded:Connect(onPlayerAdded)
Players.PlayerRemoving:Connect(onPlayerRemoving)

-- Handle existing players (for late-loading scripts)
for _, player in Players:GetPlayers() do
	onPlayerAdded(player)
end

------------------------------------------------------------------------
-- Client → Server: jump notification
------------------------------------------------------------------------
activityEvent.OnServerEvent:Connect(function(player, activityType)
	local ps = playerState[player]
	if not ps then return end

	if activityType == "jump" then
		ps.isJumping = true
		-- Reset after a short window
		task.delay(0.5, function()
			if playerState[player] then
				playerState[player].isJumping = false
			end
		end)
	end
end)

------------------------------------------------------------------------
-- Main simulation loop
------------------------------------------------------------------------
RunService.Heartbeat:Connect(function(dt)
	-- Update beat
	local beatNow = SoundscapeEngine.getBeat(120, beatEpoch)  -- use a reference BPM for the global clock; rooms adjust locally
	local isNew = SoundscapeEngine.isNewBeat(beatNow, prevBeat)
	prevBeat = beatNow

	-- Reset per-room activity counters
	for idx in roomState do
		roomState[idx].playerCount = 0
		roomState[idx].runners = 0
		roomState[idx].jumpers = 0
		roomState[idx].stillPlayers = 0
	end

	-- Update each player's state
	for player, ps in playerState do
		local character = player.Character
		if not character then continue end

		local rootPart = character:FindFirstChild("HumanoidRootPart")
		if not rootPart then continue end

		local pos = rootPart.Position
		local speed = (pos - ps.lastPos).Magnitude / math.max(dt, 0.001)
		ps.lastPos = pos
		ps.speed = speed

		-- Stillness tracking
		if speed < MusicConfig.Activity.stillThreshold then
			ps.stillTime = ps.stillTime + dt
		else
			ps.stillTime = 0
		end

		-- Room detection
		local newRoom = getRoomForPosition(pos)
		ps.room = newRoom

		-- Aggregate into room state
		if newRoom and roomState[newRoom] then
			local rs = roomState[newRoom]
			rs.playerCount = rs.playerCount + 1

			if speed >= MusicConfig.Activity.runSpeedThreshold then
				rs.runners = rs.runners + 1
			end
			if ps.isJumping then
				rs.jumpers = rs.jumpers + 1
			end
			if ps.stillTime >= MusicConfig.Activity.stillTimeRequired then
				rs.stillPlayers = rs.stillPlayers + 1
			end
		end
	end

	-- Compute active layers for each room
	for idx in roomState do
		computeActiveLayers(idx)
	end

	-- Broadcast state on every new beat (of the global reference clock)
	if isNew then
		-- Build compact state payload
		local payload = {}
		for idx, rs in roomState do
			payload[idx] = {
				pc = rs.playerCount,
				layers = rs.activeLayers,
				runners = rs.runners,
				jumpers = rs.jumpers,
				still = rs.stillPlayers,
			}
		end

		-- Send to all players: beat number + room states
		local beatNum = math.floor(beatNow)
		for _, player in Players:GetPlayers() do
			stateEvent:FireClient(player, beatNum, payload)
		end

		-- Also fire a beat event for visual sync
		local measure, beatInMeasure = SoundscapeEngine.beatToMeasure(beatNow)
		for _, player in Players:GetPlayers() do
			local ps = playerState[player]
			local roomIdx = ps and ps.room or nil
			beatEvent:FireClient(player, beatNum, measure, beatInMeasure, roomIdx)
		end
	end
end)

print("[MusicServer] Generative Music Rooms started. Beat epoch:", beatEpoch)
