-- CSP online script: the welcome overlay runs once per connection.
local VIDEO_URL = 'https://raw.githubusercontent.com/assetto-corsa-elite/ace-server-rules/main/ace-welcome-v1.mp4'
local POSTER_URL = 'https://raw.githubusercontent.com/assetto-corsa-elite/ace-server-rules/main/ace_rules.png?v=8'
local STALL_TIMEOUT = 20
local ASPECT_RATIO = 16 / 9

local closed = false
local player
local lastPosition = 0
local stalledFor = 0

ac.log('ACE welcome video: script loaded')

local function close()
  closed = true
  if player then
    player:setAutoPlay(false)
    player:pause()
    player:setSource(nil)
    player = nil
  end
end

function script.drawUI()
  if closed then return end

  local state = ac.getUI()
  local screen = state.windowSize
  if screen.x <= 0 or screen.y <= 0 then return end

  if not player then
    local ok, err = pcall(function()
      player = ui.MediaPlayer(nil, { use3D = false, rawOutput = false })
      player:setVolume(0.5)
      player:setLooping(false)
      player:setAutoPlay(true)
      player:setSource(VIDEO_URL)
      ac.log('ACE welcome video: playback requested')
    end)
    if not ok then
      ac.log('ACE welcome video failed to initialize: ' .. tostring(err))
      close()
      return
    end
  else
    if state.isMouseLeftKeyClicked or state.isMouseRightKeyClicked or state.isMouseMiddleKeyClicked then
      close()
      return
    end

    local position = player:currentTime()
    if position > lastPosition then
      if lastPosition == 0 then
        ac.log('ACE welcome video: playback started')
      end
      lastPosition = position
      stalledFor = 0
    else
      stalledFor = stalledFor + state.dt
    end

    if lastPosition > 0 and player:ended() then
      close()
      return
    end
    if stalledFor >= STALL_TIMEOUT then
      ac.log('ACE welcome video timed out')
      close()
      return
    end
  end

  -- Scale both limits of the original frame by 80%, keeping the 16:9 ratio.
  local width = math.min(screen.x * 0.75, screen.y * 0.90 * ASPECT_RATIO) * 0.80
  local size = vec2(width, width / ASPECT_RATIO)
  local topLeft = (screen - size) * 0.5
  local bottomRight = topLeft + size

  ui.transparentWindow('ace_welcome_video', vec2(0, 0), screen, true, true, function()
    ui.drawRectFilled(vec2(0, 0), screen, rgbm(0, 0, 0, 0.65))
    ui.drawRectFilled(topLeft, bottomRight, rgbm(0, 0, 0, 1))
    ui.drawImage(player:hasVideo() and player or POSTER_URL, topLeft, bottomRight, rgbm.colors.white)
    ui.dwriteDrawTextClipped('Click anywhere to skip', 16,
      vec2(topLeft.x, bottomRight.y + 4), vec2(bottomRight.x, bottomRight.y + 32),
      ui.Alignment.Center, ui.Alignment.Center, false, rgbm.colors.white)
    ui.setCursor(vec2(0, 0))
    ui.invisibleButton('ace_welcome_skip', screen)
  end)
end
