--[[
    SkywritingClient.luau
    LocalScript -- place in StarterPlayerScripts

    Client-side UI for Verse Engine Skywriting:
    - Voice and form selection panel
    - Poem notification feed (who wrote what, in which voice)
    - Screenshot mode (hides all UI)
    - Night sky atmosphere
]]

local Players = game:GetService("Players")
local UserInputService = game:GetService("UserInputService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Lighting = game:GetService("Lighting")
local StarterGui = game:GetService("StarterGui")

local Config = require(ReplicatedStorage:WaitForChild("VerseConfig"))
local remotes = ReplicatedStorage:WaitForChild("VerseRemotes")
local requestPoemEvent = remotes:WaitForChild("RequestPoem")
local poemCreatedEvent = remotes:WaitForChild("PoemCreated")

local player = Players.LocalPlayer

------------------------------------------------------------------------
-- Atmosphere -- deep night sky so poems glow against it
------------------------------------------------------------------------

Lighting.ClockTime = 2          -- Deep night
Lighting.Ambient = Color3.fromRGB(10, 12, 20)
Lighting.OutdoorAmbient = Color3.fromRGB(15, 18, 30)
Lighting.FogColor = Color3.fromRGB(5, 8, 15)
Lighting.FogEnd = 1200

local atmosphere = Instance.new("Atmosphere")
atmosphere.Density = 0.25
atmosphere.Offset = 0.1
atmosphere.Glare = 0
atmosphere.Haze = 1.5
atmosphere.Parent = Lighting

local sky = Instance.new("Sky")
sky.SunAngularSize = 8
sky.MoonAngularSize = 12
sky.StarCount = 5000
sky.Parent = Lighting

------------------------------------------------------------------------
-- GUI Setup
------------------------------------------------------------------------

local screenGui = Instance.new("ScreenGui")
screenGui.Name = "SkywritingHUD"
screenGui.ResetOnSpawn = false
screenGui.Parent = player:WaitForChild("PlayerGui")

-- Main panel (bottom left)
local panel = Instance.new("Frame")
panel.Name = "GeneratorPanel"
panel.Size = UDim2.new(0, 260, 0, 380)
panel.Position = UDim2.new(0, 16, 1, -396)
panel.BackgroundColor3 = Color3.fromRGB(15, 18, 28)
panel.BackgroundTransparency = 0.2
panel.BorderSizePixel = 0
panel.Parent = screenGui

local panelCorner = Instance.new("UICorner")
panelCorner.CornerRadius = UDim.new(0, 10)
panelCorner.Parent = panel

local panelStroke = Instance.new("UIStroke")
panelStroke.Color = Color3.fromRGB(60, 70, 100)
panelStroke.Thickness = 1
panelStroke.Parent = panel

-- Title
local title = Instance.new("TextLabel")
title.Size = UDim2.new(1, 0, 0, 36)
title.Position = UDim2.new(0, 0, 0, 8)
title.BackgroundTransparency = 1
title.Text = "VERSE ENGINE"
title.TextColor3 = Color3.fromRGB(200, 210, 240)
title.TextSize = 18
title.Font = Enum.Font.GothamBold
title.Parent = panel

-- Voice selection header
local voiceHeader = Instance.new("TextLabel")
voiceHeader.Size = UDim2.new(1, -20, 0, 20)
voiceHeader.Position = UDim2.new(0, 10, 0, 44)
voiceHeader.BackgroundTransparency = 1
voiceHeader.Text = "Voice"
voiceHeader.TextColor3 = Color3.fromRGB(140, 150, 180)
voiceHeader.TextSize = 13
voiceHeader.Font = Enum.Font.Gotham
voiceHeader.TextXAlignment = Enum.TextXAlignment.Left
voiceHeader.Parent = panel

-- State
local selectedVoice = "melancholic"
local selectedForm = "poem"
local cooldownActive = false

-- Voice buttons
local voiceButtons: { [string]: TextButton } = {}
local voiceYStart = 66

for i, voiceName in Config.Voices do
    local color = Config.VoiceColors[voiceName]
    local desc = Config.VoiceDescriptions[voiceName]

    local btn = Instance.new("TextButton")
    btn.Name = "Voice_" .. voiceName
    btn.Size = UDim2.new(1, -20, 0, 30)
    btn.Position = UDim2.new(0, 10, 0, voiceYStart + (i - 1) * 34)
    btn.BackgroundColor3 = Color3.fromRGB(30, 35, 50)
    btn.BorderSizePixel = 0
    btn.Text = "  " .. voiceName .. "  --  " .. desc
    btn.TextColor3 = color
    btn.TextSize = 12
    btn.Font = Enum.Font.Gotham
    btn.TextXAlignment = Enum.TextXAlignment.Left
    btn.AutoButtonColor = true
    btn.Parent = panel

    local btnCorner = Instance.new("UICorner")
    btnCorner.CornerRadius = UDim.new(0, 6)
    btnCorner.Parent = btn

    voiceButtons[voiceName] = btn

    btn.MouseButton1Click:Connect(function()
        selectedVoice = voiceName
        -- Update selection visuals
        for vn, vb in voiceButtons do
            if vn == voiceName then
                vb.BackgroundColor3 = Color3.fromRGB(50, 55, 80)
            else
                vb.BackgroundColor3 = Color3.fromRGB(30, 35, 50)
            end
        end
    end)
end

-- Set initial selection visual
voiceButtons[selectedVoice].BackgroundColor3 = Color3.fromRGB(50, 55, 80)

-- Form selection header
local formYStart = voiceYStart + #Config.Voices * 34 + 10

local formHeader = Instance.new("TextLabel")
formHeader.Size = UDim2.new(1, -20, 0, 20)
formHeader.Position = UDim2.new(0, 10, 0, formYStart)
formHeader.BackgroundTransparency = 1
formHeader.Text = "Form"
formHeader.TextColor3 = Color3.fromRGB(140, 150, 180)
formHeader.TextSize = 13
formHeader.Font = Enum.Font.Gotham
formHeader.TextXAlignment = Enum.TextXAlignment.Left
formHeader.Parent = panel

-- Form buttons (horizontal row)
local formButtons: { [string]: TextButton } = {}
local formBtnWidth = 55

for i, formName in Config.Forms do
    local btn = Instance.new("TextButton")
    btn.Name = "Form_" .. formName
    btn.Size = UDim2.new(0, formBtnWidth, 0, 26)
    btn.Position = UDim2.new(0, 10 + (i - 1) * (formBtnWidth + 4), 0, formYStart + 22)
    btn.BackgroundColor3 = Color3.fromRGB(30, 35, 50)
    btn.BorderSizePixel = 0
    btn.Text = formName
    btn.TextColor3 = Color3.fromRGB(180, 185, 200)
    btn.TextSize = 12
    btn.Font = Enum.Font.Gotham
    btn.AutoButtonColor = true
    btn.Parent = panel

    local btnCorner = Instance.new("UICorner")
    btnCorner.CornerRadius = UDim.new(0, 6)
    btnCorner.Parent = btn

    formButtons[formName] = btn

    btn.MouseButton1Click:Connect(function()
        selectedForm = formName
        for fn, fb in formButtons do
            if fn == formName then
                fb.BackgroundColor3 = Color3.fromRGB(50, 55, 80)
            else
                fb.BackgroundColor3 = Color3.fromRGB(30, 35, 50)
            end
        end
    end)
end

formButtons[selectedForm].BackgroundColor3 = Color3.fromRGB(50, 55, 80)

-- Generate button
local generateBtn = Instance.new("TextButton")
generateBtn.Name = "GenerateButton"
generateBtn.Size = UDim2.new(1, -20, 0, 36)
generateBtn.Position = UDim2.new(0, 10, 0, formYStart + 56)
generateBtn.BackgroundColor3 = Color3.fromRGB(60, 80, 140)
generateBtn.BorderSizePixel = 0
generateBtn.Text = "Write to the Sky"
generateBtn.TextColor3 = Color3.fromRGB(220, 225, 240)
generateBtn.TextSize = 15
generateBtn.Font = Enum.Font.GothamBold
generateBtn.AutoButtonColor = true
generateBtn.Parent = panel

local genCorner = Instance.new("UICorner")
genCorner.CornerRadius = UDim.new(0, 8)
genCorner.Parent = generateBtn

generateBtn.MouseButton1Click:Connect(function()
    if cooldownActive then return end

    cooldownActive = true
    generateBtn.Text = "..."
    generateBtn.BackgroundColor3 = Color3.fromRGB(40, 50, 80)

    requestPoemEvent:FireServer(selectedVoice, selectedForm)

    -- Visual cooldown
    task.delay(Config.GenerationCooldown, function()
        cooldownActive = false
        generateBtn.Text = "Write to the Sky"
        generateBtn.BackgroundColor3 = Color3.fromRGB(60, 80, 140)
    end)
end)

------------------------------------------------------------------------
-- Notification feed (top right, shows recent poems from all players)
------------------------------------------------------------------------

local feedFrame = Instance.new("Frame")
feedFrame.Name = "PoemFeed"
feedFrame.Size = UDim2.new(0, 320, 0, 200)
feedFrame.Position = UDim2.new(1, -336, 0, 16)
feedFrame.BackgroundTransparency = 1
feedFrame.ClipsDescendants = true
feedFrame.Parent = screenGui

local feedLayout = Instance.new("UIListLayout")
feedLayout.SortOrder = Enum.SortOrder.LayoutOrder
feedLayout.Padding = UDim.new(0, 4)
feedLayout.VerticalAlignment = Enum.VerticalAlignment.Bottom
feedLayout.Parent = feedFrame

local feedEntryCount = 0

local function addFeedEntry(playerName: string, voice: string, lines: {string})
    feedEntryCount += 1
    local color = Config.VoiceColors[voice] or Color3.fromRGB(180, 180, 180)

    -- Preview: first line, truncated
    local preview = lines[1] or ""
    if #preview > 40 then
        preview = string.sub(preview, 1, 37) .. "..."
    end

    local entry = Instance.new("TextLabel")
    entry.Name = "Feed_" .. feedEntryCount
    entry.Size = UDim2.new(1, 0, 0, 28)
    entry.LayoutOrder = feedEntryCount
    entry.BackgroundColor3 = Color3.fromRGB(15, 18, 28)
    entry.BackgroundTransparency = 0.4
    entry.BorderSizePixel = 0
    entry.Text = "  " .. playerName .. " [" .. voice .. "]: " .. preview
    entry.TextColor3 = color
    entry.TextSize = 12
    entry.Font = Enum.Font.Gotham
    entry.TextXAlignment = Enum.TextXAlignment.Left
    entry.TextTruncate = Enum.TextTruncate.AtEnd
    entry.Parent = feedFrame

    local entryCorner = Instance.new("UICorner")
    entryCorner.CornerRadius = UDim.new(0, 4)
    entryCorner.Parent = entry

    -- Fade out after 15 seconds
    task.delay(15, function()
        for i = 0, 1, 0.04 do
            if not entry.Parent then return end
            entry.TextTransparency = i
            entry.BackgroundTransparency = 0.4 + i * 0.6
            task.wait(0.03)
        end
        entry:Destroy()
    end)

    -- Remove oldest if too many
    local children = feedFrame:GetChildren()
    local labelCount = 0
    for _, child in children do
        if child:IsA("TextLabel") then labelCount += 1 end
    end
    if labelCount > 6 then
        for _, child in children do
            if child:IsA("TextLabel") then
                child:Destroy()
                break
            end
        end
    end
end

poemCreatedEvent.OnClientEvent:Connect(function(authorName: string, voice: string, lines: {string})
    addFeedEntry(authorName, voice, lines)
end)

------------------------------------------------------------------------
-- Controls hint
------------------------------------------------------------------------

local controlsLabel = Instance.new("TextLabel")
controlsLabel.Name = "Controls"
controlsLabel.Size = UDim2.new(0, 260, 0, 24)
controlsLabel.Position = UDim2.new(0, 16, 1, -410)
controlsLabel.BackgroundTransparency = 1
controlsLabel.Text = "F2 = screenshot mode (hide UI)"
controlsLabel.TextColor3 = Color3.fromRGB(120, 125, 140)
controlsLabel.TextSize = 12
controlsLabel.Font = Enum.Font.Gotham
controlsLabel.TextXAlignment = Enum.TextXAlignment.Left
controlsLabel.Parent = screenGui

-- Fade controls hint after 10 seconds
task.delay(10, function()
    for i = 0, 1, 0.03 do
        controlsLabel.TextTransparency = i
        task.wait(0.03)
    end
end)

------------------------------------------------------------------------
-- Screenshot mode (F2 hides all UI)
------------------------------------------------------------------------

local screenshotMode = false

UserInputService.InputBegan:Connect(function(input, processed)
    if processed then return end
    if input.KeyCode == Enum.KeyCode.F2 then
        screenshotMode = not screenshotMode
        panel.Visible = not screenshotMode
        feedFrame.Visible = not screenshotMode

        -- Also hide core GUI elements for clean screenshots
        pcall(function()
            StarterGui:SetCoreGuiEnabled(Enum.CoreGuiType.All, not screenshotMode)
        end)
    end
end)

------------------------------------------------------------------------

print("[VerseEngineSkywriting] Client initialized")
