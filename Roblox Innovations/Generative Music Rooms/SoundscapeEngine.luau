--[[
	SoundscapeEngine.luau
	ModuleScript → ServerStorage

	Builds room geometry (waveform walls, pulsing floors, particle
	ceilings) and provides the global beat clock used by both server
	and client.  Also exposes helpers for scale-note lookup and
	waveform math so other modules stay DRY.
]]

local SoundscapeEngine = {}

local MusicConfig = require(game:GetService("ReplicatedStorage"):WaitForChild("MusicConfig"))

------------------------------------------------------------------------
-- Waveform math
------------------------------------------------------------------------

-- Returns a Y offset for a given position along a wall (0-1 normalized)
-- based on the wall style.
function SoundscapeEngine.waveformY(style: string, t: number, periods: number, amplitude: number): number
	local phase = t * periods * math.pi * 2
	if style == "sine" then
		return math.sin(phase) * amplitude
	elseif style == "sawtooth" then
		-- Sawtooth: rises linearly, drops at period boundary
		local p = (t * periods) % 1
		return (p * 2 - 1) * amplitude
	elseif style == "square" then
		return (math.sin(phase) >= 0 and 1 or -1) * amplitude
	elseif style == "triangle" then
		local p = (t * periods) % 1
		return (math.abs(p * 4 - 2) - 1) * amplitude
	elseif style == "noise" then
		-- Deterministic noise using math.noise so geometry is stable
		return math.noise(t * periods * 3, 0.5) * amplitude * 2
	else -- "flat"
		return 0
	end
end

------------------------------------------------------------------------
-- Scale / note helpers
------------------------------------------------------------------------

-- Given a scale name, returns a table of semitone offsets
function SoundscapeEngine.getScale(scaleName: string): {number}
	return MusicConfig.Scales[scaleName] or MusicConfig.Scales.pentatonic
end

-- Maps a scale degree (1-based, can exceed octave) to a semitone offset
function SoundscapeEngine.degreeToSemitone(scale: {number}, degree: number): number
	local octave = math.floor((degree - 1) / #scale)
	local idx = ((degree - 1) % #scale) + 1
	return scale[idx] + octave * 12
end

-- Converts MIDI note to a human-readable label (for UI)
local NOTE_NAMES = {"C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"}
function SoundscapeEngine.midiToName(midi: number): string
	local octave = math.floor(midi / 12) - 1
	local note = (midi % 12) + 1
	return NOTE_NAMES[note] .. tostring(octave)
end

------------------------------------------------------------------------
-- Beat clock (lightweight, deterministic)
------------------------------------------------------------------------

-- Returns the current beat number (fractional) for a given BPM,
-- referenced to an epoch (server start time). Both server and client
-- can call this with the same epoch for sync.
function SoundscapeEngine.getBeat(bpm: number, epoch: number): number
	local elapsed = tick() - epoch
	return elapsed * (bpm / 60)
end

-- Returns true on the exact frame a new beat starts (integer crossing)
function SoundscapeEngine.isNewBeat(beatNow: number, beatPrev: number): boolean
	return math.floor(beatNow) ~= math.floor(beatPrev)
end

-- Returns the measure number (1-based) and beat-within-measure (1-based)
function SoundscapeEngine.beatToMeasure(beat: number): (number, number)
	local bpm = MusicConfig.BeatsPerMeasure
	local measure = math.floor(beat / bpm) + 1
	local beatInMeasure = math.floor(beat % bpm) + 1
	return measure, beatInMeasure
end

------------------------------------------------------------------------
-- Room geometry builder
------------------------------------------------------------------------

-- Builds a single waveform wall as a series of Part segments
local function buildWaveWall(parent: Instance, origin: Vector3, direction: Vector3, length: number, height: number, style: string, periods: number, color: Color3)
	local segments = MusicConfig.WaveResolution
	local segWidth = length / segments
	local amplitude = MusicConfig.WaveAmplitude
	local thickness = MusicConfig.WallThickness

	local wallFolder = Instance.new("Folder")
	wallFolder.Name = "WaveWall"
	wallFolder.Parent = parent

	-- direction is a unit vector along the wall's length axis
	-- "outward" is perpendicular (the wave displacement direction)
	local outward = Vector3.new(-direction.Z, 0, direction.X)

	for i = 0, segments - 1 do
		local t = (i + 0.5) / segments
		local yOff = SoundscapeEngine.waveformY(style, t, periods, amplitude)

		local part = Instance.new("Part")
		part.Anchored = true
		part.CanCollide = true
		part.Size = Vector3.new(segWidth, height, thickness)
		part.Material = Enum.Material.Neon
		part.Color = color
		part.TopSurface = Enum.SurfaceType.Smooth
		part.BottomSurface = Enum.SurfaceType.Smooth

		local pos = origin
			+ direction * (i * segWidth + segWidth / 2)
			+ outward * yOff
			+ Vector3.new(0, height / 2, 0)
		part.Position = pos
		part.Name = "WaveSeg_" .. tostring(i)

		-- Tag for beat pulsing
		local tag = Instance.new("StringValue")
		tag.Name = "PulseTag"
		tag.Value = "wall"
		tag.Parent = part

		part.Parent = wallFolder
	end

	return wallFolder
end

-- Builds the floor as a grid of tiles that can pulse individually
local function buildFloor(parent: Instance, center: Vector3, roomSize: Vector3, color: Color3)
	local tileSize = MusicConfig.FloorTileSize
	local gap = MusicConfig.FloorTileGap
	local step = tileSize + gap
	local nx = math.floor(roomSize.X / step)
	local nz = math.floor(roomSize.Z / step)
	local floorFolder = Instance.new("Folder")
	floorFolder.Name = "FloorGrid"
	floorFolder.Parent = parent

	local startX = center.X - (nx * step) / 2 + step / 2
	local startZ = center.Z - (nz * step) / 2 + step / 2

	for ix = 0, nx - 1 do
		for iz = 0, nz - 1 do
			local tile = Instance.new("Part")
			tile.Anchored = true
			tile.CanCollide = true
			tile.Size = Vector3.new(tileSize, 0.5, tileSize)
			tile.Material = Enum.Material.SmoothPlastic
			tile.Color = color
			tile.Position = Vector3.new(
				startX + ix * step,
				center.Y,
				startZ + iz * step
			)
			tile.TopSurface = Enum.SurfaceType.Smooth
			tile.BottomSurface = Enum.SurfaceType.Smooth
			tile.Name = "Tile_" .. ix .. "_" .. iz

			local tag = Instance.new("StringValue")
			tag.Name = "PulseTag"
			tag.Value = "floor"
			tag.Parent = tile

			-- Store grid coords for ripple effects
			local coordX = Instance.new("IntValue")
			coordX.Name = "GridX"
			coordX.Value = ix
			coordX.Parent = tile

			local coordZ = Instance.new("IntValue")
			coordZ.Name = "GridZ"
			coordZ.Value = iz
			coordZ.Parent = tile

			tile.Parent = floorFolder
		end
	end

	return floorFolder
end

-- Builds a ceiling with particle emitters (omitted if ceilingOpen)
local function buildCeiling(parent: Instance, center: Vector3, roomSize: Vector3, color: Color3, particleRate: number)
	local ceiling = Instance.new("Part")
	ceiling.Anchored = true
	ceiling.CanCollide = false
	ceiling.Transparency = 0.7
	ceiling.Size = Vector3.new(roomSize.X, 0.5, roomSize.Z)
	ceiling.Position = center + Vector3.new(0, roomSize.Y, 0)
	ceiling.Material = Enum.Material.ForceField
	ceiling.Color = color
	ceiling.Name = "Ceiling"

	local emitter = Instance.new("ParticleEmitter")
	emitter.Rate = particleRate
	emitter.Lifetime = NumberRange.new(2, MusicConfig.MaxParticleLifetime)
	emitter.Speed = NumberRange.new(0.5, 2)
	emitter.SpreadAngle = Vector2.new(180, 180)
	emitter.Color = ColorSequence.new(color)
	emitter.Size = NumberSequence.new({
		NumberSequenceKeypoint.new(0, 0.3),
		NumberSequenceKeypoint.new(0.5, 0.8),
		NumberSequenceKeypoint.new(1, 0),
	})
	emitter.Transparency = NumberSequence.new({
		NumberSequenceKeypoint.new(0, 0.5),
		NumberSequenceKeypoint.new(1, 1),
	})
	emitter.LightEmission = 0.8
	emitter.Parent = ceiling

	local tag = Instance.new("StringValue")
	tag.Name = "PulseTag"
	tag.Value = "ceiling"
	tag.Parent = ceiling

	ceiling.Parent = parent
	return ceiling
end

-- Builds the room entrance portal (archway connecting to lobby)
local function buildPortal(parent: Instance, center: Vector3, direction: Vector3, color: Color3, roomName: string)
	local portalFolder = Instance.new("Folder")
	portalFolder.Name = "Portal"
	portalFolder.Parent = parent

	-- Archway frame
	local pillarHeight = 12
	local pillarWidth = 2
	local archSpan = 8

	local left = center + Vector3.new(-direction.Z, 0, direction.X) * (archSpan / 2)
	local right = center + Vector3.new(direction.Z, 0, -direction.X) * (archSpan / 2)

	for _, pos in {left, right} do
		local pillar = Instance.new("Part")
		pillar.Anchored = true
		pillar.CanCollide = true
		pillar.Size = Vector3.new(pillarWidth, pillarHeight, pillarWidth)
		pillar.Position = pos + Vector3.new(0, pillarHeight / 2, 0)
		pillar.Material = Enum.Material.Neon
		pillar.Color = color
		pillar.Name = "Pillar"
		pillar.Parent = portalFolder
	end

	-- Top bar
	local topBar = Instance.new("Part")
	topBar.Anchored = true
	topBar.CanCollide = true
	topBar.Size = Vector3.new(archSpan + pillarWidth * 2, pillarWidth, pillarWidth)
	topBar.Position = center + Vector3.new(0, pillarHeight + pillarWidth / 2, 0)
	topBar.Material = Enum.Material.Neon
	topBar.Color = color
	topBar.Name = "Arch"

	-- Orient top bar to face the right direction
	local look = direction
	topBar.CFrame = CFrame.new(topBar.Position, topBar.Position + look)
	-- Correct: we want the bar to span perpendicular to the direction
	local cross = Vector3.new(-direction.Z, 0, direction.X)
	topBar.CFrame = CFrame.lookAt(topBar.Position, topBar.Position + cross)
	topBar.Size = Vector3.new(archSpan + pillarWidth * 2, pillarWidth, pillarWidth)
	topBar.Parent = portalFolder

	-- Room name sign
	local sign = Instance.new("Part")
	sign.Anchored = true
	sign.CanCollide = false
	sign.Transparency = 1
	sign.Size = Vector3.new(archSpan, 3, 0.2)
	sign.Position = center + Vector3.new(0, pillarHeight + pillarWidth + 2, 0)
	sign.Name = "RoomSign"

	local gui = Instance.new("SurfaceGui")
	gui.Face = Enum.NormalId.Front
	gui.SizingMode = Enum.SurfaceGuiSizingMode.PixelsPerStud
	gui.PixelsPerStud = 30
	gui.Parent = sign

	local label = Instance.new("TextLabel")
	label.Size = UDim2.new(1, 0, 1, 0)
	label.BackgroundTransparency = 1
	label.Text = roomName
	label.Font = Enum.Font.BuilderSansBold
	label.TextColor3 = color
	label.TextScaled = true
	label.Parent = gui

	sign.CFrame = CFrame.lookAt(sign.Position, sign.Position + direction)
	sign.Parent = portalFolder

	return portalFolder
end

-- Builds a point light in the room center for ambient glow
local function buildAmbientLight(parent: Instance, center: Vector3, color: Color3)
	local lightPart = Instance.new("Part")
	lightPart.Anchored = true
	lightPart.CanCollide = false
	lightPart.Transparency = 1
	lightPart.Size = Vector3.new(1, 1, 1)
	lightPart.Position = center + Vector3.new(0, 15, 0)
	lightPart.Name = "AmbientLightAnchor"

	local light = Instance.new("PointLight")
	light.Color = color
	light.Brightness = 1.5
	light.Range = 50
	light.Parent = lightPart

	local tag = Instance.new("StringValue")
	tag.Name = "PulseTag"
	tag.Value = "light"
	tag.Parent = lightPart

	lightPart.Parent = parent
	return lightPart
end

------------------------------------------------------------------------
-- Build one complete room
------------------------------------------------------------------------
function SoundscapeEngine.buildRoom(roomIndex: number, roomDef: table, worldFolder: Instance): Instance
	local roomFolder = Instance.new("Folder")
	roomFolder.Name = roomDef.name .. " Room"

	-- Room position: hexagonal placement around origin
	local angle = (roomIndex - 1) * (math.pi * 2 / #MusicConfig.Rooms)
	local cx = math.cos(angle) * MusicConfig.LobbyRadius
	local cz = math.sin(angle) * MusicConfig.LobbyRadius
	local center = Vector3.new(cx, MusicConfig.FloorY, cz)

	-- Store center for player proximity checks
	local centerVal = Instance.new("Vector3Value")
	centerVal.Name = "RoomCenter"
	centerVal.Value = center
	centerVal.Parent = roomFolder

	-- Store room index
	local indexVal = Instance.new("IntValue")
	indexVal.Name = "RoomIndex"
	indexVal.Value = roomIndex
	indexVal.Parent = roomFolder

	-- Store mood name
	local moodVal = Instance.new("StringValue")
	moodVal.Name = "Mood"
	moodVal.Value = roomDef.mood
	moodVal.Parent = roomFolder

	local geo = roomDef.geometry
	local vis = roomDef.visuals
	local roomSize = MusicConfig.RoomSize

	-- Direction from origin to room (for portal facing)
	local toRoom = Vector3.new(cx, 0, cz).Unit

	-- Build four walls with waveform geometry
	local halfX = roomSize.X / 2
	local halfZ = roomSize.Z / 2

	-- Wall origins (bottom-left corners when facing each wall)
	local wallDefs = {
		{origin = center + Vector3.new(-halfX, 0, -halfZ), dir = Vector3.new(1, 0, 0), len = roomSize.X},  -- front
		{origin = center + Vector3.new(halfX, 0, -halfZ),  dir = Vector3.new(0, 0, 1), len = roomSize.Z},  -- right
		{origin = center + Vector3.new(halfX, 0, halfZ),   dir = Vector3.new(-1, 0, 0), len = roomSize.X}, -- back
		{origin = center + Vector3.new(-halfX, 0, halfZ),  dir = Vector3.new(0, 0, -1), len = roomSize.Z}, -- left
	}

	for i, wd in wallDefs do
		buildWaveWall(roomFolder, wd.origin, wd.dir, wd.len, roomSize.Y, geo.wallStyle, geo.wallPeriods, vis.baseColor)
	end

	-- Floor
	buildFloor(roomFolder, center, roomSize, vis.baseColor)

	-- Ceiling (unless open)
	if not geo.ceilingOpen then
		buildCeiling(roomFolder, center, roomSize, vis.pulseColor, vis.particleRate)
	else
		-- Open ceiling: floating particle emitters on an invisible part above
		local skyEmitterPart = Instance.new("Part")
		skyEmitterPart.Anchored = true
		skyEmitterPart.CanCollide = false
		skyEmitterPart.Transparency = 1
		skyEmitterPart.Size = Vector3.new(roomSize.X, 1, roomSize.Z)
		skyEmitterPart.Position = center + Vector3.new(0, roomSize.Y + 10, 0)
		skyEmitterPart.Name = "SkyEmitter"

		local emitter = Instance.new("ParticleEmitter")
		emitter.Rate = vis.particleRate * 2
		emitter.Lifetime = NumberRange.new(3, 6)
		emitter.Speed = NumberRange.new(0.2, 1)
		emitter.SpreadAngle = Vector2.new(180, 180)
		emitter.Color = ColorSequence.new(vis.pulseColor)
		emitter.Size = NumberSequence.new({
			NumberSequenceKeypoint.new(0, 0.2),
			NumberSequenceKeypoint.new(0.5, 1.2),
			NumberSequenceKeypoint.new(1, 0),
		})
		emitter.Transparency = NumberSequence.new({
			NumberSequenceKeypoint.new(0, 0.3),
			NumberSequenceKeypoint.new(1, 1),
		})
		emitter.LightEmission = 1
		emitter.Parent = skyEmitterPart

		skyEmitterPart.Parent = roomFolder
	end

	-- Ambient light
	buildAmbientLight(roomFolder, center, vis.pulseColor)

	-- Portal
	local portalPos = center - toRoom * (halfZ + 5)
	buildPortal(roomFolder, portalPos, toRoom, vis.pulseColor, roomDef.name)

	roomFolder.Parent = worldFolder
	return roomFolder
end

------------------------------------------------------------------------
-- Build the central lobby
------------------------------------------------------------------------
function SoundscapeEngine.buildLobby(worldFolder: Instance): Instance
	local lobbyFolder = Instance.new("Folder")
	lobbyFolder.Name = "Lobby"

	local size = MusicConfig.LobbySize
	local center = Vector3.new(0, MusicConfig.FloorY, 0)

	-- Simple floor
	local floor = Instance.new("Part")
	floor.Anchored = true
	floor.CanCollide = true
	floor.Size = Vector3.new(size.X, 1, size.Z)
	floor.Position = center - Vector3.new(0, 0.5, 0)
	floor.Material = Enum.Material.SmoothPlastic
	floor.Color = Color3.fromRGB(60, 60, 60)
	floor.TopSurface = Enum.SurfaceType.Smooth
	floor.BottomSurface = Enum.SurfaceType.Smooth
	floor.Name = "LobbyFloor"
	floor.Parent = lobbyFolder

	-- Central pedestal with title
	local pedestal = Instance.new("Part")
	pedestal.Anchored = true
	pedestal.CanCollide = true
	pedestal.Size = Vector3.new(6, 4, 6)
	pedestal.Position = center + Vector3.new(0, 2, 0)
	pedestal.Material = Enum.Material.Neon
	pedestal.Color = Color3.fromRGB(200, 200, 220)
	pedestal.Shape = Enum.PartType.Cylinder
	pedestal.Name = "Pedestal"

	-- Rotate cylinder upright
	pedestal.CFrame = CFrame.new(pedestal.Position) * CFrame.Angles(0, 0, math.rad(90))
	pedestal.Size = Vector3.new(4, 6, 6) -- height, diameter, diameter after rotation

	local gui = Instance.new("SurfaceGui")
	gui.Face = Enum.NormalId.Top
	gui.SizingMode = Enum.SurfaceGuiSizingMode.PixelsPerStud
	gui.PixelsPerStud = 20
	gui.Parent = pedestal

	local label = Instance.new("TextLabel")
	label.Size = UDim2.new(1, 0, 1, 0)
	label.BackgroundTransparency = 1
	label.Text = "GENERATIVE\nMUSIC ROOMS"
	label.Font = Enum.Font.BuilderSansBold
	label.TextColor3 = Color3.fromRGB(255, 255, 255)
	label.TextScaled = true
	label.Parent = gui

	pedestal.Parent = lobbyFolder

	-- Directional signs pointing to each room
	for i, roomDef in MusicConfig.Rooms do
		local angle = (i - 1) * (math.pi * 2 / #MusicConfig.Rooms)
		local dir = Vector3.new(math.cos(angle), 0, math.sin(angle))
		local signPos = center + dir * 15 + Vector3.new(0, 3, 0)

		local signPart = Instance.new("Part")
		signPart.Anchored = true
		signPart.CanCollide = false
		signPart.Transparency = 0.3
		signPart.Size = Vector3.new(8, 3, 0.3)
		signPart.Material = Enum.Material.Neon
		signPart.Color = roomDef.visuals.baseColor
		signPart.Name = "Sign_" .. roomDef.name
		signPart.CFrame = CFrame.lookAt(signPos, signPos + dir)

		local sGui = Instance.new("SurfaceGui")
		sGui.Face = Enum.NormalId.Front
		sGui.SizingMode = Enum.SurfaceGuiSizingMode.PixelsPerStud
		sGui.PixelsPerStud = 25
		sGui.Parent = signPart

		local sLabel = Instance.new("TextLabel")
		sLabel.Size = UDim2.new(1, 0, 1, 0)
		sLabel.BackgroundTransparency = 1
		sLabel.Text = roomDef.name .. "\n→"
		sLabel.Font = Enum.Font.BuilderSansBold
		sLabel.TextColor3 = roomDef.visuals.pulseColor
		sLabel.TextScaled = true
		sLabel.Parent = sGui

		signPart.Parent = lobbyFolder
	end

	-- Ambient light
	local light = Instance.new("Part")
	light.Anchored = true
	light.CanCollide = false
	light.Transparency = 1
	light.Size = Vector3.new(1, 1, 1)
	light.Position = center + Vector3.new(0, 12, 0)
	light.Name = "LobbyLight"

	local pl = Instance.new("PointLight")
	pl.Color = Color3.fromRGB(200, 200, 220)
	pl.Brightness = 2
	pl.Range = 40
	pl.Parent = light

	light.Parent = lobbyFolder
	lobbyFolder.Parent = worldFolder
	return lobbyFolder
end

------------------------------------------------------------------------
-- Build the full world (lobby + all rooms)
------------------------------------------------------------------------
function SoundscapeEngine.buildWorld(): Instance
	local worldFolder = Instance.new("Folder")
	worldFolder.Name = "MusicWorld"
	worldFolder.Parent = workspace

	SoundscapeEngine.buildLobby(worldFolder)

	for i, roomDef in MusicConfig.Rooms do
		SoundscapeEngine.buildRoom(i, roomDef, worldFolder)
	end

	-- Spawn location in lobby
	local spawn = Instance.new("SpawnLocation")
	spawn.Anchored = true
	spawn.CanCollide = true
	spawn.Size = Vector3.new(8, 1, 8)
	spawn.Position = Vector3.new(0, MusicConfig.FloorY, 0) + MusicConfig.SpawnOffset - Vector3.new(0, 4, 0)
	spawn.Material = Enum.Material.SmoothPlastic
	spawn.Color = Color3.fromRGB(80, 80, 80)
	spawn.TopSurface = Enum.SurfaceType.Smooth
	spawn.BottomSurface = Enum.SurfaceType.Smooth
	spawn.Name = "LobbySpawn"
	spawn.Parent = worldFolder

	return worldFolder
end

return SoundscapeEngine
