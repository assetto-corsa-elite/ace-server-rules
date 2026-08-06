-- ACE Server Rules popup
-- Shown once per connection.
-- Plays Alonso.ogg once.
-- Click anywhere to close.

local IMAGE_URL =
  'https://raw.githubusercontent.com/assetto-corsa-elite/ace-server-rules/main/ace_rules.png?v=3'

local SOUND_URL =
  'https://raw.githubusercontent.com/assetto-corsa-elite/ace-server-rules/main/Alonso.ogg?v=3'

local visible = true
local openedAt = os.clock()

local rulesSound = nil
local soundAttempted = false

local function playRulesSoundOnce()
  if soundAttempted then return end
  soundAttempted = true

  -- Protected call: if the CSP build rejects remote audio,
  -- the rules image will continue working.
  local success, result = pcall(function()
    local audio = ac.AudioEvent.fromFile({
      filename = SOUND_URL,
      use3D = false
    })

    if audio ~= nil then
      audio.volume = 1.0
      audio:start()
    end

    return audio
  end)

  if success then
    rulesSound = result
  else
    ac.log('ACE rules sound failed to start: ' .. tostring(result))
  end
end

local function stopRulesSound()
  if rulesSound == nil then return end

  pcall(function()
    rulesSound:stop()
    rulesSound:dispose()
  end)

  rulesSound = nil
end

local function coverScreenWithImage()
  local screen = ui.windowSize()

  -- Dark background behind the image.
  ui.drawRectFilled(
    vec2(0, 0),
    screen,
    rgbm(0, 0, 0, 0.92)
  )

  -- Poster displayed at 60% of screen width.
  local targetRatio = 16 / 9
  local width = screen.x * 0.60
  local height = width / targetRatio

  -- Safety limit for unusually narrow or low-resolution screens.
  if height > screen.y * 0.90 then
    height = screen.y * 0.90
    width = height * targetRatio
  end

  local topLeft = vec2(
    (screen.x - width) * 0.5,
    (screen.y - height) * 0.5
  )

  local bottomRight = topLeft + vec2(width, height)

  ui.drawImage(
    IMAGE_URL,
    topLeft,
    bottomRight,
    rgbm.colors.white
  )
end

function script.update(dt)
  if visible then
    playRulesSoundOnce()
  end
end

function script.drawUI()
  if not visible then return end

  coverScreenWithImage()

  -- Prevent the loading click from immediately closing the popup.
  if os.clock() - openedAt > 1.0
      and ui.mouseClicked(ui.MouseButton.Left) then

    visible = false
    stopRulesSound()
  end
end
