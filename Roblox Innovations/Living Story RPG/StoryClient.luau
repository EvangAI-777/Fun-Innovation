--[[
	StoryClient.luau
	LocalScript → StarterPlayerScripts

	Living Story RPG client.
	- ProximityPrompt handling for NPC conversations
	- Dialogue GUI with typewriter text effect (nod to the original)
	- Personality trait HUD with bar visualization
	- World mood display
	- Memory log
]]

local Players = game:GetService("Players")
local UserInputService = game:GetService("UserInputService")
local TweenService = game:GetService("TweenService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local StoryConfig = require(ReplicatedStorage:WaitForChild("StoryConfig"))

local player = Players.LocalPlayer
local playerGui = player:WaitForChild("PlayerGui")

------------------------------------------------------------------------
-- RemoteEvents / RemoteFunctions
------------------------------------------------------------------------
local dialogueRequest = ReplicatedStorage:WaitForChild("DialogueRequest")
local choiceEvent = ReplicatedStorage:WaitForChild("DialogueChoiceEvent")
local worldStateEvent = ReplicatedStorage:WaitForChild("WorldStateEvent")
local personalityEvent = ReplicatedStorage:WaitForChild("PersonalityEvent")

------------------------------------------------------------------------
-- State
------------------------------------------------------------------------
local currentPersonality = {}
for _, trait in StoryConfig.Traits do
	currentPersonality[trait] = 0
end
local currentChoiceCount = 0
local currentMemories = {}
local currentMoodName = "Neutral"
local currentMoodGreeting = ""
local inDialogue = false
local hudVisible = true
local activeDialogueNpcId: string? = nil
local activeDialogueNodeId: string? = nil

------------------------------------------------------------------------
-- Dialogue GUI
------------------------------------------------------------------------
local dialogueGui = Instance.new("ScreenGui")
dialogueGui.Name = "DialogueGUI"
dialogueGui.ResetOnSpawn = false
dialogueGui.IgnoreGuiInset = true
dialogueGui.Enabled = false
dialogueGui.Parent = playerGui

-- Main dialogue frame (bottom center, like a classic RPG text box)
local dialogueFrame = Instance.new("Frame")
dialogueFrame.Name = "DialogueFrame"
dialogueFrame.Size = UDim2.new(0.7, 0, 0.35, 0)
dialogueFrame.Position = UDim2.new(0.15, 0, 0.6, 0)
dialogueFrame.BackgroundColor3 = Color3.fromRGB(20, 18, 16)
dialogueFrame.BackgroundTransparency = 0.1
dialogueFrame.BorderSizePixel = 0
dialogueFrame.Parent = dialogueGui

local frameCorner = Instance.new("UICorner")
frameCorner.CornerRadius = UDim.new(0, 10)
frameCorner.Parent = dialogueFrame

local frameBorder = Instance.new("UIStroke")
frameBorder.Color = Color3.fromRGB(100, 90, 80)
frameBorder.Thickness = 2
frameBorder.Parent = dialogueFrame

-- NPC name label (top of frame)
local npcNameLabel = Instance.new("TextLabel")
npcNameLabel.Name = "NPCName"
npcNameLabel.Size = UDim2.new(0.5, 0, 0, 28)
npcNameLabel.Position = UDim2.new(0.02, 0, 0, -30)
npcNameLabel.BackgroundColor3 = Color3.fromRGB(20, 18, 16)
npcNameLabel.BackgroundTransparency = 0.1
npcNameLabel.BorderSizePixel = 0
npcNameLabel.Text = ""
npcNameLabel.Font = Enum.Font.BuilderSansBold
npcNameLabel.TextColor3 = Color3.fromRGB(220, 210, 190)
npcNameLabel.TextSize = 16
npcNameLabel.TextXAlignment = Enum.TextXAlignment.Left
npcNameLabel.Parent = dialogueFrame

local nameCorner = Instance.new("UICorner")
nameCorner.CornerRadius = UDim.new(0, 6)
nameCorner.Parent = npcNameLabel

local namePadding = Instance.new("UIPadding")
namePadding.PaddingLeft = UDim.new(0, 8)
namePadding.Parent = npcNameLabel

-- Text area (scrollable for long dialogue)
local textArea = Instance.new("ScrollingFrame")
textArea.Name = "TextArea"
textArea.Size = UDim2.new(1, -24, 0.55, 0)
textArea.Position = UDim2.new(0, 12, 0, 8)
textArea.BackgroundTransparency = 1
textArea.ScrollBarThickness = 3
textArea.ScrollBarImageColor3 = Color3.fromRGB(100, 90, 80)
textArea.CanvasSize = UDim2.new(0, 0, 0, 0)
textArea.AutomaticCanvasSize = Enum.AutomaticSize.Y
textArea.Parent = dialogueFrame

local textLayout = Instance.new("UIListLayout")
textLayout.SortOrder = Enum.SortOrder.LayoutOrder
textLayout.Padding = UDim.new(0, 4)
textLayout.Parent = textArea

-- Choices container
local choicesFrame = Instance.new("Frame")
choicesFrame.Name = "ChoicesFrame"
choicesFrame.Size = UDim2.new(1, -24, 0.4, 0)
choicesFrame.Position = UDim2.new(0, 12, 0.58, 0)
choicesFrame.BackgroundTransparency = 1
choicesFrame.Parent = dialogueFrame

local choicesLayout = Instance.new("UIListLayout")
choicesLayout.SortOrder = Enum.SortOrder.LayoutOrder
choicesLayout.Padding = UDim.new(0, 4)
choicesLayout.Parent = choicesFrame

-- Continue prompt (shown when no choices, click to dismiss)
local continueLabel = Instance.new("TextLabel")
continueLabel.Name = "Continue"
continueLabel.Size = UDim2.new(1, 0, 0, 20)
continueLabel.Position = UDim2.new(0, 0, 1, -24)
continueLabel.BackgroundTransparency = 1
continueLabel.Text = "[Click or press Enter to continue]"
continueLabel.Font = Enum.Font.BuilderSans
continueLabel.TextColor3 = Color3.fromRGB(120, 110, 100)
continueLabel.TextSize = 13
continueLabel.Visible = false
continueLabel.Parent = dialogueFrame

------------------------------------------------------------------------
-- Personality HUD (top left)
------------------------------------------------------------------------
local hudGui = Instance.new("ScreenGui")
hudGui.Name = "PersonalityHUD"
hudGui.ResetOnSpawn = false
hudGui.IgnoreGuiInset = true
hudGui.Parent = playerGui

local hudFrame = Instance.new("Frame")
hudFrame.Name = "HUD"
hudFrame.Size = UDim2.new(0, 200, 0, 230)
hudFrame.Position = UDim2.new(0, 12, 0, 12)
hudFrame.BackgroundColor3 = Color3.fromRGB(0, 0, 0)
hudFrame.BackgroundTransparency = 0.5
hudFrame.BorderSizePixel = 0
hudFrame.Parent = hudGui

local hudCorner = Instance.new("UICorner")
hudCorner.CornerRadius = UDim.new(0, 8)
hudCorner.Parent = hudFrame

local hudTitle = Instance.new("TextLabel")
hudTitle.Size = UDim2.new(1, 0, 0, 22)
hudTitle.Position = UDim2.new(0, 0, 0, 4)
hudTitle.BackgroundTransparency = 1
hudTitle.Text = "PERSONALITY"
hudTitle.Font = Enum.Font.BuilderSansBold
hudTitle.TextColor3 = Color3.fromRGB(180, 175, 165)
hudTitle.TextSize = 13
hudTitle.Parent = hudFrame

-- Trait bars
local traitBars = {}
local traitColors = {
	curious   = Color3.fromRGB(100, 180, 220),
	cautious  = Color3.fromRGB(180, 180, 100),
	bold      = Color3.fromRGB(220, 120, 80),
	kind      = Color3.fromRGB(120, 200, 120),
	detached  = Color3.fromRGB(140, 140, 160),
	honest    = Color3.fromRGB(200, 200, 220),
	deceptive = Color3.fromRGB(160, 100, 180),
}

for i, trait in StoryConfig.Traits do
	local row = Instance.new("Frame")
	row.Size = UDim2.new(1, -16, 0, 22)
	row.Position = UDim2.new(0, 8, 0, 26 + (i - 1) * 26)
	row.BackgroundTransparency = 1
	row.Name = trait
	row.Parent = hudFrame

	local label = Instance.new("TextLabel")
	label.Size = UDim2.new(0, 65, 1, 0)
	label.BackgroundTransparency = 1
	label.Text = trait:sub(1, 1):upper() .. trait:sub(2)
	label.Font = Enum.Font.BuilderSans
	label.TextColor3 = Color3.fromRGB(160, 155, 145)
	label.TextSize = 12
	label.TextXAlignment = Enum.TextXAlignment.Left
	label.Parent = row

	local barBg = Instance.new("Frame")
	barBg.Size = UDim2.new(1, -72, 0, 8)
	barBg.Position = UDim2.new(0, 68, 0.5, -4)
	barBg.BackgroundColor3 = Color3.fromRGB(40, 38, 36)
	barBg.BorderSizePixel = 0
	barBg.Name = "BarBG"
	barBg.Parent = row

	local barBgCorner = Instance.new("UICorner")
	barBgCorner.CornerRadius = UDim.new(0, 3)
	barBgCorner.Parent = barBg

	local barFill = Instance.new("Frame")
	barFill.Size = UDim2.new(0, 0, 1, 0)
	barFill.BackgroundColor3 = traitColors[trait] or Color3.fromRGB(150, 150, 150)
	barFill.BorderSizePixel = 0
	barFill.Name = "Fill"
	barFill.Parent = barBg

	local fillCorner = Instance.new("UICorner")
	fillCorner.CornerRadius = UDim.new(0, 3)
	fillCorner.Parent = barFill

	local valLabel = Instance.new("TextLabel")
	valLabel.Size = UDim2.new(0, 20, 1, 0)
	valLabel.Position = UDim2.new(1, 4, 0, 0)
	valLabel.BackgroundTransparency = 1
	valLabel.Text = "0"
	valLabel.Font = Enum.Font.BuilderSans
	valLabel.TextColor3 = Color3.fromRGB(130, 125, 115)
	valLabel.TextSize = 11
	valLabel.TextXAlignment = Enum.TextXAlignment.Left
	valLabel.Parent = barBg

	traitBars[trait] = {fill = barFill, valLabel = valLabel}
end

-- Choice count label
local choiceCountLabel = Instance.new("TextLabel")
choiceCountLabel.Size = UDim2.new(1, -16, 0, 18)
choiceCountLabel.Position = UDim2.new(0, 8, 1, -22)
choiceCountLabel.BackgroundTransparency = 1
choiceCountLabel.Text = "Choices: 0"
choiceCountLabel.Font = Enum.Font.BuilderSans
choiceCountLabel.TextColor3 = Color3.fromRGB(120, 115, 105)
choiceCountLabel.TextSize = 11
choiceCountLabel.TextXAlignment = Enum.TextXAlignment.Left
choiceCountLabel.Parent = hudFrame

------------------------------------------------------------------------
-- World mood display (top right)
------------------------------------------------------------------------
local moodFrame = Instance.new("Frame")
moodFrame.Name = "MoodFrame"
moodFrame.Size = UDim2.new(0, 200, 0, 55)
moodFrame.Position = UDim2.new(1, -212, 0, 12)
moodFrame.BackgroundColor3 = Color3.fromRGB(0, 0, 0)
moodFrame.BackgroundTransparency = 0.5
moodFrame.BorderSizePixel = 0
moodFrame.Parent = hudGui

local moodCorner = Instance.new("UICorner")
moodCorner.CornerRadius = UDim.new(0, 8)
moodCorner.Parent = moodFrame

local moodTitle = Instance.new("TextLabel")
moodTitle.Size = UDim2.new(1, 0, 0, 20)
moodTitle.Position = UDim2.new(0, 0, 0, 4)
moodTitle.BackgroundTransparency = 1
moodTitle.Text = "TOWN MOOD"
moodTitle.Font = Enum.Font.BuilderSansBold
moodTitle.TextColor3 = Color3.fromRGB(180, 175, 165)
moodTitle.TextSize = 13
moodTitle.Parent = moodFrame

local moodLabel = Instance.new("TextLabel")
moodLabel.Name = "MoodLabel"
moodLabel.Size = UDim2.new(1, -16, 0, 24)
moodLabel.Position = UDim2.new(0, 8, 0, 24)
moodLabel.BackgroundTransparency = 1
moodLabel.Text = "Neutral"
moodLabel.Font = Enum.Font.BuilderSans
moodLabel.TextColor3 = Color3.fromRGB(160, 155, 145)
moodLabel.TextSize = 14
moodLabel.TextXAlignment = Enum.TextXAlignment.Left
moodLabel.TextWrapped = true
moodLabel.Parent = moodFrame

-- Controls hint (bottom center)
local hintLabel = Instance.new("TextLabel")
hintLabel.Size = UDim2.new(0, 300, 0, 20)
hintLabel.Position = UDim2.new(0.5, -150, 1, -28)
hintLabel.BackgroundTransparency = 1
hintLabel.Text = "[H] Toggle HUD | Walk up to NPCs to talk"
hintLabel.Font = Enum.Font.BuilderSans
hintLabel.TextColor3 = Color3.fromRGB(100, 95, 90)
hintLabel.TextSize = 12
hintLabel.Parent = hudGui

------------------------------------------------------------------------
-- Typewriter effect
------------------------------------------------------------------------
local function typewriteLine(text: string, label: TextLabel)
	label.Text = ""
	for i = 1, #text do
		local char = text:sub(i, i)
		label.Text = label.Text .. char
		local delay = StoryConfig.TypewriterDelay
		if char == "." or char == "!" or char == "?" then
			delay = StoryConfig.PunctuationPause
		elseif char == "," then
			delay = StoryConfig.TypewriterDelay * 3
		end
		task.wait(delay)
	end
end

------------------------------------------------------------------------
-- HUD update
------------------------------------------------------------------------
local function updateHUD()
	-- Trait bars
	local maxVal = 1  -- minimum scale
	for _, trait in StoryConfig.Traits do
		local val = currentPersonality[trait] or 0
		if val > maxVal then maxVal = val end
	end

	for _, trait in StoryConfig.Traits do
		local bar = traitBars[trait]
		if bar then
			local val = currentPersonality[trait] or 0
			local ratio = math.clamp(val / math.max(maxVal, 1), 0, 1)
			TweenService:Create(bar.fill, TweenInfo.new(0.5), {
				Size = UDim2.new(ratio, 0, 1, 0),
			}):Play()
			bar.valLabel.Text = tostring(val)
		end
	end

	choiceCountLabel.Text = "Choices: " .. tostring(currentChoiceCount)
	moodLabel.Text = currentMoodName .. (currentMoodGreeting ~= "" and ("\n" .. currentMoodGreeting) or "")
end

local function setHUDVisible(visible: boolean)
	hudVisible = visible
	hudFrame.Visible = visible
	moodFrame.Visible = visible
	hintLabel.Visible = visible
end

------------------------------------------------------------------------
-- Dialogue system
------------------------------------------------------------------------

local dialogueContinue = false  -- flag for continue prompt

local function clearDialogueText()
	for _, child in textArea:GetChildren() do
		if child:IsA("TextLabel") then
			child:Destroy()
		end
	end
	for _, child in choicesFrame:GetChildren() do
		if child:IsA("TextButton") then
			child:Destroy()
		end
	end
	continueLabel.Visible = false
end

local function showDialogueLines(lines: {string})
	clearDialogueText()

	for i, line in lines do
		local label = Instance.new("TextLabel")
		label.Size = UDim2.new(1, 0, 0, 0)
		label.AutomaticSize = Enum.AutomaticSize.Y
		label.BackgroundTransparency = 1
		label.Text = ""
		label.Font = Enum.Font.BuilderSans
		label.TextColor3 = Color3.fromRGB(200, 195, 185)
		label.TextSize = 15
		label.TextWrapped = true
		label.TextXAlignment = Enum.TextXAlignment.Left
		label.LayoutOrder = i
		label.Parent = textArea

		typewriteLine(line, label)

		if i < #lines then
			task.wait(StoryConfig.LinePause)
		end
	end
end

local closeDialogue  -- forward declaration; defined after showChoices

local function showChoices(choices: {table}, npcId: string, currentNodeId: string)
	for _, child in choicesFrame:GetChildren() do
		if child:IsA("TextButton") then
			child:Destroy()
		end
	end

	activeDialogueNpcId = npcId
	activeDialogueNodeId = currentNodeId

	for i, choice in choices do
		local btn = Instance.new("TextButton")
		btn.Size = UDim2.new(1, 0, 0, 28)
		btn.BackgroundColor3 = Color3.fromRGB(40, 38, 35)
		btn.BackgroundTransparency = 0.3
		btn.BorderSizePixel = 0
		btn.Text = "  [" .. i .. "] " .. choice.text
		btn.Font = Enum.Font.BuilderSans
		btn.TextColor3 = Color3.fromRGB(180, 175, 160)
		btn.TextSize = 14
		btn.TextXAlignment = Enum.TextXAlignment.Left
		btn.LayoutOrder = i
		btn.Name = "Choice_" .. i
		btn.Parent = choicesFrame

		local btnCorner = Instance.new("UICorner")
		btnCorner.CornerRadius = UDim.new(0, 5)
		btnCorner.Parent = btn

		-- Hover effect
		btn.MouseEnter:Connect(function()
			btn.BackgroundColor3 = Color3.fromRGB(60, 55, 50)
			btn.TextColor3 = Color3.fromRGB(240, 235, 220)
		end)
		btn.MouseLeave:Connect(function()
			btn.BackgroundColor3 = Color3.fromRGB(40, 38, 35)
			btn.TextColor3 = Color3.fromRGB(180, 175, 160)
		end)

		btn.MouseButton1Click:Connect(function()
			if not inDialogue then return end

			-- Send choice to server
			choiceEvent:FireServer(npcId, currentNodeId, choice.index)

			-- Find the next node from the choice
			-- We need to get the dialogue tree to find the nextNode
			local npcDef = nil
			for _, def in StoryConfig.NPCs do
				if def.id == npcId then
					npcDef = def
					break
				end
			end
			if not npcDef then return end

			local tree = StoryConfig.DialogueTrees[npcDef.dialogueKey]
			if not tree then return end

			local currentNode = tree[currentNodeId]
			if not currentNode or not currentNode.choices then return end

			local choiceDef = currentNode.choices[choice.index]
			if not choiceDef or not choiceDef.nextNode then
				-- No next node, end dialogue
				closeDialogue()
				return
			end

			-- Request the next node from the server
			local result = dialogueRequest:InvokeServer(npcId, choiceDef.nextNode)
			if result then
				showDialogueLines(result.text)
				if result.choices and #result.choices > 0 then
					task.wait(0.5)
					showChoices(result.choices, npcId, choiceDef.nextNode)
				else
					-- End of conversation or continue prompt
					continueLabel.Visible = true
					dialogueContinue = true
				end
			else
				closeDialogue()
			end
		end)
	end
end

closeDialogue = function()
	inDialogue = false
	dialogueGui.Enabled = false
	clearDialogueText()
	dialogueContinue = false
	activeDialogueNpcId = nil
	activeDialogueNodeId = nil
end

local function openDialogue(npcId: string)
	if inDialogue then return end
	inDialogue = true

	dialogueGui.Enabled = true
	clearDialogueText()

	-- Request start node from server
	local result = dialogueRequest:InvokeServer(npcId, "start")
	if not result then
		closeDialogue()
		return
	end

	npcNameLabel.Text = "  " .. result.npcName

	-- Show dialogue text with typewriter
	showDialogueLines(result.text)

	-- Show choices if any
	if result.choices and #result.choices > 0 then
		task.wait(0.5)
		showChoices(result.choices, npcId, "start")
	elseif result.isEnd then
		continueLabel.Visible = true
		dialogueContinue = true
	end
end

------------------------------------------------------------------------
-- ProximityPrompt handling
------------------------------------------------------------------------
local function setupPromptListeners()
	-- Find all NPCs and connect to their ProximityPrompts
	local function connectNPC(npcModel)
		local idVal = npcModel:FindFirstChild("NPCID")
		if not idVal then return end

		local torso = npcModel:FindFirstChild("Torso")
		if not torso then return end

		local prompt = torso:FindFirstChildOfClass("ProximityPrompt")
		if not prompt then return end

		prompt.Triggered:Connect(function(triggeringPlayer)
			if triggeringPlayer == player and not inDialogue then
				openDialogue(idVal.Value)
			end
		end)
	end

	-- Wait for NPCs folder
	local town = workspace:WaitForChild("LivingStoryTown", 30)
	if not town then return end

	local npcFolder = town:WaitForChild("NPCs", 10)
	if not npcFolder then return end

	for _, npc in npcFolder:GetChildren() do
		connectNPC(npc)
	end

	npcFolder.ChildAdded:Connect(connectNPC)
end

------------------------------------------------------------------------
-- Event handlers
------------------------------------------------------------------------

-- Personality update from server
personalityEvent.OnClientEvent:Connect(function(personality, choiceCount, memories)
	currentPersonality = personality
	currentChoiceCount = choiceCount
	currentMemories = memories or {}
	updateHUD()
end)

-- World state update
worldStateEvent.OnClientEvent:Connect(function(moodName, greeting)
	currentMoodName = moodName
	currentMoodGreeting = greeting
	updateHUD()
end)

------------------------------------------------------------------------
-- Input
------------------------------------------------------------------------
UserInputService.InputBegan:Connect(function(input, processed)
	if processed then return end

	if input.KeyCode == Enum.KeyCode.H then
		setHUDVisible(not hudVisible)
	end

	-- Number keys 1-4 to select dialogue choices
	if inDialogue and not dialogueContinue and activeDialogueNpcId and activeDialogueNodeId then
		local keyMap = {
			[Enum.KeyCode.One] = 1, [Enum.KeyCode.Two] = 2,
			[Enum.KeyCode.Three] = 3, [Enum.KeyCode.Four] = 4,
		}
		local choiceIdx = keyMap[input.KeyCode]
		if choiceIdx then
			local btn = choicesFrame:FindFirstChild("Choice_" .. choiceIdx)
			if btn and btn:IsA("TextButton") then
				-- Replicate the choice flow: fire server, advance dialogue
				choiceEvent:FireServer(activeDialogueNpcId, activeDialogueNodeId, choiceIdx)
				local npcDef = nil
				for _, def in StoryConfig.NPCs do
					if def.id == activeDialogueNpcId then npcDef = def break end
				end
				if npcDef then
					local tree = StoryConfig.DialogueTrees[npcDef.dialogueKey]
					if tree then
						local currentNode = tree[activeDialogueNodeId]
						if currentNode and currentNode.choices then
							local choiceDef = currentNode.choices[choiceIdx]
							if choiceDef and choiceDef.nextNode then
								local result = dialogueRequest:InvokeServer(activeDialogueNpcId, choiceDef.nextNode)
								if result then
									showDialogueLines(result.text)
									if result.choices and #result.choices > 0 then
										task.wait(0.5)
										showChoices(result.choices, activeDialogueNpcId, choiceDef.nextNode)
									else
										continueLabel.Visible = true
										dialogueContinue = true
									end
								else
									closeDialogue()
								end
							else
								closeDialogue()
							end
						end
					end
				end
			end
		end
	end

	-- Continue/dismiss dialogue
	if inDialogue and dialogueContinue then
		if input.KeyCode == Enum.KeyCode.Return
			or input.KeyCode == Enum.KeyCode.Space
			or input.UserInputType == Enum.UserInputType.MouseButton1 then
			closeDialogue()
		end
	end

	-- Escape to close dialogue
	if input.KeyCode == Enum.KeyCode.Escape and inDialogue then
		closeDialogue()
	end
end)

------------------------------------------------------------------------
-- Init
------------------------------------------------------------------------
setupPromptListeners()
updateHUD()

print("[StoryClient] Living Story RPG client started.")
