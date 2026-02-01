--[[
	DialogueManager.luau
	ModuleScript → ServerStorage

	Builds the town geometry (buildings, landmarks, ground) and NPC
	models.  Provides dialogue tree traversal with personality-aware
	template injection.  Also handles world mood application (lighting,
	fog, sky colour).
]]

local DialogueManager = {}

local StoryConfig = require(game:GetService("ReplicatedStorage"):WaitForChild("StoryConfig"))

------------------------------------------------------------------------
-- Town geometry builder
------------------------------------------------------------------------

-- Build a simple rectangular structure
local function buildBox(parent, center, size, color, material, name)
	local part = Instance.new("Part")
	part.Anchored = true
	part.CanCollide = true
	part.Size = size
	part.Position = center + Vector3.new(0, size.Y / 2, 0)
	part.Material = material
	part.Color = color
	part.TopSurface = Enum.SurfaceType.Smooth
	part.BottomSurface = Enum.SurfaceType.Smooth
	part.Name = name or "Structure"
	part.Parent = parent
	return part
end

-- Build a roof (slightly larger than the building, angled)
local function buildRoof(parent, center, size, color)
	local roof = Instance.new("Part")
	roof.Anchored = true
	roof.CanCollide = true
	roof.Size = Vector3.new(size.X + 2, 1.5, size.Z + 2)
	roof.Position = center + Vector3.new(0, size.Y + 0.75, 0)
	roof.Material = Enum.Material.WoodPlanks
	roof.Color = Color3.fromRGB(
		math.min(255, color.R * 255 * 0.7),
		math.min(255, color.G * 255 * 0.7),
		math.min(255, color.B * 255 * 0.7)
	)
	roof.TopSurface = Enum.SurfaceType.Smooth
	roof.BottomSurface = Enum.SurfaceType.Smooth
	roof.Name = "Roof"
	roof.Parent = parent
	return roof
end

-- Build the ground plane
local function buildGround(parent)
	local ground = Instance.new("Part")
	ground.Anchored = true
	ground.CanCollide = true
	ground.Size = Vector3.new(300, 1, 300)
	ground.Position = Vector3.new(0, -0.5, 0)
	ground.Material = Enum.Material.Grass
	ground.Color = Color3.fromRGB(80, 110, 70)
	ground.TopSurface = Enum.SurfaceType.Smooth
	ground.BottomSurface = Enum.SurfaceType.Smooth
	ground.Name = "Ground"
	ground.Parent = parent

	-- Stone path from gate to tower (center strip)
	local path = Instance.new("Part")
	path.Anchored = true
	path.CanCollide = true
	path.Size = Vector3.new(8, 0.15, 180)
	path.Position = Vector3.new(0, 0.075, -5)
	path.Material = Enum.Material.Slate
	path.Color = Color3.fromRGB(130, 125, 115)
	path.TopSurface = Enum.SurfaceType.Smooth
	path.BottomSurface = Enum.SurfaceType.Smooth
	path.Name = "MainPath"
	path.Parent = parent

	-- Cross path (east-west)
	local crossPath = Instance.new("Part")
	crossPath.Anchored = true
	crossPath.CanCollide = true
	crossPath.Size = Vector3.new(120, 0.15, 6)
	crossPath.Position = Vector3.new(0, 0.075, 0)
	crossPath.Material = Enum.Material.Slate
	crossPath.Color = Color3.fromRGB(130, 125, 115)
	crossPath.TopSurface = Enum.SurfaceType.Smooth
	crossPath.BottomSurface = Enum.SurfaceType.Smooth
	crossPath.Name = "CrossPath"
	crossPath.Parent = parent

	return ground
end

-- Build a fountain in the town square
local function buildFountain(parent)
	local base = Instance.new("Part")
	base.Anchored = true
	base.CanCollide = true
	base.Shape = Enum.PartType.Cylinder
	base.Size = Vector3.new(2, 10, 10)  -- height, diameter, diameter
	base.CFrame = CFrame.new(0, 1, 0) * CFrame.Angles(0, 0, math.rad(90))
	base.Material = Enum.Material.Marble
	base.Color = Color3.fromRGB(180, 175, 170)
	base.Name = "FountainBase"
	base.Parent = parent

	local pillar = Instance.new("Part")
	pillar.Anchored = true
	pillar.CanCollide = true
	pillar.Shape = Enum.PartType.Cylinder
	pillar.Size = Vector3.new(5, 2, 2)
	pillar.CFrame = CFrame.new(0, 3.5, 0) * CFrame.Angles(0, 0, math.rad(90))
	pillar.Material = Enum.Material.Marble
	pillar.Color = Color3.fromRGB(190, 185, 180)
	pillar.Name = "FountainPillar"
	pillar.Parent = parent

	-- Water particles
	local emitter = Instance.new("ParticleEmitter")
	emitter.Rate = 15
	emitter.Lifetime = NumberRange.new(1, 2.5)
	emitter.Speed = NumberRange.new(2, 5)
	emitter.SpreadAngle = Vector2.new(30, 30)
	emitter.Color = ColorSequence.new(Color3.fromRGB(150, 180, 220))
	emitter.Size = NumberSequence.new({
		NumberSequenceKeypoint.new(0, 0.2),
		NumberSequenceKeypoint.new(0.5, 0.4),
		NumberSequenceKeypoint.new(1, 0),
	})
	emitter.Transparency = NumberSequence.new({
		NumberSequenceKeypoint.new(0, 0.3),
		NumberSequenceKeypoint.new(1, 0.8),
	})
	emitter.LightEmission = 0.3
	emitter.Parent = pillar

	-- Town name sign on the fountain
	local sign = Instance.new("Part")
	sign.Anchored = true
	sign.CanCollide = false
	sign.Transparency = 1
	sign.Size = Vector3.new(8, 2, 0.2)
	sign.Position = Vector3.new(0, 7, 0)
	sign.Name = "TownSign"

	local gui = Instance.new("SurfaceGui")
	gui.Face = Enum.NormalId.Front
	gui.SizingMode = Enum.SurfaceGuiSizingMode.PixelsPerStud
	gui.PixelsPerStud = 25
	gui.Parent = sign

	local label = Instance.new("TextLabel")
	label.Size = UDim2.new(1, 0, 1, 0)
	label.BackgroundTransparency = 1
	label.Text = "LIVING STORY"
	label.Font = Enum.Font.BuilderSansBold
	label.TextColor3 = Color3.fromRGB(200, 195, 185)
	label.TextScaled = true
	label.Parent = gui

	-- Second face
	local gui2 = gui:Clone()
	gui2.Face = Enum.NormalId.Back
	gui2.Parent = sign

	sign.Parent = parent
end

-- Build a name sign for a building
local function buildBuildingSign(parent, position, text, color)
	local sign = Instance.new("Part")
	sign.Anchored = true
	sign.CanCollide = false
	sign.Transparency = 0.3
	sign.Size = Vector3.new(10, 2.5, 0.3)
	sign.Position = position
	sign.Material = Enum.Material.SmoothPlastic
	sign.Color = color or Color3.fromRGB(80, 70, 60)
	sign.Name = "Sign_" .. text

	local gui = Instance.new("SurfaceGui")
	gui.Face = Enum.NormalId.Front
	gui.SizingMode = Enum.SurfaceGuiSizingMode.PixelsPerStud
	gui.PixelsPerStud = 20
	gui.Parent = sign

	local label = Instance.new("TextLabel")
	label.Size = UDim2.new(1, 0, 1, 0)
	label.BackgroundTransparency = 1
	label.Text = text
	label.Font = Enum.Font.BuilderSansBold
	label.TextColor3 = Color3.fromRGB(220, 210, 200)
	label.TextScaled = true
	label.Parent = gui

	sign.Parent = parent
	return sign
end

------------------------------------------------------------------------
-- NPC model builder
------------------------------------------------------------------------

function DialogueManager.buildNPC(npcDef: table, parent: Instance): Instance
	local npcModel = Instance.new("Model")
	npcModel.Name = npcDef.id

	-- Torso
	local torso = Instance.new("Part")
	torso.Anchored = true
	torso.CanCollide = true
	torso.Size = Vector3.new(2, 2.5, 1.2)
	torso.Position = npcDef.position + Vector3.new(0, 3.25, 0)
	torso.Material = Enum.Material.SmoothPlastic
	torso.Color = npcDef.shirtColor
	torso.Name = "Torso"
	torso.Parent = npcModel

	-- Head
	local head = Instance.new("Part")
	head.Anchored = true
	head.CanCollide = false
	head.Shape = Enum.PartType.Ball
	head.Size = Vector3.new(StoryConfig.NPCHeadSize, StoryConfig.NPCHeadSize, StoryConfig.NPCHeadSize)
	head.Position = npcDef.position + Vector3.new(0, 5, 0)
	head.Material = Enum.Material.SmoothPlastic
	head.Color = npcDef.bodyColor
	head.Name = "Head"
	head.Parent = npcModel

	-- Eyes
	for _, side in {-0.25, 0.25} do
		local eye = Instance.new("Part")
		eye.Anchored = true
		eye.CanCollide = false
		eye.Size = Vector3.new(0.15, 0.15, 0.1)
		eye.Position = head.Position + Vector3.new(side, 0.1, -0.55)
		eye.Material = Enum.Material.Neon
		eye.Color = Color3.fromRGB(220, 220, 230)
		eye.Name = "Eye"
		eye.Parent = npcModel
	end

	-- Legs
	for _, side in {-0.5, 0.5} do
		local leg = Instance.new("Part")
		leg.Anchored = true
		leg.CanCollide = true
		leg.Size = Vector3.new(0.8, 2, 0.8)
		leg.Position = npcDef.position + Vector3.new(side, 1, 0)
		leg.Material = Enum.Material.SmoothPlastic
		leg.Color = Color3.fromRGB(60, 55, 50)
		leg.Name = "Leg"
		leg.Parent = npcModel
	end

	-- Arms
	for _, side in {-1.2, 1.2} do
		local arm = Instance.new("Part")
		arm.Anchored = true
		arm.CanCollide = false
		arm.Size = Vector3.new(0.6, 2.2, 0.6)
		arm.Position = npcDef.position + Vector3.new(side, 3.1, 0)
		arm.Material = Enum.Material.SmoothPlastic
		arm.Color = npcDef.bodyColor
		arm.Name = "Arm"
		arm.Parent = npcModel
	end

	-- Name label (floating above)
	local nameSign = Instance.new("Part")
	nameSign.Anchored = true
	nameSign.CanCollide = false
	nameSign.Transparency = 1
	nameSign.Size = Vector3.new(6, 1.5, 0.2)
	nameSign.Position = npcDef.position + Vector3.new(0, 6.5, 0)
	nameSign.Name = "NameSign"

	local gui = Instance.new("BillboardGui")
	gui.Size = UDim2.new(6, 0, 1.5, 0)
	gui.StudsOffset = Vector3.new(0, 0, 0)
	gui.AlwaysOnTop = false
	gui.MaxDistance = 30
	gui.Parent = nameSign

	local nameLabel = Instance.new("TextLabel")
	nameLabel.Size = UDim2.new(1, 0, 0.6, 0)
	nameLabel.Position = UDim2.new(0, 0, 0, 0)
	nameLabel.BackgroundTransparency = 1
	nameLabel.Text = npcDef.name
	nameLabel.Font = Enum.Font.BuilderSansBold
	nameLabel.TextColor3 = Color3.fromRGB(220, 215, 200)
	nameLabel.TextScaled = true
	nameLabel.Parent = gui

	local roleLabel = Instance.new("TextLabel")
	roleLabel.Size = UDim2.new(1, 0, 0.4, 0)
	roleLabel.Position = UDim2.new(0, 0, 0.6, 0)
	roleLabel.BackgroundTransparency = 1
	roleLabel.Text = npcDef.role
	roleLabel.Font = Enum.Font.BuilderSans
	roleLabel.TextColor3 = Color3.fromRGB(160, 155, 145)
	roleLabel.TextScaled = true
	roleLabel.Parent = gui

	nameSign.Parent = npcModel

	-- ProximityPrompt on the torso
	local prompt = Instance.new("ProximityPrompt")
	prompt.ActionText = "Talk"
	prompt.ObjectText = npcDef.name
	prompt.MaxActivationDistance = StoryConfig.InteractionRange
	prompt.HoldDuration = 0
	prompt.RequiresLineOfSight = false
	prompt.Parent = torso

	-- Store NPC data
	local idVal = Instance.new("StringValue")
	idVal.Name = "NPCID"
	idVal.Value = npcDef.id
	idVal.Parent = npcModel

	local dialogueVal = Instance.new("StringValue")
	dialogueVal.Name = "DialogueKey"
	dialogueVal.Value = npcDef.dialogueKey
	dialogueVal.Parent = npcModel

	local descVal = Instance.new("StringValue")
	descVal.Name = "Description"
	descVal.Value = npcDef.description
	descVal.Parent = npcModel

	npcModel.PrimaryPart = torso
	npcModel.Parent = parent
	return npcModel
end

------------------------------------------------------------------------
-- Dialogue tree traversal
------------------------------------------------------------------------

-- Get a dialogue node, handling return visits
function DialogueManager.getNode(dialogueKey: string, nodeId: string, hasVisited: boolean): table?
	local tree = StoryConfig.DialogueTrees[dialogueKey]
	if not tree then return nil end

	-- If player has visited before and there's a returnVisit node
	if hasVisited and nodeId == "start" and tree.returnVisit then
		return tree.returnVisit
	end

	return tree[nodeId]
end

-- Apply template substitutions to dialogue text
function DialogueManager.resolveText(text: string, playerData: table): string
	local result = text

	-- {name}
	result = result:gsub("{name}", playerData.name or "Stranger")

	-- {tendency}
	local tendency = "uncertain"
	if playerData.dominantTrait and StoryConfig.Tendencies[playerData.dominantTrait] then
		tendency = StoryConfig.Tendencies[playerData.dominantTrait]
	end
	result = result:gsub("{tendency}", tendency)

	-- {memory_reflection}
	local reflection = "You have walked quietly through this place."
	if playerData.memories and #playerData.memories > 0 then
		local mem = playerData.memories[math.random(#playerData.memories)]
		reflection = "I remember when you " .. mem .. "."
	end
	result = result:gsub("{memory_reflection}", reflection)

	-- {ending_truth}, {ending_escape}, {ending_confront}, {ending_lie}
	local function getEnding()
		local dom = playerData.dominantTrait
		if dom and StoryConfig.Endings[dom .. "_dominant"] then
			return table.concat(StoryConfig.Endings[dom .. "_dominant"], "\n")
		end
		return table.concat(StoryConfig.Endings.default, "\n")
	end
	result = result:gsub("{ending_truth}", getEnding())
	result = result:gsub("{ending_escape}", getEnding())
	result = result:gsub("{ending_confront}", getEnding())
	result = result:gsub("{ending_lie}", getEnding())

	return result
end

-- Resolve a full node's text (array of lines) with substitutions
function DialogueManager.resolveNodeText(node: table, playerData: table): {string}
	local lines = {}
	local textSource = node.text
	if type(textSource) == "string" then
		textSource = {textSource}
	end
	for _, line in textSource do
		table.insert(lines, DialogueManager.resolveText(line, playerData))
	end
	return lines
end

-- Get dominant trait from a personality table
function DialogueManager.getDominantTrait(personality: {[string]: number}): string?
	local best = nil
	local bestVal = 0
	for trait, val in personality do
		if val > bestVal then
			best = trait
			bestVal = val
		end
	end
	return best
end

------------------------------------------------------------------------
-- Build the full town
------------------------------------------------------------------------
function DialogueManager.buildTown(): Instance
	local townFolder = Instance.new("Folder")
	townFolder.Name = "LivingStoryTown"
	townFolder.Parent = workspace

	-- Ground
	buildGround(townFolder)

	-- Fountain
	buildFountain(townFolder)

	-- Buildings
	local buildingsFolder = Instance.new("Folder")
	buildingsFolder.Name = "Buildings"
	buildingsFolder.Parent = townFolder

	for _, bldg in StoryConfig.Buildings do
		local folder = Instance.new("Folder")
		folder.Name = bldg.name
		folder.Parent = buildingsFolder

		if bldg.size.Y > 2 then  -- actual structure, not just a ground marker
			buildBox(folder, bldg.center, bldg.size, bldg.color, bldg.material, "Walls")
			if bldg.hasRoof then
				buildRoof(folder, bldg.center, bldg.size, bldg.color)
			end
		else
			-- Ground-level platform
			buildBox(folder, bldg.center, bldg.size, bldg.color, bldg.material, "Platform")
		end

		-- Building sign
		local signPos = bldg.center + Vector3.new(0, bldg.size.Y + 2, -bldg.size.Z / 2 - 1)
		buildBuildingSign(folder, signPos, bldg.name, bldg.color)
	end

	-- NPCs
	local npcFolder = Instance.new("Folder")
	npcFolder.Name = "NPCs"
	npcFolder.Parent = townFolder

	for _, npcDef in StoryConfig.NPCs do
		DialogueManager.buildNPC(npcDef, npcFolder)
	end

	-- Spawn location at the gate
	local spawn = Instance.new("SpawnLocation")
	spawn.Anchored = true
	spawn.CanCollide = true
	spawn.Size = Vector3.new(8, 1, 8)
	spawn.Position = Vector3.new(0, 0, -100)
	spawn.Material = Enum.Material.SmoothPlastic
	spawn.Color = Color3.fromRGB(100, 95, 85)
	spawn.TopSurface = Enum.SurfaceType.Smooth
	spawn.BottomSurface = Enum.SurfaceType.Smooth
	spawn.Name = "GateSpawn"
	spawn.Parent = townFolder

	-- Ambient lighting (default)
	local lighting = game:GetService("Lighting")
	lighting.Ambient = StoryConfig.DefaultMood.ambientColor
	lighting.Brightness = StoryConfig.DefaultMood.brightness
	lighting.FogEnd = StoryConfig.DefaultMood.fogEnd
	lighting.FogColor = Color3.fromRGB(180, 175, 170)

	return townFolder
end

------------------------------------------------------------------------
-- World mood application
------------------------------------------------------------------------
function DialogueManager.applyWorldMood(mood: table)
	local lighting = game:GetService("Lighting")

	-- Smoothly transition lighting properties
	local TweenService = game:GetService("TweenService")
	local tweenInfo = TweenInfo.new(3, Enum.EasingStyle.Quad, Enum.EasingDirection.InOut)

	TweenService:Create(lighting, tweenInfo, {
		Ambient = mood.ambientColor,
		Brightness = mood.brightness,
		FogEnd = mood.fogEnd,
	}):Play()

	-- Sky color via Atmosphere if available
	local atmo = lighting:FindFirstChildOfClass("Atmosphere")
	if not atmo then
		atmo = Instance.new("Atmosphere")
		atmo.Parent = lighting
	end
	atmo.Color = mood.skyColor
	atmo.Decay = Color3.fromRGB(120, 115, 110)
	atmo.Density = 0.3
end

return DialogueManager
