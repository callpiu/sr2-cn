-- city_load.lua: Loading Screen
-- Options [nclok1405] (true: Yes, false: No)

-- Show Saints Row 2 Logo?
CITY_LOAD_SHOW_LOGO = true

-- Show Random Loading Screen Tips?
CITY_LOAD_ENABLE_RANDOM_LOADING_TIPS = true

-- Randomize the loading screen image after completing Corporate Meltdown (dlc05)
CITY_LOAD_ENABLE_RANDOM_IMAGE_AFTER_DLC05 = true

-- Loading screen tips (NEEDS TO BE UPPER CASE) [nclok1405]
LOADING_SCREEN_TIPS = {
	"Use cover to avoid taking damage",
	"Press R to pick up items from the ground",
	"Complete missions to raise your gang respect",
	"Mark targets on the map to get directions",
	"Press Shift while driving to boost",
	"Buy properties for extra income",
	"Upgrade your weapons to increase damage",
	"Call your homies for backup in a fight",
	"Remember to save your progress",
	"Knock down enemies to steal their weapons",
	"Drive vehicles to a garage to customize them",
	"Press Tab to open the map",
	"Watch your notoriety level around police",
	"Use grenades against grouped enemies",
	"Different outfits give different bonuses",
	"Buy weapons and supplies at the store",
	"Expand gang territory by completing missions",
	"Use the environment to win fights more easily",
	"Keep your balance while riding motorcycles",
	"Hide in buildings when wanted by police",
	"Finish activities for extra rewards",
	"Play with friends to complete more challenges",
	"Pay attention to on-screen prompts",
	"Save often so you never lose progress",
	"Upgrade your abilities to make fights easier",
	"Store your favorite vehicles in the garage",
	"Try different weapons to find your favorite",
	"Claim your reward after finishing a mission",
	"Dodge when enemies wind up their attacks",
	"You can change the difficulty at any time",
	"Take the high ground for a better view",
	"Money buys gear, weapons and property",
	"Money buys gear, weapons and property",
	"Park in a safe spot before getting out",
	"Watch the time limits on timed missions",
	"Each gang fights with a different style",
	"Explore the city to find hidden content",
	"Finishing missions unlocks new weapons",
	"Keep moving so enemies cannot surround you",
	"Use binoculars to mark distant targets",
	"Find health packs to heal after a fight",
	"Use vehicles to travel across the city fast",
	"Weather affects how your car handles",
	"Store important vehicles in your garage",
	"Finish mission chains to unlock the story",
	"Open the options menu any time to adjust settings",
}

-- Last completed mission names (used for randomly selecting images) [nclok1405]
LAST_MISSION_NAMES = {
	-- Missions
	"none",
	"tss01","tss02","tss03","tss04",
	"bh01","bh02","bh03","bh04","bh05","bh06","bh07","bh08","bh09","bh10","bh11",
	"rn01","rn02","rn03","rn04","rn05","rn06","rn07","rn08","rn09","rn10","rn11",
	"ss01","ss02","ss03","ss04","ss05","ss06","ss07","ss08","ss09","ss10","ss11",
	"ep01","ep02","ep03","ep04",
	"em01",

	-- End Screens
	"ui_c_wall_saints","ui_c_wall_bhood","ui_c_wall_ronin","ui_c_wall_samedi","ui_c_wall_ultor",
	"ui_c_wall_demoderby","ui_c_wall_escort","ui_c_wall_fightclub","ui_c_wall_insfraud",
	"ui_c_wall_fuzz","ui_c_wall_humantorch","ui_c_wall_snatch","ui_c_wall_drug",
	"ui_c_wall_crowdcontrol","ui_c_wall_septic","ui_c_wall_zombie","ui_c_wall_heli","ui_c_wall_mayhem",
	"ui_c_wall_mp","ui_c_wall_mp_red","ui_c_wall_blank",
}

-- Non-postgame mission names [nclok1405]
BEFORE_POST_GAME_MISSION_NAMES = {
	"none",
	"tss01","tss02","tss03","tss04",
	"bh01","bh02","bh03","bh04","bh05","bh06","bh07","bh08","bh09","bh10","bh11",
	"rn01","rn02","rn03","rn04","rn05","rn06","rn07","rn08","rn09","rn10","rn11",
	"ss01","ss02","ss03","ss04","ss05","ss06","ss07","ss08","ss09","ss10","ss11",
	"ep01","ep02","ep03","ep04",
	"em01",
	"dlc04"
}

City_load_images = {

--[[
	["none"] = {
		pegs = { "ui_mm_load_temp_01", "ui_mm_load_temp_02", "ui_mm_load_temp_03" },
		img1 = "ui_mainmenu_load_temp_01.tga", img2 = "ui_mainmenu_load_temp_02.tga", img3 = "ui_mainmenu_load_temp_03.tga"
	},
]]

	--THIRD STREET SAINTS
	["tss01"] = {
		pegs = { "ui_mm_load_tss01" },
		img1 = "ui_mainmenu_load_tss01_01.tga", img2 = "ui_mainmenu_load_tss01_02.tga", img3 = "ui_mainmenu_load_tss01_03.tga"
	},

	["tss02"] = {
		pegs = { "ui_mm_load_tss02" },
		img1 = "ui_mainmenu_load_tss02_01.tga", img2 = "ui_mainmenu_load_tss02_02.tga", img3 = "ui_mainmenu_load_tss02_03.tga"
	},

	["tss03"] = {
		pegs = { "ui_mm_load_tss03" },
		img1 = "ui_mainmenu_load_tss03_01.tga", img2 = "ui_mainmenu_load_tss03_02.tga", img3 = "ui_mainmenu_load_tss03_03.tga"
	},

	["tss04"] = {
		pegs = { "ui_mm_load_tss04" },
		img1 = "ui_mainmenu_load_tss04_01.tga", img2 = "ui_mainmenu_load_tss04_02.tga", img3 = "ui_mainmenu_load_tss04_03.tga"
	},

	--BROTHERHOOD
	["bh01"] = {
		pegs = { "ui_mm_load_bh01" },
		img1 = "ui_mainmenu_load_bh01_01.tga", img2 = "ui_mainmenu_load_bh01_02.tga", img3 = "ui_mainmenu_load_bh01_03.tga"
	},

	["bh02"] = {
		pegs = { "ui_mm_load_bh02" },
		img1 = "ui_mainmenu_load_bh02_01.tga", img2 = "ui_mainmenu_load_bh02_02.tga", img3 = "ui_mainmenu_load_bh02_03.tga"
	},

	["bh03"] = {
		pegs = { "ui_mm_load_bh03" },
		img1 = "ui_mainmenu_load_bh03_01.tga", img2 = "ui_mainmenu_load_bh03_02.tga", img3 = "ui_mainmenu_load_bh03_03.tga"
	},

	["bh04"] = {
		pegs = { "ui_mm_load_bh04" },
		img1 = "ui_mainmenu_load_bh04_01.tga", img2 = "ui_mainmenu_load_bh04_02.tga", img3 = "ui_mainmenu_load_bh04_03.tga"
	},

	["bh05"] = {
		pegs = { "ui_mm_load_bh05" },
		img1 = "ui_mainmenu_load_bh05_01.tga", img2 = "ui_mainmenu_load_bh05_02.tga", img3 = "ui_mainmenu_load_bh05_03.tga"
	},

	["bh06"] = {
		pegs = { "ui_mm_load_bh06" },
		img1 = "ui_mainmenu_load_bh06_01.tga", img2 = "ui_mainmenu_load_bh06_02.tga", img3 = "ui_mainmenu_load_bh06_03.tga"
	},

	["bh07"] = {
		pegs = { "ui_mm_load_bh07" },
		img1 = "ui_mainmenu_load_bh07_01.tga", img2 = "ui_mainmenu_load_bh07_02.tga", img3 = "ui_mainmenu_load_bh07_03.tga"
	},

	["bh08"] = {
		pegs = { "ui_mm_load_bh08" },
		img1 = "ui_mainmenu_load_bh08_01.tga", img2 = "ui_mainmenu_load_bh08_02.tga", img3 = "ui_mainmenu_load_bh08_03.tga"
	},

	["bh09"] = {
		pegs = { "ui_mm_load_bh09" },
		img1 = "ui_mainmenu_load_bh09_01.tga", img2 = "ui_mainmenu_load_bh09_02.tga", img3 = "ui_mainmenu_load_bh09_03.tga"
	},

	["bh10"] = {
		pegs = { "ui_mm_load_bh10" },
		img1 = "ui_mainmenu_load_bh10_01.tga", img2 = "ui_mainmenu_load_bh10_02.tga", img3 = "ui_mainmenu_load_bh10_03.tga"
	},

	["bh11"] = {
		pegs = { "ui_mm_load_bh11" },
		img1 = "ui_mainmenu_load_bh11_01.tga", img2 = "ui_mainmenu_load_bh11_02.tga", img3 = "ui_mainmenu_load_bh11_03.tga"
	},


	--RONIN
	["rn01"] = {
		pegs = { "ui_mm_load_rn01" },
		img1 = "ui_mainmenu_load_rn01_01.tga", img2 = "ui_mainmenu_load_rn01_02.tga", img3 = "ui_mainmenu_load_rn01_03.tga"
	},

	["rn02"] = {
		pegs = { "ui_mm_load_rn02" },
		img1 = "ui_mainmenu_load_rn02_01.tga", img2 = "ui_mainmenu_load_rn02_02.tga", img3 = "ui_mainmenu_load_rn02_03.tga"
	},

	["rn03"] = {
		pegs = { "ui_mm_load_rn03" },
		img1 = "ui_mainmenu_load_rn03_01.tga", img2 = "ui_mainmenu_load_rn03_02.tga", img3 = "ui_mainmenu_load_rn03_03.tga"
	},

	["rn04"] = {
		pegs = { "ui_mm_load_rn04" },
		img1 = "ui_mainmenu_load_rn04_01.tga", img2 = "ui_mainmenu_load_rn04_02.tga", img3 = "ui_mainmenu_load_rn04_03.tga"
	},

	["rn05"] = {
		pegs = { "ui_mm_load_rn05" },
		img1 = "ui_mainmenu_load_rn05_01.tga", img2 = "ui_mainmenu_load_rn05_02.tga", img3 = "ui_mainmenu_load_rn05_03.tga"
	},

	["rn06"] = {
		pegs = { "ui_mm_load_rn06" },
		img1 = "ui_mainmenu_load_rn06_01.tga", img2 = "ui_mainmenu_load_rn06_02.tga", img3 = "ui_mainmenu_load_rn06_03.tga"
	},

	["rn07"] = {
		pegs = { "ui_mm_load_rn07" },
		img1 = "ui_mainmenu_load_rn07_01.tga", img2 = "ui_mainmenu_load_rn07_02.tga", img3 = "ui_mainmenu_load_rn07_03.tga"
	},

	["rn08"] = {
		pegs = { "ui_mm_load_rn08" },
		img1 = "ui_mainmenu_load_rn08_01.tga", img2 = "ui_mainmenu_load_rn08_02.tga", img3 = "ui_mainmenu_load_rn08_03.tga"
	},

	["rn09"] = {
		pegs = { "ui_mm_load_rn09" },
		img1 = "ui_mainmenu_load_rn09_01.tga", img2 = "ui_mainmenu_load_rn09_02.tga", img3 = "ui_mainmenu_load_rn09_03.tga"
	},

	["rn10"] = {
		pegs = { "ui_mm_load_rn10" },
		img1 = "ui_mainmenu_load_rn10_01.tga", img2 = "ui_mainmenu_load_rn10_02.tga", img3 = "ui_mainmenu_load_rn10_03.tga"
	},

	["rn11"] = {
		pegs = { "ui_mm_load_rn11" },
		img1 = "ui_mainmenu_load_rn11_01.tga", img2 = "ui_mainmenu_load_rn11_02.tga", img3 = "ui_mainmenu_load_rn11_03.tga"
	},


	--SAMEDI
	["ss01"] = {
		pegs = { "ui_mm_load_ss01" },
		img1 = "ui_mainmenu_load_ss01_01.tga", img2 = "ui_mainmenu_load_ss01_02.tga", img3 = "ui_mainmenu_load_ss01_03.tga"
	},

	["ss02"] = {
		pegs = { "ui_mm_load_ss02" },
		img1 = "ui_mainmenu_load_ss02_01.tga", img2 = "ui_mainmenu_load_ss02_02.tga", img3 = "ui_mainmenu_load_ss02_03.tga"
	},

	["ss03"] = {
		pegs = { "ui_mm_load_ss03" },
		img1 = "ui_mainmenu_load_ss03_01.tga", img2 = "ui_mainmenu_load_ss03_02.tga", img3 = "ui_mainmenu_load_ss03_03.tga"
	},

	["ss04"] = {
		pegs = { "ui_mm_load_ss04" },
		img1 = "ui_mainmenu_load_ss04_01.tga", img2 = "ui_mainmenu_load_ss04_02.tga", img3 = "ui_mainmenu_load_ss04_03.tga"
	},

	["ss05"] = {
		pegs = { "ui_mm_load_ss05" },
		img1 = "ui_mainmenu_load_ss05_01.tga", img2 = "ui_mainmenu_load_ss05_02.tga", img3 = "ui_mainmenu_load_ss05_03.tga"
	},

	["ss06"] = {
		pegs = { "ui_mm_load_ss06" },
		img1 = "ui_mainmenu_load_ss06_01.tga", img2 = "ui_mainmenu_load_ss06_02.tga", img3 = "ui_mainmenu_load_ss06_03.tga"
	},

	["ss07"] = {
		pegs = { "ui_mm_load_ss07" },
		img1 = "ui_mainmenu_load_ss07_01.tga", img2 = "ui_mainmenu_load_ss07_02.tga", img3 = "ui_mainmenu_load_ss07_03.tga"
	},

	["ss08"] = {
		pegs = { "ui_mm_load_ss08" },
		img1 = "ui_mainmenu_load_ss08_01.tga", img2 = "ui_mainmenu_load_ss08_02.tga", img3 = "ui_mainmenu_load_ss08_03.tga"
	},

	["ss09"] = {
		pegs = { "ui_mm_load_ss09" },
		img1 = "ui_mainmenu_load_ss09_01.tga", img2 = "ui_mainmenu_load_ss09_02.tga", img3 = "ui_mainmenu_load_ss09_03.tga"
	},

	["ss10"] = {
		pegs = { "ui_mm_load_ss10" },
		img1 = "ui_mainmenu_load_ss10_01.tga", img2 = "ui_mainmenu_load_ss10_02.tga", img3 = "ui_mainmenu_load_ss10_03.tga"
	},

	["ss11"] = {
		pegs = { "ui_mm_load_ss11" },
		img1 = "ui_mainmenu_load_ss11_01.tga", img2 = "ui_mainmenu_load_ss11_02.tga", img3 = "ui_mainmenu_load_ss11_03.tga"
	},


	--EPILOGUE ULTOR
	["ep01"] = {
		pegs = { "ui_mm_load_ep01" },
		img1 = "ui_mainmenu_load_ep01_01.tga", img2 = "ui_mainmenu_load_ep01_02.tga", img3 = "ui_mainmenu_load_ep01_03.tga"
	},

	["ep02"] = {
		pegs = { "ui_mm_load_ep02" },
		img1 = "ui_mainmenu_load_ep02_01.tga", img2 = "ui_mainmenu_load_ep02_02.tga", img3 = "ui_mainmenu_load_ep02_03.tga"
	},

	["ep03"] = {
		pegs = { "ui_mm_load_ep03" },
		img1 = "ui_mainmenu_load_ep03_01.tga", img2 = "ui_mainmenu_load_ep03_02.tga", img3 = "ui_mainmenu_load_ep03_03.tga"
	},

	["ep04"] = {
		pegs = { "ui_mm_load_ep04" },
		img1 = "ui_mainmenu_load_ep04_01.tga", img2 = "ui_mainmenu_load_ep04_02.tga", img3 = "ui_mainmenu_load_ep04_03.tga"
	},


	--EXTRA MISSION
	["em01"] = {
		pegs = { "ui_mm_load_em01" },
		img1 = "ui_mainmenu_load_em01_01.tga", img2 = "ui_mainmenu_load_em01_02.tga", img3 = "ui_mainmenu_load_em01_03.tga"
	},

	--NEW GAME
	["none"] = {
		pegs = { "ui_mm_load_new_game" },
		img1 = "ui_mainmenu_load_new_game_01.tga", img2 = "ui_mainmenu_load_new_game_02.tga", img3 = "ui_mainmenu_load_new_game_03.tga"
	},


	--CUSTOM MISSIONS

	["dlc04"] = {
		pegs = { "ui_mm_load_ep01" },
		img1 = "ui_mainmenu_load_ep01_01.tga", img2 = "ui_mainmenu_load_ep01_02.tga", img3 = "ui_mainmenu_load_ep01_03.tga"
	},

	["dlc05"] = {
		pegs = { "ui_mm_load_ep01" },
		img1 = "ui_mainmenu_load_ep01_01.tga", img2 = "ui_mainmenu_load_ep01_02.tga", img3 = "ui_mainmenu_load_ep01_03.tga"
	},


	--MISSION END WALLS [nclok1405]

	["ui_c_wall_saints"] = {
		pegs = { "ui_c_wall_saints" },
		img1 = "ui_ct_wall_saints.tga", img2 = "ui_ct_wall_saints.tga", img3 = "ui_ct_wall_saints.tga"
	},
	["ui_c_wall_bhood"] = {
		pegs = { "ui_c_wall_bhood" },
		img1 = "ui_ct_wall_bhood.tga", img2 = "ui_ct_wall_bhood.tga", img3 = "ui_ct_wall_bhood.tga"
	},
	["ui_c_wall_ronin"] = {
		pegs = { "ui_c_wall_ronin" },
		img1 = "ui_ct_wall_ronin.tga", img2 = "ui_ct_wall_ronin.tga", img3 = "ui_ct_wall_ronin.tga"
	},
	["ui_c_wall_samedi"] = {
		pegs = { "ui_c_wall_samedi" },
		img1 = "ui_ct_wall_samedi.tga", img2 = "ui_ct_wall_samedi.tga", img3 = "ui_ct_wall_samedi.tga"
	},
	["ui_c_wall_ultor"] = {
		pegs = { "ui_c_wall_ultor" },
		img1 = "ui_ct_wall_ultor.tga", img2 = "ui_ct_wall_ultor.tga", img3 = "ui_ct_wall_ultor.tga"
	},
	["ui_c_wall_demoderby"] = {
		pegs = { "ui_c_wall_demoderby" },
		img1 = "ui_ct_wall_demoderby.tga", img2 = "ui_ct_wall_demoderby.tga", img3 = "ui_ct_wall_demoderby.tga"
	},
	["ui_c_wall_escort"] = {
		pegs = { "ui_c_wall_escort" },
		img1 = "ui_ct_wall_escort.tga", img2 = "ui_ct_wall_escort.tga", img3 = "ui_ct_wall_escort.tga"
	},
	["ui_c_wall_fightclub"] = {
		pegs = { "ui_c_wall_fightclub" },
		img1 = "ui_ct_wall_fightclub.tga", img2 = "ui_ct_wall_fightclub.tga", img3 = "ui_ct_wall_fightclub.tga"
	},
	["ui_c_wall_insfraud"] = {
		pegs = { "ui_c_wall_insfraud" },
		img1 = "ui_ct_wall_insfraud.tga", img2 = "ui_ct_wall_insfraud.tga", img3 = "ui_ct_wall_insfraud.tga"
	},
	["ui_c_wall_fuzz"] = {
		pegs = { "ui_c_wall_fuzz" },
		img1 = "ui_ct_wall_fuzz.tga", img2 = "ui_ct_wall_fuzz.tga", img3 = "ui_ct_wall_fuzz.tga"
	},
	["ui_c_wall_humantorch"] = {
		pegs = { "ui_c_wall_humantorch" },
		img1 = "ui_ct_wall_humantorch.tga", img2 = "ui_ct_wall_humantorch.tga", img3 = "ui_ct_wall_humantorch.tga"
	},
	["ui_c_wall_snatch"] = {
		pegs = { "ui_c_wall_snatch" },
		img1 = "ui_ct_wall_snatch.tga", img2 = "ui_ct_wall_snatch.tga", img3 = "ui_ct_wall_snatch.tga"
	},
	["ui_c_wall_drug"] = {
		pegs = { "ui_c_wall_drug" },
		img1 = "ui_ct_wall_drug.tga", img2 = "ui_ct_wall_drug.tga", img3 = "ui_ct_wall_drug.tga"
	},
	["ui_c_wall_crowdcontrol"] = {
		pegs = { "ui_c_wall_crowdcontrol" },
		img1 = "ui_ct_wall_crowdcontrol.tga", img2 = "ui_ct_wall_crowdcontrol.tga", img3 = "ui_ct_wall_crowdcontrol.tga"
	},
	["ui_c_wall_septic"] = {
		pegs = { "ui_c_wall_septic" },
		img1 = "ui_ct_wall_septic.tga", img2 = "ui_ct_wall_septic.tga", img3 = "ui_ct_wall_septic.tga"
	},
	["ui_c_wall_zombie"] = {
		pegs = { "ui_c_wall_zombie" },
		img1 = "ui_ct_wall_zombie.tga", img2 = "ui_ct_wall_zombie.tga", img3 = "ui_ct_wall_zombie.tga"
	},
	["ui_c_wall_heli"] = {
		pegs = { "ui_c_wall_heli" },
		img1 = "ui_ct_wall_heli.tga", img2 = "ui_ct_wall_heli.tga", img3 = "ui_ct_wall_heli.tga"
	},
	["ui_c_wall_mayhem"] = {
		pegs = { "ui_c_wall_mayhem" },
		img1 = "ui_ct_wall_mayhem.tga", img2 = "ui_ct_wall_mayhem.tga", img3 = "ui_ct_wall_mayhem.tga"
	},
	["ui_c_wall_mp"] = {
		pegs = { "ui_c_wall_mp" },
		img1 = "ui_ct_wall_mp.tga", img2 = "ui_ct_wall_mp.tga", img3 = "ui_ct_wall_mp.tga"
	},
	["ui_c_wall_mp_red"] = {
		pegs = { "ui_c_wall_mp_red" },
		img1 = "ui_ct_wall_mp_red.tga", img2 = "ui_ct_wall_mp_red.tga", img3 = "ui_ct_wall_mp_red.tga"
	},
	["ui_c_wall_blank"] = {
		pegs = { "ui_c_wall_blank" },
		img1 = "ui_ct_wall_blank.tga", img2 = "ui_ct_wall_blank.tga", img3 = "ui_ct_wall_blank.tga"
	},

	handles = { },
}

City_load_current_images = 0

-- Returns true if the mission is postgame (returns true on dlc05 and any other mod missions, false on main game and dlc04) [nclok1405]
function is_mission_postgame(mission_id)
	for i, id in pairs(BEFORE_POST_GAME_MISSION_NAMES) do
		if (id == mission_id) then
			return false
		end
	end
	return true
end

function city_load_init()
	--debug_print("vint", "city_load_init \n")

	peg_load("ui_mm_load_sr2_logo")

	local h = -1
	City_load_images.handles.loading_grp_h = vint_object_find("loading_grp")
	h = City_load_images.handles.loading_grp_h
	City_load_images.handles.logo = vint_object_find("logo", h)	-- Saints Row 2 Logo [nclok1405]
	City_load_images.handles.logo_jp = vint_object_find("logo_jp", h)
	City_load_images.handles.images_h = vint_object_find("images")
	h = City_load_images.handles.images_h
	City_load_images.handles.bmp1_h = vint_object_find("bmp1", h)
	City_load_images.handles.bmp2_h = vint_object_find("bmp2", h)
	City_load_images.handles.bmp3_h = vint_object_find("bmp3", h)
	City_load_images.handles.loading_text_h = vint_object_find("loading_text")	-- LOADING text [nclok1405]

	-- Loading Screen Tips [nclok1405]
	if CITY_LOAD_ENABLE_RANDOM_LOADING_TIPS then
		local loading_screen_tip_max = sizeof_table(LOADING_SCREEN_TIPS)
		local loading_screen_tip_index = rand_int(1, loading_screen_tip_max)
		local loading_screen_tip_text = LOADING_SCREEN_TIPS[loading_screen_tip_index]
		vint_set_property(City_load_images.handles.loading_text_h, "text_tag", loading_screen_tip_text)
	end

	--looping animation stuff
	City_load_images.handles.transition2_h = vint_object_find("transition2")
	h = City_load_images.handles.transition2_h
	City_load_images.handles.load3_bmp1_in_h = vint_object_find("load3_bmp1_in", h)
	local twn_h = City_load_images.handles.load3_bmp1_in_h

	if get_language() == "JP" then
		vint_set_property(City_load_images.handles.logo_jp, "visible", true)
	else
		vint_set_property(City_load_images.handles.logo_jp, "visible", false)
	end

	-- Hide Logo [nclok1405]
	if not CITY_LOAD_SHOW_LOGO then
		vint_set_property(City_load_images.handles.logo, "visible", false)
		vint_set_property(City_load_images.handles.logo_jp, "visible", false)

		-- If random tips is not enabled, hide the loading text too
		if not CITY_LOAD_ENABLE_RANDOM_LOADING_TIPS then
			vint_set_property(City_load_images.handles.loading_text_h, "visible", false)
		end
	end

	vint_set_property(twn_h, "end_event", "city_load_transition")

	-- Reset cheat shortcuts (Cheat IDs differ between save games) [nclok1405]
	Sui_cheat_shortcut_chat_all = -1	-- Cheat ID for Chat All key
	Sui_cheat_shortcut_chat_team = -1	-- Cheat ID for Chat Team key
	Sui_game_started_at_least_once = true	-- Game entered flag [nclok1405]

	-- Pause Not Active [nclok1405]
	Sui_paused = false
end

-- this is called by the game after city_load_init
function city_load_info(name)
	local last_mission_name = name
	--debug_print("vint", "city_load_INFO "..name.." \n")
	debug_print("Last Completed Mission: "..name.."\n")

	-- If the mission complete count is unknown, set the number of missions completed based on the last mission [nclok1405]
	-- This is set to the correct count if the player pauses the game at least once
	if (Sui_missions_completed == -1) then
		if (name == "none") then
			Sui_missions_completed = 0
		elseif (name == "tss01") then
			Sui_missions_completed = 1
		elseif (name == "tss02") then
			Sui_missions_completed = 2
		elseif (name == "tss03") then
			Sui_missions_completed = 3
		elseif (name == "tss04") then
			Sui_missions_completed = 4
		elseif (name == "bh01") or (name == "rn01") or (name == "ss01") then
			Sui_missions_completed = 5
		elseif (name == "bh02") or (name == "rn02") or (name == "ss02") then
			Sui_missions_completed = 6
		elseif (name == "bh03") or (name == "rn03") or (name == "ss03") then
			Sui_missions_completed = 7
		elseif (name == "bh04") or (name == "rn04") or (name == "ss04") then
			Sui_missions_completed = 8
		elseif (name == "bh05") or (name == "rn05") or (name == "ss05") then
			Sui_missions_completed = 9
		elseif (name == "bh06") or (name == "rn06") or (name == "ss06") then
			Sui_missions_completed = 10
		elseif (name == "bh07") or (name == "rn07") or (name == "ss07") then
			Sui_missions_completed = 11
		elseif (name == "bh08") or (name == "rn08") or (name == "ss08") then
			Sui_missions_completed = 12
		elseif (name == "bh09") or (name == "rn09") or (name == "ss09") then
			Sui_missions_completed = 13
		elseif (name == "bh10") or (name == "rn10") or (name == "ss10") then
			Sui_missions_completed = 14
		elseif (name == "bh11") or (name == "rn11") or (name == "ss11") then
			Sui_missions_completed = 19
		elseif (name == "ep01") then
			Sui_missions_completed = 51
		elseif (name == "ep02") then
			Sui_missions_completed = 52
		elseif (name == "ep03") then
			Sui_missions_completed = 53
		elseif (name == "ep04") then
			Sui_missions_completed = 55
		elseif (name == "dlc04") then
			Sui_missions_completed = 56
		elseif is_mission_postgame(name) then
			Sui_missions_completed = 56
		else
			Sui_missions_completed = 5
		end
		debug_print("Number of missions done set to: "..tostring(Sui_missions_completed).."\n")
	end

	if (name == "sr2_city") or (name == "sr2_mp_lobby02") or (name == "sr2_mp_lobby03") then
		-- Multiplayer [nclok1405]
		if rand_int(1, 2) == 1 then
			name = "ui_c_wall_mp"
		else
			name = "ui_c_wall_mp_red"
		end
	elseif is_mission_postgame(last_mission_name) and (CITY_LOAD_ENABLE_RANDOM_IMAGE_AFTER_DLC05) then
		-- Randomize the loading screen image after dlc05 or other mod missions [nclok1405]
		local last_mission_names_max = sizeof_table(LAST_MISSION_NAMES)
		local last_mission_names_index = rand_int(1, last_mission_names_max)
		name = LAST_MISSION_NAMES[last_mission_names_index]
		--debug_print("Randomly selected last mission:"..name)
	end

	local images = City_load_images[name]

	if images == nil then
		images = City_load_images["none"]
	end

	for i, v in images.pegs do
		peg_load(v)
	end

	-- Randomize the starting image [nclok1405]
	if is_mission_postgame(last_mission_name) and (CITY_LOAD_ENABLE_RANDOM_IMAGE_AFTER_DLC05) then
		local r = rand_int(1, 3)

		local i1 = images.img1
		local i2 = images.img2
		local i3 = images.img3

		if (r == 2) then
			images.img1 = i2
			images.img2 = i3
			images.img3 = i1
		elseif (r == 3) then
			images.img1 = i3
			images.img2 = i1
			images.img3 = i2
		end
	end

	--debug_print("vint", "images.img1: " .. images.img1 .. "\n")
	--debug_print("vint", "images.img2: " .. images.img2 .. "\n")
	--debug_print("vint", "images.img3: " .. images.img3 .. "\n")

	vint_set_property(City_load_images.handles.bmp1_h, "image", images.img1)
	vint_set_property(City_load_images.handles.bmp2_h, "image", images.img2)
	vint_set_property(City_load_images.handles.bmp3_h, "image", images.img3)
	City_load_current_images = images

end

function city_load_transition()
	vint_set_property(City_load_images.handles.bmp1_h, "alpha", 1)
	vint_set_property(City_load_images.handles.bmp2_h, "alpha", 1)
	vint_set_property(City_load_images.handles.bmp3_h, "alpha", 1)
	--debug_print("vint", "city_load_transition, end of anim reached, looping now \n")
	lua_play_anim(City_load_images.handles.transition2_h, 0)
end

function city_load_cleanup()
	--debug_print("vint", "city_load_CLEANUP \n")
	for i, v in City_load_current_images.pegs do
		peg_unload(v)
	end
	peg_unload("ui_mm_load_sr2_logo")

	debug_print("Loading Screen Exit\n")
end
