-- ACE Server Rules popup
-- Shown once per connection. Click anywhere to close.

local IMAGE_URL = 'https://raw.githubusercontent.com/assetto-corsa-elite/ace-server-rules/main/ace_rules.png'
local visible = true
local openedAt = os.clock()

local function coverScreenWithImage()
  local screen = ui.windowSize()

  -- Dark background behind the 16:9 image.
  ui.drawRectFilled(vec2(0, 0), screen, rgbm(0, 0, 0, 0.92))

  -- Keep the complete 16:9 poster visible on every resolution.
  local targetRatio = 16 / 9
  local width = screen.x
  local height = width / targetRatio

  if height > screen.y then
    height = screen.y
    width = height * targetRatio
  end

  local topLeft = vec2(
    (screen.x - width) * 0.5,
    (screen.y - height) * 0.5
  )

  local bottomRight = topLeft + vec2(width, height)

  ui.drawImage(IMAGE_URL, topLeft, bottomRight, rgbm.colors.white)
end

function script.update(dt)
  -- Intentionally empty.
  -- The popup state lasts only for the current server connection.
end

function script.drawUI()
  if not visible then return end

  coverScreenWithImage()

  -- Small delay prevents the loading click from instantly closing the rules.
  if os.clock() - openedAt > 1.0 and ui.mouseClicked(ui.MouseButton.Left) then
    visible = false
  end
end
