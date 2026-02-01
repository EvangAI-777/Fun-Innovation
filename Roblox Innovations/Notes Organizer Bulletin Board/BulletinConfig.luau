--[[
    BulletinConfig.luau
    ModuleScript -- place in ReplicatedStorage

    Shared configuration for Notes Organizer Bulletin Board.
]]

local Config = {}

-- Note display settings
Config.NotePartSize = Vector3.new(8, 6, 0.3)       -- Physical note frame size
Config.NoteFrameColor = Color3.fromRGB(45, 40, 35)  -- Dark wood-ish frame
Config.NoteSurfaceColor = Color3.fromRGB(250, 245, 230)  -- Paper-white surface
Config.NoteMaterial = Enum.Material.SmoothPlastic
Config.NoteFrameMaterial = Enum.Material.Wood

-- Text settings for SurfaceGui
Config.TitleTextSize = 28
Config.BodyTextSize = 18
Config.TitleColor = Color3.fromRGB(30, 30, 30)
Config.BodyColor = Color3.fromRGB(50, 50, 50)
Config.MaxBodyLength = 500  -- Characters; truncate on the physical note

-- Placement settings
Config.PlacementRange = 30       -- Max studs from player to place a note
Config.SnapToSurface = true      -- Snap notes to wall/floor surfaces
Config.PlacementOffset = 0.2     -- Studs offset from surface to avoid z-fighting

-- Room settings (folders = rooms)
Config.RoomSize = Vector3.new(60, 20, 60)   -- Interior dimensions of each room
Config.WallThickness = 1
Config.WallColor = Color3.fromRGB(55, 60, 70)
Config.FloorColor = Color3.fromRGB(35, 38, 45)
Config.CeilingColor = Color3.fromRGB(40, 42, 50)
Config.WallMaterial = Enum.Material.Concrete
Config.FloorMaterial = Enum.Material.SmoothPlastic

-- Room layout: rooms are arranged in a grid
Config.RoomSpacing = 80          -- Distance between room centers
Config.MaxRooms = 12             -- Max folders/rooms per player
Config.DoorWidth = 6
Config.DoorHeight = 10

-- Lobby (shared public space)
Config.LobbySize = Vector3.new(100, 24, 100)
Config.LobbyPosition = Vector3.new(0, 0, 0)

-- Lighting per room
Config.RoomLightColor = Color3.fromRGB(255, 245, 220)
Config.RoomLightBrightness = 1.2
Config.RoomLightRange = 40

-- DataStore keys
Config.DataStoreKey = "BulletinBoardData_v1"
Config.MaxNotesPerPlayer = 50

-- Note visibility
Config.PublicByDefault = true     -- New notes start as public
Config.PrivateNoteTransparency = 0.6  -- How faded private notes look to others

-- Interaction
Config.InteractionRange = 12     -- How close you need to be to read/edit a note
Config.ProximityPromptHoldTime = 0.3

-- Colors for folder/room themes (cycle through these)
Config.RoomThemes = {
    { accent = Color3.fromRGB(80, 120, 180), name = "Blue" },
    { accent = Color3.fromRGB(120, 180, 80), name = "Green" },
    { accent = Color3.fromRGB(180, 120, 80), name = "Amber" },
    { accent = Color3.fromRGB(160, 80, 160), name = "Purple" },
    { accent = Color3.fromRGB(80, 170, 170), name = "Teal" },
    { accent = Color3.fromRGB(200, 80, 80),  name = "Red" },
    { accent = Color3.fromRGB(180, 170, 80), name = "Gold" },
    { accent = Color3.fromRGB(100, 100, 140), name = "Slate" },
}

-- Spawn
Config.SpawnPosition = Vector3.new(0, 5, 0)

return Config
