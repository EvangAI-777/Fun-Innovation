--[[
    PlannerServer.luau
    Script -- place in ServerScriptService

    Server-side logic for the Academic Planner Study Hub.
    Handles DataStore persistence, assignment CRUD, dorm room allocation,
    study group management, group timers, and campus generation.
]]

local Players = game:GetService("Players")
local DataStoreService = game:GetService("DataStoreService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ServerStorage = game:GetService("ServerStorage")
local RunService = game:GetService("RunService")

local Config = require(ReplicatedStorage:WaitForChild("PlannerConfig"))
local Manager = require(ServerStorage:WaitForChild("AssignmentManager"))

------------------------------------------------------------------------
-- DataStore
------------------------------------------------------------------------

local plannerStore = DataStoreService:GetDataStore(Config.DataStoreKey)

------------------------------------------------------------------------
-- Remote events / functions
------------------------------------------------------------------------

local remotes = Instance.new("Folder")
remotes.Name = "PlannerRemotes"
remotes.Parent = ReplicatedStorage

local createAssignmentEvent = Instance.new("RemoteEvent")
createAssignmentEvent.Name = "CreateAssignment"
createAssignmentEvent.Parent = remotes

local updateAssignmentEvent = Instance.new("RemoteEvent")
updateAssignmentEvent.Name = "UpdateAssignment"
updateAssignmentEvent.Parent = remotes

local deleteAssignmentEvent = Instance.new("RemoteEvent")
deleteAssignmentEvent.Name = "DeleteAssignment"
deleteAssignmentEvent.Parent = remotes

local toggleCompleteEvent = Instance.new("RemoteEvent")
toggleCompleteEvent.Name = "ToggleComplete"
toggleCompleteEvent.Parent = remotes

local parseSyllabusEvent = Instance.new("RemoteFunction")
parseSyllabusEvent.Name = "ParseSyllabus"
parseSyllabusEvent.Parent = remotes

local requestDataEvent = Instance.new("RemoteFunction")
requestDataEvent.Name = "RequestData"
requestDataEvent.Parent = remotes

local assignmentUpdatedEvent = Instance.new("RemoteEvent")
assignmentUpdatedEvent.Name = "AssignmentUpdated"
assignmentUpdatedEvent.Parent = remotes

-- Study group remotes
local joinStudyGroupEvent = Instance.new("RemoteEvent")
joinStudyGroupEvent.Name = "JoinStudyGroup"
joinStudyGroupEvent.Parent = remotes

local leaveStudyGroupEvent = Instance.new("RemoteEvent")
leaveStudyGroupEvent.Name = "LeaveStudyGroup"
leaveStudyGroupEvent.Parent = remotes

local startTimerEvent = Instance.new("RemoteEvent")
startTimerEvent.Name = "StartTimer"
startTimerEvent.Parent = remotes

local pauseTimerEvent = Instance.new("RemoteEvent")
pauseTimerEvent.Name = "PauseTimer"
pauseTimerEvent.Parent = remotes

local resetTimerEvent = Instance.new("RemoteEvent")
resetTimerEvent.Name = "ResetTimer"
resetTimerEvent.Parent = remotes

local timerUpdateEvent = Instance.new("RemoteEvent")
timerUpdateEvent.Name = "TimerUpdate"
timerUpdateEvent.Parent = remotes

local studyGroupUpdateEvent = Instance.new("RemoteEvent")
studyGroupUpdateEvent.Name = "StudyGroupUpdate"
studyGroupUpdateEvent.Parent = remotes

------------------------------------------------------------------------
-- State
------------------------------------------------------------------------

local playerDataCache: { [number]: any } = {}
local playerDorms: { [number]: number } = {}       -- userId -> dormIndex
local dormModels: { [number]: Model } = {}          -- dormIndex -> Model
local stickyNoteModels: { [string]: Part } = {}     -- assignmentId -> Part
local nextDormIndex = 1

-- Study rooms (pre-built)
local studyRoomModels: { [number]: Model } = {}

-- Study group state per room
local studyGroups: { [number]: {
    members: { [number]: string },  -- userId -> playerName
    timerDuration: number,
    timerRemaining: number,
    timerStatus: string,            -- "idle" | "running" | "paused" | "finished"
} } = {}

------------------------------------------------------------------------
-- Build campus
------------------------------------------------------------------------

Manager.buildLobby()
Manager.buildLibrary()

-- Build study rooms
for i = 1, Config.MaxStudyRooms do
    local model = Manager.buildStudyRoom(i)
    studyRoomModels[i] = model
    studyGroups[i] = {
        members = {},
        timerDuration = Config.DefaultTimerDuration,
        timerRemaining = Config.DefaultTimerDuration,
        timerStatus = "idle",
    }
end

------------------------------------------------------------------------
-- Data persistence
------------------------------------------------------------------------

local function loadPlayerData(player: Player): any
    local key = "planner_" .. tostring(player.UserId)
    local success, data = pcall(function()
        return plannerStore:GetAsync(key)
    end)

    if not success then
        warn("[StudyHub] Failed to load data for " .. player.Name .. ": " .. tostring(data))
    elseif data then
        local parsed = Manager.deserialize(data)
        if parsed then return parsed end
    end

    return Manager.newPlayerData()
end

local function savePlayerData(player: Player)
    local data = playerDataCache[player.UserId]
    if not data then return end

    local key = "planner_" .. tostring(player.UserId)
    local serialized = Manager.serialize(data)

    local ok, err = pcall(function()
        plannerStore:SetAsync(key, serialized)
    end)
    if not ok then
        warn("[StudyHub] Failed to save data for " .. player.Name .. ": " .. tostring(err))
    end
end

------------------------------------------------------------------------
-- Rebuild sticky notes on a player's desk
------------------------------------------------------------------------

local function getDeskPart(dormIndex: number): Part?
    local model = dormModels[dormIndex]
    if not model then return nil end
    return model:FindFirstChild("DeskTop")
end

local function rebuildPlayerDesk(player: Player)
    local data = playerDataCache[player.UserId]
    if not data then return end

    local dormIndex = playerDorms[player.UserId]
    if not dormIndex then return end

    -- Remove old sticky notes for this player
    for _, a in data.assignments do
        if stickyNoteModels[a.id] then
            stickyNoteModels[a.id]:Destroy()
            stickyNoteModels[a.id] = nil
        end
    end

    local desk = getDeskPart(dormIndex)
    if not desk then return end

    -- Build sticky notes (max 8 visible on desk, most urgent first)
    local sorted = {}
    for _, a in data.assignments do
        table.insert(sorted, a)
    end

    -- Sort: incomplete first, then by due date (soonest first), then no-date
    table.sort(sorted, function(a, b)
        if a.completed ~= b.completed then
            return not a.completed
        end
        local tsA = Manager.parseDateToTimestamp(a.dueDate, a.dueTime)
        local tsB = Manager.parseDateToTimestamp(b.dueDate, b.dueTime)
        if tsA and tsB then return tsA < tsB end
        if tsA then return true end
        if tsB then return false end
        return (a.created or 0) < (b.created or 0)
    end)

    for i, assignment in sorted do
        if i > 8 then break end -- max 8 on desk
        local note = Manager.buildStickyNote(assignment, desk, i)
        stickyNoteModels[assignment.id] = note
    end
end

------------------------------------------------------------------------
-- Update library whiteboard with all players' classes
------------------------------------------------------------------------

local function updateLibraryBoard()
    local summaries = {}

    for userId, data in playerDataCache do
        local player = Players:GetPlayerByUserId(userId)
        if player then
            local classSet = {}
            for _, a in data.assignments do
                if a.abbreviation and a.abbreviation ~= "" and not a.completed then
                    classSet[a.abbreviation] = true
                end
            end
            local classes = {}
            for cls in classSet do
                table.insert(classes, cls)
            end
            table.sort(classes)
            if #classes > 0 then
                table.insert(summaries, {
                    name = player.Name,
                    classes = classes,
                })
            end
        end
    end

    Manager.updateLibraryBoard(summaries)
end

------------------------------------------------------------------------
-- Player lifecycle
------------------------------------------------------------------------

local function onPlayerAdded(player: Player)
    local data = loadPlayerData(player)
    playerDataCache[player.UserId] = data

    -- Assign a dorm room
    local dormIndex = nextDormIndex
    playerDorms[player.UserId] = dormIndex
    nextDormIndex += 1

    -- Build the dorm
    local dormModel = Manager.buildDormRoom(dormIndex, player.Name)
    dormModels[dormIndex] = dormModel

    -- Build desk sticky notes
    rebuildPlayerDesk(player)

    -- Update library board
    updateLibraryBoard()
end

local function onPlayerRemoving(player: Player)
    savePlayerData(player)

    -- Clean up sticky notes
    local data = playerDataCache[player.UserId]
    if data then
        for _, a in data.assignments do
            if stickyNoteModels[a.id] then
                stickyNoteModels[a.id]:Destroy()
                stickyNoteModels[a.id] = nil
            end
        end
    end

    -- Clean up dorm
    local dormIndex = playerDorms[player.UserId]
    if dormIndex and dormModels[dormIndex] then
        dormModels[dormIndex]:Destroy()
        dormModels[dormIndex] = nil
    end

    -- Remove from any study group
    for roomIdx, group in studyGroups do
        if group.members[player.UserId] then
            group.members[player.UserId] = nil
            broadcastStudyGroupUpdate(roomIdx)
        end
    end

    playerDorms[player.UserId] = nil
    playerDataCache[player.UserId] = nil

    updateLibraryBoard()
end

Players.PlayerAdded:Connect(onPlayerAdded)
Players.PlayerRemoving:Connect(onPlayerRemoving)

for _, player in Players:GetPlayers() do
    task.spawn(onPlayerAdded, player)
end

-- Auto-save every 2 minutes
task.spawn(function()
    while true do
        task.wait(120)
        for _, player in Players:GetPlayers() do
            task.spawn(savePlayerData, player)
        end
    end
end)

------------------------------------------------------------------------
-- Study group helpers
------------------------------------------------------------------------

function broadcastStudyGroupUpdate(roomIndex: number)
    local group = studyGroups[roomIndex]
    if not group then return end

    local memberNames = {}
    for _, name in group.members do
        table.insert(memberNames, name)
    end

    -- Update physical timer display
    local roomModel = studyRoomModels[roomIndex]
    if roomModel then
        Manager.updateTimerDisplay(roomModel, group.timerRemaining, group.timerStatus, memberNames)
    end

    -- Notify all clients
    studyGroupUpdateEvent:FireAllClients(roomIndex, memberNames, group.timerDuration, group.timerRemaining, group.timerStatus)
end

------------------------------------------------------------------------
-- Timer tick (runs every second for active timers)
------------------------------------------------------------------------

task.spawn(function()
    while true do
        task.wait(1)
        for roomIdx, group in studyGroups do
            if group.timerStatus == "running" then
                group.timerRemaining -= 1
                if group.timerRemaining <= 0 then
                    group.timerRemaining = 0
                    group.timerStatus = "finished"

                    -- Notify members
                    for userId in group.members do
                        local player = Players:GetPlayerByUserId(userId)
                        if player then
                            timerUpdateEvent:FireClient(player, roomIdx, "finished", 0)
                        end
                    end
                end

                broadcastStudyGroupUpdate(roomIdx)
            end
        end
    end
end)

------------------------------------------------------------------------
-- Remote handlers: Assignments
------------------------------------------------------------------------

createAssignmentEvent.OnServerEvent:Connect(function(player, abbreviation, className, assignmentName, dueDate, dueTime)
    local data = playerDataCache[player.UserId]
    if not data then return end
    if #data.assignments >= Config.MaxAssignmentsPerPlayer then return end

    -- Validate
    if type(abbreviation) ~= "string" then return end
    if type(className) ~= "string" then return end
    if type(assignmentName) ~= "string" then return end
    if type(dueDate) ~= "string" then dueDate = "" end
    if type(dueTime) ~= "string" then dueTime = "" end

    abbreviation = string.sub(abbreviation, 1, Config.MaxAbbrevLength)
    className = string.sub(className, 1, Config.MaxClassNameLength)
    assignmentName = string.sub(assignmentName, 1, Config.MaxAssignmentNameLength)
    dueDate = string.sub(dueDate, 1, 20)
    dueTime = string.sub(dueTime, 1, 20)

    local assignment = {
        id = Manager.generateId(),
        abbreviation = abbreviation,
        className = className,
        assignment = assignmentName,
        dueDate = dueDate,
        dueTime = dueTime,
        completed = false,
        created = os.time(),
    }

    table.insert(data.assignments, assignment)

    -- Rebuild desk
    rebuildPlayerDesk(player)

    -- Update library board
    updateLibraryBoard()

    -- Notify
    assignmentUpdatedEvent:FireClient(player, "created", assignment.id)
end)

updateAssignmentEvent.OnServerEvent:Connect(function(player, assignmentId, field, value)
    local data = playerDataCache[player.UserId]
    if not data then return end
    if type(assignmentId) ~= "string" then return end
    if type(field) ~= "string" then return end

    local validFields = { abbreviation = true, className = true, assignment = true, dueDate = true, dueTime = true }
    if not validFields[field] then return end
    if type(value) ~= "string" then return end

    local maxLens = {
        abbreviation = Config.MaxAbbrevLength,
        className = Config.MaxClassNameLength,
        assignment = Config.MaxAssignmentNameLength,
        dueDate = 20,
        dueTime = 20,
    }
    value = string.sub(value, 1, maxLens[field] or 100)

    for _, a in data.assignments do
        if a.id == assignmentId then
            a[field] = value
            rebuildPlayerDesk(player)
            updateLibraryBoard()
            assignmentUpdatedEvent:FireClient(player, "updated", assignmentId)
            break
        end
    end
end)

deleteAssignmentEvent.OnServerEvent:Connect(function(player, assignmentId)
    local data = playerDataCache[player.UserId]
    if not data then return end
    if type(assignmentId) ~= "string" then return end

    for i, a in data.assignments do
        if a.id == assignmentId then
            -- Remove sticky note
            if stickyNoteModels[a.id] then
                stickyNoteModels[a.id]:Destroy()
                stickyNoteModels[a.id] = nil
            end
            table.remove(data.assignments, i)
            rebuildPlayerDesk(player)
            updateLibraryBoard()
            assignmentUpdatedEvent:FireClient(player, "deleted", assignmentId)
            break
        end
    end
end)

toggleCompleteEvent.OnServerEvent:Connect(function(player, assignmentId)
    local data = playerDataCache[player.UserId]
    if not data then return end
    if type(assignmentId) ~= "string" then return end

    for _, a in data.assignments do
        if a.id == assignmentId then
            a.completed = not a.completed
            rebuildPlayerDesk(player)
            updateLibraryBoard()
            assignmentUpdatedEvent:FireClient(player, "toggled", assignmentId)
            break
        end
    end
end)

------------------------------------------------------------------------
-- Remote handlers: Syllabus parsing
------------------------------------------------------------------------

parseSyllabusEvent.OnServerInvoke = function(player, text)
    if type(text) ~= "string" then return {} end
    text = string.sub(text, 1, 10000) -- cap input size
    return Manager.parseSyllabusText(text)
end

------------------------------------------------------------------------
-- Remote handlers: Data request
------------------------------------------------------------------------

requestDataEvent.OnServerInvoke = function(player)
    local data = playerDataCache[player.UserId]
    if not data then return nil end
    return Manager.serialize(data)
end

------------------------------------------------------------------------
-- Remote handlers: Study groups
------------------------------------------------------------------------

joinStudyGroupEvent.OnServerEvent:Connect(function(player, roomIndex)
    if type(roomIndex) ~= "number" then return end
    roomIndex = math.floor(roomIndex)
    if roomIndex < 1 or roomIndex > Config.MaxStudyRooms then return end

    local group = studyGroups[roomIndex]
    if not group then return end

    -- Already in this group?
    if group.members[player.UserId] then return end

    -- Count members
    local count = 0
    for _ in group.members do count += 1 end
    if count >= Config.MaxGroupMembers then return end

    -- Remove from any other group first
    for idx, g in studyGroups do
        if g.members[player.UserId] then
            g.members[player.UserId] = nil
            broadcastStudyGroupUpdate(idx)
        end
    end

    group.members[player.UserId] = player.Name
    broadcastStudyGroupUpdate(roomIndex)
end)

leaveStudyGroupEvent.OnServerEvent:Connect(function(player, roomIndex)
    if type(roomIndex) ~= "number" then return end
    roomIndex = math.floor(roomIndex)
    if roomIndex < 1 or roomIndex > Config.MaxStudyRooms then return end

    local group = studyGroups[roomIndex]
    if not group then return end

    group.members[player.UserId] = nil

    -- If no members left, reset timer
    local count = 0
    for _ in group.members do count += 1 end
    if count == 0 then
        group.timerStatus = "idle"
        group.timerRemaining = group.timerDuration
    end

    broadcastStudyGroupUpdate(roomIndex)
end)

startTimerEvent.OnServerEvent:Connect(function(player, roomIndex, duration)
    if type(roomIndex) ~= "number" then return end
    roomIndex = math.floor(roomIndex)
    if roomIndex < 1 or roomIndex > Config.MaxStudyRooms then return end

    local group = studyGroups[roomIndex]
    if not group then return end

    -- Must be a member to start
    if not group.members[player.UserId] then return end

    if type(duration) == "number" and duration > 0 then
        duration = math.min(math.floor(duration), Config.MaxTimerDuration)
        group.timerDuration = duration
        group.timerRemaining = duration
    end

    if group.timerStatus == "idle" or group.timerStatus == "finished" then
        group.timerRemaining = group.timerDuration
    end

    group.timerStatus = "running"
    broadcastStudyGroupUpdate(roomIndex)
end)

pauseTimerEvent.OnServerEvent:Connect(function(player, roomIndex)
    if type(roomIndex) ~= "number" then return end
    roomIndex = math.floor(roomIndex)
    if roomIndex < 1 or roomIndex > Config.MaxStudyRooms then return end

    local group = studyGroups[roomIndex]
    if not group then return end
    if not group.members[player.UserId] then return end

    if group.timerStatus == "running" then
        group.timerStatus = "paused"
    elseif group.timerStatus == "paused" then
        group.timerStatus = "running"
    end

    broadcastStudyGroupUpdate(roomIndex)
end)

resetTimerEvent.OnServerEvent:Connect(function(player, roomIndex)
    if type(roomIndex) ~= "number" then return end
    roomIndex = math.floor(roomIndex)
    if roomIndex < 1 or roomIndex > Config.MaxStudyRooms then return end

    local group = studyGroups[roomIndex]
    if not group then return end
    if not group.members[player.UserId] then return end

    group.timerStatus = "idle"
    group.timerRemaining = group.timerDuration
    broadcastStudyGroupUpdate(roomIndex)
end)

------------------------------------------------------------------------
-- Game close: save all
------------------------------------------------------------------------

game:BindToClose(function()
    for _, player in Players:GetPlayers() do
        savePlayerData(player)
    end
end)

print("[StudyHub] Server initialized")
