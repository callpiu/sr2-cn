-- mission_replay.lua: Newspaper Clipboard
-----------------------
--  MISSION REPLAY   --
-----------------------

-- Load the mod mission list [nclok1405]
include("sui_mission_list.lua")

-- Mission IDs of base game [nclok1405]
MISSION_REPLAY_ID_MAIN = {
	"tss01","tss02","tss03","tss04",
	"sh_tss_caverns",
	"bh01","bh02","bh03","bh04","bh05","bh06","bh07","bh08","bh09","bh10","bh11",
	"sh_bh_airport","sh_bh_apartments","sh_bh_chinatown","sh_bh_docks",
	"rn01","rn02","rn03","rn04","rn05","rn06","rn07","rn08","rn09","rn10","rn11",
	"sh_rn_museum_pier","sh_rn_rec_center","sh_rn_sciencemuseum","sh_rn_stripclub",
	"ss01","ss02","ss03","ss04","ss05","ss06","ss07","ss08","ss09","ss10","ss11",
	"sh_ss_crackhouse","sh_ss_fishingdock","sh_ss_student_union","sh_ss_trailerpark",
	"ep01","ep02","ep03","ep04",
	"sh_tss_ugmall",
	"em01"
}

-- Headlines [nclok1405]
MISSION_HEADLINE_TABLE = {
	["tss01"] = "TSS01_HEADLINE",
	["tss02"] = "TSS02_HEADLINE",
	["tss03"] = "TSS03_HEADLINE",
	["tss04"] = "TSS04_HEADLINE",
	["sh_tss_caverns"] = "BUM_STRONGHOLD1_HEADLINE",

	["bh01"] = "BH01_HEADLINE",
	["bh02"] = "BH02_HEADLINE",
	["bh03"] = "BH03_HEADLINE",
	["bh04"] = "BH04_HEADLINE",
	["bh05"] = "BH05_HEADLINE",
	["bh06"] = "BH06_HEADLINE",
	["bh07"] = "BH07_HEADLINE",
	["bh08"] = "BH08_HEADLINE",
	["bh09"] = "BH09_HEADLINE",
	["bh10"] = "BH010_HEADLINE",
	["bh11"] = "BH011_HEADLINE",
	["sh_bh_apartments"] = "BR_STRONGHOLD1_HEADLINE",
	["sh_bh_chinatown"] = "BR_STRONGHOLD2_HEADLINE",
	["sh_bh_docks"] = "BR_STRONGHOLD3_HEADLINE",
	["sh_bh_airport"] = "BR_STRONGHOLD4_HEADLINE",

	["rn01"] = "RN01_HEADLINE",
	["rn02"] = "RN02_HEADLINE",
	["rn03"] = "RN03_HEADLINE",
	["rn04"] = "RN04_HEADLINE",
	["rn05"] = "RN05_HEADLINE",
	["rn06"] = "RN06_HEADLINE",
	["rn07"] = "RN07_HEADLINE",
	["rn08"] = "RN08_HEADLINE",
	["rn09"] = "RN09_HEADLINE",
	["rn10"] = "RN010_HEADLINE",
	["rn11"] = "RN011_HEADLINE",
	["sh_rn_stripclub"] = "RN_STRONGHOLD1_HEADLINE",
	["sh_rn_sciencemuseum"] = "RN_STRONGHOLD2_HEADLINE",
	["sh_rn_museum_pier"] = "RN_STRONGHOLD3_HEADLINE",
	["sh_rn_rec_center"] = "RN_STRONGHOLD4_HEADLINE",

	["ss01"] = "SS01_HEADLINE",
	["ss02"] = "SS02_HEADLINE",
	["ss03"] = "SS03_HEADLINE",
	["ss04"] = "SS04_HEADLINE",
	["ss05"] = "SS05_HEADLINE",
	["ss06"] = "SS06_HEADLINE",
	["ss07"] = "SS07_HEADLINE",
	["ss08"] = "SS08_HEADLINE",
	["ss09"] = "SS09_HEADLINE",
	["ss10"] = "SS010_HEADLINE",
	["ss11"] = "SS011_HEADLINE",
	["sh_ss_trailerpark"] = "SS_STRONGHOLD1_HEADLINE",
	["sh_ss_crackhouse"] = "SS_STRONGHOLD2_HEADLINE",
	["sh_ss_student_union"] = "SS_STRONGHOLD3_HEADLINE",
	["sh_ss_fishingdock"] = "SS_STRONGHOLD4_HEADLINE",

	["ep01"] = "EP01_HEADLINE",
	["ep02"] = "EP02_HEADLINE",
	["ep03"] = "EP03_HEADLINE",
	["ep04"] = "EP04_HEADLINE",
	["sh_tss_ugmall"] = "ULTOR_STRONGHOLD1_HEADLINE",

	["em01"] = "EM01_HEADLINE",
}

MISSION_REPLAY_SWATCH_HEIGHT = 125
MISSION_REPLAY_SWATCH_WIDTH = 190
MISSION_REPLAY_SWATCH_COLS = 4
MISSION_REPLAY_SWATCH_HL_SCALE = 1
MISSION_REPLAY_SWATCH_UHL_SCALE = .8

Mission_replay_building_menu = 0

Mission_replay_loaded_pegs = { }
Mission_replay_clip_peg = 0
Mission_replay_gang_peg = 0

Mission_replay_input_subs = { }

Mission_replay = { handles = {}, }

Mission_replay_cur_swatch = 0

----------------------
--	SYSTEM FUNCTIONS --
----------------------

local DLC_NEWS_PEG = "ui_crib_news_dlc"

local DLC_NEWS_MISSIONS = {
	dlc01 = true, dlc02 = true, dlc03 = true,
	dlc04 = true, dlc05 = true, dlc06 = true,
}

local function mission_replay_has_dlc_news(mission_id)
	return DLC_NEWS_MISSIONS[mission_id] == true
end

-- Returns true if the mission is in the main game [nclok1405]
-- Returns false if the mission is added via a mod
function is_mission_in_main_game(mission_id)
	for i, id in pairs(MISSION_REPLAY_ID_MAIN) do
		if (id == mission_id) then
			return true
		end
	end
	return false
end

-- Called when a mod mission is selected. Show a mission briefing box. [nclok1405]
function mission_replay_on_mod_mission_selected()
	local hl_item = Menu_active.highlighted_item
	if hl_item == nil then
		hl_item = 0
	end
	local mission = MOD_MISSION_LIST[hl_item + 1]

	local title = mission.display_name
	local msg = vint_insert_values_in_string("SUI_MOD_MISSION_INFO", {[0] = mission.internal_name, [1] = mission.author, [2] = mission.description})
	local options = { [0] = "CONTROL_BEGIN_GAME", [1] = "CONTROL_CANCEL" }
	dialog_box_open(title, msg, options, "mission_replay_on_mod_mission_selected_confirm")
	--dialog_box_confirmation(title, msg, "mission_replay_on_mod_mission_selected_confirm")
end

-- When selecting "YES" on the mod mission breifing [nclok1405]
function mission_replay_on_mod_mission_selected_confirm(result, action)
	if action == DIALOG_ACTION_CLOSE and result == 0 then
		local hl_item = Menu_active.highlighted_item
		if hl_item == nil then
			hl_item = 0
		end
		local mission = MOD_MISSION_LIST[hl_item + 1]

		Sui_mod_mission_title = mission.display_name	-- Set mod mission to active

		thread_new("mission_detail_replay_confirm", mission.internal_name)
	end
end

-- Populate Mod Mission List [nclok1405]
function mission_replay_mods_show()
	if sizeof_table(MOD_MISSION_LIST) > 0 then
		Mission_replay_mods_menu.num_items = sizeof_table(MOD_MISSION_LIST)

		for index, mission in pairs(MOD_MISSION_LIST) do
			Mission_replay_mods_menu[index - 1] = {
				label = MOD_MISSION_LIST[index].display_name,
				internal_name = MOD_MISSION_LIST[index].internal_name,
				type = MENU_ITEM_TYPE_SELECTABLE,
				on_select = mission_replay_on_mod_mission_selected
			}
		end
	end
end

--	Initialize the menu
function mission_replay_init()
	-- It is a bad idea to access Newspaper Clipboard during missions [nclok1405]
	if not sui_is_freeroam() then
		local header = "HELP_TEXT_CRIB_NEWS_CLIPPINGS_TITLE"
		local body = "HUD_TRIGGER_DISABLED_OTHER"
		local options = { [0] = "CONTROL_CONTINUE" }
		dialog_box_open(header, body, options, "mission_replay_just_close")
		return
	end

	Sui_mod_mission_title = ""		-- Mod mission is not active right now

	Menu_swap_center = true			--Change menubase to use center swapping style

	Mission_replay.handles.mission_details_slide_in = vint_object_find("mission_details_slide_in")
	Mission_replay.handles.mission_details_slide_out = vint_object_find("mission_details_slide_out")

	--check marks for the completion strings
	Mission_replay.handles.mission_check_sp = vint_object_find("mission_check_sp")
	Mission_replay.handles.mission_check_coop = vint_object_find("mission_check_coop")

	vint_set_property(Mission_replay.handles.mission_details_slide_in, "is_paused", true)
	vint_set_property(Mission_replay.handles.mission_details_slide_out, "is_paused", true)

	--Event Tracking
	event_tracking_interface_enter("Mission Replay")

	menu_store_use_hud(false)
	menu_init()
	Menu_active_anchor_end_x, Menu_active_anchor_end_y = vint_get_property(vint_object_find("menu_center"), "anchor")
	menu_horz_init(Mission_replay_horz)
	interface_effect_begin("pause")
end

-- Shutdown and cleanup the menu
function mission_replay_cleanup()
	for k, v in Mission_replay_loaded_pegs do
		peg_unload(k)
	end
	interface_effect_end()
end

function mission_replay_exit()
	--dialog_box_confirmation("MENU_TITLE_WARNING", "STORE_EXIT_CLIPBOARD", "mission_replay_exit_confirm")
	Sui_mod_mission_title = ""				-- Mod mission is not active
	menu_close(mission_replay_exit_final)	-- Exit without dialog [nclok1405]
end

function mission_replay_just_close()
	menu_close(mission_replay_exit_final)
end

function mission_replay_exit_confirm(result, action)
	if action == DIALOG_ACTION_CLOSE and result == 0 then
		menu_close(mission_replay_exit_final)
	end
end

function mission_replay_exit_final()
	mission_replay_unload_details()
	vint_document_unload(vint_document_find("mission_replay"))
end

------------------------
--	MENU FUNCTIONALITY --
------------------------

-- Scroll bar

Mission_replay_scroll_data = 0
Mission_replay_text_clip_height = 0
Mission_replay_story_text_height = 0
Mission_replay_story_text_pos = 0

function mission_replay_scroll_bar_init(bar_grp)
	vint_set_property(bar_grp, "visible", false)

	local scroll_data = {
		visible =			false,
		bar_grp =			bar_grp,
		bg_n_h =			vint_object_find("menu_scroll_bg_n", bar_grp),
		bg_c_h =			vint_object_find("menu_scroll_bg_c", bar_grp),
		bg_s_h =			vint_object_find("menu_scroll_bg_s", bar_grp),
		thumb_n_h =			vint_object_find("menu_scroll_thumb_n", bar_grp),
		thumb_s_h =			vint_object_find("menu_scroll_thumb_s", bar_grp),
		thumb_blend_h =		vint_object_find("menu_scroll_thumb_blend", bar_grp),
		thumb_pos =			0,
		bar_height =		332,
		thumb_height =		332,
	}

	return scroll_data
end

function mission_replay_scroll_bar_update(scroll_data)
	if scroll_data.visible == false then
		return
	end

	-- update the thumb pos
	local thumb_offset = scroll_data.thumb_pos * scroll_data.bar_height + 10

	if thumb_offset > scroll_data.bar_height - 50 then
		thumb_offset = scroll_data.bar_height - 50
	end

	vint_set_property(scroll_data.thumb_n_h,		"anchor", 3, thumb_offset)
	vint_set_property(scroll_data.thumb_s_h,		"anchor", 3, thumb_offset + scroll_data.thumb_height - 20) --Magic Number represents the offset from the thumb height
	vint_set_property(scroll_data.thumb_blend_h,	"anchor", 3, thumb_offset + scroll_data.thumb_height - 63) --Magic Number represents the offset from the thumb height
end

function mission_replay_scroll_bar_show(scroll_data)
	vint_set_property(scroll_data.bar_grp, "visible", true)
	scroll_data.visible = true
end

function mission_replay_scroll_bar_set_bar_height(scroll_data, new_height)
	--This magic number will allow you to change the base height of the scrollbar
	scroll_data.bar_height = new_height - 54

	vint_set_property(scroll_data.bg_s_h, "anchor", 38, new_height - 10)
	vint_set_property(scroll_data.bg_c_h, "source_se", 10, new_height - 28)

	menu_scroll_bar_update(scroll_data)
end

function mission_replay_scroll_bar_set_thumb_size(scroll_data, height)
	scroll_data.thumb_height = height * scroll_data.bar_height

	if scroll_data.thumb_height < 60 then
		scroll_data.thumb_height = 60
	end

	vint_set_property(scroll_data.thumb_n_h, "source_se", 32, scroll_data.thumb_height - 20)
	menu_scroll_bar_update(scroll_data)
end

function mission_replay_scroll_bar_set_thumb_pos(scroll_data, value)
	if scroll_data.thumb_pos ~= value then
		scroll_data.thumb_pos = value
		menu_scroll_bar_update(scroll_data)
	end
end

function mission_replay_scroll_bar_hide(scroll_data)
	vint_set_property(scroll_data.bar_grp, "visible", false)
	scroll_data.visible = false
end

-- support

function mission_replay_load_peg(peg_name)
	peg_load(peg_name)
	Mission_replay_loaded_pegs[peg_name] = true
end

function mission_replay_unload_peg(peg_name)
	peg_unload(peg_name)
	Mission_replay_loaded_pegs[peg_name] = nil
end

function mission_detail_replay_response(success)
	if success == true then
		vint_set_property(vint_object_find("mission_details"), "visible", false)

		menu_close(mission_replay_exit_final)
	end
end

-- swatches

function mission_replay_mission_select()
	local swatches = Menu_active[0].swatches
	local swatch = swatches[Menu_active[0].cur_idx]

	if swatch.is_unlocked ~= true then
		return
	end

	-- Check if the mission is in the main game [nclok1405]
	local mission_is_main_game = is_mission_in_main_game(swatch.internal_name)
	local has_dlc_news = mission_replay_has_dlc_news(swatch.internal_name)
	local has_news_image = mission_is_main_game or has_dlc_news

	--Hide swatch controls
	vint_set_property(Menu_option_labels.control_parent, "visible", false)

	local detail_frame = vint_object_find("mission_details")

	vint_set_property(vint_object_find("display_line_1", detail_frame), "text_tag", swatch.display_line_1)
	vint_set_property(vint_object_find("display_line_2", detail_frame), "text_tag", swatch.display_line_2)
	vint_set_property(vint_object_find("gang_name", detail_frame), "text_tag", swatch.gang_name)

	Mission_replay_clip_peg = "ui_c_news_"..swatch.internal_name
	mission_replay_load_peg(Mission_replay_clip_peg)

	-- The PC DLC also supplies full-size clippings in per-mission PEGs.
	if has_news_image then
		vint_set_property(vint_object_find("clipping", detail_frame), "image", "ui_ct_news_"..swatch.internal_name)
		vint_set_property(vint_object_find("clipping", detail_frame), "scale", 0.75, 0.75)
	end
	-- Hide the clipping for custom missions without a newspaper.
	vint_set_property(vint_object_find("clipping", detail_frame), "visible", has_news_image)

	Mission_replay_gang_peg = "ui_crib_news_image_"..swatch.gang_code
	mission_replay_load_peg(Mission_replay_gang_peg)

	vint_set_property(vint_object_find("gang_watermark", detail_frame), "image", "ui_crib_news_img_"..swatch.gang_code..".tga")

	local story_text = vint_object_find("story_text", detail_frame)
	local story_text_tag

	if has_dlc_news then
		story_text_tag = swatch.internal_name.."_HEADLINE_TEXT"
	elseif (not mission_is_main_game) then
		-- Mod Missions do not have story texts. [nclok1405]
		story_text_tag = "INFO_DOWN_STORY_NONE"
	elseif swatch.internal_name == "tss02" then
		-- Appointed Defender [nclok1405]
		local headline_tag = swatch.internal_name.."_HEADLINE"	-- Headline Tag
		local headline_text_tag = swatch.internal_name.."_HEADLINE_TEXT"	-- Story Tag
		local jane_news_1_tag = "JANE_TSSP02_NEWSCAST_01"	-- Jane's Newscast Subtitle Tag 1
		local jane_news_2_tag = "JANE_TSSP02_NEWSCAST_02"	-- Jane's Newscast Subtitle Tag 2

		local insert_values = {
			[0] = headline_tag,
			[1] = headline_text_tag,
			[2] = "UNL_MUGGING2",
			[3] = jane_news_1_tag,
			[4] = "UNL_MUGGING2",
			[5] = jane_news_2_tag
		}

		story_text_tag = vint_insert_values_in_string("[format][color:yellow]{0}[/format]\n{1}\n\n[format][color:green]{2} (1):[/format]\n{3}\n\n[format][color:green]{4} (2):[/format]\n{5}", insert_values)
	elseif swatch.internal_name == "em01" then
		-- Revelation [nclok1405]
		local headline_tag = swatch.internal_name.."_HEADLINE"	-- Headline Tag
		local headline_text_tag = swatch.internal_name.."_HEADLINE_TEXT"	-- Story Tag
		local jane_news_tag = "JANE_BONUS_NEWSCAST_01"	-- Jane's Newscast Subtitle Tag

		local insert_values = {
			[0] = headline_tag,
			[1] = headline_text_tag,

			[2] = "UNL_MUGGING2",
			[3] = jane_news_tag,

			-- Wiretap 1
			[4]  = "WIRETAP_TRIGGER_1",
			[5]  = "TROY_TROYWIRE01_01", -- Troy:"What's up Dex?"
			[6]  = "DEX_TROYWIRE01_01",  -- Dex:"I know you're a cop..."
			[7]  = "TROY_TROYWIRE01_02", -- T:"The fuck are you talking about?"
			[8]  = "DEX_TROYWIRE01_02",  -- D:"Come on, man, who you think you're talkin' to..."
			[9]  = "TROY_TROYWIRE01_03", -- T
			[10] = "DEX_TROYWIRE01_03",  -- D
			[11] = "TROY_TROYWIRE01_04", -- T
			[12] = "DEX_TROYWIRE01_04",  -- D:"I'm out Troy..."

			-- Wiretap 2
			[13] = "WIRETAP_TRIGGER_2",
			[14] = "TROY_TROYWIRE02_01",   -- Troy:"How ya doin' Julius?"
			[15] = "TROY_TROYWIRE02_02",
			[16] = "TROY_TROYWIRE02_03",
			[17] = "TROY_TROYWIRE02_04",
			[18] = "TROY_TROYWIRE02_05",
			[19] = "TROY_TROYWIRE02_06",
			[20] = "TROY_TROYWIRE02_07",
			[21] = "TROY_TROYWIRE02_08",
			[22] = "TROY_TROYWIRE02_09",

			-- Wiretap 3
			[23] = "WIRETAP_TRIGGER_3",
			[24] = "TROY_TROYWIRE03_01",
			[25] = "TROY_TROYWIRE03_02",

			-- Dex Phonecall
			[26] = "DEX_CALLPLAYER_BONUS_01",
		}

		local str = "[format][color:yellow]{0}[/format]\n{1}\n\n[format][color:green]{2}:[/format]\n{3}\n\n[format][color:green]{4}:[/format]\nTroy: {5}\nDex: {6}\nTroy: {7}\nDex: {8}\nTroy: {9}\nDex: {10}\nTroy: {11}\nDex: {12}\n\n[format][color:green]{13} (Troy):[/format]\n{14}\n{15}\n{16}\n{17}\n{18}\n{19}\n{20}\n{21}\n{22}\n\n[format][color:green]{23} (Troy):[/format]\n{24}\n{25}\n\n[format][color:green]Dex:[/format]\n{26}"

		story_text_tag = vint_insert_values_in_string(str, insert_values)
	else
		-- Main Missions [nclok1405]
		local headline_tag = MISSION_HEADLINE_TABLE[swatch.internal_name]	-- Headline Tag
		local headline_text_tag = swatch.internal_name.."_HEADLINE_TEXT"	-- Story Tag
		local jane_news_tag = ""	-- Jane's Newscast Subtitle Tag

		-- Only handful of missions have Jane's Newscast.
		if swatch.internal_name == "tss01" then
			jane_news_tag = "JANE_TSSP01_NEWSCAST_01"
		elseif swatch.internal_name == "tss03" then
			jane_news_tag = "JANE_TSSP03_NEWSCAST_01"
		elseif swatch.internal_name == "tss04" then
			jane_news_tag = "JANE_TSSP04_NEWSCAST_01"
		elseif swatch.internal_name == "rn01" then
			jane_news_tag = "JANE_RON01_NEWSCAST_01"
		elseif swatch.internal_name == "rn11" then
			jane_news_tag = "JANE_RON11_NEWSCAST_01"
		elseif swatch.internal_name == "ss05" then
			jane_news_tag = "JANE_SOS05_NEWSCAST_01"
		elseif swatch.internal_name == "bh08" then
			jane_news_tag = "JANE_BR08_NEWSCAST_01"
		elseif swatch.internal_name == "ep02" then
			jane_news_tag = "JANE_TSSE02_NEWSCAST_01"
		elseif swatch.internal_name == "ep03" then
			jane_news_tag = "JANE_TSSE03_NEWSCAST_01"
		elseif swatch.internal_name == "em01" then
			jane_news_tag = "JANE_BONUS_NEWSCAST_01"
		end

		local news
		news = vint_insert_values_in_string("[format][color:yellow]{0}[/format]\n{1}", {[0] = headline_tag, [1] = headline_text_tag})

		if jane_news_tag ~= "" then
			-- Jane has a newscast
			story_text_tag = vint_insert_values_in_string("{0}\n\n[format][color:green]{1}:[/format]\n{2}", {[0] = news, [1] = "UNL_MUGGING2", [2] = jane_news_tag})
		else
			-- No Jane
			story_text_tag = news
		end
	end
	vint_set_property(story_text, "text_tag", story_text_tag)
	vint_set_property(story_text, "offset", 0, 0)

	vint_set_property(vint_object_find("mission_check_coop", detail_frame), "visible", swatch.coop_complete == true)

	local dummy
	dummy, Mission_replay_story_text_height = element_get_actual_size(story_text)
	dummy, Mission_replay_text_clip_height = vint_get_property(vint_object_find("story_clip"), "clip_size")
	Mission_replay_scroll_data = mission_replay_scroll_bar_init(vint_object_find("replay_scroll_bar"))
	Mission_replay_story_text_pos = 0

	if Mission_replay_story_text_height > Mission_replay_text_clip_height then
		mission_replay_scroll_bar_show(Mission_replay_scroll_data)
		mission_replay_scroll_bar_set_bar_height(Mission_replay_scroll_data, Mission_replay_text_clip_height + 15)
		mission_replay_scroll_bar_set_thumb_size(Mission_replay_scroll_data, Mission_replay_text_clip_height / Mission_replay_story_text_height)
	end

	Menu_active.btn_tips = Mission_replay_details_btn_tips
	btn_tips_update()

	local subs_h = vint_subscribe_to_input_event(nil, "select", "mission_replay_detail_input", 500)
	Mission_replay_input_subs[subs_h] = true
	subs_h = vint_subscribe_to_input_event(nil, "back", "mission_replay_detail_input", 500)
	Mission_replay_input_subs[subs_h] = true
	subs_h = vint_subscribe_to_input_event(nil, "nav_up", "mission_replay_detail_input", 500)
	Mission_replay_input_subs[subs_h] = true
	subs_h = vint_subscribe_to_input_event(nil, "nav_down", "mission_replay_detail_input", 500)
	Mission_replay_input_subs[subs_h] = true
	subs_h = vint_subscribe_to_input_event(nil, "pause", "mission_replay_detail_input", 500)
	Mission_replay_input_subs[subs_h] = true

	subs_h = vint_subscribe_to_input_event(nil, "all_unassigned", "mission_replay_detail_input", 500)
	Mission_replay_input_subs[subs_h] = true

	vint_set_property(detail_frame, "visible", true)

	lua_play_anim(Mission_replay.handles.mission_details_slide_in)

	--Hide triggers
	mission_replay_menu_triggers_show(false)
end

function mission_replay_mission_nav()
end

function mission_replay_mission_enter(swatch)
	-- select the thumbnail, make it bright
	vint_set_property(swatch.txt_grp, "visible", true)
	vint_set_property(vint_object_find("clipping", swatch.swatch_h), "tint", 1, 1, 1)
	Mission_replay_cur_swatch = swatch
end

function mission_replay_mission_leave(swatch)
	-- unselect the thumbnail, tint it dark
	vint_set_property(swatch.txt_grp, "visible", false)
	vint_set_property(vint_object_find("clipping", swatch.swatch_h), "tint", 0.5, 0.5, 0.5)
end

function mission_replay_update_swatch(swatch, row, col)
	-- update newspaper icon
	local clipping = vint_object_find("clipping", swatch.swatch_h)

	local mission_is_main_game = is_mission_in_main_game(swatch.internal_name)

	-- Mod Missions do not have an icon, so reuse the generic "locked" icon [nclok1405]
	if swatch.is_unlocked == false then
		vint_set_property(clipping, "image", "ui_crib_news_locked_t")
	elseif mission_replay_has_dlc_news(swatch.internal_name) then
		vint_set_property(clipping, "image", "ui_ct_news_dlc_"..swatch.internal_name.."_t")
	elseif not mission_is_main_game then
		vint_set_property(clipping, "image", "ui_crib_news_locked_t")
	else
		vint_set_property(clipping, "image", "ui_crib_news_"..swatch.internal_name.."_t")
	end

	vint_set_property(clipping, "rotation", rand_float(-0.075, 0.075))
	vint_set_property(clipping, "scale", 1.5, 1.5)

	local visible_text, hidden_text
	if col < 2 then
		visible_text = vint_object_find("right_text", swatch.swatch_h)
		hidden_text = vint_object_find("left_text", swatch.swatch_h)
	else
		hidden_text = vint_object_find("right_text", swatch.swatch_h)
		visible_text = vint_object_find("left_text", swatch.swatch_h)
	end

	vint_set_property(hidden_text, "visible", false)
	vint_set_property(visible_text, "visible", false)

	vint_set_property(vint_object_find("locked", swatch.swatch_h), "visible", swatch.is_unlocked == false)
	vint_set_property(vint_object_find("locked_coop", swatch.swatch_h), "visible", swatch.buddy_complete == false)

	swatch.txt_grp = visible_text

	vint_set_property(vint_object_find("display_line_1", visible_text), "text_tag", swatch.display_line_1)
	vint_set_property(vint_object_find("display_line_2", visible_text), "text_tag", swatch.display_line_2)
	vint_set_property(vint_object_find("gang_name", visible_text), "text_tag", swatch.gang_name)
end

function mission_replay_consume_data(internal_name, display_line_1, display_line_2, gang_name, gang_code, is_unlocked, is_mission, coop_complete, buddy_complete)
	local item = {
		type = MENU_ITEM_TYPE_SELECTABLE,
		internal_name = internal_name,
		display_line_1 = display_line_1,
		display_line_2 = display_line_2,
		is_unlocked = is_unlocked,
		coop_complete = coop_complete,
		buddy_complete = buddy_complete,
		gang_name = gang_name,
		gang_code = gang_code,
		is_mission = is_mission,
		on_select = mission_replay_mission_select,
	}

	local swatches = Mission_replay_building_menu[0].swatches
	swatches[swatches.num_swatches] = item
	swatches.num_swatches = swatches.num_swatches + 1
end

function mission_replay_mission_show(menu_data)
	-- load relavent peg
	mission_replay_load_peg(menu_data.peg)

	-- build swatch list
	local menu_item = menu_data[0]

	menu_item.swatches = { num_swatches = 0 }
	Mission_replay_building_menu = menu_data
	vint_dataresponder_request("mission_replay", "mission_replay_consume_data", 0, "list_missions", menu_data.mission_group)

	-- Keep the base Extras sheet for em01; load the DLC sheet before
	-- menu_grid_show updates the thumbnails.
	if menu_data.mission_group == "extra" then
		for i = 0, menu_item.swatches.num_swatches - 1 do
			if mission_replay_has_dlc_news(menu_item.swatches[i].internal_name) then
				mission_replay_load_peg(DLC_NEWS_PEG)
				break
			end
		end
	end

	local swatch_template = vint_object_find("swatch_clipping", nil)
	menu_grid_show(menu_data, menu_item, swatch_template)

	mission_replay_menu_triggers_show(true)
end

function mission_replay_mission_release(menu)
	if menu.mission_group == "extra" and Mission_replay_loaded_pegs[DLC_NEWS_PEG] then
		mission_replay_unload_peg(DLC_NEWS_PEG)
	end
	mission_replay_unload_peg(menu.peg)
	menu_grid_release(menu[0])
end

function mission_replay_mission_back()
	mission_replay_exit()
end

-- details

function mission_replay_detail_scroll_up()
	if Mission_replay_story_text_pos <= 0 then
		return
	end

	--Mission_replay_story_text_pos = Mission_replay_story_text_pos - Mission_replay_text_clip_height
	-- Due to much bigger story text, we need more fine grained scrolling [nclok1405]
	Mission_replay_story_text_pos = Mission_replay_story_text_pos - (Mission_replay_text_clip_height / 4)

	if Mission_replay_story_text_pos < 0 then
		Mission_replay_story_text_pos = 0
	end

	vint_set_property(vint_object_find("story_text"), "offset", 0, -Mission_replay_story_text_pos)
	mission_replay_scroll_bar_set_thumb_pos(Mission_replay_scroll_data, Mission_replay_story_text_pos / Mission_replay_story_text_height)
end

function mission_replay_detail_scroll_down()
	if Mission_replay_story_text_pos + Mission_replay_text_clip_height >= Mission_replay_story_text_height then
		return
	end

	--Mission_replay_story_text_pos = Mission_replay_story_text_pos + Mission_replay_text_clip_height
	Mission_replay_story_text_pos = Mission_replay_story_text_pos + (Mission_replay_text_clip_height / 4)

	if Mission_replay_story_text_pos + Mission_replay_text_clip_height > Mission_replay_story_text_height then
		Mission_replay_story_text_pos = Mission_replay_story_text_height - Mission_replay_text_clip_height
	end

	vint_set_property(vint_object_find("story_text"), "offset", 0, -Mission_replay_story_text_pos)
	mission_replay_scroll_bar_set_thumb_pos(Mission_replay_scroll_data, Mission_replay_story_text_pos / Mission_replay_story_text_height)
end

function mission_detail_replay_confirm(mission_name)
	-- this could invoke a series of dialogs on local and remote coop player so it's blocking
	vint_dataresponder_request("mission_replay", "mission_detail_replay_response", 0, "mission_start", mission_name)
end

function mission_replay_detail_input(target, event, accelleration)
	if menu_input_is_blocked() == true then
		return
	end

	if event == "nav_up" then
		mission_replay_detail_scroll_up()
	elseif event == "nav_down" then
		mission_replay_detail_scroll_down()
	elseif event == "select" then
		local menu_item = Menu_active[0]
		local swatch = menu_item.swatches[menu_item.cur_idx]

		if swatch.is_unlocked == true then
			Sui_mod_mission_title = ""	-- Starting a vanilla mission
			thread_new("mission_detail_replay_confirm", swatch.internal_name)
		end
	elseif event == "back" then

		for k, v in Mission_replay_input_subs do
			vint_unsubscribe_to_input_event(k)
		end
		Mission_replay_input_subs = { }

		Menu_active.btn_tips = nil
		btn_tips_update()

		--Slide out frame for missions
		lua_play_anim(Mission_replay.handles.mission_details_slide_out)
		local tween_h = vint_object_find("slide_out_ender", Mission_replay.handles.mission_details_slide_out)
		vint_set_property(tween_h, "end_event", "mission_replay_unload_details")

		--Show swatches again
		vint_set_property(Menu_option_labels.control_parent, "visible", true)

		--Block input until peg is unloaded
		menu_input_block(true)

		--Show triggers
		mission_replay_menu_triggers_show(true)
	elseif event == "pause" then
		--Cause special pause
		dialog_open_pause_display()
	end
end


function mission_replay_unload_details()
	vint_set_property(vint_object_find("mission_details"), "visible", false)
	if Mission_replay_clip_peg ~= nil then
		mission_replay_unload_peg(Mission_replay_clip_peg)
	end

	if Mission_replay_gang_peg ~= nil then
		mission_replay_unload_peg(Mission_replay_gang_peg)
	end

	--Pegs are unloaded now unblock input
	menu_input_block(false)
end

function mission_replay_menu_triggers_show(is_visible)
	local h = vint_object_find("upper_nav_trigger_right", nil, MENU_BASE_DOC_HANDLE)
	vint_set_property(h, "visible", is_visible)
	h = vint_object_find("upper_nav_trigger_right_hl", nil, MENU_BASE_DOC_HANDLE)
	vint_set_property(h, "visible", is_visible)
	h = vint_object_find("upper_nav_trigger_left", nil, MENU_BASE_DOC_HANDLE)
	vint_set_property(h, "visible", is_visible)
	h = vint_object_find("upper_nav_trigger_left_hl", nil, MENU_BASE_DOC_HANDLE)
	vint_set_property(h, "visible", is_visible)
end

---------------
-- MENU DATA --
---------------
Mission_replay_details_btn_tips = {
	a_button = { label = "MISSION_COOP_REPLAY_PROMPT",	enabled = true, },
	b_button = { label = "MENU_BACK",						enabled = true, },
	-- this seem to want to put it in the extra tab but there's not room
--	right_stick = { label = "MENU_SCROLL", enabled = true},
}

Mission_replay_prologue_menu = {
--	btn_tips = Pcr01_untop_btn_tips,
	on_show = mission_replay_mission_show,
	on_release = mission_replay_mission_release,
	on_back = mission_replay_mission_back,

	mission_group = "prologue",
	peg = "ui_crib_news_tss",
	hide_header = true,
	hide_frame = true,
	max_height = 500,

	num_items = 1,
	[0] = {
		label = "",
		type = MENU_ITEM_TYPE_GRID,
		on_select = mission_replay_mission_select,
		on_nav = mission_replay_mission_nav,
		on_leave = mission_replay_mission_leave,
		on_enter = mission_replay_mission_enter,
		update_swatch = mission_replay_update_swatch,
		row_height = MISSION_REPLAY_SWATCH_HEIGHT,
		num_cols = MISSION_REPLAY_SWATCH_COLS,
		col_width = MISSION_REPLAY_SWATCH_WIDTH,
		highlight_scale = MISSION_REPLAY_SWATCH_HL_SCALE,
		unhighlight_scale = MISSION_REPLAY_SWATCH_UHL_SCALE,
		hide_arrows = true,
	}
}

Mission_replay_bh_menu = {
--	btn_tips = Pcr01_untop_btn_tips,
	on_show = mission_replay_mission_show,
	on_release = mission_replay_mission_release,
	on_back = mission_replay_mission_back,

	mission_group = "brotherhood",
	peg = "ui_crib_news_bh",
	hide_header = true,
	hide_frame = true,
	max_height = 500,

	num_items = 1,
	[0] = {
		label = "",
		type = MENU_ITEM_TYPE_GRID,
		on_select = mission_replay_mission_select,
		on_nav = mission_replay_mission_nav,
		on_leave = mission_replay_mission_leave,
		on_enter = mission_replay_mission_enter,
		update_swatch = mission_replay_update_swatch,
		row_height = MISSION_REPLAY_SWATCH_HEIGHT,
		num_cols = MISSION_REPLAY_SWATCH_COLS,
		col_width = MISSION_REPLAY_SWATCH_WIDTH,
		highlight_scale = MISSION_REPLAY_SWATCH_HL_SCALE,
		unhighlight_scale = MISSION_REPLAY_SWATCH_UHL_SCALE,
		hide_arrows = true,
	}
}

Mission_replay_rn_menu = {
--	btn_tips = Pcr01_untop_btn_tips,
	on_show = mission_replay_mission_show,
	on_release = mission_replay_mission_release,
	on_back = mission_replay_mission_back,

	mission_group = "ronin",
	peg = "ui_crib_news_rn",
	hide_header = true,
	hide_frame = true,
	max_height = 500,

	num_items = 1,
	[0] = {
		label = "",
		type = MENU_ITEM_TYPE_GRID,
		on_select = mission_replay_mission_select,
		on_nav = mission_replay_mission_nav,
		on_leave = mission_replay_mission_leave,
		on_enter = mission_replay_mission_enter,
		update_swatch = mission_replay_update_swatch,
		row_height = MISSION_REPLAY_SWATCH_HEIGHT,
		num_cols = MISSION_REPLAY_SWATCH_COLS,
		col_width = MISSION_REPLAY_SWATCH_WIDTH,
		highlight_scale = MISSION_REPLAY_SWATCH_HL_SCALE,
		unhighlight_scale = MISSION_REPLAY_SWATCH_UHL_SCALE,
		hide_arrows = true,
	}
}

Mission_replay_ss_menu = {
--	btn_tips = Pcr01_untop_btn_tips,
	on_show = mission_replay_mission_show,
	on_release = mission_replay_mission_release,
	on_back = mission_replay_mission_back,

	mission_group = "sons of samedi",
	peg = "ui_crib_news_ss",
	hide_header = true,
	hide_frame = true,
	max_height = 500,

	num_items = 1,
	[0] = {
		label = "",
		type = MENU_ITEM_TYPE_GRID,
		on_select = mission_replay_mission_select,
		on_nav = mission_replay_mission_nav,
		on_leave = mission_replay_mission_leave,
		on_enter = mission_replay_mission_enter,
		update_swatch = mission_replay_update_swatch,
		row_height = MISSION_REPLAY_SWATCH_HEIGHT,
		num_cols = MISSION_REPLAY_SWATCH_COLS,
		col_width = MISSION_REPLAY_SWATCH_WIDTH,
		highlight_scale = MISSION_REPLAY_SWATCH_HL_SCALE,
		unhighlight_scale = MISSION_REPLAY_SWATCH_UHL_SCALE,
		hide_arrows = true,
	}
}

Mission_replay_epilogue_menu = {
--	btn_tips = Pcr01_untop_btn_tips,
	on_show = mission_replay_mission_show,
	on_release = mission_replay_mission_release,
	on_back = mission_replay_mission_back,

	mission_group = "epilogue",
	peg = "ui_crib_news_ep",
	hide_header = true,
	hide_frame = true,
	max_height = 500,

	num_items = 1,
	[0] = {
		label = "",
		type = MENU_ITEM_TYPE_GRID,
		on_select = mission_replay_mission_select,
		on_nav = mission_replay_mission_nav,
		on_leave = mission_replay_mission_leave,
		on_enter = mission_replay_mission_enter,
		update_swatch = mission_replay_update_swatch,
		row_height = MISSION_REPLAY_SWATCH_HEIGHT,
		num_cols = MISSION_REPLAY_SWATCH_COLS,
		col_width = MISSION_REPLAY_SWATCH_WIDTH,
		highlight_scale = MISSION_REPLAY_SWATCH_HL_SCALE,
		unhighlight_scale = MISSION_REPLAY_SWATCH_UHL_SCALE,
		hide_arrows = true,
	}
}

Mission_replay_extras_menu = {
--	btn_tips = Pcr01_untop_btn_tips,
	on_show = mission_replay_mission_show,
	on_release = mission_replay_mission_release,
	on_back = mission_replay_mission_back,

	mission_group = "extra",
	peg = "ui_crib_news_em",
	hide_header = true,
	hide_frame = true,
	max_height = 500,

	num_items = 1,
	[0] = {
		label = "",
		type = MENU_ITEM_TYPE_GRID,
		on_select = mission_replay_mission_select,
		on_nav = mission_replay_mission_nav,
		on_leave = mission_replay_mission_leave,
		on_enter = mission_replay_mission_enter,
		update_swatch = mission_replay_update_swatch,
		row_height = MISSION_REPLAY_SWATCH_HEIGHT,
		num_cols = MISSION_REPLAY_SWATCH_COLS,
		col_width = MISSION_REPLAY_SWATCH_WIDTH,
		highlight_scale = MISSION_REPLAY_SWATCH_HL_SCALE,
		unhighlight_scale = MISSION_REPLAY_SWATCH_UHL_SCALE,
		hide_arrows = true,
	}
}

Mission_replay_mods_menu = {
	header_label_str = "MODS",
	max_height = 503,	-- Default: 375 [nclok1405]
	num_items = 1,
	on_show = mission_replay_mods_show,
	on_back = mission_replay_mission_back,

	[0] = { label = "STORE_NO_ITEMS_IN_CATEGORY", type = MENU_ITEM_TYPE_SELECTABLE, on_select = nil },
}

Mission_replay_horz = {
	num_items = 7,
	[0] = {label = "HELP_CAT_PROL", sub_menu = Mission_replay_prologue_menu},
	[1] = {label = "GANG_NAME_TB", sub_menu = Mission_replay_bh_menu},
	[2] = {label = "GANG_NAME_TR", sub_menu = Mission_replay_rn_menu},
	[3] = {label = "GANG_NAME_SOS", sub_menu = Mission_replay_ss_menu},
	[4] = {label = "HELP_CAT_EPI", sub_menu = Mission_replay_epilogue_menu},
	[5] = {label = "MAINMENU_EXTRAS", sub_menu = Mission_replay_extras_menu},
	[6] = {label = "MODS", sub_menu = Mission_replay_mods_menu},
}
