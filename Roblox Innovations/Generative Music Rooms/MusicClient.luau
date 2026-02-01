--[[
	MusicClient.luau
	LocalScript → StarterPlayerScripts

	Generative Music Rooms client.
	- Receives beat + state events from server
	- Manages per-room Sound objects and SoundGroups with crossfade
	- Drives visual beat pulses (wall neon, floor tile ripples, light flashes)
	- Detects local player activity and reports jumps to server
	- Renders the mood/room HUD
]]

local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local UserInputService = game:GetService("UserInputService")
local SoundService = game:GetService("SoundService")
local TweenService = game:GetService("TweenService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local MusicConfig = require(ReplicatedStorage:WaitForChild("MusicConfig"))

local player = Players.LocalPlayer
local playerGui = player:WaitForChild("PlayerGui")

------------------------------------------------------------------------
-- RemoteEvents
------------------------------------------------------------------------
local beatEvent = ReplicatedStorage:WaitForChild("MusicBeatEvent")
local stateEvent = ReplicatedStorage:WaitForChild("MusicStateEvent")
local activityEvent = ReplicatedStorage:WaitForChild("MusicActivityEvent")
local epochEvent = ReplicatedStorage:WaitForChild("MusicEpochEvent")

------------------------------------------------------------------------
-- State
------------------------------------------------------------------------
local beatEpoch = nil
local currentRoom = nil           -- room index or nil
local previousRoom = nil          -- for crossfade
local lastBeatNum = -1
local roomStates = {}             -- latest from server
local hudVisible = true

------------------------------------------------------------------------
-- Sound system
------------------------------------------------------------------------
-- soundGroups[roomIndex] = SoundGroup with child Sounds per layer
local soundGroups = {}

local function setupSounds()
	for i, roomDef in MusicConfig.Rooms do
		local sg = Instance.new("SoundGroup")
		sg.Name = roomDef.name .. "_SG"
		sg.Volume = 0  -- start silent; crossfade in
		sg.Parent = SoundService

		local assets = MusicConfig.SoundAssets[roomDef.mood]
		for layerName, layerDef in MusicConfig.Layers do
			local sound = Instance.new("Sound")
			sound.Name = layerName
			sound.Looped = true
			sound.Volume = 0
			sound.SoundGroup = sg

			local assetId = assets and assets[layerName] or ""
			if assetId ~= "" then
				sound.SoundId = assetId
			end

			sound.Parent = sg
		end

		soundGroups[i] = sg
	end
end

-- Crossfade: fade out previous room's SoundGroup, fade in current
local function crossfadeRooms(fromIdx: number?, toIdx: number?)
	local dur = MusicConfig.CrossfadeDuration

	if fromIdx and soundGroups[fromIdx] then
		local sg = soundGroups[fromIdx]
		TweenService:Create(sg, TweenInfo.new(dur, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), {Volume = 0}):Play()
	end

	if toIdx and soundGroups[toIdx] then
		local sg = soundGroups[toIdx]
		TweenService:Create(sg, TweenInfo.new(dur, Enum.EasingStyle.Quad, Enum.EasingDirection.In), {Volume = 1}):Play()
		-- Start any sounds that have asset IDs
		for _, sound in sg:GetChildren() do
			if sound:IsA("Sound") and sound.SoundId ~= "" and not sound.Playing then
				sound:Play()
			end
		end
	end
end

-- Update individual layer volumes based on active layers from server
local function updateLayerVolumes(roomIdx: number, activeLayers: {[string]: boolean})
	local sg = soundGroups[roomIdx]
	if not sg then return end

	for layerName, layerDef in MusicConfig.Layers do
		local sound = sg:FindFirstChild(layerName)
		if sound then
			local targetVol = (activeLayers[layerName] == true) and layerDef.baseVolume or 0
			TweenService:Create(sound, TweenInfo.new(layerDef.fadeTime, Enum.EasingStyle.Quad), {Volume = targetVol}):Play()
		end
	end
end

------------------------------------------------------------------------
-- Visual beat pulse system
------------------------------------------------------------------------

local function getRoomFolder(roomIdx: number): Instance?
	local world = workspace:FindFirstChild("MusicWorld")
	if not world then return nil end
	for _, child in world:GetChildren() do
		local idxVal = child:FindFirstChild("RoomIndex")
		if idxVal and idxVal.Value == roomIdx then
			return child
		end
	end
	return nil
end

-- Collect all parts with PulseTag in a room
local function getPulseParts(folder: Instance): {Instance}
	local parts = {}
	local function scan(parent)
		for _, child in parent:GetChildren() do
			if child:FindFirstChild("PulseTag") then
				table.insert(parts, child)
			end
			scan(child)
		end
	end
	scan(folder)
	return parts
end

-- Pulse a single part: scale up + color shift, then revert
local function pulsePart(part: Instance, roomDef: table, beatInMeasure: number)
	local vis = roomDef.visuals
	local dur = MusicConfig.PulseDuration
	local tag = part:FindFirstChild("PulseTag")
	if not tag then return end

	local pulseType = tag.Value

	if pulseType == "wall" then
		-- Neon color flash
		local origColor = part.Color
		part.Color = vis.pulseColor
		task.delay(dur, function()
			if part and part.Parent then
				TweenService:Create(part, TweenInfo.new(dur * 3, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), {Color = origColor}):Play()
			end
		end)

	elseif pulseType == "floor" then
		-- Floor tile: scale Y + color on downbeat, ripple on other beats
		local gridX = part:FindFirstChild("GridX")
		local gridZ = part:FindFirstChild("GridZ")
		local isDownbeat = (beatInMeasure == 1)

		if isDownbeat then
			-- All tiles flash on downbeat
			local origSize = part.Size
			local origColor = part.Color
			part.Size = origSize + Vector3.new(0, 0.5 * vis.pulseScale, 0)
			part.Color = vis.pulseColor
			task.delay(dur, function()
				if part and part.Parent then
					TweenService:Create(part, TweenInfo.new(dur * 4), {Size = origSize, Color = origColor}):Play()
				end
			end)
		else
			-- Ripple: only tiles where (gridX + gridZ) % 4 matches the beat
			if gridX and gridZ then
				local ring = (gridX.Value + gridZ.Value) % MusicConfig.BeatsPerMeasure
				if ring == (beatInMeasure - 1) then
					local origColor = part.Color
					part.Color = vis.pulseColor
					task.delay(dur, function()
						if part and part.Parent then
							TweenService:Create(part, TweenInfo.new(dur * 5), {Color = origColor}):Play()
						end
					end)
				end
			end
		end

	elseif pulseType == "light" then
		local light = part:FindFirstChild("PointLight")
		if light then
			local origBrightness = light.Brightness
			light.Brightness = origBrightness * 2
			task.delay(dur, function()
				if light and light.Parent then
					TweenService:Create(light, TweenInfo.new(dur * 4), {Brightness = origBrightness}):Play()
				end
			end)
		end

	elseif pulseType == "ceiling" then
		local emitter = part:FindFirstChildOfClass("ParticleEmitter")
		if emitter then
			local origRate = emitter.Rate
			emitter.Rate = origRate * 3
			task.delay(dur * 2, function()
				if emitter and emitter.Parent then
					emitter.Rate = origRate
				end
			end)
		end
	end
end

-- Trigger a full room pulse
local function pulseRoom(roomIdx: number, beatInMeasure: number)
	local folder = getRoomFolder(roomIdx)
	if not folder then return end

	local roomDef = MusicConfig.Rooms[roomIdx]
	if not roomDef then return end

	local parts = getPulseParts(folder)
	for _, part in parts do
		pulsePart(part, roomDef, beatInMeasure)
	end
end

------------------------------------------------------------------------
-- HUD
------------------------------------------------------------------------
local screenGui = Instance.new("ScreenGui")
screenGui.Name = "MusicHUD"
screenGui.ResetOnSpawn = false
screenGui.IgnoreGuiInset = true
screenGui.Parent = playerGui

-- Room name label (top center)
local roomLabel = Instance.new("TextLabel")
roomLabel.Name = "RoomLabel"
roomLabel.Size = UDim2.new(0, 300, 0, 40)
roomLabel.Position = UDim2.new(0.5, -150, 0, 10)
roomLabel.BackgroundColor3 = Color3.fromRGB(0, 0, 0)
roomLabel.BackgroundTransparency = 0.6
roomLabel.BorderSizePixel = 0
roomLabel.Text = "Lobby"
roomLabel.Font = Enum.Font.BuilderSansBold
roomLabel.TextColor3 = Color3.fromRGB(200, 200, 220)
roomLabel.TextSize = 22
roomLabel.Parent = screenGui

local roomLabelCorner = Instance.new("UICorner")
roomLabelCorner.CornerRadius = UDim.new(0, 8)
roomLabelCorner.Parent = roomLabel

-- Beat visualizer (small pulsing circle, top center below room name)
local beatDot = Instance.new("Frame")
beatDot.Name = "BeatDot"
beatDot.Size = UDim2.new(0, 12, 0, 12)
beatDot.Position = UDim2.new(0.5, -6, 0, 56)
beatDot.BackgroundColor3 = Color3.fromRGB(255, 255, 255)
beatDot.BorderSizePixel = 0
beatDot.Parent = screenGui

local beatDotCorner = Instance.new("UICorner")
beatDotCorner.CornerRadius = UDim.new(0.5, 0)
beatDotCorner.Parent = beatDot

-- Layer indicators (bottom left)
local layerPanel = Instance.new("Frame")
layerPanel.Name = "LayerPanel"
layerPanel.Size = UDim2.new(0, 180, 0, 160)
layerPanel.Position = UDim2.new(0, 16, 1, -176)
layerPanel.BackgroundColor3 = Color3.fromRGB(0, 0, 0)
layerPanel.BackgroundTransparency = 0.6
layerPanel.BorderSizePixel = 0
layerPanel.Parent = screenGui

local layerPanelCorner = Instance.new("UICorner")
layerPanelCorner.CornerRadius = UDim.new(0, 8)
layerPanelCorner.Parent = layerPanel

local layerTitle = Instance.new("TextLabel")
layerTitle.Size = UDim2.new(1, 0, 0, 24)
layerTitle.Position = UDim2.new(0, 0, 0, 4)
layerTitle.BackgroundTransparency = 1
layerTitle.Text = "LAYERS"
layerTitle.Font = Enum.Font.BuilderSansBold
layerTitle.TextColor3 = Color3.fromRGB(180, 180, 180)
layerTitle.TextSize = 14
layerTitle.Parent = layerPanel

local layerLabels = {}
local layerOrder = {"bass", "pad", "melody", "arp", "percussion"}
for i, name in layerOrder do
	local row = Instance.new("Frame")
	row.Size = UDim2.new(1, -16, 0, 22)
	row.Position = UDim2.new(0, 8, 0, 24 + (i - 1) * 26)
	row.BackgroundTransparency = 1
	row.Name = name
	row.Parent = layerPanel

	local dot = Instance.new("Frame")
	dot.Size = UDim2.new(0, 10, 0, 10)
	dot.Position = UDim2.new(0, 0, 0.5, -5)
	dot.BackgroundColor3 = Color3.fromRGB(60, 60, 60)
	dot.BorderSizePixel = 0
	dot.Name = "Dot"
	dot.Parent = row

	local dotCorner = Instance.new("UICorner")
	dotCorner.CornerRadius = UDim.new(0.5, 0)
	dotCorner.Parent = dot

	local lbl = Instance.new("TextLabel")
	lbl.Size = UDim2.new(1, -18, 1, 0)
	lbl.Position = UDim2.new(0, 18, 0, 0)
	lbl.BackgroundTransparency = 1
	lbl.Text = name:sub(1, 1):upper() .. name:sub(2)
	lbl.Font = Enum.Font.BuilderSans
	lbl.TextColor3 = Color3.fromRGB(140, 140, 140)
	lbl.TextSize = 14
	lbl.TextXAlignment = Enum.TextXAlignment.Left
	lbl.Parent = row

	layerLabels[name] = {dot = dot, label = lbl}
end

-- Activity indicator (bottom right)
local activityPanel = Instance.new("Frame")
activityPanel.Name = "ActivityPanel"
activityPanel.Size = UDim2.new(0, 160, 0, 80)
activityPanel.Position = UDim2.new(1, -176, 1, -96)
activityPanel.BackgroundColor3 = Color3.fromRGB(0, 0, 0)
activityPanel.BackgroundTransparency = 0.6
activityPanel.BorderSizePixel = 0
activityPanel.Parent = screenGui

local activityCorner = Instance.new("UICorner")
activityCorner.CornerRadius = UDim.new(0, 8)
activityCorner.Parent = activityPanel

local activityLabel = Instance.new("TextLabel")
activityLabel.Size = UDim2.new(1, 0, 0, 20)
activityLabel.Position = UDim2.new(0, 0, 0, 4)
activityLabel.BackgroundTransparency = 1
activityLabel.Text = "ACTIVITY"
activityLabel.Font = Enum.Font.BuilderSansBold
activityLabel.TextColor3 = Color3.fromRGB(180, 180, 180)
activityLabel.TextSize = 14
activityLabel.Parent = activityPanel

local playerCountLabel = Instance.new("TextLabel")
playerCountLabel.Size = UDim2.new(1, -16, 0, 18)
playerCountLabel.Position = UDim2.new(0, 8, 0, 26)
playerCountLabel.BackgroundTransparency = 1
playerCountLabel.Text = "Players: 0"
playerCountLabel.Font = Enum.Font.BuilderSans
playerCountLabel.TextColor3 = Color3.fromRGB(160, 160, 160)
playerCountLabel.TextSize = 13
playerCountLabel.TextXAlignment = Enum.TextXAlignment.Left
playerCountLabel.Parent = activityPanel

local activityStatusLabel = Instance.new("TextLabel")
activityStatusLabel.Size = UDim2.new(1, -16, 0, 18)
activityStatusLabel.Position = UDim2.new(0, 8, 0, 46)
activityStatusLabel.BackgroundTransparency = 1
activityStatusLabel.Text = "Standing"
activityStatusLabel.Font = Enum.Font.BuilderSans
activityStatusLabel.TextColor3 = Color3.fromRGB(160, 160, 160)
activityStatusLabel.TextSize = 13
activityStatusLabel.TextXAlignment = Enum.TextXAlignment.Left
activityStatusLabel.Parent = activityPanel

-- Scale display (top right, shows current room's scale)
local scaleLabel = Instance.new("TextLabel")
scaleLabel.Name = "ScaleLabel"
scaleLabel.Size = UDim2.new(0, 200, 0, 30)
scaleLabel.Position = UDim2.new(1, -216, 0, 10)
scaleLabel.BackgroundColor3 = Color3.fromRGB(0, 0, 0)
scaleLabel.BackgroundTransparency = 0.6
scaleLabel.BorderSizePixel = 0
scaleLabel.Text = ""
scaleLabel.Font = Enum.Font.BuilderSans
scaleLabel.TextColor3 = Color3.fromRGB(160, 160, 160)
scaleLabel.TextSize = 14
scaleLabel.Parent = screenGui

local scaleLabelCorner = Instance.new("UICorner")
scaleLabelCorner.CornerRadius = UDim.new(0, 8)
scaleLabelCorner.Parent = scaleLabel

-- Controls hint
local hintLabel = Instance.new("TextLabel")
hintLabel.Size = UDim2.new(0, 200, 0, 20)
hintLabel.Position = UDim2.new(0.5, -100, 1, -28)
hintLabel.BackgroundTransparency = 1
hintLabel.Text = "[H] Toggle HUD"
hintLabel.Font = Enum.Font.BuilderSans
hintLabel.TextColor3 = Color3.fromRGB(100, 100, 100)
hintLabel.TextSize = 12
hintLabel.Parent = screenGui

------------------------------------------------------------------------
-- HUD update
------------------------------------------------------------------------
local function updateHUD()
	-- Room label
	if currentRoom then
		local roomDef = MusicConfig.Rooms[currentRoom]
		roomLabel.Text = roomDef.name
		roomLabel.TextColor3 = roomDef.visuals.pulseColor
		scaleLabel.Text = roomDef.music.scale:sub(1, 1):upper() .. roomDef.music.scale:sub(2) .. " | " .. roomDef.music.bpm .. " BPM"
	else
		roomLabel.Text = "Lobby"
		roomLabel.TextColor3 = Color3.fromRGB(200, 200, 220)
		scaleLabel.Text = ""
	end

	-- Layer indicators
	local activeLayers = {}
	if currentRoom and roomStates[currentRoom] then
		activeLayers = roomStates[currentRoom].layers or {}
	end

	for layerName, ui in layerLabels do
		local isActive = activeLayers[layerName] == true
		local color = isActive and Color3.fromRGB(100, 255, 100) or Color3.fromRGB(60, 60, 60)
		ui.dot.BackgroundColor3 = color
		ui.label.TextColor3 = isActive and Color3.fromRGB(220, 220, 220) or Color3.fromRGB(100, 100, 100)
	end

	-- Player count
	if currentRoom and roomStates[currentRoom] then
		playerCountLabel.Text = "Players: " .. tostring(roomStates[currentRoom].pc or 0)
	else
		playerCountLabel.Text = "Players: --"
	end
end

local function setHUDVisible(visible: boolean)
	hudVisible = visible
	for _, child in screenGui:GetChildren() do
		if child:IsA("GuiObject") then
			child.Visible = visible
		end
	end
end

------------------------------------------------------------------------
-- Activity detection (client-side)
------------------------------------------------------------------------
local lastJumpTime = 0
local localActivity = "standing"

local function detectActivity()
	local character = player.Character
	if not character then return end

	local humanoid = character:FindFirstChildOfClass("Humanoid")
	local rootPart = character:FindFirstChild("HumanoidRootPart")
	if not humanoid or not rootPart then return end

	local speed = rootPart.AssemblyLinearVelocity.Magnitude

	if speed >= MusicConfig.Activity.runSpeedThreshold then
		localActivity = "running"
	elseif speed < MusicConfig.Activity.stillThreshold then
		localActivity = "still"
	else
		localActivity = "walking"
	end

	activityStatusLabel.Text = localActivity:sub(1, 1):upper() .. localActivity:sub(2)

	-- Jump detection
	if humanoid.Jump and (tick() - lastJumpTime) >= MusicConfig.Activity.jumpCooldown then
		lastJumpTime = tick()
		activityEvent:FireServer("jump")
	end
end

------------------------------------------------------------------------
-- Room detection (client-side, for immediate visual response)
------------------------------------------------------------------------
local function detectRoom()
	local character = player.Character
	if not character then return end

	local rootPart = character:FindFirstChild("HumanoidRootPart")
	if not rootPart then return end

	local pos = rootPart.Position
	local roomSize = MusicConfig.RoomSize
	local halfX = roomSize.X / 2
	local halfZ = roomSize.Z / 2

	local newRoom = nil
	local world = workspace:FindFirstChild("MusicWorld")
	if world then
		for _, child in world:GetChildren() do
			local idxVal = child:FindFirstChild("RoomIndex")
			local centerVal = child:FindFirstChild("RoomCenter")
			if idxVal and centerVal then
				local center = centerVal.Value
				if math.abs(pos.X - center.X) <= halfX
					and math.abs(pos.Z - center.Z) <= halfZ
					and pos.Y >= center.Y
					and pos.Y <= center.Y + roomSize.Y then
					newRoom = idxVal.Value
					break
				end
			end
		end
	end

	if newRoom ~= currentRoom then
		previousRoom = currentRoom
		currentRoom = newRoom
		crossfadeRooms(previousRoom, currentRoom)
		updateHUD()
	end
end

------------------------------------------------------------------------
-- Event handlers
------------------------------------------------------------------------

-- Receive beat epoch from server
epochEvent.OnClientEvent:Connect(function(epoch)
	beatEpoch = epoch
end)

-- Receive room state updates
stateEvent.OnClientEvent:Connect(function(beatNum, payload)
	roomStates = payload
	-- Update layer volumes for current room
	if currentRoom and roomStates[currentRoom] then
		updateLayerVolumes(currentRoom, roomStates[currentRoom].layers or {})
	end
	updateHUD()
end)

-- Receive beat events for visual pulsing
beatEvent.OnClientEvent:Connect(function(beatNum, measure, beatInMeasure, serverRoomIdx)
	if beatNum == lastBeatNum then return end
	lastBeatNum = beatNum

	-- Pulse beat dot
	beatDot.Size = UDim2.new(0, 20, 0, 20)
	beatDot.Position = UDim2.new(0.5, -10, 0, 52)
	if currentRoom then
		beatDot.BackgroundColor3 = MusicConfig.Rooms[currentRoom].visuals.pulseColor
	else
		beatDot.BackgroundColor3 = Color3.fromRGB(255, 255, 255)
	end
	task.delay(MusicConfig.PulseDuration, function()
		TweenService:Create(beatDot, TweenInfo.new(0.3), {
			Size = UDim2.new(0, 12, 0, 12),
			Position = UDim2.new(0.5, -6, 0, 56),
			BackgroundColor3 = Color3.fromRGB(80, 80, 80),
		}):Play()
	end)

	-- Pulse the room the player is in
	if currentRoom then
		pulseRoom(currentRoom, beatInMeasure)
	end
end)

------------------------------------------------------------------------
-- Input
------------------------------------------------------------------------
UserInputService.InputBegan:Connect(function(input, processed)
	if processed then return end

	if input.KeyCode == Enum.KeyCode.H then
		setHUDVisible(not hudVisible)
	end
end)

------------------------------------------------------------------------
-- Main loop
------------------------------------------------------------------------
setupSounds()

RunService.Heartbeat:Connect(function(dt)
	detectRoom()
	detectActivity()
end)

print("[MusicClient] Generative Music Rooms client started.")
