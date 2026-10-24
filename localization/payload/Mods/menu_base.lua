-- menu_base.lua: Menu System
-------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------
-- MENU DATA

MENU_TRANSITION_NONE				= 0
MENU_TRANSITION_SWAP				= 1
MENU_TRANSITION_SWEEP_RIGHT	= 2
MENU_TRANSITION_SWEEP_LEFT		= 3

MENU_ITEM_TYPE_SUB_MENU 		= 0
MENU_ITEM_TYPE_SELECTABLE 		= 1
MENU_ITEM_TYPE_NUM_SLIDER 		= 2
MENU_ITEM_TYPE_TEXT_SLIDER 	= 3
MENU_ITEM_TYPE_GRID 				= 4
MENU_ITEM_TYPE_PALETTE 			= 5
MENU_ITEM_TYPE_INFO_BOX 		= 6
MENU_ITEM_TYPE_MARQUEE			= 7

MENU_MIN_LABEL_W = 100
MENU_MIN_MENU_W = 238
MENU_MAX_MENU_H = 375
MENU_CONTROL_W = 220
MENU_ITEM_HEIGHT = 32
MENU_BASE_DOC_HANDLE = 0
MENU_SWATCH_DEFAULT_ROW_HEIGHT = 69
MENU_SWATCH_DEFAULT_COL_WIDTH = 78

MENU_FOOTER_CASH_BROKE_COLOR = {["R"] = 0.8, ["G"] = 0, ["B"] = 0} 				--RED
MENU_FOOTER_CASH_NORMAL_COLOR = {["R"] = 0.88, ["G"] = 0.749, ["B"] = 0.05}	--YELLOW

MENU_MARQUEE_SPEED = 0.009				--	Multiplier for how fast it goes. Closer to 0 this gets, the faster it gets
MENU_MARQUEE_DELAY = 0.5				-- Delay between pausing and restarting
MENU_MARQUEE_SCROLL_CORRECTION = 7	--	For adjusting how long it is for it to scroll. The smaller this number, the longer the line can be.

INVALID_PALETTE_INDEX = -1

Menu_palette_stored_index = INVALID_PALETTE_INDEX

Menu_scaler = 1
Menu_active_anchor_end_x = 0
Menu_active_anchor_end_y = 0
Menu_horz_label_clip_x = 0
Menu_horz_label_clip_y = 0

Menu_fade_to_black = false
Menu_input_blocked = 0
Menu_new = false
Menu_active = 0
Menu_inactive = 0
Menu_horz_active = 0
Menu_close_cb = 0
Menu_input_accelleration = 1
Menu_use_hud = false
Menu_option_labels = { }
Menu_option_labels_inactive = { }

Menu_nav_bars = {}
Menu_transition_data = { tweens = { } }
Menu_fading_label = 0
Menu_marquee_info = { }

Menu_anims = {}				--Handles to cloned animations
Menu_trans_in_twns = {}		--Handles to menu transition tweens (IN)
Menu_trans_out_twns = {}	--Handles to menu transition tweens (OUT)
Menu_input_subscriptions = {}

--Threads
Menu_horz_update_label_thread = -1

Menu_transition_in_progress = false
Menu_swap_center = false
Menu_hud_hidden = false

function menu_base_init()
	MENU_BASE_DOC_HANDLE = vint_document_find("menu_base")
	vint_set_property(vint_object_find("menu_trans_in",  		nil, MENU_BASE_DOC_HANDLE), "is_paused", true)
	vint_set_property(vint_object_find("menu_trans_out", 		nil, MENU_BASE_DOC_HANDLE), "is_paused", true)
	vint_set_property(vint_object_find("cash_trans_in",  		nil, MENU_BASE_DOC_HANDLE), "is_paused", true)
	vint_set_property(vint_object_find("cash_trans_out",  		nil, MENU_BASE_DOC_HANDLE), "is_paused", true)
	vint_set_property(vint_object_find("menu_horz_lt_anim", 	nil, MENU_BASE_DOC_HANDLE), "is_paused", true)
	vint_set_property(vint_object_find("menu_horz_rt_anim", 	nil, MENU_BASE_DOC_HANDLE), "is_paused", true)
	vint_set_property(vint_object_find("menu_horz_up_anim", 	nil, MENU_BASE_DOC_HANDLE), "is_paused", true)
	vint_set_property(vint_object_find("menu_horz_dn_anim", 	nil, MENU_BASE_DOC_HANDLE), "is_paused", true)
	vint_set_property(vint_object_find("swap_message_trans_in", nil, MENU_BASE_DOC_HANDLE), "is_paused", true)
	vint_set_property(vint_object_find("swap_message_trans_out",nil, MENU_BASE_DOC_HANDLE), "is_paused", true)
	vint_set_property(vint_object_find("black_fade_out", 		nil, MENU_BASE_DOC_HANDLE) , "is_paused", true)
	vint_set_property(vint_object_find("menu_btn_tips_anim", 		nil, MENU_BASE_DOC_HANDLE) , "is_paused", true)
end

-- calls release function for this control type
function menu_release_control(control)
	local cb = Menu_control_callbacks[control.type]

	if cb.on_release ~= nil then
		cb.on_release(control)
	end
end

function menu_num_slider_on_enter(menu_label, menu_data)
	if menu_label.control.is_highlighted == false then
		local g = menu_label.control.grp_h
		vint_set_property(vint_object_find("large_thumb", g), "visible", true)
		vint_set_property(vint_object_find("small_thumb", g), "visible", true)
		vint_set_property(menu_label.control.grp_h, "depth", 0)
		vint_set_property(vint_object_find("num_slider_arrow_e", g), "tint", 0.8941, 0.8489, 0.051)
		vint_set_property(vint_object_find("num_slider_arrow_w", g), "tint", 0.8941, 0.8489, 0.051)
		menu_label.control.is_highlighted = true

		menu_label.input1 = vint_subscribe_to_input_event(nil, "nav_right", "menu_num_slider_nav_right", 5)
		vint_set_input_params(menu_label.input1, MENU_NUM_SLIDER_ACCEL_REPEAT, MENU_NUM_SLIDER_ACCEL_FACTOR, MENU_NUM_SLIDER_ACCEL_LIMIT, true)
		menu_label.input2 = vint_subscribe_to_input_event(nil, "nav_left", "menu_num_slider_nav_left", 5)
		vint_set_input_params(menu_label.input2, MENU_NUM_SLIDER_ACCEL_REPEAT, MENU_NUM_SLIDER_ACCEL_FACTOR, MENU_NUM_SLIDER_ACCEL_LIMIT, true)

		--Anim in
		menu_label.control.anim_in_h = vint_object_clone(vint_object_find("menu_num_slider_in_anim"))
		vint_set_property(menu_label.control.anim_in_h, "target_handle", g)
		lua_play_anim(menu_label.control.anim_in_h, 0)

		--Trigger pulsing animation
		menu_label.control.anim_pulse_h = vint_object_clone(vint_object_find("menu_num_slider_pulse_anim"))
		vint_set_property(menu_label.control.anim_pulse_h, "target_handle", g)
		lua_play_anim(menu_label.control.anim_pulse_h, 0)
	end
end

function menu_num_slider_on_leave(menu_label, menu_data)
	if menu_label.control.is_highlighted == true then

		--Destroy animations
		if menu_label.control.anim_in_h ~= nil then
			vint_object_destroy(menu_label.control.anim_in_h)
		end
		if menu_label.control.anim_pulse_h ~= nil then
			vint_object_destroy(menu_label.control.anim_pulse_h)
		end

		local g = menu_label.control.grp_h
		vint_set_property(vint_object_find("num_slide_bg_1_left", g), "alpha", 1)
		vint_set_property(vint_object_find("num_slide_bg_1_right", g), "alpha", 1)
		vint_set_property(vint_object_find("num_slide_bg_2_right", g), "alpha", 0)
		vint_set_property(vint_object_find("num_slide_bg_2_left", g), "alpha", 0)

		vint_set_property(vint_object_find("large_thumb", g), "alpha", 0)
		vint_set_property(vint_object_find("small_thumb", g), "alpha", 1)
		vint_set_property(vint_object_find("small_thumb", g), "scale", 1, 1)
		vint_set_property(menu_label.control.grp_h, "depth", menu_label.depth)
		vint_set_property(vint_object_find("value_text", g), "scale", 0.68, 0.68)
		local arrow_e_h = vint_object_find("num_slider_arrow_e", g)
		local arrow_w_h = vint_object_find("num_slider_arrow_w", g)
		vint_set_property(arrow_e_h, "tint", 0.3647, 0.3725, 0.3804)
		vint_set_property(arrow_w_h, "tint", 0.3647, 0.3725, 0.3804)
		vint_set_property(arrow_e_h, "offset", -11, -15)
		vint_set_property(arrow_w_h, "offset", -11, -15)

		menu_label.control.is_highlighted = false

		if menu_label.input1 ~= nil then
			vint_unsubscribe_to_input_event(menu_label.input1)
			vint_unsubscribe_to_input_event(menu_label.input2)
			menu_label.input1 = nil
			menu_label.input2 = nil
		end
	end
end

function menu_num_slider_nav_left(target, event, accelleration)
	local menu_label = Menu_option_labels[Menu_active.highlighted_item - Menu_active.first_vis_item]
	local menu_data = Menu_active[Menu_active.highlighted_item]

	if menu_input_is_blocked() then
		return
	end

	if menu_data.cur_value > 0 then
		local delta = 0.01 * accelleration
		if delta > 0.03 then delta = 0.03 end
		menu_data.cur_value = menu_data.cur_value - delta

		if menu_data.cur_value < 0 then
			menu_data.cur_value = 0
		end

		audio_play(Menu_sound_value_nav)
		menu_num_slider_update_value(menu_label, menu_data)
	end
end

function menu_num_slider_nav_right(target, event, accelleration)
	local menu_label = Menu_option_labels[Menu_active.highlighted_item - Menu_active.first_vis_item]
	local menu_data = Menu_active[Menu_active.highlighted_item]

	if menu_input_is_blocked() then
		return
	end

	if menu_data.cur_value < 1 then
		local delta = 0.01 * accelleration
		if delta > 0.03 then delta = 0.03 end
		menu_data.cur_value = menu_data.cur_value + delta

		if menu_data.cur_value > 1 then
			menu_data.cur_value = 1
		end

		audio_play(Menu_sound_value_nav)
		menu_num_slider_update_value(menu_label, menu_data)
	end
end

function menu_num_slider_update_value(menu_label, menu_data)
	local left = 30 + (183 - menu_data.thumb_width) * menu_data.cur_value

	local h = vint_object_find("all_thumbs", menu_label.control.grp_h)
	vint_set_property(h, "anchor", left, 0)

	if menu_data.on_value_update ~= nil then
		-- this is the user callback
		menu_data.on_value_update(menu_label, menu_data)
	end
end

function menu_num_slider_show(menu_label, menu_data)
	local control = menu_label.control

	if control ~= nil then
		if control.type ~= MENU_ITEM_TYPE_NUM_SLIDER then
			-- this isn't a MENU_ITEM_TYPE_NUM_SLIDER so release it
			menu_release_control(control)
			control = nil
		end
	end

	if control == nil then
		local control_h = vint_object_clone(vint_object_find("menu_number_slider", Menu_option_labels.control_parent))
		control = { grp_h = control_h, type = MENU_ITEM_TYPE_NUM_SLIDER, is_highlighted = true }
	end

	menu_label.control = control

	vint_set_property(control.grp_h, "visible", true)
	vint_set_property(control.grp_h, "anchor", menu_label.anchor_x + Menu_option_labels.max_label_w + 5,
		menu_label.anchor_y)
	vint_set_property(control.grp_h, "depth", menu_label.depth)
	menu_num_slider_update_value(menu_label, menu_data)
	local h = vint_object_find("value_text", control.grp_h)
	vint_set_property(h, "anchor", menu_data.thumb_width * 0.5 -2, 0)

	-- position the thumb elements
	h = vint_object_find("large_thumb_bg", control.grp_h)
	vint_set_property(h, "source_se", menu_data.thumb_width - 5, 45)
	h = vint_object_find("large_thumb_bg_hl", control.grp_h)
	vint_set_property(h, "source_se", menu_data.thumb_width - 5, 45)

	h = vint_object_find("large_thumb_ns", control.grp_h)
	vint_set_property(h, "source_se", menu_data.thumb_width - 24, 69)
	h = vint_object_find("large_thumb_e", control.grp_h)
	vint_set_property(h, "anchor", menu_data.thumb_width - 14, -32)

	h = vint_object_find("small_thumb_bg", control.grp_h)
	vint_set_property(h, "source_se", menu_data.thumb_width - 5, 45)
	h = vint_object_find("small_thumb_ns", control.grp_h)
	vint_set_property(h, "source_se", menu_data.thumb_width - 22, 69)
	h = vint_object_find("small_thumb_e", control.grp_h)
	vint_set_property(h, "anchor", menu_data.thumb_width - 12, -22)
end

function menu_num_slider_release(control)
	vint_object_destroy(control.grp_h)
end

function menu_control_on_select(menu_label, menu_data)
	if menu_data.on_select ~= nil then
		menu_data.on_select(menu_label, menu_data)
	end
end

function menu_submenu_on_select(menu_label, menu_data)
	if menu_data.on_select ~= nil then
		menu_data.on_select(menu_label, menu_data)
	end

	if menu_data.sub_menu ~= nil then
		menu_data.sub_menu.parent_menu = Menu_active
		menu_show(menu_data.sub_menu, MENU_TRANSITION_SWEEP_LEFT)
	end
end

function menu_grid_update_swatches(menu_data, focus_row)
	local num_vis_rows = menu_data.visible_rows

	local first_vis_row = 0

	if focus_row < 2 then
		first_vis_row = 0
	elseif focus_row >= menu_data.total_rows - 1 then
		first_vis_row = menu_data.total_rows - menu_data.visible_rows
	elseif focus_row < menu_data.first_vis_row + 1 then
		first_vis_row = focus_row - 1
	elseif focus_row >= menu_data.first_vis_row + menu_data.visible_rows - 1 then
		first_vis_row = focus_row - num_vis_rows + 2
	else
		return
	end

	if first_vis_row == menu_data.first_vis_row then
		return
	end

	local last_vis_row = first_vis_row + num_vis_rows - 1

	local idx = 0
	local row, col = 0, 0
	local swatch_id
	local pos_x, pos_y
	local swatches = menu_data.swatches
	local swatch_bin = swatches.swatch_bin

	-- recycle any unused swatch clusters
	while idx < swatches.num_swatches do
		if row < first_vis_row or row > last_vis_row then
			if swatches[idx].swatch_h ~= nil then
				swatch_id = swatches[idx].swatch_h
				swatch_bin[swatch_id] = true
				vint_set_property(swatch_id, "visible", false)
				vint_set_property(swatch_id, "depth", 10 - row)
				swatches[idx].swatch_h = nil
			end
		end

		idx = idx + 1
		col = col + 1
		if col >= menu_data.num_cols then
			col = 0
			row = row + 1
		end
	end

	local offset_v = menu_data.offset_v + 3
	local offset_h = menu_data.offset_h + menu_data.col_width * 0.5
	local icon_h = 0

	row, col, idx = 0, 0, 0
	while idx < swatches.num_swatches do
		if row >= first_vis_row and row <= last_vis_row then
			local swatch = swatches[idx]

			if swatch.swatch_h == nil then
				for key, value in swatch_bin do
					-- pull a swatch from the recycle bin
					swatch.swatch_h = key
					swatch.swatch_bg_h = vint_object_find("bg", key)
					swatch_bin[key] = nil
					break
				end
			end

			if swatch.swatch_h ~= nil then
				swatch_id = swatch.swatch_h
				pos_x = col * menu_data.col_width + offset_h
				pos_y = (row - first_vis_row) * menu_data.row_height + offset_v
				vint_set_property(swatch_id, "visible", true)

				if swatch.swatch_crc ~= nil then
					vint_set_property(vint_object_find("icon", swatch_id), "image_crc", swatch.swatch_crc)
				elseif swatch.swatch_str ~= nil then
					vint_set_property(vint_object_find("icon", swatch_id), "image", swatch.swatch_str)
				end

				vint_set_property(swatch_id, "anchor", pos_x, pos_y)
				vint_set_property(swatch_id, "scale", menu_data.unhighlight_scale, menu_data.unhighlight_scale)

				vint_set_property(swatch.swatch_bg_h, "tint", .75, .75, .75)

				-- allow custom tweaking
				if menu_data.update_swatch ~= nil then
					menu_data.update_swatch(swatch, row, col, idx)
				end
			end
		end

		idx = idx + 1
		col = col + 1
		if col >= menu_data.num_cols then
			col = 0
			row = row + 1
		end
	end

	menu_data.first_vis_row = first_vis_row
	menu_scroll_bar_set_thumb_pos(first_vis_row / (menu_data.total_rows - menu_data.visible_rows))
end

function menu_grid_update_highlighted(menu_data, new_col, new_row)
	--move the grid to the appropriate place
	menu_grid_update_swatches(menu_data, new_row)

	local swatches = menu_data.swatches
	local new_idx = new_row * menu_data.num_cols + new_col

	if new_idx >= swatches.num_swatches then
		return
	end

	local cur_idx = menu_data.cur_row * menu_data.num_cols + menu_data.cur_col
	local new_idx = new_row * menu_data.num_cols + new_col

	--Animate highlighted swatch in
	--Find, Retarget, set values, and play
	local swatch_anim_h = vint_object_find("menu_swatch_in_anim")
	local swatch_twn_h = vint_object_find("swatch_general_scale_twn_1", swatch_anim_h)
	vint_set_property(swatch_twn_h, "target_handle", swatches[new_idx].swatch_h)
	vint_set_property(swatch_twn_h, "end_value", menu_data.highlight_scale, menu_data.highlight_scale)
	lua_play_anim(swatch_anim_h, 0)

	--Move the depth of highlighted swatch to bring it to front
	vint_set_property(swatches[new_idx].swatch_h, "depth", -20)

	--Tint background
	vint_set_property(swatches[new_idx].swatch_bg_h, "tint", 1, 1, 1)

	--Now reset last swatch
	if cur_idx ~= new_idx then
		vint_set_property(swatches[cur_idx].swatch_h, "scale", menu_data.unhighlight_scale, menu_data.unhighlight_scale)
		vint_set_property(swatches[cur_idx].swatch_h, "depth", 10 - menu_data.cur_row)

		vint_set_property(swatches[cur_idx].swatch_bg_h, "tint", .75, .75, .75)

		if menu_data.on_leave ~= nil then
			menu_data.on_leave(swatches[cur_idx])
		end
	end

	-- Arrow stuff [nclok1405]
	if not menu_data.hide_arrows then
		local pos_x = new_col * menu_data.col_width + menu_data.offset_h + menu_data.col_width * 0.5
		local pos_y = (new_row - menu_data.first_vis_row) * menu_data.row_height + menu_data.offset_v + 3
		vint_set_property(menu_data.arrow_grp, "anchor", pos_x, pos_y)

		--	Hide the left arrow
		if new_col == 0 then
			vint_set_property(menu_data.arrow_w_h, "visible", false)
		else
			vint_set_property(menu_data.arrow_w_h, "visible", true)
		end
		-- Hide the top arrow
		if new_row == 0 then
			vint_set_property(menu_data.arrow_n_h, "visible", false)
		else
			vint_set_property(menu_data.arrow_n_h, "visible", true)
		end
		-- Hide the right arrow
		local next_swatch_idx = new_row * menu_data.num_cols + (new_col + 1)
		if new_col == menu_data.num_cols - 1 or swatches.num_swatches == 1 or next_swatch_idx >= swatches.num_swatches then
			vint_set_property(menu_data.arrow_e_h, "visible", false)
		else
			vint_set_property(menu_data.arrow_e_h, "visible", true)
		end
		-- Hide the bottom arrow
		next_swatch_idx = (new_row + 1) * menu_data.num_cols + new_col
		if new_row == menu_data.total_rows - 1 or next_swatch_idx >= swatches.num_swatches then
			vint_set_property(menu_data.arrow_s_h, "visible", false)
		else
			vint_set_property(menu_data.arrow_s_h, "visible", true)
		end
	end

	--If the grid is suppose to pulse then do it...
	if menu_data.pulse_swatch == true then

		--Clear out the cloned highlights and pulsing
		if menu_data.swatch_highlight_h ~= nil then
			vint_object_destroy(menu_data.swatch_highlight_h)
		end
		if menu_data.swatch_highlight_anim_h ~= nil then
			vint_object_destroy(menu_data.swatch_highlight_anim_h)
		end

		--Create pulsing animations
		local root_anim = vint_object_find("root_animation")

		--Retrigger Arrow Anim
		if not menu_data.hide_arrows then
			local arrow_anim_h = vint_object_find("menu_swatch_arrows_pulse_anim")
			lua_play_anim(arrow_anim_h, 0)
		end

		--Play pulsing animation
		local ico_h = vint_object_find("icon", swatches[new_idx].swatch_h)

		if ico_h ~= 0 then
			local swatch_highlight_h = vint_object_clone(ico_h)
			local swatch_depth = vint_get_property(ico_h, "depth")
			vint_set_property(swatch_highlight_h, "depth", swatch_depth - 1)
			vint_set_property(swatch_highlight_h, "render_mode", "additive_alpha")

			local swatch_highlight_anim_h = vint_object_clone(vint_object_find("menu_swatch_icon_pulse_anim"), root_anim)
			local twn_h = vint_object_find("icon_highlight_alpha_twn_1", swatch_highlight_anim_h)
			vint_set_property(twn_h, "target_handle", swatch_highlight_h)
			vint_set_property(twn_h, "target_property", "alpha")
			vint_set_property(twn_h, "state", 1)
			lua_play_anim(swatch_highlight_anim_h, 0)

			menu_data.swatch_highlight_h = swatch_highlight_h
			menu_data.swatch_highlight_anim_h = swatch_highlight_anim_h
		end
	end

	-- update footer text
	if swatches[new_idx].label_crc ~= nil then
		vint_set_property(menu_data.footer_txt_h, "text_tag_crc", swatches[new_idx].label_crc)
	elseif swatches[new_idx].label_str ~= nil then
		vint_set_property(menu_data.footer_txt_h, "text_tag", swatches[new_idx].label_str)
	else
		vint_set_property(menu_data.footer_txt_h, "text_tag", "")
	end

	menu_data.cur_row = new_row
	menu_data.cur_col = new_col
	menu_data.cur_idx = new_idx
	menu_data.prev_idx = cur_idx

	if menu_data.on_enter ~= nil then
			menu_data.on_enter(swatches[new_idx])
	end
end

function menu_grid_nav_left(menu_label, menu_data)
	local swatches = menu_data.swatches
	local col = menu_data.cur_col
	if col == 0 then
		col = menu_data.num_cols - 1
	else
		col = col - 1
	end

	if menu_data.cur_row * menu_data.num_cols + col >= swatches.num_swatches then
		col = swatches.num_swatches - 1 - (menu_data.num_cols * (menu_data.total_rows - 1))
	end

	menu_grid_update_highlighted(menu_data, col, menu_data.cur_row)
	audio_play(Menu_sound_value_nav)

	if menu_data.on_nav ~= nil then
		menu_data.on_nav(menu_label, menu_data)
	end
end

function menu_grid_nav_right(menu_label, menu_data)
	local swatches = menu_data.swatches
	local col = menu_data.cur_col
	if col == menu_data.num_cols - 1 then
		col = 0
	else
		col = col + 1
	end

	if menu_data.cur_row * menu_data.num_cols + col >= swatches.num_swatches then
		col = 0
	end

	menu_grid_update_highlighted(menu_data, col, menu_data.cur_row)
	audio_play(Menu_sound_value_nav)

	if menu_data.on_nav ~= nil then
		menu_data.on_nav(menu_label, menu_data)
	end
end

function menu_grid_nav_up(menu_label, menu_data)
	local swatches = menu_data.swatches
	local row = menu_data.cur_row
	if row == 0 then
		row = menu_data.total_rows - 1
	else
		row = row - 1
	end

	if row * menu_data.num_cols + menu_data.cur_col >= swatches.num_swatches then
		row = menu_data.total_rows - 2
	end

	menu_grid_update_swatches(menu_data, row)
	menu_grid_update_highlighted(menu_data, menu_data.cur_col, row)
	audio_play(Menu_sound_item_nav)
	if menu_data.on_nav ~= nil then
		menu_data.on_nav(menu_label, menu_data)
	end
end

function menu_grid_nav_down(menu_label, menu_data)
	local swatches = menu_data.swatches
	local row = menu_data.cur_row
	if row == menu_data.total_rows - 1 then
		row = 0
	else
		row = row + 1
	end

	if row * menu_data.num_cols + menu_data.cur_col >= swatches.num_swatches then
		row = 0
	end

	menu_grid_update_swatches(menu_data, row)
	menu_grid_update_highlighted(menu_data, menu_data.cur_col, row)
	audio_play(Menu_sound_item_nav)

	if menu_data.on_nav ~= nil then
		menu_data.on_nav(menu_label, menu_data)
	end
end

function menu_grid_get_width(menu_data)
	local w = menu_data.col_width * menu_data.num_cols
	if menu_data.scroll_bar_visible == true then
		w = w + 25
	end
	return w - 1
end

function menu_grid_get_height(menu_data)
	return menu_data.row_height * menu_data.visible_rows
end

function menu_grid_release(menu_data)
	local swatches = menu_data.swatches

	for i = 0, swatches.num_swatches - 1 do
		if swatches[i].swatch_h ~= nil then
			vint_object_destroy(swatches[i].swatch_h)
			swatches[i].swatch_h = nil
		end
	end

	--Destroy highlights
	if menu_data.swatch_highlight_h  ~= nil then
		vint_object_destroy(menu_data.swatch_highlight_h)
	end
	if menu_data.swatch_highlight_anim_h ~= nil then
		vint_object_destroy(menu_data.swatch_highlight_anim_h)
	end

	for key, value in menu_data.swatches.swatch_bin do
		vint_object_destroy(key)
	end

	menu_data.swatches = nil

	if menu_data.arrow_grp ~= nil then
		vint_object_destroy(menu_data.arrow_grp)
	end

	local footer = menu_data.footer

	if footer ~= nil and footer.footer_grp ~= nil then
		vint_object_destroy(footer.footer_grp)
	end

	menu_data.arrow_grp = nil
	menu_data.footer = nil
	menu_data.cur_idx = nil
end

-- do_not_animate: true to disable the default pulse animations
-- no_arrows: true to disable arrows [nclok1405]
function menu_grid_show(menu_data, menu_item, master_swatch_h, do_not_animate, no_arrows)

	if master_swatch_h == nil then
		master_swatch_h = vint_object_find("swatch_general", nil, MENU_BASE_DOC_HANDLE)
		menu_item.custom_swatch = false
	else
		menu_item.custom_swatch = true
	end

	if do_not_animate == true then
		--No animations for this swatch
		menu_item.pulse_swatch = false
	else
		--Do the pulsing animation by default
		menu_item.pulse_swatch = true
	end

	if no_arrows == true then
		--No arrows for this swatch [nclok1405]
		menu_item.hide_arrows = true
	end

	local swatches = menu_item.swatches
	swatches.swatch_bin = { }
	local swatch_bin = swatches.swatch_bin

	if menu_data.max_height == nil then
		menu_data.max_height = MENU_MAX_MENU_H
	end

	local max_rows = floor(menu_data.max_height / menu_item.row_height)
	local total_rows = swatches.num_swatches / menu_item.num_cols

	if floor(total_rows) ~= total_rows then
		total_rows = floor(total_rows) + 1
	end

	local visible_rows = total_rows
	if visible_rows > max_rows then
		visible_rows = max_rows
	end

	if menu_item.cur_idx ~= nil then
		menu_item.cur_row = floor(menu_item.cur_idx / menu_item.num_cols)
		menu_item.cur_col = menu_item.cur_idx - (menu_item.cur_row * menu_item.num_cols)
		menu_item.cur_idx = nil
	else
		menu_item.cur_row = 0
		menu_item.cur_col = 0
	end

	menu_item.first_vis_row = -1
	menu_item.visible_rows = visible_rows
	menu_item.total_rows = total_rows

	-- offset used in a couple of places
	local offset_h = 21

	--[[	this use of Menu_active seemed suspicious so i replaced it with below 2008.05.30 SDR
	local offset_v = 60 + menu_item.row_height * 0.5
	if Menu_active ~= 0 then
		offset_v =  Menu_active.header_height + menu_item.row_height * 0.5
	end ]]

	local offset_v = menu_data.header_height + menu_item.row_height * 0.5

	menu_item.offset_h = offset_h
	menu_item.offset_v = offset_v

	-- build up the swatch objects
	local max_swatches = visible_rows * menu_item.num_cols

	if max_swatches > swatches.num_swatches then
		max_swatches = swatches.num_swatches
	end

	local swatch_id
	local parent_h = Menu_option_labels.control_parent
	for i = 0, max_swatches - 1 do
		swatch_id = vint_object_clone(master_swatch_h, parent_h)
		swatch_bin[swatch_id] = true
	end

	if no_arrows ~= true then
		-- set up arrows
		local arrow_grp_orig = vint_object_find("swatch_arrows", nil, MENU_BASE_DOC_HANDLE)
		local arrow_grp = vint_object_clone(arrow_grp_orig, parent_h)
		local arrow = vint_object_find("swatch_arrow_n", arrow_grp)
		menu_item.arrow_n_h = arrow
		local offset_x = (menu_item.col_width * 0.5) * menu_item.highlight_scale + 20
		local offset_y = (menu_item.row_height * 0.5) * menu_item.highlight_scale + 20
		vint_set_property(arrow, "anchor", 0, -offset_y)
		arrow = vint_object_find("swatch_arrow_s", arrow_grp)
		menu_item.arrow_s_h = arrow
		vint_set_property(arrow, "anchor", 0, offset_y)
		arrow = vint_object_find("swatch_arrow_e", arrow_grp)
		menu_item.arrow_e_h = arrow
		vint_set_property(arrow, "anchor", offset_x, 0)
		arrow = vint_object_find("swatch_arrow_w", arrow_grp)
		menu_item.arrow_w_h = arrow
		vint_set_property(arrow, "anchor", -offset_x, 0)
		menu_item.arrow_grp = arrow_grp

		--Retarget arrow animations
		local arrow_anim_h = vint_object_find("menu_swatch_arrows_pulse_anim")
		vint_set_property(arrow_anim_h, "target_handle", arrow_grp )
		lua_play_anim(arrow_anim_h, 0)

		vint_set_property(arrow_grp, "visible", menu_item.hide_arrows ~= true)
	end

	--Footer
	-- eliminate old footer if it exists
	local footer = menu_data.footer
	if footer ~= nil and footer.footer_grp ~= nil then
		vint_object_destroy(footer.footer_grp)
	end

	local width = menu_item.col_width * menu_item.num_cols
	local footer_grp = vint_object_clone(vint_object_find("swatch_footer", nil, MENU_BASE_DOC_HANDLE), parent_h)
	menu_data.footer = { }
	menu_data.footer.footer_grp = footer_grp
	menu_item.footer_txt_h = vint_object_find("text", footer_grp)

	if menu_data.footer_height == 0 and menu_data.footer ~= nil then
		vint_set_property(menu_data.footer.footer_grp, "visible", 0)
	else
		--Reset footer visibility
		vint_set_property(menu_data.footer.footer_grp, "visible", true)
	end

	-- might need a scroll bar
	if visible_rows < total_rows then
		local menu = Menu_option_labels.frame
		local bar_height = visible_rows * menu_item.row_height + 12
		menu_scroll_bar_show(menu)
		menu_scroll_bar_set_bar_height(bar_height)
		menu_scroll_bar_set_thumb_size((visible_rows / total_rows))
		menu_scroll_bar_set_pos(width + 22, Menu_active.header_height)
		menu_item.scroll_bar_visible = true
	else
		menu_scroll_bar_hide()
		menu_item.scroll_bar_visible = false
	end

	menu_grid_update_swatches(menu_item, 0)
	menu_grid_update_highlighted(menu_item, menu_item.cur_col, menu_item.cur_row)
end

function menu_horz_init(menu_data)
	Menu_horz_active = menu_data
	local item

	if menu_data.current_selection == nil or menu_data.current_selection >= menu_data.num_items then
		menu_data.current_selection = 0
	end

	if Menu_horz_label_clip_x == 0 or Menu_horz_label_clip_y == 0 then
		local label_clip_h = vint_object_find("horz_label_clip", nil, MENU_BASE_DOC_HANDLE)
		Menu_horz_label_clip_x, Menu_horz_label_clip_y = vint_get_property(label_clip_h, "anchor")
	end

	--Need to unhide the horz menu and button tips
	local h = vint_object_find("menu_horz", nil, MENU_BASE_DOC_HANDLE)
	vint_set_property(h, "visible", true)

	local h = vint_object_find("menu_tips", nil, MENU_BASE_DOC_HANDLE)
	vint_set_property(h, "visible", true)

	--The original that if the current selection is zero then we need to do something differenct.
	if menu_data.current_selection ~= 0 then
		menu_data.previous_selection = 0
	end

	local master_label_h = vint_object_find("menu_horz_label0", nil, MENU_BASE_DOC_HANDLE)
	Menu_horz_active[0].label_h = master_label_h

	if Menu_horz_active[0].label_crc ~= nil then
		vint_set_property(master_label_h, "text_tag_crc", Menu_horz_active[0].label_crc)
	else
		vint_set_property(master_label_h, "text_tag", Menu_horz_active[0].label)
	end

	-- show the second label if more than one item
	master_label_h = vint_object_find("menu_horz_label1", nil, MENU_BASE_DOC_HANDLE)
	if Menu_horz_active.num_items > 1 then
		Menu_horz_active[1].label_h = master_label_h
		vint_set_property(master_label_h, "visible", true)

		if Menu_horz_active[1].label_crc ~= nil then
			vint_set_property(master_label_h, "text_tag_crc", Menu_horz_active[1].label_crc)
		else
			vint_set_property(master_label_h, "text_tag", Menu_horz_active[1].label)
		end

		-- Set the button images
		local h = vint_object_find("upper_nav_trigger_right", nil, MENU_BASE_DOC_HANDLE)
		vint_set_property(h, "image", get_rt_button())
		vint_set_property(h, "visible", true)
		h = vint_object_find("upper_nav_trigger_right_hl", nil, MENU_BASE_DOC_HANDLE)
		vint_set_property(h, "image", get_rt_button())
		vint_set_property(h, "visible", true)
		h = vint_object_find("upper_nav_trigger_left", nil, MENU_BASE_DOC_HANDLE)
		vint_set_property(h, "image", get_lt_button())
		vint_set_property(h, "visible", true)
		h = vint_object_find("upper_nav_trigger_left_hl", nil, MENU_BASE_DOC_HANDLE)
		vint_set_property(h, "image", get_lt_button())
		vint_set_property(h, "visible", true)
		local label_clip_h = vint_object_find("horz_label_clip", nil, MENU_BASE_DOC_HANDLE)
		vint_set_property(label_clip_h, "anchor", Menu_horz_label_clip_x, Menu_horz_label_clip_y)
	else
		--Reformat heading if there is only one item
		vint_set_property(master_label_h, "visible", false)

		--No button images should be displayed
		local h = vint_object_find("upper_nav_trigger_right", nil, MENU_BASE_DOC_HANDLE)
		vint_set_property(h, "visible", false)
		h = vint_object_find("upper_nav_trigger_right_hl", nil, MENU_BASE_DOC_HANDLE)
		vint_set_property(h, "visible", false)
		h = vint_object_find("upper_nav_trigger_left", nil, MENU_BASE_DOC_HANDLE)
		vint_set_property(h, "visible", false)
		h = vint_object_find("upper_nav_trigger_left_hl", nil, MENU_BASE_DOC_HANDLE)
		vint_set_property(h, "visible", false)
		local label_clip_h = vint_object_find("horz_label_clip", nil, MENU_BASE_DOC_HANDLE)
		vint_set_property(label_clip_h, "anchor", Menu_horz_label_clip_x - 84, Menu_horz_label_clip_y)
	end

	if Menu_horz_active.num_items > 2 then
		-- create new labels
		local copy_label_h
		for i = 2, Menu_horz_active.num_items - 1 do
			copy_label_h = vint_object_clone(master_label_h)
			Menu_horz_active[i].label_h = copy_label_h

			if Menu_horz_active[i].label_crc ~= nil then
				vint_set_property(copy_label_h, "text_tag_crc", Menu_horz_active[i].label_crc)
			else
				vint_set_property(copy_label_h, "text_tag", Menu_horz_active[i].label)
			end
		end
	end



	-- store the scale and color of highlighted and highlighted
	Menu_horz_active.hl_item = { scale = {}, tint = {} }
	Menu_horz_active.norm_item = { scale = {}, tint = {} }
	local hl = Menu_horz_active.hl_item
	local norm = Menu_horz_active.norm_item

	hl.scale.x, hl.scale.y = vint_get_property(Menu_horz_active[0].label_h, "scale")
	hl.tint.r, hl.tint.g, hl.tint.b = vint_get_property(Menu_horz_active[0].label_h, "tint")

	if Menu_horz_active.num_items > 1 then
		norm.scale.x, norm.scale.y = vint_get_property(Menu_horz_active[1].label_h, "scale")
		norm.tint.r, norm.tint.g, norm.tint.b = vint_get_property(Menu_horz_active[1].label_h, "tint")
	end

	--	initialize button tips
	btn_tips_init()

	menu_show(Menu_horz_active[Menu_horz_active.current_selection].sub_menu, MENU_TRANSITION_NONE)

	menu_horz_animate_label_pos()

	--Play menu opening animation
	menu_trans_in_animation()

	-- input subscriptions
	local subs_h = vint_subscribe_to_input_event(Menu_horz_active[0].label_h, "scroll_left", "menu_horz_nav")
	Menu_input_subscriptions[subs_h] = subs_h
	subs_h = vint_subscribe_to_input_event(Menu_horz_active[0].label_h, "scroll_right", "menu_horz_nav")
	Menu_input_subscriptions[subs_h] = subs_h

	--Even tracking
	local horz_item = Menu_horz_active[Menu_horz_active.current_selection]
	if horz_item.label_crc ~= nil then
		event_tracking_interface_tab_change_string(horz_item.label_crc)
	else
		event_tracking_interface_tab_change_string(horz_item.label)
	end

end

function menu_horz_close(complete_cb)
end

function menu_horz_update_scrolling()
	local total_width = 0
	local label_widths = { }
	local label_w_pos = { }
	local label_e_pos = { }
	local clip_w = vint_get_property(vint_object_find("horz_label_clip", nil, MENU_BASE_DOC_HANDLE), "clip_size")
	local sel_index = Menu_horz_active.current_selection
	local orig_scale = { }

	-- determine the total width of the controls and position of each label
	for i = 0, Menu_horz_active.num_items - 1 do
		-- reset scale to baseline for maths
		local item = Menu_horz_active[i]
		orig_scale.x, orig_scale.y = vint_get_property(item.label_h, "scale")
		vint_set_property(item.label_h, "scale", 0.4, 0.4)

		local w = element_get_actual_size(item.label_h)

		if i == sel_index then
			w = w * 1.25		-- current selection should be scaled up
		end

		label_widths[i] = w
		label_w_pos[i] = total_width
		total_width = total_width + w + 15
		label_e_pos[i] = total_width

		-- restore scale
		vint_set_property(item.label_h, "scale", orig_scale.x, orig_scale.y)
	end

	-- are we narrow enough to not disable scrolling?
	local scrolling = (total_width > clip_w)

	vint_set_property(vint_object_find("horz_arrow_e", nil, MENU_BASE_DOC_HANDLE), "visible", scrolling)
	vint_set_property(vint_object_find("horz_arrow_w", nil, MENU_BASE_DOC_HANDLE), "visible", scrolling)

	if scrolling == false then
		vint_set_property(vint_object_find("horz_label_grp", nil, MENU_BASE_DOC_HANDLE), "anchor", 0, 0)
		return
	end

	local anchor_x = 0

	-- if the selected label is far enough to the right we are right bound
	if label_w_pos[sel_index] > total_width - clip_w then
		anchor_x = -(total_width - clip_w)
	elseif sel_index > 0 then
		anchor_x = -(label_w_pos[sel_index - 1])
	end

	-- build the tween and let it rip
	local tween_h = vint_object_find("horz_label_grp_anchor_twn_1", nil, MENU_BASE_DOC_HANDLE)
	vint_set_property(tween_h, "start_value", vint_get_property(vint_object_find("horz_label_grp", nil, MENU_BASE_DOC_HANDLE), "anchor"))
	vint_set_property(tween_h, "end_value", anchor_x, 0)
	lua_play_anim(vint_object_find("horz_label_grp_anim_1", nil, MENU_BASE_DOC_HANDLE))
end

function menu_horz_nav(target_h, event_name)
	if Menu_horz_active == 0 or menu_input_is_blocked() == true then
		return
	end

	--No naving allowed if there is only one item(JMH July 03, 2008)
	if Menu_horz_active.num_items == 1 then
		return
	end

	local previous = Menu_horz_active.current_selection
	local current = 0
	if event_name == "scroll_left" then

		Menu_horz_active.trans_animation = "menu_horz_lt_anim"
		current = Menu_horz_active.current_selection - 1

		if current < 0 then
			current = Menu_horz_active.num_items - 1
		end
	elseif event_name == "scroll_right" then

		Menu_horz_active.trans_animation = "menu_horz_rt_anim"
		current = Menu_horz_active.current_selection + 1

		if current >= Menu_horz_active.num_items then
			current = 0
		end
	else
		return
	end
	lua_play_anim(vint_object_find(Menu_horz_active.trans_animation, nil, MENU_BASE_DOC_HANDLE), 0, MENU_BASE_DOC_HANDLE)

	if Menu_active.on_horz_show ~= nil then
		Menu_active.on_horz_show(current)
	else

		audio_play(Menu_sound_scroll)
		Menu_horz_active.previous_selection = previous
		Menu_horz_active.current_selection = current

		if Menu_horz_active.on_nav ~= nil then
			Menu_horz_active.on_nav(Menu_horz_active[Menu_horz_active.current_selection].sub_menu)
		end

		--Morph Horz Menu Items
		menu_horz_animate_label_pos()
		Menu_horz_active[Menu_horz_active.current_selection].sub_menu.highlighted_item = 0
		menu_show(Menu_horz_active[Menu_horz_active.current_selection].sub_menu, MENU_TRANSITION_SWAP)
	end

	--Publish data to the event tracking system
	local horz_item = Menu_horz_active[Menu_horz_active.current_selection]
	if horz_item.label_crc ~= nil then
		event_tracking_interface_tab_change_string(horz_item.label_crc)
	else
		event_tracking_interface_tab_change_string(horz_item.label)
	end
end

--Used by the pause menu for special swapping functionality.
function menu_horz_do_nav(index)
	Menu_horz_active.previous_selection = Menu_horz_active.current_selection
	Menu_horz_active.current_selection = index
	audio_play(Menu_sound_scroll)
	--Morph Horz Menu Items
	menu_horz_animate_label_pos()
end

function menu_horz_animate_label_pos()
	local cur_x, cur_y = vint_get_property(Menu_horz_active[0].label_h, "anchor")
	local hl = Menu_horz_active.hl_item
	local norm = Menu_horz_active.norm_item
	local item

	menu_horz_update_scrolling()

	for i = 0,Menu_horz_active.num_items - 1 do
		item = Menu_horz_active[i]
		if i == Menu_horz_active.current_selection then
			--Animate text scale up
			local anim_up = vint_object_find("menu_horz_up_anim", nil, MENU_BASE_DOC_HANDLE)

			--Scale Tween
			local twn = vint_object_find("menu_horz_up_twn_1", anim_up)
			vint_set_property(twn, "target_handle", item.label_h)
			vint_set_property(twn, "state", "waiting")
			vint_set_property(twn, "end_event", "menu_horz_update_end")

			--Color Tween
			twn = vint_object_find("menu_horz_up_twn_2", anim_up)
			vint_set_property(twn, "target_handle", item.label_h)
			vint_set_property(twn, "state", "waiting")

			lua_play_anim(anim_up, 0, MENU_BASE_DOC_HANDLE)

		elseif i == Menu_horz_active.previous_selection then
			--Animate text scale down
			--Retarget Tween
			local anim_down = vint_object_find("menu_horz_dn_anim", nil, MENU_BASE_DOC_HANDLE)
			local twn = vint_object_find("menu_horz_dn_twn_1", anim_down)

			--Scale Tween
			vint_set_property(twn, "target_handle", item.label_h)
			vint_set_property(twn, "state", "waiting")
			vint_set_property(twn, "end_event", "menu_horz_update_end")

			--Color Tween
			twn = vint_object_find("menu_horz_dn_twn_2", anim_down)
			vint_set_property(twn, "target_handle", item.label_h)
			vint_set_property(twn, "state", "waiting")
			lua_play_anim(anim_down, 0, MENU_BASE_DOC_HANDLE)

		else
			--Anything left over should snap to the original size
			vint_set_property(item.label_h, "tint", norm.tint.r, norm.tint.g, norm.tint.b)
			vint_set_property(item.label_h, "scale", norm.scale.x, norm.scale.y)
		end
	end

	if Menu_horz_update_label_thread == -1 then
		Menu_horz_update_label_thread = thread_new("menu_horz_update_labels")
	end
end

--Updates horizontal menu options on a perframe basis
function menu_horz_update_labels()
	while true do
		menu_horz_align_labels()
		thread_yield()
	end
end

function menu_horz_align_labels()
	local cur_x, cur_y = vint_get_property(Menu_horz_active[0].label_h, "anchor")
	local item, w

	for i = 0, Menu_horz_active.num_items - 1 do
		item = Menu_horz_active[i]
		vint_set_property(item.label_h, "anchor", cur_x, cur_y)
		w = element_get_actual_size(item.label_h)
		cur_x = cur_x + 15 + w
	end
end

function menu_horz_update_end()
	if Menu_horz_update_label_thread ~= -1 then
		menu_horz_align_labels()
		thread_kill(Menu_horz_update_label_thread)
		Menu_horz_update_label_thread = -1
	end
end

function menu_scroll_bar_init(option_labels, bar_grp)
	-- menu_h is the handle to the parent menu for the scroll bar
	if bar_grp == nil then
		bar_grp = vint_object_find("menu_scroll_bar", option_labels.frame)
	end

	vint_set_property(bar_grp, "visible", false)

	local scroll_data = {
		visible =			false,
		bar_grp =			bar_grp,
		bg_n_h =				vint_object_find("menu_scroll_bg_n", bar_grp),
		bg_c_h =				vint_object_find("menu_scroll_bg_c", bar_grp),
		bg_s_h =				vint_object_find("menu_scroll_bg_s", bar_grp),
		thumb_n_h =			vint_object_find("menu_scroll_thumb_n", bar_grp),
		thumb_s_h =			vint_object_find("menu_scroll_thumb_s", bar_grp),
		thumb_blend_h =	vint_object_find("menu_scroll_thumb_blend", bar_grp),
		thumb_pos =			0,
		bar_height =		332,
		thumb_height =		332,
	}

	option_labels.scroll_bar = scroll_data
end

function menu_scroll_bar_update(scroll_data)
	if scroll_data.visible == false then
		return
	end

	-- update the thumb pos
	local thumb_offset = scroll_data.thumb_pos * (scroll_data.bar_height - scroll_data.thumb_height) + 10
	thumb_offset = floor(thumb_offset)

	vint_set_property(scroll_data.thumb_n_h,		"anchor", 3, thumb_offset)
	vint_set_property(scroll_data.thumb_s_h,		"anchor", 3, thumb_offset + scroll_data.thumb_height - 20) --Magic Number represents the offset from the thumb height
	vint_set_property(scroll_data.thumb_blend_h,	"anchor", 3, thumb_offset + scroll_data.thumb_height - 63) --Magic Number represents the offset from the thumb height
end

function menu_scroll_bar_show()
	local scroll_data = Menu_option_labels.scroll_bar
	vint_set_property(scroll_data.bar_grp, "visible", true)
	scroll_data.visible = true
end

function menu_scroll_bar_set_pos(x, y)
	vint_set_property(Menu_option_labels.scroll_bar.bar_grp, "anchor", x, y)
end

function menu_scroll_bar_set_bar_height(new_height)
	local scroll_data = Menu_option_labels.scroll_bar
	scroll_data.bar_height = new_height - 54 --This magic number will allow you to change the base height of the scrollbar

	vint_set_property(scroll_data.bg_s_h, "anchor", 38, new_height - 10)
	vint_set_property(scroll_data.bg_c_h, "source_se", 10, new_height - 28)

	menu_scroll_bar_update(scroll_data)
end

function menu_scroll_bar_set_thumb_size(height)
	local scroll_data = Menu_option_labels.scroll_bar
	scroll_data.thumb_height = floor(height * scroll_data.bar_height)

	if scroll_data.thumb_height < 60 then
		scroll_data.thumb_height = 60
	end

	vint_set_property(scroll_data.thumb_n_h, "source_se", 32, scroll_data.thumb_height - 20)
	menu_scroll_bar_update(scroll_data)
end

function menu_scroll_bar_set_thumb_pos(value)
	local scroll_data = Menu_option_labels.scroll_bar
	if scroll_data.thumb_pos ~= value then
		scroll_data.thumb_pos = value
		menu_scroll_bar_update(scroll_data)
	end
end

function menu_scroll_bar_hide()
	local scroll_data = Menu_option_labels.scroll_bar
	vint_set_property(scroll_data.bar_grp, "visible", false)
	scroll_data.visible = false
end

function menu_set_custom_control_callbacks(custom_callbacks)
	for key, val in custom_callbacks do
		Menu_control_callbacks[key] = val
	end
end

-- Init the menu
-- offset_x, offset_y: X and Y offsets from the default position [nclok1405]
function menu_init(offset_x, offset_y)
	if offset_x == nil then
		offset_x = 0
	end
	if offset_y == nil then
		offset_y = 0
	end

	vint_init_general_audio()

	if Menu_use_hud == false then
		Menu_hud_hidden = true;
		hud_hide(true)
	end

	if Menu_option_labels.frame ~= nil then
		vint_object_destroy(Menu_option_labels.frame)
	end

	if Menu_option_labels_inactive.frame ~= nil then
		vint_object_destroy(Menu_option_labels_inactive.frame)
	end

	-- build the initial active label list
	local active_frame = vint_object_find("menu", nil, MENU_BASE_DOC_HANDLE)

	Menu_active_anchor_end_x, Menu_active_anchor_end_y = vint_get_property(active_frame, "anchor")

	-- Apply offsets [nclok1405]
	Menu_active_anchor_end_x = Menu_active_anchor_end_x + offset_x
	Menu_active_anchor_end_y = Menu_active_anchor_end_y + offset_y

	active_frame = vint_object_clone(active_frame, vint_object_find("safe_frame"))
	Menu_option_labels.frame = active_frame
	local clip_h = vint_object_find("marquee_clip", active_frame)

	local label_h = vint_object_find("menu_option_label00", active_frame)
	local stripe_h = vint_object_find("menu_stripe00", active_frame)
	Menu_option_labels[0] = { label_h = label_h, stripe_h = stripe_h }
	Menu_option_labels.clip_h = clip_h
	Menu_option_labels.hl_bar = vint_object_find("menu_sel_bar", active_frame)
	Menu_option_labels.hl_clip = vint_object_find("marquee_clip_sel_bar", active_frame)
	Menu_option_labels.control_parent = vint_object_find("transition_clip", active_frame)
	vint_set_property(active_frame, "visible", false)

	--Reset Scaler for menu internals
	local frame_scale_x, frame_scale_y = vint_get_property(active_frame, "scale")
	Menu_scaler = 1/frame_scale_x

	-- build the initial inactive label list
	local inactive_frame = vint_object_clone(active_frame)
	Menu_option_labels_inactive.frame = inactive_frame
	local clip2_h   = vint_object_find("marquee_clip", inactive_frame)

	local label2_h  = vint_object_find("menu_option_label00", inactive_frame)
	local stripe2_h = vint_object_find("menu_stripe00", inactive_frame)
	Menu_option_labels_inactive[0] = { label_h =label2_h, stripe_h = stripe2_h }
	Menu_option_labels_inactive.clip_h = clip2_h
	Menu_option_labels_inactive.hl_bar = vint_object_find("menu_sel_bar", inactive_frame)
	Menu_option_labels_inactive.hl_clip = vint_object_find("marquee_clip_sel_bar", inactive_frame)
	Menu_option_labels_inactive.control_parent = vint_object_find("transition_clip", inactive_frame)
	vint_set_property(inactive_frame, "visible", false)

	-- pause all menu animations
	menu_init_anims()

	menu_scroll_bar_init(Menu_option_labels)
	menu_scroll_bar_init(Menu_option_labels_inactive)

	menu_grab_input()
end

function menu_grab_input()
	-- subscribe to input
	local subs_h = vint_subscribe_to_input_event(nil, "nav_up", "menu_nav")
	Menu_input_subscriptions[subs_h] = subs_h
	subs_h = vint_subscribe_to_input_event(nil, "nav_down", "menu_nav")
	Menu_input_subscriptions[subs_h] = subs_h
	subs_h = vint_subscribe_to_input_event(nil, "nav_right", "menu_nav")
	Menu_input_subscriptions[subs_h] = subs_h
	subs_h = vint_subscribe_to_input_event(nil, "nav_left", "menu_nav")
	Menu_input_subscriptions[subs_h] = subs_h
	subs_h = vint_subscribe_to_input_event(nil, "select", "menu_nav")
	Menu_input_subscriptions[subs_h] = subs_h
	subs_h = vint_subscribe_to_input_event(nil, "back", "menu_nav")
	Menu_input_subscriptions[subs_h] = subs_h
	subs_h = vint_subscribe_to_input_event(nil, "map", "menu_nav")
	Menu_input_subscriptions[subs_h] = subs_h
	subs_h = vint_subscribe_to_input_event(nil, "pause", "menu_nav")
	Menu_input_subscriptions[subs_h] = subs_h
	subs_h = vint_subscribe_to_input_event(nil, "alt_select", "menu_nav")
	Menu_input_subscriptions[subs_h] = subs_h
	subs_h = vint_subscribe_to_input_event(nil, "exit", "menu_nav")
	Menu_input_subscriptions[subs_h] = subs_h

	if Menu_horz_active ~= 0 then
		subs_h = vint_subscribe_to_input_event(Menu_horz_active[0].label_h, "scroll_left", "menu_horz_nav")
		Menu_input_subscriptions[subs_h] = subs_h
		subs_h = vint_subscribe_to_input_event(Menu_horz_active[0].label_h, "scroll_right", "menu_horz_nav")
		Menu_input_subscriptions[subs_h] = subs_h
	end
end

function menu_trans_in_tweens_kill()
	for idx, val in Menu_trans_in_twns  do
		vint_object_destroy(val, nil)
	end

	Menu_trans_in_twns = {}
	vint_set_property(vint_object_find("menu_trans_in", nil, MENU_BASE_DOC_HANDLE), "is_paused", true)

	menu_input_block(false)
end

function menu_trans_out_tweens_kill()
	for idx, val in Menu_trans_out_twns  do
		vint_object_destroy(val, nil)
	end

	--TODO: PUT SOMETHING HERE THAT TURNS OFF ALL THE LIGHTS IF Menu_fade_to_black IS TRUE!! - JHG

	Menu_trans_out_twns = {}

	-- destroy the extra item labels, leaving the two master items
	for i = 2, Menu_horz_active.num_items - 1 do
		vint_object_destroy(Menu_horz_active[i].label_h, MENU_BASE_DOC_HANDLE)
		Menu_horz_active[i].label_h = nil
	end

	--Reset horizontal menu item stems
	local i = Menu_horz_active.hl_item
	vint_set_property(Menu_horz_active[0].label_h, "scale", i.scale.x, i.scale.y)
	vint_set_property(Menu_horz_active[0].label_h, "tint", i.tint.r, i.tint.g, i.tint.b)

	if Menu_horz_active.num_items > 1 then
		i = Menu_horz_active.norm_item
		vint_set_property(Menu_horz_active[1].label_h, "scale", i.scale.x, i.scale.y)
		vint_set_property(Menu_horz_active[1].label_h, "tint", i.tint.r, i.tint.g, i.tint.b)
	end

	menu_close_finalize()
end

function menu_trans_in_animation()
	--Find intro animation
	local intro_anim = vint_object_find("menu_trans_in", nil, MENU_BASE_DOC_HANDLE)

	--Hide first two horizontal menu items
	vint_set_property(Menu_horz_active[0].label_h, "alpha", 0)

	if Menu_horz_active.num_items > 1 then
		vint_set_property(Menu_horz_active[1].label_h, "alpha", 0)
	end

	--Duplicate tweens and stagger time for other menu items
	local twn_h = vint_object_find("menu_horz_label1_alpha_twn_2", intro_anim, MENU_BASE_DOC_HANDLE)
	local start_time = vint_get_property(twn_h, "start_time")
	local duration = vint_get_property(twn_h, "duration")

	--Tweens for horizontal labels
	local twn_clone_h
	for i = 2, Menu_horz_active.num_items - 1 do
		local label_h = Menu_horz_active[i].label_h
		twn_clone_h = vint_object_clone(twn_h)
		start_time = start_time + .03
		vint_set_property(twn_clone_h, "start_time", start_time)
		vint_set_property(twn_clone_h, "target_handle", label_h)
		vint_set_property(label_h, "alpha", 0)
		Menu_trans_in_twns[twn_clone_h] = twn_clone_h
	end

	--Find out whats longer the last btn text alpha tween or the btn_tips and base our tween callback on that.
	local btn_tip_twn_h = vint_object_find("menu_btn_tip_ext_00_alpha_twn_1", intro_anim)
	local tab_twn_time = duration + start_time
	local btn_tip_twn_time = vint_get_property(btn_tip_twn_h, "duration") + vint_get_property(btn_tip_twn_h, "start_time")

	if btn_tip_twn_time > tab_twn_time or twn_clone_h == nil then
		vint_set_property(btn_tip_twn_h, "end_event", "menu_trans_in_tweens_kill")
	else
		vint_set_property(twn_clone_h, "end_event", "menu_trans_in_tweens_kill")
	end
	lua_play_anim(intro_anim, 0, MENU_BASE_DOC_HANDLE)

	--Slide in menu
	local twn = vint_object_create("menu_in_twn_1", "tween", vint_object_find("root_animation"))

	local frame_x, frame_y =  vint_get_property(Menu_option_labels.frame, "anchor")

	vint_set_property(twn, "target_handle",  Menu_option_labels.frame)
	vint_set_property(twn, "target_property",  "anchor")
	local x, y = vint_get_property(Menu_option_labels.frame, "anchor")
	vint_set_property(twn, "start_value", 0 - Menu_active.menu_width - 100, frame_y)
	vint_set_property(twn, "end_value", x, y)
	vint_set_property(twn, "start_time", vint_get_time_index())
	vint_set_property(twn, "duration", 0.2)
	Menu_trans_out_twns[twn] = twn

	menu_input_block(true)
	audio_play(Menu_sound_open)
end

function menu_release_input()
	for index, value in Menu_input_subscriptions do
		vint_unsubscribe_to_input_event(index)
	end
end

function menu_trans_out_animation()

	local exit_anim

	if Menu_fade_to_black then
		exit_anim = vint_object_find("black_fade_out", nil, MENU_BASE_DOC_HANDLE)

		vint_set_property(vint_object_find("black_fade_alpha", exit_anim), "end_event", "menu_trans_out_tweens_kill")
		lua_play_anim(exit_anim, 0, MENU_BASE_DOC_HANDLE)
	else
		exit_anim = vint_object_find("menu_trans_out", nil, MENU_BASE_DOC_HANDLE)

		--Duplicate tweens and stagger time for other menu items
		local twn_h = vint_object_find("menu_horz_label1_alpha_twn_2", exit_anim, MENU_BASE_DOC_HANDLE)
		local start_time = vint_get_property(twn_h, "start_time")

		local duration_twn_h = vint_object_find("horz_clip_offset_twn_1", exit_anim, MENU_BASE_DOC_HANDLE)
		local duration = vint_get_property(duration_twn_h, "duration")
		duration = (duration/2)/Menu_horz_active.num_items

		for i = 2, Menu_horz_active.num_items - 1 do
			local label_h = Menu_horz_active[i].label_h
			local twn_clone_h = vint_object_clone(twn_h)
			start_time = start_time + duration
			vint_set_property(twn_clone_h, "start_time", start_time)
			vint_set_property(twn_clone_h, "target_handle", label_h)
			vint_set_property(twn_clone_h, "duration", duration)
			vint_set_property(label_h, "alpha", 1)
			Menu_trans_out_twns[twn_clone_h] = twn_clone_h
		end

		--Callback to kill tweens
		vint_set_property(vint_object_find("menu_btn_tip_ext_00_alpha_twn_2", exit_anim), "end_event", "menu_trans_out_tweens_kill")
		lua_play_anim(exit_anim, 0, MENU_BASE_DOC_HANDLE)
	end

	--Slide out menu
	local twn = vint_object_create("menu_out_twn_1", "tween", vint_object_find("root_animation"))

	vint_set_property(twn, "target_handle",  Menu_option_labels.frame)
	vint_set_property(twn, "target_property",  "anchor")
	local x, y = vint_get_property(Menu_option_labels.frame, "anchor")
	vint_set_property(twn, "start_value", x, y)
	vint_set_property(twn, "end_value", 0 - Menu_active.menu_width - 100, y)
	vint_set_property(twn, "start_time", vint_get_time_index())
	vint_set_property(twn, "duration", 0.2)
	Menu_trans_out_twns[twn] = twn

	audio_play(Menu_sound_close)

end

function menu_close(complete_cb)
	-- currently all closing goodness is handled by menu_horz_close()
	-- this may not be adequate since not all menus will use the horz menu
	-- like food
	if complete_cb ~= nil then
		Menu_close_cb = complete_cb
	else
		Menu_close_cb = 0
	end

	menu_input_block(true)

	--Hide style cluster
	if Style_cluster_enabled == true then
		local cash_trans_out = vint_object_find("cash_trans_out", nil, MENU_BASE_DOC_HANDLE)
		lua_play_anim(cash_trans_out, 0)
	end

	--JMT for some reason the transition out isn't happening on coop start, so skip it
	if Menu_horz_active ~= nil and Menu_horz_active ~= 0 and is_coop_start_screen() == false then
		menu_trans_out_animation()
	else
		-- shouldn't we transition something out?
		menu_close_finalize()
	end


end

function menu_close_finalize()
	menu_input_block(false)
	menu_release_input()

	if Menu_use_hud == false then
		if Sui_hud_enable == 0 then
			hud_hide(true)
		else
			hud_hide(false)
		end
		Menu_hud_hidden = false;
	end

	if Menu_close_cb ~= 0 then
		Menu_close_cb()
	end
end

function menu_anim_clone_and_pause(name, parent, pause)
	local h = vint_object_find(name, nil, MENU_BASE_DOC_HANDLE)
	h = vint_object_clone(h, parent)

	if pause ~= false then
		vint_set_property(h, "is_paused", true)
	end

	return h
end

function menu_init_anims()
	local r = vint_object_find("root_animation")

	for idx, val in Menu_anims do	--	Clear out old menu animations
		vint_object_destroy(val)
	end

	Menu_anims[0] = menu_anim_clone_and_pause("menu_item_hl_pulse_anim", r, false)
	Menu_anims[1] = menu_anim_clone_and_pause("menu_num_slider_in_anim", r)
	Menu_anims[2] = menu_anim_clone_and_pause("menu_num_slider_pulse_anim", r, false)
	Menu_anims[3] = menu_anim_clone_and_pause("menu_option_label_in_anim", r)
	Menu_anims[4] = menu_anim_clone_and_pause("menu_option_label_out_anim", r)
	Menu_anims[5] = menu_anim_clone_and_pause("menu_sel_bar_fade_in_anim", r)
	Menu_anims[6] = menu_anim_clone_and_pause("menu_sel_bar_fade_out_anim", r)
	Menu_anims[7] = menu_anim_clone_and_pause("menu_swatch_arrows_pulse_anim", r)
	Menu_anims[8] = menu_anim_clone_and_pause("menu_swatch_in_anim", r)
	Menu_anims[9] = menu_anim_clone_and_pause("menu_swatch_icon_select_anim", r)
	Menu_anims[10] = menu_anim_clone_and_pause("menu_swatch_icon_pulse_anim", r)
	Menu_anims[11] = menu_anim_clone_and_pause("menu_text_slider_pulse_anim", r)
end

function menu_input_block(block)
	if block == true then
		Menu_input_blocked = Menu_input_blocked + 1
	elseif Menu_input_blocked > 0 then
		--don't go below 0
		Menu_input_blocked = Menu_input_blocked - 1
	end
end

function menu_input_is_blocked()
	return Menu_input_blocked > 0
end

function menu_nav(target, event, accelleration)
	if menu_input_is_blocked() == true or Menu_active == 0 then
		return
	end

	btn_tips_update()
	local item_type = 0
	if Menu_active.num_items > 0 then
		item_type = Menu_active[Menu_active.highlighted_item].type
		Menu_input_accelleration = accelleration
	end

	if event == "nav_up" then
		if Menu_control_callbacks[item_type].on_nav_up ~= nil then
			local menu_option = Menu_option_labels[Menu_active.highlighted_item - Menu_active.first_vis_item]
			Menu_control_callbacks[item_type].on_nav_up(menu_option, Menu_active[Menu_active.highlighted_item])
		else
			if Menu_active.num_items > 1 then
				local new_item = Menu_active.highlighted_item - 1

				if new_item < 0 then
					new_item = Menu_active.num_items - 1
				end

				-- skip disabled
				while Menu_active[new_item].disabled == true and new_item ~= Menu_active.highlighted_item do
					new_item = new_item - 1

					if new_item < 0 then
						new_item = Menu_active.num_items - 1
					end
				end

				menu_update_nav_bar(new_item)
				audio_play(Menu_sound_item_nav)

				if Menu_active.on_nav ~= nil then
					Menu_active.on_nav(Menu_active)
				end
			end
		end
	elseif event == "nav_down" then
		if Menu_control_callbacks[item_type].on_nav_down ~= nil then
			local menu_option = Menu_option_labels[Menu_active.highlighted_item - Menu_active.first_vis_item]
			Menu_control_callbacks[item_type].on_nav_down(menu_option, Menu_active[Menu_active.highlighted_item])
		else
			if Menu_active.num_items > 1 then
				local new_item = Menu_active.highlighted_item + 1

				if new_item >= Menu_active.num_items then
					new_item = 0
				end

				-- skip disabled
				while Menu_active[new_item].disabled == true and new_item ~= Menu_active.highlighted_item do
					new_item = new_item + 1

					if new_item >= Menu_active.num_items then
						new_item = 0
					end
				end

				menu_update_nav_bar(new_item)
				audio_play(Menu_sound_item_nav)

				if Menu_active.on_nav ~= nil then
					Menu_active.on_nav(Menu_active)
				end
			end
		end

	elseif event == "select" then
		if Menu_control_callbacks[item_type].on_select ~= nil then
			local menu_option = Menu_option_labels[Menu_active.highlighted_item - Menu_active.first_vis_item]
			Menu_control_callbacks[item_type].on_select(menu_option, Menu_active[Menu_active.highlighted_item])
			audio_play(Menu_sound_select)

		elseif Menu_active.on_select ~= nil then
			local menu_option = Menu_option_labels[Menu_active.highlighted_item - Menu_active.first_vis_item]
			Menu_active.on_select(menu_option, Menu_active[Menu_active.highlighted_item])
			audio_play(Menu_sound_select)
		end

	elseif event == "back" then

		if Menu_active.on_back ~= nil then
			audio_play(Menu_sound_back)
			Menu_active.on_back(Menu_active)
		elseif Menu_active.parent_menu ~= nil then
			audio_play(Menu_sound_back)
			menu_show(Menu_active.parent_menu, MENU_TRANSITION_SWEEP_RIGHT)
		end

	elseif event == "nav_right" then
		if Menu_control_callbacks[item_type].on_nav_right ~= nil then
			local menu_option = Menu_option_labels[Menu_active.highlighted_item - Menu_active.first_vis_item]
			Menu_control_callbacks[item_type].on_nav_right(menu_option, Menu_active[Menu_active.highlighted_item])
		end

	elseif event == "nav_left" then
		if Menu_control_callbacks[item_type].on_nav_left ~= nil then
			local menu_option = Menu_option_labels[Menu_active.highlighted_item - Menu_active.first_vis_item]
			Menu_control_callbacks[item_type].on_nav_left(menu_option, Menu_active[Menu_active.highlighted_item])
		end

	elseif event == "alt_select" then
		if Menu_control_callbacks[item_type].on_alt_select ~= nil then
			-- control gets first stab at event
			local menu_option = Menu_option_labels[Menu_active.highlighted_item - Menu_active.first_vis_item]
			Menu_control_callbacks[item_type].on_alt_select(menu_option, Menu_active[Menu_active.highlighted_item])

		elseif Menu_active.on_alt_select ~= nil then
			-- fallback to menu
			local menu_option = Menu_option_labels[Menu_active.highlighted_item - Menu_active.first_vis_item]
			Menu_active.on_alt_select(menu_option, Menu_active[Menu_active.highlighted_item])
		end
	elseif event == "pause" then
		if Menu_active.on_pause ~= nil then
			Menu_active.on_pause(Menu_active)
		elseif vint_document_find("main_menu") ~= 0 then
			-- same as select above
			if Menu_control_callbacks[item_type].on_select ~= nil then
				local menu_option = Menu_option_labels[Menu_active.highlighted_item - Menu_active.first_vis_item]
				Menu_control_callbacks[item_type].on_select(menu_option, Menu_active[Menu_active.highlighted_item])
				audio_play(Menu_sound_select)

			elseif Menu_active.on_select ~= nil then
				local menu_option = Menu_option_labels[Menu_active.highlighted_item - Menu_active.first_vis_item]
				Menu_active.on_select(menu_option, Menu_active[Menu_active.highlighted_item])
				audio_play(Menu_sound_select)
			end
		else
			--	Call regular pause
			dialog_open_pause_display()
		end
	elseif event == "map" then
		if Menu_active.on_map ~= nil then
			Menu_active.on_map(Menu_active)
		end
	elseif event == "exit" then
		--	Call Menu_active.on_exit ?
	end

end

function menu_transition_complete()
	for index, value in Menu_transition_data.tweens do
		vint_object_destroy(index)
	end

	-- release all the controls on the inactive menu
	if Menu_option_labels_inactive.max_rows ~= nil then
		for i = 0, Menu_option_labels_inactive.max_rows - 1 do
			if Menu_option_labels_inactive[i].control ~= nil then
				menu_release_control(Menu_option_labels_inactive[i].control)
				Menu_option_labels_inactive[i].control = nil
			end
		end
	end

	if Menu_inactive ~= 0 then
		if Menu_inactive.on_release ~= nil then
			Menu_inactive.on_release(Menu_inactive)
		end

		-- release footer
		if Menu_inactive.footer ~= nil then
			vint_object_destroy(Menu_inactive.footer.footer_grp)
			vint_object_destroy(Menu_inactive.footer.hr_h)
			Menu_inactive.footer = nil
		end

		--Reset size parameters
		Menu_inactive.header_width = nil
		Menu_inactive.width = 0
		Menu_inactive.height = 0
	end



	--Reset Scrollbar
	Menu_option_labels_inactive.scroll_bar_visible = false

	vint_set_property(Menu_option_labels_inactive.frame, "visible", false)

	if Menu_active ~= 0 and Menu_active.custom_show ~= true then
		vint_set_property(Menu_option_labels.frame, "visible", true)
	else
		vint_set_property(Menu_option_labels.frame, "visible", false)
	end

	if Menu_active ~= 0 then
		vint_set_property(Menu_option_labels.frame, "anchor", menu_get_transition_end(Menu_active))
	end

	Menu_transition_data = { tweens = { } }
	menu_input_block(false)
	Menu_transition_in_progress = false

	if Menu_hide_active_pending == true then
		menu_hide_active()
		Menu_hide_active_pending = false
	end
end

function menu_create_tween(name, target_h, target_prop, duration)
	local tween_h = vint_object_create(name, "tween", vint_object_find("root_animation"))

	vint_set_property(tween_h, "duration", duration)
	vint_set_property(tween_h, "target_handle", target_h)
	vint_set_property(tween_h, "algorithm", "linear")
	vint_set_property(tween_h, "target_property", target_prop)
	vint_set_property(tween_h, "start_time",	vint_get_time_index())
	vint_set_property(tween_h, "is_paused", false)
	return tween_h
end

function menu_transition_swap_stage2(tween_h)
	vint_set_property(Menu_option_labels_inactive.frame, "visible", false)

	if Menu_active ~= 0 then
		local end_x, end_y = menu_get_transition_end(Menu_active)
		local start_x = 0 - Menu_active.menu_width - 30
		vint_set_property(tween_h, "target_handle", Menu_option_labels.frame)
		vint_set_property(Menu_option_labels.frame, "anchor", start_x, end_y)
		vint_set_property(tween_h, "start_value", start_x, end_y)
		vint_set_property(tween_h, "end_value", end_x, end_y)
		vint_set_property(tween_h, "start_time",	vint_get_time_index())
		vint_set_property(tween_h, "is_paused", false)
		vint_set_property(tween_h, "end_event", "menu_transition_complete")
		vint_set_property(tween_h, "state", "waiting")
		if Menu_active.custom_show == true then
			vint_set_property(Menu_option_labels.frame, "visible", false)
		else
			vint_set_property(Menu_option_labels.frame, "visible", true)
		end
	else
		vint_set_property(Menu_option_labels.frame, "visible", false)
		menu_transition_complete()
	end
end

function menu_get_transition_end(menu_data)
	local end_x, end_y
	if Menu_swap_center == true then
		end_x = Menu_active_anchor_end_x - (menu_data.menu_width * 0.5 * (1 / Menu_scaler))
		end_y = Menu_active_anchor_end_y - (menu_data.menu_height * 0.5 * (1 / Menu_scaler))
	else
		end_x = Menu_active_anchor_end_x
		end_y = Menu_active_anchor_end_y
	end
	return end_x, end_y
end

function menu_transition_swap_begin()
	menu_input_block(true)
	Menu_transition_in_progress = true
	vint_set_property(Menu_option_labels.frame, "visible", false)
	local tween_h = menu_create_tween("menu_transition1", Menu_option_labels_inactive.frame, "anchor", 0.1)
	Menu_transition_data.tweens[tween_h] = true

	if Menu_inactive ~= 0 then
		local end_x, end_y = menu_get_transition_end(Menu_inactive)
		vint_set_property(tween_h, "start_value", end_x, end_y)
		vint_set_property(tween_h, "end_value", 0 - Menu_inactive.menu_width - 30, end_y)
		vint_set_property(tween_h, "end_event", "menu_transition_swap_stage2")

		if Menu_inactive.custom_show == true then
			vint_set_property(Menu_option_labels_inactive.frame, "visible", false)
		else
			vint_set_property(Menu_option_labels_inactive.frame, "visible", true)
		end
	else
		vint_set_property(Menu_option_labels_inactive.frame, "visible", false)
		menu_transition_swap_stage2(tween_h)
	end
end

function menu_transition_sweep_end()

	local h = vint_object_find("menu_bg",	Menu_option_labels.frame)
	vint_set_property(h, "visible", true)

	h = vint_object_find("menu_bg", Menu_option_labels_inactive.frame)
	vint_set_property(h, "anchor", 0, 0)

	h = vint_object_find("menu_fg", Menu_option_labels.frame)
	vint_set_property(h, "visible", true)

	h = vint_object_find("menu_fg", Menu_option_labels_inactive.frame)
	vint_set_property(h, "anchor", 0, 0)

	h = vint_object_find("transition_clip", Menu_option_labels_inactive.frame)
	vint_set_property(h, "clip_enabled", false)

	h = vint_object_find("transition_clip", Menu_option_labels.frame)
	vint_set_property(h, "clip_enabled", false)

	h = vint_object_find("menu_frame_middle", Menu_option_labels_inactive.frame)
	vint_set_property(h, "visible", true)

	vint_object_destroy(Menu_transition_data.backdrop_clone)

	menu_transition_complete()
end

function menu_transition_sweep_begin(sweep_left)
	if Menu_inactive ~= 0 then
		Menu_transition_in_progress = true
		menu_input_block(true)
		local duration = .15
		local option_active, menu_active, option_inactive, menu_inactive
		local t1, t2

			option_active = Menu_option_labels
			menu_active = Menu_active
			option_inactive = Menu_option_labels_inactive
			menu_inactive = Menu_inactive

		local end_x, end_y = menu_get_transition_end(Menu_active)
		local start_x, start_y = menu_get_transition_end(Menu_inactive)

		-- sweep in new menu
		local tween_h = menu_create_tween("menu_transition1", option_active.frame, "anchor", duration)
		Menu_transition_data.tweens[tween_h] = true

		if sweep_left == true then
			t1 = start_x + menu_inactive.menu_width / Menu_scaler
		else
			t1 = start_x - menu_inactive.menu_width / Menu_scaler
		end

		vint_set_property(tween_h, "start_value", t1, start_y)
		vint_set_property(tween_h, "end_value", end_x, end_y)
		vint_set_property(tween_h, "end_event", "menu_transition_sweep_end")

		-- reuse old menu's frame so reverse sweep it so it appears stationary
		local h = vint_object_find("menu_bg", option_inactive.frame)
		tween_h = menu_create_tween("menu_transition2", h, "anchor", duration)
		Menu_transition_data.tweens[tween_h] = true

		if sweep_left == true then
			t1 = menu_inactive.menu_width
		else
			t1 = -menu_inactive.menu_width
		end

		vint_set_property(tween_h, "start_value", 0, 0)
		vint_set_property(tween_h, "end_value", t1, 0)

		--Clone background frame tween on the foreground frame
		h = vint_object_find("menu_fg", option_inactive.frame)
		tween_h = vint_object_clone(tween_h)
		vint_set_property(tween_h, "target_handle", h)
		Menu_transition_data.tweens[tween_h] = true

		-- sweep out old menu
		tween_h = menu_create_tween("menu_transition3", option_inactive.frame, "anchor", duration)
		Menu_transition_data.tweens[tween_h] = true

		if sweep_left == true then
			t1 = start_x - menu_inactive.menu_width / Menu_scaler
			t2 = end_x - menu_inactive.menu_width / Menu_scaler
		else
			t1 = start_x + menu_inactive.menu_width / Menu_scaler
			t2 = end_x + menu_inactive.menu_width / Menu_scaler
		end

		vint_set_property(tween_h, "start_value",  start_x, start_y)
		vint_set_property(tween_h, "end_value", t2, end_y)

		-- hide new menu's frame
		h = vint_object_find("menu_bg", option_active.frame)
		vint_set_property(h, "visible", false)
		h = vint_object_find("menu_fg", option_active.frame)
		vint_set_property(h, "visible", false)

		-- these tweens handle the resizing

		-- Resize backdrop

		-- so that the gray backdrop is below both menus, clone the inactive's backdrop
		-- and hide the original. it will need to be unhidden after transition is complete
		local orig_h = vint_object_find("menu_frame_middle", option_inactive.frame)

		h = vint_object_clone(orig_h, vint_object_find("safe_frame"))
		Menu_transition_data.backdrop_clone = h
		--vint_set_property(h, "anchor", start_x + (17*Menu_scaler), start_y + (12*Menu_scaler))
		vint_set_property(h, "anchor", start_x , start_y )

		-- set original as hidden after we clone it
		vint_set_property(orig_h, "visible", false)

		-- animate the scale on phony backdrop
		tween_h = menu_create_tween("menu_transition4", h, "scale", duration)
		Menu_transition_data.tweens[tween_h] = true
		vint_set_property(tween_h, "start_value", option_inactive.trim_c_scale_x / Menu_scaler, option_inactive.trim_c_scale_y / Menu_scaler)
		vint_set_property(tween_h, "end_value", option_active.trim_c_scale_x / Menu_scaler, option_active.trim_c_scale_y / Menu_scaler)

		-- animate the anchor on phony backdrop
		tween_h = menu_create_tween("menu_transition4", h, "anchor", duration)
		Menu_transition_data.tweens[tween_h] = true
		vint_set_property(tween_h, "start_value", start_x + (17 /Menu_scaler), start_y + (12/Menu_scaler))
		vint_set_property(tween_h, "end_value", end_x + (17/Menu_scaler), end_y + (12/Menu_scaler))

		-- move and resize the bottom trim
		h = vint_object_find("menu_mid_trm_btm_line_img", option_inactive.frame)
		tween_h = menu_create_tween("menu_transition5", h, "anchor", duration)
		Menu_transition_data.tweens[tween_h] = true
		vint_set_property(tween_h, "start_value", option_inactive.trim_s_pos_x, option_inactive.trim_s_pos_y)
		vint_set_property(tween_h, "end_value", option_active.trim_s_pos_x, option_active.trim_s_pos_y)

		tween_h = menu_create_tween("menu_transition6", h, "source_se", duration)
		Menu_transition_data.tweens[tween_h] = true
		vint_set_property(tween_h, "start_value", option_inactive.trim_s_src_w, option_inactive.trim_s_src_h)
		vint_set_property(tween_h, "end_value", option_active.trim_s_src_w, option_active.trim_s_src_h)

		-- position the se ornate
		h = vint_object_find("menu_mid_trm_btm_right", option_inactive.frame)
		tween_h = menu_create_tween("menu_transition7", h, "anchor", duration)
		Menu_transition_data.tweens[tween_h] = true
		vint_set_property(tween_h, "start_value", option_inactive.trim_se_x, option_inactive.trim_se_y)
		vint_set_property(tween_h, "end_value", option_active.trim_se_x, option_active.trim_se_y)

		-- position and size of e border
		h = vint_object_find("menu_frame_brdr_r", option_inactive.frame)
		tween_h = menu_create_tween("menu_transition8", h, "anchor", duration)
		Menu_transition_data.tweens[tween_h] = true
		vint_set_property(tween_h, "start_value", option_inactive.trim_w_pos_x, option_inactive.trim_w_pos_y)
		vint_set_property(tween_h, "end_value", option_active.trim_w_pos_x, option_active.trim_w_pos_y)

		tween_h = menu_create_tween("menu_transition9", h, "source_se", duration)
		Menu_transition_data.tweens[tween_h] = true
		vint_set_property(tween_h, "start_value", option_inactive.trim_w_src_w, option_inactive.trim_w_src_h)
		vint_set_property(tween_h, "end_value", option_active.trim_w_src_w, option_active.trim_w_src_h)

		-- size of w border
		h = vint_object_find("menu_frame_brdr_l", option_inactive.frame)
		tween_h = menu_create_tween("menu_transition10", h, "source_se", duration)
		Menu_transition_data.tweens[tween_h] = true
		vint_set_property(tween_h, "start_value", option_inactive.trim_w_src_w, option_inactive.trim_w_src_h)
		vint_set_property(tween_h, "end_value", option_active.trim_w_src_w, option_active.trim_w_src_h)

		-- position and size of ne
		h = vint_object_find("menu_mid_trm_btm_line_img2", option_inactive.frame)
		tween_h = menu_create_tween("menu_transition11", h, "anchor", duration)
		Menu_transition_data.tweens[tween_h] = true
		vint_set_property(tween_h, "start_value", option_inactive.trim_ne_pos_x, option_inactive.trim_ne_pos_y)
		vint_set_property(tween_h, "end_value", option_active.trim_ne_pos_x, option_active.trim_ne_pos_y)

		tween_h = menu_create_tween("menu_transition12", h, "source_se", duration)
		Menu_transition_data.tweens[tween_h] = true
		vint_set_property(tween_h, "start_value", option_inactive.trim_ne_src_w, option_inactive.trim_ne_src_h)
		vint_set_property(tween_h, "end_value", option_active.trim_ne_src_w, option_active.trim_ne_src_h)

		-- size of nw border
		h = vint_object_find("menu_mid_trm_btm_line_img1", option_inactive.frame)
		tween_h = menu_create_tween("menu_transition13", h, "source_se", duration)
		Menu_transition_data.tweens[tween_h] = true
		vint_set_property(tween_h, "start_value", option_inactive.trim_ne_src_w, option_inactive.trim_ne_src_h)
		vint_set_property(tween_h, "end_value", option_active.trim_ne_src_w, option_active.trim_ne_src_h)

		-- size of nw border
		h = vint_object_find("menu_mid_trm_top_m", option_inactive.frame)
		tween_h = menu_create_tween("menu_transition14", h, "anchor", duration)
		Menu_transition_data.tweens[tween_h] = true
		vint_set_property(tween_h, "start_value", option_inactive.trim_n_pos_x, option_inactive.trim_n_pos_y)
		vint_set_property(tween_h, "end_value", option_active.trim_n_pos_x, option_active.trim_n_pos_y)

		-- set up inactive menu clip
		h = vint_object_find("transition_clip", option_inactive.frame)
		vint_set_property(h, "clip_enabled", true)

		tween_h = menu_create_tween("menu_transition15", h, "offset", duration)
		Menu_transition_data.tweens[tween_h] = true

		if sweep_left == true then
			t1 = (menu_inactive.menu_width + 20)
			t2 = 20
		else
			t1 = (-menu_inactive.menu_width - 10)
			t2 = -10
		end

		vint_set_property(tween_h, "start_value", t2, 13)
		vint_set_property(tween_h, "end_value", t1, 13)

		tween_h = menu_create_tween("menu_transition16", h, "clip_size", duration)
		Menu_transition_data.tweens[tween_h] = true
		vint_set_property(tween_h, "start_value", (menu_inactive.menu_width + 26) , (menu_inactive.menu_height - 8) )
		vint_set_property(tween_h, "end_value", (menu_active.menu_width + 26), (menu_active.menu_height  - 8))

		-- set up active menu clip
		h = vint_object_find("transition_clip", option_active.frame)
		vint_set_property(h, "clip_enabled", true)

		if sweep_left == true then
			t1 = -menu_inactive.menu_width - 10
			t2 = -10
		else
			t1 = menu_inactive.menu_width  + 20
			t2 = 20
		end

		tween_h = menu_create_tween("menu_transition17", h, "offset", duration)
		Menu_transition_data.tweens[tween_h] = true
		vint_set_property(tween_h, "start_value", t1, 13) --t1, 13
		vint_set_property(tween_h, "end_value", t2, 13)



		tween_h = menu_create_tween("menu_transition18", h, "clip_size", duration)
		Menu_transition_data.tweens[tween_h] = true
		vint_set_property(tween_h, "start_value", (menu_inactive.menu_width + 26) , (menu_inactive.menu_height - 8) )
		vint_set_property(tween_h, "end_value", (menu_active.menu_width + 26), (menu_active.menu_height- 8) )

	end
end

-- special case function to just hide the current menu
Menu_hide_active_pending = false
function menu_hide_active()
	if Menu_transition_in_progress == true then
		Menu_hide_active_pending = true
		return
	end

	if Menu_active ~= 0 then
		local o = Menu_option_labels

		-- call on_leave for the active control
		local cur_item = Menu_active.highlighted_item
		local cb = Menu_control_callbacks[Menu_active[cur_item].type].on_leave
		if cb ~= nil then
			cb(Menu_option_labels[cur_item - Menu_active.first_vis_item], Menu_active[cur_item])
		end

		Menu_option_labels = Menu_option_labels_inactive
		Menu_option_labels_inactive = o

		Menu_inactive = Menu_active
		Menu_active = 0

		menu_transition_swap_begin()
	end
end

function menu_show(menu_data, transition)
	if Menu_transition_in_progress == true then
		-- access denied!
		return
	end

	if Menu_active ~= 0 then
		-- call on_leave for the active control
		local cur_item = Menu_active.highlighted_item
		local cb = Menu_control_callbacks[Menu_active[cur_item].type].on_leave
		if cb ~= nil then
			cb(Menu_option_labels[cur_item - Menu_active.first_vis_item], Menu_active[cur_item])
		end

		if Menu_active.on_exit ~= nil then
			Menu_active.on_exit(Menu_active)
		end

		if menu_data.parent_menu == nil then
			menu_data.parent_menu = Menu_active
		end

		-- swap the label set
		local labels = Menu_option_labels_inactive
		Menu_option_labels_inactive = Menu_option_labels
		Menu_option_labels = labels
	else
		menu_data.parent_menu = nil
	end

	Menu_inactive = Menu_active

	if menu_data.hide_header ~= true then
		menu_data.hide_header = false
	end

	if menu_data.hide_header == false then
		if menu_data.header_height == nil then
			menu_data.header_height = 64
		end
	elseif menu_data.hide_frame == true then
		menu_data.header_height = 0
	else
		-- leave room for ornate junk
		menu_data.header_height = 24
	end

	if menu_data.on_show ~= nil then
		menu_data.on_show(menu_data)
	end

	-- set up footer
	if menu_data.footer_height == nil then
		menu_data.footer_height = 0
	end

	if menu_data.footer_height == 0 then
		local footer = menu_data.footer

		if footer ~= nil and footer.footer_grp ~= nil then
			vint_object_destroy(footer.footer_grp)
		end

		menu_data.footer = nil
	end

	local hl_item = menu_data.highlighted_item
	if hl_item == nil or hl_item >= menu_data.num_items then
		hl_item = 0
	end

	local use_specified_header_width = true
	if menu_data.header_width == nil then
		menu_data.header_width = MENU_MIN_MENU_W
		use_specified_header_width = false
	end

	if menu_data.max_height == nil then
		menu_data.max_height = MENU_MAX_MENU_H
	end

	--Store off old max rows
	local old_menu_options_max_rows = 0
	if Menu_option_labels.max_rows ~= nil then
		old_menu_options_max_rows = Menu_option_labels.max_rows
	end

	--Calculate current max rows
	Menu_option_labels.max_rows = floor((menu_data.max_height - menu_data.header_height - menu_data.footer_height) / MENU_ITEM_HEIGHT)

	-- create more label objects
	for i = 1, Menu_option_labels.max_rows - 1 do
		if Menu_option_labels[i] == nil then
			Menu_option_labels[i] = {
				label_h = vint_object_clone(Menu_option_labels[0].label_h),
				stripe_h = vint_object_clone(Menu_option_labels[0].stripe_h)
			}
		end

	end

	-- scan to the first item not disabled
	if hl_item >= 0 then
		local start = hl_item
		while true do
			if menu_data[hl_item].disabled == true then
				hl_item = hl_item + 1

				if hl_item >= menu_data.num_items then
					hl_item = 0
				end

				if hl_item == start then
					hl_item = -1
					break
				end
			else
				break
			end
		end
	else
		hl_item = -1
	end

	menu_data.highlighted_item = hl_item
	menu_data.first_vis_item = -1

	-- set the header text
	vint_set_property(Menu_option_labels.frame, "visible", true)
	local show_header_elements = menu_data.hide_header == false

	if menu_data.hide_header == false then
		local header_text = vint_object_find("menu_header_text", Menu_option_labels.frame)

		if menu_data.header_obj ~= nil then
			local x, y = vint_get_property(header_text, "anchor")
			vint_set_property(menu_data.header_obj, "anchor", x, y)
			vint_set_property(menu_data.header_obj, "visible", true)
		elseif menu_data.header_label_crc ~= nil then
			vint_set_property(header_text, "text_tag_crc", menu_data.header_label_crc)
		elseif menu_data.header_label_str ~= nil then
			vint_set_property(header_text, "text_tag", menu_data.header_label_str)
		else	-- apearently no text or object, must be blank
			show_header_elements = false
		end

		--if the header is not custom then
		if use_specified_header_width == false then
			--Get size of the header text
			menu_data.header_width = element_get_actual_size(header_text)
		end
	end

	--show/hides header elements
	vint_set_property(vint_object_find("menu_header_text", Menu_option_labels.frame), "visible", show_header_elements)
	vint_set_property(vint_object_find("menu_bg_header_hr", Menu_option_labels.frame), "visible", show_header_elements)

	-- vert resize
	local num_rows = menu_data.num_items

	if num_rows > Menu_option_labels.max_rows then
		num_rows = Menu_option_labels.max_rows
	end

	local pos_x = 17
	local pos_y = menu_data.header_height + MENU_ITEM_HEIGHT * 0.5 + 5

	--Hide all rows that "could be there"
	for i = 0, old_menu_options_max_rows - 1 do
		vint_set_property(Menu_option_labels[i].label_h, "visible", false)
		vint_set_property(Menu_option_labels[i].stripe_h, "visible", false)
	end

	--Show Active Rows
	for i = 0, Menu_option_labels.max_rows - 1 do
		if i < num_rows then
			local object = Menu_option_labels[i]
			vint_set_property(object.label_h, "anchor", pos_x, pos_y)
			vint_set_property(object.stripe_h, "anchor", pos_x, pos_y)
			vint_set_property(object.label_h, "visible", true)
			vint_set_property(object.stripe_h, "visible", true)
			object.anchor_x = pos_x
			object.anchor_y = pos_y
			object.depth = Menu_option_labels.max_rows - i
			pos_y = pos_y + MENU_ITEM_HEIGHT
		end
	end

	-- special case: don't deal with the scroll bars if the only
	-- item wants it
	local handle_scroll_bar = true
	if num_rows == 1 then
		if Menu_control_callbacks[menu_data[0].type].uses_scroll_bar == true then
			handle_scroll_bar = false
		end
	end

	if handle_scroll_bar == true then
		if menu_data.num_items > Menu_option_labels.max_rows then
			-- unhide scroll bar
			local thumb_size = Menu_option_labels.max_rows / menu_data.num_items
			menu_scroll_bar_show()
			menu_scroll_bar_set_bar_height(Menu_option_labels.max_rows * MENU_ITEM_HEIGHT + 15)
			menu_scroll_bar_set_thumb_size(thumb_size)
			Menu_option_labels.scroll_bar_visible = true
		else
			-- hide scroll bar
			menu_scroll_bar_hide(Menu_option_labels.frame)
			Menu_option_labels.scroll_bar_visible = false
		end
	end

	-- horz size
	local label_h = Menu_option_labels[0].label_h
	local label_w, max_label_w = 0, 0
	local has_controls = false

	for i = 0, menu_data.num_items - 1 do
		local menu_item = menu_data[i]

		if menu_item.label_crc ~= nil then
			vint_set_property(label_h, "text_tag_crc", menu_item.label_crc)
		elseif menu_item.label ~= nil then
			vint_set_property(label_h, "text_tag", menu_item.label)
		else
			vint_set_property(label_h, "text_tag", "")
		end

		if menu_item.get_width ~= nil then
			label_w = menu_item.get_width(menu_item)
		elseif Menu_control_callbacks[menu_item.type].get_width ~= nil then
			label_w = Menu_control_callbacks[menu_item.type].get_width(menu_item)
		else
			label_w = element_get_actual_size(label_h)
		end

		if label_w > max_label_w then
			max_label_w = label_w
		end

		if Menu_control_callbacks[menu_item.type].has_control == true then
			has_controls = true
		end

		vint_set_property(label_h, "tint", 0.2, 0.2, 0.2)

	end

	--Get the control width for each menu item
	local control_min_width = 0
	for i = 0, menu_data.num_items - 1 do
		local menu_item = menu_data[i]
		local item_type = menu_data[i].type

		--Get the minimum width for the control
		local cb = Menu_control_callbacks[item_type]
		if cb ~= nil then
			if cb.get_min_width ~= nil then
				local control_width = cb.get_min_width(menu_item)
				if control_width > control_min_width then
					control_min_width = control_width
				end
			end
		end
	end
	--Our control min width cannot be less than the default
	if control_min_width < MENU_CONTROL_W then
		control_min_width = MENU_CONTROL_W
	end

	--Store the control width for the future
	menu_data.control_width = control_min_width

	if Menu_option_labels.scroll_bar_visible == true then
		max_label_w = max_label_w + 35
	end

	if max_label_w < MENU_MIN_LABEL_W then
		max_label_w = MENU_MIN_LABEL_W
	end

	if menu_data.max_label_w ~= nil then
		if max_label_w > menu_data.max_label_w then
			max_label_w = menu_data.max_label_w
		end
	end

	Menu_option_labels.max_label_w = max_label_w

	-- height and width of the area occupied by labels and controls
	local height, width

	-- special case: this may be a single control menu so it might tell me it's height
	if num_rows == 1 then
		local cb = Menu_control_callbacks[menu_data[0].type].get_height
		if cb ~= nil then
			height = menu_data.header_height + cb(menu_data[0])
		end
	end

	-- check to see if menu would like to dictate the size
	if menu_data.get_width ~= nil then
		local menu_width = 10 + menu_data.get_width(menu_data)
		width = menu_width
	end

	if menu_data.get_height ~= nil then
		height = menu_data.header_height + menu_data.get_height(menu_data)
	end

	-- standard case: each item is MENU_ITEM_HEIGHT pixels high
	if height == nil then
		height = pos_y - MENU_ITEM_HEIGHT + 15
	end

	if menu_data.footer_height ~= 0 then
		height = height + menu_data.footer_height + 15
	end

	-- position the footer
	if menu_data.footer_height ~= 0 and menu_data.footer ~= nil then
		menu_data.footer.pos_y = height - menu_data.footer_height - 2
		vint_set_property(menu_data.footer.footer_grp, "anchor", 20, menu_data.footer.pos_y)
	end

	--Make sure our width is not less than the control width
	if width == nil then
		width = max_label_w

		if has_controls == true then
			width = width + menu_data.control_width
			if Menu_option_labels.scroll_bar_visible == true then
				--controls and scrollbar
				width = width + 40
			end
		end
	end

	--If our header is wider than our menu then expand
	if menu_data.header_width > width then
		width = menu_data.header_width
	end

	--If menu width is less than the mininum size then set it so...
	if width < MENU_MIN_MENU_W then
		width = MENU_MIN_MENU_W
	end

	-- make room for ornate
	width = width + 22

	local bg_h

	--Resize Selector bar
	local frame_h = Menu_option_labels.frame
	local sel_bar_width = floor(width) - 8

	if Menu_option_labels.scroll_bar_visible == true then
		sel_bar_width = sel_bar_width - 40
	end

	Menu_option_labels.item_width = sel_bar_width

	bg_h = vint_object_find("menu_sel_bar_w", frame_h)
	vint_set_property(bg_h, "source_se", sel_bar_width, 36)

	bg_h = vint_object_find("menu_sel_bar_w_hl", frame_h)
	vint_set_property(bg_h, "source_se", sel_bar_width, 36)

	bg_h = vint_object_find("menu_sel_bar_e", frame_h)
	local menu_bar_e_anchor_x, menu_bar_e_anchor_y = vint_get_property(bg_h, "anchor")
	menu_bar_e_anchor_x = sel_bar_width + 5
	vint_set_property(bg_h, "anchor", menu_bar_e_anchor_x, menu_bar_e_anchor_y)

	local bg_h = vint_object_find("menu_sel_bar_e_hl", frame_h)
	vint_set_property(bg_h, "anchor", menu_bar_e_anchor_x - 1, menu_bar_e_anchor_y)

	vint_set_property(Menu_option_labels.hl_clip, "offset", 12, -15)
	vint_set_property(Menu_option_labels.hl_clip, "clip_size", width - 17, MENU_ITEM_HEIGHT)

	--Adjust scrollbar
	if Menu_option_labels.scroll_bar_visible == true then
		menu_scroll_bar_set_pos(width - 25, menu_data.header_height + 2)
	end

	if menu_data.hide_frame ~= true then
		menu_data.hide_frame = false
	end

	vint_set_property(vint_object_find("menu_bg", frame_h), "visible", menu_data.hide_frame == false)
	vint_set_property(vint_object_find("menu_fg", frame_h), "visible", menu_data.hide_frame == false)

	bg_h = vint_object_find("menu_frame_middle", frame_h)
	Menu_option_labels.trim_c_scale_x = width / 16
	Menu_option_labels.trim_c_scale_y = height / 16
	vint_set_property(bg_h, "scale", Menu_option_labels.trim_c_scale_x, Menu_option_labels.trim_c_scale_y)

	bg_h = vint_object_find("menu_frame_brdr_l", frame_h)
	Menu_option_labels.trim_w_src_w = 19
	Menu_option_labels.trim_w_src_h = height
	vint_set_property(bg_h, "source_se", Menu_option_labels.trim_w_src_w, Menu_option_labels.trim_w_src_h)

	bg_h = vint_object_find("menu_frame_brdr_r", frame_h)
	Menu_option_labels.trim_w_pos_x = width + 17
	Menu_option_labels.trim_w_pos_y = 13
	vint_set_property(bg_h, "anchor", Menu_option_labels.trim_w_pos_x, Menu_option_labels.trim_w_pos_y)
	vint_set_property(bg_h, "source_se", Menu_option_labels.trim_w_src_w, Menu_option_labels.trim_w_src_h)

	bg_h = vint_object_find("menu_mid_trm_btm_right", frame_h)
	Menu_option_labels.trim_se_x = width - 50
	Menu_option_labels.trim_se_y = height - 36
	vint_set_property(bg_h, "anchor", Menu_option_labels.trim_se_x, Menu_option_labels.trim_se_y)

	bg_h = vint_object_find("menu_mid_trm_btm_line_img", frame_h)
	Menu_option_labels.trim_s_pos_x = 6
	Menu_option_labels.trim_s_pos_y = height + 7
	Menu_option_labels.trim_s_src_w = width - 50
	Menu_option_labels.trim_s_src_h = 12
	vint_set_property(bg_h, "anchor", Menu_option_labels.trim_s_pos_x, Menu_option_labels.trim_s_pos_y)
	vint_set_property(bg_h, "source_se", Menu_option_labels.trim_s_src_w, Menu_option_labels.trim_s_src_h)

	bg_h = vint_object_find("menu_bg_header_hr", frame_h)

	vint_set_property(bg_h, "anchor", 23, menu_data.header_height - 10)
	vint_set_property(bg_h, "source_se", width - 10, 10)

	if menu_data.footer_height ~= 0 and menu_data.footer ~= nil then
		menu_data.footer.hr_h = vint_object_clone(bg_h)
		vint_set_property(menu_data.footer.hr_h, "anchor", 23, menu_data.footer.pos_y - 8)
		vint_set_property(bg_h, "source_se", width - 10, 10)
	end

	Menu_option_labels.trim_ne_src_w = width / 2 - 60
	Menu_option_labels.trim_ne_src_h = 12
	bg_h = vint_object_find("menu_mid_trm_btm_line_img1", frame_h)
	vint_set_property(bg_h, "source_se", Menu_option_labels.trim_ne_src_w, Menu_option_labels.trim_ne_src_h)

	Menu_option_labels.trim_ne_pos_x = width + 35
	Menu_option_labels.trim_ne_pos_y = 9
	bg_h = vint_object_find("menu_mid_trm_btm_line_img2", frame_h)
	vint_set_property(bg_h, "anchor", Menu_option_labels.trim_ne_pos_x, Menu_option_labels.trim_ne_pos_y)
	vint_set_property(bg_h, "source_se", Menu_option_labels.trim_ne_src_w, Menu_option_labels.trim_ne_src_w)

	Menu_option_labels.trim_n_pos_x = (width + 38) / 2
	Menu_option_labels.trim_n_pos_y = 12
	bg_h = vint_object_find("menu_mid_trm_top_m", frame_h)
	vint_set_property(bg_h, "anchor", Menu_option_labels.trim_n_pos_x, Menu_option_labels.trim_n_pos_y)

	--	Set the clipping area
	vint_set_property(Menu_option_labels.clip_h, "clip_size", sel_bar_width + 10, height)

	Menu_active = menu_data
	menu_data.menu_height = height
	menu_data.menu_width = width

	Menu_new = true

	menu_update_nav_bar(Menu_active.highlighted_item)

	if Menu_active.on_post_show ~= nil then
		Menu_active.on_post_show(Menu_active)
	end

	btn_tips_update()

	if transition == MENU_TRANSITION_SWAP then
		menu_transition_swap_begin()
	elseif transition == MENU_TRANSITION_SWEEP_RIGHT then
		menu_transition_sweep_begin(false)
	elseif transition == MENU_TRANSITION_SWEEP_LEFT then
		menu_transition_sweep_begin(true)
	else
		menu_input_block(true)
		menu_transition_complete()
	end
end

--CDPLC: this function is nearly a copy of of menu_show(). Changed fragments are marked in order to ease future merges.
function menu_resize()

--CDPLC: whole fragment commented
--	if Menu_transition_in_progress == true then
--		-- access denied!
--		return
--	end

--	if Menu_active ~= 0 then
--		-- call on_leave for the active control
--		local cur_item = Menu_active.highlighted_item
--		local cb = Menu_control_callbacks[Menu_active[cur_item].type].on_leave
--		if cb ~= nil then
--			cb(Menu_option_labels[cur_item - Menu_active.first_vis_item], Menu_active[cur_item])
--		end

--		if Menu_active.on_exit ~= nil then
--			Menu_active.on_exit(Menu_active)
--		end

--		if menu_data.parent_menu == nil then
--			menu_data.parent_menu = Menu_active
--		end

--		-- swap the label set
--		local labels = Menu_option_labels_inactive
--		Menu_option_labels_inactive = Menu_option_labels
--		Menu_option_labels = labels
--	else
--		menu_data.parent_menu = nil
--	end

--	Menu_inactive = Menu_active

	--CDPLC: added
	local menu_data = Menu_active

	if menu_data.hide_header ~= true then
		menu_data.hide_header = false
	end

	if menu_data.hide_header == false then
		if menu_data.header_height == nil then
			menu_data.header_height = 64
		end
	elseif menu_data.hide_frame == true then
		menu_data.header_height = 0
	else
		-- leave room for ornate junk
		menu_data.header_height = 24
	end

	if menu_data.on_show ~= nil then
		menu_data.on_show(menu_data)
	end

	-- set up footer
	if menu_data.footer_height == nil then
		menu_data.footer_height = 0
	end

	if menu_data.footer_height == 0 then
		local footer = menu_data.footer

		if footer ~= nil and footer.footer_grp ~= nil then
			vint_object_destroy(footer.footer_grp)
		end

		menu_data.footer = nil
	end

	local hl_item = menu_data.highlighted_item
	if hl_item == nil or hl_item >= menu_data.num_items then
		hl_item = 0
	end

	local use_specified_header_width = true
	if menu_data.header_width == nil then
		menu_data.header_width = MENU_MIN_MENU_W
		use_specified_header_width = false
	end

	if menu_data.max_height == nil then
		menu_data.max_height = MENU_MAX_MENU_H
	end

	--Store off old max rows
	local old_menu_options_max_rows = 0
	if Menu_option_labels.max_rows ~= nil then
		old_menu_options_max_rows = Menu_option_labels.max_rows
	end

	--Calculate current max rows
	Menu_option_labels.max_rows = floor((menu_data.max_height - menu_data.header_height - menu_data.footer_height) / MENU_ITEM_HEIGHT)

	-- create more label objects
	for i = 1, Menu_option_labels.max_rows - 1 do
		if Menu_option_labels[i] == nil then
			Menu_option_labels[i] = {
				label_h = vint_object_clone(Menu_option_labels[0].label_h),
				stripe_h = vint_object_clone(Menu_option_labels[0].stripe_h)
			}
		end

	end

	-- scan to the first item not disabled
	if hl_item >= 0 then
		local start = hl_item
		while true do
			if menu_data[hl_item].disabled == true then
				hl_item = hl_item + 1

				if hl_item >= menu_data.num_items then
					hl_item = 0
				end

				if hl_item == start then
					hl_item = -1
					break
				end
			else
				break
			end
		end
	else
		hl_item = -1
	end

	menu_data.highlighted_item = hl_item
	menu_data.first_vis_item = -1

	-- set the header text
	vint_set_property(Menu_option_labels.frame, "visible", true)
	local show_header_elements = menu_data.hide_header == false

	if menu_data.hide_header == false then
		local header_text = vint_object_find("menu_header_text", Menu_option_labels.frame)

		if menu_data.header_obj ~= nil then
			local x, y = vint_get_property(header_text, "anchor")
			vint_set_property(menu_data.header_obj, "anchor", x, y)
			vint_set_property(menu_data.header_obj, "visible", true)
		elseif menu_data.header_label_crc ~= nil then
			vint_set_property(header_text, "text_tag_crc", menu_data.header_label_crc)
		elseif menu_data.header_label_str ~= nil then
			vint_set_property(header_text, "text_tag", menu_data.header_label_str)
		else	-- apearently no text or object, must be blank
			show_header_elements = false
		end

		--if the header is not custom then
		if use_specified_header_width == false then
			--Get size of the header text
			menu_data.header_width = element_get_actual_size(header_text)
		end
	end

	--show/hides header elements
	vint_set_property(vint_object_find("menu_header_text", Menu_option_labels.frame), "visible", show_header_elements)
	vint_set_property(vint_object_find("menu_bg_header_hr", Menu_option_labels.frame), "visible", show_header_elements)

	-- vert resize
	local num_rows = menu_data.num_items

	if num_rows > Menu_option_labels.max_rows then
		num_rows = Menu_option_labels.max_rows
	end

	local pos_x = 17
	local pos_y = menu_data.header_height + MENU_ITEM_HEIGHT * 0.5 + 5

	--Hide all rows that "could be there"
	for i = 0, old_menu_options_max_rows - 1 do
		vint_set_property(Menu_option_labels[i].label_h, "visible", false)
		vint_set_property(Menu_option_labels[i].stripe_h, "visible", false)
	end

	--Show Active Rows
	for i = 0, Menu_option_labels.max_rows - 1 do
		if i < num_rows then
			local object = Menu_option_labels[i]
			vint_set_property(object.label_h, "anchor", pos_x, pos_y)
			vint_set_property(object.stripe_h, "anchor", pos_x, pos_y)
			vint_set_property(object.label_h, "visible", true)
			vint_set_property(object.stripe_h, "visible", true)
			object.anchor_x = pos_x
			object.anchor_y = pos_y
			object.depth = Menu_option_labels.max_rows - i
			pos_y = pos_y + MENU_ITEM_HEIGHT
		end
	end

	-- special case: don't deal with the scroll bars if the only
	-- item wants it
	local handle_scroll_bar = true
	if num_rows == 1 then
		if Menu_control_callbacks[menu_data[0].type].uses_scroll_bar == true then
			handle_scroll_bar = false
		end
	end

	if handle_scroll_bar == true then
		if menu_data.num_items > Menu_option_labels.max_rows then
			-- unhide scroll bar
			local thumb_size = Menu_option_labels.max_rows / menu_data.num_items
			menu_scroll_bar_show()
			menu_scroll_bar_set_bar_height(Menu_option_labels.max_rows * MENU_ITEM_HEIGHT + 15)
			menu_scroll_bar_set_thumb_size(thumb_size)
			Menu_option_labels.scroll_bar_visible = true
		else
			-- hide scroll bar
			menu_scroll_bar_hide(Menu_option_labels.frame)
			Menu_option_labels.scroll_bar_visible = false
		end
	end

	-- horz size
	local label_h = Menu_option_labels[0].label_h
	local label_w, max_label_w = 0, 0
	local has_controls = false

	for i = 0, menu_data.num_items - 1 do
		local menu_item = menu_data[i]

		if menu_item.label_crc ~= nil then
			vint_set_property(label_h, "text_tag_crc", menu_item.label_crc)
		elseif menu_item.label ~= nil then
			vint_set_property(label_h, "text_tag", menu_item.label)
		else
			vint_set_property(label_h, "text_tag", "")
		end

		if menu_item.get_width ~= nil then
			label_w = menu_item.get_width(menu_item)
		elseif Menu_control_callbacks[menu_item.type].get_width ~= nil then
			label_w = Menu_control_callbacks[menu_item.type].get_width(menu_item)
		else
			label_w = element_get_actual_size(label_h)
		end

		if label_w > max_label_w then
			max_label_w = label_w
		end

		if Menu_control_callbacks[menu_item.type].has_control == true then
			has_controls = true
		end

		vint_set_property(label_h, "tint", 0.2, 0.2, 0.2)

	end

	--Get the control width for each menu item
	local control_min_width = 0
	for i = 0, menu_data.num_items - 1 do
		local menu_item = menu_data[i]
		local item_type = menu_data[i].type

		--Get the minimum width for the control
		local cb = Menu_control_callbacks[item_type]
		if cb ~= nil then
			if cb.get_min_width ~= nil then
				local control_width = cb.get_min_width(menu_item)
				if control_width > control_min_width then
					control_min_width = control_width
				end
			end
		end
	end
	--Our control min width cannot be less than the default
	if control_min_width < MENU_CONTROL_W then
		control_min_width = MENU_CONTROL_W
	end

	--Store the control width for the future
	menu_data.control_width = control_min_width

	if Menu_option_labels.scroll_bar_visible == true then
		max_label_w = max_label_w + 35
	end

	if max_label_w < MENU_MIN_LABEL_W then
		max_label_w = MENU_MIN_LABEL_W
	end

	if menu_data.max_label_w ~= nil then
		if max_label_w > menu_data.max_label_w then
			max_label_w = menu_data.max_label_w
		end
	end

	Menu_option_labels.max_label_w = max_label_w

	-- height and width of the area occupied by labels and controls
	local height, width

	-- special case: this may be a single control menu so it might tell me it's height
	if num_rows == 1 then
		local cb = Menu_control_callbacks[menu_data[0].type].get_height
		if cb ~= nil then
			height = menu_data.header_height + cb(menu_data[0])
		end
	end

	-- check to see if menu would like to dictate the size
	if menu_data.get_width ~= nil then
		local menu_width = 10 + menu_data.get_width(menu_data)
		width = menu_width
	end

	if menu_data.get_height ~= nil then
		height = menu_data.header_height + menu_data.get_height(menu_data)
	end

	-- standard case: each item is MENU_ITEM_HEIGHT pixels high
	if height == nil then
		height = pos_y - MENU_ITEM_HEIGHT + 15
	end

	if menu_data.footer_height ~= 0 then
		height = height + menu_data.footer_height + 15
	end

	-- position the footer
	if menu_data.footer_height ~= 0 and menu_data.footer ~= nil then
		menu_data.footer.pos_y = height - menu_data.footer_height - 2
		vint_set_property(menu_data.footer.footer_grp, "anchor", 20, menu_data.footer.pos_y)
	end

	--Make sure our width is not less than the control width
	if width == nil then
		width = max_label_w

		if has_controls == true then
			width = width + menu_data.control_width
			if Menu_option_labels.scroll_bar_visible == true then
				--controls and scrollbar
				width = width + 40
			end
		end
	end

	--If our header is wider than our menu then expand
	if menu_data.header_width > width then
		width = menu_data.header_width
	end

	--If menu width is less than the mininum size then set it so...
	if width < MENU_MIN_MENU_W then
		width = MENU_MIN_MENU_W
	end

	-- make room for ornate
	width = width + 22

	local bg_h

	--Resize Selector bar
	local frame_h = Menu_option_labels.frame
	local sel_bar_width = floor(width) - 8

	if Menu_option_labels.scroll_bar_visible == true then
		sel_bar_width = sel_bar_width - 40
	end

	Menu_option_labels.item_width = sel_bar_width

	bg_h = vint_object_find("menu_sel_bar_w", frame_h)
	vint_set_property(bg_h, "source_se", sel_bar_width, 36)

	bg_h = vint_object_find("menu_sel_bar_w_hl", frame_h)
	vint_set_property(bg_h, "source_se", sel_bar_width, 36)

	bg_h = vint_object_find("menu_sel_bar_e", frame_h)
	local menu_bar_e_anchor_x, menu_bar_e_anchor_y = vint_get_property(bg_h, "anchor")
	menu_bar_e_anchor_x = sel_bar_width + 5
	vint_set_property(bg_h, "anchor", menu_bar_e_anchor_x, menu_bar_e_anchor_y)

	local bg_h = vint_object_find("menu_sel_bar_e_hl", frame_h)
	vint_set_property(bg_h, "anchor", menu_bar_e_anchor_x - 1, menu_bar_e_anchor_y)

	vint_set_property(Menu_option_labels.hl_clip, "offset", 12, -15)
	vint_set_property(Menu_option_labels.hl_clip, "clip_size", width - 17, MENU_ITEM_HEIGHT)

	--Adjust scrollbar
	if Menu_option_labels.scroll_bar_visible == true then
		menu_scroll_bar_set_pos(width - 25, menu_data.header_height + 2)
	end

	if menu_data.hide_frame ~= true then
		menu_data.hide_frame = false
	end

	vint_set_property(vint_object_find("menu_bg", frame_h), "visible", menu_data.hide_frame == false)
	vint_set_property(vint_object_find("menu_fg", frame_h), "visible", menu_data.hide_frame == false)

	bg_h = vint_object_find("menu_frame_middle", frame_h)
	Menu_option_labels.trim_c_scale_x = width / 16
	Menu_option_labels.trim_c_scale_y = height / 16
	vint_set_property(bg_h, "scale", Menu_option_labels.trim_c_scale_x, Menu_option_labels.trim_c_scale_y)

	bg_h = vint_object_find("menu_frame_brdr_l", frame_h)
	Menu_option_labels.trim_w_src_w = 19
	Menu_option_labels.trim_w_src_h = height
	vint_set_property(bg_h, "source_se", Menu_option_labels.trim_w_src_w, Menu_option_labels.trim_w_src_h)

	bg_h = vint_object_find("menu_frame_brdr_r", frame_h)
	Menu_option_labels.trim_w_pos_x = width + 17
	Menu_option_labels.trim_w_pos_y = 13
	vint_set_property(bg_h, "anchor", Menu_option_labels.trim_w_pos_x, Menu_option_labels.trim_w_pos_y)
	vint_set_property(bg_h, "source_se", Menu_option_labels.trim_w_src_w, Menu_option_labels.trim_w_src_h)

	bg_h = vint_object_find("menu_mid_trm_btm_right", frame_h)
	Menu_option_labels.trim_se_x = width - 50
	Menu_option_labels.trim_se_y = height - 36
	vint_set_property(bg_h, "anchor", Menu_option_labels.trim_se_x, Menu_option_labels.trim_se_y)

	bg_h = vint_object_find("menu_mid_trm_btm_line_img", frame_h)
	Menu_option_labels.trim_s_pos_x = 6
	Menu_option_labels.trim_s_pos_y = height + 7
	Menu_option_labels.trim_s_src_w = width - 50
	Menu_option_labels.trim_s_src_h = 12
	vint_set_property(bg_h, "anchor", Menu_option_labels.trim_s_pos_x, Menu_option_labels.trim_s_pos_y)
	vint_set_property(bg_h, "source_se", Menu_option_labels.trim_s_src_w, Menu_option_labels.trim_s_src_h)

	bg_h = vint_object_find("menu_bg_header_hr", frame_h)

	vint_set_property(bg_h, "anchor", 23, menu_data.header_height - 10)
	vint_set_property(bg_h, "source_se", width - 10, 10)

	if menu_data.footer_height ~= 0 and menu_data.footer ~= nil then
		menu_data.footer.hr_h = vint_object_clone(bg_h)
		vint_set_property(menu_data.footer.hr_h, "anchor", 23, menu_data.footer.pos_y - 8)
		vint_set_property(bg_h, "source_se", width - 10, 10)
	end

	Menu_option_labels.trim_ne_src_w = width / 2 - 60
	Menu_option_labels.trim_ne_src_h = 12
	bg_h = vint_object_find("menu_mid_trm_btm_line_img1", frame_h)
	vint_set_property(bg_h, "source_se", Menu_option_labels.trim_ne_src_w, Menu_option_labels.trim_ne_src_h)

	Menu_option_labels.trim_ne_pos_x = width + 35
	Menu_option_labels.trim_ne_pos_y = 9
	bg_h = vint_object_find("menu_mid_trm_btm_line_img2", frame_h)
	vint_set_property(bg_h, "anchor", Menu_option_labels.trim_ne_pos_x, Menu_option_labels.trim_ne_pos_y)
	vint_set_property(bg_h, "source_se", Menu_option_labels.trim_ne_src_w, Menu_option_labels.trim_ne_src_w)

	Menu_option_labels.trim_n_pos_x = (width + 38) / 2
	Menu_option_labels.trim_n_pos_y = 12
	bg_h = vint_object_find("menu_mid_trm_top_m", frame_h)
	vint_set_property(bg_h, "anchor", Menu_option_labels.trim_n_pos_x, Menu_option_labels.trim_n_pos_y)

	--	Set the clipping area
	vint_set_property(Menu_option_labels.clip_h, "clip_size", sel_bar_width + 10, height)

	Menu_active = menu_data
	menu_data.menu_height = height
	menu_data.menu_width = width

	Menu_new = true

	menu_update_nav_bar(Menu_active.highlighted_item)

	if Menu_active.on_post_show ~= nil then
		Menu_active.on_post_show(Menu_active)
	end

	btn_tips_update()

	--CDPLC: added, set transition to none
	local transition = MENU_TRANSITION_NONE

	if transition == MENU_TRANSITION_SWAP then
		menu_transition_swap_begin()
	elseif transition == MENU_TRANSITION_SWEEP_RIGHT then
		menu_transition_sweep_begin(false)
	elseif transition == MENU_TRANSITION_SWEEP_LEFT then
		menu_transition_sweep_begin(true)
	else
		menu_input_block(true)
		menu_transition_complete()
	end
end

-- updates the text prop on all labels
-- called when menu is built or scrolls
function menu_update_labels()
	local h, ch, item, label_w, control

	local control_min_width = 0
	local control_width = 0

	-- set the labels and hide unused
	for i = 0, Menu_option_labels.max_rows - 1 do
		h = Menu_option_labels[i].label_h

		item = Menu_active.first_vis_item + i

		if item < Menu_active.num_items then
			local item_type = Menu_active[item].type
			vint_set_property(h, "visible", true)

			if Menu_active[item].label_crc ~= nil then
				vint_set_property(h, "text_tag_crc", Menu_active[item].label_crc)
			else
				vint_set_property(h, "text_tag", Menu_active[item].label)
			end

			if Menu_active[item].disabled == true and Menu_active[item].dimm_disabled == true then
				if Menu_active[item].it_is_caption_label == true then
					vint_set_property(h, "tint", 0.2, 0.5, 0.8 )
				else
					vint_set_property(h, "tint", 0.17, 0.17, 0.2)
				end
			else
				vint_set_property(h, "tint", 0.364, 0.368, 0.376)
			end

			-- maybe hide stripe
			if Menu_control_callbacks[Menu_active[item].type].hide_label_stripe == true then
				vint_set_property(Menu_option_labels[i].stripe_h, "visible", false)
			else
				vint_set_property(Menu_option_labels[i].stripe_h, "visible", true)
			end

			-- update control
			local cb = Menu_control_callbacks[item_type]
			if cb ~= nil then
				if cb.on_show ~= nil then
					cb.on_show(Menu_option_labels[i], Menu_active[item])
				else
					if Menu_option_labels[i].control ~= nil then
						menu_release_control(Menu_option_labels[i].control)
						Menu_option_labels[i].control = nil
					end
				end

				--set width of control using the base control width of the menu set in menu_show()
				if cb.set_width ~= nil then
					cb.set_width(Menu_option_labels[i], Menu_active[item], Menu_active.control_width)
				end

				-- hmmmm... is this right?  -sdr
				if cb.on_leave ~= nil then
					cb.on_leave(Menu_option_labels[i], Menu_active[item])
				end
			end

		else
			vint_set_property(Menu_option_labels[i].stripe_h, "visible", false)
			vint_set_property(h, "visible", false)
		end
	end

	-- update scroll bar
	if Menu_option_labels.scroll_bar_visible == true then
		menu_scroll_bar_set_thumb_pos(Menu_active.first_vis_item / (Menu_active.num_items - Menu_option_labels.max_rows) )
	end
end

function limit(value, low, high)
	if value < low then
		value = low
	elseif value > high then
		value = high
	end

	return value
end

-- moves the nav bar and checks for possible scrolling
function menu_update_nav_bar(new_item)
	-- check to see if we need to scroll
	local first_vis_item = 0
	local prev_first_vis_item = Menu_active.first_vis_item
	local prev_row = Menu_active.highlighted_item - prev_first_vis_item

	if Menu_active.num_items > Menu_option_labels.max_rows then
		local half_max = floor(Menu_option_labels.max_rows / 2)
		first_vis_item = limit(new_item - half_max, 0, Menu_active.num_items - Menu_option_labels.max_rows)
	end

	-- maybe scroll
	if first_vis_item ~= Menu_active.first_vis_item then
		Menu_active.first_vis_item = first_vis_item
		menu_update_labels()
	else
		-- Unhighlight control
		if Menu_option_labels[prev_row].control ~= nil then
			local cb = Menu_control_callbacks[Menu_option_labels[prev_row].control.type].on_leave
			if cb ~= nil then
				cb(Menu_option_labels[prev_row], Menu_active[Menu_active.highlighted_item])
			end
		end
	end

	-- highlight current control
	if Menu_active.num_items < 1 then
		-- stop crashies
		return
	end

	-- no item highlighted - not entirely sure what Jeff wants so I'll just bail
	if new_item == -1 then
		return
	end

	local hilight_row = new_item - first_vis_item

	------
	-- Move the on enter callback from THIS spot to the bottom so that
	-- the hl_bar_sel_label would be correct when its called.
	-- Not sure if it can break anything anywhere - DAD 1/8/08
	------

	if Menu_fading_label ~= 0 then
		vint_set_property(Menu_fading_label, "tint", 0.3647, 0.3686, 0.3765)
		Menu_fading_label = 0
	end

	if Menu_control_callbacks[Menu_active[new_item].type].hide_select_bar == true then
		--Control type so we do different types of fading

		vint_set_property(Menu_option_labels.hl_bar, "visible", false)

		local anim_h = vint_object_find("menu_option_label_in_anim")
		vint_set_property(anim_h, "target_handle", Menu_option_labels[hilight_row].label_h)
		local twn_h = vint_object_find("menu_option_label_in_tint_twn", anim_h)
		vint_set_property(twn_h, "state", "paused")
		lua_play_anim(anim_h, 0)
	else
		vint_set_property(Menu_option_labels.hl_bar, "visible", true)

		--Move Highlight Bar
		vint_set_property(Menu_option_labels.hl_bar, "anchor",
			Menu_option_labels[hilight_row].anchor_x - 5, Menu_option_labels[hilight_row].anchor_y)

		--Update text of highlight bar
		local hl_bar_label_h = vint_object_find("menu_sel_bar_label", Menu_option_labels.hl_bar)
		local menu_item = Menu_active[new_item]

		local show_label = false
		if menu_item.label_crc ~= nil then
			vint_set_property(hl_bar_label_h, "text_tag_crc", menu_item.label_crc)
			show_label = true
		elseif menu_item.label ~= nil then
			vint_set_property(hl_bar_label_h, "text_tag", menu_item.label)
			show_label = true
		end

		vint_set_property(hl_bar_label_h, "visible", show_label)

		--Retarget Nav Fade In Animation and Play
		vint_set_property(vint_object_find("sel_bar_in_twn"), "target_handle", Menu_option_labels.hl_bar)
		lua_play_anim(vint_object_find("menu_sel_bar_fade_in_anim"), 0)
	end

	if Menu_new == false then

		local item_diff = hilight_row + Menu_active.highlighted_item - new_item
		-- if we have scrolled, move all of the fading hl bars
		if prev_first_vis_item ~= first_vis_item then
			for index, value in Menu_nav_bars do
				--calculate offset from current first vis row
				local highlight_row_offset = value.item_num - first_vis_item

				if highlight_row_offset >= Menu_option_labels.max_rows or highlight_row_offset < 0 then
					-- kill the item if it has scrolled off the screen
					menu_duplicate_nav_bar_kill(index)
				else
					-- alls good, move it
					vint_set_property(value.obj_h, "anchor",
						Menu_option_labels[highlight_row_offset].anchor_x - 5, Menu_option_labels[highlight_row_offset].anchor_y)
				end
			end
		end

		if item_diff < Menu_option_labels.max_rows and item_diff >= 0 then
			local target_row = Menu_active.highlighted_item - first_vis_item

			if Menu_control_callbacks[Menu_active[Menu_active.highlighted_item].type].hide_select_bar == true then

					if Menu_control_callbacks[Menu_active[new_item].type].hide_select_bar ~= true then
						--Disable the fade in tween only if the new item doesn't have a select bar.
						--This is because the tween maintains its old target so it needs to be turned off.
						local anim_h = vint_object_find("menu_option_label_in_anim")
						vint_set_property(anim_h, "is_paused", true)
						local twn_h = vint_object_find("menu_option_label_in_tint_twn", anim_h)
						vint_set_property(twn_h, "state", "disabled")
					end

				vint_set_property(Menu_option_labels[target_row].label_h, "tint", 0.3647, 0.3686, 0.3765)
			else
				-- dup nav bar and fade it
				local nav_bar_clone = vint_object_clone(Menu_option_labels.hl_bar)
				vint_set_property(nav_bar_clone, "anchor", Menu_option_labels[target_row].anchor_x - 5, Menu_option_labels[target_row].anchor_y)

				--Clone, Retarget and Play Animation to fade out
				local nav_bar_anim_clone = vint_object_clone(vint_object_find("menu_sel_bar_fade_out_anim"))
				local nav_bar_twn = vint_object_find("sel_bar_out_twn", nav_bar_anim_clone)
				vint_set_property(nav_bar_twn, "target_handle", nav_bar_clone)
				vint_set_property(nav_bar_twn, "end_event", "menu_duplicate_nav_bar_kill")
				lua_play_anim(nav_bar_anim_clone, 0)

				--Update text of highlight bar
				local hl_bar_label_h = vint_object_find("menu_sel_bar_label", nav_bar_clone)

				if Menu_active[Menu_active.highlighted_item].label_crc ~= nil then
					vint_set_property(hl_bar_label_h, "text_tag_crc", Menu_active[Menu_active.highlighted_item].label_crc)
				else
					vint_set_property(hl_bar_label_h, "text_tag", Menu_active[Menu_active.highlighted_item].label)
				end

				--Store References
				Menu_nav_bars[nav_bar_twn] = {
					obj_h = nav_bar_clone,
					anim_h = nav_bar_anim_clone,
					twn_h =  nav_bar_twn,
					item_num = Menu_active.highlighted_item,
				}
			end
		end
	else
		--Retarget Pulse Animation
		local target = vint_object_find("menu_sel_bar_e_hl", Menu_option_labels.hl_bar)
		vint_set_property(vint_object_find("menu_item_pulse_0_tween"), "target_handle", target)
		target = vint_object_find("menu_sel_bar_w_hl", Menu_option_labels.hl_bar)
		vint_set_property(vint_object_find("menu_item_pulse_1_tween"), "target_handle", target)

		Menu_new = false
	end

	Menu_option_labels.highlighted = hilight_row
	Menu_active.highlighted_item = new_item

	local cb = Menu_control_callbacks[Menu_active[new_item].type]
	if cb ~= nil then
		if cb.on_enter ~= nil then
			cb.on_enter(Menu_option_labels[hilight_row], Menu_active[new_item])
		end
	end

end

function menu_duplicate_nav_bar_kill(tween_h, event_name)
	for index, value in Menu_nav_bars do
		if value.twn_h == tween_h then
			vint_object_destroy(value.obj_h)
			vint_object_destroy(value.anim_h)
			vint_set_property(value.label_h, "tint", 0.364, 0.368, 0.376)
			Menu_nav_bars[index] = nil
			return
		end
	end
end

function menu_text_slider_show(menu_label, menu_data)
	local control = menu_label.control

	if control ~= nil then
		if control.type ~= MENU_ITEM_TYPE_TEXT_SLIDER then
			menu_release_control(control)
			control = nil
		end
	end

	if control == nil then
		local control_h = vint_object_clone(vint_object_find("menu_text_slider"), Menu_option_labels.control_parent)
		control = { grp_h = control_h, type = MENU_ITEM_TYPE_TEXT_SLIDER, is_highlighted = true}
	end

	menu_label.control = control
	vint_set_property(control.grp_h, "visible", true)

	--Check if the item is selected and set its depth based on that
	if menu_label.control.is_highlighted == true then
		vint_set_property(control.grp_h, "depth", 0)
	else
		--reset the depth
		vint_set_property(control.grp_h, "depth", menu_label.depth)
	end

	--Reposition Slider with the menu label
	vint_set_property(control.grp_h, "anchor", menu_label.anchor_x + Menu_option_labels.max_label_w + 5, menu_label.anchor_y)

	--menu_label.slider_disabled = true
	if menu_data.slider_disabled == true then
		--Hide Arrows
		local arrow_h = vint_object_find("text_slider_arrow_w", control.grp_h)
		vint_set_property(arrow_h, "visible", false)
		local arrow_h = vint_object_find("text_slider_arrow_e", control.grp_h)
		vint_set_property(arrow_h, "visible", false)

		--Tint BG Reset
		local large_frame_h = vint_object_find("large_frame", control.grp_h)
		local bg_h = vint_object_find("text_slider_large_frame_bg", large_frame_h)
		vint_set_property(bg_h, "tint", .8, .8, .8)
		bg_h = vint_object_find("text_slider_large_frame_bg_hl", large_frame_h)
		vint_set_property(bg_h, "tint", .8, .8, .8)
	else
		--Show Arrows
		local arrow_h = vint_object_find("text_slider_arrow_w", control.grp_h)
		vint_set_property(arrow_h, "visible", true)
		local arrow_h = vint_object_find("text_slider_arrow_e", control.grp_h)
		vint_set_property(arrow_h, "visible", true)

		--Tint BG
		local large_frame_h = vint_object_find("large_frame", control.grp_h)
		local bg_h = vint_object_find("text_slider_large_frame_bg", large_frame_h)
		vint_set_property(bg_h, "tint", 1, 1, 1)
		bg_h = vint_object_find("text_slider_large_frame_bg_hl", large_frame_h)
		vint_set_property(bg_h, "tint", 1, 1, 1)
	end

	if menu_data.text_slider_values.cur_value == nil then
		menu_data.text_slider_values.cur_value = 0
	end

	menu_text_slider_update_value(menu_label, menu_data)
end

function menu_text_slider_on_enter(menu_label, menu_data)
	if menu_label.control.is_highlighted == false then
		local g = menu_label.control.grp_h
		vint_set_property(vint_object_find("large_frame", g), "visible", true)
		vint_set_property(vint_object_find("small_frame", g), "visible", false)
		vint_set_property(menu_label.control.grp_h, "depth", 0)
		vint_set_property(vint_object_find("value_text", g), "scale", 1, 1)
		vint_set_property(vint_object_find("text_slider_arrow_w", g), "tint", 0.8941, 0.8489, 0.051)
		vint_set_property(vint_object_find("text_slider_arrow_e", g), "tint", 0.8941, 0.8489, 0.051)

		--Trigger pulsing animation
		menu_label.control.anim_pulse_h = vint_object_clone(vint_object_find("menu_text_slider_pulse_anim"))
		vint_set_property(menu_label.control.anim_pulse_h, "target_handle", g)
		lua_play_anim(menu_label.control.anim_pulse_h, 0)

		menu_label.control.is_highlighted = true

		if menu_label.input1 == nil then
			menu_label.input1 = vint_subscribe_to_input_event(nil, "nav_right", "menu_text_slider_nav_right", 5)
		end
		if menu_label.input2 == nil then
			menu_label.input2 = vint_subscribe_to_input_event(nil, "nav_left", "menu_text_slider_nav_left", 5)
		end
	end
end

function menu_text_slider_on_leave(menu_label, menu_data)
	if menu_label.control == nil then
		debug_print("vint", "Control is nil for: " .. menu_data.label .. "\n")
		return
	end


	if menu_label.control.is_highlighted ~= false then

		local g = menu_label.control.grp_h
		vint_set_property(vint_object_find("large_frame", g), "visible", false)
		vint_set_property(vint_object_find("small_frame", g), "visible", true)
		vint_set_property(menu_label.control.grp_h, "depth", menu_label.depth)

		vint_set_property(vint_object_find("value_text", g), "scale", 0.68, 0.68)
		vint_set_property(vint_object_find("text_slider_arrow_w", g), "tint", 0.3647, 0.3725, 0.3804)
		vint_set_property(vint_object_find("text_slider_arrow_e", g), "tint", 0.3647, 0.3725, 0.3804)
		vint_set_property(vint_object_find("text_slider_arrow_w", g), "offset", -11, -15)
		vint_set_property(vint_object_find("text_slider_arrow_e", g), "offset", -11, -15)
		menu_label.control.is_highlighted = false

		if menu_label.control.anim_pulse_h ~= nil then
			vint_object_destroy(menu_label.control.anim_pulse_h)
		end

		if menu_label.input1 ~= nil then
			vint_unsubscribe_to_input_event(menu_label.input1)
			vint_unsubscribe_to_input_event(menu_label.input2)
			menu_label.input1 = nil
			menu_label.input2 = nil
		end
	end
end

function menu_text_slider_release(control)
	vint_object_destroy(control.grp_h)
end

function menu_text_slider_update_value(menu_label, menu_data)
	local values = menu_data.text_slider_values
	local v = values[values.cur_value]

	if menu_label.control == nil then
		return
	end

	local h = vint_object_find("value_text", menu_label.control.grp_h)

	if v.label_crc ~= nil then
		vint_set_property(h, "text_tag_crc", v.label_crc)
	else
		vint_set_property(h, "text_tag", v.label)
	end

--[[  DAD: 5/12/08 - If text sliders start acting funky, this might need to go back here. Moved it to the nav functions where the value actually IS changing
	if menu_data.on_value_update ~= nil then
		menu_data.on_value_update(menu_label, menu_data)
	end
]]
end

function menu_text_slider_nav_right()
	local menu_label = Menu_option_labels[Menu_active.highlighted_item - Menu_active.first_vis_item]
	local menu_data = Menu_active[Menu_active.highlighted_item]
	local values = menu_data.text_slider_values

	if menu_label == nil or menu_data == nil or values == nil then
		return
	end

	if menu_input_is_blocked() then
		return
	end

	if menu_data.slider_disabled == true then
		--Do nothing, control is disabled
		return
	end

		--Loop to increment over disabled slots...
	local value_not_disabled = false
	local option_count = 0
	while value_not_disabled == false do

		--Increment current value
		values.cur_value = values.cur_value + 1

		--Verify that its not the last in the list
		if values.cur_value >= values.num_values then
			values.cur_value = 0
		end

		--If the item is not disabled, then get out of our loop...
		if menu_data.text_slider_values[values.cur_value].disabled ~= true then
			value_not_disabled = true
		end

		--Increment option counter
		option_count = option_count + 1

		if option_count > values.num_values then
			--We've superceeded our loop count so, All items are disabled for whatever reason... do not update
			return
		end
	end

	menu_text_slider_update_value(menu_label, menu_data)
	audio_play(Menu_sound_value_nav)

	if menu_data.on_value_update ~= nil then
		menu_data.on_value_update(menu_label, menu_data)
	end

end

function menu_text_slider_nav_left()
	local menu_label = Menu_option_labels[Menu_active.highlighted_item - Menu_active.first_vis_item]
	local menu_data = Menu_active[Menu_active.highlighted_item]
	local values = menu_data.text_slider_values

	if menu_label == nil or menu_data == nil or values == nil then
		return
	end

	if menu_input_is_blocked() then
		return
	end

	if menu_data.slider_disabled == true then
		--Do nothing, control is disabled
		return
	end

	--Loop to increment over disabled slots...
	local value_not_disabled = false
	local option_count = 0
	while value_not_disabled == false do

		--Increment current value
		values.cur_value = values.cur_value - 1

		--Verify that its not the last in the list
		if values.cur_value < 0 then
			values.cur_value = values.num_values - 1
		end

		--If the item is not disabled, then get out of our loop...
		if menu_data.text_slider_values[values.cur_value].disabled ~= true then
			value_not_disabled = true
		end

		--Increment option counter
		option_count = option_count + 1

		if option_count > values.num_values then
			--We've superceeded our loop count so, All items are disabled for whatever reason... do not update
			return
		end
	end

	menu_text_slider_update_value(menu_label, menu_data)
	audio_play(Menu_sound_value_nav)

	if menu_data.on_value_update ~= nil then
		menu_data.on_value_update(menu_label, menu_data)
	end
end

function menu_text_slider_get_min_width(menu_item)

	--Get length of slider variable
	local slider_values = menu_item.text_slider_values
	local text_label
	local text_h = vint_object_find("value_text", vint_object_find("menu_text_slider"))

	--Reset the scale of the text to full size
	vint_set_property(text_h, "scale", 1, 1)

	local width = 0
	local min_width = 0
	local v
	--Check all the values within slider values
	for i = 0, slider_values.num_values - 1  do
		v = slider_values[i]
		if v.label_crc ~= nil then
			vint_set_property(text_h, "text_tag_crc", v.label_crc)
		else
			vint_set_property(text_h, "text_tag", v.label)
		end

		width = element_get_actual_size(text_h)
		if width > min_width then
			min_width = width
		end
	end

	return floor(min_width + 57)
end

function menu_info_box_get_min_width(menu_item)

	--Get length of slider variable
	local text_h = vint_object_find("value_text", vint_object_find("menu_text_slider"))

	if menu_item.info_text_crc ~= nil then
		vint_set_property(text_h, "text_tag_crc", menu_item.info_text_crc)
	else
		vint_set_property(text_h, "text_tag",  menu_item.info_text_str)
	end

	--Reset the scale of the text to full size
	vint_set_property(text_h, "scale", 1, 1)

	--Check its width
	local min_width = element_get_actual_size(text_h)
	-- return floor(min_width + 57) -- 57 is a nice looking number (I like 5 in general)... but personally I prefer 94
	return floor(min_width + 94)
end
--------------------[ PALETTE CONTROL ]----------------------

MENU_PALETTE_SWATCH_SCALE_SMALL	= 0.65
MENU_PALETTE_SWATCH_SCALE_BIG		= 1

function menu_pallette_update_selected(menu_label, menu_data, new_index)
	local colors = menu_data.palette_colors
	for i = 0, 2 do
		local swatch = vint_object_find("swatch_color_"..i, menu_label.control.grp_h)

		if i < colors.num_colors then
			if i == new_index then
				vint_set_property(swatch, "scale", MENU_PALETTE_SWATCH_SCALE_BIG, MENU_PALETTE_SWATCH_SCALE_BIG)
				vint_set_property(swatch, "depth", 0)

				local x = vint_get_property(swatch, "anchor")
				vint_set_property(vint_object_find("arrow_w", menu_label.control.grp_h), "anchor", x - 12, 0)
				vint_set_property(vint_object_find("arrow_e", menu_label.control.grp_h), "anchor", x + 80, 0)
			else
				vint_set_property(swatch, "depth", 50)
				vint_set_property(swatch, "scale", MENU_PALETTE_SWATCH_SCALE_SMALL, MENU_PALETTE_SWATCH_SCALE_SMALL)
			end
		else
			vint_set_property(swatch, "visible", false)
		end
	end

	menu_label.control.highlighted_index = new_index
end

function menu_palette_show(menu_label, menu_data)
	local control = menu_label.control

	if control ~= nil then
		if control.type ~= MENU_ITEM_TYPE_PALETTE then
			menu_release_control(control)
			control = nil
		end
	end

	if control == nil then
		local control_h = vint_object_clone(vint_object_find("menu_palette", nil, MENU_BASE_DOC_HANDLE), Menu_option_labels.control_parent)
		control = { grp_h = control_h, type = MENU_ITEM_TYPE_PALETTE, is_highlighted = true, highlighted_index = 0 }
	end

	menu_label.control = control
	vint_set_property(control.grp_h, "visible", true)
	vint_set_property(control.grp_h, "depth", menu_label.depth)
	vint_set_property(control.grp_h, "anchor", menu_label.anchor_x + Menu_option_labels.max_label_w + 5,
		menu_label.anchor_y)

	local p = menu_data.palette_colors
	local num_colors = p.num_colors

	for i = 0, 2 do
		local h = vint_object_find("swatch_color_"..i, control.grp_h)

		if i < num_colors then
			vint_set_property(h, "visible", true)
			vint_set_property(vint_object_find("fill", h), "tint", p[i].red, p[i].green, p[i].blue)
		else
			vint_set_property(h, "visible", false)
		end
	end

	menu_pallette_update_selected(menu_label, menu_data, 0)
end

function menu_palette_invalidate()
	Menu_palette_stored_index = INVALID_PALETTE_INDEX
end

function menu_palette_on_enter(menu_label, menu_data)
	if menu_label.control.is_highlighted == false then
		if Menu_palette_stored_index ~= INVALID_PALETTE_INDEX then
			menu_pallette_update_selected(menu_label, menu_data, Menu_palette_stored_index)
			Menu_palette_stored_index = INVALID_PALETTE_INDEX
		end

		local g = menu_label.control.grp_h
		vint_set_property(vint_object_find("swatch_color_"..menu_label.control.highlighted_index, g), "scale", 1, 1)
		vint_set_property(menu_label.control.grp_h, "depth", -50)

		if menu_data.palette_colors.num_colors > 1 then
			vint_set_property(vint_object_find("arrow_e", g), "visible", true)
			vint_set_property(vint_object_find("arrow_w", g), "visible", true)
			menu_label.input1 = vint_subscribe_to_input_event(nil, "nav_right", "menu_palette_nav", 5)
			menu_label.input2 = vint_subscribe_to_input_event(nil, "nav_left", "menu_palette_nav", 5)
		end

		menu_label.control.is_highlighted = true
	end
end

function menu_palette_on_leave(menu_label, menu_data)
	if menu_label.control.is_highlighted == true then
		if Menu_palette_stored_index == INVALID_PALETTE_INDEX then
			Menu_palette_stored_index = menu_label.control.highlighted_index
		end

		local g = menu_label.control.grp_h
		local hl = menu_label.control.highlighted_index

		if hl ~= nil then
			vint_set_property(vint_object_find("swatch_color_"..hl, g), "scale", MENU_PALETTE_SWATCH_SCALE_SMALL, MENU_PALETTE_SWATCH_SCALE_SMALL)
		end

		vint_set_property(menu_label.control.grp_h, "depth", menu_label.depth)
		vint_set_property(vint_object_find("arrow_e", g), "visible", false)
		vint_set_property(vint_object_find("arrow_w", g), "visible", false)
		menu_label.control.is_highlighted = false

		if menu_label.input1 ~= nil then
			vint_unsubscribe_to_input_event(menu_label.input1)
			vint_unsubscribe_to_input_event(menu_label.input2)
			menu_label.input1 = nil
			menu_label.input2 = nil
		end
	end
end

function menu_palette_release(control)
	vint_object_destroy(control.grp_h)
end

function menu_palette_nav(target, event)
	local menu_data = Menu_active[Menu_active.highlighted_item]
	local label_data = Menu_option_labels[Menu_active.highlighted_item]
	local colors = menu_data.palette_colors
	local new_idx = label_data.control.highlighted_index

	if event == "nav_right" then
		new_idx = new_idx + 1

		if new_idx >= colors.num_colors then
			new_idx = 0
		end
	else
		new_idx = new_idx - 1

		if new_idx < 0 then
			new_idx = colors.num_colors - 1
		end
	end

	audio_play(Menu_sound_item_nav)

	menu_pallette_update_selected(label_data, menu_data, new_idx)
end

--------------------[ INFO BOX CONTROL ]----------------------

function menu_info_box_show(menu_label, menu_data)
	local control = menu_label.control

	if control ~= nil then
		if control.type ~= MENU_ITEM_TYPE_INFO_BOX then
			menu_release_control(control)
			control = nil
		end
	end

	-- reuse the text slider element cluster
	if control == nil then
		local control_h = vint_object_clone(vint_object_find("menu_text_slider"), Menu_option_labels.control_parent)
		vint_set_property(vint_object_find("text_slider_arrow_w", control_h), "visible", false)
		vint_set_property(vint_object_find("text_slider_arrow_e", control_h), "visible", false)
		control = { grp_h = control_h, type = MENU_ITEM_TYPE_INFO_BOX,  is_highlighted = true }
	end

	menu_label.control = control
	vint_set_property(control.grp_h, "visible", true)
	vint_set_property(control.grp_h, "depth", menu_label.depth)
	vint_set_property(control.grp_h, "anchor", menu_label.anchor_x + Menu_option_labels.max_label_w + 5,
		menu_label.anchor_y)

	menu_info_box_update_value(menu_label, menu_data)

	--Hard code width for now
	menu_info_box_set_width(menu_label, menu_data, 215)

	--fix leftover events
	if menu_label.input1 ~= nil then
		vint_unsubscribe_to_input_event(menu_label.input1)
		vint_unsubscribe_to_input_event(menu_label.input2)
		menu_label.input1 = nil
		menu_label.input2 = nil
	end
end

function menu_info_box_update_value(menu_label, menu_data)
	if menu_label.control == nil then
		return
	end

	if menu_data.info_text_crc ~= nil then
		vint_set_property(vint_object_find("value_text", menu_label.control.grp_h), "text_tag_crc", menu_data.info_text_crc)
	else
		vint_set_property(vint_object_find("value_text", menu_label.control.grp_h), "text_tag", menu_data.info_text_str)
	end
end

function menu_info_box_on_enter(menu_label, menu_data)
	if menu_label.control.is_highlighted == false then
		local g = menu_label.control.grp_h
		vint_set_property(vint_object_find("large_frame", g), "visible", true)
		vint_set_property(vint_object_find("small_frame", g), "visible", false)
		vint_set_property(menu_label.control.grp_h, "depth", 0)
		vint_set_property(vint_object_find("value_text", g), "scale", 1, 1)
		menu_label.control.is_highlighted = true

		--Trigger pulsing animation
		menu_label.control.anim_pulse_h = vint_object_clone(vint_object_find("menu_text_slider_pulse_anim"))
		vint_set_property(menu_label.control.anim_pulse_h, "target_handle", g)
		lua_play_anim(menu_label.control.anim_pulse_h, 0)

	end
end

function menu_info_box_on_leave(menu_label, menu_data)
	if menu_label.control == nil then
		return
	end

	if menu_label.control.is_highlighted == true then
		local g = menu_label.control.grp_h
		vint_set_property(vint_object_find("large_frame", g), "visible", false)
		vint_set_property(vint_object_find("small_frame", g), "visible", true)
		vint_set_property(menu_label.control.grp_h, "depth", menu_label.depth)
		vint_set_property(vint_object_find("value_text", g), "scale", 0.68, 0.68)
		menu_label.control.is_highlighted = false

		if menu_label.control.anim_pulse_h ~= nil then
			vint_object_destroy(menu_label.control.anim_pulse_h)
		end
	end
end

function menu_info_box_release(control)
	vint_object_destroy(control.grp_h)
end

function menu_info_box_set_width(menu_label, menu_data, width)
	--what is the width?
	--width is the size of the actual control... not the text

	--Resize parts of the box
	local control_h = menu_label.control.grp_h
	local large_frame_h = vint_object_find("large_frame", control_h)
	local small_frame_h = vint_object_find("small_frame", control_h)

	--Large Frame
	local frame_ns_h = vint_object_find("frame_ns", large_frame_h)
	local frame_bg_h = vint_object_find("text_slider_large_frame_bg", large_frame_h)
	local frame_bg2_h = vint_object_find("text_slider_large_frame_bg_hl", large_frame_h)
	local frame_e_h = vint_object_find("frame_e", large_frame_h)

	--Small Frame
	local s_frame_ns_h = vint_object_find("frame_ns", small_frame_h)
	local s_frame_bg_h = vint_object_find("frame_bg", small_frame_h)
	local s_frame_e_h = vint_object_find("frame_e", small_frame_h)

	--Additional right arrow
	local arrow_e_h = vint_object_find("text_slider_arrow_e", menu_label.control.grp_h)

	-- Subtract 46 from the width sent in to make the control that actual size in pixels
	width = width - 46

	--Background of frame
	local frame_bg_se_x, frame_bg_se_y = vint_get_property(frame_bg_h, "source_se")
	vint_set_property(frame_bg_h, "source_se", width, frame_bg_se_y)
	vint_set_property(frame_bg2_h, "source_se", width, frame_bg_se_y)

	local frame_bg_se_x, frame_bg_se_y = vint_get_property(s_frame_bg_h, "source_se")
	vint_set_property(s_frame_bg_h, "source_se", width + 2, frame_bg_se_y)

	--Middle of the frame
	local frame_ns_se_x, frame_ns_se_y =  vint_get_property(frame_ns_h, "source_se")
	vint_set_property(frame_ns_h, "source_se", width - 13, frame_ns_se_y)
	local frame_ns_se_x, frame_ns_se_y =  vint_get_property(s_frame_ns_h, "source_se")
	vint_set_property(s_frame_ns_h, "source_se", width - 12, frame_ns_se_y)

	--East Side of Frame
	local frame_e_x, frame_e_y = vint_get_property(frame_e_h, "anchor")
	vint_set_property(frame_e_h, "anchor", width + 10, frame_e_y)

	local frame_e_x, frame_e_y = vint_get_property(s_frame_e_h, "anchor")
	vint_set_property(s_frame_e_h, "anchor", width + 8, frame_e_y)

	--x = base size + 51
	local arrow_e_x, arrow_e_y = vint_get_property(arrow_e_h, "anchor")
	vint_set_property(arrow_e_h, "anchor", width + 51, arrow_e_y)
end


--------------------[ SELECTABLE / MARQUEE CONTROL ]----------------------

function menu_marquee_show(menu_label, menu_data)
	local control = menu_label.control

	if control ~= nil then
		if control.type ~= MENU_ITEM_TYPE_MARQUEE then
			menu_release_control(control)
			control = nil
		end
	end

	if control == nil then
		control = { type = MENU_ITEM_TYPE_MARQUEE }
	end

	menu_label.control = control
end

function menu_marquee_on_enter(menu_label, menu_data)
	-- vint_object_create("name", "tween", vint_object_find("root_animation"))
	-- properties: target_handle, target_property, start_value, end_value, start_time (in seconds), duration (in seconds), end_event (callback)
	-- probably get screen_size for text width -
	-- start_time: vint_get_time_index() (its in seconds)
	-- Globals for scroll_speed and delay amount for tweaking are a good idea
	-- end_event: "function_name"  - Start new thread for the delays and restarting to not muck things up.

	local hl_bar_label_h = vint_object_find("menu_sel_bar_label", Menu_option_labels.hl_bar)

	local text_width, text_height = vint_get_property(hl_bar_label_h, "screen_size")
	local clip_x, clip_y = vint_get_property(Menu_option_labels.hl_clip, "clip_size")

	local clipped_width = text_width - (clip_x - MENU_MARQUEE_SCROLL_CORRECTION)

	-- Doesn't need to scroll
	if clipped_width < 0 then
		vint_set_property(Menu_marquee_info.label_h, "offset", 0, 0)
		return
	end

	local twn = vint_object_create("marquee_tween", "tween", vint_object_find("root_animation"))
	vint_set_property(twn, "target_handle", hl_bar_label_h)
	vint_set_property(twn, "target_property", "offset")
	vint_set_property(twn, "start_value", 0, 0)
	vint_set_property(twn, "end_value", 0 - clipped_width, 0)
	vint_set_property(twn, "duration", MENU_MARQUEE_SPEED * clipped_width)
	vint_set_property(twn, "end_event", "menu_marquee_twn_end")
	vint_set_property(twn, "start_time", vint_get_time_index() + MENU_MARQUEE_DELAY)
	if Menu_marquee_info.twn ~= nil then
		vint_object_destroy(Menu_marquee_info.twn)
	end

	Menu_marquee_info.twn = twn
	Menu_marquee_info.label_h = hl_bar_label_h
	Menu_marquee_info.clipped_width = clipped_width
end

function menu_marquee_twn_end()
   if Menu_marquee_info.thread ~= nil then
		thread_kill(Menu_marquee_info.thread)
	end

	Menu_marquee_info.thread = thread_new("menu_marquee_twn_restart")
end

function menu_marquee_twn_restart()
	delay(MENU_MARQUEE_DELAY)
	vint_set_property(Menu_marquee_info.label_h, "offset", 0, 0)
	delay(MENU_MARQUEE_DELAY)
	vint_set_property(Menu_marquee_info.twn, "state", "waiting")
	vint_set_property(Menu_marquee_info.twn, "start_time", vint_get_time_index())
end

function menu_marquee_on_leave(menu_label, menu_data)
	if Menu_marquee_info.thread ~= nil then
		thread_kill(Menu_marquee_info.thread)
		Menu_marquee_info.thread = nil
	end

	if Menu_marquee_info.twn ~= nil then
		vint_object_destroy(Menu_marquee_info.twn)
		Menu_marquee_info.twn = nil
	end

	vint_set_property(Menu_marquee_info.label_h, "offset", 0, 0)
end

----------------------------------------------------------------------------------
------------------------------------[ Footer ]------------------------------------
----------------------------------------------------------------------------------
Menu_footer_price_h				= 0
Menu_footer_style_h				= 0
Menu_footer_label_h				= 0

function menu_footer_build_style_footer(menu_data)
	local footer = menu_data.footer
	if footer ~= nil and footer.footer_grp ~= nil then
		vint_object_destroy(footer.footer_grp)
	end

	menu_data.footer = { }

	local grp = vint_object_clone(vint_object_find("style_footer", nil, MENU_BASE_DOC_HANDLE), Menu_option_labels.control_parent)
	vint_set_property(grp, "visible", true)
	menu_data.footer.footer_grp = grp
	Menu_footer_price_h = vint_object_find("price_amount", grp)
	Menu_footer_style_h = vint_object_find("style_amount", grp)
	Menu_footer_label_h = vint_object_find("price_label", grp)
	vint_set_property(Menu_footer_label_h, "text_tag", "FOOTER_PRICE")
end

function menu_footer_update_style_footer(price, style, tint_enable)

	vint_set_property(Menu_footer_price_h, "visible", true)
	vint_set_property(Menu_footer_style_h, "visible", true)
	vint_set_property(Menu_footer_label_h, "visible", true)

	--Localize style tag
	local style_value = { [0] = style }
	local style_string = vint_insert_values_in_string("STORE_ITEM_STYLE_AWARD", style_value)

	if tint_enable == true then
		vint_set_property(Menu_footer_price_h, "tint", 0.88, 0.749, 0.05)
	else
		vint_set_property(Menu_footer_price_h, "tint", 1, 0, 0)
	end
	vint_set_property(Menu_footer_price_h, "text_tag", "$".. format_cash(price))
	vint_set_property(Menu_footer_style_h, "text_tag", style_string)
end

function	menu_footer_remove_style_footer(menu_data)
	vint_set_property(menu_data.footer.footer_grp, "visible", false)
	vint_object_destroy(menu_data.footer.footer_grp)
end

-- Finish it up
function menu_footer_finalize_style_footer(menu_data)
	vint_set_property(Menu_footer_price_h, "anchor", menu_data.menu_width - 20, 0)
end

-----------------------------------------------------------------------------------
---------------------------------[ Style Cluster ]---------------------------------
-----------------------------------------------------------------------------------
Style_cluster_player_cash	 		= -1		--	Cash the player has
Style_cluster_displayed_cash 		= -1		--	Displayed in the style cluster
Style_cluster_cash_anim_h 			= 0		--	Thread handle for cash anim
Style_cluster_cash_style_grp_h 	= 0		--	Cash + Style meter
Style_cluster_cash_style_anim_h 	= 0		--	Handle for the cash counting down animation
Style_cluster_player_style 		= { }		--	Player's style info
Style_cluster_enabled 				= false
Style_cluster_data_subs				= false	-- Have data subscriptions been inited?

function menu_store_init(awards_style)
	Style_cluster_cash_style_grp_h = vint_object_find("cash_style_cluster", nil, MENU_BASE_DOC_HANDLE)
	Style_cluster_cash_style_grp_h = vint_object_find("cash_style_cluster", nil, MENU_BASE_DOC_HANDLE)
	Style_cluster_cash_style_anim_h = vint_object_find("add_style_anim", nil, MENU_BASE_DOC_HANDLE)
	vint_set_property(Style_cluster_cash_style_grp_h, "visible", true)

	--Animation Style cluster in
	local cash_trans_in = vint_object_find("cash_trans_in", nil, MENU_BASE_DOC_HANDLE)
	lua_play_anim(cash_trans_in, 0)

	-- subscribe to data
	if Style_cluster_data_subs == false then
		vint_dataitem_add_subscription("sr2_local_player_status_infrequent", "update", "style_cluster_cash_update")
		vint_dataitem_add_subscription("local_player_style", "update", "style_cluster_style_update")
	end

	-- hide/unhide style elements and adjust offset of cash text
	if awards_style == true then
		vint_set_property(vint_object_find("style_grp", Style_cluster_cash_style_grp_h), "visible", true)
		vint_set_property(vint_object_find("cash_style_base", Style_cluster_cash_style_grp_h), "visible", true)
		vint_set_property(vint_object_find("cash_frame", Style_cluster_cash_style_grp_h), "offset", 0, 0)
		vint_set_property(vint_object_find("style_add_text", Style_cluster_cash_style_grp_h), "visible", false)
	else
		vint_set_property(vint_object_find("style_grp", Style_cluster_cash_style_grp_h), "visible", false)
		vint_set_property(vint_object_find("cash_style_base", Style_cluster_cash_style_grp_h), "visible", false)
		vint_set_property(vint_object_find("cash_frame", Style_cluster_cash_style_grp_h), "offset", -30, 0)
		vint_set_property(vint_object_find("style_add_text", Style_cluster_cash_style_grp_h), "visible", true)
	end

	Style_cluster_enabled = true
end

function menu_base_cleanup()
	if (Menu_hud_hidden) then
		if Sui_hud_enable == 0 then
			hud_hide(true)
		else
			hud_hide(false)
		end
	end

	vint_document_unload(vint_document_find("menu_style_dialog"))

	--Event Tracking(Exit Menu)
	event_tracking_interface_exit()
end

function menu_store_use_hud(use_hud)
	Menu_use_hud = use_hud
end

function menu_store_get_player_cash()
	if Style_cluster_enabled == true then
		return Style_cluster_player_cash
	else
		return 0
	end
end

function style_cluster_cash_update(di_h)
	local cash = vint_dataitem_get(di_h)

	if Style_cluster_player_cash == -1 then
		Style_cluster_player_cash = cash
		Style_cluster_displayed_cash = cash
		style_cluster_animate_cash()
	end

	if cash ~= Style_cluster_player_cash then
		Style_cluster_player_cash = cash

		if Style_cluster_cash_anim_h == 0 then
			Style_cluster_cash_anim_h = thread_new("style_cluster_animate_cash")
		end
	end
end

function style_cluster_cleanup()
	Style_cluster_enabled = false
	vint_set_property(Style_cluster_cash_style_grp_h, "visible", false)
end

function style_cluster_animate_cash()
	local d, d_abs
	while true do
		d = Style_cluster_player_cash - Style_cluster_displayed_cash

		if d < 0 then
			d_abs = d * -1
		else
			d_abs = d
		end

		if d_abs <= 5 then
			Style_cluster_displayed_cash = Style_cluster_player_cash
			vint_set_property(vint_object_find("cash_text", Style_cluster_cash_style_grp_h), "text_tag", "$"..format_cash(Style_cluster_displayed_cash))
			Style_cluster_cash_anim_h = 0
			return
		end

		Style_cluster_displayed_cash = floor(Style_cluster_displayed_cash + (d * 0.5))
		vint_set_property(vint_object_find("cash_text", Style_cluster_cash_style_grp_h), "text_tag", "$"..format_cash(Style_cluster_displayed_cash))
		thread_yield()
	end
end

function style_cluster_style_update(di_h)
	local style_points, style_level, style_percent, respect_bonus = vint_dataitem_get(di_h)

	local s = Style_cluster_player_style
	local points_awarded = 0
	local animation_style = 0		-- 0 = no animation, 1 = 1 pass, 2 = 2 pass
	local enable_level_dialog = true

	-- check if this is the first data push
	if s.style_points == nil then
		s.level = 0
		s.percent = 0
		s.bonus = 0
		animation_style = 1
		enable_level_dialog = false
	else
		points_awarded = style_points - s.style_points
	end

	if points_awarded > 0 then
		if s.percent < style_percent then
			animation_style = 1
		else
			animation_style = 2
		end
	end

	if animation_style > 0 then
		-- set text of style level
		vint_set_property(vint_object_find("style_level_text", Style_cluster_cash_style_grp_h), "text_tag", style_level)

		if points_awarded > 0 then
			--Format Style tag with value insert
			local style_insert = {[0] = points_awarded}
			local style_string = vint_insert_values_in_string("STORE_ITEM_STYLE_AWARD", style_insert)
			vint_set_property(vint_object_find("style_add_text", Style_cluster_cash_style_grp_h), "text_tag", style_string)
			vint_set_property(vint_object_find("style_add_text_flair", Style_cluster_cash_style_grp_h), "text_tag", style_string)
			vint_set_property(vint_object_find("style_add_text", Style_cluster_cash_style_grp_h), "visible", true)
		else
			vint_set_property(vint_object_find("style_add_text", Style_cluster_cash_style_grp_h), "visible", false)
		end

		-- set up animation
		local r1 = style_percent * PI2
		local r2 = style_level * PI2
		local pr1 = s.percent * PI2
		local pr2 = s.level * PI2

		if animation_style == 1 then
			-- single stage rotation
			local object = vint_object_find("cash_style_bg_end_angle_twn_1", Style_cluster_cash_style_anim_h)
			vint_set_property(object, "start_value", pr1)
			vint_set_property(object, "end_value", r1)
			vint_set_property(object, "duration", 0.5)

			object = vint_object_find("cash_style_fill_end_angle_twn_1", Style_cluster_cash_style_anim_h)
			if pr1 > 0.13 then
				vint_set_property(object, "start_value", pr1 - 0.13)
			else
				vint_set_property(object, "start_value", 0)
			end

			if r1 > 0.13 then
				vint_set_property(object, "end_value", r1 - 0.13)
			else
				vint_set_property(object, "end_value", 0)
			end

			vint_set_property(object, "duration", 0.5)

			object = vint_object_find("cash_style_bg_end_angle_twn_2", Style_cluster_cash_style_anim_h)
			vint_set_property(object, "state", "disabled")

			object = vint_object_find("cash_style_fill_end_angle_twn_2", Style_cluster_cash_style_anim_h)
			vint_set_property(object, "state", "disabled")

			-- level label
			object = vint_object_find("style_level_grp_rotation_twn_1", Style_cluster_cash_style_anim_h)
			vint_set_property(object, "start_value", pr1)
			vint_set_property(object, "end_value", r1)
			vint_set_property(object, "duration", 0.5)
			vint_set_property(object, "state", "waiting")

			object = vint_object_find("style_level_text_rotation_twn_1", Style_cluster_cash_style_anim_h)
			vint_set_property(object, "start_value", pr1 * -1)
			vint_set_property(object, "end_value", r1 * -1)
			vint_set_property(object, "duration", 0.5)
			vint_set_property(object, "state", "waiting")

			vint_set_property(vint_object_find("style_level_grp_rotation_twn_2", Style_cluster_cash_style_anim_h), "state", "disabled")
			vint_set_property(vint_object_find("style_level_text_rotation_twn_2", Style_cluster_cash_style_anim_h), "state", "disabled")
		else
			-- two stage rotation
			local t = (1 - s.percent + style_percent) * style_percent
			local t2 = 0.5 * t
			local t1 = 0.5 * (1 - t)

			local object = vint_object_find("cash_style_bg_end_angle_twn_1", Style_cluster_cash_style_anim_h)
			vint_set_property(object, "start_value", pr1)
			vint_set_property(object, "end_value", PI2)
			vint_set_property(object, "duration", t1)

			object = vint_object_find("cash_style_bg_end_angle_twn_2", Style_cluster_cash_style_anim_h)
			vint_set_property(object, "start_value", 0)
			vint_set_property(object, "end_value", r1)
			vint_set_property(object, "state", "waiting")
			vint_set_property(object, "duration", t2)
			vint_set_property(object, "start_time", t1)

			object = vint_object_find("cash_style_fill_end_angle_twn_1", Style_cluster_cash_style_anim_h)
			if pr1 > 0.13 then
				vint_set_property(object, "start_value", pr1 - 0.13)
			else
				vint_set_property(object, "start_value", 0)
			end
			vint_set_property(object, "end_value", PI2)
			vint_set_property(object, "duration", t1)

			object = vint_object_find("cash_style_fill_end_angle_twn_2", Style_cluster_cash_style_anim_h)
			vint_set_property(object, "start_value", 0)
			if r1 > 0.13 then
				vint_set_property(object, "end_value", r1 - 0.13)
			else
				vint_set_property(object, "end_value", 0)
			end
			vint_set_property(object, "state", "waiting")
			vint_set_property(object, "duration", t2)
			vint_set_property(object, "start_time", t1)

			-- level label
			object = vint_object_find("style_level_grp_rotation_twn_1", Style_cluster_cash_style_anim_h)
			vint_set_property(object, "start_value", pr1)
			vint_set_property(object, "end_value", PI2)
			vint_set_property(object, "duration", t1)

			object = vint_object_find("style_level_text_rotation_twn_1", Style_cluster_cash_style_anim_h)
			vint_set_property(object, "start_value", pr1 * -1)
			vint_set_property(object, "end_value", PI2 * -1)
			vint_set_property(object, "duration", t1)

			object = vint_object_find("style_level_grp_rotation_twn_2", Style_cluster_cash_style_anim_h)
			vint_set_property(object, "start_value", 0)
			vint_set_property(object, "end_value", r1)
			vint_set_property(object, "start_time", t1)
			vint_set_property(object, "duration", t2)
			vint_set_property(object, "state", "waiting")

			object = vint_object_find("style_level_text_rotation_twn_2", Style_cluster_cash_style_anim_h)
			vint_set_property(object, "start_value", 0)
			vint_set_property(object, "end_value", r1 * -1)
			vint_set_property(object, "start_time", t1)
			vint_set_property(object, "duration", t2)
			vint_set_property(object, "state", "waiting")
		end

		vint_set_property(Style_cluster_cash_style_anim_h, "start_time", vint_get_time_index(MENU_BASE_DOC_HANDLE))

		if enable_level_dialog == true and style_level > s.level then
			s.level = style_level
			s.bonus = respect_bonus
			vint_document_load("menu_style_dialog")
		end
	end

	s.level = style_level
	s.percent = style_percent
	s.style_points = style_points
	s.bonus = respect_bonus
end

-----------------------------------------------------------------------------------
---------------------------------[ Interface Swap ]--------------------------------
-----------------------------------------------------------------------------------

Menu_interface_swap_complete_cb = 0

function menu_swap_interface(msg, on_complete)
	if on_complete == nil then
		Menu_interface_swap_complete_cb = 0
	else
		Menu_interface_swap_complete_cb = on_complete
	end

	local insert_values = {[0] = msg}
	local title_str = vint_insert_values_in_string("STORE_SWITCHING_TITLE", insert_values)

	lua_play_anim(vint_object_find("swap_message_trans_in", nil, MENU_BASE_DOC_HANDLE))
	vint_set_property(vint_object_find("swap_title", nil, MENU_BASE_DOC_HANDLE), "text_tag", title_str)

	menu_close(menu_swap_finalize)

end

function menu_swap_finalize()
	thread_new("menu_swap_finalize_delayed")
end

function menu_swap_finalize_delayed()
	delay(1)
	lua_play_anim(vint_object_find("swap_message_trans_out", nil, MENU_BASE_DOC_HANDLE))

	if Menu_interface_swap_complete_cb ~= 0 then
		Menu_interface_swap_complete_cb()
		Menu_interface_swap_complete_cb = 0
	end
end

------------------------------------------------------------------------------
-------------------------------[ Button Tips ]--------------------------------
------------------------------------------------------------------------------
Menu_base_btn_tips = { [0] = { }, [1] = { }, [2] = { }, [3] = { } }
Button_tips_is_init = false
Menu_base_btn_tips_pause_ind_h = -1
Menu_base_btn_tips_pause_ind_x = 0
Menu_base_btn_tips_pause_ind_y = 0
Menu_base_btn_tips_pause_ind_width = 0

function btn_tips_init()
	if Button_tips_is_init == true then
		return
	end
	local label_h = vint_object_find("menu_btn_tip_label", nil, MENU_BASE_DOC_HANDLE)
	local bitmap_h = vint_object_find("menu_btn_tip_bmp", nil, MENU_BASE_DOC_HANDLE)

	Menu_base_btn_tips[0].label_h = label_h
	Menu_base_btn_tips[0].bitmap_h = bitmap_h
	vint_set_property(Menu_base_btn_tips[0].bitmap_h, "image", "ui_ctrl_360_btn_a")

	Menu_base_btn_tips[1].label_h = vint_object_clone(label_h)
	Menu_base_btn_tips[1].bitmap_h = vint_object_clone(bitmap_h)
	vint_set_property(Menu_base_btn_tips[1].bitmap_h, "image", "ui_ctrl_360_btn_x")

	Menu_base_btn_tips[2].label_h = vint_object_clone(label_h)
	Menu_base_btn_tips[2].bitmap_h = vint_object_clone(bitmap_h)
	vint_set_property(Menu_base_btn_tips[2].bitmap_h, "image", "ui_ctrl_360_btn_b")

	Menu_base_btn_tips[3].label_h = vint_object_clone(label_h)
	Menu_base_btn_tips[3].bitmap_h = vint_object_clone(bitmap_h)
	vint_set_property(Menu_base_btn_tips[3].bitmap_h, "image", "ui_ctrl_360_btn_rs")

	Menu_base_btn_tips[3].independent_label_h = vint_object_find("menu_btn_tip_ext_label", nil, MENU_BASE_DOC_HANDLE)
	Menu_base_btn_tips[3].independent_bitmap_h = vint_object_find("menu_btn_tip_ext_bmp", nil, MENU_BASE_DOC_HANDLE)
	Menu_base_btn_tips[3].independent_group_h = vint_object_find("menu_btn_tips_ext", nil, MENU_BASE_DOC_HANDLE)
	vint_set_property(Menu_base_btn_tips[3].independent_bitmap_h, "image", "ui_ctrl_360_btn_rs")

	Menu_base_btn_tips_pause_ind_h = vint_object_find("pause_menu_indicator", nil, MENU_BASE_DOC_HANDLE)
	Menu_base_btn_tips_pause_ind_x, Menu_base_btn_tips_pause_ind_y = vint_get_property(Menu_base_btn_tips_pause_ind_h, "anchor")
	local width, height = element_get_actual_size(Menu_base_btn_tips_pause_ind_h)
	Menu_base_btn_tips_pause_ind_width = width

	Button_tips_is_init = true
end

function btn_tips_update()
	local main_menu_doc_h = vint_document_find("main_menu")
	if Menu_horz_active == 0 and main_menu_doc_h == 0 and Pause_menu_save_for_server_drop == false then
		return
	end

	local btn_tips = { }
	if Menu_active.btn_tips == nil then
		btn_tips = BTN_TIPS_DEFAULT
	else
		btn_tips = Menu_active.btn_tips
	end

	local no_a_button = false;
	if btn_tips.a_button ~= nil and var_to_bool(btn_tips.a_button.enabled) == true then
		vint_set_property(Menu_base_btn_tips[0].label_h, "visible", true)
		vint_set_property(Menu_base_btn_tips[0].bitmap_h, "visible", true)

		vint_set_property(Menu_base_btn_tips[0].bitmap_h, "image", get_a_button())
		vint_set_property(Menu_base_btn_tips[0].label_h, "text_tag", btn_tips.a_button.label)
		Menu_base_btn_tips[0].visible = true
	else
		vint_set_property(Menu_base_btn_tips[0].label_h, "visible", false)
		vint_set_property(Menu_base_btn_tips[0].bitmap_h, "visible", false)
		Menu_base_btn_tips[0].visible = false
		no_a_button = true
	end

	if btn_tips.x_button ~= nil and var_to_bool(btn_tips.x_button.enabled) == true then
		if no_a_button == true then
		end

		vint_set_property(Menu_base_btn_tips[1].label_h, "visible", true)
		vint_set_property(Menu_base_btn_tips[1].bitmap_h, "visible", true)

		vint_set_property(Menu_base_btn_tips[1].bitmap_h, "image", get_x_button())
		vint_set_property(Menu_base_btn_tips[1].label_h, "text_tag", btn_tips.x_button.label)
		Menu_base_btn_tips[1].visible = true
	else
		vint_set_property(Menu_base_btn_tips[1].label_h, "visible", false)
		vint_set_property(Menu_base_btn_tips[1].bitmap_h, "visible", false)
		Menu_base_btn_tips[1].visible = false
	end

	if btn_tips.b_button ~= nil and var_to_bool(btn_tips.b_button.enabled) == true then
		vint_set_property(Menu_base_btn_tips[2].label_h, "visible", true)
		vint_set_property(Menu_base_btn_tips[2].bitmap_h, "visible", true)

		vint_set_property(Menu_base_btn_tips[2].bitmap_h, "image", get_b_button())
		vint_set_property(Menu_base_btn_tips[2].label_h, "text_tag", btn_tips.b_button.label)
		Menu_base_btn_tips[2].visible = true
	else
		vint_set_property(Menu_base_btn_tips[2].label_h, "visible", false)
		vint_set_property(Menu_base_btn_tips[2].bitmap_h, "visible", false)
		Menu_base_btn_tips[2].visible = false
	end

	if btn_tips.right_stick ~= nil and var_to_bool(btn_tips.right_stick.enabled) == true then
		if btn_tips.right_stick.independent == false then
			vint_set_property(Menu_base_btn_tips[3].label_h, "visible", true)
			vint_set_property(Menu_base_btn_tips[3].bitmap_h, "visible", true)
			vint_set_property(Menu_base_btn_tips[3].label_h, "text_tag", btn_tips.right_stick.label)

			if btn_tips.right_stick.use_dpad == true then
				vint_set_property(Menu_base_btn_tips[3].bitmap_h, "image", get_up_down())
			else
				vint_set_property(Menu_base_btn_tips[3].bitmap_h, "image", get_right_stick())
			end
			vint_set_property(Menu_base_btn_tips[3].independent_group_h, "visible", false)
		else
			vint_set_property(Menu_base_btn_tips[3].label_h, "visible", false)
			vint_set_property(Menu_base_btn_tips[3].bitmap_h, "visible", false)

			vint_set_property(Menu_base_btn_tips[3].independent_group_h, "visible", true)
			vint_set_property(Menu_base_btn_tips[3].independent_label_h, "visible", true)
			if btn_tips.right_stick.in_playlist == true then
				vint_set_property(Menu_base_btn_tips[3].independent_bitmap_h, "visible", false)
			else
				vint_set_property(Menu_base_btn_tips[3].independent_bitmap_h, "visible", true)
			end

			if btn_tips.right_stick.use_dpad == true then
				vint_set_property(Menu_base_btn_tips[3].independent_bitmap_h, "image", get_up_down())
			else
				vint_set_property(Menu_base_btn_tips[3].independent_bitmap_h, "image", get_right_stick())
			end

			if btn_tips.right_stick.in_playlist == true then
				vint_set_property(Menu_base_btn_tips[3].independent_label_h, "force_case", "upper")
				local str = vint_insert_values_in_string(btn_tips.right_stick.label, { [0] = btn_tips.right_stick.label_text })
				vint_set_property(Menu_base_btn_tips[3].independent_label_h, "text_tag", str )
			else
				vint_set_property(Menu_base_btn_tips[3].independent_label_h, "text_tag", btn_tips.right_stick.label)
			end

			local width = element_get_actual_size(Menu_base_btn_tips[3].independent_label_h)
			local resolution_adjust = 0

			-- Awesome fun magic numbers that force the right stick graphic into the right position
			if vint_hack_is_std_res() then
				resolution_adjust = 747
			else
				resolution_adjust = 1015
			end

			local Xpos, Ypos = vint_get_property(Menu_base_btn_tips[3].independent_group_h, "anchor")
			vint_set_property(Menu_base_btn_tips[3].independent_group_h, "anchor", resolution_adjust - width, Ypos)
		end


		Menu_base_btn_tips[3].visible = true
	else
		vint_set_property(Menu_base_btn_tips[3].label_h, "visible", false)
		vint_set_property(Menu_base_btn_tips[3].bitmap_h, "visible", false)
		vint_set_property(Menu_base_btn_tips[3].independent_group_h, "visible", false)

		Menu_base_btn_tips[3].visible = false
	end


	local element, x, w, w2
	local junk, y = vint_get_property(Menu_base_btn_tips[0].label_h, "anchor")

	local btn_padding = 0
	local tip_padding = 15
	local idx_offset = -1

	local tip_count = 0

	for idx, val in Menu_base_btn_tips do
		tip_count = tip_count + 1
	end

	local tip_width = 0
	for idx = 0, tip_count - 1 do
		local val = Menu_base_btn_tips[idx]

		if idx_offset < 0 and val.visible == true then
			--do first pass (its a little different than the rest)
			vint_set_property(val.label_h, "force_case", "upper")
			x = vint_get_property(Menu_base_btn_tips[0].bitmap_h, "anchor")
			vint_set_property(val.bitmap_h, "anchor", x, y)
			w = element_get_actual_size(val.bitmap_h)
			w2 = element_get_actual_size(val.label_h)
			x = x + w/2 + btn_padding
			vint_set_property(val.label_h, "anchor", x, y)
			idx_offset = idx

			--Calculate size for possible centering
			tip_width = tip_width + w + w2 + btn_padding + tip_padding
		elseif (idx ~= 3 or (idx == 3 and btn_tips.right_stick ~= nil and btn_tips.right_stick.independent == false)) and val.visible == true then
			--Arrange button
			vint_set_property(val.label_h, "force_case", "upper")
			x = vint_get_property(Menu_base_btn_tips[idx_offset].label_h, "anchor")
			w = element_get_actual_size(Menu_base_btn_tips[idx_offset].label_h)
			w2 = element_get_actual_size(val.bitmap_h)
			x = x + w2 / 2 + w + tip_padding
			vint_set_property(val.bitmap_h, "anchor", x, 0)

			--Arrange text
			x = vint_get_property(val.bitmap_h, "anchor")
			w = w2
			x = x + w/2 + btn_padding
			vint_set_property(val.label_h, "anchor", x, y)

			idx_offset = idx

			--Calculate size for possible centering
			w = element_get_actual_size(val.label_h)
			w2 = element_get_actual_size(val.bitmap_h)
			tip_width = tip_width + w + w2 + btn_padding + tip_padding
		end

	end

	--Check if we should move the pause menu indicator because it may overlap the button tips
	if vint_document_find("pause_menu") ~= 0 then
		local safe_frame_width = 1088
		if vint_hack_is_std_res() then
			--Because we are comparing against actual size safe frame width is 1.5 * 545
			safe_frame_width = 816
		end

		local left_over_space = safe_frame_width - tip_width

		if Menu_base_btn_tips_pause_ind_width > left_over_space then
			--We have overlapping text
			--Moving pause indicator to left side right above button tips
			vint_set_property(Menu_base_btn_tips_pause_ind_h, "anchor", 98, 39)
			vint_set_property(Menu_base_btn_tips_pause_ind_h, "auto_offset", "W")
		else
			--Moving back to original position
			vint_set_property(Menu_base_btn_tips_pause_ind_h, "anchor", Menu_base_btn_tips_pause_ind_x, Menu_base_btn_tips_pause_ind_y)
			vint_set_property(Menu_base_btn_tips_pause_ind_h, "auto_offset", "NE")
		end
	end

	--if main menu then we center button tips
	if main_menu_doc_h ~= 0 then
		--Center button tips
		local center_x = 640
		if vint_hack_is_std_res() == true then
			--Yes this is a magic number but it works.
			center_x = 510
		end
		local tips_h = vint_object_find("menu_btn_tips", nil, MENU_BASE_DOC_HANDLE)
		local target_x = center_x - tip_width * 0.5
		local x, y = vint_get_property(tips_h, "anchor")
		vint_set_property(tips_h, "anchor", target_x, y)
	end
end

function btn_tips_default_a()
	return true
end

function btn_tips_default_b()
	return true
end

function btn_tips_default_x()
	if Menu_active.on_alt_select ~= nil or Menu_active[Menu_active.highlighted_item].on_alt_select ~= nil then
		return true
	else
		return false
	end
end

function btn_tips_default_rs()
	return false
end

function btn_tips_footer_build(parent_h, offset_x, offset_y, menu_data)
	local footer_grp = vint_object_clone(vint_object_find("footer_btn_tips", nil, MENU_BASE_DOC_HANDLE), parent_h)

	--Space everything based on localization
	local btn_spacing = 3 --Spacing between button -> text
	local txt_spacing = 30 -- Spacing between text -> button
	local btn_a_h = vint_object_find("footer_tip_a_bmp", footer_grp)
	local txt_a_h = vint_object_find("footer_tip_a_label", footer_grp)
	local btn_b_h = vint_object_find("footer_tip_b_bmp", footer_grp)
	local txt_b_h = vint_object_find("footer_tip_b_label", footer_grp)

	-- Force UPPERCASE or the lowercase text won't appear! [nclok1405]
	vint_set_property(txt_a_h, "force_case", "upper")
	vint_set_property(txt_b_h, "force_case", "upper")

	-- Set button text if the menu provides it [nclok1405]
	if (menu_data ~= nil) and (menu_data.btn_tips ~= nil) then
		local btn_tips = menu_data.btn_tips

		if (btn_tips.a_button ~= nil) and (btn_tips.a_button.label ~= nil) then
			vint_set_property(txt_a_h, "text_tag", btn_tips.a_button.label)
		end
		if (btn_tips.b_button ~= nil) and (btn_tips.b_button.label ~= nil) then
			vint_set_property(txt_b_h, "text_tag", btn_tips.b_button.label)
		end
	end

	--Replace buttons
	vint_set_property(btn_a_h, "image", get_a_button())
	vint_set_property(btn_b_h, "image", get_b_button())

	local x, y = vint_get_property(btn_a_h, "anchor")

	--Apply offsets
	vint_set_property(footer_grp, "anchor", offset_x, offset_y)

	local width, height = element_get_actual_size(btn_a_h)
	vint_set_property(txt_a_h, "anchor", x + width/2 + btn_spacing , y)

	x, y = vint_get_property(txt_a_h, "anchor")
	width, height = element_get_actual_size(txt_a_h)
	vint_set_property(btn_b_h, "anchor", x + width + txt_spacing, y)

	local x, y = vint_get_property(btn_b_h, "anchor")
	local width, height = element_get_actual_size(btn_b_h)
	vint_set_property(txt_b_h, "anchor", x + width/2 + btn_spacing, y)

	--Derive full control width
	local width, height = element_get_actual_size(txt_b_h)
	width = width + x + 10

	return footer_grp, width
end
function btn_tips_footer_attach(menu_data)
	local parent_h = Menu_option_labels.control_parent
	local footer_grp, width = btn_tips_footer_build(parent_h, 0, 0, menu_data)

	menu_data.footer = { }
	menu_data.footer.width = floor(width)

	menu_data.footer.footer_grp = footer_grp
	menu_data.footer_height = 25
end

function btn_tips_footer_set_width(menu_data)
	--Do nothing`
end

function menu_clone(src)
	-- copy the original
	local dst = table_clone(src)

	-- clear out any instance data
	for i = 0, dst.num_items - 1 do
		if dst[i].control ~= nil then
			menu_release_control(dst[i])
		end
	end

	if dst.footer ~= nil then
		vint_object_destroy(dst.footer.footer_grp)
		vint_object_destroy(dst.footer.hr_h)
		dst.footer = nil
	end

	return dst
end

BTN_TIPS_DEFAULT = {
	a_button = { label = "CONTROL_SELECT", enabled = btn_tips_default_a, },
	x_button = { label = "PLAYER_CREATION_RANDOMIZE", enabled = btn_tips_default_x, },
	b_button = { label = "CONTROL_RESUME", enabled = btn_tips_default_b, },
	right_stick = { label = "CONTROL_ZOOM_AND_ROTATE", enabled = btn_tips_default_rs, independent = true },
}

Menu_control_callbacks = {
	[MENU_ITEM_TYPE_NUM_SLIDER] = {
		on_show =			menu_num_slider_show,
		on_enter =			menu_num_slider_on_enter,
		on_leave =			menu_num_slider_on_leave,
		on_select =			menu_control_on_select,
		on_release =		menu_num_slider_release,
		has_control =		true,
		hide_select_bar =	true
	},

	[MENU_ITEM_TYPE_SELECTABLE] = {
		on_select =		menu_control_on_select,
	},

	[MENU_ITEM_TYPE_SUB_MENU] = {
		on_select =		menu_submenu_on_select,
	},

	[MENU_ITEM_TYPE_TEXT_SLIDER] = {
		on_show =			menu_text_slider_show,
		on_enter =			menu_text_slider_on_enter,
		on_leave =			menu_text_slider_on_leave,
		on_select =			menu_control_on_select,
		on_release =		menu_text_slider_release,
		get_min_width =	menu_text_slider_get_min_width,
		set_width =			menu_info_box_set_width,
		has_control =		true,
		hide_select_bar =	true
	},

	[MENU_ITEM_TYPE_GRID] = {
		on_select =				menu_control_on_select,
		on_nav_left =			menu_grid_nav_left,
		on_nav_right =			menu_grid_nav_right,
		on_nav_up =				menu_grid_nav_up,
		on_nav_down =			menu_grid_nav_down,
		get_width =				menu_grid_get_width,
		get_height =			menu_grid_get_height,
		uses_scroll_bar =		true,
		hide_select_bar =		true,
		hide_label_stripe =	true,
	},

	[MENU_ITEM_TYPE_PALETTE] = {
		on_show =				menu_palette_show,
		on_enter =				menu_palette_on_enter,
		on_leave =				menu_palette_on_leave,
		on_select =				menu_control_on_select,
		on_release =			menu_palette_release,
		has_control =			true,
		hide_select_bar =		true,
		hide_label_stripe =	true,
	},

	[MENU_ITEM_TYPE_INFO_BOX] = {
		on_show =				menu_info_box_show,
		on_select =				menu_control_on_select,
		on_enter =				menu_info_box_on_enter,
		on_leave =				menu_info_box_on_leave,
		on_release =			menu_info_box_release,
		set_width =				menu_info_box_set_width,
		get_min_width =		menu_info_box_get_min_width,
		has_control =			true,
		hide_select_bar =		true,
		hide_label_stripe =	true,
	},

	[MENU_ITEM_TYPE_MARQUEE] = {
		on_show	 =		menu_marquee_show,
		on_select =		menu_control_on_select,
		on_enter  =		menu_marquee_on_enter,
		on_leave  =		menu_marquee_on_leave,
	},

}
