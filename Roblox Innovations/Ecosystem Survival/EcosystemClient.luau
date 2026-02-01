--[[
    EcosystemClient.luau
    LocalScript -- place in StarterPlayer > StarterPlayerScripts

    Client-side UI for Ecosystem Survival.
    Species selection screen, energy bar, action buttons
    (eat, sprint, reproduce), population HUD, ecosystem health
    display, and event log.
]]

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local UserInputService = game:GetService("UserInputService")

local Config = require(ReplicatedStorage:WaitForChild("EcosystemConfig"))

local player = Players.LocalPlayer
local playerGui = player:WaitForChild("PlayerGui")

------------------------------------------------------------------------
-- Wait for remotes
------------------------------------------------------------------------

local remotes = ReplicatedStorage:WaitForChild("EcosystemRemotes")
local chooseSpeciesEvent = remotes:WaitForChild("ChooseSpecies")
local playerStatsEvent = remotes:WaitForChild("PlayerStats")
local eatActionEvent = remotes:WaitForChild("EatAction")
local reproduceActionEvent = remotes:WaitForChild("ReproduceAction")
local sprintEvent = remotes:WaitForChild("SprintState")
local populationEvent = remotes:WaitForChild("PopulationUpdate")
local eventLogEvent = remotes:WaitForChild("EventLog")
local playerDiedEvent = remotes:WaitForChild("PlayerDied")

------------------------------------------------------------------------
-- State
------------------------------------------------------------------------

local selectedSpecies: string? = nil
local currentEnergy = 0
local maxEnergy = 100
local huntCooldown = 0
local isAlive = false
local isSprinting = false

------------------------------------------------------------------------
-- Main ScreenGui
------------------------------------------------------------------------

local screenGui = Instance.new("ScreenGui")
screenGui.Name = "EcosystemGui"
screenGui.ResetOnSpawn = false
screenGui.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
screenGui.Parent = playerGui

------------------------------------------------------------------------
-- Species selection screen
------------------------------------------------------------------------

local selectionScreen = Instance.new("Frame")
selectionScreen.Name = "SelectionScreen"
selectionScreen.Size = UDim2.new(1, 0, 1, 0)
selectionScreen.BackgroundColor3 = Color3.fromRGB(10, 12, 18)
selectionScreen.BackgroundTransparency = 0.2
selectionScreen.BorderSizePixel = 0
selectionScreen.Parent = screenGui

local selTitle = Instance.new("TextLabel")
selTitle.Size = UDim2.new(0, 500, 0, 60)
selTitle.Position = UDim2.new(0.5, -250, 0, 80)
selTitle.BackgroundTransparency = 1
selTitle.TextColor3 = Color3.fromRGB(200, 220, 255)
selTitle.Text = "ECOSYSTEM SURVIVAL"
selTitle.TextSize = 40
selTitle.Font = Enum.Font.GothamBold
selTitle.Parent = selectionScreen

local selSubtitle = Instance.new("TextLabel")
selSubtitle.Size = UDim2.new(0, 500, 0, 30)
selSubtitle.Position = UDim2.new(0.5, -250, 0, 140)
selSubtitle.BackgroundTransparency = 1
selSubtitle.TextColor3 = Color3.fromRGB(140, 150, 160)
selSubtitle.Text = "Choose your species"
selSubtitle.TextSize = 18
selSubtitle.Font = Enum.Font.Gotham
selSubtitle.Parent = selectionScreen

-- Species cards
local function makeSpeciesCard(species: string, xOffset: number)
    local specData = Config.Species[species]

    local card = Instance.new("Frame")
    card.Size = UDim2.new(0, 220, 0, 320)
    card.Position = UDim2.new(0.5, xOffset, 0.5, -140)
    card.BackgroundColor3 = Color3.fromRGB(25, 28, 35)
    card.BorderSizePixel = 0
    card.Parent = selectionScreen

    local cardCorner = Instance.new("UICorner")
    cardCorner.CornerRadius = UDim.new(0, 12)
    cardCorner.Parent = card

    -- Color bar at top
    local colorBar = Instance.new("Frame")
    colorBar.Size = UDim2.new(1, 0, 0, 6)
    colorBar.BackgroundColor3 = specData.color
    colorBar.BorderSizePixel = 0
    colorBar.Parent = card

    local barCorner = Instance.new("UICorner")
    barCorner.CornerRadius = UDim.new(0, 12)
    barCorner.Parent = colorBar

    -- Species icon (colored circle)
    local icon = Instance.new("Frame")
    icon.Size = UDim2.new(0, 60, 0, 60)
    icon.Position = UDim2.new(0.5, -30, 0, 30)
    icon.BackgroundColor3 = specData.color
    icon.BorderSizePixel = 0
    icon.Parent = card

    local iconCorner = Instance.new("UICorner")
    iconCorner.CornerRadius = UDim.new(0.5, 0)
    iconCorner.Parent = icon

    -- Name
    local nameLabel = Instance.new("TextLabel")
    nameLabel.Size = UDim2.new(1, 0, 0, 30)
    nameLabel.Position = UDim2.new(0, 0, 0, 100)
    nameLabel.BackgroundTransparency = 1
    nameLabel.TextColor3 = Color3.new(1, 1, 1)
    nameLabel.Text = specData.name
    nameLabel.TextSize = 20
    nameLabel.Font = Enum.Font.GothamBold
    nameLabel.Parent = card

    -- Stats
    local stats = {
        "Speed: " .. specData.baseSpeed,
        "Energy: " .. specData.maxEnergy,
        "Vision: " .. specData.visionRange,
        "Eat range: " .. specData.eatRange,
    }

    if species == "herbivore" then
        table.insert(stats, "Eats: Plants")
        table.insert(stats, "Flees: Predators")
    else
        table.insert(stats, "Eats: Herbivores")
        table.insert(stats, "Hunt cooldown: " .. specData.huntCooldown .. "s")
    end

    for i, stat in stats do
        local statLabel = Instance.new("TextLabel")
        statLabel.Size = UDim2.new(0.85, 0, 0, 18)
        statLabel.Position = UDim2.new(0.075, 0, 0, 135 + (i - 1) * 20)
        statLabel.BackgroundTransparency = 1
        statLabel.TextColor3 = Color3.fromRGB(160, 165, 175)
        statLabel.Text = stat
        statLabel.TextSize = 12
        statLabel.Font = Enum.Font.Gotham
        statLabel.TextXAlignment = Enum.TextXAlignment.Left
        statLabel.Parent = card
    end

    -- Choose button
    local chooseBtn = Instance.new("TextButton")
    chooseBtn.Size = UDim2.new(0.8, 0, 0, 36)
    chooseBtn.Position = UDim2.new(0.1, 0, 1, -50)
    chooseBtn.BackgroundColor3 = specData.color
    chooseBtn.BorderSizePixel = 0
    chooseBtn.TextColor3 = Color3.new(1, 1, 1)
    chooseBtn.Text = "Play as " .. specData.name
    chooseBtn.TextSize = 14
    chooseBtn.Font = Enum.Font.GothamBold
    chooseBtn.Parent = card

    local btnCorner = Instance.new("UICorner")
    btnCorner.CornerRadius = UDim.new(0, 8)
    btnCorner.Parent = chooseBtn

    chooseBtn.MouseButton1Click:Connect(function()
        selectedSpecies = species
        chooseSpeciesEvent:FireServer(species)
        selectionScreen.Visible = false
    end)
end

makeSpeciesCard("herbivore", -130)
makeSpeciesCard("predator", 130)

------------------------------------------------------------------------
-- Energy bar (bottom-center)
------------------------------------------------------------------------

local energyFrame = Instance.new("Frame")
energyFrame.Name = "EnergyFrame"
energyFrame.Size = UDim2.new(0, 300, 0, 40)
energyFrame.Position = UDim2.new(0.5, -150, 1, -90)
energyFrame.BackgroundColor3 = Color3.fromRGB(25, 25, 30)
energyFrame.BackgroundTransparency = 0.2
energyFrame.BorderSizePixel = 0
energyFrame.Visible = false
energyFrame.Parent = screenGui

local energyCorner = Instance.new("UICorner")
energyCorner.CornerRadius = UDim.new(0, 8)
energyCorner.Parent = energyFrame

local energyLabel = Instance.new("TextLabel")
energyLabel.Size = UDim2.new(0, 60, 1, 0)
energyLabel.BackgroundTransparency = 1
energyLabel.TextColor3 = Color3.fromRGB(200, 200, 200)
energyLabel.Text = "Energy"
energyLabel.TextSize = 12
energyLabel.Font = Enum.Font.GothamBold
energyLabel.Parent = energyFrame

local barBg = Instance.new("Frame")
barBg.Size = UDim2.new(0, 220, 0, 16)
barBg.Position = UDim2.new(0, 65, 0.5, -8)
barBg.BackgroundColor3 = Color3.fromRGB(40, 40, 45)
barBg.BorderSizePixel = 0
barBg.Parent = energyFrame

local barCorner = Instance.new("UICorner")
barCorner.CornerRadius = UDim.new(0, 4)
barCorner.Parent = barBg

local barFill = Instance.new("Frame")
barFill.Name = "Fill"
barFill.Size = UDim2.new(0.5, 0, 1, 0)
barFill.BackgroundColor3 = Color3.fromRGB(80, 200, 80)
barFill.BorderSizePixel = 0
barFill.Parent = barBg

local fillCorner = Instance.new("UICorner")
fillCorner.CornerRadius = UDim.new(0, 4)
fillCorner.Parent = barFill

local energyText = Instance.new("TextLabel")
energyText.Size = UDim2.new(1, 0, 1, 0)
energyText.BackgroundTransparency = 1
energyText.TextColor3 = Color3.new(1, 1, 1)
energyText.Text = "50/100"
energyText.TextSize = 11
energyText.Font = Enum.Font.RobotoMono
energyText.Parent = barBg

-- Cooldown indicator
local cooldownLabel = Instance.new("TextLabel")
cooldownLabel.Size = UDim2.new(0, 60, 0, 16)
cooldownLabel.Position = UDim2.new(1, -55, 0.5, -8)
cooldownLabel.BackgroundTransparency = 1
cooldownLabel.TextColor3 = Color3.fromRGB(220, 160, 60)
cooldownLabel.Text = ""
cooldownLabel.TextSize = 11
cooldownLabel.Font = Enum.Font.RobotoMono
cooldownLabel.Parent = energyFrame

------------------------------------------------------------------------
-- Action buttons (bottom toolbar)
------------------------------------------------------------------------

local actionBar = Instance.new("Frame")
actionBar.Name = "ActionBar"
actionBar.Size = UDim2.new(0, 340, 0, 44)
actionBar.Position = UDim2.new(0.5, -170, 1, -44)
actionBar.BackgroundColor3 = Color3.fromRGB(30, 30, 35)
actionBar.BackgroundTransparency = 0.2
actionBar.BorderSizePixel = 0
actionBar.Visible = false
actionBar.Parent = screenGui

local actionCorner = Instance.new("UICorner")
actionCorner.CornerRadius = UDim.new(0, 8)
actionCorner.Parent = actionBar

local actionLayout = Instance.new("UIListLayout")
actionLayout.FillDirection = Enum.FillDirection.Horizontal
actionLayout.Padding = UDim.new(0, 8)
actionLayout.VerticalAlignment = Enum.VerticalAlignment.Center
actionLayout.HorizontalAlignment = Enum.HorizontalAlignment.Center
actionLayout.Parent = actionBar

local function makeActionButton(name: string, text: string, color: Color3): TextButton
    local btn = Instance.new("TextButton")
    btn.Name = name
    btn.Size = UDim2.new(0, 100, 0, 32)
    btn.BackgroundColor3 = color
    btn.BorderSizePixel = 0
    btn.TextColor3 = Color3.new(1, 1, 1)
    btn.Text = text
    btn.TextSize = 13
    btn.Font = Enum.Font.GothamBold
    btn.Parent = actionBar

    local corner = Instance.new("UICorner")
    corner.CornerRadius = UDim.new(0, 6)
    corner.Parent = btn

    return btn
end

local eatBtn = makeActionButton("EatBtn", "Eat [E]", Color3.fromRGB(50, 120, 50))
local sprintBtn = makeActionButton("SprintBtn", "Sprint [Shift]", Color3.fromRGB(60, 90, 130))
local reproduceBtn = makeActionButton("ReproduceBtn", "Reproduce [R]", Color3.fromRGB(130, 90, 50))

------------------------------------------------------------------------
-- Population HUD (top-left)
------------------------------------------------------------------------

local popFrame = Instance.new("Frame")
popFrame.Name = "PopHUD"
popFrame.Size = UDim2.new(0, 200, 0, 140)
popFrame.Position = UDim2.new(0, 12, 0, 12)
popFrame.BackgroundColor3 = Color3.fromRGB(20, 22, 28)
popFrame.BackgroundTransparency = 0.3
popFrame.BorderSizePixel = 0
popFrame.Visible = false
popFrame.Parent = screenGui

local popCorner = Instance.new("UICorner")
popCorner.CornerRadius = UDim.new(0, 8)
popCorner.Parent = popFrame

local popTitle = Instance.new("TextLabel")
popTitle.Size = UDim2.new(1, 0, 0, 24)
popTitle.Position = UDim2.new(0, 0, 0, 4)
popTitle.BackgroundTransparency = 1
popTitle.TextColor3 = Color3.fromRGB(200, 210, 230)
popTitle.Text = "Population"
popTitle.TextSize = 14
popTitle.Font = Enum.Font.GothamBold
popTitle.Parent = popFrame

local function makePopRow(yOffset: number, label: string, color: Color3): TextLabel
    local row = Instance.new("TextLabel")
    row.Size = UDim2.new(1, -16, 0, 18)
    row.Position = UDim2.new(0, 8, 0, yOffset)
    row.BackgroundTransparency = 1
    row.TextColor3 = color
    row.Text = label .. ": 0"
    row.TextSize = 12
    row.Font = Enum.Font.Gotham
    row.TextXAlignment = Enum.TextXAlignment.Left
    row.Parent = popFrame
    return row
end

local plantCountLabel = makePopRow(30, "Plants", Config.PlantColor)
local herbCountLabel = makePopRow(50, "Herbivores", Config.Species.herbivore.color)
local predCountLabel = makePopRow(70, "Predators", Config.Species.predator.color)

-- Health score
local healthLabel = Instance.new("TextLabel")
healthLabel.Size = UDim2.new(1, -16, 0, 22)
healthLabel.Position = UDim2.new(0, 8, 0, 96)
healthLabel.BackgroundTransparency = 1
healthLabel.TextColor3 = Color3.fromRGB(200, 220, 200)
healthLabel.Text = "Health: 50 (Stable)"
healthLabel.TextSize = 13
healthLabel.Font = Enum.Font.GothamBold
healthLabel.TextXAlignment = Enum.TextXAlignment.Left
healthLabel.Parent = popFrame

-- Health bar
local healthBarBg = Instance.new("Frame")
healthBarBg.Size = UDim2.new(0.85, 0, 0, 8)
healthBarBg.Position = UDim2.new(0.075, 0, 0, 122)
healthBarBg.BackgroundColor3 = Color3.fromRGB(40, 40, 45)
healthBarBg.BorderSizePixel = 0
healthBarBg.Parent = popFrame

local healthBarCorner = Instance.new("UICorner")
healthBarCorner.CornerRadius = UDim.new(0, 3)
healthBarCorner.Parent = healthBarBg

local healthBarFill = Instance.new("Frame")
healthBarFill.Name = "Fill"
healthBarFill.Size = UDim2.new(0.5, 0, 1, 0)
healthBarFill.BackgroundColor3 = Color3.fromRGB(80, 180, 80)
healthBarFill.BorderSizePixel = 0
healthBarFill.Parent = healthBarBg

local healthFillCorner = Instance.new("UICorner")
healthFillCorner.CornerRadius = UDim.new(0, 3)
healthFillCorner.Parent = healthBarFill

------------------------------------------------------------------------
-- Event log (top-right)
------------------------------------------------------------------------

local logFrame = Instance.new("Frame")
logFrame.Name = "EventLog"
logFrame.Size = UDim2.new(0, 280, 0, 180)
logFrame.Position = UDim2.new(1, -292, 0, 12)
logFrame.BackgroundTransparency = 1
logFrame.Visible = false
logFrame.Parent = screenGui

local logLayout = Instance.new("UIListLayout")
logLayout.Padding = UDim.new(0, 3)
logLayout.VerticalAlignment = Enum.VerticalAlignment.Bottom
logLayout.SortOrder = Enum.SortOrder.LayoutOrder
logLayout.Parent = logFrame

local logOrder = 0

local function addLogEntry(msg: string)
    logOrder += 1
    local entry = Instance.new("TextLabel")
    entry.Size = UDim2.new(1, 0, 0, 18)
    entry.BackgroundColor3 = Color3.fromRGB(20, 22, 28)
    entry.BackgroundTransparency = 0.4
    entry.BorderSizePixel = 0
    entry.TextColor3 = Color3.fromRGB(180, 185, 195)
    entry.Text = msg
    entry.TextSize = 11
    entry.Font = Enum.Font.Gotham
    entry.TextXAlignment = Enum.TextXAlignment.Left
    entry.TextTruncate = Enum.TextTruncate.AtEnd
    entry.LayoutOrder = logOrder
    entry.Parent = logFrame

    local corner = Instance.new("UICorner")
    corner.CornerRadius = UDim.new(0, 3)
    corner.Parent = entry

    local pad = Instance.new("UIPadding")
    pad.PaddingLeft = UDim.new(0, 6)
    pad.Parent = entry

    -- Fade after 8 seconds
    task.delay(8, function()
        if entry.Parent then
            for i = 0, 10 do
                entry.TextTransparency = i / 10
                entry.BackgroundTransparency = 0.4 + (i / 10) * 0.6
                task.wait(0.05)
            end
            entry:Destroy()
        end
    end)

    -- Cap entries
    local count = 0
    for _, c in logFrame:GetChildren() do
        if c:IsA("TextLabel") then count += 1 end
    end
    if count > 10 then
        for _, c in logFrame:GetChildren() do
            if c:IsA("TextLabel") then
                c:Destroy()
                break
            end
        end
    end
end

------------------------------------------------------------------------
-- Death overlay
------------------------------------------------------------------------

local deathOverlay = Instance.new("Frame")
deathOverlay.Name = "DeathOverlay"
deathOverlay.Size = UDim2.new(1, 0, 1, 0)
deathOverlay.BackgroundColor3 = Color3.fromRGB(60, 10, 10)
deathOverlay.BackgroundTransparency = 0.5
deathOverlay.BorderSizePixel = 0
deathOverlay.Visible = false
deathOverlay.Parent = screenGui

local deathText = Instance.new("TextLabel")
deathText.Size = UDim2.new(0, 400, 0, 80)
deathText.Position = UDim2.new(0.5, -200, 0.4, -40)
deathText.BackgroundTransparency = 1
deathText.TextColor3 = Color3.fromRGB(255, 200, 200)
deathText.Text = "You ran out of energy!\nRespawning..."
deathText.TextSize = 28
deathText.Font = Enum.Font.GothamBold
deathText.TextWrapped = true
deathText.Parent = deathOverlay

------------------------------------------------------------------------
-- Show game UI after species selection
------------------------------------------------------------------------

local function showGameUI()
    energyFrame.Visible = true
    actionBar.Visible = true
    popFrame.Visible = true
    logFrame.Visible = true
end

------------------------------------------------------------------------
-- Update energy display
------------------------------------------------------------------------

local function updateEnergyDisplay()
    local ratio = currentEnergy / maxEnergy
    barFill.Size = UDim2.new(math.clamp(ratio, 0, 1), 0, 1, 0)
    energyText.Text = math.floor(currentEnergy) .. "/" .. math.floor(maxEnergy)

    -- Color based on energy level
    if ratio > 0.6 then
        barFill.BackgroundColor3 = Color3.fromRGB(80, 200, 80)
    elseif ratio > 0.3 then
        barFill.BackgroundColor3 = Color3.fromRGB(220, 180, 60)
    else
        barFill.BackgroundColor3 = Color3.fromRGB(220, 60, 60)
    end

    -- Cooldown
    if huntCooldown > 0 then
        cooldownLabel.Text = string.format("%.1fs", huntCooldown)
    else
        cooldownLabel.Text = ""
    end

    -- Update reproduce button availability
    if selectedSpecies then
        local specData = Config.Species[selectedSpecies]
        if currentEnergy >= specData.reproductionThreshold then
            reproduceBtn.BackgroundColor3 = Color3.fromRGB(130, 90, 50)
        else
            reproduceBtn.BackgroundColor3 = Color3.fromRGB(60, 50, 40)
        end
    end
end

------------------------------------------------------------------------
-- Server event handlers
------------------------------------------------------------------------

playerStatsEvent.OnClientEvent:Connect(function(energy, maxE, cooldown, alive)
    currentEnergy = energy
    maxEnergy = maxE
    huntCooldown = cooldown
    isAlive = alive

    if not selectionScreen.Visible and selectedSpecies then
        showGameUI()
    end

    updateEnergyDisplay()

    deathOverlay.Visible = not alive
end)

populationEvent.OnClientEvent:Connect(function(plants, herbs, preds, health, label)
    plantCountLabel.Text = "Plants: " .. plants
    herbCountLabel.Text = "Herbivores: " .. herbs
    predCountLabel.Text = "Predators: " .. preds
    healthLabel.Text = "Health: " .. health .. " (" .. label .. ")"

    local ratio = health / 100
    healthBarFill.Size = UDim2.new(math.clamp(ratio, 0, 1), 0, 1, 0)

    if health >= 60 then
        healthBarFill.BackgroundColor3 = Color3.fromRGB(80, 180, 80)
    elseif health >= 30 then
        healthBarFill.BackgroundColor3 = Color3.fromRGB(200, 180, 60)
    else
        healthBarFill.BackgroundColor3 = Color3.fromRGB(200, 60, 60)
    end
end)

eventLogEvent.OnClientEvent:Connect(function(msg)
    addLogEntry(msg)
end)

playerDiedEvent.OnClientEvent:Connect(function()
    addLogEntry("You ran out of energy!")
    deathOverlay.Visible = true
    task.delay(Config.RespawnDelay, function()
        deathOverlay.Visible = false
    end)
end)

------------------------------------------------------------------------
-- Action buttons
------------------------------------------------------------------------

eatBtn.MouseButton1Click:Connect(function()
    if selectedSpecies and isAlive then
        eatActionEvent:FireServer()
    end
end)

reproduceBtn.MouseButton1Click:Connect(function()
    if selectedSpecies and isAlive then
        reproduceActionEvent:FireServer()
    end
end)

sprintBtn.MouseButton1Click:Connect(function()
    if selectedSpecies and isAlive then
        isSprinting = not isSprinting
        sprintEvent:FireServer(isSprinting)
        sprintBtn.Text = if isSprinting then "Walking [Shift]" else "Sprint [Shift]"
        sprintBtn.BackgroundColor3 = if isSprinting then Color3.fromRGB(130, 100, 40) else Color3.fromRGB(60, 90, 130)
    end
end)

------------------------------------------------------------------------
-- Keyboard controls
------------------------------------------------------------------------

UserInputService.InputBegan:Connect(function(input, gameProcessed)
    if gameProcessed then return end

    if input.KeyCode == Enum.KeyCode.E then
        if selectedSpecies and isAlive then
            eatActionEvent:FireServer()
        end
    elseif input.KeyCode == Enum.KeyCode.R then
        if selectedSpecies and isAlive then
            reproduceActionEvent:FireServer()
        end
    elseif input.KeyCode == Enum.KeyCode.LeftShift or input.KeyCode == Enum.KeyCode.RightShift then
        if selectedSpecies and isAlive then
            isSprinting = true
            sprintEvent:FireServer(true)
            sprintBtn.Text = "Walking [Shift]"
            sprintBtn.BackgroundColor3 = Color3.fromRGB(130, 100, 40)
        end
    elseif input.KeyCode == Enum.KeyCode.H then
        popFrame.Visible = not popFrame.Visible
    end
end)

UserInputService.InputEnded:Connect(function(input)
    if input.KeyCode == Enum.KeyCode.LeftShift or input.KeyCode == Enum.KeyCode.RightShift then
        if selectedSpecies and isAlive then
            isSprinting = false
            sprintEvent:FireServer(false)
            sprintBtn.Text = "Sprint [Shift]"
            sprintBtn.BackgroundColor3 = Color3.fromRGB(60, 90, 130)
        end
    end
end)

print("[Ecosystem] Client initialized")
