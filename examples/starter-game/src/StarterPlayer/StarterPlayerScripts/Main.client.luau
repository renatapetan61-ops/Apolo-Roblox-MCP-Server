local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local player = Players.LocalPlayer
local Config = require(ReplicatedStorage:WaitForChild("GameConfig"))

local gui = Instance.new("ScreenGui")
gui.Name = "APOLOStarterHUD"
gui.ResetOnSpawn = false
gui.Parent = player:WaitForChild("PlayerGui")

local panel = Instance.new("Frame")
panel.Name = "Header"
panel.AnchorPoint = Vector2.new(0.5, 0)
panel.Position = UDim2.fromScale(0.5, 0.035)
panel.Size = UDim2.fromOffset(420, 82)
panel.BackgroundColor3 = Color3.fromRGB(18, 26, 42)
panel.BackgroundTransparency = 0.08
panel.BorderSizePixel = 0
panel.Parent = gui

local corner = Instance.new("UICorner")
corner.CornerRadius = UDim.new(0, 16)
corner.Parent = panel

local title = Instance.new("TextLabel")
title.Name = "Title"
title.BackgroundTransparency = 1
title.Position = UDim2.fromOffset(18, 8)
title.Size = UDim2.new(1, -36, 0, 34)
title.Font = Enum.Font.GothamBold
title.Text = Config.Title
title.TextColor3 = Color3.fromRGB(245, 249, 255)
title.TextSize = 22
title.TextXAlignment = Enum.TextXAlignment.Left
title.Parent = panel

local subtitle = Instance.new("TextLabel")
subtitle.Name = "Subtitle"
subtitle.BackgroundTransparency = 1
subtitle.Position = UDim2.fromOffset(18, 43)
subtitle.Size = UDim2.new(1, -36, 0, 24)
subtitle.Font = Enum.Font.Gotham
subtitle.Text = Config.Subtitle
subtitle.TextColor3 = Color3.fromRGB(155, 205, 255)
subtitle.TextSize = 14
subtitle.TextXAlignment = Enum.TextXAlignment.Left
subtitle.Parent = panel
