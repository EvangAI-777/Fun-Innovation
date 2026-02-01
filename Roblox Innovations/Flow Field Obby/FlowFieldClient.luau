--[[
    FlowFieldClient.luau
    LocalScript -- place in StarterPlayerScripts

    Client-side effects for the Flow Field Obby:
    - Camera shake and FOV boost in turbulent zones
    - HUD showing checkpoint progress
    - Hide-UI toggle (press H)
    - Respawn notification
    - Ambient atmosphere that shifts with zone intensity
]]

local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local UserInputService = game:GetService("UserInputService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Lighting = game:GetService("Lighting")

local Config = require(ReplicatedStorage:WaitForChild("FlowFieldConfig"))
local remotes = ReplicatedStorage:WaitForChild("FlowFieldRemotes")
local checkpointReachedEvent = remotes:WaitForChild("CheckpointReached")
local respawnEvent = remotes:WaitForChild("PlayerRespawn")
local flowDataEvent = remotes:WaitForChild("FlowData")

local player = Players.LocalPlayer
local camera = workspace.CurrentCamera

------------------------------------------------------------------------
-- HUD Setup
------------------------------------------------------------------------

local screenGui = Instance.new("ScreenGui")
screenGui.Name = "FlowFieldHUD"
screenGui.ResetOnSpawn = false
screenGui.Parent = player:WaitForChild("PlayerGui")

-- Checkpoint display (top center)
local checkpointFrame = Instance.new("Frame")
checkpointFrame.Name = "CheckpointDisplay"
checkpointFrame.Size = UDim2.new(0, 280, 0, 50)
checkpointFrame.Position = UDim2.new(0.5, -140, 0, 16)
checkpointFrame.BackgroundColor3 = Color3.fromRGB(0, 0, 0)
checkpointFrame.BackgroundTransparency = 0.5
checkpointFrame.BorderSizePixel = 0
checkpointFrame.Parent = screenGui

local checkpointCorner = Instance.new("UICorner")
checkpointCorner.CornerRadius = UDim.new(0, 8)
checkpointCorner.Parent = checkpointFrame

local checkpointLabel = Instance.new("TextLabel")
checkpointLabel.Name = "Label"
checkpointLabel.Size = UDim2.new(1, 0, 1, 0)
checkpointLabel.BackgroundTransparency = 1
checkpointLabel.Text = "Checkpoint: 0 / " .. Config.CheckpointCount
checkpointLabel.TextColor3 = Color3.fromRGB(0, 200, 120)
checkpointLabel.TextSize = 22
checkpointLabel.Font = Enum.Font.GothamBold
checkpointLabel.Parent = checkpointFrame

-- Zone indicator (below checkpoint display)
local zoneFrame = Instance.new("Frame")
zoneFrame.Name = "ZoneIndicator"
zoneFrame.Size = UDim2.new(0, 160, 0, 32)
zoneFrame.Position = UDim2.new(0.5, -80, 0, 72)
zoneFrame.BackgroundColor3 = Color3.fromRGB(0, 0, 0)
zoneFrame.BackgroundTransparency = 0.6
zoneFrame.BorderSizePixel = 0
zoneFrame.Parent = screenGui

local zoneCorner = Instance.new("UICorner")
zoneCorner.CornerRadius = UDim.new(0, 6)
zoneCorner.Parent = zoneFrame

local zoneLabel = Instance.new("TextLabel")
zoneLabel.Name = "Label"
zoneLabel.Size = UDim2.new(1, 0, 1, 0)
zoneLabel.BackgroundTransparency = 1
zoneLabel.Text = "~ Calm ~"
zoneLabel.TextColor3 = Color3.fromRGB(100, 160, 255)
zoneLabel.TextSize = 16
zoneLabel.Font = Enum.Font.Gotham
zoneLabel.Parent = zoneFrame

-- Notification label (center, fades in/out)
local notifLabel = Instance.new("TextLabel")
notifLabel.Name = "Notification"
notifLabel.Size = UDim2.new(0, 400, 0, 60)
notifLabel.Position = UDim2.new(0.5, -200, 0.35, 0)
notifLabel.BackgroundTransparency = 1
notifLabel.Text = ""
notifLabel.TextColor3 = Color3.fromRGB(255, 255, 255)
notifLabel.TextSize = 28
notifLabel.Font = Enum.Font.GothamBold
notifLabel.TextTransparency = 1
notifLabel.Parent = screenGui

-- Controls hint (bottom right, shown initially then fades)
local controlsLabel = Instance.new("TextLabel")
controlsLabel.Name = "Controls"
controlsLabel.Size = UDim2.new(0, 220, 0, 30)
controlsLabel.Position = UDim2.new(1, -230, 1, -40)
controlsLabel.BackgroundTransparency = 1
controlsLabel.Text = "Press H to hide UI"
controlsLabel.TextColor3 = Color3.fromRGB(180, 180, 180)
controlsLabel.TextSize = 14
controlsLabel.Font = Enum.Font.Gotham
controlsLabel.TextTransparency = 0
controlsLabel.Parent = screenGui

-- Fade out controls hint after 8 seconds
task.delay(8, function()
    for i = 0, 1, 0.02 do
        controlsLabel.TextTransparency = i
        task.wait(0.03)
    end
    controlsLabel.TextTransparency = 1
end)

------------------------------------------------------------------------
-- Notification system
------------------------------------------------------------------------

local function showNotification(text: string, color: Color3?)
    notifLabel.Text = text
    notifLabel.TextColor3 = color or Color3.fromRGB(255, 255, 255)

    -- Fade in
    for i = 1, 0, -0.05 do
        notifLabel.TextTransparency = i
        task.wait(0.02)
    end
    notifLabel.TextTransparency = 0

    task.wait(2)

    -- Fade out
    for i = 0, 1, 0.04 do
        notifLabel.TextTransparency = i
        task.wait(0.02)
    end
    notifLabel.TextTransparency = 1
end

------------------------------------------------------------------------
-- Remote event handlers
------------------------------------------------------------------------

checkpointReachedEvent.OnClientEvent:Connect(function(index: number, total: number)
    checkpointLabel.Text = "Checkpoint: " .. index .. " / " .. total

    if index == total then
        task.spawn(showNotification, "All checkpoints reached!", Color3.fromRGB(0, 255, 120))
    else
        task.spawn(showNotification, "Checkpoint " .. index .. " reached", Config.CheckpointColor)
    end
end)

respawnEvent.OnClientEvent:Connect(function(checkpointIndex: number)
    local text = checkpointIndex > 0
        and "Respawning at checkpoint " .. checkpointIndex
        or "Respawning at start"
    task.spawn(showNotification, text, Color3.fromRGB(255, 200, 80))
end)

------------------------------------------------------------------------
-- Camera effects based on local flow turbulence
------------------------------------------------------------------------

local currentFlowMagnitude = 0
local targetFlowMagnitude = 0
local defaultFOV = 70

flowDataEvent.OnClientEvent:Connect(function(magnitude: number)
    targetFlowMagnitude = magnitude
end)

-- Smooth camera shake state
local shakeOffset = Vector3.zero

RunService.RenderStepped:Connect(function(dt: number)
    -- Smooth interpolation of flow magnitude
    currentFlowMagnitude += (targetFlowMagnitude - currentFlowMagnitude) * dt * 3

    -- Determine zone and update indicator
    if currentFlowMagnitude < Config.CalmThreshold then
        zoneLabel.Text = "~ Calm ~"
        zoneLabel.TextColor3 = Color3.fromRGB(100, 160, 255)
    elseif currentFlowMagnitude < Config.TurbulentThreshold then
        zoneLabel.Text = "~ Moderate ~"
        zoneLabel.TextColor3 = Color3.fromRGB(255, 200, 80)
    else
        zoneLabel.Text = "~ Turbulent ~"
        zoneLabel.TextColor3 = Color3.fromRGB(255, 80, 60)
    end

    -- Camera shake in turbulent zones
    local turbulenceAlpha = math.clamp(
        (currentFlowMagnitude - Config.CalmThreshold)
        / (Config.TurbulentThreshold - Config.CalmThreshold),
        0, 1
    )

    if turbulenceAlpha > 0 then
        local intensity = turbulenceAlpha * Config.TurbulentShakeIntensity
        local t = tick() * 8
        shakeOffset = Vector3.new(
            math.noise(t, 0, 0) * intensity,
            math.noise(0, t, 0) * intensity,
            math.noise(0, 0, t) * intensity * 0.5
        )

        camera.CFrame = camera.CFrame + shakeOffset

        -- FOV boost
        camera.FieldOfView = defaultFOV + turbulenceAlpha * Config.TurbulentFOVBoost
    else
        camera.FieldOfView = defaultFOV + (camera.FieldOfView - defaultFOV) * 0.9
    end
end)

------------------------------------------------------------------------
-- Atmosphere (shifts color with distance from origin)
------------------------------------------------------------------------

local atmosphere = Instance.new("Atmosphere")
atmosphere.Density = 0.3
atmosphere.Offset = 0.25
atmosphere.Glare = 0
atmosphere.Haze = 2
atmosphere.Parent = Lighting

local sky = Instance.new("Sky")
sky.SunAngularSize = 15
sky.MoonAngularSize = 10
sky.StarCount = 3000
sky.Parent = Lighting

Lighting.ClockTime = 4.5  -- Early dawn, dark sky with stars visible
Lighting.Ambient = Color3.fromRGB(20, 25, 40)
Lighting.OutdoorAmbient = Color3.fromRGB(30, 35, 50)
Lighting.FogColor = Color3.fromRGB(10, 15, 30)
Lighting.FogEnd = 900

------------------------------------------------------------------------
-- Hide UI toggle
------------------------------------------------------------------------

local hudVisible = true

UserInputService.InputBegan:Connect(function(input, processed)
    if processed then return end
    if input.KeyCode == Config.HideUIKey then
        hudVisible = not hudVisible
        checkpointFrame.Visible = hudVisible
        zoneFrame.Visible = hudVisible
    end
end)

------------------------------------------------------------------------

print("[FlowFieldObby] Client initialized")
