-- hud_gsi.lua: Mission/Activity HUD (Game Status Indicator?)

--########################################
--GSI
--########################################
Hud_gsi = {
	status = {
		config_index = -1,
		config = -1,
		indicator_count = 0,
		grid_spacing = 10,
		text_ind_spacing = 5, --Additional width for text only indicators
		line_height = -1,		--Height of each indicator status line
		box_height_offset = -1, --An offset for the height of the box (Changes per font)
		state = -1,
		clip_offset = 0,
		diversion_level = -1,
		fade_in_time = 1.5,
		formatted = false,
		queue_format = false,
		debug_mode = false,	-- Set true to show bounds and dump debug info to Powertools
		is_fading_out = false,
	},
	indicators = {
	},
	grid = {
	},
	elements = {
		gsi_grp_h = -1,
		icon_h = -1,
		header_grp_h = -1,
		indicators_grp_h = -1,
		clip_h = -1,
		title_text_h = -1,
		level_text_h = -1,
		level_div_text_h = -1,
		x_y_ind_h = -1,
		timer_h = -1,
		info_h = -1,
		meter_h = -1,
	},
	header = {
		width = -1,
		height = -1,
	},
	anims = {
		x_y_in_anim = -1,
		gsi_anim_in = -1,
		gsi_anim_out = -1,
		gsi_box_anim = -1,
		gsi_level_change_anim = -1,
	}
}

Hud_gsi_skins = {
	meter = {
		["Default"] = 			{ tint = {0.89, 0.749, 0.05}	},		--Default: Yellow
		["Health"] = 			{ tint = {0.75, 0 , 0} 			},		--Description: Health
      ["Damage"] = 			{ tint = {0.89, 0.749, 0.05}	}, 	--Description: Yellow
      ["Radioactivity"] =  { tint = {0, 1, 0.25} 			},		--Description: NEON Greeen
      ["Media"] =				{ tint = {0, .5, 1 } 			},		--Description: Blue
      ["Taunt"] = 			{ tint = {0.89, 0.749, 0.05} 	},		--Description: Yellow
      ["Fear"] = 				{ tint = {0.89, 0.749, 0.05}	}, 	--Description: Yellow
      ["Pleasure"] = 		{ tint = {1, 0, .5}				}, 	--Description: Pink (Escort)
      ["Footage"] = 			{ tint = {0, .5, 1} 				}, 	--Description: Blue (Escort)
		["Mayhem"] =			{ tint = {0.89, 0.749, 0.05}	},		--Descirption: Mayhem has special properties where it grabs the colors from hud_mayhem.lua
		["Fight_Club"] =		{ tint = {0.75, 0 , 0} 	},				--Descirption: Fight club is basically a red bar but requires special update functionality because the label changes all the time.
		["Nitrous"] =			{ tint = {0, .5, 1 } 			},		--Description: Blue

	}
}
Hud_gsi_meter_flash_data = {}

Hud_gsi_audio = {
	count_pos = audio_get_audio_id("SYS_HUD_CNTDWN_POS"),
	count_neg = audio_get_audio_id("SYS_HUD_CNTDWN_NEG"),
	end_pos = audio_get_audio_id("SYS_HUD_CNTDWN_ENDPOS"),
	end_neg = audio_get_audio_id("SYS_HUD_CNTDWN_ENDNEG"),
	div_complete = audio_get_audio_id("SYS_HUD_DIVERSION_COMPLETE"),
	trail_blazing = audio_get_audio_id("SYS_RACE_CHECKPOINT"),
}

--Order of creation is timer, x/y, meter, info
--GSI Indicator Indexes, increment these if there is more than one
HUD_GSI_TIMER = 0
HUD_GSI_XY = 1
HUD_GSI_METER = 5
HUD_GSI_INFO = 9

--Config Indexes
HUD_GSI_CONFIG_COL = 1		--Column Number
HUD_GSI_CONFIG_ROW = 2		--Row Number
HUD_GSI_CONFIG_SKIN = 3		--Skin Type (Indicator Specific)

--TODO: Write up behavors of skin types
--TODO: Make sure all the elements don't update their positions/widths every update. The meter has this functionality, it just needs to be adapted for the others.
--
HUD_GSI_CONFIG_MISSION = 1000
HUD_GSI_CONFIG_RACING1 = 130
HUD_GSI_CONFIG_RACING2 = 131

Hud_gsi.configs = {
	--Insurance Fraud
		--Row, Column, Indicator Handle, Indicator Type, Skin
	[0] = {
		[HUD_GSI_TIMER] = {0, 0,	"negative", },
		[HUD_GSI_XY] = 	{0, 1,	"Cash", 		},
		[HUD_GSI_METER] = 	{1, 0, 	"Cash", 			},
	},
	--Mayhem
	[1] = {
		[HUD_GSI_TIMER] = {0, 0,	"negative",	},
		[HUD_GSI_XY] = 	{0, 1,	"Cash", 		},
		[HUD_GSI_INFO] = 	{1, 0,	"Mayhem"	, 	},
		[HUD_GSI_METER] = {1, 1,	"Mayhem", 	},
	},
	--Fight Club
	[10] = {
		[HUD_GSI_XY] = {0, 0,		"", 	},
	},
	--FireTruck
	[20] = {
		[HUD_GSI_TIMER] = {0, 0,	"negative",	},
		[HUD_GSI_INFO]  =	{0, 1,	"normal",	},
	},
	-- Survival, Drive By
	[30] = {
		[HUD_GSI_TIMER] = {0, 0, 	"negative", },
		[HUD_GSI_INFO] = {0, 1, 	"",			},
	},
	--Taxi, Hostage
	[35] = {
		[HUD_GSI_TIMER] = {0, 0, 	"negative", },
		[HUD_GSI_INFO] = {0, 1, 	"Cash",			},
	},
	--Ambulance
	[40] = {
		[HUD_GSI_TIMER] = {0, 0, 	"negative",		},
		[HUD_GSI_XY] = 	{0, 1,	"", 				},
	},
	--Tow Truck, Flashing, Streaking, Snatch
	[50] = {
		[HUD_GSI_TIMER] = {0, 0, 	"negative",	},
		[HUD_GSI_XY] = 	{0, 1,	"normal", 		},
	},
	--Heli's alternate
	[51] = {
		[HUD_GSI_XY] = 	{0, 0,	"normal", 		},
	},
	--Heli's Car and XY
	[52] = {
		[HUD_GSI_XY] = 	{0, 0,	"normal", 		},
		[HUD_GSI_METER] = 	{1, 0,	"Default", 		},
	},
	--Heli for hire (Standard)
	[53] = {
		[HUD_GSI_TIMER] = {0, 0, 	"negative",	},
		[HUD_GSI_XY] = 	{0, 1,	"normal", 		},
	},
	--Pushback
	[55] = {
		[HUD_GSI_XY] = 	{0, 0,	"normal", },
	},
	--Fuzz
	[60] = {
		[HUD_GSI_TIMER]		= {0, 0,	"negative",	},
		[HUD_GSI_METER]		= {0, 1,	"Footage",	},
		[HUD_GSI_METER + 1]	= {1, 0,	"Default",	},
	},
	--Trail Blazing
	[70] = {
		[HUD_GSI_TIMER] = {0, 0,	"negative",	},
		[HUD_GSI_XY] = {0, 1, "normal", },
		[HUD_GSI_INFO] = {1, 0,	"TrailBlazing"	},
	},
	--Sewage
	[80] = {
		[HUD_GSI_XY] 		= {0, 0, "Cash_Flash_Disabled",	},
		[HUD_GSI_METER]	= {1, 0,	"Default", 		},
	},
	-- Ho-ing
	[100] = {
		[HUD_GSI_METER] 		= {0, 0, "Pleasure",			},
	},
	-- Drug Trafficking,
	[110] = {
	--	[HUD_GSI_TIMER] = {0, 0, 	"negative", },
		[HUD_GSI_XY] = 	{0, 0,	"",	},
	},
	--Demo Derby
	[112] = {
		[HUD_GSI_METER] = {0, 0, 	"Nitrous", },
		[HUD_GSI_XY] = 	{1, 0,	"Cash",	},
	},
	--Piracy
	[115] = {
		[HUD_GSI_TIMER] = {0, 0, 	"negative", },
	},
	--Crowd Control
	[120] = {
		[HUD_GSI_TIMER] = {0, 0, 	"negative",	},
		[HUD_GSI_XY] = {0, 1, 	"Cash",	},
		[HUD_GSI_METER] = {1, 0, 	"",			},
	},
	--Racing Solo
	[130] = {
		[HUD_GSI_TIMER]	= {0, 0, "negative",		},
		[HUD_GSI_XY] 		= {1, 0, "",				},
	},
	--Racing Competitive
	[131] = {
		[HUD_GSI_INFO] = 	{ 0, 0, 	"", 	},
		[HUD_GSI_XY]	=	{ 1, 0, 	"",	},
	},
	--Racing Co-op Competitive with AI
	[132] = {
		[HUD_GSI_XY] = { 0, 0, "", },
	},
	-- Escort
	[140] = {
		[HUD_GSI_METER] 		= {0, 0, "Pleasure",			},
		[HUD_GSI_METER + 1]	= {1, 0, "Footage",			},
	},
	-- Guardian_angel
	[150] = {
		[HUD_GSI_TIMER] 	= {0, 0, "Pleasure",			},
	},

	--	Coop Diversions
	[160] = {
		[HUD_GSI_INFO] = { 0, 0, "", },
		[HUD_GSI_TIMER] = { 0, 1, "negative", },
		[HUD_GSI_INFO + 1] = { 1, 0, "", },
	},

	-----------------------------
	-- Strong Arm HUDS start here
	-----------------------------

	-- SA Insurance Fraud, Racing
	[200] = {
		[HUD_GSI_TIMER]	= { 0, 0, "negative",	},
	},

	-- SA Mayhem
	[210] = {
		[HUD_GSI_INFO] = 	{0, 0,	"Mayhem"	, 	},
		[HUD_GSI_METER] = {0, 1,	"Mayhem", 	},
		[HUD_GSI_TIMER] = {1, 0,	"negative",	},
	},

	[1000] = {
		--Mission HUD!? OMG WHAT IS THIS?
	},
}

--legacy

function hud_gsi_init()

	--debug_print("vint", "hud_gsi_init()\n")
	--GSI
	local h = vint_object_find("gsi_grp")
	Hud_gsi.elements.gsi_grp_h = h
	Hud_gsi.elements.title_text_h = vint_object_find("title_txt", h)
	Hud_gsi.elements.level_text_h = vint_object_find("level_txt", h)
	Hud_gsi.elements.level_div_text_h = vint_object_find("level_div_txt", h)
	Hud_gsi.elements.header_grp_h = vint_object_find("header_grp", h)

	Hud_gsi.elements.clip_h = vint_object_find("standard_clip", h)
	Hud_gsi.elements.icon_h = vint_object_find("icon", h)
	Hud_gsi.elements.indicators_grp_h = vint_object_find("indicators_grp", h)

	--GSI Elements
	Hud_gsi.elements.xy_h 	= vint_object_find("xy_grp", h)
	Hud_gsi.elements.timer_h = vint_object_find("timer_grp", h)
	Hud_gsi.elements.info_h = vint_object_find("info_grp", h)
	Hud_gsi.elements.meter_h = vint_object_find("meter_grp", h)

	Hud_gsi.elements.standard_grp_h = vint_object_find("standard_grp", h)
	Hud_gsi.elements.standard_box_h = vint_object_find("standard_box", h)

	--GSI Standard Frame
	Hud_gsi.elements.frame_standard = {}
	Hud_gsi.elements.frame_standard.nw = vint_object_find("bg_nw", Hud_gsi.elements.standard_grp_h)
	Hud_gsi.elements.frame_standard.n = vint_object_find("bg_n", Hud_gsi.elements.standard_grp_h)
	Hud_gsi.elements.frame_standard.ne = vint_object_find("bg_ne", Hud_gsi.elements.standard_grp_h)
	Hud_gsi.elements.frame_standard.e = vint_object_find("bg_e", Hud_gsi.elements.standard_grp_h)
	Hud_gsi.elements.frame_standard.se = vint_object_find("bg_se", Hud_gsi.elements.standard_grp_h)
	Hud_gsi.elements.frame_standard.s = vint_object_find("bg_s", Hud_gsi.elements.standard_grp_h)
	Hud_gsi.elements.frame_standard.sw = vint_object_find("bg_sw", Hud_gsi.elements.standard_grp_h)
	Hud_gsi.elements.frame_standard.w = vint_object_find("bg_w", Hud_gsi.elements.standard_grp_h)
	Hud_gsi.elements.frame_standard.c = vint_object_find("bg_c", Hud_gsi.elements.standard_grp_h)
	Hud_gsi.elements.frame_standard.ghost_c = vint_object_find("bg_c_ghost", Hud_gsi.elements.standard_grp_h)

	--GSI Animations
	Hud_gsi.anims.x_y_in_anim = vint_object_find("gsi_xy_anim_in")
	Hud_gsi.anims.gsi_anim_in = vint_object_find("gsi_anim_in")
	Hud_gsi.anims.gsi_anim_out = vint_object_find("gsi_anim_out")
	Hud_gsi.anims.gsi_box_anim = vint_object_find("gsi_box_anim")
	Hud_gsi.anims.gsi_level_change_anim = vint_object_find("gsi_level_change")
	Hud_gsi.anims.gsi_fill_pulse = vint_object_find("gsi_fill_pulse")
	Hud_gsi.anims.gsi_fade_in_twn = vint_object_find("gsi_grp_alpha_twn_1", Hud_gsi.anims.gsi_anim_in)
	Hud_gsi.anims.gsi_fade_out_twn = vint_object_find("gsi_grp_alpha_twn_1", Hud_gsi.anims.gsi_anim_out)

	vint_set_property(Hud_gsi.anims.gsi_fade_out_twn, "end_event", "hud_gsi_close_final")

	--Pause Animations
	vint_set_property(Hud_gsi.anims.x_y_in_anim, "is_paused", true)
	vint_set_property(Hud_gsi.anims.gsi_anim_in, "is_paused", true)
	vint_set_property(Hud_gsi.anims.gsi_anim_out, "is_paused", true)
	vint_set_property(Hud_gsi.anims.gsi_box_anim, "is_paused", true)
	vint_set_property(Hud_gsi.anims.gsi_level_change_anim, "is_paused", true)
	vint_set_property(Hud_gsi.anims.gsi_fill_pulse, "is_paused", true)

	--Hide elements
	vint_set_property(Hud_gsi.elements.standard_grp_h , "alpha", 0)
	vint_set_property(Hud_gsi.elements.clip_h, "alpha", 0)
	vint_set_property(Hud_gsi.elements.level_text_h, "alpha", 0)
	vint_set_property(Hud_gsi.elements.icon_h, "alpha", 0)
	vint_set_property(Hud_gsi.elements.standard_box_h , "alpha", 0)

	--Persistant GSI
	Hud_gsi_persistant.handles = {}
	Hud_gsi_persistant.handles.grp = vint_object_find("persistant_grp")
	Hud_gsi_persistant.handles.poloroid_bmp = vint_object_find("poloroid_bmp", Hud_gsi_persistant.handles.grp )
	Hud_gsi_persistant.handles.poloroid_bmp = vint_object_find("poloroid_bmp", Hud_gsi_persistant.handles.grp )
	Hud_gsi_persistant.handles.poloroid_title_txt = vint_object_find("poloroid_title_txt", Hud_gsi_persistant.handles.grp)
	Hud_gsi_persistant.handles.poloroid_line_1_txt = vint_object_find("poloroid_line_1_txt", Hud_gsi_persistant.handles.grp)
	Hud_gsi_persistant.handles.poloroid_line_2_txt = vint_object_find("poloroid_line_2_txt", Hud_gsi_persistant.handles.grp)

	--GSI Persistant Frame
	Hud_gsi_persistant.handles.frame = {}
	Hud_gsi_persistant.handles.frame.nw = vint_object_find("bg_nw", Hud_gsi_persistant.handles.grp )
	Hud_gsi_persistant.handles.frame.n = vint_object_find("bg_n", Hud_gsi_persistant.handles.grp)
	Hud_gsi_persistant.handles.frame.ne = vint_object_find("bg_ne", Hud_gsi_persistant.handles.grp)
	Hud_gsi_persistant.handles.frame.e = vint_object_find("bg_e", Hud_gsi_persistant.handles.grp)
	Hud_gsi_persistant.handles.frame.se = vint_object_find("bg_se", Hud_gsi_persistant.handles.grp)
	Hud_gsi_persistant.handles.frame.s = vint_object_find("bg_s", Hud_gsi_persistant.handles.grp)
	Hud_gsi_persistant.handles.frame.sw = vint_object_find("bg_sw", Hud_gsi_persistant.handles.grp)
	Hud_gsi_persistant.handles.frame.w = vint_object_find("bg_w", Hud_gsi_persistant.handles.grp)
	Hud_gsi_persistant.handles.frame.c = vint_object_find("bg_c", Hud_gsi_persistant.handles.grp)
	Hud_gsi_persistant.handles.frame.ghost_c = vint_object_find("bg_c_ghost", Hud_gsi_persistant.handles.grp)

	local language = get_language()
	local line_width, line_height = element_get_actual_size(vint_object_find("label_txt",Hud_gsi.elements.timer_h))
	local box_height_offset = -15
	if language == "SK" or language == "JP" or language == "CH" then
		line_height = line_height - 8
		box_height_offset = -8
	else
		--Standard font
		line_height = line_height - 8
	end

	Hud_gsi.status.box_height_offset = box_height_offset
	Hud_gsi.status.line_height = line_height

	--Hide persistant GSI
	vint_set_property(Hud_gsi_persistant.handles.grp, "visible", false)

	--Init fade fade out status
	Hud_gsi.status.is_fading_out = false

	--Subscribe to events
	vint_datagroup_add_subscription("sr2_local_player_gameplay_indicator_status", "insert", "hud_gsi_update")
	vint_datagroup_add_subscription("sr2_local_player_gameplay_indicator_status", "update", "hud_gsi_update")

		--Subscribe to events
	vint_dataitem_add_subscription("persistent_gsi", "insert",  "hud_gsi_persistant_update")
end

function hud_gsi_update(di_h)

	local data_type, param1, param2, param3, param4, param5, param6, param7, param8, param9  = vint_dataitem_get(di_h)

	if Hud_gsi.status.debug_mode == true then
		debug_print("vint", "GSI Update: " .. var_to_string(data_type).. "\n")
	end

	if data_type == "configuration" then
		--@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
		--Debug Start
		--@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
		if Hud_gsi.status.debug_mode == true then
			debug_print("vint", " gsi state: " .. var_to_string(param1) .. "\n")
			debug_print("vint", " configuration: " .. var_to_string(param2) .. "\n")
			debug_print("vint", " icon_bitmap_name: " .. var_to_string(param3) .. "\n")
			debug_print("vint", " gameplay_title crc: " .. var_to_string(param4) .. "\n")
			debug_print("vint", " gameplay_title string: " .. var_to_string(param5) .. "\n")
			debug_print("vint", " diversion_level: " .. var_to_string(param6) .. "\n")
			debug_print("vint", " visible: " .. var_to_string(param7) .. "\n")
			debug_print("vint", " is_diversion: " .. var_to_string(param8) .. "\n")
			debug_print("vint", " indicator_count: " .. var_to_string(param9) .. "\n\n")
		end
		--@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

		local gsi_state				= param1	--1 = initializing, 2 = running, 3 = end
		local config 					= param2	--Configuration #
		local icon_bmp_name			= param3	--Icon Bitmap Name
		local gameplay_title_crc	= param4	--Title CRC (
		local diversion_level		= param6	--Diversion Level # string
		local visible					= param7 --Visible
		local is_diversion 			= param8	--Is it a diversion?
		local indicator_count		= param9	--Indicator Count (ONLY FOR MISSIONS)

		-- Set current gameplay [nclok1405]
		-- Cannot assign nil on global variables
		if gameplay_title_crc == nil then
			--debug_print("gameplay_title_crc is nil!")
			Sui_current_gameplay_title_crc = 0
		else
			Sui_current_gameplay_title_crc = gameplay_title_crc
		end
		if diversion_level == nil then
			--debug_print("diversion_level is nil!")
			Sui_current_gameplay_level = 0
		else
			Sui_current_gameplay_level = diversion_level
		end

		--Increment diversions because the levels are indexed by 0
		--DAD: We made the diversions pass in the right values.
--		if is_diversion == true then
--			diversion_level = diversion_level + 1
--		end

		--Update Diversion Level
		if diversion_level ~= Hud_gsi.status.diversion_level then

			--Create Diversion level string
			local level_str = ""
			if diversion_level ~= nil and diversion_level ~= 0 then
				level_str = "LVL" .. diversion_level
			else
				level_str = ""
			end

			if icon_bmp_name == nil or icon_bmp_name == "" then
				--No icon so use the Use Diversion Style Text
				vint_set_property(Hud_gsi.elements.level_div_text_h, "visible", true)
				vint_set_property(Hud_gsi.elements.level_div_text_h, "text_tag", level_str)
				vint_set_property(Hud_gsi.elements.level_text_h, "visible", false)

				if gsi_state == 2 then
					--Since the level can expand to 2 digits, Recalculate header and queue a format request
					--Only do this if the gsi is already running.
					local test_x, test_y = vint_get_property(Hud_gsi.elements.level_div_text_h, "anchor")
					local test_w, test_h = element_get_actual_size(Hud_gsi.elements.level_div_text_h)
					Hud_gsi.header.width = test_x + test_w
					hud_gsi_queue_format()
				end
			else
				--Use Standard Text
				vint_set_property(Hud_gsi.elements.level_text_h, "visible", true)
				vint_set_property(Hud_gsi.elements.level_text_h, "text_tag", level_str)
				vint_set_property(Hud_gsi.elements.level_div_text_h, "text_tag", "")
				vint_set_property(Hud_gsi.elements.level_div_text_h, "visible", false)

				--Play Level fade in Animation for activity level text
				vint_set_property(Hud_gsi.elements.level_text_h, "alpha", 0)
				lua_play_anim(Hud_gsi.anims.gsi_level_change_anim, Hud_gsi.status.fade_in_time)
			end


			Hud_gsi.status.diversion_level = diversion_level
		end

		if config == HUD_GSI_CONFIG_RACING1 or config == HUD_GSI_CONFIG_RACING2 then
			--Reset text strings for levels during races
			vint_set_property(Hud_gsi.elements.level_text_h, "text_tag", "")
			vint_set_property(Hud_gsi.elements.level_div_text_h, "text_tag", "")
		end

		if gsi_state ~= Hud_gsi.status.state or gsi_state == 4 then

			if gsi_state == 1 or (Hud_gsi.status.formatted == false and Hud_gsi.status.state == -1 and gsi_state ~= 3) or (gsi_state == 4 and config == HUD_GSI_CONFIG_MISSION and Hud_gsi.status.formatted == false ) then

				--Make sure we set the flag to unformatted.
				Hud_gsi.status.formatted = false

				--Start out with a fresh number of indicators
				local number_of_indicators = 0

				-- Set Fight Club flag [nclok1405]
				if (gameplay_title_crc == SUI_GAMEPLAY_CRC_FIGHTCLUB) then
					Sui_fight_club = true
				end

				--Update Title
				hud_gsi_update_header(icon_bmp_name, gameplay_title_crc, diversion_level, is_diversion)

				if config ~= HUD_GSI_CONFIG_MISSION then
					--Use pre-configuration settings

					--Update configuration layout
					hud_gsi_update_config(config)

					--Show the GSI
					vint_set_property(Hud_gsi.elements.standard_grp_h, "alpha", 1)

					--Get number of indicators used in configuration
					for idx, val in Hud_gsi.status.config do
						number_of_indicators = number_of_indicators + 1
					end

				else
					--Use Mission config

					--Clear Indicator Objects
					for idx, val in Hud_gsi.indicators do
						vint_object_destroy(val.elements.grp_h)
					end

					--Clear Indicator tables, grid and meter flash data
					Hud_gsi.indicators = {}
					Hud_gsi.grid = {}
					Hud_gsi_meter_flash_data = {}

					--Use Mission Configuration, then you have to wait until the indicators are setup here.
					Hud_gsi.status.config_index = HUD_GSI_CONFIG_MISSION
					Hud_gsi.status.config = Hud_gsi.configs[HUD_GSI_CONFIG_MISSION]

					--Missions get the number of active indicators needed to populate the setup
					number_of_indicators = indicator_count

					if number_of_indicators > 2 then
						debug_print("", "MISSION GSI ERROR!!! The mission is trying to use more than two indicators at once\n")
					end

				end

				--Store status data into files
				Hud_gsi.status.indicator_count = number_of_indicators

			elseif gsi_state == 3 then
				-- Set Fight Club flag [nclok1405]
				if (gameplay_title_crc == SUI_GAMEPLAY_CRC_FIGHTCLUB) then
					Sui_fight_club = false
				end

				--Set the flag to unformatted.
				Hud_gsi.status.formatted = false

				--Reset the diversion level
				Hud_gsi.status.diversion_level = -1

				--GSI state should now close
				hud_gsi_close()

			elseif gsi_state == 4 and config == HUD_GSI_CONFIG_MISSION then

				--This is used if the hud needs to change configuration midway through a mission

				--Since we are killing the old format, set the flag to unformatted.
				Hud_gsi.status.formatted = false

				--Update Title if its changed...
				hud_gsi_update_header(icon_bmp_name, gameplay_title_crc, diversion_level, is_diversion)

				--Clear Indicator Objects
				for idx, val in Hud_gsi.indicators do
					vint_object_destroy(val.elements.grp_h)
				end

				--Clear Indicator tables and grid
				Hud_gsi.indicators = {}
				Hud_gsi.grid = {}
				Hud_gsi_meter_flash_data = {}

				--Use Mission Configuration, you have to wait until the indicators are setup here.
				Hud_gsi.status.config_index = HUD_GSI_CONFIG_MISSION
				Hud_gsi.status.config = Hud_gsi.configs[HUD_GSI_CONFIG_MISSION]

				--Store status data into files
				Hud_gsi.status.indicator_count = indicator_count

			end
			Hud_gsi.status.state = gsi_state
		end

		if visible == nil then
			visible = true
		end

		--TODO: Delete this line if you want to hide the gsi
		visible = true

		vint_set_property(Hud_gsi.elements.gsi_grp_h, "visible", visible)

	elseif data_type == nil then
		--No specified data_type so don't do anything.
	else

		--These are used for every indicator
		local ind_index			=	param1	--Element Index
		local visible				= 	param2	--Is Element Visible?
		local label_crc			=	param3	--Label CRC

		--Error checking
		if Hud_gsi.status.config == -1 then
			debug_print("vint", "GSI: No configurations were created, so we do not update shit.\n")
			return
		end

		--Use Mission Configuration, you have to wait until the indicators are setup here.
		if Hud_gsi.status.config[ind_index] == nil and Hud_gsi.status.config ~= Hud_gsi.configs[HUD_GSI_CONFIG_MISSION] then
			debug_print("vint", "GSI: Indicator not supported in current configuration. [element_type = " .. var_to_string(ind_index) .. " ]\n")
			return
		end

		--Get skin from the configuration index
		local skin
		if Hud_gsi.status.config ~= Hud_gsi.configs[HUD_GSI_CONFIG_MISSION] then
			skin = Hud_gsi.status.config[ind_index][HUD_GSI_CONFIG_SKIN]
		else
			skin = ""
		end

		--TIMER
		if	data_type == "timer" then

			--@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
			--Debug Start
			--@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
			if Hud_gsi.status.debug_mode == true then
				debug_print("vint", " timer index: " .. param1 .. "\n")
				debug_print("vint", " visible: " .. var_to_string(param2) .. "\n")
				debug_print("vint", " description crc: " .. var_to_string(param3) .. "\n")
				debug_print("vint", " description: " .. var_to_string(param4) .. "\n")
				debug_print("vint", " seconds left: " .. var_to_string(param5) .. " is a positive timer: " .. var_to_string(param6) .. "\n\n")
			end
			--@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

			--Get specific indicator parameters
			local seconds				=	param5	--Time: seconds left
			local is_positive_timer	=	param6	--Is it a positive timer?

			--Check if indicator has been created
			if Hud_gsi.indicators[ind_index] == nil then
				--need to create the indicator
				hud_gsi_create_timer(ind_index, skin, visible)
			end

			--Update Timer
			hud_gsi_update_timer(ind_index, visible, skin, label_crc, seconds)

		--X OF Y INDICATOR
		elseif data_type == "x_of_y_indicator" then

			--@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
			--Debug Start
			--@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
			if Hud_gsi.status.debug_mode == true then
				debug_print("vint", " x_of_y_indicator index: " .. param1 .. "\n")
				debug_print("vint", " visible: " .. var_to_string(param2)  .. "\n")
				debug_print("vint", " description crc: " .. var_to_string(param3) .. "\n")
				debug_print("vint", " description str: " .. var_to_string(param4)  .. "\n")
				debug_print("vint", " current amount: " .. var_to_string(param5) .. " target amount: " .. var_to_string(param6) .. " is it money? " .. var_to_string(param7) .. "\n\n")
			end
			--@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

			--Get specific indicator parameters
			local x_value	=	param5	--Time: seconds left
			local y_value	=	param6	--Is it a positive timer?
			local is_cash	=	param7	--Is the indicator cash

			--If skin is left blank then
			if skin == "" then
				if is_cash == true then
					skin = "cash"
				else
					skin = "default"
				end
			end

			--Check if indicator has been created
			if Hud_gsi.indicators[ind_index] == nil then
				--need to create the indicator
				hud_gsi_create_xy(ind_index, skin)
			end

			--Update Indicator
			hud_gsi_update_xy(ind_index, visible, skin, label_crc, x_value, y_value)

		--METER
		elseif data_type == "meter" then

			--@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
			--Debug Start
			--@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
			if Hud_gsi.status.debug_mode == true then
				debug_print("vint", " meter index: " .. param1 .. "\n")
				debug_print("vint", " visible: " .. var_to_string(param2) .. "\n")
				debug_print("vint", " description crc: " .. var_to_string(param3) .. "\n")
				debug_print("vint", " description: " .. var_to_string(param4) .. "\n")
				debug_print("vint", " current amount: " .. var_to_string(param5) .. "\n\n")
			end
			--@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

			--Get specific indicator parameters
			local meter_pct	=	param5	--Meter Percentage
			local skin = param6				--Skin
			local is_flashing = param7		--Is the meter flashing!? oooohhh

			--override skin if not a mission
			if Hud_gsi.status.config_index ~= HUD_GSI_CONFIG_MISSION then
				--Get specific indicator parameters
				skin = Hud_gsi.status.config[ind_index][HUD_GSI_CONFIG_SKIN]
			end

			--Check if indicator has been created
			if Hud_gsi.indicators[ind_index] == nil then
				--need to create the indicator
				hud_gsi_create_meter(ind_index, skin)
			end

			--Update Indicator
			hud_gsi_update_meter(ind_index, visible, skin, label_crc, meter_pct, is_flashing)

		--INFORMATION INDICATOR
		elseif data_type == "information_indicator" then

			--@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
			--Debug Start
			--@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
			if Hud_gsi.status.debug_mode == true then
				debug_print("vint", " information_indicator index: " .. param1 .. "\n")
				debug_print("vint", " visible: " .. var_to_string(param2) .. "\n")
				debug_print("vint", " description crc: " .. param3 .. "\n")
				debug_print("vint", " description: " .. var_to_string(param4) .. "\n")
				debug_print("vint", " information crc: " .. param5 .. "\n")
				debug_print("vint", " information: " .. var_to_string(param6) .. "\n\n")
			end
			--@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

			local info_crc = param5
			local info_value = param6

			--Check if indicator has been created
			if Hud_gsi.indicators[ind_index] == nil then
				--need to create the indicator
				hud_gsi_create_info(ind_index, skin)
			end

			--Update Indicator
			hud_gsi_update_info(ind_index, visible, skin, label_crc, info_crc, info_value)
		end
	end

	--Check if the gsi has been re-formatted
	if Hud_gsi.status.formatted == false and Hud_gsi.status.state ~= 3 then
		local indicators_created = 0
		for i, val in Hud_gsi.indicators do
			indicators_created = indicators_created + 1
		end

		--If we have all the data then format it!
		if indicators_created == Hud_gsi.status.indicator_count then
			if Hud_gsi.status.config_index == HUD_GSI_CONFIG_MISSION then
				--Mission config doesn't exist until this is run
				hud_gsi_update_config(HUD_GSI_CONFIG_MISSION)
			end

			--If we are in state 4, it means to do a partial refresh. Otherwise play the opening animation.
			if Hud_gsi.status.state == 4 then
				local width, height = hud_gsi_update_layout()
				hud_gsi_frame_animate(width, height, 0, Hud_gsi.elements.frame_standard)
			else
				--Open up GSI
				hud_gsi_open()
			end

			--We should now be formatted so set the flag to true
			Hud_gsi.status.formatted = true
		end
	end

	--Process the GSI
	hud_gsi_process()

end

--[[
	Resets the configuration and clears out old config
]]
function hud_gsi_update_config(config_index)

	local config = Hud_gsi.configs[config_index]

	if config == nil then
		debug_print("vint", "Failed to update config. Config index doesn't exist\n")
		return false
	end

	if config_index ~= Hud_gsi.status.config_index or config_index == HUD_GSI_CONFIG_MISSION then

		if config_index ~= HUD_GSI_CONFIG_MISSION then
			--Standard Configuration

			--Clear out all old indicator elements
			for idx, val in Hud_gsi.indicators do
				vint_object_destroy(val.elements.grp_h)
			end

			--Clear indicator tables and grid
			Hud_gsi.indicators = {}
			Hud_gsi.grid = {}
			Hud_gsi_meter_flash_data = {}

			--Build the new config
			for idx, val in config do
				local col = val[HUD_GSI_CONFIG_COL]
				local row = val[HUD_GSI_CONFIG_ROW]
				local indicator_index = idx

				--Add item to grid
				hud_gsi_grid_item_add(row, col, indicator_index)
			end
		else
			--Mission Configuration

			--Oh shit this is all fucking crazy
			local indicator_mess = {}		--Indicator mess will be a table full of indicator indexes and indicator priorities
			local indicator_counter = 0
			local indicator_priority = 1

			--Prioritie defines
			local priority_timer = 1
			local priority_xy 	= 2
			local priority_info 	= 3
			local priority_meter = 4

			--first sort through the items to see what we have and build priority for them


			for idx, val in Hud_gsi.indicators do

				--Calculate priority
				if idx == HUD_GSI_TIMER then
					indicator_priority = priority_timer
				elseif idx < HUD_GSI_METER then
					indicator_priority = priority_meter
				elseif idx < HUD_GSI_INFO then
					indicator_priority = priority_info
				else
					--other... for now this is X/Y
					indicator_priority = priority_xy
				end

				indicator_mess[indicator_counter] = {["index"] = Hud_gsi.indicators[idx].data.index,	["priority"] = indicator_priority}
				indicator_counter = indicator_counter + 1
			end

			--Assign priorities to the items
			local temp_indicator_storage
			local flag = false
			while flag == false do

				flag = true

				for i = 0, Hud_gsi.status.indicator_count - 2 do

					if indicator_mess[i].priority > indicator_mess[i + 1].priority then
						--swap indexes if the priority is greater
						temp_indicator_storage = indicator_mess[i]
						indicator_mess[i] = indicator_mess[i + 1]
						indicator_mess[i + 1] = temp_indicator_storage
						flag = false
						break
					end
				end
			end

			--Place items into the grid
			local col = 0
			local row = 0
			local indicator_index = 0
			local loop_index = 0
			local indicator_placement = Hud_gsi.status.indicator_count
			local end_loop = false

			--Add Grid Items
			if indicator_counter ~= 0 then
				--First Indicator
				for i = 0, indicator_counter - 1 do
					if i >= 2 then
						--no more than two indicators allowd
						break
					end
					if indicator_mess[i].index ~= nil then
						hud_gsi_grid_item_add(0, i, indicator_mess[i].index)
					end
				end
			end
		end
		Hud_gsi.status.config_index = config_index
		Hud_gsi.status.config = config
	end
end

function hud_gsi_grid_item_add(col, row, idx)
	if Hud_gsi.grid[row] == nil then
		Hud_gsi.grid[row] = {}
	end
	Hud_gsi.grid[row][col] = idx
end

function hud_gsi_open()
	if Hud_gsi.status.debug_mode == true then
		debug_print("vint", "hud_gsi_open()\n")
	end

	--Enable fade in tween ...
	vint_set_property(Hud_gsi.anims.gsi_fade_in_twn , "state", "paused")

	--Animation doesn't play for a second so we need to hide some shit. Boosh.
	vint_set_property(Hud_gsi.elements.clip_h, "alpha", 0)
	vint_set_property(Hud_gsi.elements.icon_h, "alpha", 0)
	vint_set_property(Hud_gsi.elements.standard_box_h , "alpha", 0)
	lua_play_anim(Hud_gsi.anims.gsi_anim_in, Hud_gsi.status.fade_in_time)

	local width, height = hud_gsi_update_layout()

	--Set initial values for GSI frame to animate in from
	hud_gsi_frame_resize(20, height, Hud_gsi.elements.frame_standard)

	--Animate GSI Frame
	hud_gsi_frame_animate(width, height, Hud_gsi.status.fade_in_time, Hud_gsi.elements.frame_standard)
end

function hud_gsi_update_layout()
	--@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
		--Debug Start
	--@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
	if Hud_gsi.status.debug_mode == true then
		debug_print("vint", "Updating Layout. hud_gsi_update_layout()\n")
	end
	--@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

	for row = 0, 10 do
		if Hud_gsi.grid[row] == nil then
			break
		end
		for col = 0, 10 do
			if Hud_gsi.grid[row][col] == nil then
				break
			end
			local indicator_index = Hud_gsi.grid[row][col]
			local indicator_obj = Hud_gsi.indicators[indicator_index]

			if indicator_obj == nil then
				break
			end

			--Do processing for layout
			if row == 0 and col == 0 then
				--First Element (Incredible) place it at 0,0
				vint_set_property(indicator_obj.elements.grp_h, "anchor", 0, 0)
			end

			if row == 0 and col == 1 then
				--Line 1, Item 2
				local prev_indicator_index = Hud_gsi.grid[0][0]
				local prev_indicator_obj = Hud_gsi.indicators[prev_indicator_index]
				local p_x, p_y = vint_get_property(prev_indicator_obj.elements.grp_h, "anchor")
				local p_w = prev_indicator_obj.elements.width
				local object_offset = 0

				local x = p_x + p_w + Hud_gsi.status.grid_spacing + object_offset

				vint_set_property(indicator_obj.elements.grp_h, "anchor", x, p_y)
			end

			if row == 1 and col == 0 then
				--Line 2, Item 1
				local prev_indicator_index = Hud_gsi.grid[0][0]
				local prev_indicator_obj = Hud_gsi.indicators[prev_indicator_index]
				local p_x, p_y = vint_get_property(prev_indicator_obj.elements.grp_h, "anchor")
				local p_h = Hud_gsi.status.line_height
				local y = p_h
				vint_set_property(indicator_obj.elements.grp_h, "anchor", p_x, y)
			end

			if row == 1 and col == 1 then
				--Line 2, Item 2
				local prev_indicator_index = Hud_gsi.grid[1][0]
				local prev_indicator_obj = Hud_gsi.indicators[prev_indicator_index]
				local p_x, p_y = vint_get_property(prev_indicator_obj.elements.grp_h, "anchor")
				local p_w = prev_indicator_obj.elements.width
				local object_offset = 0

				local x = p_x + p_w + Hud_gsi.status.grid_spacing + object_offset
				vint_set_property(indicator_obj.elements.grp_h, "anchor", x, p_y)
			end
		end
	end

	--Check if both rows have meters in them...
	--We need to get them aligned if so...
	if Hud_gsi.grid[0] ~= nil and Hud_gsi.grid[1] ~= nil then
		if Hud_gsi.grid[0][0] == HUD_GSI_METER and Hud_gsi.grid[1][0] == HUD_GSI_METER + 1 then
			local meter_1_obj = Hud_gsi.indicators[HUD_GSI_METER]
			local meter_2_obj = Hud_gsi.indicators[HUD_GSI_METER + 1]
			hud_gsi_update_meter_alignment(meter_1_obj, meter_2_obj)
		end
	end

	--Calculate size of box
	--Calculate largest width
	local header_width, header_height = element_get_actual_size(Hud_gsi.elements.header_grp_h)

	--Calculate how many lines we have in the grid
	local number_of_lines_in_grid = 0

	for idx, val in Hud_gsi.grid do
		number_of_lines_in_grid = number_of_lines_in_grid + 1
	end

	--See how many lines are visible within that configuration
	local number_of_lines_visible_in_grid = 0
	local line_found = false
	local current_line_width = 0
	local largest_line_width = 0

	if number_of_lines_in_grid > 0 then
		for outer_idx, outer_val in Hud_gsi.grid do
			line_found = false
			current_line_width = 0
			for inner_idx, inner_val in outer_val do
				--is the indicator visible?

				if Hud_gsi == nil or Hud_gsi.indicators == nil or Hud_gsi.indicators[inner_val] == nil or Hud_gsi.indicators[inner_val].elements == nil then
					break
				end

				if Hud_gsi.indicators[inner_val].elements.visible == true then
					if line_found == false then
						number_of_lines_visible_in_grid = number_of_lines_visible_in_grid + 1
						line_found = true
					end
					current_line_width = Hud_gsi.indicators[inner_val].elements.width + current_line_width
				end
			end
			if current_line_width > largest_line_width then
				largest_line_width = current_line_width
			end
		end
	end

	local indicator_height = number_of_lines_visible_in_grid * Hud_gsi.status.line_height
	local indicator_width = largest_line_width

	--Finalize width and height values for the header and indicator
	local width = 0
	local height = 0
	if indicator_width > Hud_gsi.header.width then
		width = indicator_width + 5
	else
		width = Hud_gsi.header.width
	end

	width = width + Hud_gsi.status.clip_offset - 8
	height = indicator_height + Hud_gsi.header.height + Hud_gsi.status.box_height_offset

	--@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
	--Debug Start
	--@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
	if Hud_gsi.status.debug_mode == true then
		show_bounds(Hud_gsi.elements.header_grp_h)
		show_bounds(Hud_gsi.elements.indicators_grp_h)
	end
	--@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

	return width, height
end

Hud_gsi_twns = {}

function hud_gsi_frame_update(param1, event)

	local active_frame

	if event == "per_frame_event" then
		--Callback was from tween
		--If the callback was from a tween the parameter is a number.. and we always want to use the standard frame in that case
		active_frame = Hud_gsi.elements.frame_standard
	else
		-- calling_not_from_tween, so we should use the specified parameter
		active_frame = param1
	end

	--setup limits
	local source_se_x, source_se_y, anchor_x, anchor_y, c_anchor_y, c_anchor_x, target_x, target_y

	--Get ghost frame values and floor them
	local width, height = vint_get_property(active_frame.ghost_c, "source_se")
	width = floor(width)
	height = floor(height)

	--North
	source_se_x, source_se_y = vint_get_property(active_frame.n,"source_se")
	vint_set_property(active_frame.n, "source_se", width, source_se_y)

	--West
	source_se_x, source_se_y = vint_get_property(active_frame.w,"source_se")
	vint_set_property(active_frame.w, "source_se", source_se_x, height)

	--Center
	vint_set_property(active_frame.c, "source_se", width, height)
	c_anchor_y, c_anchor_x = vint_get_property(active_frame.c, "anchor")

	target_x = c_anchor_x + width - 1
	target_y = c_anchor_y + height + 1

	--North East
	anchor_x, anchor_y = vint_get_property(active_frame.ne, "anchor")
	vint_set_property(active_frame.ne, "anchor", target_x , anchor_y)

	--East
	anchor_x, anchor_y = vint_get_property(active_frame.e, "anchor")
	source_se_x, source_se_y = vint_get_property(active_frame.e, "source_se")
	vint_set_property(active_frame.e, "anchor", target_x , anchor_y)
	vint_set_property(active_frame.e, "source_se", source_se_x, height)

	--South West
	anchor_x, anchor_y = vint_get_property(active_frame.sw, "anchor")
	vint_set_property(active_frame.sw, "anchor", anchor_x, target_y)

	--South
	anchor_x, anchor_y = vint_get_property(active_frame.s, "anchor")
	vint_set_property(active_frame.s, "anchor", anchor_x, target_y)
	source_se_x, source_se_y = vint_get_property(active_frame.s, "source_se")
	vint_set_property(active_frame.s, "source_se", width, source_se_y)

	--South East
	vint_set_property(active_frame.se, "anchor", target_x, target_y)

	--Only resize the clip if we are changing the standard frame
	if active_frame == Hud_gsi.elements.frame_standard then
		--Set Clip
		vint_set_property(Hud_gsi.elements.clip_h, "clip_size",  width + 15 - Hud_gsi.status.clip_offset, height + 15)
	end
end

function hud_gsi_frame_animate(width, height, delay, active_frame)
	width = floor(width)
	height = floor(height)

	--Tween ghost part and set callback to update the actual parts
	local twn_h = vint_object_find("bg_twn_1", Hud_gsi.anims.gsi_box_anim)
	local c_width, c_height = vint_get_property(active_frame.ghost_c, "source_se")
	vint_set_property(twn_h, "start_value", c_width, c_height)
	vint_set_property(twn_h, "end_value", width, height)
	vint_set_property(twn_h, "per_frame_event", "hud_gsi_frame_update")
	vint_set_property(twn_h, "target_handle", active_frame.ghost_c)
	lua_play_anim(Hud_gsi.anims.gsi_box_anim, delay)
end


function hud_gsi_frame_resize(width, height, active_frame)
	--Floor Width/Height
	width = floor(width)
	height = floor(height)
	--Set base size and update the frame
	vint_set_property(active_frame.ghost_c, "source_se", width, height)
	hud_gsi_frame_update(active_frame)
end

function hud_gsi_close()
	--@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
	--Debug Start
	--@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
	if Hud_gsi.status.debug_mode == true then
		debug_print("vint", "hud_gsi_close()\n")
	end

	Sui_current_gameplay_title_crc = 0	-- Gameplay Ended [nclok1405]

	Hud_gsi.status.is_fading_out = true

	--Disable fade in tween in case we are fading in...
	vint_set_property(Hud_gsi.anims.gsi_fade_in_twn , "state", "disabled")

	--Fade out from current alpha state
	local alpha_val = vint_get_property(Hud_gsi.elements.standard_grp_h, "alpha")
	vint_set_property(Hud_gsi.anims.gsi_fade_out_twn, "start_value", alpha_val)

	lua_play_anim(Hud_gsi.anims.gsi_anim_out, 0)

	--close complete

	--Reset diversion level tag
	vint_set_property(Hud_gsi.elements.level_div_text_h, "text_tag", "")
end

function hud_gsi_close_final()

	--Reset fade out status
	Hud_gsi.status.is_fading_out = false
	--if the persistant hud is active we need to show it now.
	if Hud_gsi_persistant.status > 0 then
		hud_gsi_persistant_show()
	end

end

function hud_gsi_update_header(icon_bmp_name, title_crc, level, is_diversion)
	local clip_offset = 0

	if icon_bmp_name == nil or icon_bmp_name == "" then
		--No icon so it must be a diversion

		--Hide placeholder icon
		vint_set_property(Hud_gsi.elements.icon_h, "visible", false)

		debug_print("vint", "Hud_gsi.elements.icon_h: should be invisible\n")

		--Set group offset
		clip_offset = 15
		local clip_x, clip_y = vint_get_property(Hud_gsi.elements.clip_h, "anchor")
		vint_set_property(Hud_gsi.elements.clip_h, "anchor", clip_offset, clip_y)

	else
		--Ok, so there is an icon... format it so.

		--Set bitmap Name of icon
		vint_set_property(Hud_gsi.elements.icon_h, "image", icon_bmp_name)
		vint_set_property(Hud_gsi.elements.icon_h, "visible", true)

		--Set group offset
		clip_offset = 50
		local clip_x, clip_y = vint_get_property(Hud_gsi.elements.clip_h, "anchor")
		vint_set_property(Hud_gsi.elements.clip_h, "anchor", clip_offset, clip_y)
	end

	if Sui_mod_mission_title ~= "" then
		--Mod Mission Title [nclok1405]
		vint_set_property(Hud_gsi.elements.title_text_h, "text_tag", Sui_mod_mission_title)
	else
		--Set Title with crc
		vint_set_property(Hud_gsi.elements.title_text_h, "text_tag_crc", title_crc)
	end

	--Uncomment this to replace title with CRC for programming purposes [nclok1405]
	--vint_set_property(Hud_gsi.elements.title_text_h, "text_tag", tostring(title_crc))

	--Adjust positions
	local title_w, title_h = element_get_actual_size(Hud_gsi.elements.title_text_h)
	local title_x, title_y = vint_get_property(Hud_gsi.elements.title_text_h, "anchor")
	local target_x = title_w + title_x + 5
	vint_set_property(Hud_gsi.elements.level_div_text_h, "anchor", target_x, title_y)

	local test_x, test_y = vint_get_property(Hud_gsi.elements.level_div_text_h, "anchor")
	local test_w, test_h = element_get_actual_size(Hud_gsi.elements.level_div_text_h)

	Hud_gsi.status.clip_offset = clip_offset

	--Use default title height if no title specified
	if title_crc == 0 then
		title_h = 36.8
	end

	Hud_gsi.header.width = test_x + test_w
	Hud_gsi.header.height =	title_h
	Hud_gsi.header.icon_bmp_name = icon_bmp_name
	--@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
	--Debug Start
	--@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
	if Hud_gsi.status.debug_mode == true then
		show_bounds(Hud_gsi.elements.title_text_h)
		debug_print("vint", "GSI Header Update:\n")
		debug_print("vint", " Hud_gsi.header.height: " .. Hud_gsi.header.height .. "\n")
		debug_print("vint", " title_crc: " .. var_to_string(title_crc) .. "\n\n")
	end
	--@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

end


function hud_gsi_create_info(index, skin)
	--[[
	index, 		=	Index of Indicator
	skin, 	=	What type of x/y indicator ("default" == default display)
	]]

	--Error Checking
	if Hud_gsi.indicators[index] ~= nil then
		debug_print("vint", "Failed to create INFO indicator with index: " .. index .. "\n")
		return
	end

	--Duplicate groups into the indicators grp and store handles to parts
	local info_grp_h = vint_object_clone(Hud_gsi.elements.info_h, Hud_gsi.elements.indicators_grp_h)
	local label_h = vint_object_find("label_txt", info_grp_h)
	local info_h = vint_object_find("info_txt", info_grp_h)

	--Setup default table for object
	local ind_obj = {
		data = {
			index = index,
			info_value = "XXXX: IS AWESOME",
			label = 0,
			init = false,
		},
		elements = {
			skin = skin,
			grp_h = info_grp_h,
			label_h = label_h,
			info_h = info_h,
			label_padding = 9,
			visible = -1,
			width = -1,
			height = -1,
		}
	}
	Hud_gsi.indicators[index] = ind_obj
end

function hud_gsi_update_info(index, visible, skin, label_crc, info_crc, info_value)
	--[[
	index, 			some index to refer to the timer indicator
	]]
	local ind_obj = Hud_gsi.indicators[index]


	--Make sure we have found a correct index, otherwise abort!
	if ind_obj == nil then
		return nil
	end

	--[[
	if info_crc == 0 then
		debug_print("hud_gsi_update_info label_crc:"..tostring(label_crc)..", info_crc:"..tostring(info_crc))
	else
		debug_print("hud_gsi_update_info label_crc:"..tostring(label_crc)..", info_value:"..tostring(info_value))
	end
	--]]

	--Check if everything is formatted during change?

	--Hide the indicator if it is not visible
	if visible ~= ind_obj.elements.visible then
		if visible == true then
			vint_set_property(ind_obj.elements.grp_h, "visible", true)
			ind_obj.elements.visible = visible
		else
			vint_set_property(ind_obj.elements.grp_h, "visible", false)
			ind_obj.elements.visible = visible
		end

		--If the hud is already formatted, queue format process
		if Hud_gsi.status.formatted == true then
			hud_gsi_queue_format()
		end
	end

	--Set label with crc
	if label_crc == 0 or label_crc == nil then
		--No crc or Invalid crc
		vint_set_property(ind_obj.elements.label_h, "text_tag", "")
	else
		vint_set_property(ind_obj.elements.label_h, "text_tag_crc", label_crc)
	end

	--Store off local vars from the indicator object
	local info_h = ind_obj.elements.info_h
	local label_h = ind_obj.elements.label_h

	--Set Info Part
	if info_crc == 0 and info_value == nil then
		--no string
		vint_set_property(info_h, "text_tag", "")
	elseif info_crc == 0 then
		--Use string

		--Skin processing
		if skin == "Cash" then
			--format the cash
			info_value = "$" .. format_cash(tonumber(info_value))
		elseif skin == "TrailBlazing" then
			--Trailblazing specific
			local insertion_text 	= { [0] = info_value }
			info_value = vint_insert_values_in_string("HUD_AMT_SECS_B", insertion_text)
			--Tint the bonus yellow
			vint_set_property(info_h, "tint", Hud_gsi_skins.meter["Default"].tint[1], Hud_gsi_skins.meter["Default"].tint[2], Hud_gsi_skins.meter["Default"].tint[3])
		end

		vint_set_property(info_h, "text_tag", info_value)

		-- Record Drive-by Body Count [nclok1405]
		if (Sui_current_gameplay_title_crc == SUI_GAMEPLAY_CRC_DRIVEBY) and (info_value ~= nil) then
			Sui_driveby_bodycount = info_value
		end
	else
		--use crc
		vint_set_property(info_h,"text_tag_crc", info_crc)
	end

	--If info indicator is using Mayhem skin update its color
	if skin == "Mayhem" then
		if info_value ~= "0" then
			vint_set_property(info_h, "tint", Hud_mayhem_world_cash_status.color_r, Hud_mayhem_world_cash_status.color_g, Hud_mayhem_world_cash_status.color_b)
		else
			--reset color
			vint_set_property(info_h, "tint", Hud_gsi_skins.meter["Mayhem"].tint[1], Hud_gsi_skins.meter["Mayhem"].tint[2], Hud_gsi_skins.meter["Mayhem"].tint[3])
		end
	end


	--Repostion Elements and Calculate width/height
	local label_width, label_height = element_get_actual_size(label_h)
	local info_width, info_height = element_get_actual_size(info_h)

	local label_padding = ind_obj.elements.label_padding
	if label_width == 0 then
		--If the label doesn't exist then we don't need any padding
		label_padding = 0
	end

	--Left Aligned Only?
	local info_x = label_padding + label_width
	local info_y = 0
	vint_set_property(info_h, "anchor", info_x, info_y)

	--Override width for mayhem only.
	if skin == "Mayhem" then
		info_width = 30
	end

	--Queue frame resize if shit is dirty
	if label_crc ~= ind_obj.data.label_crc  then
		hud_gsi_queue_format()
	end

	--Add spacing to width
	local width = info_x + info_width + Hud_gsi.status.text_ind_spacing

	local width_dif = abs(ind_obj.elements.width - width)

	if width_dif > 3 then
		hud_gsi_queue_format()
	end

	ind_obj.elements.width = width
	ind_obj.elements.height = label_height

	---Store Values
	ind_obj.data.label_crc = label_crc
	ind_obj.data.info_value = info_value

	--@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
	--Debug Start
	--@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
	if Hud_gsi.status.debug_mode == true then
		show_bounds(ind_obj.elements.grp_h)
	end
	--@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
end

function hud_gsi_create_timer(index, skin, visible)
	--[[
		index, 		=	Index of Indicator
		skin, 	=	What type of x/y indicator ("positive" == Positive Countdown, "negative" == Negative Countdown)
	]]
	--Error Checking
	if Hud_gsi.indicators[index] ~= nil then
		debug_print("vint", "Failed to create XY indicator with index: " .. index .. "\n")
		return
	end

	if skin ~= "positive" and skin ~= "negative" then
		skin = "negative"

	end

	if visible == false and Hud_gsi.status.config_index == HUD_GSI_CONFIG_MISSION then
		debug_print("vint", "timer is invisible... do not create timer if the timer is not visible and in mission mode\n")
		return
	end

	--Duplicate group into the indicators grp and store handles to parts
	local timer_grp_h = vint_object_clone(Hud_gsi.elements.timer_h, Hud_gsi.elements.indicators_grp_h)
	local timer_h = vint_object_find("timer_txt", timer_grp_h)
	local label_h = vint_object_find("label_txt", timer_grp_h)

	local default_time = "00:00"

	--Get width/height
	vint_set_property(timer_h, "text_tag", default_time)
	local width, height = element_get_actual_size(timer_h)

	--Setup default table for object
	local ind_obj = {
		data = {
			index = index,
			timer_value = 0,
			label_crc = 0,
			init = false,
		},
		elements = {
			grp_h = timer_grp_h,
			label_h = label_h,
			timer_h = timer_h,
			skin = skin,
			label_padding = 9,
			visible = -1,
			width = width,
			height = height,
		}
	}
	Hud_gsi.indicators[index] = ind_obj
end

function hud_gsi_update_timer(index, visible, skin, label_crc, timer_value)
	local ind_obj = Hud_gsi.indicators[index]

	--Make sure we have found a correct index, otherwise abort!
	if ind_obj == nil then
		return nil
	end

	--Hide the indicator if it is not visible
	if visible ~= ind_obj.elements.visible then
		if visible == true then
			vint_set_property(ind_obj.elements.grp_h, "visible", true)
			ind_obj.elements.visible = visible
		else
			vint_set_property(ind_obj.elements.grp_h, "visible", false)
			ind_obj.elements.visible = visible
		end

		--If the hud is already formatted, queue format process
		if Hud_gsi.status.formatted == true then
			hud_gsi_queue_format()
		end
	end

	--Set label with crc
	if label_crc == 0 or label_crc == nil then
		--No crc or Invalid crc
		vint_set_property(ind_obj.elements.label_h, "text_tag", "")
	else
		vint_set_property(ind_obj.elements.label_h, "text_tag_crc", label_crc)
	end

	--Error Check for timer value
	if timer_value == nil then
		timer_value = 0
	end

	--Store local handles to indicator elements
	local timer_h = ind_obj.elements.timer_h
	local label_h = ind_obj.elements.label_h

	---Format the time
	local minutes = floor(timer_value / 60)
	local seconds =  mod(timer_value, 60)
	--Pad the seconds for the timer
	if seconds < 10 then
		seconds = "0" .. seconds
	end

	local time_formatted = minutes .. ":" .. seconds
	-- Make timer red on last 10 seconds
	if timer_value <= 10 then
		time_formatted = "[format][color:red]" .. minutes .. ":" .. seconds .. "[/format]"
	end

	--Output the time to the text field
	vint_set_property(timer_h, "text_tag", time_formatted)

	--Repostion Elements and Calculate width/height
	local label_width, label_height = element_get_actual_size(label_h)
	local timer_width, timer_height = element_get_actual_size(timer_h)

	local label_padding = ind_obj.elements.label_padding
	if label_width == 0 then
		--If the label doesn't exist then we don't need any padding
		label_padding = 0
	end

	local timer_x = label_padding + label_width
	local timer_y = 0

	vint_set_property(timer_h, "anchor", timer_x, timer_y )

	local is_positive_timer = false
	if skin == "positive" then
		is_positive_timer = true
	end


	--Resize Frame if shit is dirty
	if label_crc ~= ind_obj.data.label_crc  then
		hud_gsi_queue_format()
	end

	ind_obj.elements.width = timer_x + timer_width + Hud_gsi.status.text_ind_spacing
	ind_obj.elements.height = timer_height

	--do some extra sound processing
	hud_gsi_update_timer_sound(timer_value, ind_obj.data.timer_value, is_positive_timer)

	ind_obj.data.label_crc = label_crc
	ind_obj.data.timer_value = timer_value

	--@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
	--Debug Start
	--@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
	if Hud_gsi.status.debug_mode == true then
		show_bounds(ind_obj.elements.grp_h)
	end
	--@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
end

function hud_gsi_create_xy(index, skin)
	--[[
		index, 		=	Index of Indicator
		skin, 	=	What type of x/y indicator (nil == nothing special, "cash" == cash display)
	]]

	--Error Checking
	if Hud_gsi.indicators[index] ~= nil then
		debug_print("vint", "Failed to create XY indicator with index: " .. index .. "\n")
		return
	end

	--Duplicate groups into the indicators grp
	local xy_grp_h = vint_object_clone(Hud_gsi.elements.xy_h, Hud_gsi.elements.indicators_grp_h)
	local label_h = vint_object_find("label_txt", xy_grp_h)
	local x_h = vint_object_find("x_txt", xy_grp_h)
	local y_h = vint_object_find("y_txt", xy_grp_h)
	local slash_h = vint_object_find("slash_txt", xy_grp_h)

	--Setup default table for object
	local ind_obj = {
		data = {
			index = index,
			x_value = 200,
			y_value = 200,
			label = 0,
			init = false,
		},
		elements = {
			grp_h = xy_grp_h,
			label_h = label_h,
			x_h = x_h,
			y_h = y_h,
			slash_h = slash_h,
			skin = skin,
			label_padding = 9,
			slash_padding = 2,
			visible = -1,
			width = -1,
			height = -1,
		}
	}
	Hud_gsi.indicators[index] = ind_obj
end

function hud_gsi_update_xy(index, visible, skin, label_crc, x_value, y_value)
	local ind_obj = Hud_gsi.indicators[index]

	--Make sure we have found a correct index, otherwise abort!
	if ind_obj == nil then
		return nil
	end

	--debug_print("hud_gsi_update_xy label_crc:"..tostring(label_crc)..", "..tostring(x_value).."/"..tostring(y_value))

	-- Streaking [nclok1405]
	if (Sui_current_gameplay_title_crc == SUI_GAMEPLAY_CRC_STREAKING) or (Sui_current_gameplay_title_crc == SUI_GAMEPLAY_CRC_FLASHING) then
		if y_value ~= Sui_streaking_current_goal then
			-- Entered a new level
			Sui_streaking_confirmed_count = Sui_streaking_confirmed_count + Sui_streaking_current_goal
			Sui_streaking_current_goal = y_value
		end
		Sui_streaking_current_count = x_value
		debug_print("Streaking confirmed:"..tostring(Sui_streaking_confirmed_count)..", current:"..tostring(Sui_streaking_current_count))
	end

	--Hide the indicator if it is not visible
	if visible ~= ind_obj.elements.visible then
		if visible == true then
			vint_set_property(ind_obj.elements.grp_h, "visible", true)
			ind_obj.elements.visible = visible
		else
			vint_set_property(ind_obj.elements.grp_h, "visible", false)
			ind_obj.elements.visible = visible
		end

		--If the hud is already formatted, queue format process
		if Hud_gsi.status.formatted == true then
			hud_gsi_queue_format()
		end
	end


	--Set label with crc
	if label_crc == 0 or label_crc == nil then
		--No crc or Invalid crc
		vint_set_property(ind_obj.elements.label_h, "text_tag", "")
	else
		vint_set_property(ind_obj.elements.label_h, "text_tag_crc", label_crc)
	end


	--Store off local vars from the indicator object
	local x_h = ind_obj.elements.x_h
	local y_h = ind_obj.elements.y_h
	local slash_h = ind_obj.elements.slash_h
	local label_h = ind_obj.elements.label_h

	--Maybe play sound only if our value is greater than 0
	if x_value > 0 then
		--Play sound if we are in a certain configuration?
		if Hud_gsi.status.config_index == 70 then
			--Trail blazing
			audio_play(Hud_gsi_audio.trail_blazing)
		elseif Hud_gsi.status.config_index >= 51 and Hud_gsi.status.config_index <= 53 then
			--Heli Assault
			audio_play(Hud_gsi_audio.div_complete)
		end
	end

	--Apply any special formatting to the text
	local x_value_text, y_value_text

	if ind_obj.elements.skin == "Cash" or ind_obj.elements.skin == "Cash_Flash_Disabled" then
		x_value_text = "$" .. format_cash(x_value)
		y_value_text = "$" .. format_cash(y_value)
	else
		x_value_text = x_value
		y_value_text = y_value
	end

	--Set Text Fields
	vint_set_property(ind_obj.elements.x_h,"text_tag", x_value_text)
	vint_set_property(ind_obj.elements.y_h,"text_tag", y_value_text)

	--Reposition elements
	local slash_padding = ind_obj.elements.slash_padding
	local label_padding = ind_obj.elements.label_padding

	--Get Sizes first
	local label_x, label_y = vint_get_property(label_h, "anchor")
	local label_width, label_height = element_get_actual_size(label_h)
	local x_width, x_height = element_get_actual_size(x_h)
	local slash_width, slash_height = element_get_actual_size(slash_h)
	local y_width, y_height = element_get_actual_size(y_h)


	local slash_anchor_x
	if x_width > y_width then
		slash_anchor_x = label_x + label_width + label_padding + x_width
	else
		slash_anchor_x = label_x + label_width + label_padding + y_width
	end

	--Set Positions
	local x_anchor_x = slash_anchor_x - slash_padding - x_width
	local y_anchor_x = slash_anchor_x + slash_width + slash_padding

	vint_set_property(x_h, "anchor", x_anchor_x, label_y)
	vint_set_property(slash_h, "anchor", slash_anchor_x, label_y)
	vint_set_property(y_h, "anchor", y_anchor_x, label_y)

	--Play animations
	if x_value ~= Hud_gsi.indicators[index].data.x_value and skin ~= "Cash_Flash_Disabled" then
		--Make the new number bounce in...

		--Clone Number
		local x_clone_h = vint_object_clone(x_h)

		vint_set_property(x_clone_h, "render_mode", "additive_alpha")
		vint_set_property(x_clone_h, "depth", -1000)
		local x_clone_x, x_clone_y = vint_get_property(x_h, "anchor")
		local x_width, x_height = element_get_actual_size(x_h)

		local x_clone_x_offset = x_width * .5
		local x_clone_y_offset = x_height * .5

		x_clone_x = x_clone_x + x_clone_x_offset
		x_clone_y = x_clone_y + x_clone_y_offset

		vint_set_property(x_clone_h, "anchor", x_clone_x, x_clone_y)
		vint_set_property(x_clone_h, "auto_offset", "c")

		--Clone Tween
		local anim_h = vint_object_clone(Hud_gsi.anims.x_y_in_anim)
		local twn1 = vint_object_find("gsi_xy_alpha", anim_h)
		local twn2 = vint_object_find("gsi_xy_scale", anim_h)

		--retarget tweens
		vint_set_property(twn1, "target_handle", x_clone_h)
		vint_set_property(twn2, "target_handle", x_clone_h)

		--store tweens for cleanup and set callback
		hud_gsi_tween_prepare_cleanup(twn1, anim_h)
		hud_gsi_tween_prepare_cleanup(twn1, x_clone_h)
		vint_set_property(twn1, "end_event", "hud_gsi_tween_cleanup")

		--play anim
		lua_play_anim(anim_h, 0)
	end

	--Store values into the data set
	ind_obj.data.label_crc = label_crc

	ind_obj.data.x_value = x_value
	ind_obj.data.y_value = y_value


	--Calculate Width
	local width = y_anchor_x + y_width + Hud_gsi.status.text_ind_spacing

	local width_dif = abs(ind_obj.elements.width - width)

	if width_dif > 3 then
		hud_gsi_queue_format()
	end

	--Element Set
	ind_obj.elements.width = width
	ind_obj.elements.height = x_height

	--@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
	--Debug Start
	--@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
	if Hud_gsi.status.debug_mode == true then
		show_bounds(ind_obj.elements.grp_h)
		show_bounds(ind_obj.elements.x_h)
		show_bounds(ind_obj.elements.y_h)
		show_bounds(ind_obj.elements.slash_h)
	end
	--@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

	-- Record activity score [nclok1405]
	if Hud_gsi.status.config_index == 0 or Hud_gsi.status.config_index == 1 or Hud_gsi.status.config_index == 80 or Hud_gsi.status.config_index == 112 or Hud_gsi.status.config_index == 120 then
		if x_value ~= nil and y_value ~= nil then
			Sui_activity_score = x_value
			Sui_activity_requirement = y_value
		end
	end
end

function hud_gsi_create_meter(index, skin)
	--[[
	index, 		=	Index of Indicator
	skin, 	=	What type of x/y indicator ("default" == default display)
	]]

	--Error Checking
	if Hud_gsi.indicators[index] ~= nil then
		debug_print("vint", "Failed to create meter indicator with index: " .. index .. "\n")
		return
	end

	--Setup skin
	local meter_skin = Hud_gsi_skins.meter[skin]

	if meter_skin == nil then
		--No skin use default
		meter_skin = Hud_gsi_skins.meter["Default"]
	end

	local tint = meter_skin.tint

	--Duplicate groups into the indicators grp and store handles to parts
	local meter_grp_h = vint_object_clone(Hud_gsi.elements.meter_h, Hud_gsi.elements.indicators_grp_h)
	local label_h = vint_object_find("label_txt", meter_grp_h)
	local meter_fill_h = vint_object_find("fill", meter_grp_h)
	local meter_fill_2_h = vint_object_find("fill_2", meter_grp_h)
	local meter_bg_h = vint_object_find("bg", meter_grp_h)

	--Clone the pulsing animation and retarget the tweens
	local meter_pulse_anim_h = vint_object_clone(Hud_gsi.anims.gsi_fill_pulse)
	vint_set_property(meter_pulse_anim_h, "is_paused", true)
	local scale_twn = vint_object_find("fill_2_scale_twn_1", meter_pulse_anim_h)
	vint_set_property(vint_object_find("fill_2_alpha_twn_1", meter_pulse_anim_h), "target_handle", meter_fill_2_h)
	vint_set_property(scale_twn, "target_handle", meter_fill_2_h)
	vint_set_property(scale_twn, "end_event", "hud_gsi_meter_flash_loop")

	--Store to global for animation special properties
	Hud_gsi_meter_flash_data[scale_twn] = {
		fill_h = meter_fill_h,
		fill_2_h = meter_fill_2_h,
		anim_h = meter_pulse_anim_h,
		BAR_WIDTH_MAX = 172
	}

	--Set width of meter
	local meter_filled = vint_get_property(meter_bg_h, "source_se")
	local meter_empty = 0

	--Tint Meter
	vint_set_property(meter_fill_h, "tint", tint[1], tint[2], tint[3])
	vint_set_property(meter_fill_2_h, "tint", tint[1], tint[2], tint[3])

	--Setup default table for object
	local ind_obj = {
		data = {
			index = index,
			meter_pct = 1,
			meter_filled = meter_filled,
			meter_empty = meter_empty,
			tint = tint,
			is_flashing = false,
			label = 0,
			init = false,
		},
		elements = {
			skin = skin,
			grp_h = meter_grp_h,
			label_h = label_h,
			meter_fill_h = meter_fill_h,
			meter_fill_2_h = meter_fill_2_h,
			meter_pulse_anim_h = meter_pulse_anim_h,
			meter_bg_h = meter_bg_h,
			label_padding = 9,
			visible = -1,
			width = 100,
			height = 10,
		}
	}
	Hud_gsi.indicators[index] = ind_obj
end

function hud_gsi_update_meter(index, visible, skin, label_crc, meter_pct, is_flashing)
	--[[
	index, 			some index to refer to the timer indicator
	info_string, 	string representing the the string to use in the indicator
	]]
	local ind_obj = Hud_gsi.indicators[index]

	--Make sure we have found a correct index, otherwise abort!
	if ind_obj == nil then
		return nil
	end

	--Hide the indicator if it is not visible
	if visible ~= ind_obj.elements.visible then
		if visible == true then
			vint_set_property(ind_obj.elements.grp_h, "visible", true)
			ind_obj.elements.visible = visible
		else
			vint_set_property(ind_obj.elements.grp_h, "visible", false)
			ind_obj.elements.visible = visible
		end

		--If the hud is already formatted, queue format process
		if Hud_gsi.status.formatted == true then
			hud_gsi_queue_format()
		end
	end

	--Set label with crc
	if label_crc == 0 or label_crc == nil then
		--No crc or Invalid crc
		vint_set_property(ind_obj.elements.label_h, "text_tag", "")
	else
		vint_set_property(ind_obj.elements.label_h, "text_tag_crc", label_crc)
	end

	--If meter is using mayhem skin update its color
	--Tint Meter
	if skin == "Mayhem" then
		vint_set_property(ind_obj.elements.meter_fill_h, "tint", Hud_mayhem_world_cash_status.color_r, Hud_mayhem_world_cash_status.color_g, Hud_mayhem_world_cash_status.color_b)
		vint_set_property(ind_obj.elements.meter_fill_2_h, "tint", Hud_mayhem_world_cash_status.color_r, Hud_mayhem_world_cash_status.color_g, Hud_mayhem_world_cash_status.color_b)
	end

	--Store off local vars from the indicator object
	local label_h = ind_obj.elements.label_h
	local info_h = ind_obj.elements.info_h
	local meter_fill_h = ind_obj.elements.meter_fill_h
	local meter_fill_2_h = ind_obj.elements.meter_fill_2_h
	local meter_bg_h = ind_obj.elements.meter_bg_h

	--Calculate meter width and set it
	local fill_width, fill_height = vint_get_property(ind_obj.elements.meter_fill_h, "source_se")
	fill_width = ind_obj.data.meter_filled * meter_pct -- overwrite fill width multiplied by percentage
	vint_set_property(ind_obj.elements.meter_fill_h, "source_se", fill_width, fill_height)
	vint_set_property(ind_obj.elements.meter_fill_2_h , "source_se", fill_width, fill_height)

	if skin == "Fight_Club"	then
		if label_crc ~= ind_obj.data.label_crc then
			--If the hud is already formatted, queue format process because we have changed width
			ind_obj.data.init = false
		end
	end

	--Only re-align if this is the first time the element has been updated
	if ind_obj.data.init == false then
		--Repostion Elements and Calculate width/height
		local label_width, label_height = element_get_actual_size(label_h)

		local label_padding = ind_obj.elements.label_padding
		if label_width == 0 then
			--If the label doesn't exist then we don't need any padding
			label_padding = 0
		end

		local meter_width, meter_height = element_get_actual_size(meter_fill_h)
		local meter_x, meter_y = vint_get_property(meter_bg_h, "anchor")
		meter_x = label_padding + label_width

		vint_set_property(meter_fill_h, "anchor", meter_x + 1, meter_y + 3)
		vint_set_property(meter_fill_2_h, "anchor", meter_x + 1, meter_y + 3)
		vint_set_property(meter_bg_h, "anchor", meter_x, meter_y )

		if skin == "Fight_Club"	then
			local width, height = hud_gsi_update_layout()
			hud_gsi_frame_resize(width, height, Hud_gsi.elements.frame_standard)
		end

		ind_obj.elements.width = meter_x + meter_width
		ind_obj.elements.height = label_height

		ind_obj.data.init = true
	end

	if is_flashing == true then
		vint_set_property(ind_obj.elements.meter_pulse_anim_h, "is_paused", false)
		vint_set_property(meter_fill_2_h, "visible", true)
	elseif is_flashing == false then
		vint_set_property(ind_obj.elements.meter_pulse_anim_h, "is_paused", true)
		vint_set_property(meter_fill_2_h, "visible", false)
	end

	--Store Values
	ind_obj.data.label_crc = label_crc
	ind_obj.data.meter_pct = meter_pct
	ind_obj.data.is_flashing = is_flashing

	--@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
	--Debug Start
	--@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
	if Hud_gsi.status.debug_mode == true then
		show_bounds(ind_obj.elements.grp_h)
	end
	--@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
end

function hud_gsi_meter_flash_loop(tween_h)
	local flash_data = Hud_gsi_meter_flash_data[tween_h]

	if flash_data == nil then
		vint_set_property(tween_h, "end_event", nil)
		return
	end
	lua_play_anim(flash_data.anim_h )
end


function hud_gsi_update_meter_alignment(meter_1_obj, meter_2_obj)

	--This function assumes that both meters exist and formats them so they align with each other

	if meter_1_obj == nil or meter_2_obj == nil then
		--No valid objects homie...
		return
	end

	local meter_1_label_width, meter_1_label_height = element_get_actual_size(meter_1_obj.elements.label_h)
	local meter_2_label_width, meter_2_label_height = element_get_actual_size(meter_2_obj.elements.label_h)

	local largest_label_width = 0
	local meter_with_smallest_label_obj = nil

	--compare widths and assign it to the largest label width
	if meter_1_label_width > meter_2_label_width then
		largest_label_width = meter_1_label_width
		meter_with_smallest_label_obj = meter_2_obj
	else
		largest_label_width = meter_2_label_width
		meter_with_smallest_label_obj = meter_1_obj
	end

	--Now we now which object to adjust and what to adjust it too.
	local grp_h = meter_with_smallest_label_obj.elements.grp_h
	local meter_fill_h = meter_with_smallest_label_obj.elements.meter_fill_h
	local meter_bg_h = meter_with_smallest_label_obj.elements.meter_bg_h
	local label_padding = meter_with_smallest_label_obj.elements.label_padding
	local meter_x, meter_y = vint_get_property(meter_bg_h, "anchor")
	local meter_width, meter_height = element_get_actual_size(meter_fill_h)
	meter_x = label_padding + largest_label_width

	vint_set_property(meter_fill_h, "anchor", meter_x + 1, meter_y + 3)
	vint_set_property(meter_bg_h, "anchor", meter_x, meter_y )

	--We Only need to reset the width of the object because the height didn't change
	meter_with_smallest_label_obj.elements.width = meter_x + meter_width

end

Hud_gsi_tween_objects = {}
--Tween object cleanup
function hud_gsi_tween_prepare_cleanup(tween_h, obj_h)
	if Hud_gsi_tween_objects[tween_h] == nil then
		Hud_gsi_tween_objects[tween_h] = {}
	end
	Hud_gsi_tween_objects[tween_h][obj_h] = obj_h
end

function hud_gsi_tween_cleanup(tween_h)
	for index, value in Hud_gsi_tween_objects do
		if index == tween_h then
			--This is the one to clean up so do it
			--Clean Up items
			for ix, vx in value do
				vint_object_destroy(vx)
			end
			Hud_gsi_tween_objects[index] = nil
		end
	end
end

--Does processing to verify that the hud always maintains its proper format.
function hud_gsi_process()
	if Hud_gsi.status.queue_format == true then
		--We can't format anything if we don't have all the indicators
		local indicators_created = 0
		for i, val in Hud_gsi.indicators do
			indicators_created = indicators_created + 1
		end

		--If we have all the indicators created, we can format
		if indicators_created == Hud_gsi.status.indicator_count then
			local width, height = hud_gsi_update_layout()
			hud_gsi_frame_animate(width, height, 0, Hud_gsi.elements.frame_standard)
		end

		--Reset the format
		Hud_gsi.status.queue_format = false
	end
end

function hud_gsi_queue_format()
	Hud_gsi.status.queue_format = true
end

Hud_gsi_persistant = {
	is_active = false,
	loaded_peg = -1,
}

function hud_gsi_persistant_update(di_h)
	--Updates teh persistent gsi
	local status, title, peg_name, image_name, line_1, line_2 = vint_dataitem_get(di_h)

	if Hud_gsi.status.debug_mode == true then
		debug_print("vint", "hud_gsi_persistant_update(di_h)\n")
		debug_print("vint", " status: " .. var_to_string(status) .. "\n")
		debug_print("vint", " title: " .. var_to_string(title) .. "\n")
		debug_print("vint", " peg_name: " .. var_to_string(peg_name) .. "\n")
		debug_print("vint", " image_name: " .. var_to_string(image_name) .. "\n")
		debug_print("vint", " line_1: " .. var_to_string(line_1) .. "\n")
		debug_print("vint", " line_2: " .. var_to_string(line_2) .. "\n\n")
	end
	--[[
	status = 0 off
	status = 1 on
	status = 2 refresh
]]
	--update active state
	if status > 0 then

		--Load peg
		if Hud_gsi_persistant.loaded_peg ~= -1 then
			--unload old peg
			peg_unload(Hud_gsi_persistant.loaded_peg)
		end

		--load new peg
		Hud_gsi_persistant.loaded_peg = peg_name
		peg_load(peg_name)

		--Set image
		vint_set_property(Hud_gsi_persistant.handles.poloroid_bmp, "image", image_name)

		--Set Text
		vint_set_property(Hud_gsi_persistant.handles.poloroid_title_txt, "text_tag", title)
		vint_set_property(Hud_gsi_persistant.handles.poloroid_line_1_txt, "text_tag", line_1)
		vint_set_property(Hud_gsi_persistant.handles.poloroid_line_2_txt, "text_tag", line_2)

		if Hud_gsi.status.is_fading_out == false then
			--Show display
			hud_gsi_persistant_show()
		end

	else
		hud_gsi_persistant_hide()
	end

	Hud_gsi_persistant.status = status
end


function hud_gsi_persistant_show()
	--Pops the GSI into the poloroid mode

	--Hide normal gsi elements
	vint_set_property(Hud_gsi.elements.standard_grp_h, "visible", false)

	--Show persistant elements
	vint_set_property(Hud_gsi_persistant.handles.grp, "visible", true)

	--Resize box
	hud_gsi_persistant_resize()

	--Show box
	vint_set_property(Hud_gsi.elements.box_grp_h, "alpha", 1)
end

function hud_gsi_persistant_resize()

	local width = 0
	local height = 0
	local line_height = 0

	local temp_width, temp_height = element_get_actual_size(Hud_gsi_persistant.handles.poloroid_title_txt)

	--Store header height
	local header_height = temp_height

	--Header width test
	if temp_width > width then
		width = temp_width
	end

	--Line 1 Test
	temp_width, temp_height = element_get_actual_size(Hud_gsi_persistant.handles.poloroid_line_1_txt)
	if temp_width > width then
		width = temp_width
	end

	--Line 2 Test
	temp_width, temp_height = element_get_actual_size(Hud_gsi_persistant.handles.poloroid_line_2_txt)
	if temp_width > width then
		width = temp_width
	end

	local x, y = vint_get_property(Hud_gsi_persistant.handles.poloroid_line_2_txt, "anchor")
	width = width + x - 8

	--Calculate height with some magic numbers (indicator height) + header_height
	height = (2 * Hud_gsi.status.line_height) + header_height - Hud_gsi.status.box_height_offset - 10

	hud_gsi_frame_resize(width, height, Hud_gsi_persistant.handles.frame)
end


function hud_gsi_persistant_hide()
	--Show normal gsi elements
	vint_set_property(Hud_gsi.elements.standard_grp_h, "visible", true)

	--Hide persistant elements
	vint_set_property(Hud_gsi_persistant.handles.grp, "visible", false)
end


----------------------------------------------------------------
--Countdown process
----------------------------------------------------------------

function hud_gsi_update_timer_sound(cur_time, prev_time, is_positive_timer)
--[[	if cur_time ~= prev_time then
		local play_sound = false
		local play_second_sound = false
		if cur_time <= 15 and  cur_time > 10 then
			--2 seconds
			play_sound = true
		elseif cur_time <= 10 and cur_time > 5 then
			--1 second
			play_sound = true
		elseif cur_time <= 5 and cur_time > 0 then
			--0.5 seconds
			play_sound = true
			play_second_sound = true
		elseif cur_time == 0 then
			--Play final sound
			if is_positive_timer then
				audio_play(Hud_gsi_audio.end_pos)
			else
				audio_play(Hud_gsi_audio.end_neg)
			end
		end
		if play_sound == true then
			if is_positive_timer then
				audio_play(Hud_gsi_audio.count_pos)
				if play_second_sound == true then
					hud_gsi_sound_play_delay(Hud_gsi_audio.count_pos, .5)
				end
			else
				audio_play(Hud_gsi_audio.count_neg)
				if play_second_sound == true then
					hud_gsi_sound_play_delay(Hud_gsi_audio.count_neg, .5)
				end
			end
		end
	end

	]]--
end


--------------------------------------------
--sound delay stuff
function hud_gsi_sound_play_delay(sound_id, offset)
	thread_new("hud_gsi_sound_play_thread", sound_id, offset)
end

function hud_gsi_sound_play_thread(sound_id, offset)
	local is_pause_menu_open
	--Check if pause menu is open
	local pause_doc = vint_document_find("pause_menu")
	if pause_doc == 0 then
		delay(offset)
		audio_play(sound_id)
	end
end


--[[
#########################################################################
TEST FUNCTIONS
#########################################################################
]]

--Used to show the bounding box of an object. (NOTE: Does not work for offsets that are not 0,0)
Bounds_util_data = {}
function show_bounds(element_handle)
	local h
	if Bounds_util_data[element_handle] == nil then
		h = vint_object_create("bounds_util", "bitmap", element_handle)
		vint_set_property(h, "image", "ui_blank")
		vint_set_property(h, "tint", rand_float(.3,1),rand_float(.3,1),rand_float(.3,1))
		vint_set_property(h, "alpha", .5)
		vint_set_property(h, "depth", -5000)
		Bounds_util_data[element_handle] = h
	else
		h = Bounds_util_data[element_handle]
	end
	vint_set_property(h, "anchor", 0,0)
	local element_height, element_width = vint_get_property(element_handle,"screen_size")
	vint_set_property(h, "screen_size", element_height, element_width)
end


