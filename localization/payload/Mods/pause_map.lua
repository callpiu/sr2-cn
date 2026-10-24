-- pause_map.lua: Map Screen

Pause_map_styles = {
	colors = {
		filter_select = {0.2980, 0.5843, 0.934},
		filter_deselect = {0.6314, 0.6549, 0.684},
		filter_disabled = {0.3882, 0.4078, 0.434},
	}
}

Pause_map_icons_rectangle = {
	["map_other_bookmark_a_1"] = true,
	["map_other_bookmark_a_2"] = true,
	["map_other_bookmark_a_3"] = true,
	["map_other_bookmark_a_4"] = true,
	["map_other_bookmark_a_5"] = true,
	["map_other_bookmark_b_1"] = true,
	["map_other_bookmark_b_2"] = true,
	["map_other_bookmark_b_3"] = true,
	["map_other_bookmark_b_4"] = true,
	["map_other_bookmark_b_5"] = true,
	["map_other_crib"] = true,
	["map_other_crib_purchase"] = true,
	["map_other_train"] = true,
	["map_start_mission_3ss"] = true,
	["map_start_mission_bh"] = true,
	["map_start_mission_rn"] = true,
   ["map_start_mission_ss"] = true,
	["map_start_mission_ul"] = true,
	["map_other_hidden_mission"] = true,
}
Pause_map_icons_objective = {
	["map_act_kill"] = true,
	["map_act_kill_up"] = true,
	["map_act_kill_down"] = true,
	["map_act_location"] = true,
	["map_act_location_up"] = true,
	["map_act_location_down"] = true,
	["map_act_protectacquire"] = true,
	["map_act_protectacquire_up"] = true,
	["map_act_protectacquire_down"] = true
}


Pause_map_elements = {
	base = {
		map_grp_h = -1,
		map_h = -1,
		cursor_h = -1,
		info_h = -1
	},

	header = {
		hood_text_h = -1,
		district_text_h = -1,
	},
	filters = {
		activities_h = -1,
		all_h = -1,
		cribs_h = -1,
		missions_h = -1,
		none_h = -1,
		stores_h = -1,
		strongholds_h = -1,
		text_h = -1,
	},
	footer = {
		alt_select_btn_h = -1,
		alt_select_text_h = -1,
		select_btn_h = -1,
		select_text_h = -1,
		back_btn_h = -1,
		back_text_h = -1,
		up_down_btn_h = -1,
		up_down_text_h = -1,
		left_right_btn_h = -1,
		left_right_text_h = -1,
		rb_btn_h = -1,
		rb_text_h = -1,
	},
}

Pause_map_anims = {}

Pause_map = { done = false, }

Pause_map_filter_status = {
	selected_index = 0,
	total_filters = 7,
	filters = {}
}

Pause_map_cursor_status = {
	x = -1,
	y = -1,
	gps_active = -1,
	fade_mode = "in"
}

Pause_map_highlight_status = { }

Pause_map_subscriptions = { }

Pause_map_underground = false

-- assume not taxi unless told otherwise
Pause_map_taxi_mode = false

Pause_map_swapping = false

Pause_map_effect_disable_thread = -1

-- Disable ripple wave effect [nclok1405]
function pause_map_effect_disable_thread_handler()
	if not SUI_NO_RIPPLE_WAVE_EFFECT_ON_PAUSE then
		return
	end

	while true do
		pause_menu_release_camera()
		thread_yield()
	end
end

function pause_map_init()
	Pause_map_effect_disable_thread = thread_new("pause_map_effect_disable_thread_handler")

	vint_set_property(vint_object_find("pause_map"), "map_mode", "pause_map")

	--Base Group
	local h = vint_object_find("map_grp")
	Pause_map_elements.base.map_grp_h = h
	Pause_map_elements.base.map_h = vint_object_find("map", h)
	Pause_map_elements.base.info_h = vint_object_find("info", h)

	--Map Elements
	Pause_map_elements.base.cursor_h = vint_object_find("cursor", h)

	h = vint_object_find("map_frame")

	--Header Elements
	Pause_map_elements.header.district_text_h = 	vint_object_find("district_text", h)
	Pause_map_elements.header.hood_text_h 		=	vint_object_find("hood_text", h)

	--Filter Elements and initial values
	local h = vint_object_find("filters")

	-- Hide the filters if we're playing a competitive online game
	if mp_is_enabled() == true then
		vint_set_property(h, "visible", false)
	end

	Pause_map_filter_status.filters[0] = { bmp_h = vint_object_find("all", h), 			filter = "PFT_ALL", 			filter_str = "PAUSE_MAP_FILTER_ALL" }
	Pause_map_filter_status.filters[1] = { bmp_h = vint_object_find("cribs", h), 			filter = "PFT_CRIBS", 			filter_str = "PAUSE_MAP_FILTER_CRIBS"  }
	Pause_map_filter_status.filters[2] = { bmp_h = vint_object_find("stores", h), 		filter = "PFT_STORES", 		filter_str = "PAUSE_MAP_FILTER_STORES"  }
	--Pause_map_filter_status.filters[2] = { bmp_h = vint_object_find("saves", h), 		filter = "PFT_SAVES", 		filter_str = "SAVES"  }
	Pause_map_filter_status.filters[3] = { bmp_h = vint_object_find("activities", h), 	filter = "PFT_ACTIVITIES", 	filter_str = "PAUSE_MAP_FILTER_ACTIVITIES"  }
	Pause_map_filter_status.filters[4] = { bmp_h = vint_object_find("strongholds", h), 	filter = "PFT_STRONGHOLDS", 	filter_str = "PAUSE_MAP_FILTER_STRONGHOLDS"  }
	Pause_map_filter_status.filters[5] = { bmp_h = vint_object_find("missions", h), 		filter = "PFT_MISSIONS", 		filter_str = "PAUSE_MAP_FILTER_MISSIONS"  }
	--Pause_map_filter_status.filters[6] = { bmp_h = vint_object_find("trains", h), 		filter = "PFT_TRAIN_STATIONS", 	filter_str = "TRAINS"  }
	Pause_map_filter_status.filters[6] = { bmp_h = vint_object_find("none", h), 			filter = "PFT_NONE", 				filter_str = "PAUSE_MAP_FILTER_NONE"  }


	--Pause_map_filter_status.filters[8] = { bmp_h = vint_object_find("none", h), 			filter = "PFT_FILTER_LOCKED", 			filter_str = "HIDE ALL"  }
	Pause_map_elements.filters.text_h = vint_object_find("filter_text", h)

	--Footer Elements
	local h = vint_object_find("button_tips")
	Pause_map_elements.footer.button_tips = h
	Pause_map_elements.footer.alt_select_btn_h 	= vint_object_find("alt_select_btn", h)
	Pause_map_elements.footer.alt_select_text_h	= vint_object_find("alt_select_text", h)
	Pause_map_elements.footer.select_btn_h			= vint_object_find("select_btn", h)
	Pause_map_elements.footer.select_text_h 		= vint_object_find("select_text", h)
	Pause_map_elements.footer.back_btn_h 			= vint_object_find("back_btn", h)
	Pause_map_elements.footer.back_text_h 			= vint_object_find("back_text", h)
	Pause_map_elements.footer.up_down_btn_h 		= vint_object_find("up_down_btn", h)
	Pause_map_elements.footer.up_down_text_h 		= vint_object_find("up_down_text", h)
	Pause_map_elements.footer.left_right_btn_h 	= vint_object_find("left_right_btn", h)
	Pause_map_elements.footer.left_right_text_h 	= vint_object_find("left_right_text", h)

	--Display platform specific buttons
	if SUI_PLATFORM == "PC" then
		-- Modified for PC for better instructions [nclok1405]
		vint_set_property(Pause_map_elements.footer.alt_select_btn_h, "image", get_x_button())
		vint_set_property(Pause_map_elements.footer.select_btn_h, "image", "ui_ctrl_PC_key_rmb")	-- GPS: Right Mouse Button
		vint_set_property(Pause_map_elements.footer.select_btn_h, "scale", 0.55, 0.55)	-- Mouse is too big by default
		vint_set_property(Pause_map_elements.footer.back_btn_h, "image", "ui_ctrl_PC_key_tab")	-- Resume: Tab
		vint_set_property(Pause_map_elements.footer.left_right_btn_h, "image", get_dpad_lr_image())
		vint_set_property(Pause_map_elements.footer.up_down_btn_h, "image", get_dpad_ud_image())
	else
		vint_set_property(Pause_map_elements.footer.alt_select_btn_h, "image", get_x_button())
		vint_set_property(Pause_map_elements.footer.select_btn_h, "image", get_a_button())
		vint_set_property(Pause_map_elements.footer.back_btn_h, "image", get_b_button())
		vint_set_property(Pause_map_elements.footer.left_right_btn_h, "image", get_dpad_lr_image())
		vint_set_property(Pause_map_elements.footer.up_down_btn_h, "image", get_dpad_ud_image())
	end

	-- Localize "CHANGE MAP" [nclok1405]
	local change_map_text = "CHANGE_MAP"
	vint_set_property(Pause_map_elements.footer.up_down_text_h, "text_tag", change_map_text)

	--Hide info
	vint_set_property(vint_object_find("info"), "visible", false)

	--Animation find and pause
	h = vint_object_find("root_animation")
	Pause_map_anims.map_open_h					= vint_object_find("map_open", h)
	Pause_map_anims.map_close_h 				= vint_object_find("map_close", h)
	Pause_map_anims.cursor_fade_anim_h 		= vint_object_find("cursor_fade_anim", h)
	Pause_map_anims.cursor_fade_twn_h 		= vint_object_find("cursor_fade_twn", Pause_map_anims.cursor_fade_anim_h)
	Pause_map_anims.highlight_anim_in_h		= vint_object_find("highlight_anim_in", h)
	Pause_map_anims.highlight_anim_out_h	= vint_object_find("highlight_anim_out", h)
	Pause_map_anims.info_bg_anim_h			= vint_object_find("info_bg_anim", h)
	Pause_map_anims.icon_highlight_anim_h	= vint_object_find("icon_highlight_anim", h)

	vint_set_property(Pause_map_anims.map_open_h , "is_paused", true)
	vint_set_property(Pause_map_anims.map_close_h , "is_paused", true)
	vint_set_property(Pause_map_anims.cursor_fade_anim_h , "is_paused", true)
	vint_set_property(Pause_map_anims.highlight_anim_in_h , "is_paused", true)
	vint_set_property(Pause_map_anims.highlight_anim_out_h , "is_paused", true)
	vint_set_property(Pause_map_anims.info_bg_anim_h , "is_paused", true)

	--Set transition in and out events after into/extros
	local twn = vint_object_find("map_grp_anchor_twn_1", Pause_map_anims.map_open_h)
	vint_set_property(twn, "end_event", "pause_map_trans_in_complete")
	local twn = vint_object_find("map_grp_anchor_twn_1", Pause_map_anims.map_close_h)
	vint_set_property(twn, "end_event", "pause_map_trans_out_complete")

	--Subscribe to data items
	vint_dataitem_add_subscription("PAUSE_MAP_HIGHLIGHT1", "update", "pause_map_highlight_update")
	vint_dataitem_add_subscription("PAUSE_MAP_HIGHLIGHT2", "update", "pause_map_highlight_update")
	vint_dataitem_add_subscription("PAUSE_MAP_CURSOR", "update", "pause_map_cursor_update")

	--Initialize Map parts
	pause_map_btn_tips_format()
	pause_map_open()

	--Event Tracking
	event_tracking_interface_enter("Pause Map")

	if mp_is_enabled() then
		--If in mp show no pause indicators
		vint_set_property(vint_object_find("game_is_paused_text"), "visible", false)
	else
		--Otherwise show cash [nclok1405]
		vint_set_property(vint_object_find("game_is_paused_text"), "text_tag", "$"..format_cash(Sui_cash))
		vint_set_property(vint_object_find("game_is_paused_text"), "visible", true)
	end
end

function pause_map_cleanup()
	-- Kill effect disabler thread [nclok1405]
	if Pause_map_effect_disable_thread ~= -1 then
		--debug_print("Killing Effect Disabler Thread\n")
		thread_kill(Pause_map_effect_disable_thread)
		Pause_map_effect_disable_thread = -1
	end

	--Event Tracking(Exit Menu)
	event_tracking_interface_exit()

	-- HUD hide/enable
	if not Pause_map_swapping then
		if Sui_hud_enable == 0 then
			hud_hide(true)
		else
			hud_hide(false)
		end
	end
end

function pause_map_is_taxi_mode(tm)
	Pause_map_taxi_mode = (tm == true)
	pause_map_btn_tips_format()
end


-----------------------------------------------
-- Opens pause map
-----------------------------------------------
function pause_map_open()
	-- Pause Map active [nclok1405]
	Sui_paused = true

	--Play animation
	lua_play_anim(Pause_map_anims.map_open_h, 0)

	--Play sound
	local noise = audio_get_audio_id("SYS_MENU_OPEN")
	audio_play(noise)

	--Block all input by subscribing to everything
	Pause_map_subscriptions.all_unassigned = vint_subscribe_to_input_event(nil, "all_unassigned", "pause_map_input")
end

-----------------------------------------------
-- Closes pause map
-----------------------------------------------
function pause_map_close()
	--Unsubscribe from all the events
	for idx, val in Pause_map_subscriptions do
		vint_unsubscribe_to_input_event(val)
	end
	Pause_map_subscriptions.all_unassigned = vint_subscribe_to_input_event(nil, "all_unassigned", "pause_map_input")
	lua_play_anim(Pause_map_anims.map_close_h, 0)

	if Pause_map_swapping == false then
		pause_menu_release_camera()

		-- Pause Map no longer active [nclok1405]
		Sui_paused = false
	else
		-- Swap to Pause Menu
	end

	--Play sound
	local noise = audio_get_audio_id("SYS_MENU_CLOSE")
	audio_play(noise)
end

-----------------------------------------------
-- After all the map slides in, this sets up
-- subscrptions and shit
-----------------------------------------------
function pause_map_trans_in_complete()
--	debug_print("vint", "map is loaded\n\n")

	--Desubscribe to the blocked events
	vint_unsubscribe_to_input_event(Pause_map_subscriptions.all_unassigned)

	--Subscribe to controls

	--DPAD (For Filters and switching maps)
	Pause_map_subscriptions.left = vint_subscribe_to_input_event(nil, "dpad_left", "pause_map_input")
	Pause_map_subscriptions.right = vint_subscribe_to_input_event(nil, "dpad_right", "pause_map_input")

	--Map Button (for closing the interface)
	Pause_map_subscriptions.map = vint_subscribe_to_input_event(nil, "map", "pause_map_input")
	Pause_map_subscriptions.back = vint_subscribe_to_input_event(nil, "pad_back", "pause_map_input")

	Pause_map_subscriptions.pause = vint_subscribe_to_input_event(nil, "pause", "pause_map_input")
	--Initialize filters
	pause_map_filter_init()
end

function pause_map_trans_out_complete()
	vint_unsubscribe_to_input_event(Pause_map_subscriptions.all_unassigned)
	if Pause_map_swapping == true then
		pause_menu_swap_with_map(0)
	end

	vint_document_unload(vint_document_find("pause_map"))
end

-- Callback for exit dialog [nclok1405]
function pause_map_exit_confirm(result, action)
	if action == DIALOG_ACTION_CLOSE and result == DIALOG_RESULT_YES then
		pause_map_close()
	end
end

-- Show exit dialog on taxi, or just close the map otherwise [nclok1405]
function pause_map_show_exit_dialog()
	if Pause_map_taxi_mode then
		dialog_box_confirmation("TAXI_TITLE", "TAXI_LEAVE_FULL", "pause_map_exit_confirm")
	else
		pause_map_close()
	end
end

function pause_map_input(target, event, accelleration)
	if event == "dpad_left" then
		local new_index = Pause_map_filter_status.selected_index - 1
		if new_index  < 0 then
			new_index = Pause_map_filter_status.total_filters - 1
		end
		pause_map_filter_change(new_index, true)
	elseif event == "dpad_right" then
		local new_index = Pause_map_filter_status.selected_index + 1
		if new_index  == Pause_map_filter_status.total_filters then
			new_index = 0
		end
		pause_map_filter_change(new_index, true)
	elseif event == "map" then
		--Close the interface
		pause_map_show_exit_dialog()
	elseif event == "pad_back" then
		--Close the interface
		pause_map_show_exit_dialog()
	elseif event == "pause" then
		Pause_map_swapping = true
		pause_map_show_exit_dialog()
	end
end

--------------------------------------------------
--Pause Map Filters
--------------------------------------------------
function pause_map_filter_init()
	--Initialize pause menu filters

	--get current filter mode from the game
	local current_mode = pause_map_filter()
	local current_index = 0

--	debug_print("vint", "current_mode: " .. current_mode .. "\n")

	if current_mode == "PFT_FILTER_LOCKED" then
		pause_map_filter_lock(true)
		return
	end

	for idx, val in Pause_map_filter_status.filters do
		if val.filter == current_mode then
			current_index = idx
			break
		end
	end

	pause_map_filter_change(current_index, false)
end

function pause_map_filter_change(index, set_game_filter)
	local filter_previous = Pause_map_filter_status.filters[Pause_map_filter_status.selected_index]
	local filter = Pause_map_filter_status.filters[index]

	--Highlight Icon
	vint_set_property(filter.bmp_h, "tint", Pause_map_styles.colors.filter_select[1], Pause_map_styles.colors.filter_select[2], Pause_map_styles.colors.filter_select[3])
	vint_set_property(filter.bmp_h, "scale", 1.2, 1.2)

	--If the previous filter is not the current filter then reset the previous state state.
	if filter_previous ~= filter then
		--Deselect Old icon
		vint_set_property(filter_previous.bmp_h, "tint", Pause_map_styles.colors.filter_deselect[1], Pause_map_styles.colors.filter_deselect[2], Pause_map_styles.colors.filter_deselect[3])
		vint_set_property(filter_previous.bmp_h, "scale", 1.0, 1.0)
	end

	--Change Text
	vint_set_property(Pause_map_elements.filters.text_h, "text_tag", Pause_map_filter_status.filters[index].filter_str)

	--Set the game side filter
	if set_game_filter == true then
		pause_map_filter(filter.filter)
	end

	--Store selected index
	Pause_map_filter_status.selected_index = index
end

function pause_map_filter_lock(is_locked)
	if is_locked == true then
		local filter
		for idx, val in Pause_map_filter_status.filters do
			filter = val
			vint_set_property(filter.bmp_h, "tint", Pause_map_styles.colors.filter_disabled[1], Pause_map_styles.colors.filter_disabled[2], Pause_map_styles.colors.filter_disabled[3])
			vint_set_property(filter.bmp_h, "scale", 1.0, 1.0)
		end
		vint_set_property(Pause_map_elements.filters.text_h, "text_tag", "PAUSE_MAP_FILTER_LOCKED")

		--Unsubscribe to inputs
		vint_unsubscribe_to_input_event(Pause_map_subscriptions.left)
		vint_unsubscribe_to_input_event(Pause_map_subscriptions.right)
	else
		local filter
		for idx, val in Pause_map_filter_status.filters do
			vint_set_property(filter.bmp_h, "tint", Pause_map_styles.colors.filter_deselect[1], Pause_map_styles.colors.filter_deselect[2], Pause_map_styles.colors.filter_deselect[3])
			vint_set_property(filter.bmp_h, "scale", 1.0, 1.0)
		end
		pause_map_filter_change(Pause_map_filter_status.selected_index, true)
	end
end


--------------------------------------------------
--Pause Map Button Tips
--------------------------------------------------
function pause_map_btn_tips_format()
	local btn_padding = 0
	local tip_padding = 8

	-- Change select button text to "PURCHASE RIDE" on Taxi [nclok1405]
	if Pause_map_taxi_mode then
		vint_set_property(Pause_map_elements.footer.select_text_h, "text_tag", "TAXI_PURCHASE")
	end

	--hardcoding the formatting because it is fast... yay!
	if mp_is_enabled() == true then
		-- Only show the back button for multiplayer
		vint_set_property(Pause_map_elements.footer.select_btn_h, "visible", false)
		vint_set_property(Pause_map_elements.footer.select_text_h, "visible", false)

		vint_set_property(Pause_map_elements.footer.alt_select_btn_h, "visible", false)
		vint_set_property(Pause_map_elements.footer.alt_select_text_h, "visible", false)

		vint_set_property(Pause_map_elements.footer.left_right_btn_h, "visible", false)
		vint_set_property(Pause_map_elements.footer.left_right_text_h, "visible", false)

		vint_set_property(Pause_map_elements.footer.up_down_btn_h, "visible", false)
		vint_set_property(Pause_map_elements.footer.up_down_text_h, "visible", false)

		local x, y = vint_get_property(Pause_map_elements.footer.select_btn_h, "anchor")
		vint_set_property(Pause_map_elements.footer.back_btn_h, "anchor", x, y)

		x, y = vint_get_property(Pause_map_elements.footer.select_text_h, "anchor")
		vint_set_property(Pause_map_elements.footer.back_text_h, "anchor", x, y)
	else
		-- Format the buttons for single player and coop
		local elements = {
			[0] = {
				btn = Pause_map_elements.footer.select_btn_h,
				txt = Pause_map_elements.footer.select_text_h
			},
			[1] = {
				btn = Pause_map_elements.footer.alt_select_btn_h,
				txt = Pause_map_elements.footer.alt_select_text_h
			},
			[2] = {
				btn = Pause_map_elements.footer.back_btn_h,
				txt = Pause_map_elements.footer.back_text_h
			},
			[3] = {
				btn = Pause_map_elements.footer.left_right_btn_h,
				txt = Pause_map_elements.footer.left_right_text_h
			},
			[4] = {
				btn = Pause_map_elements.footer.up_down_btn_h,
				txt = Pause_map_elements.footer.up_down_text_h
			},
		}

		local w, show
		local x, y = 0, 0

		local prev_element = nil

		for idx = 0, 4 do
			local val = elements[idx]
			if Pause_map_taxi_mode == true and idx == 1 then
				show = false
			elseif idx == 4 then
				show = (Pause_map_underground == true)
			elseif idx == 0 then
				show = (Pause_map_underground ~= true)
			else
				show = true
			end

			if show == true then
				w = element_get_actual_size(val.btn)
				w = w/2
				if prev_element == nil then
					x = vint_get_property(elements[0].btn, "anchor")
				else
					x = x + w
				end

				-- place button
				vint_set_property(val.btn, "anchor", x, y)

				-- place text
				x = x + w + btn_padding
				vint_set_property(val.txt, "anchor", x, y)

				-- find pos for next pass
				w = element_get_actual_size(val.txt)
				x = x + w + tip_padding

				-- unhide elements
				vint_set_property(val.txt, "visible", true)
				vint_set_property(val.btn, "visible", true)
				prev_element = val
			else
				vint_set_property(val.txt, "visible", false)
				vint_set_property(val.btn, "visible", false)
			end
		end

		--Resize button tips if they are too big...
		--720 is the ~width of the cellphone frame
		if x > 720 then
			local scale = 720/x
			vint_set_property(Pause_map_elements.footer.button_tips, "scale", scale, scale)
		end
	end
end

--------------------------------------------------
--Highlight Update
--------------------------------------------------
function anim_out_complete(tween_h)
	for idx, val in Pause_map_highlight_status do
		if val.last_tween_out == tween_h then

			local status = Pause_map_highlight_status[idx]
			vint_object_destroy(status.info_h)
			vint_object_destroy(status.in_anim_h)
			vint_object_destroy(status.out_anim_h)
			vint_object_destroy(status.info_bg_anim_h)
			vint_object_destroy(status.icon_highlight_anim_h)

			Pause_map_highlight_status[idx] = nil
			break
		end
	end
end

function anim_in_complete()
	--debug_print("vint", "anim_in_complete \n")
	Pause_map.done = true
end

function pause_map_highlight_update(di_h)
	--[[
		VINT_PROP_TYPE_STRING,			// icon bitmap name
		VINT_PROP_TYPE_STRING,			// text line 1
		VINT_PROP_TYPE_STRING,			// text line 2
		VINT_PROP_TYPE_STRING,			// text line 3
		VINT_PROP_TYPE_VECTOR2F,		// position
		VINT_PROP_TYPE_BOOL,				// is highlighted
		VINT_PROP_TYPE_BOOL,				// is gps target
	]]

	local icon_bmp_name, text_line_1, text_line_2, text_line_3, position_x, position_y, is_highlighted, is_gps_target = vint_dataitem_get(di_h)

--	debug_print("vint", "icon_bmp_name: " .. 	var_to_string(icon_bmp_name)  .. "\n")
--	debug_print("vint", " di_h: " .. 	var_to_string(di_h)  .. "\n")
--	debug_print("vint", " text_line_1: " .. 	var_to_string(text_line_1) 	 .. "\n")
--	debug_print("vint", " text_line_2: " ..	 	var_to_string(text_line_2)  	 .. "\n")
--	debug_print("vint", " text_line_3: " .. 	var_to_string(text_line_3) 	 .. "\n")
--	debug_print("vint", "x: " .. 		var_to_string(position_x) 	 .. ", ")
--	debug_print("vint", "y: " .. 		var_to_string(position_y) 	 .. "\n")
--	debug_print("vint", " is_highlighted: " .. var_to_string(is_highlighted) .. "\n")
--	debug_print("vint", " is_gps_target: " .. 	var_to_string(is_gps_target)  .. "\n")

	--Exit if there is no icon
	if icon_bmp_name == nil then
		return
	end

	local status = Pause_map_highlight_status[di_h]

	--Check to see if the highlight/info element has been created then initalize the element if it hasn't.
	if status == nil then

		--Clone the object and find targets.
		local info_h = vint_object_clone(Pause_map_elements.base.info_h)
		local icon_h = vint_object_find("icon", info_h)
		local icon_highlight_h = vint_object_find("icon_highlight", info_h)
		local lock_h = vint_object_find("lock", info_h)
		local text_grp_h = vint_object_find("text_grp", info_h)
		local text_line_1_h = vint_object_find("line_1_txt", info_h)
		local text_line_2_h = vint_object_find("line_2_txt", info_h)
		local text_line_3_h = vint_object_find("line_3_txt", info_h)

		--Clone, Retarget, and Pause Animations
		local in_anim_h = vint_object_clone(Pause_map_anims.highlight_anim_in_h)
		local out_anim_h = vint_object_clone(Pause_map_anims.highlight_anim_out_h)
		local info_bg_anim_h = vint_object_clone(Pause_map_anims.info_bg_anim_h)
		local icon_highlight_anim_h = vint_object_clone(Pause_map_anims.icon_highlight_anim_h)
		local last_tween_in = vint_object_find("bg_wrapper_alpha_twn_1", in_anim_h)
		local last_tween_out = vint_object_find("bg_wrapper_alpha_twn_1", out_anim_h)

		vint_set_property(in_anim_h, "is_paused", true)
		vint_set_property(out_anim_h, "is_paused", true)
		vint_set_property(info_bg_anim_h, "is_paused", true)
		vint_set_property(icon_highlight_anim_h, "is_paused", true)
		vint_set_property(in_anim_h, "target_handle", info_h)
		vint_set_property(out_anim_h, "target_handle", info_h)
		vint_set_property(icon_highlight_anim_h, "target_handle", info_h)

		vint_set_property(info_bg_anim_h, "target_handle", vint_object_find("bg_wrapper", info_h))
		vint_set_property(last_tween_in, "end_event", "anim_in_complete")
		vint_set_property(last_tween_out, "end_event", "anim_out_complete")

		Pause_map_highlight_status[di_h] = {
			info_h = info_h,
			in_anim_h = in_anim_h,
			out_anim_h = out_anim_h,
			info_bg_anim_h = info_bg_anim_h,
			icon_highlight_anim_h = icon_highlight_anim_h,
			icon_h = icon_h,
			icon_highlight_h = icon_highlight_h,
			lock_h = lock_h,
			text_grp_h = text_grp_h,
			text_line_1_h = text_line_1_h,
			text_line_2_h = text_line_2_h,
			text_line_3_h = text_line_3_h,
			icon_bmp_name = -1,
			text_line_1 = -1,
			text_line_2 = -1,
			text_line_3 = -1,
			text_width = -1,
			text_height = -1,
			alignment = "left",
			is_highlighted = -1,
			is_gps_target = -1,
			last_tween_in = last_tween_in,
			last_tween_out = last_tween_out,
		}

		status = Pause_map_highlight_status[di_h]
	end

	--Create locals from the status table
	local info_h = status.info_h
	local icon_h = status.icon_h
	local icon_highlight_h = status.icon_highlight_h
	local lock_h = status.lock_h
	local last_tween_in = status.last_tween_in
	local text_line_1_h = status.text_line_1_h
	local text_line_2_h = status.text_line_2_h
	local text_line_3_h = status.text_line_3_h

	--Set Icon bitmap
	if icon_bmp_name ~= status.icon_bmp_name then
		vint_set_property(icon_h, "image", icon_bmp_name)
		vint_set_property(icon_h, "alpha", 0)
		vint_set_property(icon_highlight_h, "image", icon_bmp_name)
		vint_set_property(icon_highlight_h, "alpha", 0)
		status.icon_bmp_name = icon_bmp_name
	end

	vint_set_property(info_h, "anchor", position_x, position_y)			--Set screen coordinate positions
	vint_set_property(info_h, "visible", true)								--show item

	--Adjust angle of the lock on graphic based on the icon name
	if Pause_map_icons_rectangle[icon_bmp_name] == true then
		vint_set_property(lock_h, "rotation", 0)
	else
		vint_set_property(lock_h, "rotation", .78)
	end

	--Update lines of text
	--Initialize alignment variables
	local reset_alignment = false
	local alignment = status.alignment

	--If text tags equal nil then we need to set the string to ""
	if text_line_1 == nil then
		text_line_1 = ""
	end
	if text_line_2 == nil then
		text_line_3 = ""
	end
	if text_line_3 == nil then
		text_line_3 = ""
	end

	if text_line_1 ~= status.text_line_1 or text_line_2 ~= status.text_line_2 or text_line_3 ~= status.text_line_3 then

		--Set text tags
		vint_set_property(text_line_1_h, "text_tag", text_line_1)
		vint_set_property(text_line_2_h, "text_tag", text_line_2)
		vint_set_property(text_line_3_h, "text_tag", text_line_3)

		--Get Largest text width and height
		local text_width = 0
		local text_height = 0
		local temp1_width = element_get_actual_size(text_line_1_h)
		local temp2_width = element_get_actual_size(text_line_2_h)
		local temp3_width = element_get_actual_size(text_line_3_h)

		if temp1_width > text_width then
			text_width = temp1_width
		end
		if temp2_width > text_width then
			text_width = temp2_width
		end
		if temp3_width > text_width then
			text_width = temp3_width
		end

		if text_width ~= status.text_width then
			--Set the reset alignment if the text has changed widths
			reset_alignment = true
		end

		--Do text height based on the line count
		if text_line_2 == nil then
			text_height = 40
		elseif text_line_3 == nil then
			text_height = 60
		end

		--Store values
		status.text_width = text_width
		status.text_height = text_height
		status.text_line_1 = text_line_1
		status.text_line_2 = text_line_2
		status.text_line_3 = text_line_3
	end

	if reset_alignment == true then
		local text_offset = 40	--Aprox offset from the center point of the box
		local map_obj_h = vint_object_find("pause_map")	--Get map object
		local box_width = vint_get_property(map_obj_h, "scale")									--use scale instead of screensize because it is the actual size

		if position_x + status.text_width + text_offset > box_width then
			alignment = "right"
		end

		local target_anchor = floor(status.text_width + text_offset)
		local target_c_scale = (target_anchor / 45.0000)

		--Apply sizing directions to both sides of the tween
		local left_c_scale_twn_h = vint_object_find("left_c_scale_twn", status.info_bg_anim_h)
		local right_c_scale_twn_h = vint_object_find("right_c_scale_twn", status.info_bg_anim_h)
		local left_e_anchor_twn_h = vint_object_find("left_e_anchor_twn", status.info_bg_anim_h)
		local right_w_anchor_twn_h = vint_object_find("right_w_anchor_twn", status.info_bg_anim_h)

		vint_set_property(left_c_scale_twn_h, "end_value", target_c_scale, 1 )
		vint_set_property(right_c_scale_twn_h, "end_value", target_c_scale, 1 )
		vint_set_property(left_e_anchor_twn_h, "end_value", target_anchor, 0)
		vint_set_property(right_w_anchor_twn_h, "end_value", 0 - target_anchor, 0)

		if alignment == "right" then
			--RIGHT ALIGNMENT
			vint_set_property(status.text_grp_h, "anchor", -31, -30)			--Set text group anchor
			vint_set_property(status.text_line_1_h, "auto_offset", "ne")	--Adjust Text Alignment
			vint_set_property(status.text_line_2_h, "auto_offset", "ne")	--Adjust Text Alignment
			vint_set_property(status.text_line_3_h, "auto_offset", "ne")	--Adjust Text Alignment

			vint_set_property(vint_object_find("bg_left", status.info_h), "visible", false)	--Hide left aligned bg
			vint_set_property(vint_object_find("bg_right", status.info_h), "visible", true)	--Show right aligned bg

		else
			--LEFT ALIGNMENT
			vint_set_property(status.text_grp_h, "anchor", 25, -30)			--Set text group anchor
			vint_set_property(status.text_line_1_h, "auto_offset", "nw")	--Adjust Text Alignment
			vint_set_property(status.text_line_2_h, "auto_offset", "nw")	--Adjust Text Alignment
			vint_set_property(status.text_line_3_h, "auto_offset", "nw")	--Adjust Text Alignment

			vint_set_property(vint_object_find("bg_left", status.info_h), "visible", true)	--Show left aligned bg
			vint_set_property(vint_object_find("bg_right", status.info_h), "visible", false)	--Hide left aligned bg
		end

		if alignment ~= status.alignment then
			status.alignment = alignment
		end
	end

	--If the highlighted item changes state the we need to change how it is displayed
	if is_highlighted ~= status.is_highlighted then

		--1. Check if we need to fade in or fade out the info box
		if is_highlighted == true then
			--Reset elements
			vint_set_property(vint_object_find("bg_wrapper",info_h), "alpha", 0)
			vint_set_property(status.text_grp_h, "alpha", 0)
			vint_set_property(status.out_anim_h, "is_paused", true)	--Pause the out animation
			lua_play_anim(status.in_anim_h, 0)								--Play in animation
			lua_play_anim(status.info_bg_anim_h, 0)
			lua_play_anim(status.icon_highlight_anim_h, 0)
			Pause_map.done = false
		elseif is_highlighted == false then
			--if the fade in tweens are done, then its ok to fade them out
			if Pause_map.done == true then
				vint_set_property(status.in_anim_h, "is_paused", true)	--Pause the in animation
				local alpha = vint_get_property(status.text_grp_h, "alpha")
				vint_set_property(vint_object_find("txt_grp_alpha_twn_1",status.out_anim_h), "start_value", alpha)
				lua_play_anim(status.out_anim_h, 0)
			else
				--if fade in tweens arent finished, just destroy them
				vint_object_destroy(status.info_h)
				vint_object_destroy(status.in_anim_h)
				vint_object_destroy(status.out_anim_h)
				vint_object_destroy(status.info_bg_anim_h)
				vint_object_destroy(status.icon_highlight_anim_h)

				Pause_map_highlight_status[di_h] = nil
			end
		end

		status.is_highlighted = is_highlighted

		--2. Fade the cursor if highlight and cursor state have changed
		local is_active = false
		for idx, val in Pause_map_highlight_status do
			if val.is_highlighted == true then
				is_active = true
				break
			end
		end

		if is_active == true then
			if Pause_map_cursor_status.fade_mode == "in" then
				--Fade out Cursor
				local current_alpha = vint_get_property(Pause_map_elements.base.cursor_h, "alpha")
				vint_set_property(Pause_map_anims.cursor_fade_twn_h, "start_value", current_alpha)
				vint_set_property(Pause_map_anims.cursor_fade_twn_h, "end_value", 0)
				lua_play_anim(Pause_map_anims.cursor_fade_anim_h, 0)
				Pause_map_cursor_status.fade_mode = "out"
			end
		else
			if Pause_map_cursor_status.fade_mode == "out" then
				--Fade In Cursor
				local current_alpha = vint_get_property(Pause_map_elements.base.cursor_h, "alpha")
				vint_set_property(Pause_map_anims.cursor_fade_twn_h, "start_value", current_alpha)
				vint_set_property(Pause_map_anims.cursor_fade_twn_h, "end_value", 1)
				lua_play_anim(Pause_map_anims.cursor_fade_anim_h, 0)
				Pause_map_cursor_status.fade_mode = "in"
			end
		end
	end

	if is_gps_target == true then
		vint_set_property(lock_h, "tint", 0,1,0)
	else
		vint_set_property(lock_h, "tint", 1,1,1)
	end
end

function pause_map_cursor_update(di_h)
	--[[
      VINT_PROP_TYPE_VECTOR2F,	// cursor pos
      VINT_PROP_TYPE_BOOL,			// gps active
      VINT_PROP_TYPE_STRING,		// district name
      VINT_PROP_TYPE_STRING,		// hood name
	]]
	local cursor_x, cursor_y, gps_active, district_str, hood_str, is_underground = vint_dataitem_get(di_h)

	vint_set_property(Pause_map_elements.base.cursor_h, "anchor", cursor_x, cursor_y)
	Pause_map_cursor_status.x = cursor_x
	Pause_map_cursor_status.y = cursor_y

	--Update district/hood text
	vint_set_property(Pause_map_elements.header.hood_text_h, "text_tag", district_str)
	vint_set_property(Pause_map_elements.header.district_text_h, "text_tag", hood_str)

	--Update button tips
	if gps_active ~= Pause_map_cursor_status.gps_active or is_underground ~= Pause_map_underground then
		if gps_active == true then
			--LOCALIZE:
			vint_set_property(Pause_map_elements.footer.select_text_h, "text_tag", "PAUSE_MAP_WAYPOINT_REMOVE")
		else
			vint_set_property(Pause_map_elements.footer.select_text_h, "text_tag", "PAUSE_MAP_WAYPOINT_SET")
		end
		--Reformat button tips because the text has been updated
		Pause_map_underground = is_underground
		Pause_map_cursor_status.gps_active = gps_active
		pause_map_btn_tips_format()
	end
end
