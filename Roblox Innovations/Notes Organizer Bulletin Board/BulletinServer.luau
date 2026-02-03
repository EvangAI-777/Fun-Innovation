--[[
    BulletinServer.luau
    Script -- place in ServerScriptService

    Server-side logic for the Notes Organizer Bulletin Board.
    Handles DataStore persistence, note CRUD operations, room generation,
    and relays note data between clients.
]]

local Players = game:GetService("Players")
local DataStoreService = game:GetService("DataStoreService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ServerStorage = game:GetService("ServerStorage")

local Config = require(ReplicatedStorage:WaitForChild("BulletinConfig"))
local NoteManager = require(ServerStorage:WaitForChild("NoteManager"))

------------------------------------------------------------------------
-- DataStore
------------------------------------------------------------------------

local bulletinStore = DataStoreService:GetDataStore(Config.DataStoreKey)

------------------------------------------------------------------------
-- Remote events
------------------------------------------------------------------------

local remotes = Instance.new("Folder")
remotes.Name = "BulletinRemotes"
remotes.Parent = ReplicatedStorage

local createNoteEvent = Instance.new("RemoteEvent")
createNoteEvent.Name = "CreateNote"
createNoteEvent.Parent = remotes

local updateNoteEvent = Instance.new("RemoteEvent")
updateNoteEvent.Name = "UpdateNote"
updateNoteEvent.Parent = remotes

local deleteNoteEvent = Instance.new("RemoteEvent")
deleteNoteEvent.Name = "DeleteNote"
deleteNoteEvent.Parent = remotes

local createFolderEvent = Instance.new("RemoteEvent")
createFolderEvent.Name = "CreateFolder"
createFolderEvent.Parent = remotes

local deleteFolderEvent = Instance.new("RemoteEvent")
deleteFolderEvent.Name = "DeleteFolder"
deleteFolderEvent.Parent = remotes

local toggleVisibilityEvent = Instance.new("RemoteEvent")
toggleVisibilityEvent.Name = "ToggleVisibility"
toggleVisibilityEvent.Parent = remotes

local requestDataEvent = Instance.new("RemoteFunction")
requestDataEvent.Name = "RequestData"
requestDataEvent.Parent = remotes

local readNoteEvent = Instance.new("RemoteFunction")
readNoteEvent.Name = "ReadNote"
readNoteEvent.Parent = remotes

local noteUpdatedEvent = Instance.new("RemoteEvent")
noteUpdatedEvent.Name = "NoteUpdated"
noteUpdatedEvent.Parent = remotes

------------------------------------------------------------------------
-- Player data cache
------------------------------------------------------------------------

local playerDataCache: { [number]: any } = {}  -- userId -> PlayerData
local noteModels: { [string]: Model } = {}     -- noteId -> Model
local roomModels: { [string]: Model } = {}     -- folderId -> Model
local playerSlots: { [number]: number } = {}   -- userId -> slot (for room grid offset)
local nextPlayerSlot = 0

------------------------------------------------------------------------
-- Notes folder in workspace
------------------------------------------------------------------------

local notesFolder = Instance.new("Folder")
notesFolder.Name = "BulletinNotes"
notesFolder.Parent = workspace

------------------------------------------------------------------------
-- Build the lobby
------------------------------------------------------------------------

NoteManager.buildLobby()

------------------------------------------------------------------------
-- Data persistence
------------------------------------------------------------------------

local function loadPlayerData(player: Player): any
    local key = "player_" .. tostring(player.UserId)
    local success, data = pcall(function()
        return bulletinStore:GetAsync(key)
    end)

    if not success then
        warn("[Bulletin] Failed to load data for " .. player.Name .. ": " .. tostring(data))
    elseif data then
        local parsed = NoteManager.deserialize(data)
        if parsed then return parsed end
    end

    return NoteManager.newPlayerData()
end

local function savePlayerData(player: Player)
    local data = playerDataCache[player.UserId]
    if not data then return end

    local key = "player_" .. tostring(player.UserId)
    local serialized = NoteManager.serialize(data)

    local ok, err = pcall(function()
        bulletinStore:SetAsync(key, serialized)
    end)
    if not ok then
        warn("[Bulletin] Failed to save data for " .. player.Name .. ": " .. tostring(err))
    end
end

------------------------------------------------------------------------
-- Rebuild all physical notes for a player
------------------------------------------------------------------------

local function rebuildPlayerNotes(player: Player)
    local data = playerDataCache[player.UserId]
    if not data then return end

    -- Remove old note models for this player
    for _, note in data.notes do
        if noteModels[note.id] then
            noteModels[note.id]:Destroy()
            noteModels[note.id] = nil
        end
    end

    -- Rebuild
    for _, note in data.notes do
        local model = NoteManager.buildNoteModel(note, notesFolder)
        noteModels[note.id] = model
    end
end

------------------------------------------------------------------------
-- Rebuild rooms for a player
------------------------------------------------------------------------

local function rebuildPlayerRooms(player: Player)
    local data = playerDataCache[player.UserId]
    if not data then return end

    -- Remove old rooms
    for _, folder in data.folders do
        if roomModels[folder.id] then
            roomModels[folder.id]:Destroy()
            roomModels[folder.id] = nil
        end
    end

    -- Rebuild with player-specific slot to avoid room overlap between players
    local slot = playerSlots[player.UserId] or 0
    for i, folder in data.folders do
        local model = NoteManager.buildRoom(folder, i, slot)
        roomModels[folder.id] = model
    end
end

------------------------------------------------------------------------
-- Player lifecycle
------------------------------------------------------------------------

local function onPlayerAdded(player: Player)
    local data = loadPlayerData(player)
    playerDataCache[player.UserId] = data

    -- Assign a unique grid slot so this player's rooms don't overlap others
    nextPlayerSlot += 1
    playerSlots[player.UserId] = nextPlayerSlot

    -- Build rooms and notes
    rebuildPlayerRooms(player)
    rebuildPlayerNotes(player)
end

local function onPlayerRemoving(player: Player)
    savePlayerData(player)

    -- Clean up models
    local data = playerDataCache[player.UserId]
    if data then
        for _, note in data.notes do
            if noteModels[note.id] then
                noteModels[note.id]:Destroy()
                noteModels[note.id] = nil
            end
        end
        for _, folder in data.folders do
            if roomModels[folder.id] then
                roomModels[folder.id]:Destroy()
                roomModels[folder.id] = nil
            end
        end
    end

    playerDataCache[player.UserId] = nil
    playerSlots[player.UserId] = nil
end

Players.PlayerAdded:Connect(onPlayerAdded)
Players.PlayerRemoving:Connect(onPlayerRemoving)

for _, player in Players:GetPlayers() do
    task.spawn(onPlayerAdded, player)
end

-- Periodic auto-save
task.spawn(function()
    while true do
        task.wait(120)
        for _, player in Players:GetPlayers() do
            task.spawn(savePlayerData, player)
        end
    end
end)

------------------------------------------------------------------------
-- Remote handlers
------------------------------------------------------------------------

-- Create a new note
createNoteEvent.OnServerEvent:Connect(function(player, title, body, folderId, posX, posY, posZ, normX, normY, normZ)
    local data = playerDataCache[player.UserId]
    if not data then return end
    if #data.notes >= Config.MaxNotesPerPlayer then return end

    -- Validate strings
    if type(title) ~= "string" then return end
    if type(body) ~= "string" then return end
    title = string.sub(title, 1, 100)
    body = string.sub(body, 1, 2000)

    -- Validate position and normal are numbers
    if type(posX) ~= "number" or type(posY) ~= "number" or type(posZ) ~= "number" then return end
    if type(normX) ~= "number" or type(normY) ~= "number" or type(normZ) ~= "number" then return end

    local note = {
        id = NoteManager.generateId(),
        title = title,
        body = body,
        folderId = if type(folderId) == "string" and folderId ~= "" then folderId else nil,
        isPublic = Config.PublicByDefault,
        authorId = player.UserId,
        authorName = player.Name,
        position = { x = posX, y = posY, z = posZ },
        normal = { x = normX, y = normY, z = normZ },
        created = os.time(),
        modified = os.time(),
    }

    table.insert(data.notes, note)

    -- Build physical note
    local model = NoteManager.buildNoteModel(note, notesFolder)
    noteModels[note.id] = model

    -- Notify all clients
    noteUpdatedEvent:FireAllClients("created", player.Name, note.id, title)
end)

-- Update an existing note
updateNoteEvent.OnServerEvent:Connect(function(player, noteId, newTitle, newBody)
    local data = playerDataCache[player.UserId]
    if not data then return end

    for _, note in data.notes do
        if note.id == noteId and note.authorId == player.UserId then
            if type(newTitle) == "string" then
                note.title = string.sub(newTitle, 1, 100)
            end
            if type(newBody) == "string" then
                note.body = string.sub(newBody, 1, 2000)
            end
            note.modified = os.time()

            -- Rebuild the physical note
            if noteModels[noteId] then
                noteModels[noteId]:Destroy()
            end
            local model = NoteManager.buildNoteModel(note, notesFolder)
            noteModels[noteId] = model

            noteUpdatedEvent:FireAllClients("updated", player.Name, noteId, note.title)
            break
        end
    end
end)

-- Delete a note
deleteNoteEvent.OnServerEvent:Connect(function(player, noteId)
    local data = playerDataCache[player.UserId]
    if not data then return end

    for i, note in data.notes do
        if note.id == noteId and note.authorId == player.UserId then
            table.remove(data.notes, i)
            if noteModels[noteId] then
                noteModels[noteId]:Destroy()
                noteModels[noteId] = nil
            end
            noteUpdatedEvent:FireAllClients("deleted", player.Name, noteId, "")
            break
        end
    end
end)

-- Toggle note public/private
toggleVisibilityEvent.OnServerEvent:Connect(function(player, noteId)
    local data = playerDataCache[player.UserId]
    if not data then return end

    for _, note in data.notes do
        if note.id == noteId and note.authorId == player.UserId then
            note.isPublic = not note.isPublic
            note.modified = os.time()

            -- Rebuild
            if noteModels[noteId] then
                noteModels[noteId]:Destroy()
            end
            local model = NoteManager.buildNoteModel(note, notesFolder)
            noteModels[noteId] = model
            break
        end
    end
end)

-- Create a folder (room)
createFolderEvent.OnServerEvent:Connect(function(player, folderName)
    local data = playerDataCache[player.UserId]
    if not data then return end
    if #data.folders >= Config.MaxRooms then return end
    if type(folderName) ~= "string" then return end

    folderName = string.sub(folderName, 1, 30)

    local folder = {
        id = NoteManager.generateId(),
        name = folderName,
        themeIndex = (#data.folders % #Config.RoomThemes) + 1,
    }
    table.insert(data.folders, folder)

    -- Build the room with player-specific slot
    local slot = playerSlots[player.UserId] or 0
    local model = NoteManager.buildRoom(folder, #data.folders, slot)
    roomModels[folder.id] = model

    noteUpdatedEvent:FireAllClients("folderCreated", player.Name, folder.id, folderName)
end)

-- Delete a folder (room) -- notes move to lobby (no folder)
deleteFolderEvent.OnServerEvent:Connect(function(player, folderId)
    local data = playerDataCache[player.UserId]
    if not data then return end
    if type(folderId) ~= "string" then return end

    -- Move notes out of this folder
    for _, note in data.notes do
        if note.folderId == folderId then
            note.folderId = nil
        end
    end

    -- Remove the folder
    for i, folder in data.folders do
        if folder.id == folderId then
            table.remove(data.folders, i)
            break
        end
    end

    -- Destroy the room
    if roomModels[folderId] then
        roomModels[folderId]:Destroy()
        roomModels[folderId] = nil
    end

    -- Rebuild notes (some moved)
    rebuildPlayerNotes(player)
end)

-- Request all data (client asks on join)
requestDataEvent.OnServerInvoke = function(player)
    local data = playerDataCache[player.UserId]
    if not data then return nil end
    return NoteManager.serialize(data)
end

-- Read a specific note's full content
readNoteEvent.OnServerInvoke = function(player, noteId)
    -- Search all players' notes for this noteId
    for userId, data in playerDataCache do
        for _, note in data.notes do
            if note.id == noteId then
                -- Check visibility
                if note.isPublic or note.authorId == player.UserId then
                    return {
                        title = note.title,
                        body = note.body,
                        authorName = note.authorName,
                        isPublic = note.isPublic,
                        isOwner = (note.authorId == player.UserId),
                        created = note.created,
                        modified = note.modified,
                    }
                else
                    return { title = "Private Note", body = "This note is private.", authorName = note.authorName, isPublic = false, isOwner = false }
                end
            end
        end
    end
    return nil
end

------------------------------------------------------------------------
-- Game close: save all
------------------------------------------------------------------------

game:BindToClose(function()
    for _, player in Players:GetPlayers() do
        savePlayerData(player)
    end
end)

print("[BulletinBoard] Server initialized")
