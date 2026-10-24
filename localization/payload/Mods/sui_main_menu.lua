-- main_menu.lua: Main Menu

-- Random loading messages while the main menu is loading [nclok1405]
RANDOM_LOADING_MESSAGES = {
	"GAME_LOADING",
	"Loading game...",
	"Reading save...",
	"Preparing city...",
	"Loading resources...",
	"Initializing...",
	"Loading map...",
	"Preparing vehicles...",
	"Loading audio...",
	"Please wait...",
}

help_category_id = 0	-- Help Category ID [nclok1405]

MAIN_MENU_FIND_SERVER_CONTROL = 1100

Main_menu_first_menu = "top"
Main_menu_screen_alpha = .8
-- load all assets needed to display everything up to and including the top main menu
-- this includes: loading, press start, and main menu
-- do nothing else, wait for call to main_menu_load_complete() to let you know when to transition
Main_menu_loading_friends_dialog_handle = 0

Main_menu = {}

Main_menu_syslink_server_data = {}

FIND_SERVER_WIDTH = 375
FIND_SERVER_HEIGHT = 393
FIND_SERVER_MAX_ITEMS = 12
FIND_SERVER_SELECT_BAR_WIDTH = 350
Main_menu_press_start_peg = -1

Multi_ranked = 0
loadFromCoop = false
search_type = 0
sort_by = 0
search_filter = ""

Main_menu_searching_LAN_games = false
Main_menu_is_coop_game = false

function Main_menu_LAN_find_game_PC()
	Main_menu_showing_coop_games = false
	Main_menu_syslink_server_data.num_items = 0
	Main_menu_searching_LAN_games = true
	Main_menu_is_coop_game = false
	Multi_ranked = 0
	vint_document_load("mp_server_browser")
	--start_find_syslink_servers()
end

function Main_menu_Online_find_game_PC()
end

function Main_menu_system_link_find_game_coop_PC()
	Main_menu_showing_coop_games = true
	Main_menu_syslink_server_data.num_items = 0
	Main_menu_searching_LAN_games = true
	Main_menu_is_coop_game = true
	Multi_ranked = 0
	vint_document_load("mp_server_browser")
	--start_find_syslink_servers()
end

function Main_menu_find_coop_online_menu_PC()
end

function Main_menu_online_find_ranked_game_PC()
end

function Main_menu_LAN_find_game_setup_PC()
end

function Main_menu_Online_find_game_setup_PC()
end

function Main_menu_system_link_find_game_coop_setup_PC()
end

function Main_menu_find_coop_online_menu_setup_PC()
end

function Main_menu_online_find_ranked_game_setup_PC()
end


sort_by_values = {}

function multi_change_sort()
end

function on_multi_change_name_filter(menu_label, menu_data)
end

function pc_multi_change_game_type_filter(menu_label, menu_data)
end

function main_menu_multi_apply_filter()
end

function multi_build_search_filter()
end

function main_menu_init()
	debug_print("main_menu_init() called\n")

	local language = get_language()

	peg_load("ui_load_main")
	peg_load("ui_mainmenu")
	peg_load("ui_multiplayer")

	--Main_menu_press_start_peg  = "ui_mm_start_" .. language
	--peg_load(Main_menu_press_start_peg)

	--localize press start btn
	--local press_start_bmp = "ui_mainmenu_pres_start_" .. language
	--vint_set_property(vint_object_find("press_start_bmp"), "image", press_start_bmp)
	--vint_set_property(vint_object_find("press_start_bmp_highlight"), "image", press_start_bmp)
	vint_set_property(vint_object_find("press_start_bmp"), "visible", false)
	vint_set_property(vint_object_find("press_start_bmp_highlight"), "visible", false)

	--Platform filter for various things
	vint_set_property(vint_object_find("press_start_txt"), "visible", false)

	--Initialize state
	Main_menu.handles = {}

	Main_menu.handles.loading_grp = vint_object_find("loading_grp")
	Main_menu.handles.main_menu_grp = vint_object_find("main_menu_grp")
	Main_menu.handles.press_start_grp = vint_object_find("press_start_grp")
	Main_menu.handles.ornate = vint_object_find("ornate")
	Main_menu.handles.menu_screen = vint_object_find("main_menu_screen")

	--Logos
	Main_menu.handles.logo_grp = vint_object_find("logo_sr2")
	Main_menu.handles.logo_bling = vint_object_find("logo_bling", Main_menu.handles.logo_grp)
	Main_menu.handles.logo_sr2 = vint_object_find("logo", Main_menu.handles.logo_grp)
	Main_menu.handles.logo_jp = vint_object_find("logo_jp", Main_menu.handles.logo_grp)
	Main_menu.handles.logo_sr2_ornate_left = vint_object_find("ornate_left", Main_menu.handles.logo_grp)
	Main_menu.handles.logo_sr2_ornate_right = vint_object_find("ornate_right", Main_menu.handles.logo_grp)

	if get_language() == "JP" then
		vint_set_property(Main_menu.handles.logo_jp, "visible", true)
	else
		vint_set_property(Main_menu.handles.logo_jp, "visible", false)
	end

	--Menu Items (Where all the items go into
	Main_menu.handles.menu_items = vint_object_find("menu_items")

	--Menu item
	Main_menu.handles.menu_item = vint_object_find("menu_item")
	vint_set_property(Main_menu.handles.menu_item, "visible", false)

	--Animations
	Main_menu.anims = {}

	--Intro Anims
	Main_menu.anims.intro_loading = vint_object_find("intro_loading_anim")							--Intro Loading
	Main_menu.anims.intro_loading_fadeout = vint_object_find("intro_loading_fadeout_anim")		--Loading Fadeout

	Main_menu.anims.intro_logo = vint_object_find("intro_logo_anim")									--Intro Logo
	Main_menu.anims.intro_ornate = vint_object_find("intro_ornate_anim")								--ornate
	Main_menu.anims.intro_press_start = vint_object_find("intro_press_start_anim")				--Shows press start btn
	Main_menu.anims.intro_menu  = vint_object_find("intro_menu_anim")									--Fades in the menu
	Main_menu.anims.menu_screen_fade  = vint_object_find("menu_screen_fade_anim")					--Darkens main menu using black bitmap

	main_menu_pause_all_anims()

	vint_set_property(Main_menu.anims.intro_press_start, "is_paused", true)

	Main_menu.anims.text_item_deselect = vint_object_find("text_item_deselect")
	Main_menu.anims.text_item_select = vint_object_find("text_item_select")
	vint_set_property(Main_menu.anims.text_item_deselect, "is_paused", true)
	vint_set_property(Main_menu.anims.text_item_select, "is_paused", true)

	--Main menu fade anim
	Main_menu.anims.menu_screen_fade = vint_object_find("menu_screen_fade_anim")
	Main_menu.anims.menu_screen_fade_twn = vint_object_find("main_menu_screen_alpha_twn_1", Main_menu.anims.menu_screen_fade)

	--Initialize bling
	main_menu_bling_init()

	main_menu_visual_set("init")

	--menu_set_custom_control_callbacks(Main_menu_controls)

	Pause_menu_return_to_main = main_menu_restore
	Pause_menu_main_close_ref = main_menu_force_close

	-- prune all objects from pause menu doc to here
	local pause_safe_frame_h = vint_object_find("safe_frame", nil, vint_document_find("pause_menu"))
	local main_safe_frame_h = vint_object_find("safe_frame")

	local c = vint_object_first_child(pause_safe_frame_h)

	if c ~= nil then
		while c ~= nil do
			local n = vint_object_next_sibling(c)
			vint_object_set_parent(c, main_safe_frame_h)
			c = n
		end
	end

	if Main_menu_gameboot_complete == true then
		--Game is already loaded, so we know we are coming from game.(no need to press start)
		vint_set_property(Main_menu.handles.press_start_grp, "visible", false)
		main_menu_load_complete(1)
	else
		main_menu_visual_set("start_load")
	end

	if Main_menu_controller_selected == true then
		main_menu_controller_selected()
	end

	--	Initialize Main Menu button tips

	--Override button tips for main menu
	BTN_TIPS_DEFAULT.b_button.label = "CONTROL_BACK"
	Pause_save_load_btn_tips.b_button.label = "CONTROL_BACK"

	btn_tips_init()

	-- Set button tips to visible but hide the actual tips.
	local menu_tips_h = vint_object_find("menu_tips", nil, MENU_BASE_DOC_HANDLE)
	vint_set_property(menu_tips_h, "visible", true)
	local menu_btn_tips_h = vint_object_find("menu_btn_tips", nil, MENU_BASE_DOC_HANDLE)
	vint_set_property(menu_btn_tips_h, "alpha", 0)

	local tips_clip_h = vint_object_find("tips_clip", nil, MENU_BASE_DOC_HANDLE)
	vint_set_property(tips_clip_h, "visible", false)
end

function main_menu_cleanup()
	main_menu_close_extra_screens(false)
	peg_unload("ui_load_main")
	peg_unload("ui_mainmenu")
	peg_unload("ui_multiplayer")
	--peg_unload(Main_menu_press_start_peg)
end

function main_menu_pause_all_anims()
	vint_set_property(Main_menu.anims.menu_screen_fade, "is_paused", true)
	vint_set_property(Main_menu.anims.intro_loading_fadeout, "is_paused", true)
	vint_set_property(Main_menu.anims.intro_loading, "is_paused", true)
	vint_set_property(Main_menu.anims.intro_logo, "is_paused", true)
	vint_set_property(Main_menu.anims.intro_ornate, "is_paused", true)
	vint_set_property(Main_menu.anims.intro_menu, "is_paused", true)
end

-- if percent < 1 then update the loading progress indicator
-- otherwise transition to "press start..."
function main_menu_load_complete(percent)
	if percent >= 1 then
		main_menu_visual_set("load_to_start")
	else
		--Load random message [nclok1405]
		local msg_max = sizeof_table(RANDOM_LOADING_MESSAGES)
		local msg_index = rand_int(1, msg_max)
		local msg = RANDOM_LOADING_MESSAGES[msg_index]
		--Insert Percent into loading text
		local values = {[0] = msg, [1] = floor(percent*100)}
		local str = vint_insert_values_in_string("{0} {1}%%%", values)

		vint_set_property(vint_object_find("mm_percent_complete"), "text_tag", str)
	end
end

-- called by C when a controller has been selected - you will get no input until after this stage
-- when called, transition to main menu
function main_menu_controller_selected()
	Main_menu_controller_selected = true
	menu_input_block(true)
	main_menu_grab_input()
	menu_init()
	thread_new("main_menu_start")
	menu_input_block(false)
end

-- show main menu
function main_menu_start()
	menu_input_block(true)

	pause_save_get_global_info(false)	-- this can block across frames

	Menu_swap_center = true			--Change menubase to use center swapping style
	local active_frame = vint_object_find("main_menu_reg_pnt")		--Find point for centering menus
	Menu_active_anchor_end_x, Menu_active_anchor_end_y = vint_get_property(active_frame, "anchor")

	--Build Main menu
	main_menu_build(Main_menu_top)

	--Change visual state
	main_menu_visual_set("start_to_main_menu")

	menu_input_block(false)

	-- I'll Uncomment this when SuperUI drops support for 2009 version of SR2 [nclok1405]
	--if not Sui_sr2_rerelease then
		--local options = { [0] = "CONTROL_QUITGAME" }
		--dialog_box_open("SuperUI", "This save is from an older version", options, "main_menu_exit_game_cb_pc", 0, DIALOG_PRIORITY_ACTION)
		--return
	--end

	if Sui_sr2_rerelease then
		-- Warn if SR2 is probably re-release version [nclok1405]
		dialog_box_message_critical("SuperUI", "This save is from a different release")
	elseif SUI_AUTO_CONTINUE and (not Sui_game_started_at_least_once) then
		-- Auto Continue [nclok1405]
		debug_print("Auto Continue is enabled\n")
		main_menu_continue_select()
	end
end

function main_menu_close_extra_screens(staying_in_main_menu)
	stop_mp_tutorial(staying_in_main_menu)
	credits_force_close()
	pause_menu_force_close_brightness_screen()
	vint_document_unload(vint_document_find("mm_wireless"))
	vint_document_unload(vint_document_find("mp_player_info_popup"))
	vint_document_unload(vint_document_find("mp_leaderboards"))
	vint_document_unload(vint_document_find("mp_lobby_players"))
end

function main_menu_force_to_menu(menu_name)

	if Main_menu_controller_selected == false then
		Main_menu_first_menu = menu_name
	else
		main_menu_close_extra_screens(true)
		if menu_name == "top" then
			if Main_menu_controller_selected == true then
				menu_hide_active()
				vint_set_property(vint_object_find("safe_frame"), "visible", true)
				Main_menu_can_has_input = true
				menu_input_block(false)
				main_menu_screen_fade(0)
			end

			main_menu_grab_input()
			dialog_box_force_close_all()
		elseif menu_name == "coop_load" then
			credits_force_close()
			Pause_load_is_coop = true
			vint_set_property(vint_object_find("safe_frame"), "visible", true)
			loadFromCoop = false
			main_menu_load_menu_select()
		end
	end
end

function main_menu_continue_success(s)
	if s == "success" then
		menu_close(main_menu_close_final)
	elseif s == "new_game" then
		main_menu_new_game_select()
	end
end

function main_menu_continue_select_deferred()
	menu_input_block(true)
	main_menu_release_input()
	vint_dataresponder_request("save_load", "main_menu_continue_success", 0, "continue")
	main_menu_grab_input()
	menu_input_block(false)
end

function main_menu_continue_select()
	set_single_player(true)
	set_name_to_use(0)
	mp_switch_modes(-1)
	thread_new("main_menu_continue_select_deferred")
end

function main_menu_new_game_select()
	set_single_player(true)
	set_name_to_use(0)
	mp_switch_modes(-1)
	vint_dataresponder_request("main_menu_responder", "", 0, "new_game")
end

function main_menu_close_final()
	vint_document_unload(vint_document_find("main_menu"))
end

function main_menu_show_mp_live()
	vint_set_property(vint_object_find("safe_frame"), "visible", false)
	vint_dataresponder_request("main_menu_responder", "", 0, "show_temp_mp")
end

function main_menu_show_mp_syslink()
	vint_set_property(vint_object_find("safe_frame"), "visible", false)
	vint_dataresponder_request("main_menu_responder", "", 0, "show_temp_syslink")
end

-- called by C to tell you to close
function main_menu_force_close()
	main_menu_btn_tips_show(false)
	menu_close(main_menu_close_final)
end

function main_menu_customize_menu_select()
end

function main_menu_load_menu_select()
	if loadFromCoop == true then
		set_single_player(false)
	else
		set_single_player(true)
	end

	set_name_to_use(0)

	mp_switch_modes(-1)

	Pause_load_menu.parent_menu = Menu_active
	if Main_menu_can_has_input == true or Menu_active == Pause_load_menu then
		Pause_load_menu.on_back = main_menu_load_back_restore
	else
		Pause_load_menu.on_back = main_menu_load_back_parent
	end
	main_menu_release_input()

	pause_load_menu_select()
end

function main_menu_load_coop_online()
end

function main_menu_load_coop_syslink()
	Pause_load_from_menu = PAUSE_LOAD_FROM_MENU_COOP_SYSLINK
	loadFromCoop = true
	main_menu_load_menu_select()
end

-- called by system to activate attract mode
function main_menu_attract_mode(active)
	--Hides/shows main menu based on active flag
	vint_set_property(vint_object_find("safe_frame"), "visible", active == false)

	--Button Tips
	local menu_tips_h = vint_object_find("menu_tips", nil, MENU_BASE_DOC_HANDLE)
	vint_set_property(menu_tips_h, "visible", active == false)
	menu_input_block(active)
end

function main_menu_tutorial_mode(active)
	--Hides/shows main menu based on active flag
	vint_set_property(vint_object_find("safe_frame"), "visible", active == false)

	--Button Tips
	local menu_tips_h = vint_object_find("menu_tips", nil, MENU_BASE_DOC_HANDLE)
	vint_set_property(menu_tips_h, "visible", active == false)
end

function main_menu_roll_credits(menu_label, menu_data)
	credits_roll_credits()
end

function Main_menu_online_logout()
end

function main_menu_wireless(menu_label, menu_data)
end

function main_menu_wireless_complete()
end

--[[ Main menu building ]]--
Main_menu_styles = {
	highlight_tint = { r = 0.8980, g = 0.7490, b = 0.054},
	normal_tint = { r = 0.6314, g = 0.6314, b = 0.634},
	highlight_scale = 1,
	normal_scale = .8,
	glow_highlight_alpha = .35,
	glow_normal_alpha = 0,
}

function main_menu_build(menu)
	local menu_grp = vint_object_find("menu_items", Main_menu.handles.main_menu_grp)
	local pos_y = -2

	local text_width, text_height, width, height, x, y
	local menu_item_h, text_h, glow_h
	local glow_left_h, glow_right_h, glow_mid_h

	-- clean the old elements out
	local o = vint_object_first_child(menu_grp)
	local o2
	while o ~= nil do
		o2 = vint_object_next_sibling(o)
		vint_object_destroy(o)
		o = o2
	end

	-- populate
	local item_num = 0

	--Use continue?
	if Pause_save_global_info.continue_avail == true then
		Main_menu_top.current_selection = 0
	else
		Main_menu_top.current_selection = 1
	end

	-- add continue item
	menu[item_num] = Main_menu_master[0]
	item_num = item_num + 1

	--Populate rest of items
	for i = 1, Main_menu_master.num_items - 1 do
		menu[item_num] = Main_menu_master[i]
		item_num = item_num + 1
	end

	menu.num_items = item_num

	--Build Elements
	for i = 0, menu.num_items - 1 do

		--Clone menu items
		menu_item_h = vint_object_clone(Main_menu.handles.menu_item)
		vint_object_set_parent(menu_item_h, Main_menu.handles.menu_items)

		--Find elements within item to manipulate
		text_h = vint_object_find("item_text", menu_item_h)
		glow_h = vint_object_find("item_glow", menu_item_h)

		--Set Text
		vint_set_property(text_h , "text_tag", menu[i].label)

		--Rescale Glow
		glow_left_h = vint_object_find("glow_left", glow_h)
		glow_right_h = vint_object_find("glow_right", glow_h)
		glow_mid_h = vint_object_find("glow_mid", glow_h)

		text_width, text_height = element_get_actual_size(text_h)
		width, height = element_get_actual_size(glow_mid_h)
		text_width = text_width - 20

		element_set_actual_size(glow_mid_h, text_width, height)
		x, y = vint_get_property(glow_mid_h, "anchor")
		vint_set_property(glow_left_h, "anchor", -text_width/2, y)
		vint_set_property(glow_right_h, "anchor", text_width/2, y)

		if i == Main_menu_top.current_selection then
			--Highlight first item
			vint_set_property(Main_menu.anims.text_item_select, "target_handle", menu_item_h)
			vint_set_property(menu_item_h, "depth", -50)
			lua_play_anim(Main_menu.anims.text_item_select, -2)
		else
			vint_set_property(text_h, "tint", Main_menu_styles.normal_tint.r, Main_menu_styles.normal_tint.g, Main_menu_styles.normal_tint.b)
			vint_set_property(menu_item_h, "scale", Main_menu_styles.normal_scale, Main_menu_styles.normal_scale)
			vint_set_property(glow_h, "alpha", Main_menu_styles.glow_normal_alpha)
		end

		vint_set_property(menu_item_h, "anchor", 0, pos_y)

		--Set Item to visible
		vint_set_property(menu_item_h, "visible", true)

		--Reposition
		pos_y = pos_y + 30
		menu[i].item_h = menu_item_h
		menu[i].text_h = text_h
		menu[i].glow_h = glow_h
	end
end

function main_menu_load_back_parent()
	vint_dataresponder_request("save_load", "", 0, "load_cancelled")
	if Menu_active.parent_menu ~= nil and Menu_active ~= Menu_active.parent_menu then
		menu_show(Menu_active.parent_menu, MENU_TRANSITION_SWEEP_RIGHT)
	else
		main_menu_restore()
	end
end

function main_menu_load_back_restore()
	vint_dataresponder_request("save_load", "", 0, "load_cancelled")
	main_menu_restore()
end

function main_menu_restore()
	main_menu_grab_input()

	--Undarken main menu
	main_menu_screen_fade(0)
	menu_hide_active()
end

function main_menu_grab_input()
	Main_menu_can_has_input = true
end

function main_menu_release_input()
	Main_menu_can_has_input = false
end

function main_menu_update_nav_bar(new_sel)
	local cur_item = Main_menu_top[Main_menu_top.current_selection]
	local cur_item_h = cur_item.item_h
	local anim_h = vint_object_clone(Main_menu.anims.text_item_deselect)
	vint_set_property(anim_h , "target_handle", cur_item_h)
	vint_set_property(cur_item_h, "depth", 0)

	--Reset tween states for fade out
	local val_r, val_g, val_b = vint_get_property(cur_item.text_h, "tint")
	local twn_h = vint_object_find("menu_item_select", anim_h)
	vint_set_property(twn_h , "start_value", val_r, val_g, val_b)
	local val = vint_get_property(cur_item.glow_h, "alpha")
	twn_h = vint_object_find("item_glow_alpha_twn_1", anim_h)
	vint_set_property(twn_h , "start_value", val )
	vint_set_property(twn_h , "end_event", "main_menu_item_deselect_cleanup")

	local new_item = Main_menu_top[new_sel]
	local new_item_h = new_item.item_h
	vint_set_property(Main_menu.anims.text_item_select, "target_handle", new_item_h)
	vint_set_property(new_item_h, "depth", -50)

	lua_play_anim(anim_h)
	lua_play_anim(Main_menu.anims.text_item_select)

	Main_menu_top.current_selection = new_sel
end

function main_menu_item_deselect_cleanup(twn_h)
	--Cleansup used animations/tweens
	vint_object_destroy(vint_object_parent(twn_h))
end

function main_menu_nav(target, event)
	if menu_input_is_blocked() == true then
		return
	end

	if event == "nav_up" then
		local cur_selection = Main_menu_top.current_selection - 1

		if cur_selection < 0 then
			cur_selection = Main_menu_top.num_items - 1
		end

		main_menu_update_nav_bar(cur_selection)
		audio_play(Menu_sound_item_nav)

	elseif event == "nav_down" then
		local cur_selection = Main_menu_top.current_selection + 1

		if cur_selection >= Main_menu_top.num_items then
			cur_selection = 0
		end

		main_menu_update_nav_bar(cur_selection)
		audio_play(Menu_sound_item_nav)

	elseif event == "select" then
		local item = Main_menu_top[Main_menu_top.current_selection]
		if item.on_select ~= nil then
			item.on_select()
			audio_play(Menu_sound_select)
		elseif item.sub_menu ~= nil then
			main_menu_release_input()
			main_menu_screen_fade(Main_menu_screen_alpha)
			item.sub_menu.highlighted_item = 0	--Always select first item in list
			menu_show(item.sub_menu, MENU_TRANSITION_SWAP)
			audio_play(Menu_sound_select)
		end
	end
end

function main_menu_visual_set(state)
	if state == "init" then
		--Hide everything
		vint_set_property(Main_menu.handles.loading_grp, "alpha", 0)
		vint_set_property(Main_menu.handles.main_menu_grp, "alpha", 0)
		vint_set_property(Main_menu.handles.press_start_grp, "alpha", 0)
		vint_set_property(Main_menu.handles.logo_bling, "alpha", 0)
		vint_set_property(Main_menu.handles.logo_sr2, "alpha", 0)
		vint_set_property(Main_menu.handles.logo_sr2_ornate_left, "alpha", 0)
		vint_set_property(Main_menu.handles.logo_sr2_ornate_right, "alpha", 0)
		vint_set_property(Main_menu.handles.menu_screen, "alpha", 0)
	elseif state == "start_load" then
		--Fade into loading
		lua_play_anim(Main_menu.anims.intro_loading)
	elseif state == "load_to_start" then
		--Fade out loading
		vint_object_destroy(Main_menu.anims.intro_loading)
		lua_play_anim(Main_menu.anims.intro_loading_fadeout)

		--Fade in other elements
		lua_play_anim(Main_menu.anims.intro_ornate, 0)
		lua_play_anim(Main_menu.anims.intro_logo, .2)
		lua_play_anim(Main_menu.anims.intro_press_start, .6)

		--Start bling
		main_menu_play_bling()
	elseif state == "start_to_main_menu" then
		vint_set_property(Main_menu.handles.loading_grp, "alpha", 0)

		vint_set_property(Main_menu.anims.intro_press_start, "is_paused", true)
		lua_play_anim(Main_menu.anims.intro_menu,.5)
		audio_play(audio_get_audio_id("SYS_MENU_SELECT"))
	end
end

function main_menu_screen_fade(target_alpha)
	--Fades menu to the alpha value
	local cur_alpha = vint_get_property(Main_menu.handles.menu_screen, "alpha")
	vint_set_property(Main_menu.anims.menu_screen_fade_twn, "start_value", cur_alpha)
	vint_set_property(Main_menu.anims.menu_screen_fade_twn, "end_value", target_alpha)
	lua_play_anim(Main_menu.anims.menu_screen_fade, 0)

	--if we are faded in show button tips
	if target_alpha > 0 then
		--Show button tips
		main_menu_btn_tips_show(true)
	else
		--Hide button tips
		main_menu_btn_tips_show(false)
	end
end

--coop
function main_menu_maybe_show_coop_menu()
	set_single_player(false)

	main_menu_release_input()
	--Darken main menu
	main_menu_screen_fade(Main_menu_screen_alpha)

	main_manu_switch_controls_coop()

	mp_switch_modes(-1)

	--menu_show(Main_menu_coop_pc, MENU_TRANSITION_SWAP)
	menu_show(Main_menu_coop_syslink, MENU_TRANSITION_SWAP)	-- Show LAN menu directly [nclok1405]
end

function main_menu_maybe_show_online_pc()
end

function main_menu_show_coop_online_menu()
end

function main_menu_maybe_show_coop_online()
end

function main_menu_maybe_show_coop_quickmatch()
end

function main_menu_start_public_coop()
end

function main_menu_start_friends_coop()
end

function main_menu_start_private_coop()
end

function main_menu_start_syslink_coop()
	set_coop_join_type(0)
	coop_start_new_syslink()
	vint_dataresponder_request("main_menu_responder", "", 0, "new_game")
end

function main_menu_start_coop_quickmatch()

end

--coop friends list
function main_menu_coop_join_friend()
end

function  main_menu_populate_friends(display_name)
end

function  main_menu_build_join_player_request()
end

function  main_menu_load_friends()
end

--multiplayer functions
function main_menu_ethernet_disconnected()
	vint_document_unload(vint_document_find("mp_player_info_popup"))
	vint_document_unload(vint_document_find("mp_leaderboards"))

--	main_menu_grab_input()
	--see if we have a mp menu active
	if Menu_active == nil or Menu_active == 0 then
		return
	end

	--we're only in the Pause_info_sub_menu in the main menu if we're online
	if Menu_active.multi_menu == true or Menu_active == Pause_info_sub_menu then
		--we're in a multiplayer menu, RETREAT!!
		main_menu_restore()
		--pop up a dialogue saying why we kicked them out, make this critical so we don't close it
		if is_mp_tutorial_playing() == false then
			if vint_document_find("mp_server_browser") then --CDPLC close server browser if its opened
				vint_document_unload(vint_document_find("mp_server_browser"))
			end
			if get_disconnected_reason() ~= 6 then
				dialog_box_message_critical("MENU_TITLE_WARNING", "MULTI_LOST_CONNECTION_SYS")
			end
		end
	end
end

function main_menu_internet_disconnected()
	vint_document_unload(vint_document_find("mp_player_info_popup"))
	vint_document_unload(vint_document_find("mp_leaderboards"))

--	main_menu_grab_input()
	--see if we have a mp menu active
	if Menu_active == nil or Menu_active == 0 then
		return
	end

	--we're only in the Pause_info_sub_menu in the main menu if we're online
	if Menu_active.multi_internet_menu == true or Menu_active == Pause_info_sub_menu then
		--kill any low priority dialog boxes
		dialog_box_force_close_all()
		--we're in a multiplayer menu, RETREAT!!
		main_menu_restore()
		--pop up a dialogue saying why we kicked them out, make this critical so we don't close it
		if is_mp_tutorial_playing() == false then
			dialog_box_message("MENU_TITLE_WARNING", "MULTI_LOST_CONNECTION")
		end
	end
end

function main_menu_maybe_show_multiplayer_menu()
	-- Prevent naked [nclok1405]
	if not Sui_game_started_at_least_once then
		dialog_box_message("MENU_TITLE_WARNING", "Nudity is shown in multiplayer")
	end

	--release input
	main_menu_release_input()
	--Darken main menu
	main_menu_screen_fade(Main_menu_screen_alpha)

	menu_show(Main_menu_multiplayer_pc, MENU_TRANSITION_SWAP)
end

function main_menu_show_mp_online_menu()
end

function main_menu_maybe_show_online_menu()
end

function main_menu_build_online_menu()
end

function main_menu_build_online_ranked_menu()
end

function main_menu_build_coop_online_menu()
end

function main_menu_cleanup_online_menu()
end

function main_menu_start_ranked_quickmatch()
end

function main_menu_start_unranked_quickmatch()
end

function main_menu_start_lobby(lobby_type)
	mp_start_lobby(lobby_type)
end

function main_menu_start_public_lobby()
end

function main_menu_start_friends_lobby()
end

function main_menu_start_private_lobby()
end

function main_menu_start_syslink_lobby()
	main_menu_start_lobby(5)
end

function main_menu_show_mp_stats()

end

function main_menu_show_mp_leaderboard()
end

function main_menu_start_player_create()
	main_menu_start_lobby(3)
end

function main_menu_start_player_customize()
	main_menu_start_lobby(4)
end

function main_menu_start_player_wardrobe()
	main_menu_start_lobby(6)
end

function main_menu_start_mp_help()

end

function main_menu_get_gamercard()
end

function main_menu_add_syslink_host(display_name)
end

Main_menu_showing_coop_games = false

function main_menu_syslink_menu_update(di_h, event)
end

function main_menu_build_syslink_menu()
end

function main_menu_build_syslink_menu_coop()
end

function main_menu_cleanup_syslink_menu()
end

function find_server_control_get_width()
	return FIND_SERVER_WIDTH
end

function find_server_control_get_height()
	return FIND_SERVER_HEIGHT
end

function main_menu_join_syslink_server()
end

function main_menu_join_online_server()
end

function main_menu_join_online_ranked_server()
end

function main_menu_join_online_coop_server()
end

function main_menu_start_tutorial_mode()
	start_mp_tutorial()
end

--mp help stuff
function main_menu_populate_help(description_tag)
	local idx = Main_menu_mp_help_info.num_items
	Main_menu_mp_help_info[idx] = { label = description_tag, type = PAUSE_MENU_CONTROL_HELP_TEXT }
	Main_menu_mp_help_info.num_items = 1	--	Should never be more than one
end

function main_menu_build_help_menu_info(menu_data)
	if Menu_active.do_not_rebuild_previous == true and Menu_active.parent_menu == menu_data then
		Menu_active.do_not_rebuild = nil
		return
	end

	local hl_item = Menu_active.highlighted_item
	if hl_item == nil then
		hl_item = 0
	end

	local idx = Menu_active[hl_item].id

	-- Set the header
	menu_data.header_label_str = Menu_active[hl_item].label

	--prep
	menu_data.get_width = pause_menu_control_help_text_get_width
	menu_data.get_height = pause_menu_control_help_text_get_height
	menu_data.do_not_rebuild_previous = true

	--	Prepare to populate
	menu_data.num_items = 0
	menu_data.highlighted_item = 0

	--???
	if Menu_active[hl_item].index ~= nil then
		hl_item = Menu_active[hl_item].index
	end

	--	Populate the menu

	-- Help Override Stuff... [nclok1405]
	--debug_print("help_category_id:"..help_category_id..", hl_item:"..hl_item)
	local override_text = sui_get_help_override_text(help_category_id, hl_item)

	if (override_text ~= "") then
		-- Have override
		main_menu_populate_help(override_text)
	else
		-- Load help normally
		--main_menu_populate_help("help_category_id:"..help_category_id.."\nidx:"..idx.."\nhl_item:"..hl_item)
		vint_dataresponder_request("pause_menu_populate", "main_menu_populate_help", 0, idx, hl_item)
	end

	if menu_data.num_items == 0 then
		menu_data.num_items = 1
		menu_data[0] = { label = "STORE_NO_ITEMS_IN_CATEGORY", type=PAUSE_MENU_CONTROL_OBJECTIVE_TEXT_LINE }
	end
end

function main_menu_populate_help_topics(title_tag)
	local idx = Main_menu_mp_help_topics.num_items
	Main_menu_mp_help_topics[idx] = { label = title_tag, type = MENU_ITEM_TYPE_SUB_MENU, sub_menu = Main_menu_mp_help_info, id = 13 }
	Main_menu_mp_help_topics.num_items = Main_menu_mp_help_topics.num_items + 1
end

function main_menu_build_help_menu_topics(menu_data)
	if Menu_active.do_not_rebuild_previous == true and Menu_active.parent_menu == menu_data then
		Menu_active.do_not_rebuild = nil
		return
	end

	local hl_item = Menu_active.highlighted_item
	if hl_item == nil then
		hl_item = 0
	end

	local idx = Menu_active[hl_item].id

	-- Set the header
	menu_data.header_label_str = Menu_active[hl_item].label

	--prep
	menu_data.do_not_rebuild_previous = true

	--	Prepare to populate
	menu_data.num_items = 0
	menu_data.highlighted_item = 0

	--???
	if Menu_active[hl_item].index ~= nil then
		hl_item = Menu_active[hl_item].index
	end

	--	Populate the menu
	vint_dataresponder_request("pause_menu_populate", "main_menu_populate_help_topics", 0, 12, help_category_id) --12 = help topics, help_category_id = help category

	if menu_data.num_items == 0 then
		menu_data.num_items = 1
		menu_data[0] = { label = "STORE_NO_ITEMS_IN_CATEGORY", type=PAUSE_MENU_CONTROL_OBJECTIVE_TEXT_LINE }
	end
end

Main_menu_friends_tips = {
	a_button 	= 	{ label = "CONTROL_SELECT", 					enabled = btn_tips_default_a, },
	x_button 	= 	{ label = "MULTI_MENU_SHOW_GAMERCARD", 			enabled = btn_tips_default_a, },
	b_button 	= 	{ label = "MENU_BACK", 						enabled = btn_tips_default_a, },
}

function main_manu_switch_controls_syslink(menu_data)
end

function main_manu_switch_controls_online(menu_data)
end

function main_manu_switch_controls_coop(menu_data)
end

function maybe_show_login_window()
end

function main_menu_exit_game_cb_pc(result, action)
	if action ~= DIALOG_ACTION_CLOSE then
		return
	end
	if result == 0 then
		debug_print("Game Shutdown triggered from Main Menu\n")
		pc_invoke_exit_game()
	end
end

function main_menu_exit_game_pc(menu_data)
	local header = "MAINMENU_EXIT"
	local body = "MAINMENU_EXIT_PROMPT" 	-- Do you really want to quit ?
	local options = { [0] = "CONTROL_YES", [1] = "CONTROL_NO" }
	dialog_box_open(header, body, options, "main_menu_exit_game_cb_pc", 0, DIALOG_PRIORITY_ACTION)
end

function dummy_login_pc_func()
end

function on_multi_login_enter_login(menu_label, menu_data)
end

function on_multi_login_enter_pass(menu_label, menu_data)
end
function on_multi_login_enter_repass(menu_label, menu_data)
end

function on_multi_login_enter_player_name(menu_label, menu_data)
end

function on_multi_login_enter_player_syslink_name(menu_label, menu_data)
	menu_open_player_syslink_name_window()
	vint_dataresponder_request( "enter_login_PC_data_responder", "dummy_login_pc_func", 0 )
	if menu_open_enter_name_result() == 1 then
		local entered_text = menu_open_enter_name_result_string(4)
		if entered_text == nil then
			entered_text = ""
		end
		vint_set_property(vint_object_find("value_text", menu_label.control.grp_h), "text_tag", entered_text )
	end
	menu_resize()
end

function on_multi_login_enter_session_pass(menu_label, menu_data)
end

function on_coop_login_enter_session_pass(menu_label, menu_data)
end

function on_multi_login_enter_session_name(menu_label, menu_data)
end

function on_multi_login_try_login()
end

function on_multi_login_create()
end

function after_gamespy_loggin()
end

function main_menu_multiplayer_create_account_build()
end

function main_menu_multiplayer_sign_in_build()
end

function main_menu_multiplayer_syslink_sign_in_build()
	local t1 = menu_open_enter_name_result_string(4)
	if t1 == nil then
		t1 = ""
	end
	Main_menu_system_link[0].info_text_str = t1

	set_name_to_use(0)
end

function main_menu_coop_syslink_sign_in_build()
	local t1 = menu_open_enter_name_result_string(4)
	if t1 == nil then
		t1 = ""
	end
	Main_menu_coop_syslink[0].info_text_str = t1

	set_name_to_use(0)
end

Main_menu_empty_menu = {
	header_label_str = "NOT IMPLEMENTED",
	num_items = 1,
	on_back = main_menu_restore,
	[0] = { label = "DON'T CLICK THIS", type = MENU_ITEM_TYPE_SELECTABLE},
}

Main_menu_quickmatch = {
}

ranked_values = {}
game_type_values = {}
game_mode_values = {}

function multi_player_switch_match_rank_type_pc()
end

function multi_player_switch_match_type_pc()
end

function multi_player_build_ranked_type_pc()
end

function start_online_game_pc()
end

Main_menu_ranked_type_pc = {
}

Main_menu_start_lobby = {
}

Main_menu_cuztomize_mp_player = {
}

Main_menu_system_link_find_game = {
}

Main_menu_online_find_game = {
}

Main_menu_online_find_ranked_game = {
}

Main_menu_system_link = {
	header_label_str = "MULTI_LAN",
	num_items = 3,
	on_map = main_menu_restore,
	multi_menu = true,
	on_show = main_menu_multiplayer_syslink_sign_in_build,

	[0] = { label = "MULTI_NAME", type = MENU_ITEM_TYPE_INFO_BOX, info_text_str = "Unknown", on_select = on_multi_login_enter_player_syslink_name },
	[1] = { label = "MULTI_FIND_GAMES", type = MENU_ITEM_TYPE_SELECTABLE, on_select = Main_menu_LAN_find_game_PC },
	[2] = { label = "MULTI_LOBBY_START_GAME", type = MENU_ITEM_TYPE_SELECTABLE, on_select = main_menu_start_syslink_lobby },
}

Main_menu_online_pc = {
}

Main_menu_mp_help_topics = {
	num_items = 0,
	on_show = main_menu_build_help_menu_topics,
	multi_menu = true,
}

Main_menu_mp_help_info = {
	num_items = 0,
	on_show = main_menu_build_help_menu_info,
	multi_menu = true,
	btn_tips = Pause_menu_back_only,
}

Main_menu_multiplayer = {
}

Main_menu_multiplayer_pc = {
	header_label_str = "MAINMENU_MULTI",
	num_items = 5,
	on_back = main_menu_restore,
	on_map = main_menu_restore,
	multi_menu = true,

	[0] = { label = "MULTI_LAN",				type = MENU_ITEM_TYPE_SUB_MENU, sub_menu = Main_menu_system_link },
	[1] = { label = "MSGLOG_TITLE_TUT",				type = MENU_ITEM_TYPE_SELECTABLE, on_select = main_menu_start_tutorial_mode },
	[2] = { label = "HELP_TEXT_SURGEON_TITLE", type = MENU_ITEM_TYPE_SELECTABLE,	on_select = main_menu_start_player_create	},
	[3] = { label = "MAP_HIDDENNAME_STORE", type = MENU_ITEM_TYPE_SELECTABLE,	on_select = main_menu_start_player_customize	},
	[4] = { label = "MULTI_MENU_CUSTOMIZATION_WARDROBE", type = MENU_ITEM_TYPE_SELECTABLE, on_select = main_menu_start_player_wardrobe },
}

Main_menu_coop_privacy = {
}

Main_menu_coop_join_player_menu = {
}

Main_menu_system_link_find_game_coop = {
}

Main_menu_coop_syslink = {
	header_label_str = "MAINMENU_COOP",
	num_items = 4,
	on_back = main_menu_restore,	-- Enable back button [nclok1405]
	on_map = main_menu_restore,
	multi_menu = true,
	on_show = main_menu_coop_syslink_sign_in_build,

	[0] = { label = "MULTI_NAME", type = MENU_ITEM_TYPE_INFO_BOX, info_text_str = "Unknown", on_select = on_multi_login_enter_player_syslink_name },
	[1] = { label = "MULTI_FIND_GAMES", 		type = MENU_ITEM_TYPE_SELECTABLE, 	on_select = Main_menu_system_link_find_game_coop_PC },
	[2] = { label = "MAINMENU_NEW", 			type = MENU_ITEM_TYPE_SELECTABLE,	on_select = main_menu_start_syslink_coop },
	[3] = { label = "SAVELOAD_LOAD_GAME", 		type = MENU_ITEM_TYPE_SELECTABLE,	on_select = main_menu_load_coop_syslink},

}

Main_menu_find_coop_online_menu = {
}

function multi_menu_coop_build_save_new_pc()
end

-- Show Help Page 1
function show_help_page_1()
	Main_menu_mp_help_topics.parent_menu = Help_menu_1	-- Set parent menu of help list
	menu_show(Help_menu_1, MENU_TRANSITION_SWEEP_LEFT)
end

-- Show Help Page 2
function show_help_page_2()
	Main_menu_mp_help_topics.parent_menu = Help_menu_2	-- Set parent menu of help list
	menu_show(Help_menu_2, MENU_TRANSITION_SWEEP_LEFT)
end

-- Show Help Category
function show_help(cat)
	help_category_id = cat
	menu_show(Main_menu_mp_help_topics, MENU_TRANSITION_SWEEP_LEFT)
end

-- Display Help Categories
function help_act()
	show_help(0)
end
function help_cell()
	show_help(1)
end
function help_cc()
	show_help(2)
end
function help_control()
	show_help(3)
end
function help_crib()
	show_help(4)
end
function help_diversions()
	show_help(5)
end
function help_gangs()
	show_help(6)
end
function help_homies()
	show_help(7)
end
function help_hud()
	show_help(8)
end
function help_msn()
	show_help(9)
end
function help_pause()
	show_help(10)
end
function help_respect()
	show_help(11)
end
function help_shop()
	show_help(12)
end
function help_mp()
	show_help(13)
end
function help_sandboxplusplus()
	show_help(14)
end

-- SuperUI Version Info [nclok1405]
function main_menu_about_superui()
	dialog_box_message("SuperUI", "SuperUI v"..tostring(SUI_VERSION).."\nMod by nclok1405\nhttps://www.saintsrowmods.com/forum/threads/16718/")
end

-- Help Menu [nclok1405]
-- Can't put more than 9 in one page, otherwise a glitchy scroll bar appear on the help page...
Help_menu_1 = {
	header_label_str = "Profile",
	num_items = 9,
	[0] = { label = "HELP_CAT_ACT",	type = MENU_ITEM_TYPE_SELECTABLE, on_select = help_act },
	[1] = { label = "HELP_CAT_CELL", type = MENU_ITEM_TYPE_SELECTABLE, on_select = help_cell },
	[2] = { label = "HELP_CAT_CC", type = MENU_ITEM_TYPE_SELECTABLE, on_select = help_cc },
	[3] = { label = "HELP_CAT_CONTROL", type = MENU_ITEM_TYPE_SELECTABLE,  on_select = help_control },
	[4] = { label = "HELP_CAT_CRIB", type = MENU_ITEM_TYPE_SELECTABLE,  on_select = help_crib },
	[5] = { label = "HELP_CAT_DIVERSIONS", type = MENU_ITEM_TYPE_SELECTABLE,  on_select = help_diversions },
	[6] = { label = "HELP_CAT_GANGS", type = MENU_ITEM_TYPE_SELECTABLE,  on_select = help_gangs },
	[7] = { label = "HELP_CAT_HOMIES", type = MENU_ITEM_TYPE_SELECTABLE,  on_select = help_homies },
	[8] = { label = "HELP_CAT_HUD", type = MENU_ITEM_TYPE_SELECTABLE,  on_select = help_hud },
}
Help_menu_2 = {
	header_label_str = "Settings",
	num_items = 6,
	[0] = { label = "HELP_CAT_MSN", type = MENU_ITEM_TYPE_SELECTABLE,  on_select = help_msn },
	[1] = { label = "HELP_CAT_PAUSE", type = MENU_ITEM_TYPE_SELECTABLE,  on_select = help_pause },
	[2] = { label = "HELP_CAT_RESPECT", type = MENU_ITEM_TYPE_SELECTABLE,  on_select = help_respect },
	[3] = { label = "HELP_CAT_SHOP", type = MENU_ITEM_TYPE_SELECTABLE,  on_select = help_shop },
	[4] = { label = "MULTI_HELP_MULTIPLAYER", type = MENU_ITEM_TYPE_SELECTABLE,  on_select = help_mp },
	[5] = { label = "Sandbox++", type = MENU_ITEM_TYPE_SELECTABLE,  on_select = help_sandboxplusplus },
}

Main_menu_coop_online_save_new_pc = {
}

Main_menu_coop_online_pc = {
}

Main_menu_coop_pc = {
	header_label_str = "MAINMENU_COOP",
	num_items = 1,
	on_map = main_menu_restore,
	on_back = main_menu_restore,
	multi_menu = true,
	--on_show = maybe_show_login_window,

	[0] = { label = "MULTI_LAN",			type = MENU_ITEM_TYPE_SUB_MENU, 		sub_menu = Main_menu_coop_syslink },
}

Main_menu_extras = {
	header_label_str = "INFO_HELP", -- "MAINMENU_EXTRAS"
	num_items = 4,
	on_map = main_menu_restore,
	on_back = main_menu_restore,

	[0] = { label = "Profile", type = MENU_ITEM_TYPE_SELECTABLE, on_select = show_help_page_1 },
	[1] = { label = "Settings", type = MENU_ITEM_TYPE_SELECTABLE, on_select = show_help_page_2 },
	[2] = { label = "Credits", type = MENU_ITEM_TYPE_SELECTABLE, on_select = main_menu_roll_credits },
	[3] = { label = "SuperUI", type = MENU_ITEM_TYPE_SELECTABLE, on_select = main_menu_about_superui },
}

Main_menu_top = {
	num_items = 0,
	current_selection = 0,
}

Main_menu_master = {
	num_items = 8,

	[0] = { label = "MAINMENU_CONTINUE", 		type = MENU_ITEM_TYPE_SELECTABLE,	on_select = main_menu_continue_select	},
	[1] = { label = "MAINMENU_NEW",				type = MENU_ITEM_TYPE_SELECTABLE,	on_select = main_menu_new_game_select	},
	[2] = { label = "MAINMENU_LOAD",				type = MENU_ITEM_TYPE_SELECTABLE,	on_select = main_menu_load_menu_select	},
	[3] = { label = "MAINMENU_COOP", 			type = MENU_ITEM_TYPE_SELECTABLE,	on_select = main_menu_maybe_show_coop_menu	},
	[4] = { label = "MAINMENU_MULTI",			type = MENU_ITEM_TYPE_SELECTABLE,	on_select = main_menu_maybe_show_multiplayer_menu	},
	[5] = { label = "MAINMENU_OPTIONS", 		type = MENU_ITEM_TYPE_SUB_MENU,		sub_menu = Pause_options_menu	},
	[6] = { label = "INFO_HELP",			type = MENU_ITEM_TYPE_SUB_MENU,		sub_menu = Main_menu_extras	},
	-- PC
	[7] = { label = "MAINMENU_EXIT",			type = MENU_ITEM_TYPE_SUB_MENU,		on_select = main_menu_exit_game_pc	},
}

function multi_menu_log_restore()
end


Main_menu_multiplayer_create_account_gamespy = {
}

Main_menu_multiplayer_sign_in_to_gamespy = {
}

Main_menu_server_filter = {
}

Main_menu_server_filter_short = {
}

--=====================================================
--Button Tips Show
--=====================================================
function main_menu_btn_tips_show(visible)
	--Fades in/out button tips
	local anim_h = vint_object_find("menu_btn_tips_anim", nil, MENU_BASE_DOC_HANDLE)
	local twn_h = vint_object_find("menu_btn_tips_alpha_twn", anim_h)
	local target_h = vint_object_find("menu_btn_tips", nil, MENU_BASE_DOC_HANDLE)
	local initial_alpha = vint_get_property(target_h, "alpha")
	vint_set_property(twn_h, "start_value", initial_alpha)
	local target_alpha = 0
	local delay = 0
	if visible == true then
		target_alpha = 1
		delay = .1
	end
	vint_set_property(twn_h, "end_value", target_alpha)
	lua_play_anim(anim_h, delay)
end

--=====================================================
--Bling
--=====================================================
Mm_bling = {}
Mm_bling.handles = {}

function main_menu_bling_init()
	Mm_bling.handles.bling_bmp = vint_object_find("bling_0")
	Mm_bling.max_bling = 2				--Max number of blings running
	Mm_bling.wait_max = 3				--Maximum wait time for bling to start playing
	Mm_bling.wait_min = 1				--Minimum wait time for bling to start playing
	Mm_bling.active_bling = {}			--Active bling indexes
	Mm_bling.total_blings = 15 		--Total Number of blings (ANIMATIONS MUST EXIST)
	Mm_bling.items = {}
	--Hide initial bling
	vint_set_property(Mm_bling.handles.bling_bmp, "alpha", 0)

	local bmp_h, anim_h, twn_h
	for i = 0, Mm_bling.total_blings - 1 do
		--Clone and retarget bling, setup animations and callbacks
		bmp_h = vint_object_clone(Mm_bling.handles.bling_bmp)
		anim_h = vint_object_find("bling_" .. i .. "_anim")
		twn_h = vint_object_find("bling_0_alpha_twn_2", anim_h)
		vint_set_property(anim_h, "target_handle", bmp_h)
		vint_set_property(anim_h, "is_paused", true)
		vint_set_property(twn_h , "end_event", "main_menu_bling_end")
		Mm_bling.items[i] = {bmp_h = bmp_h, anim_h = anim_h, twn_h = twn_h}
	end
end



function main_menu_play_bling()
	for i = 0, 1 do
		main_menu_bling_trigger(i)
	end
end

function main_menu_bling_end(twn_h)
	--callback when a bling is done...

	--Clear bling out of active blings
	for idx, val in Mm_bling.items do
		if Mm_bling.items[idx].twn_h == twn_h then
			--Found match now clear it out of active bling
			Mm_bling.active_bling[idx] = nil
		end
	end

	--Just trigger another bling...
	main_menu_bling_trigger()
end

function main_menu_bling_trigger(offset)
	local offset_time
	if offset == nil then
		offset_time = rand_int(Mm_bling.wait_min, Mm_bling.wait_max)
	else
		offset_time = offset
	end

	local random_bling
	local counter = 0

	--At least thirty tries before we lose a bling.
	while counter < 30 do
		random_bling = rand_int(0, Mm_bling.total_blings - 1)
		if Mm_bling.active_bling[random_bling] == nil then
			--bling is not active so it is suitible
			--Add to list and play
			Mm_bling.active_bling[random_bling] = true
			lua_play_anim(Mm_bling.items[random_bling].anim_h, offset_time)
			return
		end
		counter = counter + 1
	end
end

------------------
-- Syslink Server control
-- Unused in PC, so I removed them. Server Browser is instead handled by mp_server_browser.lua. [nclok1405]
------------------
Find_server_control_no_games = true

function find_server_control_show(menu_label, menu_data)
end

function pc_update_find_server()
end

function find_server_control_release(control)
end

function find_server_control_resize_select_bar()
end

function find_server_control_update_highlight(menu_label, menu_data)
end

function find_server_control_create_scroll_bar(menu_label, menu_data)
end

function find_server_control_update_scroll_bar(menu_label, menu_data)
end

function find_server_control_show_scroll_bar(menu_data)
end

function find_server_control_set_bar_height(menu_data, new_height)
end

function find_server_control_set_thumb_size_scroll_bar(menu_data, height)
end

function find_server_control_set_thumb_pos_scroll_bar(menu_data, value)
end


function find_server_control_update_scroll_bar_scroll_bar(menu_data, scroll_data)
end

function find_server_control_update(menu_label, menu_data)
end

function find_server_control_nav_up(menu_label, menu_data)
end

function find_server_control_nav_down(menu_label, menu_data)
end

Main_menu_controls = {
}

Main_menu_controls_online = {
}
