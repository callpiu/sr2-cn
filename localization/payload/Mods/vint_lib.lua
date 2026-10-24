-- vint_lib.lua: Global function and variables for Saints Row 2 GUI

-- ********** SuperUI for SR2 Options [nclok1405] **********

-- Controller type. Valid values are "PC", "XBOX360", or "PS3".
-- Please change this to an appropriate value if you are using 360 or PS3 Controller Onscreen Prompts Mod.
SUI_PLATFORM = "PC"

-- Enable Fast Weapon Switch by Q key?
-- Valid values are true (Enable Fast Weapon Switch) or false (Disable Fast Weapon Switch as in vanilla Single Player)
SUI_FAST_WEAPON_SWITCH = true

-- Play a Sound Effect when you switch weapons by Mouse Wheel or 1-8 keys?
-- Valid values are true (Play a sound on Weapon Switch) or false (Silent)
SUI_WEAPON_SWITCH_SOUND = true

-- Automatically load the latest save on launch?
-- Valid values are true (Load the latest save automatically) or false (Show Main Menu on launch).
SUI_AUTO_CONTINUE = false

-- Show HUD?
-- Valid values are 0 (Completely hide HUD), 1 (Hide most of HUD except Diversion Stars), or 2 (Show HUD).
SUI_HUD_ENABLE = 2

-- Enable on-screen messages?
-- Valid values are true (Enable messages) or false (Do not show messages).
SUI_HUD_MESSAGES_ENABLE = true

-- Use modern HUD layout (Health Bar and Weapon Circle on bottom-right)
-- Valid values are true (Health Bar goes Bottom-right) or false (Top-right).
SUI_MODERN_HUD_LAYOUT = true

-- Autohide various HUD elements
-- Valid values are true (autohide) or false (always display everything).
SUI_MODERN_HUD_AUTOHIDE = true

-- Use normal gameplay HUD in Zombie Uprising (Enable minimap and weapon display)
-- Valid values are true (Enable regular gameplay HUD) or false (Unmodded ZU HUD).
SUI_USE_NORMAL_HUD_IN_ZOMBIE_UPRISING = true

-- Enable Tutorials
-- Valid values are 0 (skip tutorials), 1 (enable tutorial popups in missions only), or 2 (enable tutorial popups).
SUI_TUTORIAL = 2

-- Show shadow around the edge of the screen
-- Valid values are true (enable shadow) or false (no shadow).
SUI_VIGNETTE = true

-- Disable ripple wave effect on pause menu (delete interface_effects.xtbl if you set to false)
-- Valid values are true (No Ripple Effects) or false (With Ripple Effects).
SUI_NO_RIPPLE_WAVE_EFFECT_ON_PAUSE = true

-- Animate the cash display when spending (true or false)
SUI_CASH_TINT_DOWN = true

-- Animate the cash display when cash is increased (true or false)
SUI_CASH_TINT_UP = true

-- Show horizontal bars at top and bottom of garage menu
-- true is the default (13 items in one page), set it false to expand the menu height (15 items in one page)
SUI_GARAGE_HORZ_BARS = true

-- Use a ' ' (space) instead of ',' (comma) as a number separator (true or false)
-- NOTE: Stats menu and Stash messages are unaffected due to technical limitations
SUI_USE_SPACE_SEPARATOR = false

-- Subtitle Size
-- Default: 0.7
SUI_SUBTITLE_SIZE = 0.7

-- *************************************************

-- ***** SuperUI Global Variables [nclok1405] *****
SUI_VERSION = 2.9					-- SuperUI version

Sui_sr2_rerelease = false			-- true if SR2 is probably the re-release edition
Sui_game_started_at_least_once = false	-- Single player played flag

Sui_stopwatch_enabled = false		-- Stopwatch Tool Enabled
Sui_stopwatch_timer = 0				-- Stopwatch Tool Timer
Sui_stopwatch_countdown = 0			-- Stopwatch Start Countdown
Sui_stopwatch_countdown_finished = false	-- Stopwatch Start Countdown Finished

Sui_player_dead = false				-- true if the players died and death screen is active

Sui_cash = 0						-- Current cash, updated from hud.lua

Sui_zombie_final_score = 0			-- Zombie Uprising Score
Sui_zombie_final_kills = 0			-- Zombie Uprising Zombie Kill Count
Sui_zombie_high_score = 0			-- Zombie Uprising High Score

Sui_activity_score = 0				-- Activity Score
Sui_activity_requirement = 0		-- Activity Required Score
Sui_last_bonus_derby_played = 0		-- ID of last Bonus Derby played
Sui_fight_club = false				-- true if Fight Club is active

Sui_missions_completed = -1			-- Number of missions completed, -1 means unknown
Sui_time_played = -1				-- Total Time Played in minutes

Sui_fast_weapon_switch = SUI_FAST_WEAPON_SWITCH		-- Fast Weapon Switch with Q key
Sui_weapon_switch_sound = SUI_WEAPON_SWITCH_SOUND	-- Weapon Switch Sound
Sui_hud_enable = SUI_HUD_ENABLE						-- Show HUD
Sui_hud_messages_enable = SUI_HUD_MESSAGES_ENABLE	-- Enable on-screen messages
Sui_hud_modern_layout = SUI_MODERN_HUD_LAYOUT	-- Use modern HUD layout
Sui_hud_autohide = SUI_MODERN_HUD_AUTOHIDE		-- Autohide HUD elements
Sui_normal_hud_in_zombie = SUI_USE_NORMAL_HUD_IN_ZOMBIE_UPRISING	-- Use normal HUD in Zombie Uprising
Sui_tutorial = SUI_TUTORIAL		-- Enable Tutorials
Sui_vignette = SUI_VIGNETTE		-- Enable screen edge shadow

Sui_cheat_shortcut_chat_all = -1	-- Cheat ID for Chat All key
Sui_cheat_shortcut_chat_team = -1	-- Cheat ID for Chat Team key

-- Gameplay Title CRCs
SUI_GAMEPLAY_CRC_FIGHTCLUB = 633025216
SUI_GAMEPLAY_CRC_TAXI = 1063143153
SUI_GAMEPLAY_CRC_AMBULANCE = 2186918582
SUI_GAMEPLAY_CRC_FIRETRUCK = 790536895
SUI_GAMEPLAY_CRC_TOWTRUCK = 3931915293
SUI_GAMEPLAY_CRC_DRIVEBY = 1593498816
SUI_GAMEPLAY_CRC_STREAKING = 3097643501
SUI_GAMEPLAY_CRC_FLASHING = 1894825903

Sui_current_gameplay_title_crc = 0		-- Current gameplay crc
Sui_current_gameplay_level = 0			-- Current level number
Sui_driveby_bodycount = 0				-- Drive-by Body Count
Sui_streaking_current_count = 0			-- Streaking: Currently shown count
Sui_streaking_current_goal = 0			-- Streaking: Goal of current level
Sui_streaking_confirmed_count = 0		-- Streaking: People streaked in all previous levels

Sui_mod_mission_title = ""				-- Active Mod Mission Title

Sui_skip_activity_cancel_fail_screen = false	-- Skip "Activity Canceled" fail screen
Sui_mission_fail_text = ""				-- Mission Failed text

Sui_weapon_store_active = false			-- true if the Weapon Store is active
Sui_weapon_bmp = {}						-- Equipped weapon bitmap
Sui_weapon_dual = {}					-- Dual weapon status
Sui_weapon_infinite = {}				-- Infinite Ammo status

Sui_paused = false						-- true if game is paused
Sui_demo_derby_menu = false				-- true if in Demo Derby menu
Sui_liquor_store_active = false			-- true if liquor store menu is active

Sui_force_message_region = -1			-- Message region force (-1:None)
Sui_custom_hud_active = false			-- Custom HUD system active
Sui_custom_hud_timer_active = false		-- Timer display
Sui_custom_hud_timer_value = 0			-- Timer value (seconds)
Sui_custom_hud_number_active = false	-- Number display
Sui_custom_hud_number_value = 0			-- Number value

SUI_DEBUG_SHOW_VINT_DOC_LIST = false	-- If true, show the list of currently loaded vint_doc
SUI_VINT_DOC_LIST = {
	"activity_level",
	"alpha_skin",
	"building_purchase",
	"cdl01",
	"cellphone",
	"city_load",
	"clothing_store",
	"completion",
	"credits",
	"crib_cust",
	"cte_news6",
	"cte_sniper_rifle",
	"cutscene_test",
	"cutscene_tv",
	"demo_derby",
	"dialog_box",
	"gang_cust",
	"garage",
	"gmb_blackjack",
	"gmb_poker",
	"hud",
	"hud_btnmash",
	"hud_coop_div",
	"hud_demo_derby",
	"hud_msg",
	"hud_multi_prototype",
	"hud_overhead",
	"hud_race_start",
	"hud_touch_combo",
	"hud_zombie",
	"liquor_store",
	"main_menu",
	"menu_base",
	"menu_gambling_poker",
	"menu_multi_color",
	"menu_style_dialog",
	"mission_replay",
	"mm_wireless",
	"mp_completion",
	"mp_hud",
	"mp_hud_lobby",
	"mp_leaderboards",
	"mp_lobby_players",
	"mp_match_load",
	"mp_player_info_popup",
	"mp_scoreboard",
	"mp_server_browser",
	"music_store",
	"pause_map",
	"pause_menu",
	"pcr01",
	"ss_grid",
	"television",
	"tutorial",
	"tutorial_subtitles",
	"vehicle_cust",
	"vignette",
	"weapon_store",
}

-- ***** Global Variables from the Vanilla SR2 *****
GAME_BUILD_DATE = "0000-00-00 20:00:00"

MENU_NUM_SLIDER_ACCEL_REPEAT =	0.08
MENU_NUM_SLIDER_ACCEL_FACTOR =	15
MENU_NUM_SLIDER_ACCEL_LIMIT =		1000

Pcr_open_plastic_surgeon = false

COLOR_DEFAULT_TEXT = { r = 230, g = 230, b = 230 }

-- some docs need to know what menu mode we are doing
-- set this from C before loading menu docs
Menu_mode_current = ""

Main_menu_controller_selected = false
Main_menu_gameboot_complete = false
Menu_swap_in_progress = false

Main_menu_can_has_input = false

 --stored here so we know how to properly restart the clothing store
Clothing_store_name = "DEBUG_CLOTHING_STORE"
Clothing_store_display_name = 0
Clothing_store_original_name = "DEBUG_CLOTHING_STORE"
Clothing_store_original_display_name = 0
Menu_swap_interface_unload_handle = 0
Menu_swap_interface_reload_name = 0
Menu_swap_callback_function = 0
Menu_swap_hud_hidden = false;

INVALID_NUM_FRAMES = -1
Num_frames_from_switch = INVALID_NUM_FRAMES

Pause_menu_save_for_server_drop = false

DIALOG_OPEN_SOUND 		= "SYS_HUD_HELPTEXT"
DIALOG_SERIOUS_SOUND	= "SYS_HUD_CONF_SERIOUS"
Menu_sound_item_nav		= "SYS_MENU_CLICK_UD"		-- Current menu item changes
Menu_sound_value_nav	= "SYS_MENU_CLICK_LR"		-- Value of current item changes
Menu_sound_select		= "SYS_MENU_SELECT"			-- Current item selected
Menu_sound_scroll		= "SYS_MENU_TRIGGER_LR"		-- Horizontal menu changes
Menu_sound_back			= "SYS_MENU_BACK"			-- Current menu changes to previous
Menu_sound_open			= "SYS_MENU_OPEN"			-- Menu system is opened
Menu_sound_close		= "SYS_MENU_CLOSE"			-- Menu system is closed
Menu_sound_warning		= "SYS_MENU_OPEN"			-- Warning dialog opens
Menu_sound_purchase		= "SYS_MENU_PURCHASE"		-- Any item is purchased
Menu_sound_confirm		= "SYS_HUD_CONF_SERIOUS"	-- Confirmation/warning dialog opens
Menu_sound_reward		= "SYS_HUD_CONF_REWARD"		-- Reward notification dialog


function vint_init_general_audio()
	DIALOG_OPEN_SOUND 		= audio_get_audio_id(DIALOG_OPEN_SOUND)
	DIALOG_SERIOUS_SOUND	= audio_get_audio_id(DIALOG_SERIOUS_SOUND)
	Menu_sound_item_nav		= audio_get_audio_id(Menu_sound_item_nav)
	Menu_sound_value_nav	= audio_get_audio_id(Menu_sound_value_nav)
	Menu_sound_select		= audio_get_audio_id(Menu_sound_select)
	Menu_sound_scroll		= audio_get_audio_id(Menu_sound_scroll)
	Menu_sound_back			= audio_get_audio_id(Menu_sound_back)
	Menu_sound_open			= audio_get_audio_id(Menu_sound_open)
	Menu_sound_close		= audio_get_audio_id(Menu_sound_close)
	Menu_sound_warning		= audio_get_audio_id(Menu_sound_warning)
	Menu_sound_purchase		= audio_get_audio_id(Menu_sound_purchase)
	Menu_sound_confirm		= audio_get_audio_id(Menu_sound_confirm)
	Menu_sound_reward		= audio_get_audio_id(Menu_sound_reward)
end

function vint_menu_swap_thread()
	while true do
		if Menu_swap_interface_reload_name ~= 0 then
			if Menu_swap_hud_hidden == false then
				hud_hide(true);
				Menu_swap_hud_hidden = true
			end
			if Num_frames_from_switch ~= INVALID_NUM_FRAMES then
				Num_frames_from_switch = Num_frames_from_switch + 1
			end
			if Num_frames_from_switch > 2 then
				if Menu_swap_interface_reload_name ~= 0 then
					vint_document_load(Menu_swap_interface_reload_name)
					Menu_swap_interface_reload_name = 0
					Num_frames_from_switch = INVALID_NUM_FRAMES
					Menu_swap_in_progress = false
					if Menu_swap_callback_function ~= 0 then
						Menu_swap_callback_function()
						Menu_swap_callback_function = 0
					end
				end
			end
		end
		thread_yield()
	end
end

function vint_menu_swap_invalidate()
	Menu_swap_interface_reload_name = 0
	Num_frames_from_switch = INVALID_NUM_FRAMES
	Clothing_store_name = "DEBUG_CLOTHING_STORE"
	Clothing_store_display_name = 0
	Clothing_store_original_name = "DEBUG_CLOTHING_STORE"
	Clothing_store_original_display_name = 0
	Menu_swap_interface_unload_handle = 0
	Menu_swap_interface_reload_name = 0
	Menu_swap_in_progress = false
	if Sui_hud_enable == 0 then
		hud_hide(true)
	else
		hud_hide(false)
	end
	Menu_swap_hud_hidden = false
end

function vint_menu_swap_unload()
	vint_document_unload(Menu_swap_interface_unload_handle)
	Num_frames_from_switch = 0
end

function argument_unwrapper(arguments, start)
	if start < arguments.n then
		return arguments[start + 1], argument_unwrapper(arguments, start + 1)
	end
end

function vint_dataresponder_request(data_responder_name, callback_function_name, max_records_to_return, ...)
	vint_internal_dataresponder_request(data_responder_name, callback_function_name, max_records_to_return, argument_unwrapper(arg, 0))
	while(vint_dataresponder_finished(data_responder_name) ~= true) do
		thread_yield()
		vint_internal_dataresponder_request(data_responder_name, callback_function_name, max_records_to_return, argument_unwrapper(arg, 0))
	end
end

--[[
#########################################################################
UTILITY FUNCTIONS
#########################################################################
]]

function set_text_tag(text_element_h, text_crc, text_string)
	--Set Label
	if text_crc == 0 and text_string == nil then
		--no string
		vint_set_property(text_element_h,"text_tag", "")
	elseif text_crc == 0 then
		--use string
		vint_set_property(text_element_h, "text_tag", text_string)
	elseif text_crc == nil then
		--Label crc invalid
		vint_set_property(text_element_h,"text_tag", "")
	else
		--use crc
		vint_set_property(text_element_h, "text_tag_crc",text_crc)
	end
end

--Easy Start Anim
function lua_play_anim(anim_h, start_time_offset, doc)
	if start_time_offset == nil then
		start_time_offset = 0
	end

	local start_time = vint_get_time_index(doc) + start_time_offset

	vint_set_property(anim_h, "is_paused", false)
	vint_set_property(anim_h, "start_time", start_time)
end

--Easy Play tween method
function lua_play_tween(tween_handle, target_handle, start_time_offset)
	vint_set_property(tween_handle, "target_handle",	target_handle)
	vint_set_property(tween_handle, "start_time",		vint_get_time_index() + start_time_offset)
	vint_set_property(tween_handle, "state",				"running")
end

function var_to_string(var)
	if type(var) == "table" then
		return "{table}"
	elseif var == nil then
		return "nil"
	elseif var == true then
		return "true"
	elseif var == false then
		return "false"
	else
		return var
	end
end

--Sets actual size of the element. This is independant of the parent scaler values.
function element_set_actual_size(element_h, width, height)
	local current_width, current_height = vint_get_property(element_h, "unscaled_size")
	if current_width == nil or current_height == nil then
		debug_print("vint", "Can't set actual size, element handle: " .. element_h .. " does not exist.\n")
		return
	end
	local scale_x = width/current_width
	local scale_y = height/current_height
	vint_set_property(element_h, "scale", scale_x, scale_y)
end

--Returns actual size of the element, indpendant from the parent scaler values.
function element_get_actual_size(element_h)
	local width, height = vint_get_property(element_h, "unscaled_size")
	local scale_x, scale_y = vint_get_property(element_h, "scale")
	width = width * scale_x
	height = height * scale_y
	return width, height
end

--Useful Mod function
function mod(number, divisor)
	return number - (divisor * floor(number/divisor))
end

-- Support for hud monkey business
Hud_has_focus = true

-- Math stuffs
PI = 3.1415
PI2 = 6.283

--=======================================
--MP Utilities
--=======================================
MP_gameplay_mode_names = {
	"Pre-game lobby",
	"Gangsta Brawl",
	"Team Gangsta Brawl",
	"Braveheart",
	"Multiplayer Creation",
	"Multiplayer Customization",
	"Multiplayer Game Results",
	"Multiplayer Scoreboard",
	"Multiplayer Tutorial",
}

function mp_is_enabled()
	--Get some multiplayer Data
	local gp_mode = get_pending_game_play_mode()
	for i, m in pairs( MP_gameplay_mode_names ) do
		if gp_mode == m then
			--found a match
			return true
		end
	end

	gp_mode = get_game_play_mode()
	for i, m in pairs( MP_gameplay_mode_names ) do
		if gp_mode == m then
			--found a match
			return true
		end
	end
	return false
end



--#######################################
--Audio Delay
--#######################################
function audio_play_delayed(sound_id, offset)
	thread_new("audio_play_delayed_thread", sound_id, offset)
end

function audio_play_delayed_thread(sound_id, offset)
	delay(offset)
	audio_play(sound_id)
end

function format_cash(cash)
	-- format_int_to_string(value) adds ',' every 3 digits and automatically cuts the fraction
	if not SUI_USE_SPACE_SEPARATOR then
		return format_int_to_string(cash)
	end

	-- SR2 doesn't have any string inspector functions so we have to do it the "hard way" :( [nclok1405]
	local digit_count = 1
	local digit_count_for_separator = 1
	local n = 1
	local s = ""

	while true do
		local n1 = n
		n = n * 10
		local m = cash - (n * floor(cash / n)) -- cash % n
		local p = floor(m / n1)
		s = tostring(p) .. s

		if n > cash then
			break
		else
			digit_count = digit_count + 1
			digit_count_for_separator = digit_count_for_separator + 1

			if digit_count_for_separator >= 4 then
				s = " " .. s
				digit_count_for_separator = 1
			end
		end
	end

	return s
end

function format_cash_add_padding(c)
	if c < 10 then
		return "00" .. c
	elseif c < 100 then
		return "0" .. c
	else
		return c
	end
end

function format_clock(time_in_seconds)

	local neg_symbol = ""

	if time_in_seconds < 0 then
		time_in_seconds = abs(time_in_seconds)
		neg_symbol  = "-"
	end

	---Format the time
	local minutes = floor(time_in_seconds / 60)
	local seconds =  mod(time_in_seconds, 60)
	--Pad the seconds for the timer
	if seconds < 10 then
		seconds = "0" .. seconds
	end
	return neg_symbol .. minutes .. ":" .. seconds
end

-- this is now unofficially get_confirm_button!
function get_a_button()
	local button
	if SUI_PLATFORM == "XBOX360" then
		button = "ui_ctrl_360_btn_a"
	elseif SUI_PLATFORM == "PS3" then
		button = "ui_ctrl_ps3_btn_cross"
	elseif SUI_PLATFORM == "PC" then
		button = "ui_ctrl_PC_btn_enter"
	end

	return button
end

function get_x_button()
	local button
	if SUI_PLATFORM == "XBOX360" then
		button = "ui_ctrl_360_btn_x"
	elseif SUI_PLATFORM == "PS3" then
		button = "ui_ctrl_ps3_btn_square"
	elseif SUI_PLATFORM == "PC" then
		button = "ui_ctrl_PC_btn_x"
	end
	return button
end

-- this is now unofficially get_back_button!
function get_b_button()
	local button
	if SUI_PLATFORM == "XBOX360" then
		button = "ui_ctrl_360_btn_b"
	elseif SUI_PLATFORM == "PS3" then
		button = "ui_ctrl_ps3_btn_circle"
	elseif SUI_PLATFORM == "PC" then
		button = "ui_ctrl_PC_key_esc"
	end
	return button
end

function get_y_button()
	local button
	if SUI_PLATFORM == "XBOX360" then
		button = "ui_ctrl_360_btn_y"
	elseif SUI_PLATFORM == "PS3" then
		button = "ui_ctrl_ps3_btn_triangle"
	elseif SUI_PLATFORM == "PC" then
		button = "ui_ctrl_PC_key_e"
	end
	return button
end

function get_right_stick()
	local button
	if SUI_PLATFORM == "XBOX360" then
		button = "ui_ctrl_360_btn_rs"
	elseif SUI_PLATFORM == "PS3" then
		button = "ui_ctrl_ps3_btn_r3"
	elseif SUI_PLATFORM == "PC" then
		button = "ui_ctrl_PC_mouse"
	end
	return button
end

function get_lt_button()
	local button
	if SUI_PLATFORM == "XBOX360" then
		button = "ui_ctrl_360_btn_lt"
	elseif SUI_PLATFORM == "PS3" then
		button = "ui_ctrl_ps3_btn_l1"
	elseif SUI_PLATFORM == "PC" then
		button = "ui_ctrl_PC_key_ctrl"
	end
	return button
end

function get_rt_button()
	local button
	if SUI_PLATFORM == "XBOX360" then
		button = "ui_ctrl_360_btn_rt"
	elseif SUI_PLATFORM == "PS3" then
		button = "ui_ctrl_ps3_btn_r1"
	elseif SUI_PLATFORM == "PC" then
		button = "ui_ctrl_PC_key_shift"
	end
	return button
end

function get_lb_button()
	local button
	if SUI_PLATFORM == "XBOX360" then
		button = "ui_ctrl_360_btn_lb"
	elseif SUI_PLATFORM == "PS3" then
		button = "ui_ctrl_ps3_btn_l2"
	elseif SUI_PLATFORM == "PC" then
		button = "ui_ctrl_PC_key_ctrl"
	end
	return button
end

function get_rb_button()
	local button
	if SUI_PLATFORM == "XBOX360" then
		button = "ui_ctrl_360_btn_rb"
	elseif SUI_PLATFORM == "PS3" then
		button = "ui_ctrl_ps3_btn_r2"
	elseif SUI_PLATFORM == "PC" then
		button = "ui_ctrl_PC_key_shift"
	end
	return button
end

function get_left_right()
	local button
	if SUI_PLATFORM == "XBOX360" then
		button = "ui_ctrl_360_dpad_lr"
	elseif SUI_PLATFORM == "PS3" then
		button = "ui_ctrl_ps3_dapd_lr"
	elseif SUI_PLATFORM == "PC" then
		button = "ui_ctrl_PC_dpad_lr"
	end
	return button
end

function get_up_down()
	local button
	if SUI_PLATFORM == "XBOX360" then
		button = "ui_ctrl_360_dpad_ud"
	elseif SUI_PLATFORM == "PS3" then
		button = "ui_ctrl_ps3_dpad_ud"
	elseif SUI_PLATFORM == "PC" then
		button = "ui_ctrl_360_dpad_ud"
	end
	return button
end

function get_left_trigger()
	local button
	if SUI_PLATFORM == "XBOX360" then
		button = "ui_ctrl_360_btn_lt"
	elseif SUI_PLATFORM == "PS3" then
		button = "ui_ctrl_ps3_btn_l2"
	elseif SUI_PLATFORM == "PC" then
		button = "ui_ctrl_PC_key_ctrl"
	end
	return button
end

function get_right_trigger()
	local button
	if SUI_PLATFORM == "XBOX360" then
		button = "ui_ctrl_360_btn_rt"
	elseif SUI_PLATFORM == "PS3" then
		button = "ui_ctrl_ps3_btn_r2"
	elseif SUI_PLATFORM == "PC" then
		button = "ui_ctrl_PC_key_shift"
	end
	return button
end

function get_control_stick_base()
	local image
	if SUI_PLATFORM == "XBOX360" then
		image = "ui_hud_base_radial_base_xbox"
	elseif SUI_PLATFORM == "PS3" then
		image = "ui_hud_base_radial_base_ps3"
	elseif SUI_PLATFORM == "PC" then
		image = "ui_hud_base_radial_base_xbox"
	end
	return image
end

function get_control_stick_thumb()
	local image
	if SUI_PLATFORM == "XBOX360" then
		image = "ui_hud_base_radial_thumb_xbox"
	elseif SUI_PLATFORM == "PS3" then
		image = "ui_hud_base_radial_thumb_ps3"
	elseif SUI_PLATFORM == "PC" then
		image = "ui_hud_base_radial_thumb_xbox"
	end
	return image
end

function get_control_stick_text()
	local text

	if pause_menu_is_using_southpaw_control_scheme() == true and is_local_player_in_vehicle() == false then
		if SUI_PLATFORM == "XBOX360" then
			text = "RS"
		elseif SUI_PLATFORM == "PS3" then
			text = "R3"
		elseif SUI_PLATFORM == "PC" then
			text = ""
		end
	else
		if SUI_PLATFORM == "XBOX360" then
			text = "LS"
		elseif SUI_PLATFORM == "PS3" then
			text = "L3"
		elseif SUI_PLATFORM == "PC" then
			text = ""
		end
	end
	return text
end

function get_dpad_image()
	local image
	if SUI_PLATFORM == "XBOX360" then
		image = "ui_hud_base_radial_dpad_xbox"
	elseif SUI_PLATFORM == "PS3" then
		image = "ui_hud_base_radial_dpad_ps3"
	elseif SUI_PLATFORM == "PC" then
		image = "ui_hud_base_radial_dpad_xbox"
	end
	return image
end

function get_dpad_lr_image()
	local image
	if SUI_PLATFORM == "XBOX360" then
		image = "ui_ctrl_360_dpad_lr"
	elseif SUI_PLATFORM == "PS3" then
		image = "ui_ctrl_ps3_dpad_lr"
	elseif SUI_PLATFORM == "PC" then
		image = "ui_ctrl_360_dpad_lr"
	end
	return image
end

function get_dpad_ud_image()
	local image
	if SUI_PLATFORM == "XBOX360" then
		image = "ui_ctrl_360_dpad_ud"
	elseif SUI_PLATFORM == "PS3" then
		image = "ui_ctrl_ps3_dpad_ud"
	elseif SUI_PLATFORM == "PC" then
		image = "ui_ctrl_360_dpad_ud"
	end
	return image
end

function table_clone(src)
	local dst = { }

	for k, v in src do
--		if type(v) == "table" then
--			dst[k] = table_clone(v)
--		else
			dst[k] = v
--		end
	end

	return dst
end

-- convert anything to a bool
function var_to_bool(var)
	if var == true then
		return true
	elseif var == false then
		return false
	elseif var == nil then
		return false
	elseif type(var) == "function" then
		return var()
	else
		return false
	end
end

-- ***** SuperUI Global Functions [nclok1405] *****

-- Create an Unicode string
function sui_create_string(s)
	return vint_insert_values_in_string("{0}", {[0] = s})
end

-- Compare two strings which may or may not be in Unicode
function sui_compare_string(a, b)
	-- End early if these two strings are the same and the Unicode versions are not needed
	if (a == b) then
		return true
	end

	-- Create Unicode versions of the strings
	local ua = sui_create_string(a)

	-- Compare
	if (ua == b) then
		return true
	end

	local ub = sui_create_string(b)

	-- Compare
	if (ua == ub) or (a == ub) then
		return true
	end

	-- The two strings are different
	return false
end

-- Hide the specified GUI object
function sui_hide_object(name, parent)
	local obj = vint_object_find(name, parent)
	if (obj ~= nil) and (obj > 0) then
		vint_set_property(obj, "visible", false)
	else
		debug_print("sui_hide_object: Object not found! name:" .. tostring(name) .. ", parent:" .. tostring(parent) .. "\n")
	end
end

-- Show the specified GUI object
function sui_show_object(name, parent)
	local obj = vint_object_find(name, parent)
	if (obj ~= nil) and (obj > 0) then
		vint_set_property(obj, "visible", true)
	else
		debug_print("sui_show_object: Object not found! name:" .. tostring(name) .. ", parent:" .. tostring(parent) .. "\n")
	end
end

-- Returns true if the game is in freeroam
function sui_is_freeroam()
	return (get_game_play_mode() == "Normal")
end

-- Returns true if Zombie Uprising is active
function sui_is_zombie()
	return (vint_document_find("hud_zombie") ~= 0)
end

-- Returns true if Demolition Derby menu is active
function sui_is_demo_derby_menu()
	return Sui_demo_derby_menu
end

-- Returns true if Demolition Derby gameplay is active
function sui_is_demo_derby_gameplay()
	return (vint_document_find("hud_demo_derby") ~= 0)
end

-- Returns true if Demolition Derby gameplay or menu is active
function sui_is_demo_derby()
	return (sui_is_demo_derby_menu() or sui_is_demo_derby_gameplay())
end

-- Returns a human readable float timer value
function sui_get_human_readable_time_float(t)
	local minutes = 0
	local minutes_str = "00"
	local seconds = 0
	local seconds_str = "00"
	local milliseconds_str = "000"

	while (t >= 60) do
		t = t - 60
		minutes = minutes + 1
	end
	if (minutes < 10) then
		minutes_str = "0"..tostring(minutes)
	else
		minutes_str = tostring(minutes)
	end

	while (t >= 1) do
		t = t - 1
		seconds = seconds + 1
	end
	if (seconds < 10) then
		seconds_str = "0"..tostring(seconds)
	else
		seconds_str = tostring(seconds)
	end

	t = t * 1000
	t = floor(t)

	if (t < 10) then
		milliseconds_str = "00"..tostring(t)
	elseif (t < 100) then
		milliseconds_str = "0"..tostring(t)
	else
		milliseconds_str = tostring(t)
	end

	return minutes_str..":"..seconds_str.."."..milliseconds_str
end

-- Get override text for help screen
function sui_get_help_override_text(category, item)
	local insert_values

	if category == 0 and item == 1 then
		-- Crowd Control
		insert_values = {[0] = "HELPSCREEN_TEXT_CROWD_CONTROL", [1] = "TUT_ACT_CROWD_CONTROL_THROWING", [2] = "TUT_ACT_CROWD_CONTROL_LB"}
		return vint_insert_values_in_string("{0}\n{1}\n\n{2}", insert_values)
	elseif category == 0 and item == 4 then
		-- Escort
		insert_values = {[0] = "HELP_TEXT_ESCORT", [1] = "ACT_ESCORT_OBJECTIVE_MSG", [2] = "ACT_ESCORT_ESCORTING_2_MSG"}
		return vint_insert_values_in_string("{0}\n{1}\n{2}.", insert_values)
	elseif category == 0 and item == 5 then
		-- Fight Club
		insert_values = {[0] = "TUT_ACT_INTRO_FIGHT_CLUB", [1] = "TUT_ACT_FIGHT_CLUB_FINISHER", [2] = "TUT_FIGHT_CLUB_NECK_BREAKER", [3] = "TUT_NAG_IMPROV_WEAPONS"}
		return vint_insert_values_in_string("{0}\n{1}\n{2}\n\n{3}", insert_values)
	elseif category == 0 and item == 9 then
		-- Insurance Fraud
		insert_values = {[0] = "HELP_TEXT_FRAUD", [1] = "ACT_FRAUD_GO_GET_HURT", [2] = "TUT_ACT_INS_FRAUD_FIRST_HIT", [3] = "ACT_FRAUD_VISIT_BONUS_AREA", [4] = "TUT_ACT_INS_FRAUD_ANDRENALINE"}
		return vint_insert_values_in_string("{0}\n{1}.\n{2}\n\n{3}.\n{4}", insert_values)
	elseif category == 0 and item == 12 then
		-- Septic Avenger
		insert_values = {[0] = "HELPSCREEN_TEXT_SEPTIC_AVENGER", [1] = "HELP_TEXT_SEPTIC"}
		return vint_insert_values_in_string("{0}\n{1}", insert_values)
	elseif category == 0 and item == 14 then
		-- Trail Blazing
		insert_values = {[0] = "HELPSCREEN_TEXT_HUMAN_TORCH", [1] = "ACT_TORCH_RACE_INSTRUCTIONS2", [2] = "ACT_TORCH_RACE_INSTRUCTIONS1"}
		return vint_insert_values_in_string("{0}\n{1}\n{2}", insert_values)
	elseif category == 0 and item == 15 then
		-- Zombie Uprising
		insert_values = {[0] = "ACT_ZOMBIE_START_WAVES", [1] = "ACT_ZOMBIE_LIMITED_USES", [2] = "ACT_ZOMBIE_CANT_REVIVE", [3] = "ACT_ZOMBIE_TRIGGER_WARNING"}
		return vint_insert_values_in_string("{0}.\n{1}\n{2}\n{3}", insert_values)
	elseif category == 5 and item == 8 then
		-- Streaking
		insert_values = {[0] = "TUT_DIV_INTRO_STREAKING", [1] = "DIVERSION_STREAKING_HELP_TEXT_MESSAGE", [2] = "TUT_STREAKING"}
		return vint_insert_values_in_string("{0}\n{1}\n{2}", insert_values)
	elseif category == 5 and item == 10 then
		-- Ambulance EMT
		insert_values = {[0] = "TUT_DIV_INTRO_AMBULANCE", [1] = "DIVERSION_AMBULANCE_GET_TO_ACCIDENT", [2] = "TUT_AMBULANCE_CPR", [3] = "TUT_AMBULANCE_SHOCK_PADDLES", [4] = "DIVERSION_AMBULANCE_MINIGAME_SHOCK_REVIVE"}
		return vint_insert_values_in_string("{0}\n{1}.\n{2}\n{3}\n{4}", insert_values)
	elseif category == 5 and item == 11 then
		-- Fire Truck
		insert_values = {[0] = "TUT_DIV_INTRO_FIRE_TRUCK", [1] = "DIVERSION_FIRETRUCK_GET_TO_BUILDING"}
		return vint_insert_values_in_string("{0}\n{1}", insert_values)
	elseif category == 5 and item == 13 then
		-- Tow Truck
		insert_values = {[0] = "TUT_DIV_INTRO_TOW_TRUCK", [1] = "DIVERSION_TOW_TRUCK_VEHICLE_IN_PLACE_TEXT", [2] = "DIVERSION_TOWTRUCK_DIVERSION_HURT_VEHICLE_TEXT"}
		return vint_insert_values_in_string("{0}\n{1}.\n{2}.", insert_values)
	elseif category == 10 and item == 0 then
		-- Save/Load
		insert_values = {[0] = "HELP_TEXT_SAVE_LOAD", [1] = "SAVELOAD_SAVE_WARNING"}
		return vint_insert_values_in_string("{0}\n\n{1}", insert_values)
	elseif category == 12 and item == 9 then
		-- Weapon Stores
		insert_values = {[0] = "HELP_TEXT_WEAPONS", [1] = "TUT_STORE_INTRO_WEAPONS"}
		return vint_insert_values_in_string("{0}\n\n{1}", insert_values)
	elseif category == 12 and item == 10 then
		-- Vehicle Dealerships
		insert_values = {[0] = "TUT_STORE_INTRO_VEHICLE_DEALER"}
		return vint_insert_values_in_string("{MAP_IMG_CARDEALER}{0}", insert_values)
	end

	-- No Override
	return ""
end

-- Lua Error Message display for UI context
function mission_help_table(tag, string1, string2, sync)
	dialog_box_message_critical("Lua UI Context Error!", tag)
end
