-- multi_pause_menu.lua: Pause Menu for Competitive Multiplayer Lobby
Multi_lobby_menu_player_list = {
	size = 0,
	dirty = false,
}

Multi_lobby_has_variants = true
Multi_lobby_my_lobby_menu = 0
Multi_lobby_building_lobby_menu = false
Multi_lobby_reshowing_friends = false
Multi_lobby_loading_friends_dialog_handle = 0
Multi_lobby_custom_data_version = 0

Multi_pause_menu_showing_load_favorites = false
----[functions for menus]-----

function multi_lobby_menu_setup()
	--debug_print("vint","multiplayer_lobby_menu: setup start\n")
	Pause_horz_menu = Multi_pause_horz_menu

	if get_platform() ~= "XBOX360" then
		mp_match_type_slider_values[1] = { label = Mp_lobby_game_mode_unranked_PS3 }
	else
		-- Add ability to get friends gamercards on 360
		Multi_lobby_invite_player_menu.on_alt_select = multi_player_get_gamercard
		Multi_lobby_invite_player_menu.btn_tips = Multi_lobby_friends_tips
	end

	if get_is_host() then
		mp_lobby_stop_countdown()
	end
	Multi_lobby_my_lobby_menu = Multi_lobby_menu

	if get_platform() == "PC" then
		if get_is_matchmaking() == true then
			if get_mp_is_ranked() == true then
				Pause_lobby_players.btn_tips = Multi_lobby_ranked_menu_tips
			else
				Pause_lobby_players.btn_tips = Multi_lobby_player_menu_tips
			end
		else
			Pause_lobby_players.btn_tips = Multi_lobby_player_menu_tips_syslink
		end
	else
		if get_is_syslink() then
			Pause_lobby_players.btn_tips = Multi_lobby_player_menu_tips_syslink
		else
			Pause_lobby_players.btn_tips = Multi_lobby_player_menu_tips
		end
	end

	multi_lobby_menu_setup_populate_menus()

	--subscriptions
	vint_dataitem_add_subscription("sr2_multi_lobby_game_data", "update", "multi_menu_game_data_update")
end

function multi_lobby_menu_setup_populate_menus()
	--populate game type list
	mp_game_mode_slider_values.num_values = 0
	vint_dataresponder_request("sr2_multi_lobby_modes", "multi_player_populate_modes", 0)
	--mp_game_mode_slider_values.cur_value = get_mp_mode_index()

	-- populate map list
	mp_map_slider_values.num_values = 0
	vint_dataresponder_request("sr2_multi_lobby_maps", "multi_player_populate_maps", 0)
	--mp_map_slider_values.cur_value = get_mp_map_index()

	--populate activities
	Multi_lobby_custom_activities_menu.num_items = 0
	vint_dataresponder_request("sr2_multi_lobby_activities", "multi_menu_populate_activities", 0)

	--populate weapons
	Multi_lobby_custom_weapons_menu.num_items = 0
	vint_dataresponder_request("sr2_multi_lobby_weapon_categories", "multi_menu_populate_weapon_categories", 0)
	vint_dataresponder_request("sr2_multi_lobby_special_weapons", "multi_menu_populate_special_weapons", 0)

	--populate weather
	mp_weather_slider_values.num_values = 0
	vint_dataresponder_request("sr2_multi_lobby_weather", "multi_player_populate_weather", 0)

	--populate tags
	Multi_lobby_custom_tags_menu.num_items = 0
	vint_dataresponder_request("sr2_multi_lobby_tags", "multi_menu_populate_tags", 0)

	-- populate time of day
	mp_tod_slider_values.num_values = 0
	vint_dataresponder_request("sr2_multi_lobby_tod", "multi_menu_populate_tod", 0)

	--populate scores
	mp_brawl_scores_slider_values.num_values = 0
	vint_dataresponder_request("sr2_multi_lobby_match_scores", "multi_menu_populate_scores", 0, 0)

	mp_sa_scores_slider_values.num_values = 0
	vint_dataresponder_request("sr2_multi_lobby_match_scores", "multi_menu_populate_scores", 0, 1)

	--populate times
	mp_brawl_times_slider_values.num_values = 0
	vint_dataresponder_request("sr2_multi_lobby_match_times", "multi_menu_populate_times", 0, 0)

	mp_sa_times_slider_values.num_values = 0
	vint_dataresponder_request("sr2_multi_lobby_match_times", "multi_menu_populate_times", 0, 1)

	--set other custom options
	vint_dataresponder_request("sr2_multi_lobby_custom_options", "multi_menu_read_custom_options", 0)

	--populate vehicles
	mp_vehicle_slider_values.num_values = 0
	vint_dataresponder_request("sr2_multi_lobby_vehicles", "multi_menu_populate_vehicles", 0)

	--populate_variants
	mp_variant_slider_values.num_values = 0
	mp_variant_slider_values.set = false
	vint_dataresponder_request("sr2_multi_lobby_preset", "multi_menu_populate_variants", 0)

	--add 'custom' option past menu
	multi_menu_add_custom_variant_option()
end

function multi_lobby_maybe_show_slider( cur_menu, pos )
	if pos == -1 then
		return --option not there
	end
	if cur_menu == Menu_active then
		if Menu_active ~= nil and Menu_active.first_vis_item ~= nil and Menu_option_labels ~= nil and Menu_option_labels.max_rows ~= nil then
			local top = Menu_active.first_vis_item --does show
			local bottom = top + Menu_option_labels.max_rows --doesn't show
			if pos < Menu_active.num_items + 1 and pos >= top and pos < bottom then
				if Menu_active[pos].type == MENU_ITEM_TYPE_TEXT_SLIDER then
					menu_text_slider_update_value(Menu_option_labels[pos-top], Menu_active[pos])
				elseif Menu_active[pos].type == MENU_ITEM_TYPE_INFO_BOX then
					menu_info_box_update_value(Menu_option_labels[pos-top], Menu_active[pos])
				end
			end
		end
	end
end

function multi_lobby_show_main_sliders()
	multi_lobby_maybe_show_slider( Multi_lobby_my_lobby_menu, Multi_lobby_my_lobby_menu.rank_pos )
	multi_lobby_maybe_show_slider( Multi_lobby_my_lobby_menu, Multi_lobby_my_lobby_menu.variant_pos)
	multi_lobby_maybe_show_slider( Multi_lobby_my_lobby_menu, Multi_lobby_my_lobby_menu.map_pos )
	multi_lobby_maybe_show_slider( Multi_lobby_my_lobby_menu, Multi_lobby_my_lobby_menu.time_pos)
	multi_lobby_maybe_show_slider( Multi_lobby_my_lobby_menu, Multi_lobby_my_lobby_menu.score_pos)
	multi_lobby_maybe_show_slider( Multi_lobby_my_lobby_menu, Multi_lobby_my_lobby_menu.friendly_fire_pos )
	multi_lobby_maybe_show_slider( Multi_lobby_my_lobby_menu, Multi_lobby_my_lobby_menu.weather_pos )
	multi_lobby_maybe_show_slider( Multi_lobby_my_lobby_menu, Multi_lobby_my_lobby_menu.tod_pos)
	multi_lobby_maybe_show_slider( Multi_lobby_my_lobby_menu, Multi_lobby_my_lobby_menu.sprint_pos )
	multi_lobby_maybe_show_slider( Multi_lobby_my_lobby_menu, Multi_lobby_my_lobby_menu.ammo_pos )
	multi_lobby_maybe_show_slider( Multi_lobby_my_lobby_menu, Multi_lobby_my_lobby_menu.ped_pos )
	multi_lobby_maybe_show_slider( Multi_lobby_my_lobby_menu, Multi_lobby_my_lobby_menu.vehicle_pos)
end

function multi_player_swap_teams()
	if get_platform() == "PC" then
		if get_mp_is_ranked() == true then
			return
		end
	end

	-- flip the local player to the other team
	if get_is_team_game() == false then
		--popup a message box explaining how this is impossible
		dialog_box_message("MENU_TITLE_NOTICE", "CANT_SWITCH_TEAMS")
		return
	end
	multi_menu_switch_teams()
	--debug_print("vint","mp_hud_lobby: Swapping teams!.\n")
	--blah call code function
end

function multi_player_switch_map()
	if Multi_lobby_building_lobby_menu == true then
		return --dont' do anything
	end
	-- change current map selection to the next one
	if get_is_host() == false then
		return
	end
	mp_switch_maps(mp_map_slider_values.cur_value)
	--debug_print("vint","mp_hud_lobby: Swapping maps!.\n")
	--repopulate activities, can change based on map
	Multi_lobby_custom_activities_menu.num_items = 0
	vint_dataresponder_request("sr2_multi_lobby_activities", "multi_menu_populate_activities", 0)
end

function multi_player_switch_match_rank_type()
	if get_is_host() == false then
		return
	end
	--change the ranking type
	local rank_val = mp_match_type_slider_values.cur_value
	local ranked = true
	if rank_val == 1 then
		ranked = false
	end
	mp_change_ranked_game_type(ranked)
	if Multi_lobby_building_lobby_menu == false then
		--rebuild lobby menu
		menu_show(Multi_lobby_my_lobby_menu, MENU_TRANSITION_SWEEP_RIGHT)
	end
end

function multi_menu_add_custom_variant_option()
	--just stuff the custom option at the end past the last entry
	local size = mp_variant_slider_values.num_values
	mp_variant_slider_values[size] = { label = "MULTI_LOBBY_CUSTOM_SETTINGS", disabled = true }
	mp_variant_slider_values.num_values = size + 1
	if mp_variant_slider_values.set == false then
		--debug_print("vint", "mp_lobby_menu: setting cust 1\n")
		multi_player_set_variant_custom()
	end
	--debug_print("vint","mp_lobby_menu: added custom variant\n")
end

function multi_player_set_variant_custom()
	--debug_print("vint","mp_lobby_menu: set custom variant\n")
	--move slider to the bonus option
	Multi_lobby_menu_variant_submenu.text_slider_values.cur_value = mp_variant_slider_values.num_values - 1

	multi_lobby_maybe_show_slider(Multi_lobby_my_lobby_menu, Multi_lobby_my_lobby_menu.variant_pos)
end

Multi_lobby_game_mode = -1

function multi_player_switch_game_mode()
	if Multi_lobby_building_lobby_menu == true then
		return --dont' do anything
	end

	if Multi_lobby_game_mode == mp_game_mode_slider_values.cur_value then
		--debug_print("vint","mp_lobby_menu: switch game mode to same mode\n")
		return
	end

	if get_is_host() == false then
		--should we be able to get here?
		return
	end
	--debug_print("vint","mp_lobby_menu: swapping game modes\n")
	Multi_lobby_game_mode = mp_game_mode_slider_values.cur_value
	mp_switch_modes(mp_game_mode_slider_values.cur_value)
	--debug_print("vint","mp_lobby_menu: setting to default\n")
	multi_custom_set_preset(0) --0 is default
	mp_map_slider_values.num_values = 0
	mp_map_slider_values.cur_value = 0
	mp_variant_slider_values.num_values = 0
	mp_variant_slider_values.set = false
	vint_dataresponder_request("sr2_multi_lobby_preset", "multi_menu_populate_variants", 0)
	--add 'custom' option past menu
	multi_menu_add_custom_variant_option()
	vint_dataresponder_request("sr2_multi_lobby_maps", "multi_player_populate_maps", 0)
	mp_map_slider_values.cur_value = get_mp_map_index()
	local map_pos = Multi_lobby_my_lobby_menu.num_items - 1
	multi_lobby_read_and_show_custom_match_data()
	if Multi_lobby_building_lobby_menu == false then
		--rebuild lobby menu
		menu_show(Multi_lobby_my_lobby_menu, MENU_TRANSITION_SWEEP_RIGHT)
	end
end

function multi_player_start_game()
	-- start the game as is bitches!
	if start_multiplayer_game() then
		pause_menu_exit()
	end
	--blah
end

function multi_player_populate_maps(display_name, enabled)
	local num_maps = mp_map_slider_values.num_values
	mp_map_slider_values.num_values = num_maps + 1
	mp_map_slider_values[num_maps] = { label = display_name }
	if enabled then
		mp_map_slider_values.cur_value = num_maps
	end
end

function multi_player_populate_modes(display_name, enabled)
	local num_modes = mp_game_mode_slider_values.num_values
	--debug_print("vint","mp_lobby_menu: adding mode\n")
	mp_game_mode_slider_values.num_values = num_modes + 1
	mp_game_mode_slider_values[num_modes] = { label = display_name }
	if enabled then
		mp_game_mode_slider_values.cur_value = num_modes
		Multi_lobby_game_mode = num_modes
	end
end

function multi_menu_populate_variants(display_name, enabled)
	local num_variants = mp_variant_slider_values.num_values
	mp_variant_slider_values.num_values = num_variants + 1
	mp_variant_slider_values[num_variants] = { label = display_name }
	if enabled then
		mp_variant_slider_values.cur_value = num_variants
		mp_variant_slider_values.set = true
	end
end

function multi_menu_populate_activities(display_name, active, available)
	local num_activities = Multi_lobby_custom_activities_menu.num_items

	if available == false then
		Multi_lobby_custom_activities_menu[num_activities] = {label = display_name, type = MENU_ITEM_TYPE_INFO_BOX, info_text_str = "STORE_NOT_AVAILABLE", on_select = multi_menu_submenu_on_select}
		Multi_lobby_custom_activities_menu.num_items = num_activities + 1
		multi_lobby_maybe_show_slider( Multi_lobby_custom_activities_menu, num_activities )
		return
	end

	local option = 0
	if active == false then
		option = 1
	end

	if get_is_host() == false then
		--debug_print("vint", "activities client\n")
		Multi_lobby_custom_activities_menu[num_activities] = {label = display_name, type = MENU_ITEM_TYPE_TEXT_SLIDER, text_slider_values = { [0] = { label = "MULTI_LOBBY_ON" }, [1] = { label = "MULTI_LOBBY_OFF" }, num_values = 2, cur_value = option }, slider_disabled = true, on_value_update = nil, id = num_activities, on_select = multi_menu_submenu_on_select}
	else
		--debug_print("vint", "activities host\n")
		Multi_lobby_custom_activities_menu[num_activities] = {label = display_name, type = MENU_ITEM_TYPE_TEXT_SLIDER, text_slider_values = { [0] = { label = "MULTI_LOBBY_ON" }, [1] = { label = "MULTI_LOBBY_OFF" }, num_values = 2, cur_value = option }, on_value_update = multi_lobby_update_activity, id = num_activities, on_select = multi_menu_submenu_on_select}
	end
	Multi_lobby_custom_activities_menu.num_items = num_activities + 1
	multi_lobby_maybe_show_slider( Multi_lobby_custom_activities_menu, num_activities )
end

function multi_menu_populate_tags(display_name, enabled)
	local num_tags = Multi_lobby_custom_tags_menu.num_items
	if get_is_host() then
		Multi_lobby_custom_tags_menu[num_tags] = {label = display_name, type = MENU_ITEM_TYPE_TEXT_SLIDER, text_slider_values = { [0] = { label = "MULTI_LOBBY_ON" }, [1] = { label = "MULTI_LOBBY_OFF" }, num_values = 2, cur_value = 0 }, on_value_update = multi_lobby_update_tag, id = num_tags, on_select = multi_menu_submenu_on_select}
	else
		Multi_lobby_custom_tags_menu[num_tags] = {label = display_name, type = MENU_ITEM_TYPE_TEXT_SLIDER, text_slider_values = { [0] = { label = "MULTI_LOBBY_ON" }, [1] = { label = "MULTI_LOBBY_OFF" }, num_values = 2, cur_value = 0 }, slider_disabled = true, on_value_update = nil, id = num_tags, on_select = multi_menu_submenu_on_select}
	end
	if enabled == false then
		Multi_lobby_custom_tags_menu[num_tags].text_slider_values.cur_value = 1
	end
	Multi_lobby_custom_tags_menu.num_items = num_tags + 1
	multi_lobby_maybe_show_slider(Multi_lobby_custom_tags_menu, num_tags)
end

function multi_menu_submenu_on_select(menu_label, menu_data)
	menu_show(Multi_lobby_menu, MENU_TRANSITION_SWEEP_LEFT)
end

function multi_menu_populate_tod(display_name, enabled)
	--debug_print("vint", "multi_lobby: pop tod\n")
	local num_tod = mp_tod_slider_values.num_values
	mp_tod_slider_values.num_values = num_tod + 1
	mp_tod_slider_values[num_tod] = { label = display_name }
	if enabled == true then
		--debug_print("vint", "multi_lobby: tod set!\n")
		mp_tod_slider_values.cur_value = num_tod
	end
end

function multi_menu_populate_vehicles(display_name, enabled)
	local num_veh = mp_vehicle_slider_values.num_values
	mp_vehicle_slider_values.num_values = num_veh + 1
	mp_vehicle_slider_values[num_veh] = { label = display_name }
	if enabled then
		mp_vehicle_slider_values.cur_value = num_veh
	end
end

function multi_menu_populate_scores(display_name, strongarm, enabled)
	local slider = mp_brawl_scores_slider_values
	local test = "MULTI_MODE_13"
	if strongarm == true then
		slider = mp_sa_scores_slider_values
		test = "MULTI_MODE_STRONGARM"
	end

	local num_items = slider.num_values
	slider[num_items] = { label = display_name }
	slider.num_values = num_items + 1
	if enabled then
		--debug_print("vint","set score to ".. num_items .."\n")
		slider.cur_value = num_items
	end
end

function multi_menu_populate_times(display_name, strongarm, enabled)
	local slider = mp_brawl_times_slider_values
	if strongarm == true then
		slider = mp_sa_times_slider_values
	end
	local num_items = slider.num_values

	slider[num_items] = { label = display_name }
	slider.num_values = num_items + 1
	if enabled then
		slider.cur_value = num_items
	end
end

function multi_menu_populate_weapon_infos(display_name, id, enabled)
	local my_slider = Multi_lobby_custom_weapons_menu[id].text_slider_values
	local slider_size = my_slider.num_values
	my_slider[slider_size] = {label = display_name}
	if enabled then
		my_slider.set_value = true
		my_slider.cur_value = slider_size
	end
	my_slider.num_values = slider_size + 1
end

function multi_menu_populate_weapon_categories(display_name)
	local num_types = Multi_lobby_custom_weapons_menu.num_items
	if get_is_host() then
		Multi_lobby_custom_weapons_menu[num_types] = {label = display_name, type = MENU_ITEM_TYPE_TEXT_SLIDER, text_slider_values = { [0] = { label = "test" }, num_values = 0, cur_value = 0 }, on_value_update = multi_lobby_update_weapon_selection, id = num_types, on_select = multi_menu_submenu_on_select}
	else
		Multi_lobby_custom_weapons_menu[num_types] = {label = display_name, type = MENU_ITEM_TYPE_TEXT_SLIDER, text_slider_values = { [0] = { label = "test" }, num_values = 0, cur_value = 0 }, slider_disabled = true, on_value_update = nil, id = num_types, on_select = multi_menu_submenu_on_select}
	end
	Multi_lobby_custom_weapons_menu.num_items = num_types + 1
	local my_slider = Multi_lobby_custom_weapons_menu[num_types].text_slider_values
	my_slider.set_value = false

	--fill out the selections on the slider
	vint_dataresponder_request("sr2_multi_lobby_weapon_info", "multi_menu_populate_weapon_infos", 0, num_types)

	--add a 'none' selection
	local slider_size = my_slider.num_values
	my_slider[slider_size] = {label = "LOCALIZE_NONE"}
	my_slider.num_values = slider_size + 1
	if my_slider.set_value == false then
		my_slider.cur_value = slider_size
	end
	multi_lobby_maybe_show_slider(Multi_lobby_custom_weapons_menu, num_types)
end

function multi_menu_populate_special_weapons(display_name, id, enabled)
	local num_items = Multi_lobby_custom_weapons_menu.num_items

	if get_is_host() then
		Multi_lobby_custom_weapons_menu[num_items] = {label = display_name, type = MENU_ITEM_TYPE_TEXT_SLIDER, text_slider_values = { [0] = { label = "MULTI_LOBBY_ON" }, [1] = { label = "MULTI_LOBBY_OFF" }, num_values = 2, cur_value = 0 }, on_value_update = multi_lobby_update_special_weapon_selection, id = id, on_select = multi_menu_submenu_on_select}
	else
		Multi_lobby_custom_weapons_menu[num_items] = {label = display_name, type = MENU_ITEM_TYPE_TEXT_SLIDER, text_slider_values = { [0] = { label = "MULTI_LOBBY_ON" }, [1] = { label = "MULTI_LOBBY_OFF" }, num_values = 2, cur_value = 0 }, slider_disabled = true, on_value_update = nil, id = id, on_select = multi_menu_submenu_on_select}
	end
	if enabled == false then
		Multi_lobby_custom_weapons_menu[num_items].text_slider_values.cur_value = 1
	end

	multi_lobby_maybe_show_slider( Multi_lobby_custom_weapons_menu, num_items )

	Multi_lobby_custom_weapons_menu.num_items = num_items + 1
end

function multi_player_populate_weather(display_name, current)
	local num_types = mp_weather_slider_values.num_values
	mp_weather_slider_values[num_types] = {label = display_name}
	mp_weather_slider_values.num_values = num_types + 1
	if current then
		mp_weather_slider_values.cur_value = num_types
	end
end

function multi_menu_read_custom_options(peds, ammo, sprint, friendly_fire)
	--just set the cur value on the sliders
	local option = 1
	if peds then
		option = 0
	end
	Multi_lobby_menu_peds_submenu.text_slider_values.cur_value = option
	option = 1
	if ammo then
		option = 0
	end
	Multi_lobby_menu_ammo_submenu.text_slider_values.cur_value = option
	option = 1
	if sprint then
		option = 0
	end
	Multi_lobby_menu_sprint_submenu.text_slider_values.cur_value = option

	Multi_lobby_menu_friendly_fire_submenu.text_slider_values.cur_value = friendly_fire

	multi_lobby_maybe_show_slider( Multi_lobby_my_lobby_menu, Multi_lobby_my_lobby_menu.ped_pos )
	multi_lobby_maybe_show_slider( Multi_lobby_my_lobby_menu, Multi_lobby_my_lobby_menu.ammo_pos )
	multi_lobby_maybe_show_slider( Multi_lobby_my_lobby_menu, Multi_lobby_my_lobby_menu.sprint_pos )
	multi_lobby_maybe_show_slider( Multi_lobby_my_lobby_menu, Multi_lobby_my_lobby_menu.friendly_fire_pos )

end

function multi_lobby_read_and_show_custom_match_data()
	--debug_print("vint", "multi lobby: read custom match data\n")
	--populate activities
	Multi_lobby_custom_activities_menu.num_items = 0
	vint_dataresponder_request("sr2_multi_lobby_activities", "multi_menu_populate_activities", 0)

	--populate weapons
	Multi_lobby_custom_weapons_menu.num_items = 0
	vint_dataresponder_request("sr2_multi_lobby_weapon_categories", "multi_menu_populate_weapon_categories", 0)
	vint_dataresponder_request("sr2_multi_lobby_special_weapons", "multi_menu_populate_special_weapons", 0)

	--populate weather
	mp_weather_slider_values.num_values = 0
	vint_dataresponder_request("sr2_multi_lobby_weather", "multi_player_populate_weather", 0)

	--populate tags
	Multi_lobby_custom_tags_menu.num_items = 0
	vint_dataresponder_request("sr2_multi_lobby_tags", "multi_menu_populate_tags", 0)

	-- populate time of day
	mp_tod_slider_values.num_values = 0
	vint_dataresponder_request("sr2_multi_lobby_tod", "multi_menu_populate_tod", 0)

	--populate scores
	mp_brawl_scores_slider_values.num_values = 0
	vint_dataresponder_request("sr2_multi_lobby_match_scores", "multi_menu_populate_scores", 0, 0)

	mp_sa_scores_slider_values.num_values = 0
	vint_dataresponder_request("sr2_multi_lobby_match_scores", "multi_menu_populate_scores", 0, 1)

	--populate times
	mp_brawl_times_slider_values.num_values = 0
	vint_dataresponder_request("sr2_multi_lobby_match_times", "multi_menu_populate_times", 0, 0)

	mp_sa_times_slider_values.num_values = 0
	vint_dataresponder_request("sr2_multi_lobby_match_times", "multi_menu_populate_times", 0, 1)

	--set other custom options
	vint_dataresponder_request("sr2_multi_lobby_custom_options", "multi_menu_read_custom_options", 0)

	--populate vehicles
	mp_vehicle_slider_values.num_values = 0
	vint_dataresponder_request("sr2_multi_lobby_vehicles", "multi_menu_populate_vehicles", 0)

	--if get_is_host() == false then
		--populate_variants
		mp_variant_slider_values.num_values = 0
		mp_variant_slider_values.set = false
		vint_dataresponder_request("sr2_multi_lobby_preset", "multi_menu_populate_variants", 0)
		--add 'custom' option past menu
		multi_menu_add_custom_variant_option()
	--end

	--reshow everything
	multi_lobby_show_main_sliders()
end

function multi_player_send_invite()
	--debug_print("vint","multi_lobby_menu: sending invite to ".. Menu_active.highlighted_item .."\n")
	local result = send_mp_lobby_player_invite(Menu_active.highlighted_item)
	if result == true then
		--say we invited the friend
		local style_insert = {[0] = Multi_lobby_invite_player_menu[Menu_active.highlighted_item].label}
		local style_string = vint_insert_values_in_string("MP_INVITE_SENT_BODY", style_insert)
		dialog_box_message("MP_INVITE_SENT_TITLE", style_string)
	else
		local style_insert = {[0] = Multi_lobby_invite_player_menu[Menu_active.highlighted_item].label}
		local style_string = vint_insert_values_in_string("INVITE_FAILED_BODY", style_insert)
		dialog_box_message("INVITE_FAILED_TITLE", style_string)
	end
		--do we need to say invite failed?
end

function multi_player_populate_friends(display_name)
	--debug_print("vint","multi_lobby_menu: pop_friends\n")
	local num_items = Multi_lobby_invite_player_menu.num_items
	--add item yay
	Multi_lobby_invite_player_menu[num_items] = {label = display_name, type = MENU_ITEM_TYPE_SELECTABLE, on_select = multi_player_send_invite 	}
	Multi_lobby_invite_player_menu.num_items = num_items + 1

end

function multi_player_get_gamercard()
	--debug_print("vint", "Get friend gamercard here!\n")
	show_mp_lobby_friend_gamercard(Menu_active.highlighted_item)
end

function multi_lobby_build_invite_player_request()
	--debug_print("vint","multi_lobby_menu: player request\n")
	Multi_lobby_invite_player_menu.num_items = 0
	vint_dataresponder_request("sr2_multi_lobby_friends", "multi_player_populate_friends", 0)
	--debug_print("vint","multi_lobby_menu: request done\n")
	if Multi_lobby_loading_friends_dialog_handle ~= 0 then
		dialog_box_force_close(Multi_lobby_loading_friends_dialog_handle)
		Multi_lobby_loading_friends_dialog_handle = 0
	end
	if Multi_lobby_invite_player_menu.num_items == 0 then
		dialog_box_message("MENU_TITLE_NOTICE", "NO_FRIENDS_ONLINE")
	else
		menu_show(Multi_lobby_invite_player_menu, MENU_TRANSITION_SWEEP_RIGHT)
	end
	--debug_print("vint","multi_lobby_menu: test\n")
end

function multi_lobby_load_friends()
	--open a dialog box
	Multi_lobby_loading_friends_dialog_handle = dialog_box_message("GAME_LOADING", "MULTI_INVITE_FILTER_FRIENDS")
	--request the friends
	thread_new("multi_lobby_build_invite_player_request")
end

function multi_player_switch_game_variant(menu_label, menu_data)
	if Multi_lobby_building_lobby_menu == true then
		return --dont' do anything
	end
	if get_is_host() == false then
		return
	end
	--debug_print("vint","switching_variants "..menu_data.text_slider_values.cur_value.." out of : ".. menu_data.text_slider_values.num_values.."\n")
	multi_custom_set_preset(menu_data.text_slider_values.cur_value)
	--re read the custom shiz
	multi_lobby_read_and_show_custom_match_data()
	multi_lobby_show_main_sliders()
end

function multi_lobby_update_time_limit(menu_label, menu_data)
	if Multi_lobby_building_lobby_menu == true then
		return --dont' do anything
	end

	if get_is_host() == false then
		--should we be able to get here
		return
	end
	multi_custom_set_time_limit(menu_data.text_slider_values.cur_value)
	multi_player_set_variant_custom()
end

function multi_lobby_update_score_limit(menu_label, menu_data)
	if Multi_lobby_building_lobby_menu == true then
		return --dont' do anything
	end

	if get_is_host() == false then
		--should we be able to get here?
		return
	end
	multi_custom_set_score_limit(menu_data.text_slider_values.cur_value)
	multi_player_set_variant_custom()
end

function multi_lobby_update_friendly_fire(menu_label, menu_data)
	if Multi_lobby_building_lobby_menu == true then
		return --dont' do anything
	end

	if get_is_host() == false then
		--should we be able to get here?
		return
	end
	multi_custom_set_friendly_fire(menu_data.text_slider_values.cur_value)
	multi_player_set_variant_custom()
end

function multi_player_switch_vehicle_set(menu_label, menu_data)
	if Multi_lobby_building_lobby_menu == true then
		return --dont' do anything
	end

	if get_is_host() == false then
		--should we be able to get here?
		return
	end
	--debug_print("vint","mp_lobby_menu: changing vehicle "..menu_data.text_slider_values.cur_value.."\n")
	multi_custom_set_vehicle_set(menu_data.text_slider_values.cur_value)
		--debug_print("vint", "mp_lobby_menu: setting cust 3\n")
	multi_player_set_variant_custom()
end

function multi_lobby_update_weather(menu_label, menu_data)
	if Multi_lobby_building_lobby_menu == true then
		return --dont' do anything
	end

	if get_is_host() == false then
		--should we be able to get here?
		return
	end

	multi_set_weather_stage(menu_data.text_slider_values.cur_value)
		--debug_print("vint", "mp_lobby_menu: setting cust 4\n")
end

function multi_lobby_update_tod(menu_label, menu_data)
	if Multi_lobby_building_lobby_menu == true then
		return --dont' do anything
	end

	if get_is_host() == false then
		--should we be able to get here?
		return
	end

	multi_custom_set_tod(menu_data.text_slider_values.cur_value)
		--debug_print("vint", "mp_lobby_menu: setting cust 5\n")
end

function multi_lobby_update_peds(menu_label, menu_data)
	if Multi_lobby_building_lobby_menu == true then
		return --dont' do anything
	end

	if get_is_host() == false then
		--should we be able to get here?
		return
	end
	local peds = true
	if menu_data.text_slider_values.cur_value == 1 then
		peds = false
	end
	multi_custom_set_peds(peds)
		--debug_print("vint", "mp_lobby_menu: setting cust 6\n")
	multi_player_set_variant_custom()
end

function multi_lobby_update_sprint(menu_label, menu_data)
	if Multi_lobby_building_lobby_menu == true then
		return --dont' do anything
	end

	if get_is_host() == false then
		--should we be able to get here?
		return
	end
	local sprint = true
	if menu_data.text_slider_values.cur_value == 1 then
		sprint = false
	end
	multi_custom_set_sprint(sprint)
		--debug_print("vint", "mp_lobby_menu: setting cust 7\n")
	multi_player_set_variant_custom()
end

function multi_lobby_update_ammo(menu_label, menu_data)
	if Multi_lobby_building_lobby_menu == true then
		return --dont' do anything
	end

	if get_is_host() == false then
		--should we be able to get here?
		return
	end
	local ammo = true
	if menu_data.text_slider_values.cur_value == 1 then
		ammo = false
	end
	multi_custom_set_ammo(ammo)
		--debug_print("vint", "mp_lobby_menu: setting cust 8\n")
	multi_player_set_variant_custom()
end

function multi_lobby_update_special_weapon_selection(menu_label, menu_data)
	if get_is_host() == false then
		--should we be able to get here?
		return
	end
	local weapon_id = menu_data.id
	local enabled = true
	if menu_data.text_slider_values.cur_value == 1 then
		enabled = false
	end
	multi_enable_special_weapon(weapon_id, enabled)
		--debug_print("vint", "mp_lobby_menu: setting cust 9\n")
	multi_player_set_variant_custom()
end

function multi_lobby_update_weapon_selection(menu_label, menu_data)
	if get_is_host() == false then
		--should we be able to get here?
		return
	end
	local category = menu_data.id
	local choice = menu_data.text_slider_values.cur_value

	multi_set_weapon_category_choice(category, choice)
		--debug_print("vint", "mp_lobby_menu: setting cust 10\n")
	multi_player_set_variant_custom()
end

function multi_lobby_update_activity(menu_label, menu_data)
	if get_is_host() == false then
		--should we be able to get here?
		return
	end
	local activity_val = true
	if menu_data.text_slider_values.cur_value == 1 then
		activity_val = false
	end
	multi_custom_set_activity_status(menu_data.id, activity_val)
		--debug_print("vint", "mp_lobby_menu: setting cust 11\n")
	multi_player_set_variant_custom()

end

function multi_lobby_update_tag(menu_label, menu_data)
	if get_is_host() == false then
		--should we be able to get here?
		return
	end
	local tag_val = true
	if menu_data.text_slider_values.cur_value == 1 then
		tag_val = false
	end
	multi_custom_set_tag_status(menu_data.id, tag_val)
		--debug_print("vint", "mp_lobby_menu: setting cust 12\n")
	multi_player_set_variant_custom()
end


function multi_lobby_menu_build_menu()

	Multi_lobby_building_lobby_menu = true
	Multi_lobby_my_lobby_menu = Multi_lobby_menu

	if get_is_matchmaking() then
		if get_mp_is_ranked() then
			Multi_lobby_my_lobby_menu.header_label_str =  "MULTI_GAMETYPE_3"
		else
			if get_is_custom_game() then
				Multi_lobby_my_lobby_menu.header_label_str = "MULTI_PARTY_GAME"
			else
				Multi_lobby_my_lobby_menu.header_label_str =  "MULTI_GAMETYPE_2"
			end
		end
		--Multi_lobby_my_lobby_menu.header_label_str = "MULTI_GAMETYPE_4"
	else
		Multi_lobby_my_lobby_menu.header_label_str = "MULTI_PARTY_GAME"
	end

	--update button tips
	if get_is_host() and get_is_syslink() == false then
		if get_platform() == "PC" then
			Multi_lobby_my_lobby_menu.on_alt_select = nil
		else
			Multi_lobby_my_lobby_menu.on_alt_select = multi_lobby_switch_matchmaking
		end
		if get_is_matchmaking() then
			Multi_lobby_my_lobby_menu.btn_tips = Multi_lobby_lobby_menu_matchmaking_tips
		else
			Multi_lobby_my_lobby_menu.btn_tips = Multi_lobby_lobby_menu_custom_tips
		end
	else
		Multi_lobby_my_lobby_menu.btn_tips = nil
		Multi_lobby_my_lobby_menu.on_alt_select = nil
	end

	--menu is very different based on game state
	--method, go through items in order and just add to list keeping track of position
	local menu_size = 0
	if get_is_host() then
		--add 'start game' variant
		if get_platform() ~= "PC" then
			if get_is_matchmaking() then
				Multi_lobby_my_lobby_menu[menu_size] = Multi_lobby_menu_find_match_submenu
			else
				Multi_lobby_my_lobby_menu[menu_size] = Multi_lobby_menu_start_match_submenu
			end
		else
			Multi_lobby_my_lobby_menu[menu_size] = Multi_lobby_menu_start_match_submenu
		end
		menu_size = menu_size + 1
	end


	if get_platform() ~= "PC" then
		if get_is_syslink() == false then
			--invite your friends!
			Multi_lobby_my_lobby_menu[menu_size] = Multi_lobby_menu_invite_submenu
			menu_size = menu_size + 1
		end
	end

	if get_platform() ~= "PC" then
		if get_is_matchmaking() then
			-- what type of match!?
			Multi_lobby_my_lobby_menu[menu_size] = Multi_lobby_menu_match_type_submenu
			if get_is_host() == false then
				Multi_lobby_my_lobby_menu[menu_size].slider_disabled = true
			end

			if get_mp_is_ranked() then
				mp_match_type_slider_values.cur_value = 0
			else
				mp_match_type_slider_values.cur_value = 1
			end
			Multi_lobby_my_lobby_menu.rank_pos = menu_size
			menu_size = menu_size + 1

		else
			Multi_lobby_my_lobby_menu.rank_pos = -1
		end
	end
	--everyone has game mode! yay
	if get_is_matchmaking() ~= true then
		Multi_lobby_my_lobby_menu[menu_size] = Multi_lobby_menu_game_mode_submenu

		if get_is_host() == false then
			Multi_lobby_my_lobby_menu[menu_size].slider_disabled = true
		end
		menu_size = menu_size + 1
	end

	local num_variants = get_num_mp_variants()
	--debug_print("vint","mp_lobby_menu: build lobby menu. vars: "..num_variants.."\n")
	if num_variants > 0 and get_mp_is_ranked() == false then
		--hey we have variants for this mode... show em
		Multi_lobby_my_lobby_menu[menu_size] = Multi_lobby_menu_variant_submenu
		Multi_lobby_my_lobby_menu.variant_pos = menu_size
		if get_is_host() == false then
			Multi_lobby_my_lobby_menu[menu_size].slider_disabled = true
		end
		menu_size = menu_size + 1
	else
		Multi_lobby_my_lobby_menu.variant_pos = -1
	end

	--everyone has a map.. gotta have a place to play
	Multi_lobby_my_lobby_menu[menu_size] = Multi_lobby_menu_map_submenu
	Multi_lobby_my_lobby_menu.map_pos = menu_size
	if get_is_host() == false then
		Multi_lobby_my_lobby_menu[menu_size].slider_disabled = true
	end
	menu_size = menu_size + 1

	if get_is_matchmaking() == false or get_is_custom_game() == true then
		--the rest of this stuff is only used in create your own maptches
		Multi_lobby_my_lobby_menu.time_pos = menu_size
		Multi_lobby_my_lobby_menu.score_pos = menu_size + 1
		Multi_lobby_my_lobby_menu.friendly_fire_pos = menu_size + 2
		Multi_lobby_my_lobby_menu.weather_pos = menu_size + 3
		Multi_lobby_my_lobby_menu.tod_pos = menu_size + 4
		Multi_lobby_my_lobby_menu.sprint_pos = menu_size + 5
		Multi_lobby_my_lobby_menu.ammo_pos = menu_size + 6
		if get_is_strongarm() then
			Multi_lobby_menu_time_submenu.text_slider_values = mp_sa_times_slider_values
			Multi_lobby_menu_score_submenu.text_slider_values = mp_sa_scores_slider_values
		else
			Multi_lobby_menu_time_submenu.text_slider_values = mp_brawl_times_slider_values
			Multi_lobby_menu_score_submenu.text_slider_values = mp_brawl_scores_slider_values
		end
		Multi_lobby_my_lobby_menu[menu_size]   = Multi_lobby_menu_time_submenu
		Multi_lobby_my_lobby_menu[menu_size+1] = Multi_lobby_menu_score_submenu
		Multi_lobby_my_lobby_menu[menu_size+2] = Multi_lobby_menu_friendly_fire_submenu
		Multi_lobby_my_lobby_menu[menu_size+3] = Multi_lobby_menu_weather_submenu
		Multi_lobby_my_lobby_menu[menu_size+4] = Multi_lobby_menu_tod_submenu
		Multi_lobby_my_lobby_menu[menu_size+5] = Multi_lobby_menu_sprint_submenu
		Multi_lobby_my_lobby_menu[menu_size+6] = Multi_lobby_menu_ammo_submenu
		if get_is_host() == false then
			Multi_lobby_my_lobby_menu[menu_size].slider_disabled = true
			Multi_lobby_my_lobby_menu[menu_size+1].slider_disabled = true
			Multi_lobby_my_lobby_menu[menu_size+2].slider_disabled = true
			Multi_lobby_my_lobby_menu[menu_size+3].slider_disabled = true
			Multi_lobby_my_lobby_menu[menu_size+4].slider_disabled = true
			Multi_lobby_my_lobby_menu[menu_size+5].slider_disabled = true
			Multi_lobby_my_lobby_menu[menu_size+6].slider_disabled = true
		end
		menu_size = menu_size + 7
		if get_is_strongarm() then
			Multi_lobby_my_lobby_menu.ped_pos = menu_size
			Multi_lobby_my_lobby_menu[menu_size] = Multi_lobby_menu_peds_submenu
			if get_is_host() == false then
				Multi_lobby_my_lobby_menu[menu_size].slider_disabled = true
			end
			menu_size = menu_size + 1
		else
			Multi_lobby_my_lobby_menu.ped_pos = -1
		end

		if get_is_strongarm() then
			Multi_lobby_my_lobby_menu.vehicle_pos = menu_size
			Multi_lobby_my_lobby_menu[menu_size] = Multi_lobby_menu_vehicles_submenu
			if get_is_host() == false then
				Multi_lobby_my_lobby_menu[menu_size].slider_disabled = true
			end
			menu_size = menu_size + 1
		else
			Multi_lobby_my_lobby_menu.vehicle_pos = -1
		end

		Multi_lobby_my_lobby_menu[menu_size] = Multi_lobby_menu_weapons_submenu
		menu_size = menu_size + 1

		if get_is_strongarm() then
			--debug_print("vint","mp_lobby_menu: custom menu stronghold\n")

			Multi_lobby_my_lobby_menu[menu_size] = Multi_lobby_menu_activities_submenu
			Multi_lobby_my_lobby_menu[menu_size+1] = Multi_lobby_menu_tags_submenu
			menu_size = menu_size + 2
		end

		--possibly add favorites controls
		if get_is_host() then
			--always get save option
			Multi_lobby_my_lobby_menu[menu_size] = Multi_lobby_menu_save_favorite_submenu
			menu_size = menu_size + 1
			Multi_pause_menu_showing_load_favorites = false
			if mp_player_has_favorite_match_settings() then
				Multi_lobby_my_lobby_menu[menu_size] = Multi_lobby_menu_load_favorite_submenu
				menu_size = menu_size + 1
				Multi_pause_menu_showing_load_favorites = true
			end
		end
	else
		Multi_lobby_my_lobby_menu.time_pos = -1
		Multi_lobby_my_lobby_menu.score_pos = -1
		Multi_lobby_my_lobby_menu.friendly_fire_pos = -1
		Multi_lobby_my_lobby_menu.weather_pos = -1
		Multi_lobby_my_lobby_menu.tod_pos = -1
		Multi_lobby_my_lobby_menu.sprint_pos = -1
		Multi_lobby_my_lobby_menu.ammo_pos = -1
		Multi_lobby_my_lobby_menu.ped_pos = -1
	end
	--make sure we have the most up to date stuff in our sliders for width detection
	multi_lobby_menu_setup_populate_menus()
	--debug_print("vint","mp_lobby_menu: new menu size: ".. menu_size .."\n")
	Multi_lobby_my_lobby_menu.num_items = menu_size

end

function multi_lobby_menu_post_show()
	--debug_print("vint","multi_lobby_menu: post lobby menu show\n")
	Multi_lobby_building_lobby_menu = false
end

function multi_lobby_switch_matchmaking()
	if get_is_syslink() then
		--debug_print("vint","multi_lobby_menu: syslink swapping matchmaking! BAD\n")
		return
	end
	--debug_print("vint","mp_lobby_menu: menu change\n")
	--tell the game about the swap
	mp_swap_matchmaking()
	menu_show(Multi_lobby_menu, MENU_TRANSITION_SWEEP_RIGHT)
end

function multi_lobby_save_favorites_confirm(result, action)
	if action ~= DIALOG_ACTION_CLOSE then
		return
	end

	if result == DIALOG_RESULT_YES then
		mp_save_custom_match_settings_as_favorite()
		if Multi_pause_menu_showing_load_favorites == false then
			menu_show(Multi_lobby_menu, MENU_TRANSITION_SWEEP_RIGHT)
		end
	end
end

function multi_custom_match_maybe_save_settings()
	--throw up a confirmaton box
	if mp_player_has_favorite_match_settings() then
		dialog_box_confirmation("MENU_TITLE_WARNING", "FAVORITE_RESAVE_WARNING", "multi_lobby_save_favorites_confirm")
	else
		mp_save_custom_match_settings_as_favorite()
		if Multi_pause_menu_showing_load_favorites == false then
			menu_show(Multi_lobby_menu, MENU_TRANSITION_SWEEP_RIGHT)
		end
	end
end

function multi_custom_match_load_favorite_settings()
	mp_load_custom_match_settings_from_favorite()
	--re read the custom shiz
	multi_lobby_read_and_show_custom_match_data()
	multi_lobby_show_main_sliders()
end

Multi_local_game_data = {
	custom_match = -1,
	ranked_match = -1,
	mode_name = "invalid_mode",
	map_index = 0,
}
----[update functions]------
function multi_menu_game_data_update(data_item_handle, event_name)
	local custom_match, ranked_match, mode_name, map_index, variant_name, custom_data_version = vint_dataitem_get(data_item_handle)
	--debug_print("vint","mp_hud_lobby: update game map or type \n")
	if get_is_host() then
		--nothing for now, we should be in charge on the host side
	else
		--debug_print("vint","mp_lobby_menu: mode_name: "..mode_name.." map_index: "..map_index.."\n")
		--see what's changed
		local menu_change = false;
		local slider_change = false;

		if map_index == -1 then
			--random map
			map_index = mp_map_slider_values.num_values - 1
		end

		if map_index ~= Multi_local_game_data.map_index then
			mp_map_slider_values.cur_value = map_index
			multi_lobby_maybe_show_slider( Multi_lobby_my_lobby_menu, Multi_lobby_my_lobby_menu.map_pos )
			--debug_print("vint","mp_lobby_menu: new map: ".. map_index .."\n")
			Multi_local_game_data.map_index = map_index
			--repopulate activities
			Multi_lobby_custom_activities_menu.num_items = 0
			vint_dataresponder_request("sr2_multi_lobby_activities", "multi_menu_populate_activities", 0)
		end

		if Multi_local_game_data.ranked_match == -1 or Multi_local_game_data.ranked_match ~= ranked_match then
			--debug_print("vint","mp_lobby_menu: rank change\n")
			menu_change = true
			Multi_local_game_data.ranked_match = ranked_match
		end

		if mode_name ~= Multi_local_game_data.mode_name then
			--debug_print("vint","mp_lobby_menu: new mode \n")
			--Multi_lobby_menu_game_mode_client_submenu.info_text_str = mode_name
			slider_change = true;
			menu_change = true;
			Multi_local_game_data.mode_name = mode_name
		end

		if Multi_local_game_data.custom_match == -1 or Multi_local_game_data.custom_match ~= custom_match then
			Multi_local_game_data.custom_match = custom_match
			menu_change = true
		end

		if Multi_lobby_custom_data_version ~= custom_data_version or menu_change then
			--new custom data, read it all again
			--debug_print("vint", "mp_lobby_menu: custom data update\n")
			Multi_lobby_custom_data_version = custom_data_version
			multi_lobby_read_and_show_custom_match_data()
		end

		--update map/mode sliders
		if Menu_active == Multi_lobby_my_lobby_menu then
			if menu_change == true then
				menu_show(Multi_lobby_my_lobby_menu, MENU_TRANSITION_SWEEP_RIGHT)
			end
		end
	end
end

----[ Sliders for the Menus ]----

Mp_lobby_game_mode_ranked = "MULTI_GAMETYPE_3"
Mp_lobby_game_mode_unranked_360 = "MULTI_GAMETYPE_2"
Mp_lobby_game_mode_unranked_PS3 = "MULTI_GAMETYPE_2"
mp_map_slider_values 			= { [0] = { label = "test" }, num_values = 1, cur_value = 0 } -- values from code
mp_game_mode_slider_values 		= { [0] = { label = "test" }, num_values = 1, cur_value = 0 } -- values from code
mp_match_type_slider_values		= { [0] = { label = Mp_lobby_game_mode_ranked }, [1] = { label = Mp_lobby_game_mode_unranked_360 }, num_values = 2, cur_value = 0}
mp_variant_slider_values		= { num_values = 0, cur_value = 0 } -- values from code
--mp_on_off_slider_values			= { [0] = { label = "On" }, [1] = { label = "Off" }, num_values = 2, cur_value = 0 }
mp_brawl_times_slider_values   	= { [0] = { label = "test" }, num_values = 1, cur_value = 0 } -- values from code
mp_sa_times_slider_values	    = { [0] = { label = "test" }, num_values = 1, cur_value = 0 } -- values from code
mp_brawl_scores_slider_values	= { [0] = { label = "test" }, num_values = 1, cur_value = 0 } -- values from code
mp_sa_scores_slider_values	    = { [0] = { label = "test" }, num_values = 1, cur_value = 0 } -- values from code
mp_tod_slider_values			= { [0] = { label = "MULTI_TOD_DAY" }, [1] = { label = "MULTI_TOD_NIGHT"}, num_values = 2, cur_value = 0 }
mp_weather_slider_values		= { [0] = { label = "sunny" }, [1] = { label = "rainy" }, num_values = 2, cur_value = 0 }
mp_vehicle_slider_values 		= { [0] = { label = "test" }, num_values = 1, cur_value = 0 } -- values from code
----[Menus]----
Multi_lobby_lobby_menu_matchmaking_tips = {
	a_button 	= 	{ label = "CONTROL_SELECT", 				enabled = btn_tips_default_a, },
	--x_button 	= 	{ label = "MULTI_PARTY_GAME",		 				enabled = btn_tips_default_a, },
	b_button 	= 	{ label = "MENU_RESUME", 						enabled = btn_tips_default_a, },
}
Multi_lobby_lobby_menu_custom_tips = {
	a_button 	= 	{ label = "CONTROL_SELECT", 				enabled = btn_tips_default_a, },
	x_button 	= 	{ label = "MULTI_GAMETYPE_4", 				enabled = btn_tips_default_a, },
	b_button 	= 	{ label = "MENU_RESUME", 						enabled = btn_tips_default_a, },
}

Multi_lobby_player_menu_tips_syslink = {
	x_button 	= 	{ label = "MULTI_SWITCH_TEAMS", 				enabled = btn_tips_default_a, },
	b_button 	= 	{ label = "MENU_RESUME", 						enabled = btn_tips_default_a, },
}

Multi_lobby_player_menu_tips = {
	a_button 	= 	{ label = "CONTROL_SELECT", 				enabled = btn_tips_default_a, },
	x_button 	= 	{ label = "MULTI_SWITCH_TEAMS", 				enabled = btn_tips_default_a, },
	b_button 	= 	{ label = "MENU_RESUME", 						enabled = btn_tips_default_a, },
}

Multi_lobby_ranked_menu_tips = {
	a_button 	= 	{ label = "CONTROL_SELECT", 				enabled = btn_tips_default_a, },
	--x_button 	= 	{ label = "MULTI_SWITCH_TEAMS", 				enabled = btn_tips_default_a, },
	b_button 	= 	{ label = "MENU_RESUME", 						enabled = btn_tips_default_a, },
}

Multi_lobby_friends_tips = {
	a_button 	= 	{ label = "CONTROL_SELECT", 					enabled = btn_tips_default_a, },
	x_button 	= 	{ label = "MULTI_MENU_SHOW_GAMERCARD", 			enabled = btn_tips_default_a, },
	b_button 	= 	{ label = "MENU_BACK", 						enabled = btn_tips_default_a, },
}

Multi_lobby_subgroup_tips = {
	a_button 	= 	{ label = "MULTI_LOBBY_ACCEPT", 				enabled = btn_tips_default_a, },
	b_button 	= 	{ label = "MENU_BACK", 						enabled = btn_tips_default_a, },
}

Multi_lobby_custom_weapons_menu = {
	num_items = 1,
	max_height = 503,	-- Default: 375 [nclok1405]
	header_label_str = "MULTI_LOBBY_WEAPONS",
	on_pause = pause_menu_exit,

	[0] = {label = "test",	type = MENU_ITEM_TYPE_TEXT_SLIDER, text_slider_values = { [0] = { label = "test" }, num_values = 1, cur_value = 0 } },

	btn_tips = Multi_lobby_subgroup_tips,
}

Multi_lobby_custom_activities_menu = {
	num_items = 1,
	max_height = 503,	-- Default: 375 [nclok1405]
	header_label_str = "MULTI_ACTIVITIES",
	on_pause = pause_menu_exit,

	[0] = {label = "test",	type = MENU_ITEM_TYPE_TEXT_SLIDER, text_slider_values = { [0] = { label = "test" }, num_values = 1, cur_value = 0 } },

	btn_tips = Multi_lobby_subgroup_tips,
}

Multi_lobby_custom_tags_menu = {
	num_items = 1,
	max_height = 503,	-- Default: 375 [nclok1405]
	header_label_str = "MULTI_TAGS",
	on_pause = pause_menu_exit,

	[0] = {label = "test",	type = MENU_ITEM_TYPE_TEXT_SLIDER, text_slider_values = { [0] = { label = "test" }, num_values = 1, cur_value = 0 } },

	btn_tips = Multi_lobby_subgroup_tips,
}

Pause_lobby_players	= {
	header_label_str = "MULTI_LOBBY_SCREEN_PLAYERS",
	on_back = pause_menu_exit,
	on_pause = pause_menu_exit,
	num_items = 1,
	get_width = pause_menu_lobby_players_get_width,
	get_height = pause_menu_lobby_players_get_height,
	on_alt_select = multi_player_swap_teams,
	[0] = { label = "", type = PAUSE_MENU_CONTROL_LOBBY_PLAYERS }
}

Multi_lobby_invite_player_menu = {
	num_items = 1,
	header_label_str = "MULTI_LOBBY_INVITE_FRIENDS",
	on_pause	= pause_menu_exit,

	[0] =  { label = "MM_LOAD_LOADING", type = MENU_ITEM_TYPE_SELECTABLE, on_select = nil },
}

Multi_lobby_menu_variant_submenu = {label = "MULTI_LOBBY_VARIANT",	type = MENU_ITEM_TYPE_TEXT_SLIDER, on_value_update = multi_player_switch_game_variant, text_slider_values = mp_variant_slider_values}
Multi_lobby_menu_vehicles_submenu = {label = "MULTI_LOBBY_VEHICLES", type = MENU_ITEM_TYPE_TEXT_SLIDER, text_slider_values = mp_vehicle_slider_values, on_value_update = multi_player_switch_vehicle_set}
Multi_lobby_menu_activities_submenu = {label = "MULTI_ACTIVITIES", type = MENU_ITEM_TYPE_SUB_MENU, sub_menu = Multi_lobby_custom_activities_menu}
Multi_lobby_menu_tags_submenu = {label = "MULTI_TAGS", type = MENU_ITEM_TYPE_SUB_MENU, sub_menu = Multi_lobby_custom_tags_menu}
Multi_lobby_menu_find_match_submenu = {label = "MULTI_LOBBY_FIND_MATCH", type = MENU_ITEM_TYPE_SELECTABLE, on_select = multi_player_start_game 	}
Multi_lobby_menu_start_match_submenu = {label = "MULTI_LOBBY_START_GAME", type = MENU_ITEM_TYPE_SELECTABLE, on_select = multi_player_start_game }
Multi_lobby_menu_invite_submenu = {label = "MULTI_LOBBY_INVITE_FRIENDS", type = MENU_ITEM_TYPE_SELECTABLE, on_select = multi_lobby_load_friends}
Multi_lobby_menu_match_type_submenu = {label = "MULTI_MATCH_TYPE", type = MENU_ITEM_TYPE_TEXT_SLIDER, text_slider_values = mp_match_type_slider_values, on_value_update = multi_player_switch_match_rank_type}
Multi_lobby_menu_game_mode_submenu = {label = "MULTI_LOBBY_GAME_MODE", type = MENU_ITEM_TYPE_TEXT_SLIDER, text_slider_values = mp_game_mode_slider_values, on_value_update = multi_player_switch_game_mode}
Multi_lobby_menu_map_submenu = {label = "MULTI_LOBBY_SCREEN_MAP",	type = MENU_ITEM_TYPE_TEXT_SLIDER, text_slider_values = mp_map_slider_values, on_value_update = multi_player_switch_map}
Multi_lobby_menu_time_submenu = {label = "MULTI_TIME_LIMIT", type = MENU_ITEM_TYPE_TEXT_SLIDER, text_slider_values = mp_sa_times_slider_values, on_value_update = multi_lobby_update_time_limit}
Multi_lobby_menu_score_submenu = {label = "MULTI_LOBBY_SCORE_LIMIT", type = MENU_ITEM_TYPE_TEXT_SLIDER, text_slider_values = mp_sa_scores_slider_values, on_value_update = multi_lobby_update_score_limit}
Multi_lobby_menu_friendly_fire_submenu = {label = "MULTI_LOBBY_FRIENDLY_FIRE", type = MENU_ITEM_TYPE_TEXT_SLIDER, text_slider_values = { [0] = { label = "MULTI_LOBBY_ON" }, [1] = { label = "GENERAL_LIGHT"}, [2] = { label = "MULTI_LOBBY_OFF" }, num_values = 3, cur_value = 0 }, on_value_update = multi_lobby_update_friendly_fire}
Multi_lobby_menu_weapons_submenu = {label = "MULTI_LOBBY_WEAPONS", type = MENU_ITEM_TYPE_SUB_MENU, sub_menu = Multi_lobby_custom_weapons_menu}
Multi_lobby_menu_tod_submenu = {label = "MULTI_LOBBY_TIME_OF_DAY", type = MENU_ITEM_TYPE_TEXT_SLIDER, text_slider_values = mp_tod_slider_values, on_value_update = multi_lobby_update_tod}
Multi_lobby_menu_weather_submenu = {label = "MULTI_LOBBY_WEATHER", type = MENU_ITEM_TYPE_TEXT_SLIDER, text_slider_values = mp_weather_slider_values, on_value_update = multi_lobby_update_weather}
Multi_lobby_menu_peds_submenu = {label = "MULTI_PEDESTRIANS", type = MENU_ITEM_TYPE_TEXT_SLIDER, text_slider_values = { [0] = { label = "MULTI_LOBBY_ON" }, [1] = { label = "MULTI_LOBBY_OFF" }, num_values = 2, cur_value = 0 }, on_value_update = multi_lobby_update_peds}
Multi_lobby_menu_ammo_submenu = {label = "MULTI_UNLIMITED_AMMO", type = MENU_ITEM_TYPE_TEXT_SLIDER, text_slider_values = { [0] = { label = "MULTI_LOBBY_ON" }, [1] = { label = "MULTI_LOBBY_OFF" }, num_values = 2, cur_value = 0 }, on_value_update = multi_lobby_update_ammo}
Multi_lobby_menu_sprint_submenu = {label = "MULTI_UNLIMITED_SPRINT", type = MENU_ITEM_TYPE_TEXT_SLIDER, text_slider_values = { [0] = { label = "MULTI_LOBBY_ON" }, [1] = { label = "MULTI_LOBBY_OFF" }, num_values = 2, cur_value = 0 }, on_value_update = multi_lobby_update_sprint}
Multi_lobby_menu_save_favorite_submenu = {label = "SAVE_FAVORITE", type = MENU_ITEM_TYPE_SELECTABLE, on_select = multi_custom_match_maybe_save_settings }
Multi_lobby_menu_load_favorite_submenu = {label = "LOAD_FAVORITE", type = MENU_ITEM_TYPE_SELECTABLE, on_select = multi_custom_match_load_favorite_settings }

Multi_lobby_menu = {
	num_items = 0,
	max_height = 503,	-- Default: 375 [nclok1405]
	header_label_str = "MULTI_MENU_LOBBY",
	on_back = pause_menu_exit,
	on_pause = pause_menu_exit,
	on_show = multi_lobby_menu_build_menu,
	on_post_show = multi_lobby_menu_post_show,
	map_pos = -1,
	variant_pos = -1,
	rank_pos = -1,
	time_pos = -1,
	score_pos = -1,
	friendly_fire_pos = -1,
	tod_pos = -1,
	weather_pos = -1,
	sprint_pos = -1,
	ammo_pos = -1,
	ped_pos = -1,
	vehicle_pos = -1,
}

Multi_pause_horz_menu = {
	num_items = 3,
	current_selection = 0,
	on_back = pause_menu_exit,
	on_pause	= pause_menu_exit,

	[0] = { label = "MULTI_MENU_LOBBY", 			sub_menu = Multi_lobby_menu },
	[1] = { label = "MULTI_LOBBY_SCREEN_PLAYERS", 	sub_menu =  Pause_lobby_players	},
	[2] = { label = "PAUSEMENU_CAT_OPTIONS",		sub_menu = Pause_options_menu 	},
}
