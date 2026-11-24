local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Lighting = game:GetService("Lighting")
local Workspace = game:GetService("Workspace")

local Config = require(ReplicatedStorage:WaitForChild("GameConfig"))

local world = Instance.new("Model")
world.Name = Config.WorldName
world.Parent = Workspace

local function createPart(name, size, position, material, color)
    local part = Instance.new("Part")
    part.Name = name
    part.Size = size
    part.Position = position
    part.Anchored = true
    part.Material = material
    part.Color = color
    part.Parent = world
    return part
end

createPart(
    "GreenBase",
    Vector3.new(Config.BaseplateSize, 2, Config.BaseplateSize),
    Vector3.new(0, -1, 0),
    Enum.Material.Grass,
    Color3.fromRGB(74, 132, 72)
)

local spawn = Instance.new("SpawnLocation")
spawn.Name = "APOLOSpawn"
spawn.Size = Vector3.new(14, 1, 14)
spawn.Position = Vector3.new(0, 1, 0)
spawn.Anchored = true
spawn.Neutral = true
spawn.Material = Enum.Material.Neon
spawn.Color = Color3.fromRGB(65, 190, 255)
spawn.Parent = world

for index = 1, 8 do
    local angle = math.rad(index * 45)
    local radius = 42
    local position = Vector3.new(math.cos(angle) * radius, 4, math.sin(angle) * radius)
    createPart(
        "DiscoveryPlatform" .. index,
        Vector3.new(18, 2, 18),
        position,
        Enum.Material.SmoothPlastic,
        Color3.fromRGB(80 + index * 12, 110, 210)
    )
end

Lighting.ClockTime = 14
Lighting.Brightness = 2
Lighting.GlobalShadows = true
Lighting.Ambient = Color3.fromRGB(115, 125, 145)
Lighting.OutdoorAmbient = Color3.fromRGB(145, 155, 175)

Players.PlayerAdded:Connect(function(player)
    player.CharacterAdded:Connect(function(character)
        local humanoid = character:WaitForChild("Humanoid", 10)
        if humanoid then
            humanoid.WalkSpeed = 16
        end
    end)
end)
