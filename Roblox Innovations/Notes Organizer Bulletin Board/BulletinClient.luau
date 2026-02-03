--[[
    BulletinClient.luau
    LocalScript -- place in StarterPlayerScripts

    Client-side UI for Notes Organizer Bulletin Board:
    - Note creation panel with title, body, folder, and placement mode
    - Raycasting to place notes on walls/floors/surfaces
    - Note reading overlay when interacting with existing notes
    - Folder creation dialog
    - Activity feed
]]

local Players = game:GetService("Players")
local UserInputService = game:GetService("UserInputService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Lighting = game:GetService("Lighting")

local Config = require(ReplicatedStorage:WaitForChild("BulletinConfig"))
local remotes = ReplicatedStorage:WaitForChild("BulletinRemotes")
local createNoteEvent = remotes:WaitForChild("CreateNote")
local updateNoteEvent = remotes:WaitForChild("UpdateNote")
local deleteNoteEvent = remotes:WaitForChild("DeleteNote")
local createFolderEvent = remotes:WaitForChild("CreateFolder")
local deleteFolderEvent = remotes:WaitForChild("DeleteFolder")
local toggleVisibilityEvent = remotes:WaitForChild("ToggleVisibility")
local requestDataEvent = remotes:WaitForChild("RequestData")
local readNoteEvent = remotes:WaitForChild("ReadNote")
local noteUpdatedEvent = remotes:WaitForChild("NoteUpdated")

local player = Players.LocalPlayer
local mouse = player:GetMouse()
local camera = workspace.CurrentCamera

------------------------------------------------------------------------
-- Lighting
------------------------------------------------------------------------

Lighting.ClockTime = 10
Lighting.Ambient = Color3.fromRGB(40, 42, 50)
Lighting.OutdoorAmbient = Color3.fromRGB(50, 55, 65)

------------------------------------------------------------------------
-- State
------------------------------------------------------------------------

local placementMode = false
local placementPreview: Part? = nil
local myFolders: { { id: string, name: string } } = {}

------------------------------------------------------------------------
-- GUI Setup
------------------------------------------------------------------------

local screenGui = Instance.new("ScreenGui")
screenGui.Name = "BulletinHUD"
screenGui.ResetOnSpawn = false
screenGui.Parent = player:WaitForChild("PlayerGui")

-- ===== CREATE PANEL (left side) =====
local createPanel = Instance.new("Frame")
createPanel.Name = "CreatePanel"
createPanel.Size = UDim2.new(0, 280, 0, 360)
createPanel.Position = UDim2.new(0, 16, 0.5, -180)
createPanel.BackgroundColor3 = Color3.fromRGB(25, 28, 35)
createPanel.BackgroundTransparency = 0.1
createPanel.BorderSizePixel = 0
createPanel.Visible = false
createPanel.Parent = screenGui

local panelCorner = Instance.new("UICorner")
panelCorner.CornerRadius = UDim.new(0, 10)
panelCorner.Parent = createPanel

local panelStroke = Instance.new("UIStroke")
panelStroke.Color = Color3.fromRGB(60, 65, 80)
panelStroke.Thickness = 1
panelStroke.Parent = createPanel

-- Panel title
local panelTitle = Instance.new("TextLabel")
panelTitle.Size = UDim2.new(1, 0, 0, 36)
panelTitle.Position = UDim2.new(0, 0, 0, 4)
panelTitle.BackgroundTransparency = 1
panelTitle.Text = "New Note"
panelTitle.TextColor3 = Color3.fromRGB(200, 200, 210)
panelTitle.TextSize = 18
panelTitle.Font = Enum.Font.BuilderSansBold
panelTitle.Parent = createPanel

-- Title input
local titleInput = Instance.new("TextBox")
titleInput.Name = "TitleInput"
titleInput.Size = UDim2.new(1, -20, 0, 32)
titleInput.Position = UDim2.new(0, 10, 0, 42)
titleInput.BackgroundColor3 = Color3.fromRGB(35, 38, 48)
titleInput.BorderSizePixel = 0
titleInput.PlaceholderText = "Note title..."
titleInput.PlaceholderColor3 = Color3.fromRGB(100, 100, 110)
titleInput.Text = ""
titleInput.TextColor3 = Color3.fromRGB(220, 220, 230)
titleInput.TextSize = 14
titleInput.Font = Enum.Font.BuilderSans
titleInput.TextXAlignment = Enum.TextXAlignment.Left
titleInput.ClearTextOnFocus = false
titleInput.Parent = createPanel

local titleCorner = Instance.new("UICorner")
titleCorner.CornerRadius = UDim.new(0, 6)
titleCorner.Parent = titleInput

local titlePad = Instance.new("UIPadding")
titlePad.PaddingLeft = UDim.new(0, 8)
titlePad.Parent = titleInput

-- Body input
local bodyInput = Instance.new("TextBox")
bodyInput.Name = "BodyInput"
bodyInput.Size = UDim2.new(1, -20, 0, 130)
bodyInput.Position = UDim2.new(0, 10, 0, 82)
bodyInput.BackgroundColor3 = Color3.fromRGB(35, 38, 48)
bodyInput.BorderSizePixel = 0
bodyInput.PlaceholderText = "Write your note..."
bodyInput.PlaceholderColor3 = Color3.fromRGB(100, 100, 110)
bodyInput.Text = ""
bodyInput.TextColor3 = Color3.fromRGB(220, 220, 230)
bodyInput.TextSize = 13
bodyInput.Font = Enum.Font.BuilderSans
bodyInput.TextXAlignment = Enum.TextXAlignment.Left
bodyInput.TextYAlignment = Enum.TextYAlignment.Top
bodyInput.MultiLine = true
bodyInput.TextWrapped = true
bodyInput.ClearTextOnFocus = false
bodyInput.Parent = createPanel

local bodyCorner = Instance.new("UICorner")
bodyCorner.CornerRadius = UDim.new(0, 6)
bodyCorner.Parent = bodyInput

local bodyPad = Instance.new("UIPadding")
bodyPad.PaddingLeft = UDim.new(0, 8)
bodyPad.PaddingTop = UDim.new(0, 6)
bodyPad.Parent = bodyInput

-- Folder label
local folderLabel = Instance.new("TextLabel")
folderLabel.Size = UDim2.new(0, 50, 0, 24)
folderLabel.Position = UDim2.new(0, 10, 0, 222)
folderLabel.BackgroundTransparency = 1
folderLabel.Text = "Folder:"
folderLabel.TextColor3 = Color3.fromRGB(140, 140, 150)
folderLabel.TextSize = 13
folderLabel.Font = Enum.Font.BuilderSans
folderLabel.TextXAlignment = Enum.TextXAlignment.Left
folderLabel.Parent = createPanel

-- Folder selector (text button that cycles)
local folderSelector = Instance.new("TextButton")
folderSelector.Name = "FolderSelector"
folderSelector.Size = UDim2.new(1, -80, 0, 28)
folderSelector.Position = UDim2.new(0, 65, 0, 220)
folderSelector.BackgroundColor3 = Color3.fromRGB(35, 38, 48)
folderSelector.BorderSizePixel = 0
folderSelector.Text = "  Lobby (no folder)"
folderSelector.TextColor3 = Color3.fromRGB(180, 180, 190)
folderSelector.TextSize = 12
folderSelector.Font = Enum.Font.BuilderSans
folderSelector.TextXAlignment = Enum.TextXAlignment.Left
folderSelector.Parent = createPanel

local selCorner = Instance.new("UICorner")
selCorner.CornerRadius = UDim.new(0, 6)
selCorner.Parent = folderSelector

local selectedFolderIndex = 0  -- 0 = no folder (lobby)

folderSelector.MouseButton1Click:Connect(function()
    selectedFolderIndex = (selectedFolderIndex + 1) % (#myFolders + 1)
    if selectedFolderIndex == 0 then
        folderSelector.Text = "  Lobby (no folder)"
    else
        folderSelector.Text = "  " .. myFolders[selectedFolderIndex].name
    end
end)

-- Place button
local placeBtn = Instance.new("TextButton")
placeBtn.Name = "PlaceButton"
placeBtn.Size = UDim2.new(1, -20, 0, 36)
placeBtn.Position = UDim2.new(0, 10, 0, 260)
placeBtn.BackgroundColor3 = Color3.fromRGB(50, 90, 70)
placeBtn.BorderSizePixel = 0
placeBtn.Text = "Place on Surface"
placeBtn.TextColor3 = Color3.fromRGB(220, 230, 220)
placeBtn.TextSize = 14
placeBtn.Font = Enum.Font.BuilderSansBold
placeBtn.Parent = createPanel

local placeBtnCorner = Instance.new("UICorner")
placeBtnCorner.CornerRadius = UDim.new(0, 8)
placeBtnCorner.Parent = placeBtn

-- Cancel button
local cancelBtn = Instance.new("TextButton")
cancelBtn.Name = "CancelButton"
cancelBtn.Size = UDim2.new(1, -20, 0, 28)
cancelBtn.Position = UDim2.new(0, 10, 0, 304)
cancelBtn.BackgroundColor3 = Color3.fromRGB(60, 40, 40)
cancelBtn.BorderSizePixel = 0
cancelBtn.Text = "Cancel"
cancelBtn.TextColor3 = Color3.fromRGB(200, 180, 180)
cancelBtn.TextSize = 13
cancelBtn.Font = Enum.Font.BuilderSans
cancelBtn.Parent = createPanel

local cancelCorner = Instance.new("UICorner")
cancelCorner.CornerRadius = UDim.new(0, 6)
cancelCorner.Parent = cancelBtn

-- ===== READ OVERLAY (center) =====
local readOverlay = Instance.new("Frame")
readOverlay.Name = "ReadOverlay"
readOverlay.Size = UDim2.new(0, 420, 0, 340)
readOverlay.Position = UDim2.new(0.5, -210, 0.5, -170)
readOverlay.BackgroundColor3 = Color3.fromRGB(250, 245, 230)
readOverlay.BackgroundTransparency = 0.05
readOverlay.BorderSizePixel = 0
readOverlay.Visible = false
readOverlay.Parent = screenGui

local readCorner = Instance.new("UICorner")
readCorner.CornerRadius = UDim.new(0, 10)
readCorner.Parent = readOverlay

local readStroke = Instance.new("UIStroke")
readStroke.Color = Color3.fromRGB(180, 170, 150)
readStroke.Thickness = 2
readStroke.Parent = readOverlay

local readTitle = Instance.new("TextLabel")
readTitle.Name = "ReadTitle"
readTitle.Size = UDim2.new(1, -20, 0, 36)
readTitle.Position = UDim2.new(0, 10, 0, 10)
readTitle.BackgroundTransparency = 1
readTitle.Text = ""
readTitle.TextColor3 = Config.TitleColor
readTitle.TextSize = 22
readTitle.Font = Enum.Font.BuilderSansBold
readTitle.TextXAlignment = Enum.TextXAlignment.Left
readTitle.TextTruncate = Enum.TextTruncate.AtEnd
readTitle.Parent = readOverlay

local readBody = Instance.new("TextLabel")
readBody.Name = "ReadBody"
readBody.Size = UDim2.new(1, -20, 1, -100)
readBody.Position = UDim2.new(0, 10, 0, 50)
readBody.BackgroundTransparency = 1
readBody.Text = ""
readBody.TextColor3 = Config.BodyColor
readBody.TextSize = 15
readBody.Font = Enum.Font.BuilderSans
readBody.TextXAlignment = Enum.TextXAlignment.Left
readBody.TextYAlignment = Enum.TextYAlignment.Top
readBody.TextWrapped = true
readBody.Parent = readOverlay

local readAuthor = Instance.new("TextLabel")
readAuthor.Name = "ReadAuthor"
readAuthor.Size = UDim2.new(1, -20, 0, 20)
readAuthor.Position = UDim2.new(0, 10, 1, -40)
readAuthor.BackgroundTransparency = 1
readAuthor.Text = ""
readAuthor.TextColor3 = Color3.fromRGB(140, 135, 125)
readAuthor.TextSize = 12
readAuthor.Font = Enum.Font.BuilderSans
readAuthor.TextXAlignment = Enum.TextXAlignment.Right
readAuthor.Parent = readOverlay

local closeReadBtn = Instance.new("TextButton")
closeReadBtn.Size = UDim2.new(0, 30, 0, 30)
closeReadBtn.Position = UDim2.new(1, -35, 0, 5)
closeReadBtn.BackgroundTransparency = 1
closeReadBtn.Text = "X"
closeReadBtn.TextColor3 = Color3.fromRGB(120, 110, 100)
closeReadBtn.TextSize = 18
closeReadBtn.Font = Enum.Font.BuilderSansBold
closeReadBtn.Parent = readOverlay

closeReadBtn.MouseButton1Click:Connect(function()
    readOverlay.Visible = false
end)

-- ===== TOOLBAR (bottom center) =====
local toolbar = Instance.new("Frame")
toolbar.Name = "Toolbar"
toolbar.Size = UDim2.new(0, 340, 0, 44)
toolbar.Position = UDim2.new(0.5, -170, 1, -60)
toolbar.BackgroundColor3 = Color3.fromRGB(25, 28, 35)
toolbar.BackgroundTransparency = 0.15
toolbar.BorderSizePixel = 0
toolbar.Parent = screenGui

local tbCorner = Instance.new("UICorner")
tbCorner.CornerRadius = UDim.new(0, 10)
tbCorner.Parent = toolbar

local tbStroke = Instance.new("UIStroke")
tbStroke.Color = Color3.fromRGB(60, 65, 80)
tbStroke.Thickness = 1
tbStroke.Parent = toolbar

-- New Note button
local newNoteBtn = Instance.new("TextButton")
newNoteBtn.Size = UDim2.new(0, 100, 0, 30)
newNoteBtn.Position = UDim2.new(0, 10, 0.5, -15)
newNoteBtn.BackgroundColor3 = Color3.fromRGB(50, 80, 120)
newNoteBtn.BorderSizePixel = 0
newNoteBtn.Text = "+ New Note"
newNoteBtn.TextColor3 = Color3.fromRGB(220, 225, 240)
newNoteBtn.TextSize = 13
newNoteBtn.Font = Enum.Font.BuilderSansBold
newNoteBtn.Parent = toolbar

local nnCorner = Instance.new("UICorner")
nnCorner.CornerRadius = UDim.new(0, 6)
nnCorner.Parent = newNoteBtn

-- New Folder button
local newFolderBtn = Instance.new("TextButton")
newFolderBtn.Size = UDim2.new(0, 100, 0, 30)
newFolderBtn.Position = UDim2.new(0, 120, 0.5, -15)
newFolderBtn.BackgroundColor3 = Color3.fromRGB(70, 60, 100)
newFolderBtn.BorderSizePixel = 0
newFolderBtn.Text = "+ New Room"
newFolderBtn.TextColor3 = Color3.fromRGB(210, 200, 230)
newFolderBtn.TextSize = 13
newFolderBtn.Font = Enum.Font.BuilderSansBold
newFolderBtn.Parent = toolbar

local nfCorner = Instance.new("UICorner")
nfCorner.CornerRadius = UDim.new(0, 6)
nfCorner.Parent = newFolderBtn

-- Note count
local noteCountLabel = Instance.new("TextLabel")
noteCountLabel.Size = UDim2.new(0, 90, 0, 30)
noteCountLabel.Position = UDim2.new(0, 235, 0.5, -15)
noteCountLabel.BackgroundTransparency = 1
noteCountLabel.Text = "0 notes"
noteCountLabel.TextColor3 = Color3.fromRGB(120, 120, 130)
noteCountLabel.TextSize = 12
noteCountLabel.Font = Enum.Font.BuilderSans
noteCountLabel.TextXAlignment = Enum.TextXAlignment.Right
noteCountLabel.Parent = toolbar

-- ===== FEED (top right) =====
local feedFrame = Instance.new("Frame")
feedFrame.Name = "ActivityFeed"
feedFrame.Size = UDim2.new(0, 280, 0, 150)
feedFrame.Position = UDim2.new(1, -296, 0, 16)
feedFrame.BackgroundTransparency = 1
feedFrame.ClipsDescendants = true
feedFrame.Parent = screenGui

local feedLayout = Instance.new("UIListLayout")
feedLayout.SortOrder = Enum.SortOrder.LayoutOrder
feedLayout.Padding = UDim.new(0, 3)
feedLayout.VerticalAlignment = Enum.VerticalAlignment.Bottom
feedLayout.Parent = feedFrame

local feedCount = 0

------------------------------------------------------------------------
-- Feed notifications
------------------------------------------------------------------------

local function addFeedEntry(text: string)
    feedCount += 1
    local entry = Instance.new("TextLabel")
    entry.Size = UDim2.new(1, 0, 0, 22)
    entry.LayoutOrder = feedCount
    entry.BackgroundColor3 = Color3.fromRGB(25, 28, 35)
    entry.BackgroundTransparency = 0.4
    entry.BorderSizePixel = 0
    entry.Text = "  " .. text
    entry.TextColor3 = Color3.fromRGB(160, 165, 175)
    entry.TextSize = 11
    entry.Font = Enum.Font.BuilderSans
    entry.TextXAlignment = Enum.TextXAlignment.Left
    entry.TextTruncate = Enum.TextTruncate.AtEnd
    entry.Parent = feedFrame

    local eCorner = Instance.new("UICorner")
    eCorner.CornerRadius = UDim.new(0, 4)
    eCorner.Parent = entry

    task.delay(12, function()
        if entry.Parent then entry:Destroy() end
    end)
end

noteUpdatedEvent.OnClientEvent:Connect(function(action, authorName, noteId, noteTitle)
    if action == "created" then
        addFeedEntry(authorName .. " pinned: " .. noteTitle)
    elseif action == "updated" then
        addFeedEntry(authorName .. " edited: " .. noteTitle)
    elseif action == "deleted" then
        addFeedEntry(authorName .. " removed a note")
    elseif action == "folderCreated" then
        addFeedEntry(authorName .. " created room: " .. noteTitle)
        -- Resolve pending folder ID for the local player
        if authorName == player.Name then
            for _, f in myFolders do
                if f.id == "pending" and f.name == noteTitle then
                    f.id = noteId
                    break
                end
            end
        end
    end
end)

------------------------------------------------------------------------
-- Load initial data
------------------------------------------------------------------------

task.spawn(function()
    local rawData = requestDataEvent:InvokeServer()
    if rawData then
        local HttpService = game:GetService("HttpService")
        local success, data = pcall(function()
            return HttpService:JSONDecode(rawData)
        end)
        if success and data then
            myFolders = data.folders or {}
            noteCountLabel.Text = tostring(#(data.notes or {})) .. " notes"
        end
    end
end)

------------------------------------------------------------------------
-- Placement mode
------------------------------------------------------------------------

local function startPlacement()
    placementMode = true
    createPanel.Visible = false

    -- Create preview ghost note
    placementPreview = Instance.new("Part")
    placementPreview.Name = "PlacementPreview"
    placementPreview.Size = Config.NotePartSize
    placementPreview.Anchored = true
    placementPreview.CanCollide = false
    placementPreview.Material = Enum.Material.SmoothPlastic
    placementPreview.Color = Config.NoteSurfaceColor
    placementPreview.Transparency = 0.5
    placementPreview.Parent = workspace

    addFeedEntry("Click a surface to place your note...")
end

local function cancelPlacement()
    placementMode = false
    if placementPreview then
        placementPreview:Destroy()
        placementPreview = nil
    end
end

local function finishPlacement(position: Vector3, normal: Vector3)
    placementMode = false
    if placementPreview then
        placementPreview:Destroy()
        placementPreview = nil
    end

    local noteTitle = titleInput.Text
    if noteTitle == "" then noteTitle = "Untitled Note" end
    local noteBody = bodyInput.Text
    local folderId = if selectedFolderIndex > 0 and myFolders[selectedFolderIndex]
        then myFolders[selectedFolderIndex].id
        else ""

    local placedPos = position + normal * Config.PlacementOffset
    createNoteEvent:FireServer(
        noteTitle, noteBody, folderId,
        placedPos.X, placedPos.Y, placedPos.Z,
        normal.X, normal.Y, normal.Z
    )

    -- Reset form
    titleInput.Text = ""
    bodyInput.Text = ""
    selectedFolderIndex = 0
    folderSelector.Text = "  Lobby (no folder)"
end

------------------------------------------------------------------------
-- Mouse tracking for placement
------------------------------------------------------------------------

local function updatePlacementPreview()
    if not placementMode or not placementPreview then return end

    local ray = camera:ScreenPointToRay(mouse.X, mouse.Y)
    local raycastParams = RaycastParams.new()
    raycastParams.FilterType = Enum.RaycastFilterType.Exclude
    raycastParams.FilterDescendantsInstances = { placementPreview, player.Character }

    local result = workspace:Raycast(ray.Origin, ray.Direction * Config.PlacementRange, raycastParams)

    if result then
        local pos = result.Position + result.Normal * Config.PlacementOffset
        local lookAt = pos + result.Normal
        placementPreview.CFrame = CFrame.lookAt(pos, lookAt)
        placementPreview.Transparency = 0.4
    else
        placementPreview.Transparency = 0.8
    end
end

------------------------------------------------------------------------
-- Input handling
------------------------------------------------------------------------

UserInputService.InputBegan:Connect(function(input, processed)
    if processed then return end

    if input.UserInputType == Enum.UserInputType.MouseButton1 and placementMode then
        local ray = camera:ScreenPointToRay(mouse.X, mouse.Y)
        local raycastParams = RaycastParams.new()
        raycastParams.FilterType = Enum.RaycastFilterType.Exclude
        raycastParams.FilterDescendantsInstances = { placementPreview, player.Character }

        local result = workspace:Raycast(ray.Origin, ray.Direction * Config.PlacementRange, raycastParams)
        if result then
            finishPlacement(result.Position, result.Normal)
        end
    end

    if input.KeyCode == Enum.KeyCode.Escape then
        if placementMode then
            cancelPlacement()
        elseif readOverlay.Visible then
            readOverlay.Visible = false
        elseif createPanel.Visible then
            createPanel.Visible = false
        end
    end
end)

game:GetService("RunService").RenderStepped:Connect(updatePlacementPreview)

------------------------------------------------------------------------
-- Button connections
------------------------------------------------------------------------

newNoteBtn.MouseButton1Click:Connect(function()
    createPanel.Visible = not createPanel.Visible
    if createPanel.Visible then
        titleInput:CaptureFocus()
    end
end)

placeBtn.MouseButton1Click:Connect(startPlacement)
cancelBtn.MouseButton1Click:Connect(function()
    createPanel.Visible = false
    cancelPlacement()
end)

newFolderBtn.MouseButton1Click:Connect(function()
    -- Simple text input via a popup approach: use the title input temporarily
    local folderName = "Room " .. tostring(#myFolders + 1)
    createFolderEvent:FireServer(folderName)
    table.insert(myFolders, { id = "pending", name = folderName })
    addFeedEntry("Created room: " .. folderName)
end)

------------------------------------------------------------------------
-- Proximity prompt handler (reading notes)
------------------------------------------------------------------------

local function onPromptTriggered(prompt: ProximityPrompt)
    local frame = prompt.Parent
    if not frame then return end

    local noteId = frame:GetAttribute("NoteId")
    if not noteId then return end

    local noteData = readNoteEvent:InvokeServer(noteId)
    if not noteData then return end

    readTitle.Text = noteData.title
    readBody.Text = noteData.body
    readAuthor.Text = "- " .. noteData.authorName
    readOverlay.Visible = true
end

-- Connect to all proximity prompts (existing and future)
workspace.DescendantAdded:Connect(function(desc)
    if desc:IsA("ProximityPrompt") and desc.Name == "ReadPrompt" then
        desc.Triggered:Connect(function()
            onPromptTriggered(desc)
        end)
    end
end)

-- Also connect existing ones
for _, desc in workspace:GetDescendants() do
    if desc:IsA("ProximityPrompt") and desc.Name == "ReadPrompt" then
        desc.Triggered:Connect(function()
            onPromptTriggered(desc)
        end)
    end
end

------------------------------------------------------------------------

print("[BulletinBoard] Client initialized")
