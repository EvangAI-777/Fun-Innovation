--[[
    AssignmentManager.luau
    ModuleScript -- place in ServerStorage

    Builds all physical campus geometry: lobby, dorm rooms, library,
    study rooms, desks, chairs, sticky notes, whiteboards, and timers.
    Also handles data serialization and syllabus text parsing.
]]

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Config = require(ReplicatedStorage:WaitForChild("PlannerConfig"))

local Manager = {}

------------------------------------------------------------------------
-- ID generation
------------------------------------------------------------------------

local idCounter = 0

function Manager.generateId(): string
    idCounter += 1
    return tostring(os.time()) .. "_" .. tostring(idCounter) .. "_" .. tostring(math.random(1000, 9999))
end

------------------------------------------------------------------------
-- New player data
------------------------------------------------------------------------

function Manager.newPlayerData()
    return {
        assignments = {},
        dormIndex = nil, -- assigned on join
    }
end

------------------------------------------------------------------------
-- Serialization
------------------------------------------------------------------------

function Manager.serialize(data: any): string
    -- Convert to a JSON-safe table
    local out = {
        assignments = {},
    }

    for _, a in data.assignments do
        table.insert(out.assignments, {
            id = a.id,
            abbreviation = a.abbreviation,
            className = a.className,
            assignment = a.assignment,
            dueDate = a.dueDate,
            dueTime = a.dueTime,
            completed = a.completed,
            created = a.created,
        })
    end

    local HttpService = game:GetService("HttpService")
    return HttpService:JSONEncode(out)
end

function Manager.deserialize(str: string): any?
    local HttpService = game:GetService("HttpService")
    local ok, parsed = pcall(function()
        return HttpService:JSONDecode(str)
    end)
    if not ok or type(parsed) ~= "table" then return nil end

    local data = Manager.newPlayerData()

    if type(parsed.assignments) == "table" then
        for _, a in parsed.assignments do
            if type(a) == "table" and type(a.id) == "string" then
                table.insert(data.assignments, {
                    id = a.id,
                    abbreviation = a.abbreviation or "",
                    className = a.className or "",
                    assignment = a.assignment or "",
                    dueDate = a.dueDate or "",
                    dueTime = a.dueTime or "",
                    completed = a.completed == true,
                    created = a.created or os.time(),
                })
            end
        end
    end

    return data
end

------------------------------------------------------------------------
-- Helper: make a Part
------------------------------------------------------------------------

local function makePart(props: { [string]: any }): Part
    local part = Instance.new("Part")
    part.Anchored = true
    part.CanCollide = if props.CanCollide ~= nil then props.CanCollide else true
    part.Size = props.Size or Vector3.new(1, 1, 1)
    part.Position = props.Position or Vector3.zero
    part.Color = props.Color or Color3.new(1, 1, 1)
    part.Material = props.Material or Enum.Material.SmoothPlastic
    part.TopSurface = Enum.SurfaceType.Smooth
    part.BottomSurface = Enum.SurfaceType.Smooth
    part.Name = props.Name or "Part"
    part.Parent = props.Parent
    return part
end

------------------------------------------------------------------------
-- Helper: make a SurfaceGui with a TextLabel
------------------------------------------------------------------------

local function makeSurfaceText(parent: Part, face: Enum.NormalId, text: string, textSize: number, textColor: Color3?): TextLabel
    local gui = Instance.new("SurfaceGui")
    gui.Face = face
    gui.SizingMode = Enum.SurfaceGuiSizingMode.PixelsPerStud
    gui.PixelsPerStud = 40
    gui.Parent = parent

    local label = Instance.new("TextLabel")
    label.Size = UDim2.new(1, 0, 1, 0)
    label.BackgroundTransparency = 1
    label.TextColor3 = textColor or Color3.new(1, 1, 1)
    label.Text = text
    label.TextScaled = false
    label.TextSize = textSize
    label.Font = Enum.Font.GothamBold
    label.TextWrapped = true
    label.TextXAlignment = Enum.TextXAlignment.Center
    label.TextYAlignment = Enum.TextYAlignment.Center
    label.Parent = gui

    return label
end

------------------------------------------------------------------------
-- Build lobby
------------------------------------------------------------------------

function Manager.buildLobby(): Folder
    local folder = Instance.new("Folder")
    folder.Name = "CampusLobby"
    folder.Parent = workspace

    -- Floor
    makePart({
        Name = "LobbyFloor",
        Size = Config.LobbySize,
        Position = Vector3.new(0, -0.5, 0),
        Color = Config.LobbyFloorColor,
        Material = Config.LobbyFloorMaterial,
        Parent = folder,
    })

    -- Title sign
    local sign = makePart({
        Name = "LobbySign",
        Size = Vector3.new(20, 4, 0.5),
        Position = Vector3.new(0, 12, -55),
        Color = Color3.fromRGB(60, 50, 40),
        Material = Enum.Material.Slate,
        Parent = folder,
    })
    makeSurfaceText(sign, Enum.NormalId.Front, "STUDY HUB", 60, Color3.fromRGB(255, 240, 200))
    makeSurfaceText(sign, Enum.NormalId.Back, "STUDY HUB", 60, Color3.fromRGB(255, 240, 200))

    -- Directional signs
    local dormSign = makePart({
        Name = "DormSign",
        Size = Vector3.new(8, 2, 0.3),
        Position = Vector3.new(45, 8, 0),
        Color = Color3.fromRGB(60, 50, 40),
        Material = Enum.Material.Slate,
        Parent = folder,
    })
    makeSurfaceText(dormSign, Enum.NormalId.Front, "DORMS -->", 30, Color3.fromRGB(255, 240, 200))

    local libSign = makePart({
        Name = "LibrarySign",
        Size = Vector3.new(8, 2, 0.3),
        Position = Vector3.new(-45, 8, 0),
        Color = Color3.fromRGB(60, 50, 40),
        Material = Enum.Material.Slate,
        Parent = folder,
    })
    makeSurfaceText(libSign, Enum.NormalId.Front, "<-- LIBRARY", 30, Color3.fromRGB(255, 240, 200))

    local studySign = makePart({
        Name = "StudyRoomSign",
        Size = Vector3.new(8, 2, 0.3),
        Position = Vector3.new(0, 8, -45),
        Color = Color3.fromRGB(60, 50, 40),
        Material = Enum.Material.Slate,
        Parent = folder,
    })
    makeSurfaceText(studySign, Enum.NormalId.Front, "STUDY ROOMS", 28, Color3.fromRGB(255, 240, 200))

    -- Spawn location
    local spawn = Instance.new("SpawnLocation")
    spawn.Anchored = true
    spawn.CanCollide = false
    spawn.Transparency = 1
    spawn.Size = Vector3.new(6, 1, 6)
    spawn.Position = Config.SpawnPosition
    spawn.Parent = folder

    -- Ambient lighting
    local atmosphere = Instance.new("Atmosphere")
    atmosphere.Density = 0.2
    atmosphere.Offset = 0.5
    atmosphere.Color = Color3.fromRGB(200, 210, 230)
    atmosphere.Decay = Color3.fromRGB(180, 170, 160)
    atmosphere.Glare = 0.2
    atmosphere.Haze = 1
    atmosphere.Parent = game:GetService("Lighting")

    -- Warm daytime lighting
    local lighting = game:GetService("Lighting")
    lighting.ClockTime = 10 -- morning
    lighting.Brightness = 2
    lighting.Ambient = Color3.fromRGB(80, 75, 70)
    lighting.OutdoorAmbient = Color3.fromRGB(120, 115, 110)

    return folder
end

------------------------------------------------------------------------
-- Build a dorm room
------------------------------------------------------------------------

function Manager.buildDormRoom(dormIndex: number, playerName: string): Model
    local model = Instance.new("Model")
    model.Name = "Dorm_" .. dormIndex

    local rs = Config.DormRoomSize
    local wt = Config.DormWallThickness

    -- Position: rooms line up along +X axis, staggered in Z
    local baseX = Config.DormStartX + (dormIndex - 1) * (rs.X + Config.DormSpacing)
    local baseY = 0
    local baseZ = 0

    -- Floor
    makePart({
        Name = "DormFloor",
        Size = Vector3.new(rs.X, wt, rs.Z),
        Position = Vector3.new(baseX, baseY, baseZ),
        Color = Config.DormFloorColor,
        Material = Config.DormFloorMaterial,
        Parent = model,
    })

    -- Ceiling
    makePart({
        Name = "DormCeiling",
        Size = Vector3.new(rs.X, wt, rs.Z),
        Position = Vector3.new(baseX, baseY + rs.Y, baseZ),
        Color = Config.DormWallColor,
        Material = Config.DormWallMaterial,
        Parent = model,
    })

    -- Ceiling light
    local ceilingLight = makePart({
        Name = "CeilingLight",
        Size = Vector3.new(4, 0.3, 4),
        Position = Vector3.new(baseX, baseY + rs.Y - 0.5, baseZ),
        Color = Color3.fromRGB(255, 250, 230),
        Material = Enum.Material.Neon,
        CanCollide = false,
        Parent = model,
    })
    local pointLight = Instance.new("PointLight")
    pointLight.Brightness = 1.5
    pointLight.Range = 30
    pointLight.Color = Color3.fromRGB(255, 245, 220)
    pointLight.Parent = ceilingLight

    -- Back wall (-Z)
    makePart({
        Name = "WallBack",
        Size = Vector3.new(rs.X, rs.Y, wt),
        Position = Vector3.new(baseX, baseY + rs.Y / 2, baseZ - rs.Z / 2),
        Color = Config.DormWallColor,
        Material = Config.DormWallMaterial,
        Parent = model,
    })

    -- Left wall (-X) - solid
    makePart({
        Name = "WallLeft",
        Size = Vector3.new(wt, rs.Y, rs.Z),
        Position = Vector3.new(baseX - rs.X / 2, baseY + rs.Y / 2, baseZ),
        Color = Config.DormWallColor,
        Material = Config.DormWallMaterial,
        Parent = model,
    })

    -- Right wall (+X) - solid
    makePart({
        Name = "WallRight",
        Size = Vector3.new(wt, rs.Y, rs.Z),
        Position = Vector3.new(baseX + rs.X / 2, baseY + rs.Y / 2, baseZ),
        Color = Config.DormWallColor,
        Material = Config.DormWallMaterial,
        Parent = model,
    })

    -- Front wall (+Z) with door gap
    local doorWidth = 5
    local doorHeight = 9
    -- Left portion
    local leftWidth = (rs.X - doorWidth) / 2
    makePart({
        Name = "WallFrontLeft",
        Size = Vector3.new(leftWidth, rs.Y, wt),
        Position = Vector3.new(baseX - doorWidth / 2 - leftWidth / 2, baseY + rs.Y / 2, baseZ + rs.Z / 2),
        Color = Config.DormWallColor,
        Material = Config.DormWallMaterial,
        Parent = model,
    })
    -- Right portion
    makePart({
        Name = "WallFrontRight",
        Size = Vector3.new(leftWidth, rs.Y, wt),
        Position = Vector3.new(baseX + doorWidth / 2 + leftWidth / 2, baseY + rs.Y / 2, baseZ + rs.Z / 2),
        Color = Config.DormWallColor,
        Material = Config.DormWallMaterial,
        Parent = model,
    })
    -- Above door
    makePart({
        Name = "WallFrontAbove",
        Size = Vector3.new(doorWidth, rs.Y - doorHeight, wt),
        Position = Vector3.new(baseX, baseY + doorHeight + (rs.Y - doorHeight) / 2, baseZ + rs.Z / 2),
        Color = Config.DormWallColor,
        Material = Config.DormWallMaterial,
        Parent = model,
    })

    -- Door sign
    local doorSign = makePart({
        Name = "DoorSign",
        Size = Vector3.new(6, 2, 0.2),
        Position = Vector3.new(baseX, baseY + doorHeight + 1.5, baseZ + rs.Z / 2 + 0.6),
        Color = Color3.fromRGB(60, 50, 40),
        Material = Enum.Material.Slate,
        Parent = model,
    })
    makeSurfaceText(doorSign, Enum.NormalId.Front, playerName .. "'s Room", 28, Color3.fromRGB(255, 240, 200))

    -- Desk (centered against back wall)
    local deskTop = makePart({
        Name = "DeskTop",
        Size = Config.DeskSize,
        Position = Vector3.new(baseX, baseY + Config.DeskSize.Y + Config.DeskLegSize.Y, baseZ - rs.Z / 2 + Config.DeskSize.Z / 2 + 2),
        Color = Config.DeskColor,
        Material = Config.DeskMaterial,
        Parent = model,
    })

    -- Desk legs (4 corners)
    local legOffsets = {
        Vector3.new(-Config.DeskSize.X / 2 + 0.4, 0, -Config.DeskSize.Z / 2 + 0.4),
        Vector3.new(Config.DeskSize.X / 2 - 0.4, 0, -Config.DeskSize.Z / 2 + 0.4),
        Vector3.new(-Config.DeskSize.X / 2 + 0.4, 0, Config.DeskSize.Z / 2 - 0.4),
        Vector3.new(Config.DeskSize.X / 2 - 0.4, 0, Config.DeskSize.Z / 2 - 0.4),
    }
    for i, offset in legOffsets do
        makePart({
            Name = "DeskLeg" .. i,
            Size = Config.DeskLegSize,
            Position = deskTop.Position + offset + Vector3.new(0, -(Config.DeskSize.Y / 2 + Config.DeskLegSize.Y / 2), 0),
            Color = Config.DeskColor,
            Material = Config.DeskMaterial,
            Parent = model,
        })
    end

    -- Chair
    local chairY = baseY + Config.ChairSeatSize.Y / 2 + 1.5
    local chairZ = deskTop.Position.Z + Config.DeskSize.Z / 2 + 2
    makePart({
        Name = "ChairSeat",
        Size = Config.ChairSeatSize,
        Position = Vector3.new(baseX, chairY, chairZ),
        Color = Config.ChairColor,
        Material = Config.ChairMaterial,
        Parent = model,
    })
    makePart({
        Name = "ChairBack",
        Size = Config.ChairBackSize,
        Position = Vector3.new(baseX, chairY + Config.ChairBackSize.Y / 2, chairZ + Config.ChairSeatSize.Z / 2),
        Color = Config.ChairColor,
        Material = Config.ChairMaterial,
        Parent = model,
    })

    -- Store desk reference info as attributes
    deskTop:SetAttribute("IsPlannerDesk", true)
    deskTop:SetAttribute("DormIndex", dormIndex)

    -- ProximityPrompt on desk
    local prompt = Instance.new("ProximityPrompt")
    prompt.ActionText = "Open Planner"
    prompt.ObjectText = "Desk"
    prompt.MaxActivationDistance = Config.DeskInteractionRange
    prompt.HoldDuration = 0
    prompt.Parent = deskTop

    model.Parent = workspace
    return model
end

------------------------------------------------------------------------
-- Build sticky note on desk
------------------------------------------------------------------------

function Manager.buildStickyNote(assignment: any, deskPart: Part, slotIndex: number): Part
    -- Arrange notes in a grid on the desk surface
    local cols = 2
    local row = math.floor((slotIndex - 1) / cols)
    local col = (slotIndex - 1) % cols

    local noteWidth = Config.StickyNoteSize.X
    local noteDepth = Config.StickyNoteSize.Z
    local padX = 0.3
    local padZ = 0.3

    local startX = -(cols * (noteWidth + padX) - padX) / 2 + noteWidth / 2
    local startZ = -(noteDepth + padZ) + noteDepth / 2

    local offsetX = startX + col * (noteWidth + padX)
    local offsetZ = startZ - row * (noteDepth + padZ)

    local deskPos = deskPart.Position
    local noteY = deskPos.Y + Config.DeskSize.Y / 2 + Config.StickyNoteSize.Y / 2

    -- Determine status color
    local statusColor = Config.StatusColors.noDate
    if assignment.completed then
        statusColor = Config.StatusColors.completed
    elseif assignment.dueDate and assignment.dueDate ~= "" then
        local dueTimestamp = Manager.parseDateToTimestamp(assignment.dueDate, assignment.dueTime)
        if dueTimestamp then
            local now = os.time()
            if dueTimestamp < now then
                statusColor = Config.StatusColors.overdue
            elseif dueTimestamp - now < Config.DueSoonThreshold then
                statusColor = Config.StatusColors.dueSoon
            else
                statusColor = Config.StatusColors.upcoming
            end
        end
    end

    local note = makePart({
        Name = "StickyNote_" .. assignment.id,
        Size = Config.StickyNoteSize,
        Position = Vector3.new(deskPos.X + offsetX, noteY, deskPos.Z + offsetZ),
        Color = statusColor,
        Material = Config.StickyNoteMaterial,
        CanCollide = false,
        Parent = deskPart.Parent, -- same model as desk
    })

    -- Top face: abbreviation + assignment name
    local topGui = Instance.new("SurfaceGui")
    topGui.Face = Enum.NormalId.Top
    topGui.SizingMode = Enum.SurfaceGuiSizingMode.PixelsPerStud
    topGui.PixelsPerStud = 50
    topGui.Parent = note

    local topFrame = Instance.new("Frame")
    topFrame.Size = UDim2.new(1, 0, 1, 0)
    topFrame.BackgroundTransparency = 1
    topFrame.Parent = topGui

    local layout = Instance.new("UIListLayout")
    layout.FillDirection = Enum.FillDirection.Vertical
    layout.Padding = UDim.new(0, 2)
    layout.HorizontalAlignment = Enum.HorizontalAlignment.Center
    layout.VerticalAlignment = Enum.VerticalAlignment.Center
    layout.Parent = topFrame

    -- Abbreviation
    local abbrevLabel = Instance.new("TextLabel")
    abbrevLabel.Size = UDim2.new(0.9, 0, 0, 20)
    abbrevLabel.BackgroundTransparency = 1
    abbrevLabel.TextColor3 = Color3.fromRGB(30, 30, 30)
    abbrevLabel.Text = assignment.abbreviation or ""
    abbrevLabel.TextSize = 16
    abbrevLabel.Font = Enum.Font.GothamBold
    abbrevLabel.TextTruncate = Enum.TextTruncate.AtEnd
    abbrevLabel.LayoutOrder = 1
    abbrevLabel.Parent = topFrame

    -- Assignment name
    local nameLabel = Instance.new("TextLabel")
    nameLabel.Size = UDim2.new(0.9, 0, 0, 30)
    nameLabel.BackgroundTransparency = 1
    nameLabel.TextColor3 = Color3.fromRGB(40, 40, 40)
    nameLabel.Text = assignment.assignment or ""
    nameLabel.TextSize = 13
    nameLabel.Font = Enum.Font.Gotham
    nameLabel.TextWrapped = true
    nameLabel.TextTruncate = Enum.TextTruncate.AtEnd
    nameLabel.LayoutOrder = 2
    nameLabel.Parent = topFrame

    -- Due date
    local dateLabel = Instance.new("TextLabel")
    dateLabel.Size = UDim2.new(0.9, 0, 0, 16)
    dateLabel.BackgroundTransparency = 1
    dateLabel.TextColor3 = Color3.fromRGB(60, 60, 60)
    dateLabel.Text = if assignment.dueDate ~= "" then ("Due: " .. assignment.dueDate) else ""
    dateLabel.TextSize = 11
    dateLabel.Font = Enum.Font.Gotham
    dateLabel.LayoutOrder = 3
    dateLabel.Parent = topFrame

    -- Store assignment ID
    note:SetAttribute("AssignmentId", assignment.id)

    return note
end

------------------------------------------------------------------------
-- Parse date string to unix timestamp
------------------------------------------------------------------------

function Manager.parseDateToTimestamp(dateStr: string, timeStr: string?): number?
    -- Try M/D/YYYY format
    local month, day, year = string.match(dateStr, "(%d+)/(%d+)/(%d+)")
    if not month then
        -- Try M-D-YYYY
        month, day, year = string.match(dateStr, "(%d+)-(%d+)-(%d+)")
    end
    if not month then return nil end

    local m = tonumber(month)
    local d = tonumber(day)
    local y = tonumber(year)
    if not m or not d or not y then return nil end

    -- Handle 2-digit year
    if y < 100 then y = y + 2000 end

    local hour = 23
    local min = 59

    -- Parse time if provided
    if timeStr and timeStr ~= "" then
        local h, mn, ampm = string.match(timeStr, "(%d+):(%d+)%s*(%a*)")
        if h then
            hour = tonumber(h) or 23
            min = tonumber(mn) or 59
            if string.lower(ampm or "") == "pm" and hour < 12 then
                hour = hour + 12
            elseif string.lower(ampm or "") == "am" and hour == 12 then
                hour = 0
            end
        end
    end

    local ok, timestamp = pcall(function()
        return os.time({ year = y, month = m, day = d, hour = hour, min = min, sec = 0 })
    end)

    if ok then return timestamp end
    return nil
end

------------------------------------------------------------------------
-- Parse syllabus text into assignment suggestions
------------------------------------------------------------------------

function Manager.parseSyllabusText(text: string): { any }
    local results = {}
    local lines = string.split(text, "\n")

    -- Date patterns
    local datePatterns = {
        "(%d+/%d+/%d+)",           -- M/D/YYYY
        "(%d+%-%d+%-%d+)",         -- M-D-YYYY
        "(%a+%.?%s+%d+%s*,?%s*%d*)", -- Month Day, Year
    }

    -- Assignment keywords
    local keywords = {
        "assignment", "homework", "hw", "quiz", "exam", "test",
        "paper", "essay", "project", "lab", "report", "reading",
        "chapter", "due", "submit", "presentation", "midterm", "final",
    }

    for _, line in lines do
        local trimmed = string.gsub(line, "^%s+", "")
        trimmed = string.gsub(trimmed, "%s+$", "")
        if #trimmed < 5 then continue end

        local hasKeyword = false
        local lower = string.lower(trimmed)
        for _, kw in keywords do
            if string.find(lower, kw) then
                hasKeyword = true
                break
            end
        end

        local foundDate = nil
        for _, pattern in datePatterns do
            local match = string.match(trimmed, pattern)
            if match then
                foundDate = match
                break
            end
        end

        if hasKeyword or foundDate then
            table.insert(results, {
                text = trimmed,
                date = foundDate or "",
            })
        end
    end

    return results
end

------------------------------------------------------------------------
-- Build library
------------------------------------------------------------------------

function Manager.buildLibrary(): Folder
    local folder = Instance.new("Folder")
    folder.Name = "Library"
    folder.Parent = workspace

    local pos = Config.LibraryPosition
    local ls = Config.LibrarySize
    local wt = Config.DormWallThickness

    -- Floor
    makePart({
        Name = "LibraryFloor",
        Size = Vector3.new(ls.X, wt, ls.Z),
        Position = Vector3.new(pos.X, 0, pos.Z),
        Color = Config.LibraryFloorColor,
        Material = Config.LibraryFloorMaterial,
        Parent = folder,
    })

    -- Ceiling
    makePart({
        Name = "LibraryCeiling",
        Size = Vector3.new(ls.X, wt, ls.Z),
        Position = Vector3.new(pos.X, ls.Y, pos.Z),
        Color = Config.LibraryWallColor,
        Material = Config.LibraryWallMaterial,
        Parent = folder,
    })

    -- Walls (4 sides with door on +X side)
    -- Back wall (-Z)
    makePart({
        Name = "LibWallBack",
        Size = Vector3.new(ls.X, ls.Y, wt),
        Position = Vector3.new(pos.X, ls.Y / 2, pos.Z - ls.Z / 2),
        Color = Config.LibraryWallColor,
        Material = Config.LibraryWallMaterial,
        Parent = folder,
    })

    -- Front wall (+Z)
    makePart({
        Name = "LibWallFront",
        Size = Vector3.new(ls.X, ls.Y, wt),
        Position = Vector3.new(pos.X, ls.Y / 2, pos.Z + ls.Z / 2),
        Color = Config.LibraryWallColor,
        Material = Config.LibraryWallMaterial,
        Parent = folder,
    })

    -- Left wall (-X)
    makePart({
        Name = "LibWallLeft",
        Size = Vector3.new(wt, ls.Y, ls.Z),
        Position = Vector3.new(pos.X - ls.X / 2, ls.Y / 2, pos.Z),
        Color = Config.LibraryWallColor,
        Material = Config.LibraryWallMaterial,
        Parent = folder,
    })

    -- Right wall (+X) with door
    local doorWidth = 8
    local doorHeight = 10
    local sideWidth = (ls.Z - doorWidth) / 2
    makePart({
        Name = "LibDoorTop",
        Size = Vector3.new(wt, ls.Y - doorHeight, doorWidth),
        Position = Vector3.new(pos.X + ls.X / 2, doorHeight + (ls.Y - doorHeight) / 2, pos.Z),
        Color = Config.LibraryWallColor,
        Material = Config.LibraryWallMaterial,
        Parent = folder,
    })
    makePart({
        Name = "LibDoorSide1",
        Size = Vector3.new(wt, ls.Y, sideWidth),
        Position = Vector3.new(pos.X + ls.X / 2, ls.Y / 2, pos.Z - doorWidth / 2 - sideWidth / 2),
        Color = Config.LibraryWallColor,
        Material = Config.LibraryWallMaterial,
        Parent = folder,
    })
    makePart({
        Name = "LibDoorSide2",
        Size = Vector3.new(wt, ls.Y, sideWidth),
        Position = Vector3.new(pos.X + ls.X / 2, ls.Y / 2, pos.Z + doorWidth / 2 + sideWidth / 2),
        Color = Config.LibraryWallColor,
        Material = Config.LibraryWallMaterial,
        Parent = folder,
    })

    -- Library sign above door
    local libSign = makePart({
        Name = "LibraryDoorSign",
        Size = Vector3.new(0.3, 3, 12),
        Position = Vector3.new(pos.X + ls.X / 2 + 0.5, doorHeight + 2, pos.Z),
        Color = Color3.fromRGB(60, 50, 40),
        Material = Enum.Material.Slate,
        Parent = folder,
    })
    makeSurfaceText(libSign, Enum.NormalId.Right, "LIBRARY", 50, Color3.fromRGB(255, 240, 200))

    -- Ceiling lights
    for i = 1, 3 do
        local lightX = pos.X - ls.X / 4 + (i - 1) * (ls.X / 3)
        local light = makePart({
            Name = "LibLight" .. i,
            Size = Vector3.new(6, 0.3, 3),
            Position = Vector3.new(lightX, ls.Y - 0.5, pos.Z),
            Color = Color3.fromRGB(255, 250, 230),
            Material = Enum.Material.Neon,
            CanCollide = false,
            Parent = folder,
        })
        local pl = Instance.new("PointLight")
        pl.Brightness = 2
        pl.Range = 40
        pl.Color = Color3.fromRGB(255, 245, 220)
        pl.Parent = light
    end

    -- Study tables in the library
    for i = 1, Config.LibraryTableCount do
        local row = math.floor((i - 1) / 3)
        local col = (i - 1) % 3
        local tableX = pos.X - 25 + col * 25
        local tableZ = pos.Z - 10 + row * 20

        local table_ = makePart({
            Name = "LibTable" .. i,
            Size = Vector3.new(10, 2.5, 5),
            Position = Vector3.new(tableX, 2.5, tableZ),
            Color = Color3.fromRGB(100, 75, 50),
            Material = Enum.Material.Wood,
            Parent = folder,
        })

        -- Table has a SurfaceGui showing "who's studying"
        table_:SetAttribute("IsLibraryTable", true)
        table_:SetAttribute("TableIndex", i)
    end

    -- Main whiteboard in library (back wall)
    local wb = makePart({
        Name = "LibraryWhiteboard",
        Size = Config.WhiteboardSize,
        Position = Vector3.new(pos.X, 10, pos.Z - ls.Z / 2 + 0.5),
        Color = Config.WhiteboardColor,
        Material = Config.WhiteboardMaterial,
        Parent = folder,
    })

    -- Whiteboard frame
    makePart({
        Name = "WBFrameTop",
        Size = Vector3.new(Config.WhiteboardSize.X + 0.6, 0.3, 0.5),
        Position = wb.Position + Vector3.new(0, Config.WhiteboardSize.Y / 2 + 0.15, 0),
        Color = Config.WhiteboardFrameColor,
        Material = Enum.Material.Metal,
        Parent = folder,
    })
    makePart({
        Name = "WBFrameBot",
        Size = Vector3.new(Config.WhiteboardSize.X + 0.6, 0.3, 0.5),
        Position = wb.Position + Vector3.new(0, -Config.WhiteboardSize.Y / 2 - 0.15, 0),
        Color = Config.WhiteboardFrameColor,
        Material = Enum.Material.Metal,
        Parent = folder,
    })

    wb:SetAttribute("IsWhiteboard", true)
    wb:SetAttribute("Location", "Library")

    -- ProximityPrompt on whiteboard
    local wbPrompt = Instance.new("ProximityPrompt")
    wbPrompt.ActionText = "View Board"
    wbPrompt.ObjectText = "Whiteboard"
    wbPrompt.MaxActivationDistance = Config.WhiteboardInteractionRange
    wbPrompt.HoldDuration = 0
    wbPrompt.Parent = wb

    return folder
end

------------------------------------------------------------------------
-- Build a study room
------------------------------------------------------------------------

function Manager.buildStudyRoom(roomIndex: number): Model
    local model = Instance.new("Model")
    model.Name = "StudyRoom_" .. roomIndex

    local rs = Config.StudyRoomSize
    local wt = Config.DormWallThickness

    local baseX = -30 + (roomIndex - 1) * (rs.X + 4)
    local baseY = 0
    local baseZ = Config.StudyRoomStartZ

    -- Floor
    makePart({
        Name = "SRFloor",
        Size = Vector3.new(rs.X, wt, rs.Z),
        Position = Vector3.new(baseX, baseY, baseZ),
        Color = Config.LibraryFloorColor,
        Material = Config.LibraryFloorMaterial,
        Parent = model,
    })

    -- Ceiling
    makePart({
        Name = "SRCeiling",
        Size = Vector3.new(rs.X, wt, rs.Z),
        Position = Vector3.new(baseX, baseY + rs.Y, baseZ),
        Color = Config.DormWallColor,
        Material = Config.DormWallMaterial,
        Parent = model,
    })

    -- Accent color for this room
    local accentColor = Config.CourseColors[((roomIndex - 1) % #Config.CourseColors) + 1]

    -- Walls
    -- Back (-Z)
    makePart({
        Name = "SRWallBack",
        Size = Vector3.new(rs.X, rs.Y, wt),
        Position = Vector3.new(baseX, baseY + rs.Y / 2, baseZ - rs.Z / 2),
        Color = Config.DormWallColor,
        Material = Config.DormWallMaterial,
        Parent = model,
    })

    -- Left (-X)
    makePart({
        Name = "SRWallLeft",
        Size = Vector3.new(wt, rs.Y, rs.Z),
        Position = Vector3.new(baseX - rs.X / 2, baseY + rs.Y / 2, baseZ),
        Color = Config.DormWallColor,
        Material = Config.DormWallMaterial,
        Parent = model,
    })

    -- Right (+X)
    makePart({
        Name = "SRWallRight",
        Size = Vector3.new(wt, rs.Y, rs.Z),
        Position = Vector3.new(baseX + rs.X / 2, baseY + rs.Y / 2, baseZ),
        Color = Config.DormWallColor,
        Material = Config.DormWallMaterial,
        Parent = model,
    })

    -- Front (+Z) with door
    local doorWidth = 5
    local doorHeight = 9
    local sideW = (rs.X - doorWidth) / 2
    makePart({
        Name = "SRFrontLeft",
        Size = Vector3.new(sideW, rs.Y, wt),
        Position = Vector3.new(baseX - doorWidth / 2 - sideW / 2, baseY + rs.Y / 2, baseZ + rs.Z / 2),
        Color = Config.DormWallColor,
        Material = Config.DormWallMaterial,
        Parent = model,
    })
    makePart({
        Name = "SRFrontRight",
        Size = Vector3.new(sideW, rs.Y, wt),
        Position = Vector3.new(baseX + doorWidth / 2 + sideW / 2, baseY + rs.Y / 2, baseZ + rs.Z / 2),
        Color = Config.DormWallColor,
        Material = Config.DormWallMaterial,
        Parent = model,
    })
    makePart({
        Name = "SRFrontAbove",
        Size = Vector3.new(doorWidth, rs.Y - doorHeight, wt),
        Position = Vector3.new(baseX, baseY + doorHeight + (rs.Y - doorHeight) / 2, baseZ + rs.Z / 2),
        Color = Config.DormWallColor,
        Material = Config.DormWallMaterial,
        Parent = model,
    })

    -- Accent stripe above door
    makePart({
        Name = "AccentStripe",
        Size = Vector3.new(rs.X, 0.5, wt + 0.2),
        Position = Vector3.new(baseX, baseY + doorHeight + 0.25, baseZ + rs.Z / 2),
        Color = accentColor,
        Material = Enum.Material.Neon,
        CanCollide = false,
        Parent = model,
    })

    -- Room sign
    local roomSign = makePart({
        Name = "RoomSign",
        Size = Vector3.new(6, 2, 0.2),
        Position = Vector3.new(baseX, baseY + doorHeight + 2, baseZ + rs.Z / 2 + 0.6),
        Color = Color3.fromRGB(60, 50, 40),
        Material = Enum.Material.Slate,
        Parent = model,
    })
    makeSurfaceText(roomSign, Enum.NormalId.Front, "Study Room " .. roomIndex, 26, Color3.fromRGB(255, 240, 200))

    -- Ceiling light
    local light = makePart({
        Name = "SRLight",
        Size = Vector3.new(4, 0.3, 4),
        Position = Vector3.new(baseX, baseY + rs.Y - 0.5, baseZ),
        Color = Color3.fromRGB(255, 250, 230),
        Material = Enum.Material.Neon,
        CanCollide = false,
        Parent = model,
    })
    local pl = Instance.new("PointLight")
    pl.Brightness = 1.5
    pl.Range = 25
    pl.Color = Color3.fromRGB(255, 245, 220)
    pl.Parent = light

    -- Central table
    makePart({
        Name = "SRTable",
        Size = Vector3.new(8, 2.5, 4),
        Position = Vector3.new(baseX, 2.5, baseZ),
        Color = Color3.fromRGB(100, 75, 50),
        Material = Enum.Material.Wood,
        Parent = model,
    })

    -- Whiteboard on back wall
    local wb = makePart({
        Name = "SRWhiteboard",
        Size = Vector3.new(8, 5, 0.3),
        Position = Vector3.new(baseX, 9, baseZ - rs.Z / 2 + 0.5),
        Color = Config.WhiteboardColor,
        Material = Config.WhiteboardMaterial,
        Parent = model,
    })
    wb:SetAttribute("IsWhiteboard", true)
    wb:SetAttribute("Location", "StudyRoom")
    wb:SetAttribute("RoomIndex", roomIndex)

    -- Timer display on whiteboard
    local timerGui = Instance.new("SurfaceGui")
    timerGui.Name = "TimerGui"
    timerGui.Face = Enum.NormalId.Front
    timerGui.SizingMode = Enum.SurfaceGuiSizingMode.PixelsPerStud
    timerGui.PixelsPerStud = 40
    timerGui.Parent = wb

    local timerFrame = Instance.new("Frame")
    timerFrame.Name = "TimerFrame"
    timerFrame.Size = UDim2.new(1, 0, 1, 0)
    timerFrame.BackgroundTransparency = 1
    timerFrame.Parent = timerGui

    local timerLabel = Instance.new("TextLabel")
    timerLabel.Name = "TimerLabel"
    timerLabel.Size = UDim2.new(1, 0, 0.4, 0)
    timerLabel.Position = UDim2.new(0, 0, 0.1, 0)
    timerLabel.BackgroundTransparency = 1
    timerLabel.TextColor3 = Color3.fromRGB(60, 60, 60)
    timerLabel.Text = "25:00"
    timerLabel.TextSize = 60
    timerLabel.Font = Enum.Font.RobotoMono
    timerLabel.Parent = timerFrame

    local statusLabel = Instance.new("TextLabel")
    statusLabel.Name = "StatusLabel"
    statusLabel.Size = UDim2.new(1, 0, 0.2, 0)
    statusLabel.Position = UDim2.new(0, 0, 0.55, 0)
    statusLabel.BackgroundTransparency = 1
    statusLabel.TextColor3 = Color3.fromRGB(100, 100, 100)
    statusLabel.Text = "Ready"
    statusLabel.TextSize = 24
    statusLabel.Font = Enum.Font.Gotham
    statusLabel.Parent = timerFrame

    local membersLabel = Instance.new("TextLabel")
    membersLabel.Name = "MembersLabel"
    membersLabel.Size = UDim2.new(1, 0, 0.15, 0)
    membersLabel.Position = UDim2.new(0, 0, 0.78, 0)
    membersLabel.BackgroundTransparency = 1
    membersLabel.TextColor3 = Color3.fromRGB(130, 130, 130)
    membersLabel.Text = ""
    membersLabel.TextSize = 16
    membersLabel.Font = Enum.Font.Gotham
    membersLabel.TextWrapped = true
    membersLabel.Parent = timerFrame

    -- ProximityPrompt on whiteboard
    local wbPrompt = Instance.new("ProximityPrompt")
    wbPrompt.ActionText = "Study Timer"
    wbPrompt.ObjectText = "Whiteboard"
    wbPrompt.MaxActivationDistance = Config.WhiteboardInteractionRange
    wbPrompt.HoldDuration = 0
    wbPrompt.Parent = wb

    model.Parent = workspace
    return model
end

------------------------------------------------------------------------
-- Update library whiteboard (show who's studying what)
------------------------------------------------------------------------

function Manager.updateLibraryBoard(playerSummaries: { { name: string, classes: { string } } })
    local wb = workspace:FindFirstChild("Library")
    if not wb then return end

    local board = wb:FindFirstChild("LibraryWhiteboard")
    if not board then return end

    -- Remove old gui
    local oldGui = board:FindFirstChild("BoardGui")
    if oldGui then oldGui:Destroy() end

    local gui = Instance.new("SurfaceGui")
    gui.Name = "BoardGui"
    gui.Face = Enum.NormalId.Front
    gui.SizingMode = Enum.SurfaceGuiSizingMode.PixelsPerStud
    gui.PixelsPerStud = 40
    gui.Parent = board

    local frame = Instance.new("Frame")
    frame.Size = UDim2.new(1, 0, 1, 0)
    frame.BackgroundTransparency = 1
    frame.Parent = gui

    local titleLabel = Instance.new("TextLabel")
    titleLabel.Size = UDim2.new(1, 0, 0, 30)
    titleLabel.BackgroundTransparency = 1
    titleLabel.TextColor3 = Color3.fromRGB(40, 40, 40)
    titleLabel.Text = "Who's Studying What"
    titleLabel.TextSize = 22
    titleLabel.Font = Enum.Font.GothamBold
    titleLabel.Parent = frame

    local listLayout = Instance.new("UIListLayout")
    listLayout.Padding = UDim.new(0, 4)
    listLayout.SortOrder = Enum.SortOrder.LayoutOrder
    listLayout.Parent = frame

    -- Spacer after title
    local spacer = Instance.new("Frame")
    spacer.Size = UDim2.new(1, 0, 0, 35)
    spacer.BackgroundTransparency = 1
    spacer.LayoutOrder = 0
    spacer.Parent = frame

    for i, summary in playerSummaries do
        if i > 10 then break end -- cap display at 10
        local entry = Instance.new("TextLabel")
        entry.Size = UDim2.new(0.95, 0, 0, 18)
        entry.BackgroundTransparency = 1
        entry.TextColor3 = Color3.fromRGB(50, 50, 50)
        entry.Text = summary.name .. ": " .. table.concat(summary.classes, ", ")
        entry.TextSize = 14
        entry.Font = Enum.Font.Gotham
        entry.TextXAlignment = Enum.TextXAlignment.Left
        entry.TextTruncate = Enum.TextTruncate.AtEnd
        entry.LayoutOrder = i
        entry.Parent = frame
    end
end

------------------------------------------------------------------------
-- Update study room timer display
------------------------------------------------------------------------

function Manager.updateTimerDisplay(roomModel: Model, timeLeft: number, status: string, members: { string })
    local wb = roomModel:FindFirstChild("SRWhiteboard")
    if not wb then return end

    local gui = wb:FindFirstChild("TimerGui")
    if not gui then return end

    local timerFrame = gui:FindFirstChild("TimerFrame")
    if not timerFrame then return end

    local timerLabel = timerFrame:FindFirstChild("TimerLabel")
    if timerLabel then
        local mins = math.floor(timeLeft / 60)
        local secs = timeLeft % 60
        timerLabel.Text = string.format("%02d:%02d", mins, secs)

        if status == "running" then
            timerLabel.TextColor3 = Color3.fromRGB(40, 140, 40)
        elseif status == "paused" then
            timerLabel.TextColor3 = Color3.fromRGB(200, 160, 40)
        else
            timerLabel.TextColor3 = Color3.fromRGB(60, 60, 60)
        end
    end

    local statusLabel = timerFrame:FindFirstChild("StatusLabel")
    if statusLabel then
        if status == "running" then
            statusLabel.Text = "Studying..."
        elseif status == "paused" then
            statusLabel.Text = "Paused"
        elseif status == "finished" then
            statusLabel.Text = "Time's up!"
        else
            statusLabel.Text = "Ready"
        end
    end

    local membersLabel = timerFrame:FindFirstChild("MembersLabel")
    if membersLabel then
        if #members > 0 then
            membersLabel.Text = table.concat(members, ", ")
        else
            membersLabel.Text = ""
        end
    end
end

return Manager
