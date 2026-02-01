--[[
    PlannerClient.luau
    LocalScript -- place in StarterPlayer > StarterPlayerScripts

    Client-side UI for the Academic Planner Study Hub.
    Assignment creation/editing panel, syllabus paste parser, desk
    interaction, study group controls, timer controls, and HUD.
]]

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local UserInputService = game:GetService("UserInputService")
local ProximityPromptService = game:GetService("ProximityPromptService")

local Config = require(ReplicatedStorage:WaitForChild("PlannerConfig"))

local player = Players.LocalPlayer
local playerGui = player:WaitForChild("PlayerGui")

------------------------------------------------------------------------
-- Wait for remotes
------------------------------------------------------------------------

local remotes = ReplicatedStorage:WaitForChild("PlannerRemotes")
local createAssignmentEvent = remotes:WaitForChild("CreateAssignment")
local updateAssignmentEvent = remotes:WaitForChild("UpdateAssignment")
local deleteAssignmentEvent = remotes:WaitForChild("DeleteAssignment")
local toggleCompleteEvent = remotes:WaitForChild("ToggleComplete")
local parseSyllabusEvent = remotes:WaitForChild("ParseSyllabus")
local requestDataEvent = remotes:WaitForChild("RequestData")
local assignmentUpdatedEvent = remotes:WaitForChild("AssignmentUpdated")
local joinStudyGroupEvent = remotes:WaitForChild("JoinStudyGroup")
local leaveStudyGroupEvent = remotes:WaitForChild("LeaveStudyGroup")
local startTimerEvent = remotes:WaitForChild("StartTimer")
local pauseTimerEvent = remotes:WaitForChild("PauseTimer")
local resetTimerEvent = remotes:WaitForChild("ResetTimer")
local timerUpdateEvent = remotes:WaitForChild("TimerUpdate")
local studyGroupUpdateEvent = remotes:WaitForChild("StudyGroupUpdate")

------------------------------------------------------------------------
-- Local assignment cache
------------------------------------------------------------------------

local myAssignments: { any } = {}
local currentPanel: string? = nil  -- "planner" | "syllabus" | "studyGroup" | nil

------------------------------------------------------------------------
-- Main ScreenGui
------------------------------------------------------------------------

local screenGui = Instance.new("ScreenGui")
screenGui.Name = "PlannerGui"
screenGui.ResetOnSpawn = false
screenGui.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
screenGui.Parent = playerGui

------------------------------------------------------------------------
-- Toolbar (bottom)
------------------------------------------------------------------------

local toolbar = Instance.new("Frame")
toolbar.Name = "Toolbar"
toolbar.Size = UDim2.new(0, 520, 0, 44)
toolbar.Position = UDim2.new(0.5, -260, 1, -54)
toolbar.BackgroundColor3 = Color3.fromRGB(35, 35, 40)
toolbar.BackgroundTransparency = 0.15
toolbar.BorderSizePixel = 0
toolbar.Parent = screenGui

local toolCorner = Instance.new("UICorner")
toolCorner.CornerRadius = UDim.new(0, 8)
toolCorner.Parent = toolbar

local toolLayout = Instance.new("UIListLayout")
toolLayout.FillDirection = Enum.FillDirection.Horizontal
toolLayout.Padding = UDim.new(0, 8)
toolLayout.VerticalAlignment = Enum.VerticalAlignment.Center
toolLayout.HorizontalAlignment = Enum.HorizontalAlignment.Center
toolLayout.Parent = toolbar

local function makeToolbarButton(name: string, text: string, color: Color3): TextButton
    local btn = Instance.new("TextButton")
    btn.Name = name
    btn.Size = UDim2.new(0, 155, 0, 32)
    btn.BackgroundColor3 = color
    btn.BorderSizePixel = 0
    btn.TextColor3 = Color3.new(1, 1, 1)
    btn.Text = text
    btn.TextSize = 14
    btn.Font = Enum.Font.BuilderSansBold
    btn.Parent = toolbar

    local corner = Instance.new("UICorner")
    corner.CornerRadius = UDim.new(0, 6)
    corner.Parent = btn

    return btn
end

local plannerBtn = makeToolbarButton("PlannerBtn", "+ New Assignment", Color3.fromRGB(45, 74, 62))
local syllabusBtn = makeToolbarButton("SyllabusBtn", "Paste Syllabus", Color3.fromRGB(74, 61, 110))
local studyBtn = makeToolbarButton("StudyBtn", "Study Groups", Color3.fromRGB(74, 90, 110))

------------------------------------------------------------------------
-- HUD: upcoming assignments (top-left)
------------------------------------------------------------------------

local hud = Instance.new("Frame")
hud.Name = "HUD"
hud.Size = UDim2.new(0, 280, 0, 200)
hud.Position = UDim2.new(0, 12, 0, 12)
hud.BackgroundColor3 = Color3.fromRGB(25, 25, 30)
hud.BackgroundTransparency = 0.3
hud.BorderSizePixel = 0
hud.Parent = screenGui

local hudCorner = Instance.new("UICorner")
hudCorner.CornerRadius = UDim.new(0, 8)
hudCorner.Parent = hud

local hudTitle = Instance.new("TextLabel")
hudTitle.Size = UDim2.new(1, 0, 0, 28)
hudTitle.BackgroundTransparency = 1
hudTitle.TextColor3 = Color3.fromRGB(255, 240, 200)
hudTitle.Text = "Upcoming"
hudTitle.TextSize = 16
hudTitle.Font = Enum.Font.BuilderSansBold
hudTitle.TextXAlignment = Enum.TextXAlignment.Left
hudTitle.Parent = hud

local hudTitlePad = Instance.new("UIPadding")
hudTitlePad.PaddingLeft = UDim.new(0, 10)
hudTitlePad.PaddingTop = UDim.new(0, 6)
hudTitlePad.Parent = hudTitle

local hudList = Instance.new("Frame")
hudList.Name = "HUDList"
hudList.Size = UDim2.new(1, -16, 1, -36)
hudList.Position = UDim2.new(0, 8, 0, 32)
hudList.BackgroundTransparency = 1
hudList.Parent = hud

local hudListLayout = Instance.new("UIListLayout")
hudListLayout.Padding = UDim.new(0, 3)
hudListLayout.SortOrder = Enum.SortOrder.LayoutOrder
hudListLayout.Parent = hudList

local hudToggle = true -- visible by default

------------------------------------------------------------------------
-- Notification feed (top-right)
------------------------------------------------------------------------

local feedFrame = Instance.new("Frame")
feedFrame.Name = "Feed"
feedFrame.Size = UDim2.new(0, 260, 0, 160)
feedFrame.Position = UDim2.new(1, -272, 0, 12)
feedFrame.BackgroundTransparency = 1
feedFrame.Parent = screenGui

local feedLayout = Instance.new("UIListLayout")
feedLayout.Padding = UDim.new(0, 4)
feedLayout.VerticalAlignment = Enum.VerticalAlignment.Bottom
feedLayout.SortOrder = Enum.SortOrder.LayoutOrder
feedLayout.Parent = feedFrame

local feedOrder = 0

local function addFeedMessage(msg: string)
    feedOrder += 1
    local label = Instance.new("TextLabel")
    label.Size = UDim2.new(1, 0, 0, 20)
    label.BackgroundColor3 = Color3.fromRGB(30, 30, 35)
    label.BackgroundTransparency = 0.4
    label.BorderSizePixel = 0
    label.TextColor3 = Color3.fromRGB(200, 200, 200)
    label.Text = msg
    label.TextSize = 12
    label.Font = Enum.Font.BuilderSans
    label.TextXAlignment = Enum.TextXAlignment.Left
    label.TextTruncate = Enum.TextTruncate.AtEnd
    label.LayoutOrder = feedOrder
    label.Parent = feedFrame

    local corner = Instance.new("UICorner")
    corner.CornerRadius = UDim.new(0, 4)
    corner.Parent = label

    local pad = Instance.new("UIPadding")
    pad.PaddingLeft = UDim.new(0, 6)
    pad.Parent = label

    -- Fade and remove
    task.delay(5, function()
        if label.Parent then
            for i = 0, 10 do
                label.TextTransparency = i / 10
                label.BackgroundTransparency = 0.4 + (i / 10) * 0.6
                task.wait(0.05)
            end
            label:Destroy()
        end
    end)

    -- Cap feed items
    local children = feedFrame:GetChildren()
    local count = 0
    for _, c in children do
        if c:IsA("TextLabel") then count += 1 end
    end
    if count > 8 then
        for _, c in children do
            if c:IsA("TextLabel") then
                c:Destroy()
                break
            end
        end
    end
end

------------------------------------------------------------------------
-- Planner panel (assignment creation/list)
------------------------------------------------------------------------

local plannerPanel = Instance.new("Frame")
plannerPanel.Name = "PlannerPanel"
plannerPanel.Size = UDim2.new(0, 420, 0, 500)
plannerPanel.Position = UDim2.new(0.5, -210, 0.5, -250)
plannerPanel.BackgroundColor3 = Color3.fromRGB(30, 30, 35)
plannerPanel.BackgroundTransparency = 0.05
plannerPanel.BorderSizePixel = 0
plannerPanel.Visible = false
plannerPanel.Parent = screenGui

local ppCorner = Instance.new("UICorner")
ppCorner.CornerRadius = UDim.new(0, 10)
ppCorner.Parent = plannerPanel

-- Title bar
local ppTitle = Instance.new("TextLabel")
ppTitle.Size = UDim2.new(1, 0, 0, 36)
ppTitle.BackgroundColor3 = Color3.fromRGB(45, 74, 62)
ppTitle.BorderSizePixel = 0
ppTitle.TextColor3 = Color3.new(1, 1, 1)
ppTitle.Text = "Assignment Planner"
ppTitle.TextSize = 16
ppTitle.Font = Enum.Font.BuilderSansBold
ppTitle.Parent = plannerPanel

local ppTitleCorner = Instance.new("UICorner")
ppTitleCorner.CornerRadius = UDim.new(0, 10)
ppTitleCorner.Parent = ppTitle

-- Input fields
local function makeInputField(parent: Frame, yOffset: number, placeholderText: string, name: string): TextBox
    local label = Instance.new("TextLabel")
    label.Size = UDim2.new(0, 110, 0, 28)
    label.Position = UDim2.new(0, 12, 0, yOffset)
    label.BackgroundTransparency = 1
    label.TextColor3 = Color3.fromRGB(180, 180, 180)
    label.Text = placeholderText
    label.TextSize = 13
    label.Font = Enum.Font.BuilderSans
    label.TextXAlignment = Enum.TextXAlignment.Left
    label.Parent = parent

    local box = Instance.new("TextBox")
    box.Name = name
    box.Size = UDim2.new(0, 270, 0, 28)
    box.Position = UDim2.new(0, 130, 0, yOffset)
    box.BackgroundColor3 = Color3.fromRGB(20, 20, 25)
    box.BorderSizePixel = 0
    box.TextColor3 = Color3.fromRGB(230, 230, 230)
    box.PlaceholderText = placeholderText
    box.PlaceholderColor3 = Color3.fromRGB(80, 80, 80)
    box.Text = ""
    box.TextSize = 13
    box.Font = Enum.Font.BuilderSans
    box.ClearTextOnFocus = false
    box.Parent = parent

    local boxCorner = Instance.new("UICorner")
    boxCorner.CornerRadius = UDim.new(0, 4)
    boxCorner.Parent = box

    return box
end

local abbrevInput = makeInputField(plannerPanel, 48, "Class Abbrev", "AbbrevInput")
local classInput = makeInputField(plannerPanel, 84, "Class Name", "ClassInput")
local assignInput = makeInputField(plannerPanel, 120, "Assignment", "AssignInput")
local dateInput = makeInputField(plannerPanel, 156, "Due Date", "DateInput")
local timeInput = makeInputField(plannerPanel, 192, "Due Time", "TimeInput")

-- Add button
local addBtn = Instance.new("TextButton")
addBtn.Name = "AddBtn"
addBtn.Size = UDim2.new(0, 150, 0, 32)
addBtn.Position = UDim2.new(0.5, -75, 0, 232)
addBtn.BackgroundColor3 = Color3.fromRGB(45, 74, 62)
addBtn.BorderSizePixel = 0
addBtn.TextColor3 = Color3.new(1, 1, 1)
addBtn.Text = "Add Assignment"
addBtn.TextSize = 14
addBtn.Font = Enum.Font.BuilderSansBold
addBtn.Parent = plannerPanel

local addBtnCorner = Instance.new("UICorner")
addBtnCorner.CornerRadius = UDim.new(0, 6)
addBtnCorner.Parent = addBtn

-- Assignment list (scrollable)
local listDivider = Instance.new("Frame")
listDivider.Size = UDim2.new(0.9, 0, 0, 1)
listDivider.Position = UDim2.new(0.05, 0, 0, 274)
listDivider.BackgroundColor3 = Color3.fromRGB(60, 60, 65)
listDivider.BorderSizePixel = 0
listDivider.Parent = plannerPanel

local listTitle = Instance.new("TextLabel")
listTitle.Size = UDim2.new(1, 0, 0, 24)
listTitle.Position = UDim2.new(0, 0, 0, 280)
listTitle.BackgroundTransparency = 1
listTitle.TextColor3 = Color3.fromRGB(180, 180, 180)
listTitle.Text = "Your Assignments"
listTitle.TextSize = 13
listTitle.Font = Enum.Font.BuilderSansBold
listTitle.Parent = plannerPanel

local scrollFrame = Instance.new("ScrollingFrame")
scrollFrame.Name = "AssignmentList"
scrollFrame.Size = UDim2.new(1, -20, 0, 190)
scrollFrame.Position = UDim2.new(0, 10, 0, 306)
scrollFrame.BackgroundTransparency = 1
scrollFrame.ScrollBarThickness = 4
scrollFrame.ScrollBarImageColor3 = Color3.fromRGB(100, 100, 100)
scrollFrame.CanvasSize = UDim2.new(0, 0, 0, 0)
scrollFrame.Parent = plannerPanel

local scrollLayout = Instance.new("UIListLayout")
scrollLayout.Padding = UDim.new(0, 4)
scrollLayout.SortOrder = Enum.SortOrder.LayoutOrder
scrollLayout.Parent = scrollFrame

------------------------------------------------------------------------
-- Syllabus paste panel
------------------------------------------------------------------------

local syllabusPanel = Instance.new("Frame")
syllabusPanel.Name = "SyllabusPanel"
syllabusPanel.Size = UDim2.new(0, 440, 0, 420)
syllabusPanel.Position = UDim2.new(0.5, -220, 0.5, -210)
syllabusPanel.BackgroundColor3 = Color3.fromRGB(30, 30, 35)
syllabusPanel.BackgroundTransparency = 0.05
syllabusPanel.BorderSizePixel = 0
syllabusPanel.Visible = false
syllabusPanel.Parent = screenGui

local spCorner = Instance.new("UICorner")
spCorner.CornerRadius = UDim.new(0, 10)
spCorner.Parent = syllabusPanel

local spTitle = Instance.new("TextLabel")
spTitle.Size = UDim2.new(1, 0, 0, 36)
spTitle.BackgroundColor3 = Color3.fromRGB(74, 61, 110)
spTitle.BorderSizePixel = 0
spTitle.TextColor3 = Color3.new(1, 1, 1)
spTitle.Text = "Paste Syllabus Text"
spTitle.TextSize = 16
spTitle.Font = Enum.Font.BuilderSansBold
spTitle.Parent = syllabusPanel

local spTitleCorner = Instance.new("UICorner")
spTitleCorner.CornerRadius = UDim.new(0, 10)
spTitleCorner.Parent = spTitle

-- Hint
local spHint = Instance.new("TextLabel")
spHint.Size = UDim2.new(0.9, 0, 0, 36)
spHint.Position = UDim2.new(0.05, 0, 0, 42)
spHint.BackgroundTransparency = 1
spHint.TextColor3 = Color3.fromRGB(140, 160, 180)
spHint.Text = "Paste syllabus or schedule text below. The system will detect assignments and dates."
spHint.TextSize = 12
spHint.Font = Enum.Font.BuilderSans
spHint.TextWrapped = true
spHint.TextXAlignment = Enum.TextXAlignment.Left
spHint.Parent = syllabusPanel

-- TextBox for syllabus
local syllabusInput = Instance.new("TextBox")
syllabusInput.Name = "SyllabusInput"
syllabusInput.Size = UDim2.new(0.9, 0, 0, 140)
syllabusInput.Position = UDim2.new(0.05, 0, 0, 84)
syllabusInput.BackgroundColor3 = Color3.fromRGB(15, 15, 20)
syllabusInput.BorderSizePixel = 0
syllabusInput.TextColor3 = Color3.fromRGB(200, 200, 200)
syllabusInput.PlaceholderText = "Paste syllabus text here..."
syllabusInput.PlaceholderColor3 = Color3.fromRGB(70, 70, 70)
syllabusInput.Text = ""
syllabusInput.TextSize = 12
syllabusInput.Font = Enum.Font.RobotoMono
syllabusInput.TextWrapped = true
syllabusInput.TextXAlignment = Enum.TextXAlignment.Left
syllabusInput.TextYAlignment = Enum.TextYAlignment.Top
syllabusInput.ClearTextOnFocus = false
syllabusInput.MultiLine = true
syllabusInput.Parent = syllabusPanel

local syllInputCorner = Instance.new("UICorner")
syllInputCorner.CornerRadius = UDim.new(0, 6)
syllInputCorner.Parent = syllabusInput

local syllInputPad = Instance.new("UIPadding")
syllInputPad.PaddingLeft = UDim.new(0, 8)
syllInputPad.PaddingTop = UDim.new(0, 8)
syllInputPad.Parent = syllabusInput

-- Parse button
local parseBtn = Instance.new("TextButton")
parseBtn.Name = "ParseBtn"
parseBtn.Size = UDim2.new(0, 140, 0, 32)
parseBtn.Position = UDim2.new(0.5, -70, 0, 232)
parseBtn.BackgroundColor3 = Color3.fromRGB(74, 61, 110)
parseBtn.BorderSizePixel = 0
parseBtn.TextColor3 = Color3.new(1, 1, 1)
parseBtn.Text = "Parse Text"
parseBtn.TextSize = 14
parseBtn.Font = Enum.Font.BuilderSansBold
parseBtn.Parent = syllabusPanel

local parseBtnCorner = Instance.new("UICorner")
parseBtnCorner.CornerRadius = UDim.new(0, 6)
parseBtnCorner.Parent = parseBtn

-- Results area (scrollable)
local parseResults = Instance.new("ScrollingFrame")
parseResults.Name = "ParseResults"
parseResults.Size = UDim2.new(0.9, 0, 0, 140)
parseResults.Position = UDim2.new(0.05, 0, 0, 272)
parseResults.BackgroundTransparency = 1
parseResults.ScrollBarThickness = 4
parseResults.ScrollBarImageColor3 = Color3.fromRGB(100, 100, 100)
parseResults.CanvasSize = UDim2.new(0, 0, 0, 0)
parseResults.Visible = false
parseResults.Parent = syllabusPanel

local parseResultsLayout = Instance.new("UIListLayout")
parseResultsLayout.Padding = UDim.new(0, 4)
parseResultsLayout.SortOrder = Enum.SortOrder.LayoutOrder
parseResultsLayout.Parent = parseResults

------------------------------------------------------------------------
-- Study group panel
------------------------------------------------------------------------

local studyPanel = Instance.new("Frame")
studyPanel.Name = "StudyPanel"
studyPanel.Size = UDim2.new(0, 380, 0, 360)
studyPanel.Position = UDim2.new(0.5, -190, 0.5, -180)
studyPanel.BackgroundColor3 = Color3.fromRGB(30, 30, 35)
studyPanel.BackgroundTransparency = 0.05
studyPanel.BorderSizePixel = 0
studyPanel.Visible = false
studyPanel.Parent = screenGui

local sgCorner = Instance.new("UICorner")
sgCorner.CornerRadius = UDim.new(0, 10)
sgCorner.Parent = studyPanel

local sgTitle = Instance.new("TextLabel")
sgTitle.Size = UDim2.new(1, 0, 0, 36)
sgTitle.BackgroundColor3 = Color3.fromRGB(74, 90, 110)
sgTitle.BorderSizePixel = 0
sgTitle.TextColor3 = Color3.new(1, 1, 1)
sgTitle.Text = "Study Groups"
sgTitle.TextSize = 16
sgTitle.Font = Enum.Font.BuilderSansBold
sgTitle.Parent = studyPanel

local sgTitleCorner = Instance.new("UICorner")
sgTitleCorner.CornerRadius = UDim.new(0, 10)
sgTitleCorner.Parent = sgTitle

local sgScroll = Instance.new("ScrollingFrame")
sgScroll.Name = "GroupList"
sgScroll.Size = UDim2.new(1, -20, 1, -46)
sgScroll.Position = UDim2.new(0, 10, 0, 42)
sgScroll.BackgroundTransparency = 1
sgScroll.ScrollBarThickness = 4
sgScroll.ScrollBarImageColor3 = Color3.fromRGB(100, 100, 100)
sgScroll.CanvasSize = UDim2.new(0, 0, 0, 0)
sgScroll.Parent = studyPanel

local sgScrollLayout = Instance.new("UIListLayout")
sgScrollLayout.Padding = UDim.new(0, 6)
sgScrollLayout.SortOrder = Enum.SortOrder.LayoutOrder
sgScrollLayout.Parent = sgScroll

-- Track study group state locally
local studyGroupState: { [number]: { members: { string }, duration: number, remaining: number, status: string } } = {}

------------------------------------------------------------------------
-- Panel management
------------------------------------------------------------------------

local function closeAllPanels()
    plannerPanel.Visible = false
    syllabusPanel.Visible = false
    studyPanel.Visible = false
    currentPanel = nil
end

local function togglePanel(panelName: string, panel: Frame)
    if currentPanel == panelName then
        closeAllPanels()
    else
        closeAllPanels()
        panel.Visible = true
        currentPanel = panelName
    end
end

plannerBtn.MouseButton1Click:Connect(function()
    togglePanel("planner", plannerPanel)
end)

syllabusBtn.MouseButton1Click:Connect(function()
    togglePanel("syllabus", syllabusPanel)
end)

studyBtn.MouseButton1Click:Connect(function()
    togglePanel("studyGroup", studyPanel)
end)

------------------------------------------------------------------------
-- Update HUD
------------------------------------------------------------------------

local function updateHUD()
    -- Clear existing
    for _, child in hudList:GetChildren() do
        if child:IsA("TextLabel") then child:Destroy() end
    end

    -- Sort: incomplete, soonest first
    local sorted = {}
    for _, a in myAssignments do
        if not a.completed then
            table.insert(sorted, a)
        end
    end

    table.sort(sorted, function(a, b)
        local tsA = a._timestamp or 0
        local tsB = b._timestamp or 0
        if tsA > 0 and tsB > 0 then return tsA < tsB end
        if tsA > 0 then return true end
        if tsB > 0 then return false end
        return (a.created or 0) < (b.created or 0)
    end)

    for i, a in sorted do
        if i > 6 then break end

        local statusColor = Config.StatusColors.noDate
        if a.dueDate and a.dueDate ~= "" then
            local now = os.time()
            if a._timestamp then
                if a._timestamp < now then
                    statusColor = Config.StatusColors.overdue
                elseif a._timestamp - now < Config.DueSoonThreshold then
                    statusColor = Config.StatusColors.dueSoon
                else
                    statusColor = Config.StatusColors.upcoming
                end
            end
        end

        local entry = Instance.new("TextLabel")
        entry.Size = UDim2.new(1, 0, 0, 24)
        entry.BackgroundColor3 = statusColor
        entry.BackgroundTransparency = 0.7
        entry.BorderSizePixel = 0
        entry.TextColor3 = Color3.fromRGB(230, 230, 230)
        entry.Text = "  " .. (a.abbreviation or "") .. " - " .. (a.assignment or "")
        entry.TextSize = 12
        entry.Font = Enum.Font.BuilderSans
        entry.TextXAlignment = Enum.TextXAlignment.Left
        entry.TextTruncate = Enum.TextTruncate.AtEnd
        entry.LayoutOrder = i
        entry.Parent = hudList

        local entryCorner = Instance.new("UICorner")
        entryCorner.CornerRadius = UDim.new(0, 4)
        entryCorner.Parent = entry
    end

    if #sorted == 0 then
        local empty = Instance.new("TextLabel")
        empty.Size = UDim2.new(1, 0, 0, 24)
        empty.BackgroundTransparency = 1
        empty.TextColor3 = Color3.fromRGB(100, 100, 100)
        empty.Text = "No upcoming assignments"
        empty.TextSize = 12
        empty.Font = Enum.Font.BuilderSans
        empty.Parent = hudList
    end
end

------------------------------------------------------------------------
-- Update assignment list in planner panel
------------------------------------------------------------------------

local function updateAssignmentList()
    for _, child in scrollFrame:GetChildren() do
        if child:IsA("Frame") then child:Destroy() end
    end

    for i, a in myAssignments do
        local row = Instance.new("Frame")
        row.Size = UDim2.new(1, 0, 0, 36)
        row.BackgroundColor3 = if a.completed then Color3.fromRGB(35, 40, 35) else Color3.fromRGB(40, 40, 45)
        row.BackgroundTransparency = 0.3
        row.BorderSizePixel = 0
        row.LayoutOrder = i
        row.Parent = scrollFrame

        local rowCorner = Instance.new("UICorner")
        rowCorner.CornerRadius = UDim.new(0, 4)
        rowCorner.Parent = row

        -- Status indicator bar
        local statusColor = Config.StatusColors.noDate
        if a.completed then
            statusColor = Config.StatusColors.completed
        elseif a._timestamp then
            local now = os.time()
            if a._timestamp < now then
                statusColor = Config.StatusColors.overdue
            elseif a._timestamp - now < Config.DueSoonThreshold then
                statusColor = Config.StatusColors.dueSoon
            else
                statusColor = Config.StatusColors.upcoming
            end
        end

        local statusBar = Instance.new("Frame")
        statusBar.Size = UDim2.new(0, 4, 0.7, 0)
        statusBar.Position = UDim2.new(0, 4, 0.15, 0)
        statusBar.BackgroundColor3 = statusColor
        statusBar.BorderSizePixel = 0
        statusBar.Parent = row

        -- Assignment text
        local text = Instance.new("TextLabel")
        text.Size = UDim2.new(1, -80, 1, 0)
        text.Position = UDim2.new(0, 14, 0, 0)
        text.BackgroundTransparency = 1
        text.TextColor3 = if a.completed then Color3.fromRGB(120, 120, 120) else Color3.fromRGB(220, 220, 220)
        text.Text = (a.abbreviation or "") .. " | " .. (a.assignment or "") .. (if a.dueDate ~= "" then " | " .. a.dueDate else "")
        text.TextSize = 12
        text.Font = Enum.Font.BuilderSans
        text.TextXAlignment = Enum.TextXAlignment.Left
        text.TextTruncate = Enum.TextTruncate.AtEnd
        text.Parent = row

        -- Complete toggle button
        local completeBtn = Instance.new("TextButton")
        completeBtn.Size = UDim2.new(0, 24, 0, 24)
        completeBtn.Position = UDim2.new(1, -62, 0.5, -12)
        completeBtn.BackgroundColor3 = if a.completed then Color3.fromRGB(80, 140, 80) else Color3.fromRGB(50, 50, 55)
        completeBtn.BorderSizePixel = 0
        completeBtn.TextColor3 = Color3.new(1, 1, 1)
        completeBtn.Text = if a.completed then "v" else ""
        completeBtn.TextSize = 14
        completeBtn.Font = Enum.Font.BuilderSansBold
        completeBtn.Parent = row

        local cbCorner = Instance.new("UICorner")
        cbCorner.CornerRadius = UDim.new(0, 4)
        cbCorner.Parent = completeBtn

        completeBtn.MouseButton1Click:Connect(function()
            toggleCompleteEvent:FireServer(a.id)
        end)

        -- Delete button
        local delBtn = Instance.new("TextButton")
        delBtn.Size = UDim2.new(0, 24, 0, 24)
        delBtn.Position = UDim2.new(1, -32, 0.5, -12)
        delBtn.BackgroundColor3 = Color3.fromRGB(100, 40, 40)
        delBtn.BorderSizePixel = 0
        delBtn.TextColor3 = Color3.new(1, 1, 1)
        delBtn.Text = "x"
        delBtn.TextSize = 14
        delBtn.Font = Enum.Font.BuilderSansBold
        delBtn.Parent = row

        local dbCorner = Instance.new("UICorner")
        dbCorner.CornerRadius = UDim.new(0, 4)
        dbCorner.Parent = delBtn

        delBtn.MouseButton1Click:Connect(function()
            deleteAssignmentEvent:FireServer(a.id)
        end)
    end

    -- Update canvas size
    scrollFrame.CanvasSize = UDim2.new(0, 0, 0, #myAssignments * 40)
end

------------------------------------------------------------------------
-- Add assignment
------------------------------------------------------------------------

addBtn.MouseButton1Click:Connect(function()
    local abbrev = abbrevInput.Text
    local className = classInput.Text
    local assignName = assignInput.Text
    local dueDate = dateInput.Text
    local dueTime = timeInput.Text

    if assignName == "" then return end

    createAssignmentEvent:FireServer(abbrev, className, assignName, dueDate, dueTime)

    -- Clear inputs
    abbrevInput.Text = ""
    classInput.Text = ""
    assignInput.Text = ""
    dateInput.Text = ""
    timeInput.Text = ""

    addFeedMessage("Assignment added")
end)

------------------------------------------------------------------------
-- Parse syllabus
------------------------------------------------------------------------

parseBtn.MouseButton1Click:Connect(function()
    local text = syllabusInput.Text
    if text == "" then return end

    -- Clear old results
    for _, child in parseResults:GetChildren() do
        if child:IsA("Frame") then child:Destroy() end
    end

    local results = parseSyllabusEvent:InvokeServer(text)
    if not results or #results == 0 then
        parseResults.Visible = true
        local noResults = Instance.new("TextLabel")
        noResults.Size = UDim2.new(1, 0, 0, 24)
        noResults.BackgroundTransparency = 1
        noResults.TextColor3 = Color3.fromRGB(120, 120, 120)
        noResults.Text = "No assignments detected."
        noResults.TextSize = 12
        noResults.Font = Enum.Font.BuilderSans
        noResults.Parent = parseResults
        return
    end

    parseResults.Visible = true

    for i, result in results do
        local row = Instance.new("Frame")
        row.Size = UDim2.new(1, 0, 0, 40)
        row.BackgroundColor3 = Color3.fromRGB(35, 35, 40)
        row.BorderSizePixel = 0
        row.LayoutOrder = i
        row.Parent = parseResults

        local rowCorner = Instance.new("UICorner")
        rowCorner.CornerRadius = UDim.new(0, 4)
        rowCorner.Parent = row

        local textLabel = Instance.new("TextLabel")
        textLabel.Size = UDim2.new(1, -80, 0, 20)
        textLabel.Position = UDim2.new(0, 8, 0, 2)
        textLabel.BackgroundTransparency = 1
        textLabel.TextColor3 = Color3.fromRGB(200, 200, 200)
        textLabel.Text = result.text or ""
        textLabel.TextSize = 11
        textLabel.Font = Enum.Font.BuilderSans
        textLabel.TextXAlignment = Enum.TextXAlignment.Left
        textLabel.TextTruncate = Enum.TextTruncate.AtEnd
        textLabel.Parent = row

        if result.date and result.date ~= "" then
            local dateLabel = Instance.new("TextLabel")
            dateLabel.Size = UDim2.new(1, -80, 0, 16)
            dateLabel.Position = UDim2.new(0, 8, 0, 22)
            dateLabel.BackgroundTransparency = 1
            dateLabel.TextColor3 = Color3.fromRGB(140, 160, 180)
            dateLabel.Text = "Date: " .. result.date
            dateLabel.TextSize = 10
            dateLabel.Font = Enum.Font.BuilderSans
            dateLabel.TextXAlignment = Enum.TextXAlignment.Left
            dateLabel.Parent = row
        end

        -- Add button
        local addToPlanner = Instance.new("TextButton")
        addToPlanner.Size = UDim2.new(0, 50, 0, 24)
        addToPlanner.Position = UDim2.new(1, -58, 0.5, -12)
        addToPlanner.BackgroundColor3 = Color3.fromRGB(45, 74, 62)
        addToPlanner.BorderSizePixel = 0
        addToPlanner.TextColor3 = Color3.new(1, 1, 1)
        addToPlanner.Text = "Add"
        addToPlanner.TextSize = 12
        addToPlanner.Font = Enum.Font.BuilderSansBold
        addToPlanner.Parent = row

        local abCorner = Instance.new("UICorner")
        abCorner.CornerRadius = UDim.new(0, 4)
        abCorner.Parent = addToPlanner

        addToPlanner.MouseButton1Click:Connect(function()
            createAssignmentEvent:FireServer("", "", result.text or "", result.date or "", "")
            addToPlanner.Text = "Added"
            addToPlanner.BackgroundColor3 = Color3.fromRGB(60, 60, 65)
            addFeedMessage("Parsed assignment added")
        end)
    end

    parseResults.CanvasSize = UDim2.new(0, 0, 0, #results * 44)
end)

------------------------------------------------------------------------
-- Update study group panel
------------------------------------------------------------------------

local function updateStudyGroupPanel()
    for _, child in sgScroll:GetChildren() do
        if child:IsA("Frame") then child:Destroy() end
    end

    for roomIdx = 1, Config.MaxStudyRooms do
        local state = studyGroupState[roomIdx]
        local members = if state then state.members else {}
        local status = if state then state.status else "idle"
        local remaining = if state then state.remaining else Config.DefaultTimerDuration

        local card = Instance.new("Frame")
        card.Size = UDim2.new(1, 0, 0, 70)
        card.BackgroundColor3 = Color3.fromRGB(38, 38, 44)
        card.BorderSizePixel = 0
        card.LayoutOrder = roomIdx
        card.Parent = sgScroll

        local cardCorner = Instance.new("UICorner")
        cardCorner.CornerRadius = UDim.new(0, 6)
        cardCorner.Parent = card

        -- Accent bar
        local accent = Instance.new("Frame")
        accent.Size = UDim2.new(0, 4, 0.8, 0)
        accent.Position = UDim2.new(0, 4, 0.1, 0)
        accent.BackgroundColor3 = Config.CourseColors[((roomIdx - 1) % #Config.CourseColors) + 1]
        accent.BorderSizePixel = 0
        accent.Parent = card

        -- Room label
        local roomLabel = Instance.new("TextLabel")
        roomLabel.Size = UDim2.new(0, 120, 0, 20)
        roomLabel.Position = UDim2.new(0, 14, 0, 6)
        roomLabel.BackgroundTransparency = 1
        roomLabel.TextColor3 = Color3.fromRGB(220, 220, 220)
        roomLabel.Text = "Room " .. roomIdx
        roomLabel.TextSize = 14
        roomLabel.Font = Enum.Font.BuilderSansBold
        roomLabel.TextXAlignment = Enum.TextXAlignment.Left
        roomLabel.Parent = card

        -- Timer display
        local mins = math.floor(remaining / 60)
        local secs = remaining % 60
        local timerLabel = Instance.new("TextLabel")
        timerLabel.Size = UDim2.new(0, 80, 0, 20)
        timerLabel.Position = UDim2.new(0, 140, 0, 6)
        timerLabel.BackgroundTransparency = 1
        timerLabel.TextColor3 = if status == "running" then Color3.fromRGB(100, 200, 100) elseif status == "paused" then Color3.fromRGB(220, 180, 60) else Color3.fromRGB(150, 150, 150)
        timerLabel.Text = string.format("%02d:%02d", mins, secs)
        timerLabel.TextSize = 14
        timerLabel.Font = Enum.Font.RobotoMono
        timerLabel.TextXAlignment = Enum.TextXAlignment.Left
        timerLabel.Parent = card

        -- Members
        local memberText = if #members > 0 then table.concat(members, ", ") else "Empty"
        local memberLabel = Instance.new("TextLabel")
        memberLabel.Size = UDim2.new(1, -20, 0, 16)
        memberLabel.Position = UDim2.new(0, 14, 0, 28)
        memberLabel.BackgroundTransparency = 1
        memberLabel.TextColor3 = Color3.fromRGB(140, 140, 140)
        memberLabel.Text = memberText
        memberLabel.TextSize = 11
        memberLabel.Font = Enum.Font.BuilderSans
        memberLabel.TextXAlignment = Enum.TextXAlignment.Left
        memberLabel.TextTruncate = Enum.TextTruncate.AtEnd
        memberLabel.Parent = card

        -- Buttons row
        local isInGroup = false
        for _, name in members do
            if name == player.Name then
                isInGroup = true
                break
            end
        end

        local joinLeaveBtn = Instance.new("TextButton")
        joinLeaveBtn.Size = UDim2.new(0, 55, 0, 22)
        joinLeaveBtn.Position = UDim2.new(0, 14, 0, 46)
        joinLeaveBtn.BackgroundColor3 = if isInGroup then Color3.fromRGB(100, 50, 50) else Color3.fromRGB(45, 74, 62)
        joinLeaveBtn.BorderSizePixel = 0
        joinLeaveBtn.TextColor3 = Color3.new(1, 1, 1)
        joinLeaveBtn.Text = if isInGroup then "Leave" else "Join"
        joinLeaveBtn.TextSize = 11
        joinLeaveBtn.Font = Enum.Font.BuilderSansBold
        joinLeaveBtn.Parent = card

        local jlCorner = Instance.new("UICorner")
        jlCorner.CornerRadius = UDim.new(0, 4)
        jlCorner.Parent = joinLeaveBtn

        joinLeaveBtn.MouseButton1Click:Connect(function()
            if isInGroup then
                leaveStudyGroupEvent:FireServer(roomIdx)
            else
                joinStudyGroupEvent:FireServer(roomIdx)
            end
        end)

        if isInGroup then
            local startPauseBtn = Instance.new("TextButton")
            startPauseBtn.Size = UDim2.new(0, 55, 0, 22)
            startPauseBtn.Position = UDim2.new(0, 76, 0, 46)
            startPauseBtn.BackgroundColor3 = Color3.fromRGB(74, 90, 110)
            startPauseBtn.BorderSizePixel = 0
            startPauseBtn.TextColor3 = Color3.new(1, 1, 1)
            startPauseBtn.Text = if status == "running" then "Pause" else "Start"
            startPauseBtn.TextSize = 11
            startPauseBtn.Font = Enum.Font.BuilderSansBold
            startPauseBtn.Parent = card

            local spBtnCorner = Instance.new("UICorner")
            spBtnCorner.CornerRadius = UDim.new(0, 4)
            spBtnCorner.Parent = startPauseBtn

            startPauseBtn.MouseButton1Click:Connect(function()
                if status == "running" then
                    pauseTimerEvent:FireServer(roomIdx)
                elseif status == "paused" then
                    pauseTimerEvent:FireServer(roomIdx) -- resume
                else
                    startTimerEvent:FireServer(roomIdx, nil)
                end
            end)

            local resetBtn = Instance.new("TextButton")
            resetBtn.Size = UDim2.new(0, 55, 0, 22)
            resetBtn.Position = UDim2.new(0, 138, 0, 46)
            resetBtn.BackgroundColor3 = Color3.fromRGB(80, 60, 40)
            resetBtn.BorderSizePixel = 0
            resetBtn.TextColor3 = Color3.new(1, 1, 1)
            resetBtn.Text = "Reset"
            resetBtn.TextSize = 11
            resetBtn.Font = Enum.Font.BuilderSansBold
            resetBtn.Parent = card

            local rBtnCorner = Instance.new("UICorner")
            rBtnCorner.CornerRadius = UDim.new(0, 4)
            rBtnCorner.Parent = resetBtn

            resetBtn.MouseButton1Click:Connect(function()
                resetTimerEvent:FireServer(roomIdx)
            end)
        end
    end

    sgScroll.CanvasSize = UDim2.new(0, 0, 0, Config.MaxStudyRooms * 76)
end

------------------------------------------------------------------------
-- Load initial data from server
------------------------------------------------------------------------

local function loadData()
    local HttpService = game:GetService("HttpService")
    local serialized = requestDataEvent:InvokeServer()
    if not serialized then return end

    local ok, parsed = pcall(function()
        return HttpService:JSONDecode(serialized)
    end)
    if not ok or type(parsed) ~= "table" then return end

    myAssignments = {}
    if type(parsed.assignments) == "table" then
        for _, a in parsed.assignments do
            if type(a) == "table" then
                -- Pre-compute timestamp for sorting
                a._timestamp = nil
                if a.dueDate and a.dueDate ~= "" then
                    local month, day, year = string.match(a.dueDate, "(%d+)/(%d+)/(%d+)")
                    if not month then
                        month, day, year = string.match(a.dueDate, "(%d+)-(%d+)-(%d+)")
                    end
                    if month then
                        local y = tonumber(year) or 2026
                        if y < 100 then y = y + 2000 end
                        local okTs, ts = pcall(function()
                            return os.time({ year = y, month = tonumber(month), day = tonumber(day), hour = 23, min = 59, sec = 0 })
                        end)
                        if okTs then a._timestamp = ts end
                    end
                end
                table.insert(myAssignments, a)
            end
        end
    end

    updateHUD()
    updateAssignmentList()
end

task.spawn(function()
    task.wait(1) -- let remotes initialize
    loadData()
end)

------------------------------------------------------------------------
-- Listen for server updates
------------------------------------------------------------------------

assignmentUpdatedEvent.OnClientEvent:Connect(function(action, assignmentId)
    -- Reload all data (simplest approach)
    loadData()

    if action == "created" then
        addFeedMessage("Assignment created")
    elseif action == "deleted" then
        addFeedMessage("Assignment removed")
    elseif action == "toggled" then
        addFeedMessage("Assignment status toggled")
    end
end)

studyGroupUpdateEvent.OnClientEvent:Connect(function(roomIndex, memberNames, duration, remaining, status)
    studyGroupState[roomIndex] = {
        members = memberNames,
        duration = duration,
        remaining = remaining,
        status = status,
    }
    if currentPanel == "studyGroup" then
        updateStudyGroupPanel()
    end
end)

timerUpdateEvent.OnClientEvent:Connect(function(roomIndex, status, remaining)
    if status == "finished" then
        addFeedMessage("Study Room " .. roomIndex .. " timer finished!")
    end
end)

------------------------------------------------------------------------
-- Desk ProximityPrompt: open planner
------------------------------------------------------------------------

ProximityPromptService.PromptTriggered:Connect(function(prompt, triggeringPlayer)
    if triggeringPlayer ~= player then return end

    local parent = prompt.Parent
    if not parent then return end

    if parent:GetAttribute("IsPlannerDesk") then
        togglePanel("planner", plannerPanel)
    elseif parent:GetAttribute("IsWhiteboard") then
        local location = parent:GetAttribute("Location")
        if location == "StudyRoom" then
            togglePanel("studyGroup", studyPanel)
            updateStudyGroupPanel()
        elseif location == "Library" then
            addFeedMessage("Viewing library board")
        end
    end
end)

------------------------------------------------------------------------
-- Keyboard shortcuts
------------------------------------------------------------------------

UserInputService.InputBegan:Connect(function(input, gameProcessed)
    if gameProcessed then return end

    if input.KeyCode == Enum.KeyCode.Escape then
        closeAllPanels()
    elseif input.KeyCode == Enum.KeyCode.H then
        hudToggle = not hudToggle
        hud.Visible = hudToggle
    end
end)

------------------------------------------------------------------------
-- Initialize study group panel
------------------------------------------------------------------------

for i = 1, Config.MaxStudyRooms do
    studyGroupState[i] = {
        members = {},
        duration = Config.DefaultTimerDuration,
        remaining = Config.DefaultTimerDuration,
        status = "idle",
    }
end
updateStudyGroupPanel()

print("[StudyHub] Client initialized")
