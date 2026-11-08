-- ACE welcome video, shown once per connection.
-- The original poster fills the same frame while the video loads.
-- Click anywhere to skip. Playback ending also closes the popup.

local IMAGE_URL =
  'https://raw.githubusercontent.com/assetto-corsa-elite/ace-server-rules/main/ace_rules.png?v=8'

local VIDEO_URL =
  'https://ace-welcome-media.malas-alvaro.chatgpt.site/ace-welcome.mp4'

local visible = true
local videoPlayer = nil
local videoRequested = false

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


local function startVideoOnce()
  if videoRequested then return end
  videoRequested = true

  local success, err = pcall(function()
    local player = ui.MediaPlayer(nil, {
      use3D = false,
      rawOutput = false
    })

    player:setVolume(0.50)
    player:setLooping(false)
    player:setAutoPlay(true)
    player:setSource(VIDEO_URL)
    videoPlayer = player
  end)

  if not success then
    ac.log('ACE welcome video failed: ' .. tostring(err))
  end
end


local function closePopup()
  visible = false

  if videoPlayer then
    videoPlayer:setAutoPlay(false)
    videoPlayer:pause()
    videoPlayer:setSource(nil)
    videoPlayer = nil
  end
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


local function drawMainMedia(screen, source)
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
    source,
    topLeft,
    bottomRight,
    rgbm.colors.white
  )
end


function script.update(dt)
  if not visible then return end

  startVideoOnce()
  if videoPlayer and videoPlayer:ended() then
    closePopup()
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
      local source = IMAGE_URL
      if videoPlayer and videoPlayer:hasVideo() then
        source = videoPlayer
      end
      drawMainMedia(screen, source)

      ui.setCursor(vec2(0, 0))

      if ui.invisibleButton('ace_rules_close', screen) then
        closePopup()
      end
    end
  )
end
