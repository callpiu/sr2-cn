-- pcr01.lua: Plastic Surgeon and Initial Player Customization
-- Player creation interface

Pcr01_building_menu = 0

Pcr01_current_makeup_area = -1
Pcr01_current_makeup_item = -1
Pcr01_current_makeup_variant = -1
Pcr01_current_makeup_primary_color = -1
Pcr01_current_makeup_secondary_color = -1
Pcr01_makeup_color_is_primary = true

INVALID_MAKEUP_VARIANT = -1
INVALID_COLOR 	= -1
INVALID_MAKEUP_INDEX = -1

Pcr01_saved_makeup = {	[0] = {item = INVALID_MAKEUP_INDEX, variant = INVALID_MAKEUP_VARIANT, primary_color = INVALID_COLOR, secondary_color = INVALID_COLOR},
							[1] = {item = INVALID_MAKEUP_INDEX, variant = INVALID_MAKEUP_VARIANT, primary_color = INVALID_COLOR, secondary_color = INVALID_COLOR},
							[2] = {item = INVALID_MAKEUP_INDEX, variant = INVALID_MAKEUP_VARIANT, primary_color = INVALID_COLOR, secondary_color = INVALID_COLOR},
							[3] = {item = INVALID_MAKEUP_INDEX, variant = INVALID_MAKEUP_VARIANT, primary_color = INVALID_COLOR, secondary_color = INVALID_COLOR},
							[4] = {item = INVALID_MAKEUP_INDEX, variant = INVALID_MAKEUP_VARIANT, primary_color = INVALID_COLOR, secondary_color = INVALID_COLOR}}

INVALID_HAIR_STYLE = -1
INVALID_HAIR_COLOR = -1

Pcr01_saved_hair = { 	[0] = {style = INVALID_HAIR_STYLE, primary_color = INVALID_HAIR_COLOR, secondary_color = INVALID_HAIR_COLOR},
						[1] = {style = INVALID_HAIR_STYLE, primary_color = INVALID_HAIR_COLOR, secondary_color = INVALID_HAIR_COLOR},
						[2] = {style = INVALID_HAIR_STYLE, primary_color = INVALID_HAIR_COLOR, secondary_color = INVALID_HAIR_COLOR},
						[3] = {style = INVALID_HAIR_STYLE, primary_color = INVALID_HAIR_COLOR, secondary_color = INVALID_HAIR_COLOR},
						[4] = {style = INVALID_HAIR_STYLE, primary_color = INVALID_HAIR_COLOR, secondary_color = INVALID_HAIR_COLOR}}

-- used for delayed updates
Pcr01_nav_value = -1
Pcr01_nav_thread = -1

-- stores values for rollback
Pcr01_original_values = { }

Pcr01_current_preset_gender = -1
Pcr01_current_preset_race = -1
Pcr01_current_preset_figure = -1

PCR01_MALE_GENDER_NAME 			=	"male"
PCR01_FEMALE_GENDER_NAME		=	"female"

PCR01_DEFAULT_MALE_FIGURE		=	"bodybuilder"
PCR01_DEFAULT_FEMALE_FIGURE	=	"slender"

-- -1 == uninitialized, becomes 2 in plastic surgeon and 0 in player creation
-- 0 == nothing has been changed on player
-- 1 == player has randomized values, but not customized any
-- 2 == player has customized values
Pcr01_player_tweaked = -1
Pcr01_dialog = { }

PCR01_YOUNG_AGE_THRESHOLD 		= 0.33
PCR01_MIDDLE_AGE_THRESHOLD		= 0.66

PCR01_HAIR_AREA_HEAD			= 0
PCR01_HAIR_AREA_MUSTACHE	= 1
PCR01_HAIR_AREA_BEARD		= 2
PCR01_HAIR_AREA_SIDEBURNS	= 3
PCR01_HAIR_AREA_EYEBROWS	= 4

PCR01_CHEEK_MAKEUP_INDEX		 = 1
PCR01_ENTIRE_FACE_MAKEUP_INDEX	 = 3

PCR01_FACIAL_EXPRESSIONS_INDEX = 1

Pcr01_hair_colors = {
	[PCR01_HAIR_AREA_HEAD] = { primary = -1, secondary = -1 },
	[PCR01_HAIR_AREA_BEARD] = { primary = -1, secondary = -1 },
}

Pcr01_hair_preview_area = -1
Pcr01_hair_preview_item = -1
Pcr01_hair_preview_color = { primary = -1, secondary = -1 }

Pcr01_hair_color_ref = {
	[PCR01_HAIR_AREA_HEAD]			= PCR01_HAIR_AREA_HEAD,
	[PCR01_HAIR_AREA_MUSTACHE]		= PCR01_HAIR_AREA_BEARD,
	[PCR01_HAIR_AREA_BEARD]			= PCR01_HAIR_AREA_BEARD,
	[PCR01_HAIR_AREA_SIDEBURNS]	= PCR01_HAIR_AREA_HEAD,
	[PCR01_HAIR_AREA_EYEBROWS]		= PCR01_HAIR_AREA_HEAD,
}

Pcr01_current_swatch_peg = -1

function pcr01_spew_hair_info()
	--debug_print("vint", "Pcr01_saved_hair[0].style: "..var_to_string(Pcr01_saved_hair[0].style).."\n")
	--debug_print("vint", "Pcr01_saved_hair[0].primary_color: "..var_to_string(Pcr01_saved_hair[0].primary_color).."\n")
	--debug_print("vint", "Pcr01_saved_hair[0].secondary_color: "..var_to_string(Pcr01_saved_hair[0].secondary_color).."\n")
	--debug_print("vint", "Pcr01_saved_hair[1].style: "..var_to_string(Pcr01_saved_hair[1].style).."\n")
	--debug_print("vint", "Pcr01_saved_hair[1].primary_color: "..var_to_string(Pcr01_saved_hair[1].primary_color).."\n")
	--debug_print("vint", "Pcr01_saved_hair[1].secondary_color: "..var_to_string(Pcr01_saved_hair[1].secondary_color).."\n")
	--debug_print("vint", "Pcr01_saved_hair[2].style: "..var_to_string(Pcr01_saved_hair[2].style).."\n")
	--debug_print("vint", "Pcr01_saved_hair[2].primary_color: "..var_to_string(Pcr01_saved_hair[2].primary_color).."\n")
	--debug_print("vint", "Pcr01_saved_hair[2].secondary_color: "..var_to_string(Pcr01_saved_hair[2].secondary_color).."\n")
	--debug_print("vint", "Pcr01_saved_hair[3].style: "..var_to_string(Pcr01_saved_hair[3].style).."\n")
	--debug_print("vint", "Pcr01_saved_hair[3].primary_color: "..var_to_string(Pcr01_saved_hair[3].primary_color).."\n")
	--debug_print("vint", "Pcr01_saved_hair[3].secondary_color: "..var_to_string(Pcr01_saved_hair[3].secondary_color).."\n")
	--debug_print("vint", "Pcr01_saved_hair[4].style: "..var_to_string(Pcr01_saved_hair[4].style).."\n")
	--debug_print("vint", "Pcr01_saved_hair[4].primary_color: "..var_to_string(Pcr01_saved_hair[4].primary_color).."\n")
	--debug_print("vint", "Pcr01_saved_hair[4].secondary_color: "..var_to_string(Pcr01_saved_hair[4].secondary_color).."\n")

	--debug_print("vint", "Pcr01_hair_colors[PCR01_HAIR_AREA_HEAD].primary: "..var_to_string(Pcr01_hair_colors[PCR01_HAIR_AREA_HEAD].primary).."\n")
	--debug_print("vint", "Pcr01_hair_colors[PCR01_HAIR_AREA_HEAD].secondary: "..var_to_string(Pcr01_hair_colors[PCR01_HAIR_AREA_HEAD].secondary).."\n")
	--debug_print("vint", "Pcr01_hair_colors[PCR01_HAIR_AREA_BEARD].primary: "..var_to_string(Pcr01_hair_colors[PCR01_HAIR_AREA_BEARD].primary).."\n")
	--debug_print("vint", "Pcr01_hair_colors[PCR01_HAIR_AREA_BEARD].secondary: "..var_to_string(Pcr01_hair_colors[PCR01_HAIR_AREA_BEARD].secondary).."\n")

	--debug_print("vint", "Pcr01_hair_preview_area: "..var_to_string(Pcr01_hair_preview_area).."\n")
	--debug_print("vint", "Pcr01_hair_preview_item: "..var_to_string(Pcr01_hair_preview_item).."\n")
	--debug_print("vint", "Pcr01_hair_preview_color.primary: "..var_to_string(Pcr01_hair_preview_color.primary).."\n")
	--debug_print("vint", "Pcr01_hair_preview_color.secondary: "..var_to_string(Pcr01_hair_preview_color.secondary).."\n")

end

function pcr01_init()
	-- Localize "Start without clothing" option [nclok1405]
	if (get_language() ~= "US") then
		Pcr01_exit_menu[1].label = vint_insert_values_in_string("{0} ({1})", {[0] = "CUST_MENU_START_GAME", [1] = "DIVERSION_STREAKING_TITLE"})
	end

	-- this is just here until adjusted for std res
	if vint_hack_is_std_res() == true then
		--vint_set_property(vint_object_find("safe_frame"), "scale", 0.66666, 0.66666)
	end

	--interface_effect_begin("store", 1, 2)

	local event_tracking_name = "Plastic Surgeon"

	menu_init()
	local is_plastic_surgeon = pcr_is_plastic_surgeon()
	if is_plastic_surgeon == false and mp_is_enabled() == false then
		Pcr01_movement_menu.num_items = 5	-- During initial player creation, only 1 melee style is available, so do not show it [nclok1405]
		Pcr01_horz_menu = {
			num_items = 7,
			current_selection = 0,
			[0] = { label = "CUST_MENU_PRESETS", sub_menu = Pcr01_presets_menu },
			[1] = { label = "CUST_MENU_GLOBAL", sub_menu = Pcr01_globals_menu },
			[2] = { label = "CUST_MENU_FINE_TUNING", sub_menu = Pcr01_fine_tuning_menu },
			[3] = { label = "CUST_MENU_HAIR", sub_menu = Pcr01_hair_areas_menu },
			[4] = { label = "CUST_MENU_MAKEUP", sub_menu = Pcr01_makeup_areas_menu },
			[5] = { label = "CUST_MENU_MOVEMENT", sub_menu = Pcr01_movement_menu },
			[6] = { label = "CUST_MENU_EXIT", sub_menu = Pcr01_exit_menu }
		}
		event_tracking_name = "Player Creation"
	else
		Pcr01_horz_menu = {
			num_items = 6,
			current_selection = 0,
			[0] = { label = "CUST_MENU_PRESETS", sub_menu = Pcr01_presets_menu },
			[1] = { label = "CUST_MENU_GLOBAL", sub_menu = Pcr01_globals_menu },
			[2] = { label = "CUST_MENU_FINE_TUNING", sub_menu = Pcr01_fine_tuning_menu },
			[3] = { label = "CUST_MENU_HAIR", sub_menu = Pcr01_hair_areas_menu },
			[4] = { label = "CUST_MENU_MAKEUP", sub_menu = Pcr01_makeup_areas_menu },
			[5] = { label = "CUST_MENU_MOVEMENT", sub_menu = Pcr01_movement_menu },
		}
		event_tracking_name = "MP: Player Creation"
	end
	if mp_is_enabled() == true then
		Pcr01_top_btn_tips.b_button = { label = "COMPLETION_EXIT", 	enabled = btn_tips_default_b, }
		Pcr01_untop_btn_tips.b_button = { label = "MENU_BACK",						enabled = btn_tips_default_b, }
	else
		if pcr_is_plastic_surgeon() == false then
			Pcr01_top_btn_tips.b_button = { label = "CUST_MENU_EXIT", 			enabled = btn_tips_default_b, }
		else
			Pcr01_top_btn_tips.b_button = { label = "CONTROL_RESUME", 			enabled = btn_tips_default_b, }
		end
		Pcr01_untop_btn_tips.b_button = { label = "MENU_BACK",						enabled = btn_tips_default_b, }
	end

	--Event Tracking
	event_tracking_interface_enter(event_tracking_name)

	--Initialize Horz Menu
	menu_horz_init(Pcr01_horz_menu)

	if mp_is_enabled() then
		-- Make sure we back out by fading to black when viewing this in multiplayer mode
		Menu_fade_to_black = true

		-- Hide the hud for the duration
		hud_fade_out()
	end
	pcr01_store_current_makeup()
	pcr01_store_hair_values()
end

function pcr01_store_current_makeup(area_to_store)
	--debug_print("vint", "saving current makeup\n")

	Pcr01_original_values.makeup_variant = Pcr01_current_makeup_variant
	if area_to_store ~= nil and type(area_to_store) ~= "table" then  --the table here is because this function is occasionally passed menu_data when it's called from an on_exit
		Pcr01_saved_makeup[area_to_store].item					= Pcr01_current_makeup_item
		Pcr01_saved_makeup[area_to_store].variant				= Pcr01_current_makeup_variant
		Pcr01_saved_makeup[area_to_store].primary_color			= Pcr01_current_makeup_primary_color
		Pcr01_saved_makeup[area_to_store].secondary_color		= Pcr01_current_makeup_secondary_color
	else
		for area = 0,4 do
			Pcr01_current_makeup_item, Pcr01_current_makeup_variant, Pcr01_current_makeup_primary_color, Pcr01_current_makeup_secondary_color = pcr_get_makeup_info(area)

			Pcr01_saved_makeup[area].item					= Pcr01_current_makeup_item
			Pcr01_saved_makeup[area].variant				= Pcr01_current_makeup_variant
			Pcr01_saved_makeup[area].primary_color		= Pcr01_current_makeup_primary_color
			Pcr01_saved_makeup[area].secondary_color	= Pcr01_current_makeup_secondary_color
		end
	end
end

function pcr01_cleanup()
	-- make sure pegs are unloaded
	peg_unload("ui_pcr_skin")
	peg_unload("ui_pcr_eyes")
	peg_unload("ui_pc_hair")
end

function pcr01_load_swatch_peg(peg_name)
	if Pcr01_current_swatch_peg ~= peg_name then
		if Pcr01_current_swatch_peg ~= -1 then
			peg_unload(Pcr01_current_swatch_peg)
		end

		peg_load(peg_name)
		Pcr01_current_swatch_peg = peg_name
	end
end

-- morph support
function pcr01_change_morph(menu_label, menu_data)
	if menu_label.control.prev_displayed ~= menu_data.cur_value then
		local h = vint_object_find("value_text", menu_label.control.grp_h)
		local new_display = ""

		if menu_data.is_gender == true then
			new_display = ""..(floor(menu_data.cur_value * 100) - 50)
		else
			new_display = ""..(floor(menu_data.cur_value * 100))
		end

		vint_set_property(h, "text_tag", new_display)
		menu_label.control.prev_displayed = menu_data.cur_value
	end

	if menu_data.prev_value ~= menu_data.cur_value then
		pcr_apply_morph_value(menu_data.morph_set, menu_data.morph_id, menu_data.cur_value)
		pcr_mark_changed()
		menu_data.prev_value = menu_data.cur_value
		Pcr01_player_tweaked = 2
	end
end

function pcr01_build_morph_menu(menu_data)
	Pcr01_building_menu = menu_data

	menu_data.num_items = 0
	pcr_report_avail_morphs(menu_data.morph_set, "pcr01_add_morph")
	Pcr01_building_menu = 0

	if menu_data.camera ~= nil then
		store_set_camera_pos(menu_data.camera)
	end
end

function pcr01_hair_preview_cat_color(cat, pcolor, scolor)

	if pcolor == nil then
		pcolor = -1
	end
	if scolor == nil then
		scolor = -1
	end
	-- look for area in the same category and make same color
	local item_id
	for key, value in Pcr01_hair_color_ref do
		if value == cat then
			item_id = pcr_get_hair_info(key)

			if item_id >= 0 then
				pcr_change_hair(key, item_id, pcolor, scolor)
			end
		end
	end
end

function pcr01_hair_update_top_colors()
	local color_cat_area = Pcr01_hair_color_ref[Pcr01_hair_preview_area]
	local color_lookup = Pcr01_hair_colors[color_cat_area]

	-- save the colors - need to copy, no refs allowed
	if Pcr01_hair_preview_color.primary == -1 then
		color_lookup.primary = Pcr01_saved_hair[Pcr01_hair_preview_area].primary_color
	else
		color_lookup.primary = Pcr01_hair_preview_color.primary
	end
	if Pcr01_hair_preview_color.secondary == -1 then
		color_lookup.secondary = Pcr01_saved_hair[Pcr01_hair_preview_area].secondary_color
	else
		color_lookup.secondary = Pcr01_hair_preview_color.secondary
	end

	pcr01_hair_preview_cat_color(color_cat_area, color_lookup.primary, color_lookup.secondary)
end

function pcr01_hair_preview()
	local color_cat = Pcr01_hair_color_ref[Pcr01_hair_preview_area]
	local pcolor = Pcr01_hair_preview_color.primary
	local scolor = Pcr01_hair_preview_color.secondary

	pcr_change_hair(Pcr01_hair_preview_area, Pcr01_hair_preview_item, pcolor, scolor)

	pcr01_hair_preview_cat_color(color_cat, pcolor, scolor)
end

function pcr01_hair_randomize_secondary_color()
	local item, primary_color, secondary_color = pcr_hair_randomize(Pcr01_hair_preview_area, Pcr01_hair_preview_item,
		Pcr01_hair_preview_color.primary, -1)

	if item > -2 then
		Pcr01_hair_preview_color.secondary = secondary_color
		pcr01_hair_preview()
		pcr01_hair_update_top_colors()

		-- update menu yay!
		local swatch_idx = -1
		local swatches = Menu_active[0].swatches

		for i = 0, swatches.num_swatches - 1 do
			if swatches[i].id == secondary_color then
				swatch_idx = i
				break
			end
		end

		if swatch_idx > -1 then
			local menu_data = Menu_active[0]
			local row = floor(swatch_idx / menu_data.num_cols)
			local col = swatch_idx - (row * menu_data.num_cols)

			menu_grid_update_swatches(menu_data, row)
			menu_grid_update_highlighted(menu_data, col, row)

			if menu_data.on_nav ~= nil then
				menu_data.on_nav(nil, menu_data)
			end
		end
	end

	pcr_mark_changed()
	Pcr01_player_tweaked = 1
end

function pcr01_hair_randomize_primary_color()
	local item, primary_color, secondary_color = pcr_hair_randomize(Pcr01_hair_preview_area, Pcr01_hair_preview_item,
		-1, -1)

	if item > -2 then
		Pcr01_hair_preview_color.primary = primary_color
		Pcr01_hair_preview_color.secondary = secondary_color
		pcr01_hair_preview()
		pcr01_hair_update_top_colors()

		-- update menu yay!
		local swatch_idx = -1
		local swatches = Menu_active[0].swatches

		for i = 0, swatches.num_swatches - 1 do
			if swatches[i].id == primary_color then
				swatch_idx = i
				break
			end
		end

		if swatch_idx > -1 then
			local menu_data = Menu_active[0]
			local row = floor(swatch_idx / menu_data.num_cols)
			local col = swatch_idx - (row * menu_data.num_cols)

			menu_grid_update_swatches(menu_data, row)
			menu_grid_update_highlighted(menu_data, col, row)

			if menu_data.on_nav ~= nil then
				menu_data.on_nav(nil, menu_data)
			end
		end
	end

	pcr_mark_changed()
	Pcr01_player_tweaked = 1
end

function pcr01_hair_randomize_area()
	local item, primary_color, secondary_color = pcr_hair_randomize(Pcr01_hair_preview_area, -2, -1, -1)

	if item > -2 then
		Pcr01_hair_preview_item = item
		Pcr01_hair_preview_color.primary = primary_color
		Pcr01_hair_preview_color.secondary = secondary_color
		pcr01_hair_preview()
		pcr01_hair_update_top_colors()

		-- update menu
		local menu_item_index = -1
		for i = 0, Menu_active.num_items - 1 do
			if Menu_active[i].hair_item == item then
				menu_item_index = i
				break
			end
		end

		if menu_item_index > -1 then
			menu_update_nav_bar(menu_item_index)
			audio_play(Menu_sound_item_nav)

			if Menu_active.on_nav ~= nil then
				Menu_active.on_nav(Menu_active)
			end
		end
	end

	pcr_mark_changed()
	Pcr01_player_tweaked = 1
end

function pcr01_hair_randomize_all_areas(result, action)
	if action ~= DIALOG_ACTION_CLOSE then
		return
	end

	if result == 0 then
		pcr_hair_randomize_all()
		pcr_mark_changed()

		Pcr01_player_tweaked = 1

		menu_input_block(true)
		thread_new("delayed_hair_store") --menu input is reenabled here
		--pcr01_spew_hair_info()
	end
end

function delayed_hair_store()
	while (pcu_is_streaming_done() == false) do
		thread_yield()
	end --we won't have valid values to store until the streaming is done
	pcr01_hair_color_get_from_player()
	pcr01_store_hair_values()
	pcr01_hair_color_get_from_player()
	menu_input_block(false)

end


function pcr01_morph_accept()
	Pcr01_player_tweaked = 2
	menu_show(Menu_active.parent_menu, MENU_TRANSITION_SWEEP_LEFT)
end

function pcr01_add_morph(id, name_crc, name_str, value, gender)
	local item = {
		type = MENU_ITEM_TYPE_NUM_SLIDER, morph_id = id, morph_set = Pcr01_building_menu.morph_set,
		is_gender = gender, cur_value = value, prev_value = value, orig_value = value, thumb_width = 55,
		on_value_update = pcr01_change_morph, on_select = pcr01_morph_accept
	}

	if name_crc ~= nil then
		item.label_crc = name_crc
	else
		item.label = name_str
	end

	Pcr01_building_menu[Pcr01_building_menu.num_items] = item
	Pcr01_building_menu.num_items = Pcr01_building_menu.num_items + 1
end

function pcr01_preset_show(result, action)
	if action ~= DIALOG_ACTION_CLOSE then
		return
	end

	if result == 1 then
		menu_show(Pcr01_dialog.cancel_menu, MENU_TRANSITION_SWEEP_RIGHT)
		return
	end

	if Pcr01_current_preset_gender == -1 then
		Pcr01_current_preset_gender, Pcr01_current_preset_race, Pcr01_current_preset_figure = pcr_get_player_preset()
	end

	Pcr01_player_tweaked = 0
	menu_show(Pcr01_dialog.yes_menu, MENU_TRANSITION_SWEEP_LEFT)
end

function pcr01_randomize_confirm(menu_label, menu_data)
	if pcr_is_streaming() == true then
		return
	end

	if Pcr01_player_tweaked == -1 then
		if pcr_is_plastic_surgeon() == true then
			Pcr01_player_tweaked = 2
		else
			Pcr01_player_tweaked = 0
		end
	end
	if Pcr01_player_tweaked < 2 then
		Menu_active.rand_func(0, DIALOG_ACTION_CLOSE)
		return
	end

	local body = "RANDOM_WARNING_BODY"
	local heading = "RANDOM_WARNING_HEADING"
	dialog_box_confirmation(heading, body, Menu_active.rand_func_name)
end

function pcr01_enter_preset(menu_label, menu_data)
	menu_data.sub_menu.parent_menu = Pcr01_presets_menu

	Pcr01_dialog.yes_menu = menu_data.sub_menu
	Pcr01_dialog.cancel_menu = Pcr01_presets_menu

	--debug_print("vint", "tweaked status is"..var_to_string(Pcr01_player_tweaked).."\n")

	if Pcr01_player_tweaked == -1 then
		if pcr_is_plastic_surgeon() == true then
			Pcr01_player_tweaked = 2
		else
			Pcr01_player_tweaked = 0;
		end
	end
	if Pcr01_player_tweaked == 0 then
		pcr01_preset_show(0, DIALOG_ACTION_CLOSE)
		return
	end

	local body
	if Pcr01_current_preset_gender == -1 then
		body = "PRESET_WARNING_BODY1"
	else
		body = "PRESET_WARNING_BODY2"
	end

	local heading = "PRESET_WARNING_HEADING"
	dialog_box_confirmation(heading, body, "pcr01_preset_show")
end

-- presets support
function pcr01_select_preset(menu_label, menu_data)
	local update_preset = false
	local update_regional_preset = false

	if menu_data.preset_gender ~= nil and menu_data.preset_gender ~= Pcr01_current_preset_gender then
		Pcr01_current_preset_gender = menu_data.preset_gender
		update_preset = true
		if Pcr01_current_preset_gender == PCR01_FEMALE_GENDER_NAME then
			Pcr01_current_preset_figure = PCR01_DEFAULT_FEMALE_FIGURE
		else
			Pcr01_current_preset_figure = PCR01_DEFAULT_MALE_FIGURE
		end
	end

	if menu_data.preset_race ~= nil and menu_data.preset_race ~= Pcr01_current_preset_race then
		Pcr01_current_preset_race = menu_data.preset_race
		update_preset = true
	end

	if menu_data.preset_figure ~= nil and menu_data.preset_figure ~= Pcr01_current_preset_figure then
		Pcr01_current_preset_figure = menu_data.preset_figure
		update_regional_preset = true;
	end

	if update_preset == true then
		local preset_name = Pcr01_current_preset_gender .. "_" .. Pcr01_current_preset_race
-- JNW 6.22.08: Apply both presets before components start to stream in.
		local regional_preset_name = Pcr01_current_preset_gender .. "_" .. Pcr01_current_preset_figure;
		pcr_apply_preset(preset_name, "figure", regional_preset_name)
		pcr_mark_changed()
		pcr01_store_hair_values()
		Pcr01_player_tweaked = 0
	else
		if update_regional_preset == true then
			pcr_apply_regional_preset("figure", Pcr01_current_preset_gender .. "_" .. Pcr01_current_preset_figure)
			pcr_mark_changed()
			pcr01_store_hair_values()
			Pcr01_player_tweaked = 0
		end
	end

	menu_show(Pcr01_presets_menu, MENU_TRANSITION_SWEEP_LEFT)
end

function pcr01_clear_saved_makeup()

	Pcr01_current_makeup_area = -1
	Pcr01_current_makeup_item = -1
	Pcr01_current_makeup_variant = -1
	Pcr01_current_makeup_primary_color = -1
	Pcr01_current_makeup_secondary_color = -1
	Pcr01_makeup_color_is_primary = true
	Pcr01_saved_makeup[0] = {item = INVALID_MAKEUP_INDEX, variant = INVALID_MAKEUP_VARIANT, primary_color = INVALID_COLOR, secondary_color = INVALID_COLOR}
	Pcr01_saved_makeup[1] = {item = INVALID_MAKEUP_INDEX, variant = INVALID_MAKEUP_VARIANT, primary_color = INVALID_COLOR, secondary_color = INVALID_COLOR}
	Pcr01_saved_makeup[2] = {item = INVALID_MAKEUP_INDEX, variant = INVALID_MAKEUP_VARIANT, primary_color = INVALID_COLOR, secondary_color = INVALID_COLOR}
	Pcr01_saved_makeup[3] = {item = INVALID_MAKEUP_INDEX, variant = INVALID_MAKEUP_VARIANT, primary_color = INVALID_COLOR, secondary_color = INVALID_COLOR}
	Pcr01_saved_makeup[4] = {item = INVALID_MAKEUP_INDEX, variant = INVALID_MAKEUP_VARIANT, primary_color = INVALID_COLOR, secondary_color = INVALID_COLOR}
end

function pcr01_load_saved_character(result, action)
	if action ~= DIALOG_ACTION_CLOSE then
		return
	end

	if result == 1 then
		--do nothing, we canceled
		return
	end
	--DO IT!!
	--debug_print("vint","pcr: actually load saved game character\n")
	pcr01_clear_saved_makeup()
	pcr01_store_current_makeup()

	multi_load_saved_character()

	--save the makeup it could have changed
	pcr01_store_current_makeup()

	pcr_mark_changed()
end

function pcr01_load_saved_confirm()
	local options = { [0] = "CONTROL_OKAY", [1] = "CONTROL_CANCEL" }
	dialog_box_open("PLAYER_CREATION_IMPORT", "SAVELOAD_IMPORT_GAME_CONFIRM_EXPOSITION", options, "pcr01_load_saved_character", 0, DIALOG_PRIORITY_ACTION)
end

function pcr01_preset_menu_show(menu_label, menu_data)
	-- Allow import in campaign mode [nclok1405]
	--if mp_is_enabled() then
		--add a button tip and set a function for the x button
		Pcr01_presets_menu.btn_tips = Pcr01_mp_preset_btn_tips
		Pcr01_presets_menu.on_alt_select = pcr01_load_saved_confirm
	--end
	--what the old on show did
	pcr01_camera_body_pos()
end
----------------
-- START HAIR --
----------------

function pcr01_hair_color_get_from_player()
	local item, pcv, pcn, scv, scn

	-- get the current colors for hair and beard
	local color_cat = Pcr01_hair_colors[PCR01_HAIR_AREA_HEAD]
	color_cat.primary = -1
	color_cat.secondary = -1
	color_cat.primary_name = ""
	color_cat.secondary_name = ""

	for key, val in Pcr01_hair_color_ref do
		if val == PCR01_HAIR_AREA_HEAD then
			item, pcv, scv, pcn, scn = pcr_get_hair_info(key)

			if item >= 0 then
				color_cat.primary = pcv
				color_cat.secondary = scv
				color_cat.primary_name = pcn
				color_cat.secondary_name = scn
				break
			end
		end
	end

	color_cat = Pcr01_hair_colors[PCR01_HAIR_AREA_BEARD]
	color_cat.primary = -1
	color_cat.secondary = -1
	color_cat.primary_name = ""
	color_cat.secondary_name = ""

	for key, val in Pcr01_hair_color_ref do
		if val == PCR01_HAIR_AREA_BEARD then
			item, pcv, scv, pcn, scn = pcr_get_hair_info(key)

			if item >= 0 then
				color_cat.primary = pcv
				color_cat.secondary = scv
				color_cat.primary_name = pcn
				color_cat.secondary_name = scn
				break
			end
		end
	end
end

function pcr01_hair_item_select(menu_label, menu_data)
	if Pcr01_nav_thread ~= -1 then
		thread_kill(Pcr01_nav_thread)
		Pcr01_nav_thread = -1
	end
	Pcr01_hair_preview_item = menu_data.hair_item
	local color_cat_area = Pcr01_hair_color_ref[Pcr01_hair_preview_area]
	local color_lookup = Pcr01_hair_colors[color_cat_area]

	Pcr01_hair_preview_color.primary = color_lookup.primary
	Pcr01_hair_preview_color.secondary = color_lookup.secondary

	pcr01_hair_preview()
	pcr_mark_changed()
	Pcr01_player_tweaked = 2

	if menu_data == Pcr01_hair_style_menu[0] then
		-- selected no hair so back up to areas
		menu_show(Pcr01_hair_areas_menu, MENU_TRANSITION_SWEEP_LEFT)
	elseif Pcr01_hair_preview_color.primary == -1 then
		-- only show secondary color if it's a head color area
		Pcr01_hair_primary_color_menu.show_secondary = (color_cat_area == PCR01_HAIR_AREA_HEAD)
		Pcr01_hair_primary_color_menu.parent_menu = Menu_active
		Pcr01_hair_secondary_color_menu.parent_menu = Pcr01_hair_primary_color_menu
		menu_show(Pcr01_hair_primary_color_menu, MENU_TRANSITION_SWEEP_LEFT)
	else
		menu_show(Pcr01_hair_areas_menu, MENU_TRANSITION_SWEEP_LEFT)
	end
end

function pcr01_globals_show(menu_data)
	pcr01_camera_body_pos()

	-- set the initial value of sliders

	for i = 0, 3 do
		local slider = menu_data[i]
		local val = pcr_get_morph_value(slider.morph_set, slider.morph_id)
		slider.cur_value = val
		slider.prev_value = val
		slider.orig_value = val
	end
end

function pcr01_hair_areas_show(menu_data)
	pcr01_camera_head_pos()
	pcr01_hair_color_get_from_player()
	pcr01_store_hair_values()
	pcr01_restore_makeup() --when the player uses shoulder buttons to navigate away from the menu, makeup needs to be reset
	--and the only way to do this was putting it in the on_show of adjacent menues
end

function pcr01_hair_style_nav(menu_data)
	if Pcr01_nav_thread ~= -1 then
		thread_kill(Pcr01_nav_thread)
		Pcr01_nav_thread = -1
	end

	Pcr01_nav_value = menu_data[menu_data.highlighted_item].hair_item
	Pcr01_nav_thread = thread_new("pcr01_delayed_set_hair_item")
end

function pcr01_hair_style_show(menu_data)
	if Pcr01_nav_thread > -1 then
		thread_kill(Pcr01_nav_thread)
		Pcr01_nav_thread = -1
	end

	local hair_area = Pcr01_hair_areas_menu[Pcr01_hair_areas_menu.highlighted_item].hair_area
	Pcr01_hair_preview_area = hair_area
	Pcr01_hair_preview_item = pcr_get_hair_info(hair_area)

	local color_set = Pcr01_hair_colors[Pcr01_hair_color_ref[hair_area]]
	Pcr01_hair_preview_color.primary = color_set.primary
	Pcr01_hair_preview_color.secondary = color_set.secondary

	Pcr01_building_menu = menu_data

	menu_data.header_label_str = Pcr01_hair_areas_menu[Pcr01_hair_areas_menu.highlighted_item].header_label_str

	menu_data[0] = {
		label = "HAIR_CAT_NONE", type = MENU_ITEM_TYPE_SELECTABLE, hair_area = hair_area,
		hair_item = -1, on_select = pcr01_hair_item_select }

	menu_data.hair_area = hair_area
	menu_data.highlighted_item = 0
	Pcr01_building_menu = menu_data
	menu_data.num_items = 1
	pcr_report_hair_items(hair_area, "pcr01_add_hair_item")
	Pcr01_building_menu = 0
	pcr01_camera_head_pos()
end

function pcr01_highlight_random_swatch(result, action)
	if action ~= DIALOG_ACTION_CLOSE then
		return
	end

	if result == 0 then
		local swatches = Menu_active[0].swatches
		local new_swatch_idx = rand_int(0, swatches.num_swatches - 1)
		local menu_data = Menu_active[0]

		local row = floor(new_swatch_idx / menu_data.num_cols)
		local col = new_swatch_idx - (row * menu_data.num_cols)

		menu_grid_update_swatches(menu_data, row)
		menu_grid_update_highlighted(menu_data, col, row)

		if menu_data.on_nav ~= nil then
			menu_data.on_nav(nil, menu_data)
		end

		if Pcr01_player_tweaked == 2 then
			Pcr01_player_tweaked = 1
		end
	end
end

function pcr01_highlight_random_item()
	local new_item = rand_int(0, Menu_active.num_items - 1)

	menu_update_nav_bar(new_item)
	audio_play(Menu_sound_item_nav)

	if Menu_active.on_nav ~= nil then
		Menu_active.on_nav(Menu_active)
	end
end

function pcr01_add_hair_item(hair_item, label_crc, label_str, is_current)
	Pcr01_building_menu[Pcr01_building_menu.num_items] = {
		type = MENU_ITEM_TYPE_SELECTABLE, hair_area = Pcr01_building_menu.hair_area,
		hair_item = hair_item, on_select = pcr01_hair_item_select, label = label_str, label_crc = label_crc
	}

	if is_current == true then

		Pcr01_building_menu.highlighted_item = Pcr01_building_menu.num_items
	end

	Pcr01_building_menu.num_items = Pcr01_building_menu.num_items + 1
end

function pcr01_hair_style_back()
	if pcu_is_streaming_done() then  --make sure hair doesn't update as we back out
		if Pcr01_nav_thread ~= -1 then
			thread_kill(Pcr01_nav_thread)
			Pcr01_nav_thread = -1
		end
		--debug_print("vint", "backing out of hair with"..var_to_string(Pcr01_saved_hair[Pcr01_hair_preview_area].style).."\n")
		if Pcr01_saved_hair[Pcr01_hair_preview_area].style ~= nil then
			Pcr01_hair_preview_item = Pcr01_saved_hair[Pcr01_hair_preview_area].style
			pcr01_hair_preview()
		end

		audio_play(Menu_sound_back)

		menu_show(Menu_active.parent_menu, MENU_TRANSITION_SWEEP_RIGHT)
	end
end

function pcr01_hair_color_grid_show(menu_data)
	local menu_item = menu_data[0]

	Pcr01_original_values.skin_color = nil
	menu_item.swatches = { num_swatches = 0 }
	Pcr01_building_menu = menu_data
	pcr_report_hair_colors(Pcr01_hair_preview_area, menu_data.is_primary, "pcr01_add_hair_color")
	pcr01_load_swatch_peg("ui_pc_hair")

	menu_grid_show(menu_data, menu_item, vint_object_find("swatch_hair"))
end

function pcr01_add_hair_color(id, swatch_crc, label_crc, label_str, current, swatch_label)
	local swatches = Pcr01_building_menu[0].swatches
	swatches[swatches.num_swatches] = {
		id = id, swatch_crc = swatch_crc, label_crc = label_crc, label_str = label_str, swatch_label = swatch_label
	}

	if current == true then

		Pcr01_building_menu[0].cur_idx = swatches.num_swatches
	end

	swatches.num_swatches = swatches.num_swatches + 1
end

function pcr01_delayed_set_hair_item()
	delay(0.8)

	Pcr01_hair_preview_item = Pcr01_nav_value
	pcr01_hair_preview()
	Pcr01_nav_value = -1

	Pcr01_nav_thread = -1
end

function pcr01_hair_color_delayed_set()
	delay(0.8)

	if Pcr01_nav_value > -1 then
		if Menu_active.is_primary == true then
			Pcr01_hair_preview_color.primary = Pcr01_nav_value
		else
			Pcr01_hair_preview_color.secondary = Pcr01_nav_value
		end
		pcr01_hair_preview()
		Pcr01_nav_value = -1
	end

	Pcr01_nav_thread = -1
end

function pcr01_hair_color_nav(menu_option, menu_data)
	if Pcr01_nav_thread > -1 then
		thread_kill(Pcr01_nav_thread)
		Pcr01_nav_thread = -1
	end

	local swatches = menu_data.swatches
	local idx = menu_data.cur_row * menu_data.num_cols + menu_data.cur_col

	if idx < swatches.num_swatches then
		Pcr01_nav_value = swatches[idx].id
		Pcr01_nav_thread = thread_new("pcr01_hair_color_delayed_set")
	end
end

function pcr01_store_hair_values()

	--debug_print("vint", "about to store hair values\n")
	for hair_area_iter = 0, 4 do
		Pcr01_saved_hair[hair_area_iter].style, Pcr01_saved_hair[hair_area_iter].primary_color,
		Pcr01_saved_hair[hair_area_iter].secondary_color = pcr_get_hair_info(hair_area_iter)
		--[[
		debug_print("vint", "area: "..var_to_string(hair_area_iter).." style: "..var_to_string(Pcr01_saved_hair[hair_area_iter].style)..
			" primary color: "..var_to_string(Pcr01_saved_hair[hair_area_iter].primary_color)..
			" secondary color: "..var_to_string(Pcr01_saved_hair[hair_area_iter].secondary_color).."\n")
		--]]
	end
end

function pcr01_restore_primary_hair_values()
	if Pcr01_nav_thread ~= -1 then
		thread_kill(Pcr01_nav_thread)
		Pcr01_nav_thread = -1
	end
	for hair_area_iter = 0, 4 do
		if Pcr01_saved_hair[hair_area_iter].primary_color ~= nil then
			Pcr01_hair_preview_color.primary = Pcr01_saved_hair[hair_area_iter].primary_color
			Pcr01_hair_preview_color.secondary = -1
			Pcr01_hair_preview_area = hair_area_iter
			pcr01_hair_update_top_colors()
		end
	end
end

function pcr01_restore_secondary_hair_values()
	if Pcr01_nav_thread ~= -1 then
		thread_kill(Pcr01_nav_thread)
		Pcr01_nav_thread = -1
	end
	for hair_area_iter = 0, 4 do
		if Pcr01_saved_hair[hair_area_iter].secondary_color ~= nil then
			Pcr01_hair_preview_color.primary = -1
			Pcr01_hair_preview_color.secondary = Pcr01_saved_hair[hair_area_iter].secondary_color
			--debug_print("vint", "SC: "..var_to_string(Pcr01_saved_hair[hair_area_iter].secondary_color).."\n")
			Pcr01_hair_preview_area = hair_area_iter
			pcr01_hair_update_top_colors()
		end
	end
end

function pcr01_restore_hair_values()

	if Pcr01_nav_thread ~= -1 then
		thread_kill(Pcr01_nav_thread)
		Pcr01_nav_thread = -1
	end
	--debug_print("vint", "About to restore hair\n")
	for hair_area_iter = 0, 4 do
		local preview_needed = false
		if Pcr01_saved_hair[hair_area_iter].style ~= nil then
			Pcr01_hair_preview_item = Pcr01_saved_hair[hair_area_iter].style
			preview_needed = true;
			--debug_print("vint", "The new hair style is "..var_to_string(hair_area_iter).."\n");
		end
		if Pcr01_saved_hair[hair_area_iter].primary_color ~= nil then
			Pcr01_hair_preview_color.primary = Pcr01_saved_hair[hair_area_iter].primary_color
			preview_needed = true;
			Pcr01_hair_preview_area = hair_area_iter
			pcr01_hair_update_top_colors()
			--debug_print("vint", "The new hair primary color is "..var_to_string(hair_area_iter).."\n");
		end
		if Pcr01_saved_hair[hair_area_iter].secondary_color ~= nil then
			Pcr01_hair_preview_color.secondary = Pcr01_saved_hair[hair_area_iter].secondary_color
			preview_needed = true;
			Pcr01_hair_preview_area = hair_area_iter
			pcr01_hair_update_top_colors()
			--debug_print("vint", "The new hair style is "..var_to_string(hair_area_iter).."\n");
		end
		if preview_needed == true then
			Pcr01_hair_preview_area = hair_area_iter
			pcr01_hair_preview()
		end
	end

end


function pcr01_hair_color_category_select(menu_label, menu_item)
	Pcr01_hair_preview_area  = menu_item.hair_area
	Pcr01_hair_preview_item, Pcr01_hair_preview_color.primary, Pcr01_hair_preview_color.secondary = pcr_get_hair_info(Pcr01_hair_preview_area)
	local menu = nil

	if menu_item.is_primary == false then
		menu = Pcr01_hair_secondary_color_menu
	else
		menu = Pcr01_hair_primary_color_menu
	end

	menu.show_secondary = false
	menu.parent_menu = Menu_active
	menu_show(menu, MENU_TRANSITION_SWEEP_LEFT)
end

function pcr01_hair_color_select(menu_option, menu_data)
	if Pcr01_nav_thread > -1 then
		thread_kill(Pcr01_nav_thread)
		Pcr01_nav_thread = -1
	end
	local swatches = menu_data.swatches
	local idx = menu_data.cur_row * menu_data.num_cols + menu_data.cur_col

	if idx < swatches.num_swatches then
		if Menu_active.is_primary == true then
			Pcr01_hair_preview_color.primary = swatches[idx].id
		else
			Pcr01_hair_preview_color.secondary = swatches[idx].id
		end
		pcr01_hair_preview()
		pcr01_hair_update_top_colors()
		pcr_mark_changed()
		Pcr01_player_tweaked = 2
	end
--	pcr01_spew_hair_info()
	if Menu_active.is_primary == true and Menu_active.show_secondary == true then
		menu_show(Pcr01_hair_secondary_color_menu, MENU_TRANSITION_SWEEP_LEFT)
	else
		menu_show(Pcr01_hair_areas_menu, MENU_TRANSITION_SWEEP_LEFT)
	end
end

function pcr01_hair_color_grid_back(menu_option, menu_data)
	if Pcr01_nav_thread > -1 then
		thread_kill(Pcr01_nav_thread)
		Pcr01_nav_thread = -1
	end

	--debug_print("vint", "the area we're backing out of is: "..var_to_string(Pcr01_hair_preview_area).."\n")
	if Menu_active.is_primary == true then
		--debug_print("vint", "primary\n")
		pcr01_restore_primary_hair_values()
	else
		--debug_print("vint", "secondary\n")
		pcr01_restore_secondary_hair_values()
	end

	audio_play(Menu_sound_back)

	menu_show(Menu_active.parent_menu, MENU_TRANSITION_SWEEP_RIGHT)
end

function pcr01_hair_color_grid_release(menu)
	menu_grid_release(menu[0])
end

function pcr01_hair_color_update_swatch(swatch)
	local label = vint_object_find("label_text", swatch.swatch_h)
	vint_set_property(label, "text_tag", swatch.swatch_label)
end

-- voice
function pcr01_set_voice(menu_label, menu_data)
	pcr_set_voice(menu_data.voice, false)
	pcr_mark_changed()
	Pcr01_player_tweaked = 2
	menu_show(Pcr01_movement_menu, MENU_TRANSITION_SWEEP_LEFT)
end

function pcr01_nav_voice(menu_data)
	pcr_set_voice(menu_data[menu_data.highlighted_item].voice)
end

function pcr01_voice_menu_show(menu_data)
	pcr_set_voice("play_current")
	menu_data.highlighted_item = pcr_get_current_voice_number()
	pcr01_camera_head_pos()
end

-- makeup
function pcr01_makeup_area_list_show()
	Pcr01_current_makeup_variant = 0
	Pcr01_current_makeup_primary_color = -1
	Pcr01_current_makeup_secondary_color = -1

	pcr01_restore_hair_values()
	pcr01_store_current_makeup()

	pcr01_camera_head_pos()
end

function pcr01_set_makeup_item(menu_label, menu_data)
	Pcr01_current_makeup_item = menu_data.makeup_item
	pcr01_makeup_update()

	if Menu_active.highlighted_item == 0 then
		pcr_mark_changed()	-- Removal is permanent
		Pcr01_player_tweaked = 2
		menu_show(Pcr01_makeup_areas_menu, MENU_TRANSITION_SWEEP_LEFT)
		return
	end
	Pcr01_makeup_variations_menu.num_items = 0
	pcr_report_makeup_variants(Pcr01_current_makeup_item, "pcr01_makeup_variation_add_item")
	Pcr01_current_makeup_variant = 0

	if Pcr01_makeup_variations_menu.num_items < 2 then
		Pcr01_makeup_primary_color_menu.parent_menu = Menu_active
		menu_show(Pcr01_makeup_primary_color_menu, MENU_TRANSITION_SWEEP_LEFT)
	else
		Pcr01_makeup_variations_menu.parent_menu = Menu_active
		menu_show(Pcr01_makeup_variations_menu, MENU_TRANSITION_SWEEP_LEFT)
	end
end

function pcr01_makeup_item_delayed_set()
	delay(0.8)

	pcr01_makeup_update()

	Pcr01_nav_thread = -1
end

function pcr01_makeup_item_nav()
	if Pcr01_nav_thread ~= -1 then
		thread_kill(Pcr01_nav_thread)
		Pcr01_nav_thread = -1
	end

	if Menu_active == Pcr01_makeup_variations_menu then
		Pcr01_current_makeup_variant = Menu_active[Menu_active.highlighted_item].makeup_variant
	else
		Pcr01_current_makeup_variant = 0
		Pcr01_current_makeup_item = Menu_active[Menu_active.highlighted_item].makeup_item
	end

	Pcr01_nav_thread = thread_new("pcr01_makeup_item_delayed_set")
end

function prc01_makeup_variant_show()
	if Menu_active == Pcr01_makeup_variations_menu then
		Pcr01_current_makeup_variant = Menu_active[Menu_active.highlighted_item].makeup_variant
	else
		Pcr01_current_makeup_variant = 0
		if Menu_active[Menu_active.highlighted_item].makeup_item ~= nil then
			Pcr01_current_makeup_item = Menu_active[Menu_active.highlighted_item].makeup_item
		end
	end
end

function pcr01_build_makeup_menu(menu_data)
	if Menu_active[Menu_active.highlighted_item].makeup_area ~= nil then
		Pcr01_current_makeup_area = Menu_active[Menu_active.highlighted_item].makeup_area
	end

	Pcr01_building_menu = menu_data
	Pcr01_building_menu.num_items = 1
	Pcr01_building_menu[0] = {
		label = "CUST_ITEM_NOTHING", type = MENU_ITEM_TYPE_SELECTABLE, makeup_item = -1, on_select = pcr01_set_makeup_item }
	Pcr01_building_menu.highlighted_item = 0 --default the first item to be highlighted,
														--add_make_up_item will change this to currently worn item
	pcr_report_makeup_items(Pcr01_current_makeup_area, "pcr01_add_makeup_item")

end

function pcr01_add_makeup_item(makeup_index, name_crc, name_str, current)
	local item = {
		type = MENU_ITEM_TYPE_SELECTABLE, makeup_item = makeup_index, on_select = pcr01_set_makeup_item
	}

	if name_crc == nil then
		item.label = name_str
	else
		item.label_crc = name_crc
	end

	if current == true then
		Pcr01_building_menu.highlighted_item = Pcr01_building_menu.num_items

		if Pcr01_original_values.makeup_item == nil then
			Pcr01_original_values.makeup_item = makeup_index
		end
	end

	Pcr01_building_menu[Pcr01_building_menu.num_items] = item
	Pcr01_building_menu.num_items = Pcr01_building_menu.num_items + 1
end

function pcr01_makeup_color_grid_show(menu_data)
	local menu_item = menu_data[0]

	menu_item.swatches = { num_swatches = 0 }
	Pcr01_building_menu = menu_data
	Pcr01_makeup_color_is_primary = menu_data.is_primary
	pcr_report_makeup_colors(Pcr01_current_makeup_area, Pcr01_makeup_color_is_primary, "pcr01_makeup_add_color")

	local swatch_template = vint_object_find("swatch_color", nil, MENU_BASE_DOC_HANDLE)
	menu_grid_show(menu_data, menu_item, swatch_template)
end

function pcr01_makeup_add_color(color_index, label_crc, label_str, red, green, blue, max_colors, is_current)
	local item = {
		type = MENU_ITEM_TYPE_SELECTABLE, color_index = color_index, on_select = pcr01_select_makeup_color,
		red = red, green = green, blue = blue, max_colors = max_colors,
	}

	if label_crc == nil then
		item.label_str = label_str
	else
		item.label_crc = label_crc
	end

	local swatches = Pcr01_building_menu[0].swatches
	swatches[swatches.num_swatches] = item

	if is_current == true then
		Pcr01_building_menu[0].cur_idx = swatches.num_swatches
	end

	swatches.num_swatches = swatches.num_swatches + 1
end

function pcr01_delayed_set_makeup_color()
	delay(0.8)

	if Pcr01_nav_value > -1 then
		if Menu_active.is_primary == true then
			Pcr01_current_makeup_primary_color = Pcr01_nav_value
		else
			Pcr01_current_makeup_secondary_color = Pcr01_nav_value
		end
		pcr01_makeup_update()
	end

	Pcr01_nav_thread = -1
end

function pcr01_nav_makeup_color(menu_option, menu_data)
	if Pcr01_nav_thread > -1 then
		thread_kill(Pcr01_nav_thread)
		Pcr01_nav_thread = -1
	end

	local swatches = menu_data.swatches
	local idx = menu_data.cur_row * menu_data.num_cols + menu_data.cur_col

	if idx < swatches.num_swatches then
		Pcr01_nav_value = swatches[idx].color_index
		Pcr01_nav_thread = thread_new("pcr01_delayed_set_makeup_color")
	end
end

function pcr01_select_makeup_color(menu_option, menu_data)
	if Pcr01_nav_thread > -1 then
		thread_kill(Pcr01_nav_thread)
		Pcr01_nav_thread = -1
	end

	local swatch_idx = menu_data.cur_row * menu_data.num_cols + menu_data.cur_col
	local color_index = menu_data.swatches[swatch_idx].color_index

	if Menu_active.is_primary == true then
		Pcr01_current_makeup_primary_color = color_index
	else
		Pcr01_current_makeup_secondary_color = color_index
	end

	pcr01_makeup_update()

	--cheek makeup only has a primary color
	if Menu_active.is_primary == true and Pcr01_current_makeup_area ~= PCR01_CHEEK_MAKEUP_INDEX then
		menu_show(Pcr01_makeup_secondary_color_menu, MENU_TRANSITION_SWEEP_RIGHT)
	else
		pcr_mark_changed()	-- Okay, *now* it's permanent
		Pcr01_player_tweaked = 2
		menu_show(Pcr01_makeup_areas_menu, MENU_TRANSITION_SWEEP_LEFT)
	end
end

function pcr01_makeup_color_grid_back(menu_option, menu_data)
	if Pcr01_nav_thread > -1 then
		thread_kill(Pcr01_nav_thread)
		Pcr01_nav_thread = -1
	end

	if Menu_active.is_primary == true then
		if Pcr01_original_values.makeup_primary_color ~= nil then
			Pcr01_current_makeup_primary_color = Pcr01_original_values.makeup_primary_color
			pcr01_makeup_update()
		end
	else
		if Pcr01_original_values.makeup_secondary_color ~= nil then
			Pcr01_current_makeup_secondary_color = Pcr01_original_values.makeup_secondary_color
			pcr01_makeup_update()
		end

		Menu_active.parent_menu = Pcr01_makeup_primary_color_menu
	end

	audio_play(Menu_sound_back)

	menu_show(Menu_active.parent_menu, MENU_TRANSITION_SWEEP_RIGHT)
end

function pcr01_makeup_color_grid_release(menu)
	menu_grid_release(menu[0])
end

function pcr01_makeup_color_update_swatch(swatch)
	local fill = vint_object_find("fill", swatch.swatch_h)
	vint_set_property(fill, "tint", swatch.red, swatch.green, swatch.blue)
end

function pcr01_makeup_item_back()
	if Pcr01_nav_thread ~= -1 then
		thread_kill(Pcr01_nav_thread)
		Pcr01_nav_thread = -1
	end

	pcr01_restore_makeup()

	audio_play(Menu_sound_back)

	menu_show(Menu_active.parent_menu, MENU_TRANSITION_SWEEP_RIGHT)
end

function pcr01_makeup_variant_back()
	if Pcr01_nav_thread ~= -1 then
		thread_kill(Pcr01_nav_thread)
		Pcr01_nav_thread = -1
	end

	if Pcr01_original_values.makeup_variant ~= nil then
		Pcr01_current_makeup_variant = Pcr01_original_values.makeup_variant
		pcr01_makeup_update()
	end

	audio_play(Menu_sound_back)

	menu_show(Menu_active.parent_menu, MENU_TRANSITION_SWEEP_RIGHT)
end


function pcr01_restore_makeup()
	--debug_print("vint", "trying to restore makeup\n")
	for area = 0, 4 do
		pcr_change_makeup(area,
								Pcr01_saved_makeup[area].item,
								Pcr01_saved_makeup[area].variant,
								Pcr01_saved_makeup[area].primary_color,
								Pcr01_saved_makeup[area].secondary_color)

	end
end

function pcr01_makeup_update()
	pcr_change_makeup(Pcr01_current_makeup_area,
							Pcr01_current_makeup_item,
							Pcr01_current_makeup_variant,
							Pcr01_current_makeup_primary_color,
							Pcr01_current_makeup_secondary_color)
end

function pcr01_makeup_set_variant(menu_label, menu_data)
	Pcr01_current_makeup_variant = menu_data.makeup_variant
	pcr01_makeup_update()		-- Not permanent until you choose a color

	Pcr01_makeup_primary_color_menu.parent_menu = Menu_active

	menu_show(Pcr01_makeup_primary_color_menu, MENU_TRANSITION_SWEEP_LEFT)
end

function pcr01_makeup_variation_add_item(variant, name_crc, name_str, max_colors, current)
	local item = {
		type = MENU_ITEM_TYPE_SELECTABLE, makeup_variant = variant, on_select = pcr01_makeup_set_variant, max_colors = max_colors
	}

	if name_crc ~= nil then
		item.label_crc = name_crc
	else
		item.label = name_str
	end

	if current == true then
		Pcr01_makeup_variations_menu.highlighted_item = Pcr01_makeup_variations_menu.num_items

		if Pcr01_original_values.makeup_variant == nil then
			Pcr01_original_values.makeup_variant = variant
		end
	end

	Pcr01_makeup_variations_menu[Pcr01_makeup_variations_menu.num_items] = item
	Pcr01_makeup_variations_menu.num_items = Pcr01_makeup_variations_menu.num_items + 1
end

function pcr01_makeup_randomize_variant(result, action)
	if action ~= DIALOG_ACTION_CLOSE then
		return
	end
	if result == 0 then
		local item, variant, primary_color, secondary_color = pcr_makeup_randomize(Pcr01_current_makeup_area, Pcr01_current_makeup_item, -1, -1, -1)
		item = Pcr01_current_makeup_item

		if item > -2 then

			-- update menu
			local menu_item_index = -1
			for i = 0, Menu_active.num_items - 1 do
				if Menu_active[i].makeup_variant == variant then
					menu_item_index = i
					break
				end
			end

			if menu_item_index > -1 then
				menu_update_nav_bar(menu_item_index)
				audio_play(Menu_sound_item_nav)

				if Menu_active.on_nav ~= nil then
					Menu_active.on_nav(Menu_active)
				end
			end

		end

		Pcr01_current_makeup_variant = variant
		Pcr01_current_makeup_primary_color = primary_color
		Pcr01_current_makeup_secondary_color = secondary_color

		pcr01_store_current_makeup(Pcr01_current_makeup_area)
		pcr_mark_changed()

		Pcr01_player_tweaked = 1
	end
end

function pcr01_makeup_randomize_primary_color(result, action)
	if action ~= DIALOG_ACTION_CLOSE then
		return
	end

	if result == 0 then
		local item, variant, primary_color, secondary_color = pcr_makeup_randomize(Pcr01_current_makeup_area, Pcr01_current_makeup_item,
			Pcr01_current_makeup_variant, -1, -1)

		if item > -2 then

			-- update menu yay!
			local swatch_idx = -1
			local swatches = Menu_active[0].swatches

			for i = 0, swatches.num_swatches - 1 do
				if swatches[i].color_index == primary_color then
					swatch_idx = i
					break
				end
			end

			if swatch_idx > -1 then
				local menu_data = Menu_active[0]
				local row = floor(swatch_idx / menu_data.num_cols)
				local col = swatch_idx - (row * menu_data.num_cols)

				menu_grid_update_swatches(menu_data, row)
				menu_grid_update_highlighted(menu_data, col, row)

				if menu_data.on_nav ~= nil then
					menu_data.on_nav(nil, menu_data)
				end
			end

		end

		Pcr01_current_makeup_primary_color = primary_color
		Pcr01_current_makeup_secondary_color = secondary_color

		pcr_change_makeup(Pcr01_current_makeup_area, item, variant, primary_color, secondary_color)
		pcr01_store_current_makeup(Pcr01_current_makeup_area)
		pcr_mark_changed()

		Pcr01_player_tweaked = 1
	end
end

function pcr01_makeup_randomize_secondary_color(result, action)
	if action ~= DIALOG_ACTION_CLOSE then
		return
	end

	if result == 0 then
		local item, variant, primary_color, secondary_color = pcr_makeup_randomize(Pcr01_current_makeup_area, Pcr01_current_makeup_item,
			Pcr01_current_makeup_variant, Pcr01_current_makeup_primary_color, -1)

		if item > -2 then

			-- update menu yay!
			local swatch_idx = -1
			local swatches = Menu_active[0].swatches

			for i = 0, swatches.num_swatches - 1 do
				if swatches[i].color_index == secondary_color then
					swatch_idx = i
					break
				end
			end

			if swatch_idx > -1 then
				local menu_data = Menu_active[0]
				local row = floor(swatch_idx / menu_data.num_cols)
				local col = swatch_idx - (row * menu_data.num_cols)

				menu_grid_update_swatches(menu_data, row)
				menu_grid_update_highlighted(menu_data, col, row)

				if menu_data.on_nav ~= nil then
					menu_data.on_nav(nil, menu_data)
				end
			end
		end
		Pcr01_current_makeup_secondary_color = secondary_color

		pcr_change_makeup(Pcr01_current_makeup_area, item, variant, primary_color, secondary_color)
		pcr01_store_current_makeup(Pcr01_current_makeup_area)
		pcr_mark_changed()

		Pcr01_player_tweaked = 1
	end
end

function pcr01_makeup_randomize_area(result, action)
	if action ~= DIALOG_ACTION_CLOSE then
		return
	end

	if result == 0 then
		local item, variant, primary_color, secondary_color = pcr_makeup_randomize(Pcr01_current_makeup_area, -2, -1, -1, -1)

		if item > -2 then

			-- update menu
			local menu_item_index = -1
			for i = 0, Menu_active.num_items - 1 do
				if Menu_active[i].makeup_item == item then
					menu_item_index = i
					break
				end
			end

			if menu_item_index > -1 then
				menu_update_nav_bar(menu_item_index)
				audio_play(Menu_sound_item_nav)

				if Menu_active.on_nav ~= nil then
					Menu_active.on_nav(Menu_active)
				end
			end

		end

		Pcr01_current_makeup_item = item
		Pcr01_current_makeup_variant = variant
		Pcr01_current_makeup_primary_color = primary_color
		Pcr01_current_makeup_secondary_color = secondary_color

		pcr_change_makeup(Pcr01_current_makeup_area, item, variant, primary_color, secondary_color)
		pcr01_store_current_makeup(Pcr01_current_makeup_area)
		pcr_mark_changed()

		Pcr01_player_tweaked = 1
	end
end

function pcr01_makeup_randomize_all_areas(result, action)
	if action ~= DIALOG_ACTION_CLOSE then
		return
	end
	if pcu_is_streaming_done() == false then
		return
	end

	if result == 0 then
		local item, variant, primary_color, secondary_color

		for area = 0, 4 do
			if area ~= PCR01_ENTIRE_FACE_MAKEUP_INDEX then
				item, variant, primary_color, secondary_color = pcr_makeup_randomize(area, -2, -1, -1, -1)
				if item > -2 then
					pcr_change_makeup(area, item, variant, primary_color, secondary_color)
				end
			end
		end

		pcr_mark_changed()
		Pcr01_player_tweaked = 1
	end
	pcr01_store_current_makeup()
end

function pcr01_morph_set_accept()
	Pcr01_player_tweaked = 2
	menu_show(Pcr01_fine_tuning_menu, MENU_TRANSITION_SWEEP_LEFT)
end

function pcr01_morph_set_revert_confirm(result, action)
	if action ~= DIALOG_ACTION_CLOSE or (result ~= 0 and result ~= 1) then
		return
	end
	if result == 0 then
		pcr01_morph_set_accept()
	else
		for i = 0, Menu_active.num_items - 1 do
			local m = Menu_active[i]
			if m.morph_id ~= nil then
				pcr_apply_morph_value(m.morph_set, m.morph_id, m.orig_value)
			end
		end
		audio_play(Menu_sound_back)
		menu_show(Menu_active.parent_menu, MENU_TRANSITION_SWEEP_RIGHT)
	end
end

function pcr01_morph_set_revert()
	local options = { [0] = "PAUSE_MENU_ACCEPT", [1] = "PAUSE_MENU_REVERT", [2] = "CONTROL_CANCEL" }
	dialog_box_open( "STORE_EXIT_WARNING_HEADER", "PLAYER_CREATION_ABOUT_TO_REVERT", options, "pcr01_morph_set_revert_confirm", 0, DIALOG_PRIORITY_ACTION )
end

----------------------
-- START SKIN COLOR --
----------------------
function pcr01_skin_grid_show(menu_data)
	local menu_item = menu_data[0]

	Pcr01_original_values.skin_color = nil
	menu_item.swatches = { num_swatches = 0 }
	pcr_report_skin_colors("pcr01_add_skin_color")

	pcr01_load_swatch_peg("ui_pcr_skin")

	local master_swatch = vint_object_find("swatch_skin", nil, MENU_BASE_DOC_HANDLE)
	menu_grid_show(menu_data, menu_item, master_swatch)
	pcr01_camera_body_pos()
end

function pcr01_add_skin_color(id, swatch_crc, label_crc, label_str, current)
	local swatches = Pcr01_global_skin_menu[0].swatches
	swatches[swatches.num_swatches] = {
		id = id, swatch_crc = swatch_crc, label_crc = label_crc, label_str = label_str
	}

	if current == true then
		Pcr01_original_values.skin_color = id
		Pcr01_global_skin_menu[0].cur_idx = swatches.num_swatches
	end

	swatches.num_swatches = swatches.num_swatches + 1
end

function pcr01_delayed_set_skin_color()
	delay(0.8)

	if Pcr01_nav_value > -1 then
		pcr_change_skin_color(Pcr01_nav_value)
		Pcr01_nav_value = -1
	end

	Pcr01_nav_thread = -1
end

function pcr01_nav_skin_color(menu_option, menu_data)
	if Pcr01_nav_thread > -1 then
		thread_kill(Pcr01_nav_thread)
		Pcr01_nav_thread = -1
	end

	local swatches = menu_data.swatches
	local idx = menu_data.cur_row * menu_data.num_cols + menu_data.cur_col

	if idx < swatches.num_swatches then
		Pcr01_nav_value = swatches[idx].id
		Pcr01_nav_thread = thread_new("pcr01_delayed_set_skin_color")
	end
end

function pcr01_select_skin_color(menu_option, menu_data)
	local swatches = menu_data.swatches
	local idx = menu_data.cur_row * menu_data.num_cols + menu_data.cur_col

	if idx < swatches.num_swatches then
		pcr_change_skin_color(swatches[idx].id)
		pcr_mark_changed()
		Pcr01_player_tweaked = 2
		Pcr01_original_values.skin_color = nil;
	end

	menu_show(Pcr01_globals_menu, MENU_TRANSITION_SWEEP_LEFT)
end

function pcr01_skin_grid_back(menu_option, menu_data)
	if Pcr01_nav_thread > -1 then
		thread_kill(Pcr01_nav_thread)
		Pcr01_nav_thread = -1
	end

	audio_play(Menu_sound_back)

	menu_show(Menu_active.parent_menu, MENU_TRANSITION_SWEEP_RIGHT)
end

function pcr01_skin_grid_release()

	if Pcr01_nav_thread ~= -1 then
		thread_kill(Pcr01_nav_thread)
		Pcr01_nav_thread = -1
	end

	if Pcr01_original_values.skin_color ~= nil then
		pcr_change_skin_color(Pcr01_original_values.skin_color)
		Pcr01_original_values.skin_color = nil
	end

	menu_grid_release(Pcr01_global_skin_menu[0])
end

----------------------
-- START EYE COLOR --
----------------------
function pcr01_eye_grid_show(menu_data)
	local menu_item = menu_data[0]

	Pcr01_original_values.eye_color = nil
	menu_item.swatches = { num_swatches = 0 }
	pcr_report_eye_colors("pcr01_add_eye_color")

	pcr01_load_swatch_peg("ui_pcr_eyes")

	menu_grid_show(menu_data, menu_item, vint_object_find("swatch_eye"))
	pcr01_camera_eyes_pos()
end

function pcr01_add_eye_color(id, swatch_crc, label_crc, label_str, current)
	local swatches = Pcr01_global_eye_menu[0].swatches
	swatches[swatches.num_swatches] = {
		id = id, swatch_crc = swatch_crc, label_crc = label_crc, label_str = label_str
	}

	if current == true then
		Pcr01_original_values.eye_color = id
		Pcr01_global_eye_menu[0].cur_idx = swatches.num_swatches
	end

	swatches.num_swatches = swatches.num_swatches + 1
end

function pcr01_delayed_set_eye_color()
	delay(0.8)

	if Pcr01_nav_value > -1 then
		pcr_change_eye_color(Pcr01_nav_value)
		Pcr01_nav_value = -1
	end

	Pcr01_nav_thread = -1
end

function pcr01_nav_eye_color(menu_option, menu_data)
	if Pcr01_nav_thread ~= -1 then
		thread_kill(Pcr01_nav_thread)
		Pcr01_nav_thread = -1
	end

	local swatches = menu_data.swatches
	local idx = menu_data.cur_row * menu_data.num_cols + menu_data.cur_col

	if idx < swatches.num_swatches then
		Pcr01_nav_value = swatches[idx].id
		Pcr01_nav_thread = thread_new("pcr01_delayed_set_eye_color")
	end
end

function pcr01_select_eye_color(menu_option, menu_data)
	local swatches = menu_data.swatches
	local idx = menu_data.cur_row * menu_data.num_cols + menu_data.cur_col

	if idx < swatches.num_swatches then
		pcr_change_eye_color(swatches[idx].id)
		pcr_mark_changed()
		Pcr01_player_tweaked = 2
	end

	menu_show(Pcr01_fine_tuning_menu, MENU_TRANSITION_SWEEP_LEFT)
end

function pcr01_eye_grid_back(menu_option, menu_data)
	if Pcr01_nav_thread > -1 then
		thread_kill(Pcr01_nav_thread)
		Pcr01_nav_thread = -1
	end

	if Pcr01_original_values.eye_color ~= nil then
		pcr_change_eye_color(Pcr01_original_values.eye_color)
		Pcr01_original_values.eye_color = nil
	end

	audio_play(Menu_sound_back)

	menu_show(Menu_active.parent_menu, MENU_TRANSITION_SWEEP_RIGHT)
end

function pcr01_eye_grid_release(menu)
	menu_grid_release(menu[0])
end

-------------------------
-- START RANDOMIZATION --
-------------------------
Pcr01_randomizing_morph_set = -1

function pcr01_randomize_one_morph(id, name_crc, name_str, value, gender)
	pcr_apply_morph_value(Pcr01_randomizing_morph_set, id, rand_float(0.35, 0.65))
	pcr_mark_changed()
end

--function pcr01_randomize_all_morphs(menu_option, menu_data)
function pcr01_randomize_all_morphs(result, action)
	if action ~= DIALOG_ACTION_CLOSE then
		return
	end

	if result == 0 then
		local morph_sets = {"Brow", "Crown", "Forehead", "Eyes", "Nose", "Cheekbones", "Ears", "Chin", "Mouth", "Jaw"}

		for index, morph_set_id in morph_sets do
			Pcr01_randomizing_morph_set = morph_set_id
			pcr_report_avail_morphs(morph_set_id, "pcr01_randomize_one_morph")
		end

		Pcr01_randomizing_morph_set = -1
		Pcr01_player_tweaked = 1
	end
end

function pcr01_randomize_morph_set(result, action)
	if action ~= DIALOG_ACTION_CLOSE then
		return
	end

	if result == 0 then
		local option_index, v
		for i = 0, Menu_active.num_items - 1 do
			v = rand_float(0.35, 0.65)
			Menu_active[i].cur_value = v
			pcr_apply_morph_value(Menu_active.morph_set, Menu_active[i].morph_id, v)

			option_index = i - Menu_active.first_vis_item
			if option_index >= 0 and option_index < Menu_option_labels.max_rows then
				menu_num_slider_update_value(Menu_option_labels[option_index], Menu_active[i])
			end
		end

		pcr_mark_changed()
		Pcr01_player_tweaked = 1
	end
end

function pcr01_camera_body_pos()
	store_set_camera_pos("body")
end

function pcr01_camera_head_pos()
	store_set_camera_pos("head")
end

function pcr01_camera_eyes_pos()
	store_set_camera_pos("eyes")
end

function pcr01_exit_final()
	vint_document_unload(vint_document_find("pcr01"))
	if mp_is_enabled() == true or pcr_about_to_do_intro_sequence() then
		--fade out
		screen_fx_fadeout(0.5)
		--delay(0.5)
	end

	if pcr_is_plastic_surgeon() == false and mp_is_enabled() == false then
		pcr_add_default_clothing()
	end
end

function pcr01_exit_confirm(result, action)
	if action ~= DIALOG_ACTION_CLOSE then
		return
	end

	if result == DIALOG_RESULT_YES then
		pcr_release_camera()
		menu_close(pcr01_exit_final)
	end
end

-- Start without clothing [nclok1405]
function pcr01_exit_naked_final()
	vint_document_unload(vint_document_find("pcr01"))
	if mp_is_enabled() == true or pcr_about_to_do_intro_sequence() then
		--fade out
		screen_fx_fadeout(0.5)
		--delay(0.5)
	end
end

function pcr01_exit_naked_confirm(result, action)
	if action ~= DIALOG_ACTION_CLOSE then
		return
	end

	if result == DIALOG_RESULT_YES then
		pcr_release_camera()
		menu_close(pcr01_exit_naked_final)
	end
end

-- Quit Game [nclok1405]
function pcr01_exit_quit_game_final()
	vint_document_unload(vint_document_find("pcr01"))
	pause_menu_quit_game_internal()
end

function pcr01_exit_quit_game_confirm(result, action)
	if action ~= DIALOG_ACTION_CLOSE then
		return
	end

	if result == DIALOG_RESULT_YES then
		pcr_release_camera()
		menu_close(pcr01_exit_quit_game_final)
	end
end

function pcr01_mp_exit_confirm(result, action)
	if action ~= DIALOG_ACTION_CLOSE then
		return
	end

	if result == 0 then
		pcr_save_to_mp_storage(true)
		pcr01_exit_confirm(DIALOG_RESULT_YES, DIALOG_ACTION_CLOSE)
	end
end

function pcr01_mp_exit_with_revert_confirm(result, action)
	if action ~= DIALOG_ACTION_CLOSE then
		return
	end

	if result == 0 then
		pcr_save_to_mp_storage(true)
		pcr01_exit_confirm(DIALOG_RESULT_YES, DIALOG_ACTION_CLOSE)
	elseif result == 1 then
		pcr_save_to_mp_storage(false)
		pcr01_exit_confirm(DIALOG_RESULT_YES, DIALOG_ACTION_CLOSE)
	end
end

function pcr01_exit(menu_data)
	if mp_is_enabled() == true then
		if pcr_avatar_is_blank() then
			local options = { [0] = "PAUSE_MENU_ACCEPT", [1] = "CONTROL_CANCEL" }
			dialog_box_open( "STORE_EXIT_WARNING_HEADER", "PLAYER_CREATION_SAVE_CHANGES", options, "pcr01_mp_exit_confirm", 0, DIALOG_PRIORITY_ACTION )

		elseif pcr_avatar_changed() then
			local options = { [0] = "PAUSE_MENU_ACCEPT", [1] = "PAUSE_MENU_REVERT", [2] = "CONTROL_CANCEL" }
			dialog_box_open( "STORE_EXIT_WARNING_HEADER", "PLAYER_CREATION_SAVE_CHANGES", options, "pcr01_mp_exit_with_revert_confirm", 0, DIALOG_PRIORITY_ACTION )

		else
			dialog_box_confirmation( "STORE_EXIT_WARNING_HEADER", "CUST_EXIT_WARNING_BODY", "pcr01_exit_confirm", true, true )
		end

	else
		local body
		local heading = "MENU_TITLE_WARNING"

		if pcr_is_plastic_surgeon() == true then
			body = "SURGEON_FINISHED_FULL"
		else
			body = "CUST_EXIT_WARNING_BODY"
		end

		dialog_box_confirmation(heading, body, "pcr01_exit_confirm", true, true)
	end
end

function pcr01_exit_naked(menu_data)
	dialog_box_confirmation("MENU_TITLE_WARNING", "SUI_START_WITHOUT_CLOTHING", "pcr01_exit_naked_confirm", true, true)
end

function pcr01_exit_quit_game(menu_data)
	dialog_box_confirmation("PAUSE_MENU_QUIT_TITLE", "PAUSE_MENU_QUIT_NO_SAVE_CONFIRM_TEXT", "pcr01_exit_quit_game_confirm", true, true)
end

function pcr01_change_identity(menu_label, menu_data)
	pcr_change_identity(menu_data.text_slider_values.cur_value)
end

function pcr01_preset_age_show(menu_data)
	Pcr01_original_values.age_morph = pcr_get_morph_value("global body", "old")
	if Pcr01_original_values.age_morph < PCR01_YOUNG_AGE_THRESHOLD then
		menu_data.highlighted_item = 0
	else
		if Pcr01_original_values.age_morph < PCR01_MIDDLE_AGE_THRESHOLD then
				menu_data.highlighted_item = 1
		else
			menu_data.highlighted_item = 2
		end
	end
end

function pcr01_preset_age_nav(menu_data)
	if Pcr01_nav_thread ~= -1 then
		thread_kill(Pcr01_nav_thread)
	end

	Pcr01_nav_value = menu_data[menu_data.highlighted_item].preset_age
	Pcr01_nav_thread = thread_new("pcr01_preset_age_preview")
end

function pcr01_preset_age_preview()
	delay(1)
	pcr_apply_morph_value("global body", "old", Pcr01_nav_value)
	Pcr01_nav_thread = -1
end

function pcr01_preset_age_back()
	if Pcr01_nav_thread ~= -1 then
		thread_kill(Pcr01_nav_thread)
		Pcr01_nav_thread = -1
	end

	if Pcr01_original_values.age_morph ~= nil then
		pcr_apply_morph_value("global body", "old", Pcr01_original_values.age_morph)
	end
	audio_play(Menu_sound_back)

	menu_show(Pcr01_presets_menu, MENU_TRANSITION_SWEEP_RIGHT)
end

function pcr01_preset_age_select(menu_label, menu_item)
	if Pcr01_nav_thread ~= -1 then
		thread_kill(Pcr01_nav_thread)
		Pcr01_nav_thread = -1
	end

	pcr_apply_morph_value("global body", "old", menu_item.preset_age)
	pcr_mark_changed()
	menu_show(Pcr01_presets_menu, MENU_TRANSITION_SWEEP_LEFT)
end

function fine_tuning_menu_show()
	pcr01_camera_head_pos()
	pcr01_restore_hair_values()
end

-----[ MOVEMENT SUBMENUS ]-----

function pcr01_movement_show(menu_data)
	Pcr01_original_values.anim_id = nil
	Pcr01_original_values.anim_grp = menu_data.anim_group
	Pcr01_building_menu = menu_data
	menu_data.num_items = 0
	menu_data.saved = false
	pcr_report_anims(menu_data.anim_group, "pcr01_movement_add_item")
	if menu_data.num_items == 0 then
		menu_data[0] = { label = "NO_OPTIONS_RIGHT_NOW", type = MENU_ITEM_TYPE_SELECTABLE }
		menu_data.num_items = 1
	else
		if menu_data.highlighted_item == nil then
			menu_data.highlighted_item = 0
		end

		pcr01_movement_nav(menu_data)
	end
end

function prc01_movement_custom_camera(menu_data)

	if menu_data.highlighted_item == PCR01_FACIAL_EXPRESSIONS_INDEX then
		pcr01_camera_head_pos()
	else
		pcr01_camera_body_pos()
	end

end

function prc01_movement_list_show(menu_data)
	prc01_movement_custom_camera(menu_data)
	pcr01_restore_makeup() --when the player uses shoulder buttons to navigate away from the menu, makeup needs to be reset
	--and the only way to do this was putting it in the on_show of adjacent menues
end

function pcr01_movement_add_item(display_name, id, current)
	local i = Pcr01_building_menu.num_items

	Pcr01_building_menu[i] = { label = display_name, type = MENU_ITEM_TYPE_SELECTABLE, on_select = pcr01_movement_select, anim_id = id }

	if current == true then
		Pcr01_original_values.anim_id = id

		Pcr01_building_menu.highlighted_item = i
	end

	i = i + 1
	Pcr01_building_menu.num_items = i
end

function pcr01_movement_nav(menu_data)
	if Pcr01_nav_thread ~= -1 then
		thread_kill(Pcr01_nav_thread)
	end

	Pcr01_nav_value = { grp = menu_data.anim_group, id = menu_data[menu_data.highlighted_item].anim_id }
	Pcr01_nav_thread = thread_new("pcr01_movement_preview")
end

function pcr01_movement_preview()
	pcr_preview_anim(Pcr01_nav_value.grp)
	pcr_set_anim(Pcr01_nav_value.grp, Pcr01_nav_value.id)
	Pcr01_nav_thread = -1
end

function pcr01_movement_select(menu_label, menu_item)
	if Pcr01_nav_thread ~= -1 then
		thread_kill(Pcr01_nav_thread)
		Pcr01_nav_thread = -1
	end
	pcr_set_anim(Pcr01_nav_value.grp, Pcr01_nav_value.id)
	pcr_mark_changed()
	pcr_preview_anim()
	Menu_active.saved = true

	menu_show(Pcr01_movement_menu, MENU_TRANSITION_SWEEP_LEFT)
end

function pcr01_movement_exit(menu_data)
	if Pcr01_nav_thread ~= -1 then
		thread_kill(Pcr01_nav_thread)
		Pcr01_nav_thread = -1
	end

	if menu_data.saved == false and Pcr01_original_values.anim_id ~= nil then
		pcr_set_anim(Pcr01_original_values.anim_grp, Pcr01_original_values.anim_id)
	end

	pcr_preview_anim()
	pcr_stop_anim()
end

function pcr01_movement_back(menu_data)
	pcr01_movement_exit(menu_data)
	audio_play(Menu_sound_back)
	menu_show(Pcr01_movement_menu, MENU_TRANSITION_SWEEP_RIGHT)
end

function pcr01_preset_sex_show(menu_data)
	menu_data.highlighted_item = 0

	for i = 0, menu_data.num_items do
		if menu_data[i].preset_gender == Pcr01_current_preset_gender then
			menu_data.highlighted_item = i
			break
		end
	end
end

function pcr01_preset_race_show(menu_data)
	menu_data.highlighted_item = 0

	for i = 0, menu_data.num_items do
		if menu_data[i].preset_race == Pcr01_current_preset_race then
			menu_data.highlighted_item = i
			break
		end
	end
end

function pcr01_preset_figure_show(menu_data)
	menu_data.highlighted_item = 0

	for i = 0, menu_data.num_items do
		if menu_data[i].preset_figure == Pcr01_current_preset_figure then
			menu_data.highlighted_item = i
			break
		end
	end
end

--------------------[ MENU DATA ]----------------------

--since the text on the B button is variable depending on game mode, it is added dynamically
Pcr01_top_btn_tips = {
	a_button = { label = "CONTROL_SELECT",					enabled = btn_tips_default_a, },
	x_button = { label = "PLAYER_CREATION_RANDOMIZE",	enabled = btn_tips_default_x, },
	right_stick =  	{ label = "CONTROL_ZOOM_AND_ROTATE", 	enabled = true },
}

Pcr01_untop_btn_tips = {
	a_button = { label = "CONTROL_SELECT",					enabled = btn_tips_default_a, },
	x_button = { label = "PLAYER_CREATION_RANDOMIZE",	enabled = btn_tips_default_x, },
	right_stick =  	{ label = "CONTROL_ZOOM_AND_ROTATE", 	enabled = true },
}

Pcr01_mp_preset_btn_tips = {
	a_button = { label = "CONTROL_SELECT", 				enabled = btn_tips_default_a, },
	x_button = { label = "PLAYER_CREATION_IMPORT",		enabled = btn_tips_default_x, },
	b_button = { label = "COMPLETION_EXIT",				enabled = btn_tips_default_b, },
	right_stick =  	{ label = "CONTROL_ZOOM_AND_ROTATE", 	enabled = true },
}

Pcr01_presets_sex_menu = {
	header_label_str = "CUST_MENU_SEX_PRESETS",
	num_items = 2,
	on_exit = pcr01_store_current_makeup, --the male and female presets load makeup so we need to save
	btn_tips = Pcr01_untop_btn_tips,
	on_show = pcr01_preset_sex_show,
	[0] = { label = "PLAYER_CREATION_PRESET_MALE", type = MENU_ITEM_TYPE_SELECTABLE, on_select = pcr01_select_preset, preset_gender = "male" },
	[1] = { label = "PLAYER_CREATION_PRESET_FEMALE", type = MENU_ITEM_TYPE_SELECTABLE, on_select = pcr01_select_preset, preset_gender = "female" },
}

Pcr01_presets_race_menu = {
	header_label_str = "CUST_MENU_RACE_PRESETS",
	num_items = 4,
	btn_tips = Pcr01_untop_btn_tips,
	on_show = pcr01_preset_race_show,
	[0] = { label = "RACE_AFRICAN", type = MENU_ITEM_TYPE_SELECTABLE, on_select = pcr01_select_preset, preset_race = "black" },
	[1] = { label = "RACE_ASIAN", type = MENU_ITEM_TYPE_SELECTABLE, on_select = pcr01_select_preset, preset_race = "asian" },
	[2] = { label = "RACE_CAUCASIAN", type = MENU_ITEM_TYPE_SELECTABLE, on_select = pcr01_select_preset, preset_race = "white" },
	[3] = { label = "RACE_HISPANIC", type = MENU_ITEM_TYPE_SELECTABLE, on_select = pcr01_select_preset, preset_race = "hispanic" },
}

Pcr01_presets_figure_menu = {
	header_label_str = "CUST_MENU_FIGURE_PRESETS",
	num_items = 8,
	btn_tips = Pcr01_untop_btn_tips,
	on_show = pcr01_preset_figure_show,
	[0] = { label = "PLAYER_CREATION_FIGURE_AVERAGE", type = MENU_ITEM_TYPE_SELECTABLE, on_select = pcr01_select_preset, preset_figure = "average" },
	[1] = { label = "PLAYER_CREATION_FIGURE_SLENDER", type = MENU_ITEM_TYPE_SELECTABLE, on_select = pcr01_select_preset, preset_figure = "slender" },
	[2] = { label = "PLAYER_CREATION_FIGURE_OVERWEIGHT", type = MENU_ITEM_TYPE_SELECTABLE, on_select = pcr01_select_preset, preset_figure = "overweight" },
	[3] = { label = "PLAYER_CREATION_FIGURE_ATHLETIC", type = MENU_ITEM_TYPE_SELECTABLE, on_select = pcr01_select_preset, preset_figure = "athletic" },
	[4] = { label = "PLAYER_CREATION_FIGURE_EMACIATED", type = MENU_ITEM_TYPE_SELECTABLE, on_select = pcr01_select_preset, preset_figure = "emaciated" },
	[5] = { label = "PLAYER_CREATION_FIGURE_OBESE", type = MENU_ITEM_TYPE_SELECTABLE, on_select = pcr01_select_preset, preset_figure = "obese" },
	[6] = { label = "PLAYER_CREATION_FIGURE_BODYBUILDER", type = MENU_ITEM_TYPE_SELECTABLE, on_select = pcr01_select_preset, preset_figure = "bodybuilder" },
	[7] = { label = "PLAYER_CREATION_FIGURE_HUGE", type = MENU_ITEM_TYPE_SELECTABLE, on_select = pcr01_select_preset, preset_figure = "huge" },
}

Pcr01_presets_age_menu = {
	header_label_str = "PLAYER_MORPH_OLD_TEXT",
	num_items = 3,
	btn_tips = Pcr01_untop_btn_tips,
	on_show = pcr01_preset_age_show,
	on_nav = pcr01_preset_age_nav,
	on_back = pcr01_preset_age_back,
	[0] = { label = "PLAYER_CREATION_AGE_YOUNG", type = MENU_ITEM_TYPE_SELECTABLE, on_select = pcr01_preset_age_select, preset_age = 0.1 },
	[1] = { label = "PLAYER_CREATION_AGE_MIDDLE", type = MENU_ITEM_TYPE_SELECTABLE, on_select = pcr01_preset_age_select, preset_age = 0.5 },
	[2] = { label = "PLAYER_CREATION_AGE_OLD", type = MENU_ITEM_TYPE_SELECTABLE, on_select = pcr01_preset_age_select, preset_age = 0.8 },
}

Pcr01_presets_voice_menu = {
	header_label_str = "CUST_VOICE",
	num_items = 6,
	btn_tips = Pcr01_untop_btn_tips,
	on_show = pcr01_voice_menu_show,
	on_nav = pcr01_nav_voice,
	--on_alt_select = pcr01_highlight_random_item,
	[0] = { label = "CUST_VOICE_MALE_WHITE", type = MENU_ITEM_TYPE_SELECTABLE, on_select = pcr01_set_voice, voice = "MALE_WHITE" },
	[1] = { label = "CUST_VOICE_MALE_BLACK", type = MENU_ITEM_TYPE_SELECTABLE, on_select = pcr01_set_voice, voice = "MALE_BLACK" },
	[2] = { label = "CUST_VOICE_MALE_LATINO", type = MENU_ITEM_TYPE_SELECTABLE, on_select = pcr01_set_voice, voice = "MALE_LATINO" },
	[3] = { label = "CUST_VOICE_FEMALE_WHITE", type = MENU_ITEM_TYPE_SELECTABLE, on_select = pcr01_set_voice, voice = "FEMALE_WHITE" },
	[4] = { label = "CUST_VOICE_FEMALE_BLACK", type = MENU_ITEM_TYPE_SELECTABLE, on_select = pcr01_set_voice, voice = "FEMALE_BLACK" },
	[5] = { label = "CUST_VOICE_FEMALE_LATINO", type = MENU_ITEM_TYPE_SELECTABLE, on_select = pcr01_set_voice, voice = "FEMALE_LATINO" },
}

Pcr01_presets_menu = {
	header_label_str = "CUST_MENU_PRESETS",
	num_items = 4,
	btn_tips = Pcr01_top_btn_tips,
	on_back = pcr01_exit,
	on_show = pcr01_preset_menu_show,
	[0] = { label = "CUST_PRESET_SEX", type = MENU_ITEM_TYPE_SELECTABLE, on_select = pcr01_enter_preset, sub_menu = Pcr01_presets_sex_menu },
	[1] = { label = "CUST_PRESET_RACE", type = MENU_ITEM_TYPE_SELECTABLE, on_select = pcr01_enter_preset, sub_menu = Pcr01_presets_race_menu },
	[2] = { label = "CUST_PRESET_FIGURE", type = MENU_ITEM_TYPE_SELECTABLE, on_select = pcr01_enter_preset, sub_menu = Pcr01_presets_figure_menu },
	[3] = { label = "CUST_PRESET_AGE", type = MENU_ITEM_TYPE_SUB_MENU, sub_menu = Pcr01_presets_age_menu },

}

Pcr01_global_skin_menu = {
	header_label_str = "CUST_SKIN",
	btn_tips = Pcr01_untop_btn_tips,
	on_show = pcr01_skin_grid_show,
	on_release = pcr01_skin_grid_release,
	on_back = pcr01_skin_grid_back,
	--on_alt_select = pcr01_randomize_confirm,
	rand_func = pcr01_highlight_random_swatch,
	rand_func_name = "pcr01_highlight_random_swatch",
	footer_height = nil,
	num_items = 1,
	[0] = { label = "", type = MENU_ITEM_TYPE_GRID, on_select = pcr01_select_skin_color, on_nav = pcr01_nav_skin_color,
		row_height = MENU_SWATCH_DEFAULT_ROW_HEIGHT, num_cols = 6, col_width = MENU_SWATCH_DEFAULT_COL_WIDTH, highlight_scale = 1, unhighlight_scale = 0.8},
}

Pcr01_global_eye_menu = {
	header_label_str = "CUST_EYE_COLOR",
	btn_tips = Pcr01_untop_btn_tips,
	on_show = pcr01_eye_grid_show,
	on_release = pcr01_eye_grid_release,
	on_back = pcr01_eye_grid_back,
	on_alt_select = pcr01_randomize_confirm,
	rand_func = pcr01_highlight_random_swatch,
	rand_func_name = "pcr01_highlight_random_swatch",
	footer_height = nil,
	num_items = 1,
	[0] = { label = "", type = MENU_ITEM_TYPE_GRID, on_select = pcr01_select_eye_color, on_nav = pcr01_nav_eye_color,
		row_height = 72, num_cols = 4, col_width = 83, highlight_scale = 1, unhighlight_scale = 0.8},
}

Pcr01_identity_values = {
	num_values = 2,
	btn_tips = Pcr01_untop_btn_tips,
	[0] = { label = "Male", value = 0 },
	[1] = { label = "Female", value = 1 },
}

Pcr01_globals_menu = {
	header_label_str = "CUST_MENU_GLOBAL",
	num_items = 5,
	btn_tips = Pcr01_top_btn_tips,
	on_back = pcr01_exit,
	on_show = pcr01_globals_show,
	[0] = { label = "PLAYER_GENDER_TEXT", type = MENU_ITEM_TYPE_NUM_SLIDER, morph_id = "body gender", morph_set = "global gender",
		is_gender = true, thumb_width = 55, on_value_update = pcr01_change_morph },
	[1] = { label = "PLAYER_MORPH_MUSCLE_TEXT", type = MENU_ITEM_TYPE_NUM_SLIDER, morph_id = "body muscle", morph_set = "Global Body",
		thumb_width = 55, on_value_update = pcr01_change_morph },
	[2] = { label = "PLAYER_MORPH_BODY_FAT_TEXT", type = MENU_ITEM_TYPE_NUM_SLIDER, morph_id = "body fat", morph_set = "Global Body",
		thumb_width = 55, on_value_update = pcr01_change_morph },
	[3] = { label = "CUST_PRESET_AGE", type = MENU_ITEM_TYPE_NUM_SLIDER, morph_id = "old", morph_set = "Global Body",
		thumb_width = 55, on_value_update = pcr01_change_morph },
	[4] = { label = "CUST_SKIN",	type = MENU_ITEM_TYPE_SUB_MENU, sub_menu = Pcr01_global_skin_menu},
}

Pcr01_hair_primary_color_menu = {
	header_label_str = "CUST_PRIMARY_COLOR",
	btn_tips = Pcr01_untop_btn_tips,
	on_show = pcr01_hair_color_grid_show,
	on_release = pcr01_hair_color_grid_release,
	on_back = pcr01_hair_color_grid_back,
	on_alt_select = pcr01_hair_randomize_primary_color,
	num_items = 1,
	is_primary = true,
	[0] = { label = "", type = MENU_ITEM_TYPE_GRID, on_select = pcr01_hair_color_select, on_nav = pcr01_hair_color_nav,
		row_height = 72, num_cols = 5, col_width = 83, highlight_scale = 1, unhighlight_scale = 0.8,
		update_swatch = pcr01_hair_color_update_swatch
	},
}

Pcr01_hair_secondary_color_menu = {
	header_label_str = "CUST_SECONDARY_COLOR",
	btn_tips = Pcr01_untop_btn_tips,
	on_show = pcr01_hair_color_grid_show,
	on_release = pcr01_hair_color_grid_release,
	on_back = pcr01_hair_color_grid_back,
	on_alt_select = pcr01_hair_randomize_secondary_color,
	num_items = 1,
	is_primary = false,
	[0] = { label = "", type = MENU_ITEM_TYPE_GRID, on_select = pcr01_hair_color_select, on_nav = pcr01_hair_color_nav,
		row_height = 72, num_cols = 5, col_width = 83, highlight_scale = 1, unhighlight_scale = 0.8,
		update_swatch = pcr01_hair_color_update_swatch
	}
}

Pcr01_hair_style_menu = {
	header_label_str = "CUST_MENU_HAIR",
	max_height = 503,	-- Default: 375 [nclok1405]
	num_items = 0,
	btn_tips = Pcr01_untop_btn_tips,
	on_show = pcr01_hair_style_show,
	on_nav = pcr01_hair_style_nav,
	on_back = pcr01_hair_style_back,
	on_alt_select = pcr01_hair_randomize_area,
}

Pcr01_hair_areas_menu = {
	header_label_str = "CUST_CAT_HAIR",
	num_items = 8,
	btn_tips = Pcr01_top_btn_tips,
	on_show = pcr01_hair_areas_show,
	on_back = pcr01_exit,
	on_alt_select = pcr01_randomize_confirm,
	rand_func = pcr01_hair_randomize_all_areas,
	rand_func_name = "pcr01_hair_randomize_all_areas",
	[0] = { label = "CUST_CAT_HAIR_COLOR_PRIMARY", type = MENU_ITEM_TYPE_SUB_MENU, on_select = pcr01_hair_color_category_select, hair_area = PCR01_HAIR_AREA_HEAD },
	[1] = { label = "CUST_CAT_HAIR_COLOR_SECONDARY", type = MENU_ITEM_TYPE_SUB_MENU, on_select = pcr01_hair_color_category_select, hair_area = PCR01_HAIR_AREA_HEAD, is_primary = false },
	[2] = { label = "CUST_CAT_HAIR_COLOR_FACE", type = MENU_ITEM_TYPE_SUB_MENU, on_select = pcr01_hair_color_category_select, hair_area = PCR01_HAIR_AREA_BEARD },
	[3] = { label = "CUST_CAT_HAIR_HEAD", type = MENU_ITEM_TYPE_SUB_MENU, sub_menu = Pcr01_hair_style_menu, hair_area = 0, header_label_str = "CUST_CAT_HAIR_HEAD" },
	[4] = { label = "CUST_CAT_HAIR_MUSTACHE", type = MENU_ITEM_TYPE_SUB_MENU, sub_menu = Pcr01_hair_style_menu, hair_area = 1, header_label_str = "CUST_CAT_HAIR_MUSTACHE" },
	[5] = { label = "CUST_CAT_HAIR_BEARD", type = MENU_ITEM_TYPE_SUB_MENU, sub_menu = Pcr01_hair_style_menu, hair_area = 2, header_label_str = "CUST_CAT_HAIR_BEARD" },
	[6] = { label = "CUST_CAT_HAIR_SIDEBURNS", type = MENU_ITEM_TYPE_SUB_MENU, sub_menu = Pcr01_hair_style_menu, hair_area = 3, header_label_str = "CUST_CAT_HAIR_SIDEBURNS" },
	[7] = { label = "CUST_CAT_HAIR_EYEBROWS", type = MENU_ITEM_TYPE_SUB_MENU, sub_menu = Pcr01_hair_style_menu, hair_area = 4, header_label_str = "CUST_CAT_HAIR_EYEBROWS" },
}

Pcr01_tuning_crown_menu = {
	header_label_str = "CUST_MORPH_CAT_CROWN",
	max_height = 503,	-- Default: 375 [nclok1405]
	num_items = 0,
	morph_set = "crown",
	btn_tips = Pcr01_untop_btn_tips,
	on_show = pcr01_build_morph_menu,
	on_select = pcr01_morph_set_accept,
	on_back = pcr01_morph_set_revert,
	on_alt_select = pcr01_randomize_confirm,
	rand_func = pcr01_randomize_morph_set,
	rand_func_name = "pcr01_randomize_morph_set",
}

Pcr01_tuning_forehead_menu = {
	header_label_str = "CUST_MORPH_CAT_FOREHEAD",
	max_height = 503,	-- Default: 375 [nclok1405]
	num_items = 0,
	morph_set = "forehead",
	btn_tips = Pcr01_untop_btn_tips,
	on_show = pcr01_build_morph_menu,
	on_select = pcr01_morph_set_accept,
	on_back = pcr01_morph_set_revert,
	on_alt_select = pcr01_randomize_confirm,
	rand_func = pcr01_randomize_morph_set,
	rand_func_name = "pcr01_randomize_morph_set",
}

Pcr01_tuning_brow_menu = {
	header_label_str = "CUST_MORPH_CAT_BROW",
	max_height = 503,	-- Default: 375 [nclok1405]
	num_items = 0,
	morph_set = "brow",
	btn_tips = Pcr01_untop_btn_tips,
	on_show = pcr01_build_morph_menu,
	on_select = pcr01_morph_set_accept,
	on_back = pcr01_morph_set_revert,
	on_alt_select = pcr01_randomize_confirm,
	rand_func = pcr01_randomize_morph_set,
	rand_func_name = "pcr01_randomize_morph_set",
}

Pcr01_tuning_eyes_menu = {
	header_label_str = "CUST_MORPH_CAT_EYES",
	max_height = 503,	-- Default: 375 [nclok1405]
	num_items = 0,
	morph_set = "eyes",
	btn_tips = Pcr01_untop_btn_tips,
	on_show = pcr01_build_morph_menu,
	on_select = pcr01_morph_set_accept,
	on_back = pcr01_morph_set_revert,
	on_alt_select = pcr01_randomize_confirm,
	rand_func = pcr01_randomize_morph_set,
	rand_func_name = "pcr01_randomize_morph_set",
}

Pcr01_tuning_nose_menu = {
	header_label_str = "CUST_MORPH_CAT_NOSE",
	max_height = 503,	-- Default: 375 [nclok1405]
	num_items = 0,
	morph_set = "nose",
	btn_tips = Pcr01_untop_btn_tips,
	on_show = pcr01_build_morph_menu,
	on_select = pcr01_morph_set_accept,
	on_back = pcr01_morph_set_revert,
	on_alt_select = pcr01_randomize_confirm,
	rand_func = pcr01_randomize_morph_set,
	rand_func_name = "pcr01_randomize_morph_set",
}

Pcr01_tuning_cheekbones_menu = {
	header_label_str = "CUST_MORPH_CAT_CHEEKBONES",
	max_height = 503,	-- Default: 375 [nclok1405]
	num_items = 0,
	morph_set = "cheekbones",
	btn_tips = Pcr01_untop_btn_tips,
	on_show = pcr01_build_morph_menu,
	on_select = pcr01_morph_set_accept,
	on_back = pcr01_morph_set_revert,
	on_alt_select = pcr01_randomize_confirm,
	rand_func = pcr01_randomize_morph_set,
	rand_func_name = "pcr01_randomize_morph_set",
}

Pcr01_tuning_ears_menu = {
	header_label_str = "CUST_MORPH_CAT_EARS",
	max_height = 503,	-- Default: 375 [nclok1405]
	num_items = 0,
	morph_set = "ears",
	btn_tips = Pcr01_untop_btn_tips,
	on_show = pcr01_build_morph_menu,
	on_select = pcr01_morph_set_accept,
	on_back = pcr01_morph_set_revert,
	on_alt_select = pcr01_randomize_confirm,
	rand_func = pcr01_randomize_morph_set,
	rand_func_name = "pcr01_randomize_morph_set",
}

Pcr01_tuning_chin_menu = {
	header_label_str = "CUST_MORPH_CAT_CHIN",
	max_height = 503,	-- Default: 375 [nclok1405]
	num_items = 0,
	morph_set = "chin",
	btn_tips = Pcr01_untop_btn_tips,
	on_show = pcr01_build_morph_menu,
	on_select = pcr01_morph_set_accept,
	on_back = pcr01_morph_set_revert,
	on_alt_select = pcr01_randomize_confirm,
	rand_func = pcr01_randomize_morph_set,
	rand_func_name = "pcr01_randomize_morph_set",
}

Pcr01_tuning_mouth_menu = {
	header_label_str = "CUST_MORPH_CAT_MOUTH",
	max_height = 503,	-- Default: 375 [nclok1405]
	num_items = 0,
	morph_set = "mouth",
	btn_tips = Pcr01_untop_btn_tips,
	on_show = pcr01_build_morph_menu,
	on_select = pcr01_morph_set_accept,
	on_back = pcr01_morph_set_revert,
	on_alt_select = pcr01_randomize_confirm,
	rand_func = pcr01_randomize_morph_set,
	rand_func_name = "pcr01_randomize_morph_set",
}

Pcr01_tuning_jaw_menu = {
	header_label_str = "CUST_MORPH_CAT_JAW",
	max_height = 503,	-- Default: 375 [nclok1405]
	num_items = 0,
	morph_set = "jaw",
	btn_tips = Pcr01_untop_btn_tips,
	on_show = pcr01_build_morph_menu,
	on_select = pcr01_morph_set_accept,
	on_back = pcr01_morph_set_revert,
	on_alt_select = pcr01_randomize_confirm,
	rand_func = pcr01_randomize_morph_set,
	rand_func_name = "pcr01_randomize_morph_set",
}

Pcr01_fine_tuning_menu = {
	header_label_str = "CUST_FINE_TUNING",
	max_height = 503,	-- Default: 375 [nclok1405]
	num_items = 10,
	btn_tips = Pcr01_top_btn_tips,
	on_back = pcr01_exit,
	on_alt_select = pcr01_randomize_confirm,
	rand_func = pcr01_randomize_all_morphs,
	rand_func_name = "pcr01_randomize_all_morphs",
	on_show = fine_tuning_menu_show,
	[0] = { label = "cust_morph_cat_crown", type = MENU_ITEM_TYPE_SUB_MENU, sub_menu = Pcr01_tuning_crown_menu },
	[1] = { label = "cust_morph_cat_forehead", type = MENU_ITEM_TYPE_SUB_MENU, sub_menu = Pcr01_tuning_forehead_menu },
	[2] = { label = "cust_morph_cat_brow", type = MENU_ITEM_TYPE_SUB_MENU, sub_menu = Pcr01_tuning_brow_menu },
	[3] = { label = "cust_morph_cat_eyes", type = MENU_ITEM_TYPE_SUB_MENU, sub_menu = Pcr01_tuning_eyes_menu },
	[4] = { label = "cust_morph_cat_ears", type = MENU_ITEM_TYPE_SUB_MENU, sub_menu = Pcr01_tuning_ears_menu },
	[5] = { label = "cust_morph_cat_cheekbones", type = MENU_ITEM_TYPE_SUB_MENU, sub_menu = Pcr01_tuning_cheekbones_menu },
	[6] = { label = "cust_morph_cat_nose", type = MENU_ITEM_TYPE_SUB_MENU, sub_menu = Pcr01_tuning_nose_menu },
	[7] = { label = "cust_morph_cat_mouth", type = MENU_ITEM_TYPE_SUB_MENU, sub_menu = Pcr01_tuning_mouth_menu },
	[8] = { label = "cust_morph_cat_chin", type = MENU_ITEM_TYPE_SUB_MENU, sub_menu = Pcr01_tuning_chin_menu },
	[9] = { label = "cust_morph_cat_jaw", type = MENU_ITEM_TYPE_SUB_MENU, sub_menu = Pcr01_tuning_jaw_menu },
	--[10] = { label = "STORE_NOT_AVAILABLE",			type = MENU_ITEM_TYPE_SUB_MENU, sub_menu = Pcr01_global_eye_menu },
	-- Removed eye color menu [nclok1405]
}

Pcr01_makeup_secondary_color_menu = {
	header_label_str = "CUST_SECONDARY_COLOR",
	btn_tips = Pcr01_untop_btn_tips,
	on_show = pcr01_makeup_color_grid_show,
	on_release = pcr01_makeup_color_grid_release,
	on_back = pcr01_makeup_color_grid_back,
	on_alt_select = pcr01_randomize_confirm,
	rand_func = pcr01_makeup_randomize_secondary_color,
	rand_func_name = "pcr01_makeup_randomize_secondary_color",
	num_items = 1,
	is_primary = false,
	[0] = { label = "", type = MENU_ITEM_TYPE_GRID, on_select = pcr01_select_makeup_color, on_nav = pcr01_nav_makeup_color,
		row_height = 41, num_cols = 6, col_width = 65, highlight_scale = 1, unhighlight_scale = 0.8,
		update_swatch = pcr01_makeup_color_update_swatch
	}
}

Pcr01_makeup_primary_color_menu = {
	header_label_str = "CUST_PRIMARY_COLOR",
	btn_tips = Pcr01_untop_btn_tips,
	on_show = pcr01_makeup_color_grid_show,
	on_release = pcr01_makeup_color_grid_release,
	on_back = pcr01_makeup_color_grid_back,
	on_alt_select = pcr01_randomize_confirm,
	rand_func = pcr01_makeup_randomize_primary_color,
	rand_func_name = "pcr01_makeup_randomize_primary_color",
	num_items = 1,
	is_primary = true,
	[0] = { label = "", type = MENU_ITEM_TYPE_GRID, on_select = pcr01_select_makeup_color, on_nav = pcr01_nav_makeup_color,
		row_height = 41, num_cols = 6, col_width = 65, highlight_scale = 1, unhighlight_scale = 0.8,
		update_swatch = pcr01_makeup_color_update_swatch
	}
}

Pcr01_makeup_variations_menu = {
	header_label_str = "CUST_MAKEUP_VARIATION",
	max_height = 503,	-- Default: 375 [nclok1405]
	num_items = 0,
	btn_tips = Pcr01_untop_btn_tips,
	on_back = pcr01_makeup_variant_back,
	on_nav = pcr01_makeup_item_nav,
	on_show = prc01_makeup_variant_show,
	on_alt_select = pcr01_randomize_confirm,
	rand_func = pcr01_makeup_randomize_variant,
	rand_func_name = "pcr01_makeup_randomize_variant",
}

Pcr01_makeup_forehead = {
	header_label_str = "CUST_CAT_MAKEUP_FOREHEAD",
	max_height = 503,	-- Default: 375 [nclok1405]
	num_items = 0,
	btn_tips = Pcr01_untop_btn_tips,
	on_show = pcr01_build_makeup_menu,
	on_back = pcr01_makeup_item_back,
	on_nav = pcr01_makeup_item_nav,
	on_alt_select = pcr01_randomize_confirm,
	rand_func = pcr01_makeup_randomize_area,
	rand_func_name = "pcr01_makeup_randomize_area",
}

Pcr01_makeup_cheeks = {
	header_label_str = "CUST_CAT_MAKEUP_CHEEKS",
	max_height = 503,	-- Default: 375 [nclok1405]
	num_items = 0,
	btn_tips = Pcr01_untop_btn_tips,
	on_show = pcr01_build_makeup_menu,
	on_back = pcr01_makeup_item_back,
	on_nav = pcr01_makeup_item_nav,
	on_alt_select = pcr01_randomize_confirm,
	rand_func = pcr01_makeup_randomize_area,
	rand_func_name = "pcr01_makeup_randomize_area",
}

Pcr01_makeup_mouth = {
	header_label_str = "CUST_CAT_MAKEUP_MOUTH",
	max_height = 503,	-- Default: 375 [nclok1405]
	num_items = 0,
	btn_tips = Pcr01_untop_btn_tips,
	on_show = pcr01_build_makeup_menu,
	on_back = pcr01_makeup_item_back,
	on_nav = pcr01_makeup_item_nav,
	on_alt_select = pcr01_randomize_confirm,
	rand_func = pcr01_makeup_randomize_area,
	rand_func_name = "pcr01_makeup_randomize_area",
}

Pcr01_makeup_face = {
	header_label_str = "CUST_CAT_MAKEUP_ENTIRE_FACE",
	max_height = 503,	-- Default: 375 [nclok1405]
	num_items = 0,
	btn_tips = Pcr01_untop_btn_tips,
	on_show = pcr01_build_makeup_menu,
	on_back = pcr01_makeup_item_back,
	on_nav = pcr01_makeup_item_nav,
	on_alt_select = pcr01_randomize_confirm,
	rand_func = pcr01_makeup_randomize_area,
	rand_func_name = "pcr01_makeup_randomize_area",
}

Pcr01_makeup_eyes = {
	header_label_str = "CUST_CAT_MAKEUP_AROUND_EYES",
	max_height = 503,	-- Default: 375 [nclok1405]
	num_items = 0,
	btn_tips = Pcr01_untop_btn_tips,
	on_show = pcr01_build_makeup_menu,
	on_back = pcr01_makeup_item_back,
	on_nav = pcr01_makeup_item_nav,
	on_alt_select = pcr01_randomize_confirm,
	rand_func = pcr01_makeup_randomize_area,
	rand_func_name = "pcr01_makeup_randomize_area",
}

Pcr01_makeup_areas_menu = {
	header_label_str = "CUST_MENU_MAKEUP",
	num_items = 4,
	btn_tips = Pcr01_top_btn_tips,
	on_show = pcr01_makeup_area_list_show,
	on_back = pcr01_exit,
	on_alt_select = pcr01_randomize_confirm,
	rand_func = pcr01_makeup_randomize_all_areas,
	rand_func_name = "pcr01_makeup_randomize_all_areas",
	[0] = { label = "CUST_CAT_MAKEUP_AROUND_EYES", type = MENU_ITEM_TYPE_SUB_MENU, sub_menu = Pcr01_makeup_eyes, makeup_area = 4 },
	[1] = { label = "CUST_CAT_MAKEUP_CHEEKS", type = MENU_ITEM_TYPE_SUB_MENU, sub_menu = Pcr01_makeup_cheeks, makeup_area = 1 },
	[2] = { label = "CUST_CAT_MAKEUP_MOUTH", type = MENU_ITEM_TYPE_SUB_MENU, sub_menu = Pcr01_makeup_mouth, makeup_area = 2 },
	[3] = { label = "CUST_CAT_MAKEUP_ENTIRE_FACE", type = MENU_ITEM_TYPE_SUB_MENU, sub_menu = Pcr01_makeup_face, makeup_area = 3 },
}

Pcr01_movement_walk_menu = {
	header_label_str = "CUST_MOVEMENT_WALK",
	max_height = 503,	-- Default: 375 [nclok1405]
	num_items = 0,
	btn_tips = Pcr01_untop_btn_tips,
	on_show = pcr01_movement_show,
	on_nav = pcr01_movement_nav,
	on_back = pcr01_movement_back,
	on_exit = pcr01_movement_exit,
	anim_group = "walk_style"
}

Pcr01_movement_melee_menu = {
	header_label_str = "CUST_MOVEMENT_MELEE",
	num_items = 0,
	btn_tips = Pcr01_untop_btn_tips,
	on_show = pcr01_movement_show,
	on_nav = pcr01_movement_nav,
	on_back = pcr01_movement_back,
	on_exit = pcr01_movement_exit,
	anim_group = "melee_combat_style"
}

Pcr01_movement_taunt_menu = {
	header_label_str = "CUST_MOVEMENT_TAUNT",
	max_height = 503,	-- Default: 375 [nclok1405]
	num_items = 0,
	btn_tips = Pcr01_untop_btn_tips,
	on_show = pcr01_movement_show,
	on_nav = pcr01_movement_nav,
	on_back = pcr01_movement_back,
	on_exit = pcr01_movement_exit,
	anim_group = "taunt_style"
}

Pcr01_movement_compliment_menu = {
	header_label_str = "CUST_MOVEMENT_COMPLIMENT",
	max_height = 503,	-- Default: 375 [nclok1405]
	num_items = 0,
	btn_tips = Pcr01_untop_btn_tips,
	on_show = pcr01_movement_show,
	on_nav = pcr01_movement_nav,
	on_back = pcr01_movement_back,
	on_exit = pcr01_movement_exit,
	anim_group = "compliment_style"
}

Pcr01_movement_facial_expression_menu = {
	header_label_str = "CUST_MOVEMENT_FACE",
	max_height = 503,	-- Default: 375 [nclok1405]
	num_items = 0,
	btn_tips = Pcr01_untop_btn_tips,
	on_show = pcr01_movement_show,
	on_nav = pcr01_movement_nav,
	on_back = pcr01_movement_back,
	on_exit = pcr01_movement_exit,
	anim_group = "facial_expression_style"
}

Pcr01_movement_menu = {
	header_label_str = "CUST_MENU_MOVEMENT",
	num_items = 6,
	on_show = prc01_movement_list_show,
	on_back = pcr01_exit,
	on_nav = prc01_movement_custom_camera,
	btn_tips = Pcr01_top_btn_tips,
	[0] = { label = "CUST_VOICE", type = MENU_ITEM_TYPE_SUB_MENU, sub_menu = Pcr01_presets_voice_menu },
	[1] = { label = "CUST_MOVEMENT_FACIAL_EXPRESSION", type = MENU_ITEM_TYPE_SUB_MENU, sub_menu = Pcr01_movement_facial_expression_menu},
	[2] = { label = "CUST_MOVEMENT_WALK", type = MENU_ITEM_TYPE_SUB_MENU, sub_menu = Pcr01_movement_walk_menu },
	[3] = { label = "CUST_MOVEMENT_COMPLIMENT", type = MENU_ITEM_TYPE_SUB_MENU, sub_menu = Pcr01_movement_compliment_menu },
	[4] = { label = "CUST_MOVEMENT_TAUNT", type = MENU_ITEM_TYPE_SUB_MENU, sub_menu = Pcr01_movement_taunt_menu },
	[5] = { label = "CUST_MOVEMENT_MELEE", type = MENU_ITEM_TYPE_SUB_MENU, sub_menu = Pcr01_movement_melee_menu },
}

function pcr01_do_nothing()

end

-- "Start Game" for initial player creation
Pcr01_exit_menu = {
	header_label_str = "CUST_MENU_EXIT",
	num_items = 3,
	btn_tips = Pcr01_top_btn_tips,
	on_back = pcr01_exit,
	[0] = { label = "CUST_MENU_EXIT", type = MENU_ITEM_TYPE_SELECTABLE, on_select = pcr01_exit },
	[1] = { label = "Start Without Clothing", type = MENU_ITEM_TYPE_SELECTABLE, on_select = pcr01_exit_naked },
	[2] = { label = "PCS_RETURN_MAIN", type = MENU_ITEM_TYPE_SELECTABLE, on_select = pcr01_exit_quit_game }
}

Pcr01_horz_menu = {
	num_items = 7,
	btn_tips = Pcr01_top_btn_tips,
	current_selection = 0,
	[0] = { label = "CUST_MENU_PRESETS", sub_menu = Pcr01_presets_menu },
	[1] = { label = "CUST_MENU_GLOBAL", sub_menu = Pcr01_globals_menu },
	[2] = { label = "CUST_MENU_FINE_TUNING", sub_menu = Pcr01_fine_tuning_menu },
	[3] = { label = "CUST_MENU_HAIR", sub_menu = Pcr01_hair_areas_menu },
	[4] = { label = "CUST_MENU_MAKEUP", sub_menu = Pcr01_makeup_areas_menu },
	[5] = { label = "CUST_MENU_MOVEMENT", sub_menu = Pcr01_movement_menu },
	[6] = { label = "CUST_MENU_EXIT", sub_menu = Pcr01_exit_menu }
}
