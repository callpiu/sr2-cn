-- prison.lua: Prison Island District Script, modified for SuperUI [nclok1405]
-- SR2 district script
-- 3/28/07

function prison_init()
end

function prison_main()
end

-- debug function - call from the console with 'lua' command
function warp_prison()
	message("warping...")
	delay(0)
	teleport("#PLAYER#", "prison_$nav-warp")
end

-- These two functions are here to prevent SuperUI's error handler from being tripped off. [nclok1405]
function dlc04_main()
end
function dlc05_main()
end
