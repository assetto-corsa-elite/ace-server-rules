-- ACE Server Rules popup
-- Shown once per connection.
-- Poster displayed at 75%.
-- Blurred full-screen poster in background.
-- Plays WTF once with a smooth fade-in to 50% volume.
-- Click anywhere to close.

local IMAGE_URL =
  'https://raw.githubusercontent.com/assetto-corsa-elite/ace-server-rules/main/ace_rules.png?v=6'

local SOUND_URL =
  'https://raw.githubusercontent.com/assetto-corsa-elite/ace-server-rules/main/WTF?v=6'

local visible = true
local openedAt = os.clock()

local soundPlayer = nil
local soundStarted = false

local blurredBackground = ui.ExtraCanvas(vec2(640, 360))
local blurredBackgroundReady = false


-- Prepare a blurred copy of the rules poster.
ui.onImageReady(IMAGE_URL, function()
  local success, err = pcall(function()
    blurredBackground:gaussianBlurFrom(IMAGE_URL, 63)
    blurredBackgroundReady = true
  end)

  if not success then
    ac.log('ACE rules blur failed: ' .. tostring(err))
  end
end)


local function startSoundOnce()
  if soundStarted then return end
  soundStarted = true

  local success, err = pcall(function()
    soundPlayer = ui.MediaPlayer(SOUND_URL, {
      use3D = false,
      rawOutput = false
    })

    -- Start silent
    soundPlayer:setVolume(0.0)
    soundPlayer:setLooping(false)
    soundPlayer:setAutoPlay(true)
    soundPlayer:play()
  end)

  if not success then
    soundPlayer = nil
    ac.log('ACE rules sound failed: ' .. tostring(err))
  end
end


local function stopSound()
  if soundPlayer == nil then return end

  pcall(function()
    soundPlayer:pause()
    soundPlayer:setCurrentTime(0)
  end)

  soundPlayer = nil
end


local function drawCoverImage(imageSource, screen)
  local imageRatio = 16 / 9
  local screenRatio = screen.x / screen.y

  local size
  local position

  if screenRatio > imageRatio then
    size = vec2(screen.x, screen.x / imageRatio)
    position = vec2(0, (screen.y - size.y) * 0.5)
  else
    size = vec2(screen.y * imageRatio, screen.y)
    position = vec2((screen.x - size.x) * 0.5, 0)
  end

  ui.drawImage(
    imageSource,
    position,
    position + size,
    rgbm.colors.white
  )
end


local function drawBlurredBackground(screen)
  if blurredBackgroundReady then
    drawCoverImage(blurredBackground, screen)
  else
    drawCoverImage(IMAGE_URL, screen)
  end

  ui.drawRectFilled(
    vec2(0, 0),
    screen,
    rgbm(0, 0, 0, 0.48)
  )
end


local function drawMainPoster(screen)
  local targetRatio = 16 / 9

  local width = screen.x * 0.75
  local height = width / targetRatio

  if height > screen.y * 0.90 then
    height = screen.y * 0.90
    width = height * targetRatio
  end

  local topLeft = vec2(
    (screen.x - width) * 0.5,
    (screen.y - height) * 0.5
  )

  local bottomRight = topLeft + vec2(width, height)

  ui.drawRectFilled(
    topLeft - vec2(10, 10),
    bottomRight + vec2(10, 10),
    rgbm(0, 0, 0, 0.55),
    8
  )

  ui.drawImage(
    IMAGE_URL,
    topLeft,
    bottomRight,
    rgbm.colors.white
  )
end


function script.update(dt)
  if visible then
    startSoundOnce()

    if soundPlayer ~= nil then
      local elapsed = os.clock() - openedAt

      -- Fade in over 1 second.
      local volume = math.min(elapsed / 1.0, 1.0)

      -- Cap at 50%.
      volume = volume * 0.50

      soundPlayer:setVolume(volume)
    end
  end
end


function script.drawUI()
  if not visible then return end

  local screen = ui.windowSize()

  ui.transparentWindow(
    'ace_rules_popup',
    vec2(0, 0),
    screen,
    true,
    true,
    function()
      drawBlurredBackground(screen)
      drawMainPoster(screen)

      ui.setCursor(vec2(0, 0))

      if ui.invisibleButton('ace_rules_close', screen)
          and os.clock() - openedAt > 1.0 then

        visible = false
        stopSound()
      end
    end
  )
end
