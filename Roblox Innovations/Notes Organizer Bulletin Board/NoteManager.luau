--[[
    NoteManager.luau
    ModuleScript -- place in ServerStorage

    Handles note CRUD, folder management, serialization for DataStore,
    and building physical note objects in the 3D world.
]]

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Config = require(ReplicatedStorage:WaitForChild("BulletinConfig"))

local NoteManager = {}

------------------------------------------------------------------------
-- Data types
------------------------------------------------------------------------

export type NoteData = {
    id: string,
    title: string,
    body: string,
    folderId: string?,
    isPublic: boolean,
    authorId: number,       -- Player.UserId
    authorName: string,
    position: { x: number, y: number, z: number },
    normal: { x: number, y: number, z: number },  -- Surface normal for orientation
    created: number,        -- os.time()
    modified: number,
}

export type FolderData = {
    id: string,
    name: string,
    themeIndex: number,     -- Index into Config.RoomThemes
}

export type PlayerData = {
    notes: { NoteData },
    folders: { FolderData },
}

------------------------------------------------------------------------
-- ID generation
------------------------------------------------------------------------

local idCounter = 0

function NoteManager.generateId(): string
    idCounter += 1
    return tostring(os.time()) .. "_" .. tostring(idCounter) .. "_" .. tostring(math.random(1000, 9999))
end

------------------------------------------------------------------------
-- Serialization (for DataStore)
------------------------------------------------------------------------

function NoteManager.serialize(playerData: PlayerData): string
    return game:GetService("HttpService"):JSONEncode(playerData)
end

function NoteManager.deserialize(jsonString: string): PlayerData?
    local success, data = pcall(function()
        return game:GetService("HttpService"):JSONDecode(jsonString)
    end)
    if success and data then
        return data :: PlayerData
    end
    return nil
end

function NoteManager.newPlayerData(): PlayerData
    return {
        notes = {},
        folders = {},
    }
end

------------------------------------------------------------------------
-- Build physical note in the world
------------------------------------------------------------------------

--[[
    Create a 3D note object: a framed Part with a SurfaceGui showing
    the title and body text. Returns the Model.
]]
function NoteManager.buildNoteModel(note: NoteData, parentFolder: Folder): Model
    local model = Instance.new("Model")
    model.Name = "Note_" .. note.id

    -- Back frame (the "board" the note is pinned to)
    local frame = Instance.new("Part")
    frame.Name = "Frame"
    frame.Size = Config.NotePartSize + Vector3.new(1, 1, 0)
    frame.Anchored = true
    frame.CanCollide = true
    frame.Material = Config.NoteFrameMaterial
    frame.Color = Config.NoteFrameColor

    -- Position from saved data
    local pos = Vector3.new(note.position.x, note.position.y, note.position.z)
    local normal = Vector3.new(note.normal.x, note.normal.y, note.normal.z)

    -- Orient the note to face outward from the surface
    local lookAt = pos + normal
    frame.CFrame = CFrame.lookAt(pos, lookAt)

    frame.Parent = model

    -- Note surface (the "paper")
    local surface = Instance.new("Part")
    surface.Name = "Surface"
    surface.Size = Config.NotePartSize
    surface.Anchored = true
    surface.CanCollide = false
    surface.Material = Config.NoteMaterial
    surface.Color = Config.NoteSurfaceColor
    surface.CFrame = frame.CFrame + normal * 0.2  -- Slightly in front of frame

    -- SurfaceGui for text
    local gui = Instance.new("SurfaceGui")
    gui.Name = "NoteGui"
    gui.Face = Enum.NormalId.Front
    gui.SizingMode = Enum.SurfaceGuiSizingMode.PixelsPerStud
    gui.PixelsPerStud = 32
    gui.LightInfluence = 0.3
    gui.Brightness = 1
    gui.Parent = surface

    -- Title label
    local titleLabel = Instance.new("TextLabel")
    titleLabel.Name = "Title"
    titleLabel.Size = UDim2.new(1, -20, 0, 40)
    titleLabel.Position = UDim2.new(0, 10, 0, 8)
    titleLabel.BackgroundTransparency = 1
    titleLabel.Text = note.title
    titleLabel.TextColor3 = Config.TitleColor
    titleLabel.TextSize = Config.TitleTextSize
    titleLabel.Font = Enum.Font.GothamBold
    titleLabel.TextXAlignment = Enum.TextXAlignment.Left
    titleLabel.TextTruncate = Enum.TextTruncate.AtEnd
    titleLabel.Parent = gui

    -- Divider line
    local divider = Instance.new("Frame")
    divider.Name = "Divider"
    divider.Size = UDim2.new(1, -20, 0, 1)
    divider.Position = UDim2.new(0, 10, 0, 50)
    divider.BackgroundColor3 = Color3.fromRGB(180, 175, 165)
    divider.BorderSizePixel = 0
    divider.Parent = gui

    -- Body label
    local bodyText = note.body
    if #bodyText > Config.MaxBodyLength then
        bodyText = string.sub(bodyText, 1, Config.MaxBodyLength) .. "..."
    end

    local bodyLabel = Instance.new("TextLabel")
    bodyLabel.Name = "Body"
    bodyLabel.Size = UDim2.new(1, -20, 1, -65)
    bodyLabel.Position = UDim2.new(0, 10, 0, 56)
    bodyLabel.BackgroundTransparency = 1
    bodyLabel.Text = bodyText
    bodyLabel.TextColor3 = Config.BodyColor
    bodyLabel.TextSize = Config.BodyTextSize
    bodyLabel.Font = Enum.Font.Gotham
    bodyLabel.TextXAlignment = Enum.TextXAlignment.Left
    bodyLabel.TextYAlignment = Enum.TextYAlignment.Top
    bodyLabel.TextWrapped = true
    bodyLabel.Parent = gui

    -- Author label (bottom)
    local authorLabel = Instance.new("TextLabel")
    authorLabel.Name = "Author"
    authorLabel.Size = UDim2.new(1, -20, 0, 20)
    authorLabel.Position = UDim2.new(0, 10, 1, -24)
    authorLabel.BackgroundTransparency = 1
    authorLabel.Text = "- " .. note.authorName
    authorLabel.TextColor3 = Color3.fromRGB(140, 135, 125)
    authorLabel.TextSize = 14
    authorLabel.Font = Enum.Font.Gotham
    authorLabel.TextXAlignment = Enum.TextXAlignment.Right
    authorLabel.Parent = gui

    surface.Parent = model

    -- Proximity prompt for interaction
    local prompt = Instance.new("ProximityPrompt")
    prompt.Name = "ReadPrompt"
    prompt.ActionText = "Read Note"
    prompt.ObjectText = note.title
    prompt.MaxActivationDistance = Config.InteractionRange
    prompt.HoldDuration = Config.ProximityPromptHoldTime
    prompt.Parent = frame

    -- Store metadata as attributes
    frame:SetAttribute("NoteId", note.id)
    frame:SetAttribute("AuthorId", note.authorId)
    frame:SetAttribute("IsPublic", note.isPublic)
    frame:SetAttribute("FolderId", note.folderId or "")

    -- Handle private note visibility
    if not note.isPublic then
        surface.Transparency = Config.PrivateNoteTransparency
        frame.Transparency = Config.PrivateNoteTransparency * 0.5
    end

    model.PrimaryPart = frame
    model.Parent = parentFolder

    return model
end

------------------------------------------------------------------------
-- Build a room (folder)
------------------------------------------------------------------------

function NoteManager.buildRoom(folder: FolderData, gridIndex: number): Model
    local theme = Config.RoomThemes[((folder.themeIndex - 1) % #Config.RoomThemes) + 1]
    local roomModel = Instance.new("Model")
    roomModel.Name = "Room_" .. folder.id

    -- Calculate room position in grid
    local cols = 4
    local row = math.floor((gridIndex - 1) / cols)
    local col = (gridIndex - 1) % cols
    local centerX = Config.LobbySize.X / 2 + Config.RoomSpacing + col * Config.RoomSpacing
    local centerZ = row * Config.RoomSpacing
    local centerY = Config.RoomSize.Y / 2

    local roomCenter = Vector3.new(centerX, centerY, centerZ)
    local rs = Config.RoomSize
    local wt = Config.WallThickness

    -- Floor
    local floor = Instance.new("Part")
    floor.Name = "Floor"
    floor.Size = Vector3.new(rs.X, wt, rs.Z)
    floor.Position = Vector3.new(centerX, 0, centerZ)
    floor.Anchored = true
    floor.Material = Config.FloorMaterial
    floor.Color = Config.FloorColor
    floor.TopSurface = Enum.SurfaceType.Smooth
    floor.Parent = roomModel

    -- Ceiling
    local ceiling = Instance.new("Part")
    ceiling.Name = "Ceiling"
    ceiling.Size = Vector3.new(rs.X, wt, rs.Z)
    ceiling.Position = Vector3.new(centerX, rs.Y, centerZ)
    ceiling.Anchored = true
    ceiling.Material = Config.WallMaterial
    ceiling.Color = Config.CeilingColor
    ceiling.Parent = roomModel

    -- Walls (4 walls, front wall has a door opening)
    local wallDefs = {
        { name = "WallLeft",  size = Vector3.new(wt, rs.Y, rs.Z), pos = Vector3.new(centerX - rs.X/2, centerY, centerZ) },
        { name = "WallRight", size = Vector3.new(wt, rs.Y, rs.Z), pos = Vector3.new(centerX + rs.X/2, centerY, centerZ) },
        { name = "WallBack",  size = Vector3.new(rs.X, rs.Y, wt), pos = Vector3.new(centerX, centerY, centerZ + rs.Z/2) },
    }

    for _, wd in wallDefs do
        local wall = Instance.new("Part")
        wall.Name = wd.name
        wall.Size = wd.size
        wall.Position = wd.pos
        wall.Anchored = true
        wall.Material = Config.WallMaterial
        wall.Color = Config.WallColor
        wall.Parent = roomModel
    end

    -- Front wall with door (split into two parts + header above door)
    local frontZ = centerZ - rs.Z / 2
    local doorHalfW = Config.DoorWidth / 2
    local sideWidth = (rs.X - Config.DoorWidth) / 2

    -- Left side of door
    local frontLeft = Instance.new("Part")
    frontLeft.Name = "WallFrontLeft"
    frontLeft.Size = Vector3.new(sideWidth, rs.Y, wt)
    frontLeft.Position = Vector3.new(centerX - rs.X/2 + sideWidth/2, centerY, frontZ)
    frontLeft.Anchored = true
    frontLeft.Material = Config.WallMaterial
    frontLeft.Color = Config.WallColor
    frontLeft.Parent = roomModel

    -- Right side of door
    local frontRight = Instance.new("Part")
    frontRight.Name = "WallFrontRight"
    frontRight.Size = Vector3.new(sideWidth, rs.Y, wt)
    frontRight.Position = Vector3.new(centerX + rs.X/2 - sideWidth/2, centerY, frontZ)
    frontRight.Anchored = true
    frontRight.Material = Config.WallMaterial
    frontRight.Color = Config.WallColor
    frontRight.Parent = roomModel

    -- Above door
    local aboveDoor = Instance.new("Part")
    aboveDoor.Name = "AboveDoor"
    aboveDoor.Size = Vector3.new(Config.DoorWidth, rs.Y - Config.DoorHeight, wt)
    aboveDoor.Position = Vector3.new(centerX, Config.DoorHeight + (rs.Y - Config.DoorHeight)/2, frontZ)
    aboveDoor.Anchored = true
    aboveDoor.Material = Config.WallMaterial
    aboveDoor.Color = Config.WallColor
    aboveDoor.Parent = roomModel

    -- Room name sign above door
    local sign = Instance.new("Part")
    sign.Name = "RoomSign"
    sign.Size = Vector3.new(Config.DoorWidth + 4, 3, 0.3)
    sign.Position = Vector3.new(centerX, Config.DoorHeight + 2, frontZ - 0.5)
    sign.Anchored = true
    sign.CanCollide = false
    sign.Material = Enum.Material.SmoothPlastic
    sign.Color = theme.accent
    sign.Parent = roomModel

    local signGui = Instance.new("SurfaceGui")
    signGui.Face = Enum.NormalId.Front
    signGui.SizingMode = Enum.SurfaceGuiSizingMode.PixelsPerStud
    signGui.PixelsPerStud = 24
    signGui.Parent = sign

    local signLabel = Instance.new("TextLabel")
    signLabel.Size = UDim2.new(1, 0, 1, 0)
    signLabel.BackgroundTransparency = 1
    signLabel.Text = folder.name
    signLabel.TextColor3 = Color3.fromRGB(255, 255, 255)
    signLabel.TextSize = 36
    signLabel.Font = Enum.Font.GothamBold
    signLabel.Parent = signGui

    -- Room light
    local light = Instance.new("PointLight")
    light.Color = Config.RoomLightColor
    light.Brightness = Config.RoomLightBrightness
    light.Range = Config.RoomLightRange
    light.Parent = ceiling

    -- Accent stripe along the top of each wall
    local accentHeight = 0.5
    local accentParts = {
        { size = Vector3.new(wt + 0.1, accentHeight, rs.Z), pos = Vector3.new(centerX - rs.X/2, rs.Y - accentHeight/2, centerZ) },
        { size = Vector3.new(wt + 0.1, accentHeight, rs.Z), pos = Vector3.new(centerX + rs.X/2, rs.Y - accentHeight/2, centerZ) },
        { size = Vector3.new(rs.X, accentHeight, wt + 0.1), pos = Vector3.new(centerX, rs.Y - accentHeight/2, centerZ + rs.Z/2) },
        { size = Vector3.new(rs.X, accentHeight, wt + 0.1), pos = Vector3.new(centerX, rs.Y - accentHeight/2, frontZ) },
    }
    for i, ap in accentParts do
        local accent = Instance.new("Part")
        accent.Name = "Accent_" .. i
        accent.Size = ap.size
        accent.Position = ap.pos
        accent.Anchored = true
        accent.CanCollide = false
        accent.Material = Enum.Material.Neon
        accent.Color = theme.accent
        accent.Parent = roomModel
    end

    -- Store room metadata
    roomModel:SetAttribute("FolderId", folder.id)
    roomModel:SetAttribute("FolderName", folder.name)
    roomModel:SetAttribute("ThemeIndex", folder.themeIndex)

    roomModel.Parent = workspace
    return roomModel
end

------------------------------------------------------------------------
-- Build the lobby (shared public space)
------------------------------------------------------------------------

function NoteManager.buildLobby(): Model
    local lobbyModel = Instance.new("Model")
    lobbyModel.Name = "Lobby"

    local ls = Config.LobbySize
    local centerY = ls.Y / 2

    -- Floor
    local floor = Instance.new("Part")
    floor.Name = "LobbyFloor"
    floor.Size = Vector3.new(ls.X, 1, ls.Z)
    floor.Position = Vector3.new(0, 0, 0)
    floor.Anchored = true
    floor.Material = Enum.Material.Marble
    floor.Color = Color3.fromRGB(45, 48, 55)
    floor.TopSurface = Enum.SurfaceType.Smooth
    floor.Parent = lobbyModel

    -- Ceiling with lights
    local ceiling = Instance.new("Part")
    ceiling.Name = "LobbyCeiling"
    ceiling.Size = Vector3.new(ls.X, 1, ls.Z)
    ceiling.Position = Vector3.new(0, ls.Y, 0)
    ceiling.Anchored = true
    ceiling.Material = Enum.Material.SmoothPlastic
    ceiling.Color = Color3.fromRGB(50, 52, 58)
    ceiling.Parent = lobbyModel

    -- Central light
    local mainLight = Instance.new("PointLight")
    mainLight.Color = Color3.fromRGB(255, 250, 235)
    mainLight.Brightness = 1.5
    mainLight.Range = 60
    mainLight.Parent = ceiling

    -- Lobby sign (floating text)
    local signPart = Instance.new("Part")
    signPart.Name = "LobbySign"
    signPart.Size = Vector3.new(30, 4, 0.3)
    signPart.Position = Vector3.new(0, ls.Y - 4, -ls.Z / 2 + 2)
    signPart.Anchored = true
    signPart.CanCollide = false
    signPart.Transparency = 1
    signPart.Parent = lobbyModel

    local signGui = Instance.new("SurfaceGui")
    signGui.Face = Enum.NormalId.Front
    signGui.SizingMode = Enum.SurfaceGuiSizingMode.PixelsPerStud
    signGui.PixelsPerStud = 20
    signGui.Parent = signPart

    local signLabel = Instance.new("TextLabel")
    signLabel.Size = UDim2.new(1, 0, 1, 0)
    signLabel.BackgroundTransparency = 1
    signLabel.Text = "BULLETIN BOARD"
    signLabel.TextColor3 = Color3.fromRGB(200, 195, 180)
    signLabel.TextSize = 48
    signLabel.Font = Enum.Font.GothamBold
    signLabel.Parent = signGui

    -- Spawn
    local spawn = Instance.new("SpawnLocation")
    spawn.Size = Vector3.new(12, 1, 12)
    spawn.Position = Config.SpawnPosition
    spawn.Anchored = true
    spawn.CanCollide = false
    spawn.Transparency = 1
    spawn.Parent = lobbyModel

    lobbyModel:SetAttribute("IsLobby", true)
    lobbyModel.Parent = workspace

    return lobbyModel
end

return NoteManager
