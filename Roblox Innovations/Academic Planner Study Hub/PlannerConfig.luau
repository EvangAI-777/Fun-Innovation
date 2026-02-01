--[[
    PlannerConfig.luau
    ModuleScript -- place in ReplicatedStorage

    Shared configuration for the Academic Planner Study Hub.
    Campus layout, assignment display settings, timer values, and DataStore key.
]]

local Config = {}

------------------------------------------------------------------------
-- DataStore
------------------------------------------------------------------------

Config.DataStoreKey = "AcademicPlannerV1"

------------------------------------------------------------------------
-- Campus layout
------------------------------------------------------------------------

-- Lobby (central area)
Config.LobbySize = Vector3.new(120, 1, 120)
Config.LobbyFloorColor = Color3.fromRGB(200, 195, 185) -- warm stone
Config.LobbyFloorMaterial = Enum.Material.Marble

-- Dorm rooms (arranged in a row along the +X side)
Config.DormRoomSize = Vector3.new(24, 16, 20) -- interior dimensions
Config.DormWallThickness = 1
Config.DormWallColor = Color3.fromRGB(235, 225, 210) -- warm cream
Config.DormWallMaterial = Enum.Material.SmoothPlastic
Config.DormFloorColor = Color3.fromRGB(140, 110, 80) -- wood floor
Config.DormFloorMaterial = Enum.Material.Wood
Config.DormSpacing = 4 -- gap between dorm rooms
Config.DormStartX = 70 -- X offset from lobby center
Config.MaxDormRooms = 20

-- Library (large shared building on -X side)
Config.LibrarySize = Vector3.new(80, 20, 60)
Config.LibraryPosition = Vector3.new(-80, 0, 0)
Config.LibraryFloorColor = Color3.fromRGB(180, 170, 155)
Config.LibraryFloorMaterial = Enum.Material.Marble
Config.LibraryWallColor = Color3.fromRGB(190, 180, 165)
Config.LibraryWallMaterial = Enum.Material.Brick
Config.LibraryTableCount = 6

-- Study rooms (small group rooms along -Z side)
Config.StudyRoomSize = Vector3.new(20, 14, 16)
Config.StudyRoomStartZ = -70
Config.MaxStudyRooms = 8

------------------------------------------------------------------------
-- Desk and planner
------------------------------------------------------------------------

Config.DeskSize = Vector3.new(8, 3, 5)
Config.DeskColor = Color3.fromRGB(120, 85, 55) -- dark wood
Config.DeskMaterial = Enum.Material.Wood
Config.DeskLegSize = Vector3.new(0.6, 3, 0.6)

Config.ChairSeatSize = Vector3.new(3, 0.5, 3)
Config.ChairBackSize = Vector3.new(3, 4, 0.5)
Config.ChairColor = Color3.fromRGB(80, 60, 45)
Config.ChairMaterial = Enum.Material.Wood

------------------------------------------------------------------------
-- Sticky notes (physical assignment cards on desk)
------------------------------------------------------------------------

Config.StickyNoteSize = Vector3.new(3, 0.15, 2.5)
Config.StickyNoteMaterial = Enum.Material.SmoothPlastic

-- Status colors
Config.StatusColors = {
    upcoming  = Color3.fromRGB(130, 200, 130), -- green
    dueSoon   = Color3.fromRGB(240, 200, 80),  -- yellow
    overdue   = Color3.fromRGB(220, 90, 80),   -- red
    completed = Color3.fromRGB(160, 160, 170), -- gray
    noDate    = Color3.fromRGB(150, 180, 220), -- light blue
}

-- "Due soon" means within this many seconds
Config.DueSoonThreshold = 86400 * 2 -- 2 days

------------------------------------------------------------------------
-- Assignments
------------------------------------------------------------------------

Config.MaxAssignmentsPerPlayer = 50
Config.MaxClassNameLength = 60
Config.MaxAssignmentNameLength = 100
Config.MaxAbbrevLength = 20

------------------------------------------------------------------------
-- Study groups & timers
------------------------------------------------------------------------

Config.MaxStudyGroups = 8
Config.MaxGroupMembers = 6
Config.MaxTimerDuration = 7200 -- 2 hours in seconds
Config.DefaultTimerDuration = 1500 -- 25 min (pomodoro)

------------------------------------------------------------------------
-- Whiteboard (in study rooms and library)
------------------------------------------------------------------------

Config.WhiteboardSize = Vector3.new(10, 6, 0.3)
Config.WhiteboardColor = Color3.fromRGB(245, 245, 245)
Config.WhiteboardMaterial = Enum.Material.SmoothPlastic
Config.WhiteboardFrameColor = Color3.fromRGB(60, 60, 60)

------------------------------------------------------------------------
-- Interaction
------------------------------------------------------------------------

Config.DeskInteractionRange = 8
Config.WhiteboardInteractionRange = 10
Config.DoorInteractionRange = 10

------------------------------------------------------------------------
-- Course color palette (for study group accents)
------------------------------------------------------------------------

Config.CourseColors = {
    Color3.fromRGB(70, 130, 180),  -- steel blue
    Color3.fromRGB(180, 100, 60),  -- terra cotta
    Color3.fromRGB(100, 160, 90),  -- sage green
    Color3.fromRGB(160, 90, 160),  -- purple
    Color3.fromRGB(200, 160, 60),  -- gold
    Color3.fromRGB(90, 160, 160),  -- teal
    Color3.fromRGB(180, 80, 80),   -- muted red
    Color3.fromRGB(120, 120, 170), -- lavender
}

------------------------------------------------------------------------
-- Spawn
------------------------------------------------------------------------

Config.SpawnPosition = Vector3.new(0, 5, 30) -- lobby center area

return Config
