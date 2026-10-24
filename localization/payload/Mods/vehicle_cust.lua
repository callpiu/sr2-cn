-- vehicle_cust.lua: Vehicle Customization

---------------------------
-- VEHICLE CUSTOMIZATION --
---------------------------
-- "global" variables
Vehicle_cust_menu			 		= { }
Vehicle_cust_footer 				= { }

Vehicle_cust_title_to_use		  	= ""
Vehicle_cust_menu_type			  	= 0

Vehicle_cust_show_slot			  	= -1
Vehicle_cust_color_slot			  	= -1
Vehicle_cust_show_region			= false

Vehicle_cust_style_to_award			= 0
Vehicle_cust_category_selected  	= 0
Vehicle_cust_palette_choice	  		= 0
Vehicle_cust_rim_family			 	= 0
Vehicle_cust_rim_index				= 0
Vehicle_cust_component_selected		= -1
Vehicle_cust_chosen_axle			= 0
Vehicle_cust_current_peg	  		= ""
Vehicle_cust_rebuild_wheel_menu		= true

Vehicle_cust_color_menu				= { }

Vehicle_cust_wheel_price			= 0
Vehicle_cust_rim_price				= 0
Vehicle_cust_tire_price				= 0
Vehicle_cust_hubcap_price			= 0

Vehicle_cust_slider_values 			= { rim_size = -1, wheel_size = -1, wheel_width = -1 }

VEHICLE_CUST_SLIDER_COST			= 100

VEHICLE_CUST_RIM_PEG				= "ui_veh_r_0"
VEHICLE_CUST_TIRE_PEG 				= "ui_veh_tires"
VEHICLE_CUST_HUBCAP_PEG				= "ui_veh_h_01"
VEHICLE_CUST_SPINNER_PEG			= "ui_veh_s_0"

VEHICLE_CUST_DOC_HANDLE 		  	= vint_document_find("vehicle_cust")

VEHICLE_COMPONENT_LINE_CHECK_COLOR 	= {["R"] = 0.27, ["G"] = 0.47, ["B"] = 0.09}
VEHICLE_COMPONENT_LINE				= 2001

Vehicle_just_upgrade				= false
Vehicle_upgrade_sound				= audio_get_audio_id("SYS_VEH_UPGRADE")		-- Any item is purchased

Vehicle_cust_rim_sizes = {
	num_rim_sizes = 5,
	median_rim_size = 2,

	[0] = "VCUST_EXTRA_HIGH_PROFILE",
	[1] = "VCUST_HIGH_PROFILE",
	[2] = "VCUST_NORMAL_PROFILE",
	[3] = "VCUST_LOW_PROFILE",
	[4] = "VCUST_EXTRA_LOW_PROFILE",
}

Vehicle_equipped_perf_upgrade = false		-- true if the currently checking pref upgrade is equipped [nclok1405]
Vehicle_own_perf_upgrade = false			-- true if the perf upgrade is owned [nclok1405]
Vehicle_equipped_normal_perf_part = false	-- true if the normal perf part is equipped [nclok1405]

----------------------
--	SYSTEM FUNCTIONS --
----------------------
--[ INITIALIZE AND SHUTDOWN ]--
-------------------------------
--	Initialize the menu
function vehicle_cust_init()

	--Event Tracking
	event_tracking_interface_enter("Vehicle Customization")

	peg_load("ui_veh_paint")
	peg_load("ui_veh_glass")

	menu_set_custom_control_callbacks(Vehicle_menu_controls)

	if vcust_using_lightset() == true then
		interface_effect_begin("store", 1, 2, true)
	end

	menu_store_init(true)

	vehicle_cust_build_horz_menu()

	menu_init()
	menu_horz_init(Vehicle_cust_horz_menu)

end

-- Shutdown and cleanup the menu
function vehicle_cust_cleanup()
	style_cluster_cleanup()
	peg_unload("ui_veh_paint")
	peg_unload("ui_veh_glass")
	if Vehicle_cust_current_peg ~= "" then
		peg_unload(Vehicle_cust_current_peg)
	end

	if vcust_using_lightset() == true then
		interface_effect_end(2)
	end

end

--[ EXIT ]--
------------
function vehicle_cust_exit(menu_data)
	local body = "VCUST_EXIT_PROMPT"
	local heading = "MENU_TITLE_WARNING"

	--dialog_box_confirmation(heading, body, "vehicle_cust_exit_confirm")
	menu_close(vehicle_cust_exit_final)	-- Exit without dialog [nclok1405]
end

function vehicle_cust_exit_confirm(result, action)
	if action ~= DIALOG_ACTION_CLOSE then
		return
	end

	if result == 0 then
		menu_close(vehicle_cust_exit_final)
	end
end
function vehicle_cust_exit_final()
	vint_document_unload(VEHICLE_CUST_DOC_HANDLE)
end

-------------------
-- CHECKBOX LINE --
-------------------
function vehicle_component_line_on_show(menu_label, menu_data)
	local control = menu_label.control

	if control ~= nil then
		if control.type ~= VEHICLE_COMPONENT_LINE then
			menu_release_control(control)
			control = nil
		end
	end

	if control == nil then
		local control_h = vint_object_clone(vint_object_find("pm_objective_text_line"), Menu_option_labels.control_parent)
		control = { grp_h = control_h, type = VEHICLE_COMPONENT_LINE, is_highlighted = false }
		menu_label.original_anchor = { }
		menu_label.original_anchor.x, menu_label.original_anchor.y  = vint_get_property(vint_object_find("pm_objective_text_line_label"), "anchor")
	end

	menu_label.control = control

	--	Hide the O.G. Label
	vint_set_property(menu_label.label_h, "visible", false)

	--	Show the new control
	vint_set_property(control.grp_h, "visible", true)
	vint_set_property(control.grp_h, "anchor", menu_label.anchor_x, menu_label.anchor_y)
	vint_set_property(control.grp_h, "depth", menu_label.depth)

	--	Set the color and text_tag
	menu_label.real_label_h = vint_object_find("pm_objective_text_line_label", control.grp_h)
	vint_set_property(menu_label.real_label_h, "text_tag", menu_data.label)
	vint_set_property(menu_label.real_label_h, "tint", 0.364, 0.368, 0.376)
	vint_set_property(menu_label.real_label_h, "visible", true)
	menu_label.checkbox_h = vint_object_find("pm_objective_checkbox", control.grp_h)
	menu_label.check_h = vint_object_find("pm_objective_checkmark", control.grp_h)
	vint_set_property(menu_label.checkbox_h, "tint", 0.364, 0.368, 0.376)
	vint_set_property(menu_label.check_h, "tint", VEHICLE_COMPONENT_LINE_CHECK_COLOR.R, VEHICLE_COMPONENT_LINE_CHECK_COLOR.G, VEHICLE_COMPONENT_LINE_CHECK_COLOR.B)

	vint_set_property(menu_label.real_label_h, "anchor", menu_label.original_anchor.x, menu_label.original_anchor.y)
	vint_set_property(menu_label.checkbox_h, "visible", true)
	if menu_data.checked == true then
		vint_set_property(menu_label.real_label_h, "alpha", 0.6)
		vint_set_property(menu_label.checkbox_h, "alpha", 0.6)
		vint_set_property(menu_label.check_h, "visible", true)
		vint_set_property(menu_label.check_h, "alpha", 0.6)

	else
		vint_set_property(menu_label.real_label_h, "alpha", 1.0)
		vint_set_property(menu_label.check_h, "visible", false)
	end
end

function vehicle_update_custom_scrollbar()
	local data_idx  = Menu_active.highlighted_item
	local label_idx = Menu_active.highlighted_item - Menu_active.first_vis_item

	if label_idx  >= Menu_option_labels.max_rows then
		return
	end
	local anchor_x, anchor_y = vint_get_property(Menu_option_labels[label_idx].real_label_h, "anchor")
	local hl_bar_label_h = vint_object_find("menu_sel_bar_label", Menu_option_labels.hl_bar)
	vint_set_property(Menu_option_labels.hl_bar, "anchor", anchor_x + 5, Menu_option_labels[label_idx].anchor_y + 1)

	vint_set_property(hl_bar_label_h, "text_tag", Menu_active[data_idx].label)
	vehicle_component_line_resize_select_bar()
end

function vehicle_component_line_resize_select_bar()
	local width = Menu_active.menu_width - (element_get_actual_size(Menu_option_labels[0].checkbox_h) + 5)
	local bg_h
	local frame_h = Menu_option_labels.frame
	local sel_bar_width = width

	if Menu_option_labels.scroll_bar_visible == true then
		sel_bar_width = sel_bar_width - 40
	end

	--Floor the selection bar width
	sel_bar_width = floor(sel_bar_width)

	bg_h = vint_object_find("menu_sel_bar_w", frame_h)
	vint_set_property(bg_h, "source_se", sel_bar_width, 36)

	bg_h = vint_object_find("menu_sel_bar_w_hl", frame_h)
	vint_set_property(bg_h, "source_se", sel_bar_width, 36)

	bg_h = vint_object_find("menu_sel_bar_e", frame_h)
	local menu_bar_e_anchor_x, menu_bar_e_anchor_y = vint_get_property(bg_h, "anchor")
	menu_bar_e_anchor_x = sel_bar_width + 4
	vint_set_property(bg_h, "anchor", menu_bar_e_anchor_x, menu_bar_e_anchor_y)

	local bg_h = vint_object_find("menu_sel_bar_e_hl", frame_h)
	vint_set_property(bg_h, "anchor", menu_bar_e_anchor_x, menu_bar_e_anchor_y)

	vint_set_property(Menu_option_labels.hl_clip, "offset", 12, -15)
	vint_set_property(Menu_option_labels.hl_clip, "clip_size", width - 17, MENU_ITEM_HEIGHT)
end

function vehicle_component_line_nav_up(menu_label, menu_data)
	local idx = Menu_active.highlighted_item

	if idx - 1 >= 0 then
		Menu_active.highlighted_item = Menu_active.highlighted_item - 1
	else
		Menu_active.highlighted_item = Menu_active.num_items - 1
	end

	audio_play(Menu_sound_item_nav)
	vehicle_update_custom_control()

	if Menu_active.on_nav ~= nil then
		Menu_active.on_nav(Menu_active)
	end
end

function vehicle_component_line_nav_down(menu_label, menu_data)
	local idx = Menu_active.highlighted_item

	if idx + 1 < Menu_active.num_items then
		Menu_active.highlighted_item = Menu_active.highlighted_item + 1
	else
		Menu_active.highlighted_item = 0
	end

	audio_play(Menu_sound_item_nav)
	vehicle_update_custom_control()

	if Menu_active.on_nav ~= nil then
		Menu_active.on_nav(Menu_active)
	end
end

function vehicle_update_custom_control()
	local h, ch, item, label_w, control

	-- check to see if we need to scroll
	local first_vis_item = 0
	local prev_first_vis_item = Menu_active.first_vis_item

	if Menu_active.num_items > Menu_option_labels.max_rows then
		local half_max = floor(Menu_option_labels.max_rows / 2)
		first_vis_item = limit(Menu_active.highlighted_item - half_max, 0, Menu_active.num_items - Menu_option_labels.max_rows)
	end
	Menu_active.first_vis_item = first_vis_item

	local idx = Menu_active
	-- set the labels and hide unused
	for i = 0, Menu_option_labels.max_rows - 1 do
		if Menu_active.first_vis_item < 0 then
			Menu_active.first_vis_item = 0
		end

		item = Menu_active.first_vis_item + i
		if item < Menu_active.num_items then
			local item_type = Menu_active[item].type

			-- update control
			local cb = Menu_control_callbacks[item_type]
			if cb ~= nil then
				if cb.on_show ~= nil then
					cb.on_show(Menu_option_labels[i], Menu_active[item])
				end
			end
		else
			if Menu_option_labels[i].control ~= nil then
				h = Menu_option_labels[i].control.grp_h
				vint_set_property(Menu_option_labels[i].stripe_h, "visible", false)
				vint_set_property(h, "visible", false)
			end
		end
	end

	-- update scroll bar
	if Menu_option_labels.scroll_bar_visible == true then
		menu_scroll_bar_set_thumb_pos(Menu_active.first_vis_item / (Menu_active.num_items - Menu_option_labels.max_rows))
	end

	vehicle_update_custom_scrollbar()
	vehicle_component_line_update_checkbox(Menu_active)
end


function vehicle_component_line_on_release(control)
	if control.grp_h ~= nil then
		vint_object_destroy(control.grp_h)
		control.grp_h = nil
	end
end

function vehicle_component_line_get_width(menu_data)

	local grp_h = vint_object_find("pm_objective_text_line")
	local label_h =  vint_object_find("pm_objective_text_line_label", grp_h)
	local checkbox_h = vint_object_find("pm_objective_checkbox", grp_h)

	vint_set_property(label_h, "text_tag", menu_data.label)

	--Check its width
	local min_width = element_get_actual_size(label_h)
	min_width = min_width + element_get_actual_size(checkbox_h)

	return min_width + 5
end

function vehicle_component_line_get_height(menu_label, menu_data)

end

function vehicle_component_line_update_checkbox(menu_data)
	for i = 0, Menu_option_labels.max_rows - 1 do
		if Menu_active.first_vis_item < 0 then
			Menu_active.first_vis_item = 0
		end

		local item = Menu_active.first_vis_item + i
		if item < Menu_active.num_items then
			if menu_data[item].owned == false then
				vint_set_property(Menu_option_labels[i].checkbox_h, "visible", false)
			else
				vint_set_property(Menu_option_labels[i].checkbox_h, "visible", true)
			end

			if menu_data[item].equipped == true then
				vint_set_property(Menu_option_labels[i].check_h, "visible", true)
			else
				vint_set_property(Menu_option_labels[i].check_h, "visible", false)
			end
		end
	end
end

------------
--	FOOTER --
------------
function vehicle_cust_adjust_footer_positions()
	if Menu_active == 0 then
		return
	end

	if Menu_active.footer_height ~= 0 then
		vint_set_property(Vehicle_cust_footer.label_h, "scale", 1.0, 1.0)
		vint_set_property(Vehicle_cust_footer.price_h, "scale", 1.0, 1.0)
		local text_x, text_y = vint_get_property(Vehicle_cust_footer.label_h, "anchor")
		local text_width, text_height = element_get_actual_size(Vehicle_cust_footer.label_h)
		local price_anchor_x = vint_get_property(Vehicle_cust_footer.price_h, "anchor")
		local price_width, price_height = element_get_actual_size(Vehicle_cust_footer.price_h)


		if price_width > text_width then
			local size_of_text = Menu_active.menu_width - (text_x + text_width) - 30
			local text_scale = (size_of_text / price_width)

			if price_width >= size_of_text then
				vint_set_property(Vehicle_cust_footer.price_h, "scale", text_scale, text_scale)
			end
		else
			local size_of_text = Menu_active.menu_width - price_width - 30
			local text_scale  = (size_of_text / (text_x + text_width))

			if text_x + text_width >= size_of_text then
				vint_set_property(Vehicle_cust_footer.label_h, "scale", text_scale, text_scale)
			end
		end
	end
end

function vehicle_cust_build_footer(menu_data)
	local grp = vint_object_clone(vint_object_find("style_footer"), Menu_option_labels.control_parent)
	vint_set_property(grp, "visible", true)

	if menu_data.footer ~= nil and menu_data.footer.footer_grp ~= nil and menu_data.footer.footer_grp ~= 0 then
		vint_object_destroy(menu_data.footer.footer_grp)
	end

	menu_data.footer = { }
	menu_data.footer.footer_grp = grp

	Vehicle_cust_footer.label_h = vint_object_find("price_label", grp)
	Vehicle_cust_footer.price_h = vint_object_find("price_amount", grp)
	Vehicle_cust_footer.style_h = vint_object_find("style_amount", grp)

	vint_set_property(Vehicle_cust_footer.label_h , "visible", true)
	vint_set_property(Vehicle_cust_footer.price_h , "visible", true)
	vint_set_property(Vehicle_cust_footer.style_h, "visible", true)

end

function vehicle_cust_build_footer_color(menu_data, swatch)
	vehicle_cust_build_footer(menu_data)

	vint_set_property(Vehicle_cust_footer.label_h, "visible", true)
	vint_set_property(Vehicle_cust_footer.price_h , "visible", false)
	vint_set_property(Vehicle_cust_footer.style_h, "visible", false)

	if swatch ~= nil then
		vehicle_cust_update_footer_color(swatch)
	end
end

function vehicle_cust_update_footer_color(swatch)
	vint_set_property(Vehicle_cust_footer.label_h, "visible", false)
	if swatch.label ~= nil and swatch.label ~= 0 then

		vint_set_property(Vehicle_cust_footer.label_h, "visible", true)
		vint_set_property(Vehicle_cust_footer.label_h, "text_tag", swatch.label)

		if swatch.price == nil then
			vint_set_property(Vehicle_cust_footer.price_h , "visible", false)
			return
		end

		if swatch.price == 0 then
			swatch.owned = true
		end

		vint_set_property(Vehicle_cust_footer.price_h , "visible", true)

		if swatch.owned == true then
			vint_set_property(Vehicle_cust_footer.price_h, "text_tag", "STORE_ITEM_OWNED")
		else
			vint_set_property(Vehicle_cust_footer.price_h, "text_tag", "$" .. format_cash(swatch.price))
		end

		if Style_cluster_player_cash < swatch.price and swatch.owned ~= true then
			vint_set_property(Vehicle_cust_footer.price_h, "tint",  MENU_FOOTER_CASH_BROKE_COLOR.R, MENU_FOOTER_CASH_BROKE_COLOR.G, MENU_FOOTER_CASH_BROKE_COLOR.B)
		else
			vint_set_property(Vehicle_cust_footer.price_h, "tint",  MENU_FOOTER_CASH_NORMAL_COLOR.R, MENU_FOOTER_CASH_NORMAL_COLOR.G, MENU_FOOTER_CASH_NORMAL_COLOR.B)
		end
	else
		vint_set_property(Vehicle_cust_footer.label_h, "text_tag_crc", swatch.label_crc)
	end

	vehicle_cust_adjust_footer_positions()
end

function vehicle_cust_update_footer_component(display_name, price, owned)

	vint_set_property(Vehicle_cust_footer.label_h, "text_tag", display_name)

	if price == 0 then
		owned = true
	end

	if owned == true then
		vint_set_property(Vehicle_cust_footer.price_h, "text_tag", "STORE_ITEM_OWNED")
		vint_set_property(Vehicle_cust_footer.style_h, "visible", false)
	else
		vint_set_property(Vehicle_cust_footer.price_h, "text_tag", "$" .. format_cash(price))
		vint_set_property(Vehicle_cust_footer.style_h, "visible", true)

		--Insert style values into style string
		local style = { [0] = award_style("veh_comp", price, true) }
		local style_string = vint_insert_values_in_string("STORE_ITEM_STYLE_AWARD", style)
		vint_set_property(Vehicle_cust_footer.style_h, "text_tag", style_string)
	end

	if Style_cluster_player_cash < price and owned ~= true then
		vint_set_property(Vehicle_cust_footer.price_h, "tint",  MENU_FOOTER_CASH_BROKE_COLOR.R, MENU_FOOTER_CASH_BROKE_COLOR.G, MENU_FOOTER_CASH_BROKE_COLOR.B)
	else
		vint_set_property(Vehicle_cust_footer.price_h, "tint",  MENU_FOOTER_CASH_NORMAL_COLOR.R, MENU_FOOTER_CASH_NORMAL_COLOR.G, MENU_FOOTER_CASH_NORMAL_COLOR.B)
	end

	vehicle_cust_adjust_footer_positions()
end

function vehicle_cust_update_footer_wheels(label)
	Vehicle_cust_wheel_price = Vehicle_cust_rim_price + Vehicle_cust_tire_price + Vehicle_cust_hubcap_price
	if rim_size_text_slider.original_val ~= rim_size_text_slider.cur_value then
		Vehicle_cust_wheel_price = Vehicle_cust_wheel_price + 100
	end

	if wheel_size_text_slider.original_val ~= wheel_size_text_slider.cur_value then
		Vehicle_cust_wheel_price = Vehicle_cust_wheel_price + 100
	end

	if wheel_width_text_slider.original_val ~= wheel_width_text_slider.cur_value then
		Vehicle_cust_wheel_price = Vehicle_cust_wheel_price + 100
	end

	vint_set_property(Vehicle_cust_footer.label_h, "text_tag", label)	--	Should use text_tag_crc


	vint_set_property(Vehicle_cust_footer.price_h, "text_tag", "$" .. format_cash(Vehicle_cust_wheel_price))

	--Style Insert
	local style = { [0] = award_style("veh_comp", Vehicle_cust_wheel_price, true) }
	local style_string = vint_insert_values_in_string("STORE_ITEM_STYLE_AWARD", style)
	vint_set_property(Vehicle_cust_footer.style_h, "text_tag", style_string)

	if Style_cluster_player_cash < Vehicle_cust_wheel_price then
		vint_set_property(Vehicle_cust_footer.price_h, "tint",  MENU_FOOTER_CASH_BROKE_COLOR.R, MENU_FOOTER_CASH_BROKE_COLOR.G, MENU_FOOTER_CASH_BROKE_COLOR.B)
	else
		vint_set_property(Vehicle_cust_footer.price_h, "tint",  MENU_FOOTER_CASH_NORMAL_COLOR.R, MENU_FOOTER_CASH_NORMAL_COLOR.G, MENU_FOOTER_CASH_NORMAL_COLOR.B)
	end

	vehicle_cust_adjust_footer_positions()
end

function vehicle_cust_color_select_release(menu_data)
	vcust_revert_color()
	vehicle_cust_release(menu_data)
end

function vehicle_cust_release(menu_data)
	if menu_data.footer ~= nil then
		vint_set_property(menu_data.footer.footer_grp, "visible", false)
		vint_object_destroy(menu_data.footer.footer_grp)
	end

	if menu_data[0].type == MENU_ITEM_TYPE_GRID then
		menu_grid_release(menu_data[0])
	end
end

function vehicle_cust_finalize_footer(menu_data)
	vint_set_property(Vehicle_cust_footer.price_h, "anchor", menu_data.menu_width - 20, 0)
	vehicle_cust_adjust_footer_positions()
end

------------------------
--	MENU FUNCTIONALITY --
------------------------
-- Creation of Menus
------------------------
--------------------------
---[ Horizontal Menu ]---
function vehicle_cust_build_horz_menu()
	-- New menu, clear out all items
	Vehicle_cust_horz_menu.num_items = 0
	-- Make the request to build the menu
	vint_dataresponder_request("vcust_populate_menu", "vehicle_cust_populate_horz_menu", 0, 0) -- 0 = VCUST_INTF_POPULATE_HORZ_MENU
end

function vehicle_cust_populate_horz_menu(display_name, index)
	local sub_menu
	--	 Alternate the menu so that changing menus erases the footer correctly
	sub_menu = table_clone(Vehicle_cust_menu_a)

	-- Add the item
	Vehicle_cust_horz_menu[Vehicle_cust_horz_menu.num_items] = { label = display_name, sub_menu = sub_menu, id = index }
	-- Increase the count
	Vehicle_cust_horz_menu.num_items = Vehicle_cust_horz_menu.num_items + 1
end

-- Update the Current Menu selection
function vehicle_cust_nav_horz_menu()
	vcust_change_top_level_menu(0, Vehicle_cust_horz_menu[Vehicle_cust_horz_menu.current_selection].id)

	Vehicle_cust_horz_menu[Vehicle_cust_horz_menu.current_selection].sub_menu.btn_tips = Vehicle_cust_btns_top
end

----------------------
---[ Generic Menu ]---
function vehicle_cust_build_menu(menu_data)

	--	If we get back here, we need to rebuild the wheel menu next time we go in
	Vehicle_cust_rebuild_wheel_menu = true
	Vehicle_cust_color_menu = Vehicle_cust_menu
	Vehicle_cust_menu = menu_data
	Vehicle_cust_menu.btn_tips = Vehicle_cust_btns_top
	-- New menu, clear out all items
	Vehicle_cust_menu.num_items = 0
	-- Make the request to build the menu
	if Vehicle_cust_show_slot == -1 then
		Vehicle_cust_menu.on_nav = nil
		Vehicle_cust_menu.on_post_show = nil
		Vehicle_cust_menu.footer_height = nil

		-- Build region menu
		if Vehicle_cust_show_region == true then
			Vehicle_cust_show_region = false
			Vehicle_cust_menu.on_back = nil
			Vehicle_cust_menu.header_label_str = "VCUST_REGION_TITLE"
			--debug_print("VCUST_INTF_POPULATE_COLOR_REGION\n")
			vint_dataresponder_request("vcust_populate_menu", "vehicle_cust_populate_menu", 0, 4) -- 4 = VCUST_INTF_POPULATE_COLOR_REGION
			Vehicle_cust_menu.btn_tips = Vehicle_cust_btns
		else
			Vehicle_cust_menu.on_back = vehicle_cust_exit
			Vehicle_cust_menu.header_label_str = Vehicle_cust_horz_menu[Vehicle_cust_horz_menu.current_selection].label
			--debug_print("VCUST_INTF_POPULATE_CURRENT_MENU\n")
			vint_dataresponder_request("vcust_populate_menu", "vehicle_cust_populate_menu", 0, 1) -- 1 = VCUST_INTF_POPULATE_CURRENT_MENU
			local component = Vehicle_cust_horz_menu[Vehicle_cust_horz_menu.current_selection].sub_menu
			local hl_item = 0
			if component.highlighted_item ~= nil then
				hl_item = component.highlighted_item
			end

			-- In Performance tab, check each upgrade's status [nclok1405]
			if sui_compare_string(Vehicle_cust_menu.header_label_str, "GARAGE_CAT_3") then
				for i = 0, Vehicle_cust_menu.num_items-1, 1 do
					local item = Vehicle_cust_menu[i]

					if item ~= nil and item.id ~= nil then
						local id = item.id
						--debug_print("Checking Performance "..tostring(id).." Status\n")

						-- Pretend the player opened the upgrade options menu for this slot.
						-- Query the upgrade options and its status.
						Vehicle_equipped_perf_upgrade = false
						Vehicle_own_perf_upgrade = false
						Vehicle_equipped_normal_perf_part = false
						vint_dataresponder_request("vcust_populate_menu", "vehicle_cust_performance_state_callback", 0, 2, id)

						-- Add a gold star if this perf upgrade is equipped
						local star = Vehicle_equipped_perf_upgrade and (not Vehicle_equipped_normal_perf_part)

						-- BUG: The game has trouble checking if Tire Durability Upgrade is equipped.
						-- If neither part is equipped, but the upgrade part is owned (price == 0) then probably it is upgraded.
						if (id == 10) and (not Vehicle_equipped_perf_upgrade) and (not Vehicle_equipped_normal_perf_part) and Vehicle_own_perf_upgrade then
							star = true
						end

						if star then
							item.label = vint_insert_values_in_string("[format][color:full_bright][image:ui_hud_diversion_star_gold]{0}[/format]", {[0] = item.label})
						end

						-- Pretend the player backed out from the upgrade options menu.
						-- May or may not be needed, but this is the menu flow expected by the game.
						vint_dataresponder_request("vcust_populate_menu", "vehicle_cust_dummy_callback", 0, 1) -- 1 = VCUST_INTF_POPULATE_CURRENT_MENU
					end
				end
			end

--			vcust_adjust_camera_angle(component[hl_item].id)
		end

	else
		Vehicle_cust_menu.header_label_str = Vehicle_cust_title_to_use
		Vehicle_cust_menu.on_nav = vehicle_cust_nav_component
		Vehicle_cust_menu.on_post_show = vehicle_cust_finalize_component
		Vehicle_cust_menu.footer_height = 40
		vehicle_cust_build_footer(Vehicle_cust_menu)
		Vehicle_cust_menu.highlighted_item = 0
		--debug_print("VCUST_INTF_POPULATE_COMPONENT_MENU\n")
		vint_dataresponder_request("vcust_populate_menu", "vehicle_cust_populate_menu", 0, 2, Vehicle_cust_show_slot) -- 2 = VCUST_INTF_POPULATE_COMPONENT_MENU

		local component = Vehicle_cust_menu[Vehicle_cust_menu.highlighted_item]
		vehicle_cust_update_footer_component(component.label, component.price, component.owned)
		vcust_preview_component(0, component.id)
--		vcust_adjust_camera_angle(component.id)
		Vehicle_cust_menu.btn_tips = Vehicle_cust_btns
		btn_tips_update()
	end
	Vehicle_cust_show_slot = -1 -- Reset it so we don't get stuck in perma-slot menu

	--	No footer if there are no options in there
	if Vehicle_cust_menu.num_items == 0 then
		Vehicle_cust_menu.num_items = 1
		Vehicle_cust_menu.on_post_show = nil
		Vehicle_cust_menu[0] = { label = "STORE_NO_ITEMS_IN_CATEGORY", type=MENU_ITEM_TYPE_SELECTABLE }
		Vehicle_cust_menu.footer_height = nil
	end

end

-- Do nothing [nclok1405]
function vehicle_cust_dummy_callback(display_name, cat_type, id, price, current)
	--debug_print("vehicle_cust_dummy_callback cat_type:"..tostring(cat_type)..", id:"..tostring(id)..", price:"..tostring(price)..", current:"..tostring(current).."\n")
end

-- Performance upgrade query callback [nclok1405]
function vehicle_cust_performance_state_callback(display_name, cat_type, id, price, current)
	local partname = "unknown"
	if sui_compare_string(display_name, "VCUST_PERFORMANCE_ADD") then
		partname = "VCUST_PERFORMANCE_ADD"	-- Upgrade
	elseif sui_compare_string(display_name, "COMPONENT_OPTION_2") then
		partname = "COMPONENT_OPTION_2"	-- Option 2 (Speed Upgrade)
	elseif sui_compare_string(display_name, "VCUST_PERFORMANCE_REMOVE") then
		partname = "VCUST_PERFORMANCE_REMOVE"	-- Stock
	elseif sui_compare_string(display_name, "COMPONENT_NONE") then
		partname = "COMPONENT_NONE"	-- None (Speed Upgrade)
	end

	--debug_print("vehicle_cust_performance_state_callback partname:"..partname..", cat_type:"..tostring(cat_type)..", id:"..tostring(id)..", price:"..tostring(price)..", current:"..tostring(current).."\n")

	if partname == "VCUST_PERFORMANCE_ADD" or partname == "COMPONENT_OPTION_2" then
		-- Performance Upgrade Part is currently Equipped
		if (current == true) then
			Vehicle_equipped_perf_upgrade = true
		end
		-- Performance Upgrade Part is owned
		if (price == 0) then
			Vehicle_own_perf_upgrade = true
		end
	elseif partname == "VCUST_PERFORMANCE_REMOVE" or partname == "COMPONENT_NONE" then
		-- Normal Performance Part is currently equipped
		if (current == true) then
			Vehicle_equipped_normal_perf_part = true
		end
	end
end

function vehicle_cust_populate_menu(display_name, cat_type, id, price, current)
	--debug_print("vehicle_cust_populate_menu cat_type:"..tostring(cat_type)..", id:"..tostring(id)..", price:"..tostring(price)..", current:"..tostring(current).."\n")

	-- Add the item
	Vehicle_cust_menu[Vehicle_cust_menu.num_items] =
		{ label = display_name, type=MENU_ITEM_TYPE_SUB_MENU, sub_menu = Vehicle_cust_menu_c, id = id, price = price, equipped = current }
	if price == 0 then
		Vehicle_cust_menu[Vehicle_cust_menu.num_items].owned = true
	else
		Vehicle_cust_menu[Vehicle_cust_menu.num_items].owned = false
	end

	if cat_type > -1 and cat_type < Vehicle_cust_menu_ops.num_ops then
		Vehicle_cust_menu[Vehicle_cust_menu.num_items].on_select = Vehicle_cust_menu_ops[cat_type].on_select
		Vehicle_cust_menu[Vehicle_cust_menu.num_items].type = Vehicle_cust_menu_ops[cat_type].type
		Vehicle_cust_menu[Vehicle_cust_menu.num_items].sub_menu = Vehicle_cust_menu_ops[cat_type].sub_menu
		if Vehicle_cust_menu_ops[cat_type].on_nav ~= nil then
			Vehicle_cust_menu.on_nav = Vehicle_cust_menu_ops[cat_type].on_nav
		end

	else
		debug_print("vint", "Vehicle Customization - Invalid Category type: " .. cat_type .. "\n")
	end

	if current == true then
		Vehicle_cust_menu.highlighted_item = Vehicle_cust_menu.num_items
	end

	-- Increase the count
	Vehicle_cust_menu.num_items = Vehicle_cust_menu.num_items + 1
end

-- Selection / Navigation
function vehicle_cust_select_category(menu_label, menu_data)		--	Category selection
	Vehicle_cust_show_slot = -1
	vcust_make_menu_selection(0, Vehicle_cust_category_selected)	-- 0 = category
end

function vehicle_cust_select_advanced_region(menu_label, menu_data)			-- Special case for Palette menu
	Vehicle_cust_color_slot = menu_data.id
end

function vehicle_cust_select_region(menu_label, menu_data)
	Vehicle_cust_color_slot = menu_data.id
	vcust_select_paint_slot(Vehicle_cust_color_slot)					--	Build the paint slots
	Vehicle_cust_region_menu.on_show = vehicle_cust_build_menu
	Vehicle_cust_show_region = true
end

-- Update the current menu slot
function vehicle_cust_select_slot(menu_label, menu_data)
	Vehicle_cust_show_slot = menu_data.id
	Vehicle_cust_title_to_use = menu_data.label
--	vcust_adjust_camera_angle(Vehicle_cust_show_slot)
	Vehicle_cust_menu_c.on_show = vehicle_cust_build_menu
end

function vehicle_cust_nav_slot(menu_data)
--	vcust_adjust_camera_angle(menu_data[menu_data.highlighted_item].id)
end

function vehicle_cust_nav_component(menu_data)
	vcust_preview_component(0, menu_data[menu_data.highlighted_item].id)
	vehicle_cust_update_footer_component(menu_data[menu_data.highlighted_item].label, menu_data[menu_data.highlighted_item].price, menu_data[menu_data.highlighted_item].owned)
end

function vehicle_cust_finalize_component(menu_data)
	vehicle_component_line_update_checkbox(menu_data)
	vehicle_update_custom_scrollbar()
	vehicle_cust_finalize_footer(menu_data)
end

-- Possibly make a purchase
function vehicle_cust_select_component(menu_label, menu_data)
	-- Confirm the purchase if we can afford it
	if Style_cluster_player_cash >= menu_data.price and menu_data.price ~= 0 and menu_data.owned ~= true then
		Vehicle_cust_component_selected = menu_data
		-- local body = "Do you wish to purchase " .. menu_data.label .. " for $" .. format_cash(menu_data.price) .. "?"
		local insert = { [0] = menu_data.label, [1] = format_cash(menu_data.price) }
		local body = vint_insert_values_in_string("VCUST_PURCHASE_PROMPT", insert)
		local heading = "MENU_TITLE_CONFIRM"
		dialog_box_confirmation(heading, body, "vehicle_cust_component_confirm")
	elseif menu_data.price ~= 0 and menu_data.owned ~= true then
		dialog_box_message("MENU_TITLE_NOTICE", "HUD_SHOP_INSUFFICIENT_FUNDS")
	else
		Vehicle_cust_component_selected = menu_data
		Vehicle_just_upgrade = true
		vehicle_cust_component_confirm(0, DIALOG_ACTION_CLOSE)
	end
end

-- Make the purchase for realz
function vehicle_cust_component_confirm(result, action)
	if action ~= DIALOG_ACTION_CLOSE then
		return
	end

	if result == 0 then
		if vcust_show_nos_hydraulic_warning() == true then
			dialog_box_confirmation("MENU_TITLE_CONFIRM", "VCUST_PERFORMANCE_WARNING", "vehicle_cust_component_confirm2")
		else
			vehicle_cust_component_confirm2(0, DIALOG_ACTION_CLOSE)
		end
	end
end

function vehicle_cust_component_confirm2(result, action)
	if action ~= DIALOG_ACTION_CLOSE then
		return
	end

	if result == 0 then
		if Vehicle_cust_component_selected.price ~= 0 then
			award_style("veh_comp", Vehicle_cust_component_selected.price)
		end
		Vehicle_cust_component_selected.owned = true
		vcust_purchase_component()		--	Stop previewing the component, keep it and deduct cash
		if Vehicle_just_upgrade	== true then
			audio_play(Vehicle_upgrade_sound)
			Vehicle_just_upgrade = false
		else
			audio_play(Menu_sound_purchase)
		end
		menu_show(Menu_active.parent_menu, MENU_TRANSITION_SWEEP_RIGHT)
	end
end

------------------------------
----[ Color Palette Menu ]----
function vehicle_cust_build_palette(menu_data)
	Vehicle_cust_menu = menu_data

	local menu_item = menu_data[0]
	menu_item.swatches = { num_swatches = 0 }
	menu_item.cur_idx = 0

	-- Make the request to build the menu
	vint_dataresponder_request("vcust_populate_palette_menu", "vehicle_cust_populate_palette_menu", 0, Vehicle_cust_color_slot)
	local master_swatch = vint_object_find("swatch_paint", nil, MENU_BASE_DOC_HANDLE)
	menu_grid_show(menu_data, menu_item, master_swatch, true)

	-- update/build footer
	vehicle_cust_build_footer_color(menu_data, menu_item.swatches[menu_item.cur_idx])
	local idx = menu_item.cur_row * menu_item.num_cols + menu_item.cur_col
	if idx < menu_item.swatches.num_swatches then
		vehicle_cust_update_footer_color(menu_item.swatches[idx])
	end
end

function vehicle_cust_populate_palette_menu(display_name, current, base_r, base_g, base_b, spec_col_r, spec_col_g, spec_col_b, spec_alpha, fres_col_r, fres_col_g, fres_col_b, fres_con, refl, is_glass)
	local swatches = Vehicle_cust_color_palette[0].swatches
	swatches[swatches.num_swatches] = {
		label = display_name,
		base_r = base_r, base_g = base_g, base_b = base_b, 								-- Base paint color, used on base
		spec_col_r = spec_col_r, spec_col_g = spec_col_g, spec_col_b = spec_col_b,	-- Specular color, used on spec and irr
		spec_alpha = spec_alpha, 																	-- Specular alpha, used on spec
		fres_col_r = fres_col_r, fres_col_g = fres_col_g, fres_col_b = fres_col_b, -- Fresnel color, used on fres, refl, sky
		fres_con = fres_con, 																		-- Fresnel 'alpha' (contrast), used on fres
		refl = refl, 																					-- Reflection color
		is_glass = is_glass,
	}

	if current == true then
		Vehicle_cust_color_palette[0].cur_idx = swatches.num_swatches
	end

	swatches.num_swatches = swatches.num_swatches + 1
	--[[
	debug_print("vint", "display_name " .. vint_debug_decode_wide_string(display_name) .. "\n")
	debug_print("vint", "spec_alpha " .. var_to_string(spec_alpha).. "\n")
	debug_print("vint", "spec_col_r " .. var_to_string(spec_col_r).. "\n")
	debug_print("vint", "fres_con " .. var_to_string(fres_con).. "\n")
	debug_print("vint", "fres_col_r " .. var_to_string(fres_col_r).. "\n")
	debug_print("vint", "refl " .. var_to_string(refl) .."\n\n\n")

	]]
end

function vehicle_cust_return_palette()
	Vehicle_cust_show_region = true
	menu_show(Menu_active.parent_menu, MENU_TRANSITION_SWEEP_RIGHT)
	audio_play(Menu_sound_back)
end

function vehicle_cust_update_palette_swatch(swatch)
	local icon_h = vint_object_find("icon", swatch.swatch_h)
	vint_set_property(icon_h, "visible", true)
	vint_set_property(swatch.swatch_h, "visible", true)

	local base_h = vint_object_find("base", icon_h)
	local fres_h = vint_object_find("fres", icon_h)
	local irr_h  = vint_object_find("irr", icon_h)
	local refl_h = vint_object_find("refl", icon_h)
	local sky_h  = vint_object_find("sky", icon_h)
	local spec_h = vint_object_find("spec", icon_h)

	--turn off the sky, it blows out the interior color... we turn this on later
	vint_set_property(sky_h, "visible", false)

	-- If there's no Fresnel, then hide irridescence.
	if swatch.fres_con == 0 then
		vint_set_property(irr_h, "visible", false)
	end

	local base_adj = 1.2
	local refl_adj = .7
	local glass_adj = .5
	-- Setup the colors
	vint_set_property(base_h, "tint", swatch.base_r * base_adj, swatch.base_g * base_adj, swatch.base_b * base_adj)
	if swatch.is_glass == true then
		vint_set_property(icon_h, "scale", 0.86, 0.86)
		vint_set_property(icon_h, "anchor", -1, -1)
		--base, make this dark
		vint_set_property(base_h, "image", "ui_menu_veh_glass")  -- dark
		vint_set_property(base_h, "alpha", 0.4)
		vint_set_property(base_h, "tint", 0, 0, 0)
		vint_set_property(base_h, "anchor", 3, 3)
		--make the irr channel be the tinted color of glass
		vint_set_property(irr_h, "image", "ui_menu_veh_glass")  --normal
		vint_set_property(irr_h, "alpha", 1)
		vint_set_property(irr_h, "tint", swatch.base_r * base_adj, swatch.base_g * base_adj, swatch.base_b * base_adj)
		--make reflection turn on, be normal color to simulate real reflection
		vint_set_property(refl_h, "image", "ui_menu_veh_glass")
		vint_set_property(refl_h, "alpha", 0.62)
		vint_set_property(refl_h, "tint", 1, 1, 1)
		--turn off other shit
		vint_set_property(fres_h, "visible", false)
		vint_set_property(sky_h, "visible", false)
		vint_set_property(spec_h, "visible", false)
		return
	end

	if swatch.is_glass == false then
		--reset swatch back from glass to default
		vint_set_property(icon_h, "scale", 1, 1)
		vint_set_property(refl_h, "alpha", .2)
		vint_set_property(icon_h, "anchor", 0, -3)
		vint_set_property(base_h, "anchor", 0, 0)

	end

	vint_set_property(sky_h, "tint", .65 + (swatch.base_r * .55), .65 + (swatch.base_g * .55), .65 + (swatch.base_b * .55))
	vint_set_property(spec_h, "tint", swatch.spec_col_r, swatch.spec_col_g, swatch.spec_col_b)
	vint_set_property(irr_h, "tint", swatch.fres_col_r, swatch.fres_col_g, swatch.fres_col_b)
	vint_set_property(fres_h, "tint", swatch.fres_col_r, swatch.fres_col_g,  swatch.fres_col_b)
	vint_set_property(refl_h, "tint", swatch.base_r * refl_adj, swatch.base_g * refl_adj, swatch.base_b * refl_adj)

	--Setup the alphas
	vint_set_property(spec_h, "alpha", swatch.spec_alpha * 0.8)

	-- Interior/glass
	if swatch.refl ~= nil then
		vint_set_property(sky_h, "visible", true)
		vint_set_property(refl_h, "alpha", swatch.refl)
		vint_set_property(sky_h, "alpha", swatch.refl * 0.25)
		vint_set_property(fres_h, "alpha", swatch.fres_con * 0.56)
	end


	if swatch.fres_con ~= nil then
		if swatch.fres_con > 1 or swatch.fres_con == 0.75 then
			local fres_adj = (swatch.fres_col_r + swatch.fres_col_g +  swatch.fres_col_b) /3
			vint_set_property(refl_h, "alpha", swatch.fres_con * 1.1)
			vint_set_property(sky_h, "alpha", fres_adj * 0.55)
			vint_set_property(fres_h, "alpha", swatch.fres_con * 0.56)
			vint_set_property(refl_h, "tint", swatch.fres_col_r * refl_adj, swatch.fres_col_g * refl_adj, swatch.fres_col_b * refl_adj)
		else
			-- opaque
			if swatch.fres_con == 0 and swatch.spec_alpha < .21  and swatch.spec_alpha > .2 and swatch.refl < 16 then
				vint_set_property(refl_h, "alpha", 0)
				vint_set_property(sky_h, "alpha", 0)
				vint_set_property(fres_h, "alpha", 0)
				vint_set_property(spec_h, "alpha", 0)
				vint_set_property(irr_h, "alpha", 0)
			end

			-- matte
			if swatch.fres_con == 0 and swatch.spec_alpha < .21  and swatch.spec_alpha > .2 and swatch.refl < 13 and swatch.refl > 12 then
				vint_set_property(refl_h, "alpha", 0)
				vint_set_property(sky_h, "alpha", 0)
				vint_set_property(fres_h, "alpha", 0)
				vint_set_property(irr_h, "alpha", 0)
			end
		end
	end

end

-- Menu Navigation / Selection
function vehicle_cust_nav_new_palette(menu_label, menu_data)
	local swatches = menu_data.swatches
	local idx = menu_data.cur_row * menu_data.num_cols + menu_data.cur_col

	if idx < swatches.num_swatches then
		vehicle_cust_update_footer_color(swatches[idx])
	end
end

---------------------------
----[ Color Grid Menu ]----
function vehicle_cust_build_color_grid(menu_data)
	Vehicle_cust_menu = menu_data

	local menu_item = menu_data[0]
	menu_item.swatches = { num_swatches = 0 }
	menu_item.cur_idx = 0

	-- Make the request to build the menu
	vint_dataresponder_request("vcust_populate_color_grid", "vehicle_cust_populate_color_grid", 0, Vehicle_cust_color_slot, Vehicle_cust_palette_choice)
	local master_swatch = vint_object_find("swatch_paint", nil, MENU_BASE_DOC_HANDLE)

	menu_grid_show(menu_data, menu_item, master_swatch, true)
	vehicle_cust_build_footer_color(menu_data, menu_item.swatches[menu_item.cur_idx])
	local idx = menu_item.cur_row * menu_item.num_cols + menu_item.cur_col
	if idx < menu_item.swatches.num_swatches then
		vehicle_cust_update_footer_color(menu_item.swatches[idx])
	end

	Vehicle_cust_menu.btn_tips = Vehicle_cust_btns
	btn_tips_update()
end

function vehicle_cust_populate_color_grid(display_name, current, base_r, base_g, base_b, spec_col_r, spec_col_g, spec_col_b, spec_alpha, fres_col_r, fres_col_g, fres_col_b, fres_con, refl, price, is_glass)
	local swatches = Vehicle_cust_color_select_menu[0].swatches
	swatches[swatches.num_swatches] = {
		label = display_name,
		base_r = base_r, base_g = base_g, base_b = base_b, 								-- Base paint color, used on base
		spec_col_r = spec_col_r, spec_col_g = spec_col_g, spec_col_b = spec_col_b,	-- Specular color, used on spec and irr
		spec_alpha = spec_alpha, 																	-- Specular alpha, used on spec
		fres_col_r = fres_col_r, fres_col_g = fres_col_g, fres_col_b = fres_col_b, -- Fresnel color, used on fres, refl, sky
		fres_con = fres_con, 																		-- Fresnel 'alpha' (contrast), used on fres
		refl = refl, 																					-- Reflection color
		price = price,
		owned = current,
		is_glass = is_glass,																			-- Glass or Interior or normal
	}
	if current == true then
		Vehicle_cust_color_select_menu[0].cur_idx = swatches.num_swatches
	end

	swatches.num_swatches = swatches.num_swatches + 1

end

function vehicle_cust_update_color_grid(swatch)
	local icon_h = vint_object_find("icon", swatch.swatch_h)

	vint_set_property(icon_h, "visible", true)
	vint_set_property(swatch.swatch_h, "visible", true)

	local base_h = vint_object_find("base", icon_h)
	local fres_h = vint_object_find("fres", icon_h)
	local irr_h  = vint_object_find("irr", icon_h)
	local refl_h = vint_object_find("refl", icon_h)
	local sky_h  = vint_object_find("sky", icon_h)
	local spec_h = vint_object_find("spec", icon_h)

	local base_adj = 1.5

	-- Setup the colors
	vint_set_property(base_h, "tint", swatch.base_r * base_adj, swatch.base_g * base_adj, swatch.base_b * base_adj)

	if swatch.is_glass == true then
		vint_set_property(base_h, "image", "ui_bms_veh_glass")
		vint_set_property(fres_h, "visible", false)
		vint_set_property(irr_h, "visible", false)
		vint_set_property(refl_h, "visible", false)
		vint_set_property(sky_h, "visible", false)
		vint_set_property(spec_h, "visible", false)
		return
	end
	vint_set_property(spec_h, "tint", swatch.spec_col_r, swatch.spec_col_g, swatch.spec_col_b)
	vint_set_property(irr_h, "tint", swatch.spec_col_r, swatch.spec_col_g, swatch.spec_col_b)
	vint_set_property(fres_h, "tint", swatch.fres_col_r, swatch.fres_col_g, swatch.fres_col_b)
--	vint_set_property(sky_h, "tint", swatch.fres_col_r, swatch.fres_col_g, swatch.fres_col_b)
	vint_set_property(refl_h, "tint", swatch.fres_col_r, swatch.fres_col_g, swatch.fres_col_b)

	--Setup the alphas
	vint_set_property(spec_h, "alpha", swatch.spec_alpha * 0.8)
	vint_set_property(refl_h, "alpha", swatch.refl)
	vint_set_property(sky_h, "alpha",  swatch.refl * 0.2)
	vint_set_property(fres_h, "alpha", swatch.fres_con * 0.5)
	if swatch.fres_con == 0 then
		vint_set_property(irr_h, "visible", false)
	end
end

-- Selection / Navigation
function vehicle_cust_nav_new_color(menu_label, menu_data)
	local swatches = menu_data.swatches
	local idx = menu_data.cur_row * menu_data.num_cols + menu_data.cur_col

	if idx < swatches.num_swatches then
		vehicle_cust_update_footer_color(swatches[idx])
		vcust_preview_color(idx)
	end
end

Vehicle_cust_color_swatch_to_purchase = { }
function vehicle_cust_select_color(menu_label, menu_data)
	local swatches = menu_data.swatches
	local idx = menu_data.cur_row * menu_data.num_cols + menu_data.cur_col

	if idx < swatches.num_swatches then
		Vehicle_cust_color_swatch_to_purchase = swatches[idx]
		if Vehicle_cust_color_swatch_to_purchase.price == 0 or Vehicle_cust_color_swatch_to_purchase.owned == true then
			menu_show(Vehicle_cust_color_menu, MENU_TRANSITION_SWEEP_LEFT)
		elseif Style_cluster_player_cash >= Vehicle_cust_color_swatch_to_purchase.price then -- Confirm the purchase if we can afford it
--			local body = "Do you wish to purchase " .. Vehicle_cust_color_swatch_to_purchase.label .. " for $" .. format_cash(Vehicle_cust_color_swatch_to_purchase.price) .. "?"
			local insert = { [0] = Vehicle_cust_color_swatch_to_purchase.label, [1] = format_cash(Vehicle_cust_color_swatch_to_purchase.price) }
			local body = vint_insert_values_in_string("VCUST_PURCHASE_PROMPT", insert)
			local heading = "MENU_TITLE_CONFIRM"
			dialog_box_confirmation(heading, body, "vehicle_cust_color_confirm")
		else
			dialog_box_message("MENU_TITLE_NOTICE", "HUD_SHOP_INSUFFICIENT_FUNDS")
		end
	end
end

function vehicle_cust_color_confirm(result, action)
	if action ~= DIALOG_ACTION_CLOSE then
		return
	end

	if result == 0 then
		if Vehicle_cust_color_swatch_to_purchase.price ~= 0 then
			award_style("veh_comp", Vehicle_cust_color_swatch_to_purchase.price)
		end

		vcust_purchase_paint(Vehicle_cust_color_swatch_to_purchase.price)	--	Purchase the currently previewed color
		audio_play(Menu_sound_purchase)
		menu_show(Vehicle_cust_color_menu, MENU_TRANSITION_SWEEP_LEFT)
	end
end

function vcehicle_cust_revert_color()
	vcust_revert_color();
	menu_show(Menu_active.parent_menu, MENU_TRANSITION_SWEEP_RIGHT)
	audio_play(Menu_sound_back)
end

function vehicle_cust_select_color_grid(menu_label, menu_data)
	local swatches = menu_data.swatches
	local idx = menu_data.cur_row * menu_data.num_cols + menu_data.cur_col

	if idx < swatches.num_swatches then
		Vehicle_cust_palette_choice = idx
	end

	Vehicle_cust_color_select_menu.parent_menu = Menu_active
	menu_show(Vehicle_cust_color_select_menu, MENU_TRANSITION_SWEEP_LEFT)
end

----------------------
----[ Wheel Menu ]----
----------------------
function vehicle_cust_select_axle(menu_label, menu_data)
	Vehicle_cust_wheel_menu.header_label_str = menu_data.label
	Vehicle_cust_chosen_axle = Vehicle_cust_axle_menu.highlighted_item - 1   -- -1 = both, 0 = front, 1 = rear
end

function vehicle_cust_revert_wheels()
	vcust_revert_wheels()
	menu_show(Menu_active.parent_menu, MENU_TRANSITION_SWEEP_RIGHT)
	audio_play(Menu_sound_back)
end

function vehicle_cust_reset_wheels()
	Vehicle_cust_rebuild_wheel_menu = true
	Vehicle_cust_slider_values.rim_size = -1
	Vehicle_cust_slider_values.wheel_size = -1
	Vehicle_cust_slider_values.wheel_width = -1
end

function vehicle_cust_build_wheel_menu(menu_data)
	Vehicle_cust_menu = menu_data
	vint_dataresponder_request("vcust_populate_wheel_menu", "vehicle_cust_populate_wheel_menu", 0, 7, Vehicle_cust_rebuild_wheel_menu, Vehicle_cust_chosen_axle) -- 7 = VCUST_INTF_POPULATE_WHEEL_MENU
	Vehicle_cust_rebuild_wheel_menu = false

	vehicle_cust_build_footer(menu_data)
	vehicle_cust_update_footer_wheels(Vehicle_cust_menu.header_label_str)
	Vehicle_cust_menu.btn_tips = Vehicle_cust_btns
end

function vehicle_cust_populate_wheel_menu(rim_display_name, tire_index, hubcap_index, spinner_index, current_rim_family, rim_size,
														wheel_size_min, wheel_size_max, wheel_size,
														wheel_width_min, wheel_width_max, wheel_width)
	Vehicle_cust_menu.num_items = 8
	Vehicle_cust_rim_family = current_rim_family
	Vehicle_cust_rim_index = current_rim_family
	--	Rim Display
	Vehicle_cust_menu[0].info_text_str = rim_display_name

	--	Tire tread display
	local insert_values = { [0] = tire_index + 1, }
	Vehicle_cust_menu[1].info_text_str = vint_insert_values_in_string("VCUST_TIRE_TREAD_NUMBER", insert_values)

	--	Hubcap Display
	Vehicle_cust_menu[2].disabled = false
	if hubcap_index == -2 or hubcap_index == -1 then
		if hubcap_index == -2 then
			Vehicle_cust_menu[2].disabled = true
			Vehicle_cust_menu[2].info_text_str = "STORE_NOT_AVAILABLE"
		else
			Vehicle_cust_menu[2].info_text_str = "COMPONENT_NONE"
		end
	else
		local insert_values = { [0] = hubcap_index + 1, }
		Vehicle_cust_menu[2].info_text_str = vint_insert_values_in_string("VCUST_HUBCAP_NUMBER" , insert_values)
	end

	-- Spinner Display
	Vehicle_cust_menu[3].disabled = false
	if spinner_index == -2 or spinner_index == -1 then
		if spinner_index == -2 then
			Vehicle_cust_menu[3].disabled = true
			Vehicle_cust_menu[3].info_text_str = "STORE_NOT_AVAILABLE"
		else
			Vehicle_cust_menu[3].info_text_str = "COMPONENT_NONE"
		end
	else
		local insert_values = { [0] = spinner_index + 1, }
		Vehicle_cust_menu[3].info_text_str = vint_insert_values_in_string("VCUST_SPINNER_NUMBER", insert_values)
	end

	--	Rim Size display
	local idx = 4
	if rim_size == -10 then
		Vehicle_cust_menu.num_items = Vehicle_cust_menu.num_items - 1
		rim_size_text_slider.cur_value = 0
		rim_size_text_slider.original_val = 0
	else
		rim_size_text_slider.num_values = 5
		rim_size_text_slider.cur_value = rim_size
		rim_size_text_slider.original_val = rim_size_text_slider.cur_value
		for i = 0, rim_size_text_slider.num_values - 1 do
			rim_size_text_slider[i] = { label = Vehicle_cust_rim_sizes[i] }
		end

		idx = idx + 1
	end

	--	Wheel Size Display

	if wheel_size_min == wheel_size_max then
		Vehicle_cust_menu.num_items = Vehicle_cust_menu.num_items - 1
		wheel_size_text_slider.cur_value = 0
		wheel_size_text_slider.original_val = 0
	else
		Vehicle_cust_menu[idx] = { label="VCUST_WHEEL_SIZE_OPTION", type=MENU_ITEM_TYPE_TEXT_SLIDER, text_slider_values = wheel_size_text_slider, on_value_update = vehicle_cust_wheel_size_update }

		wheel_size_text_slider.num_values = (wheel_size_max - wheel_size_min) + 1
		wheel_size_text_slider.cur_value = wheel_size - wheel_size_min
		wheel_size_text_slider.original_val = wheel_size_text_slider.cur_value
		Vehicle_cust_menu[idx].wheel_size_min = wheel_size_min

		local count = 0
		for i = wheel_size_min, wheel_size_max do
			wheel_size_text_slider[count] = { label = i }
			count = count + 1
		end

		idx = idx + 1
	end

	--	Wheel Width display
	if wheel_width_min == wheel_width_max then
		Vehicle_cust_menu.num_items = Vehicle_cust_menu.num_items - 1
		wheel_width_text_slider.cur_value = 0
		wheel_width_text_slider.original_val = 0
	else
		Vehicle_cust_menu[idx] = { label="VCUST_WHEEL_WIDTH_OPTION", type=MENU_ITEM_TYPE_TEXT_SLIDER,  text_slider_values = wheel_width_text_slider, on_value_update = vehicle_cust_wheel_width_update}  -- on_select

		wheel_width_text_slider.num_values = (wheel_width_max - wheel_width_min) + 1
		wheel_width_text_slider.cur_value = wheel_width - wheel_width_min
		wheel_width_text_slider.original_val = wheel_width_text_slider.cur_value
		Vehicle_cust_menu[idx].wheel_width_min = wheel_width_min

		local count = 0
		for i = wheel_width_min, wheel_width_max do
			wheel_width_text_slider[count] = { label = i }
			count = count + 1
		end

		idx = idx + 1
	end

	Vehicle_cust_menu[idx] = { label="VCUST_PURCHASE_OPTION", type=MENU_ITEM_TYPE_SELECTABLE, on_select = vehicle_cust_purchase_wheels }

end

----------------------------------
-- Wheel/Rim Size Slider Functions
function vehicle_cust_rim_profile_update(menu_label, menu_data)
	vcust_preview_rim_sizing(menu_data.text_slider_values.cur_value)
	vehicle_cust_update_footer_wheels(Vehicle_cust_wheel_menu.header_label_str)
end

function vehicle_cust_wheel_size_update(menu_label, menu_data)
	vcust_preview_wheel_sizing(menu_data.text_slider_values.cur_value + menu_data.wheel_size_min, -1)
	vehicle_cust_update_footer_wheels(Vehicle_cust_wheel_menu.header_label_str)
end

function vehicle_cust_wheel_width_update(menu_label, menu_data)
	vcust_preview_wheel_sizing(-1, menu_data.text_slider_values.cur_value  + menu_data.wheel_width_min)
	vehicle_cust_update_footer_wheels(Vehicle_cust_wheel_menu.header_label_str)
end

-----------------------
-- Create Rim menu
function vehicle_cust_build_rim_menu(menu_data)
	Vehicle_cust_menu = menu_data
	-- New menu, clear out all items
	Vehicle_cust_menu.num_items = 0
	Vehicle_cust_menu.header_label_str = "VCUST_RIM_FAMILY_TITLE"
	vint_dataresponder_request("vcust_populate_wheel_menu", "vehicle_cust_populate_rim_menu", 0, 8) -- 8 = VCUST_INTF_POPULATE_RIM_FAMILY_MENU
	Vehicle_cust_menu.btn_tips = Vehicle_cust_btns
end

function vehicle_cust_populate_rim_menu(display_name, current, id)
	Vehicle_cust_menu[Vehicle_cust_menu.num_items] = { label = display_name, type=MENU_ITEM_TYPE_SELECTABLE, on_select=vehicle_cust_get_rim_grid, id = id }
	if current == 1 then
		Vehicle_cust_menu.highlighted_item = Vehicle_cust_menu.num_items
	end
	Vehicle_cust_menu.num_items = Vehicle_cust_menu.num_items + 1
end

function vehicle_cust_build_rim_grid(menu_data)
	menu_data.header_label_str = Vehicle_cust_menu[Vehicle_cust_menu.highlighted_item].label

	Vehicle_cust_menu = menu_data
	Vehicle_cust_menu.num_items = 1
	Vehicle_cust_menu.on_back = vehicle_cust_revert_rims
	Vehicle_cust_menu.on_post_show = vehicle_cust_finalize_footer

	-- Create the grid
	Vehicle_cust_menu[0] = { label = "", type = MENU_ITEM_TYPE_GRID, on_select = vehicle_cust_preview_wheel_changes, on_nav = vehicle_cust_nav_new_rim,
									 row_height = MENU_SWATCH_DEFAULT_ROW_HEIGHT, num_cols = 4, col_width = MENU_SWATCH_DEFAULT_COL_WIDTH, highlight_scale = 1, unhighlight_scale = 0.7}
	Vehicle_cust_menu[0].item_type = "rim"

	--	Initilaize the swatches
	local menu_item = Vehicle_cust_menu[0]
	menu_item.swatches = { }
	menu_item.swatches = { num_swatches = 0 }
	menu_item.cur_idx = 0

	-- Make the request to build the menu
	vint_dataresponder_request("vcust_populate_wheel_grid_menu", "vehicle_cust_populate_rim_grid", 0, 9, Vehicle_cust_rim_index) -- 9 = VCUST_INTF_POPULATE_RIM_MENU

	-- Show the current rim
	vcust_preview_component(2, 0, Vehicle_cust_rim_index, menu_item.cur_idx)

	local idx = menu_item.cur_idx
	menu_grid_show(menu_data, menu_item)

	vehicle_cust_build_footer(menu_data)

	local insert_values = { [0] = idx + 1, }
	local rim_name = vint_insert_values_in_string("VCUST_RIM_NUMBER", insert_values)
	vehicle_cust_update_footer_component(rim_name, menu_item.swatches[idx].price, menu_item.swatches[idx].owned)
	Vehicle_cust_menu.btn_tips = Vehicle_cust_btns
end

function vehicle_cust_populate_rim_grid(display_name, image_crc, price, current)
	local swatches = Vehicle_cust_menu[0].swatches
	swatches[swatches.num_swatches] = {	label = display_name, swatch_crc = image_crc, price = price, owned = false }

	if price == 0 then
		swatches[swatches.num_swatches].owned = true
	end

	if current == true then
		Vehicle_cust_menu[0].cur_idx = swatches.num_swatches
	end

	swatches.num_swatches = swatches.num_swatches + 1
end

-----------------------
-- Create Tires Menu
function vehicle_cust_build_tire_menu(menu_data)
	Vehicle_cust_menu = menu_data

	-- New menu, clear out all items
	Vehicle_cust_menu.num_items = 1
	Vehicle_cust_menu.header_label_crc = nil
	Vehicle_cust_menu.header_label_str = "VCUST_TIRES_TITLE"
	Vehicle_cust_menu.on_back = vehicle_cust_revert_tires
	Vehicle_cust_menu.on_post_show = vehicle_cust_finalize_footer
	Vehicle_cust_menu.footer_height = 40

	-- Create the grid
	Vehicle_cust_menu[0] = { label = "", type = MENU_ITEM_TYPE_GRID, on_select = vehicle_cust_preview_wheel_changes, on_nav = vehicle_cust_nav_new_tire,
									  row_height = MENU_SWATCH_DEFAULT_ROW_HEIGHT, num_cols = 4, col_width = MENU_SWATCH_DEFAULT_COL_WIDTH, highlight_scale = 1, unhighlight_scale = 0.7}
	Vehicle_cust_menu[0].item_type = "tire"

	--	Initilaize the swatches
	local menu_item = Vehicle_cust_menu[0]
	menu_item.swatches = { }
	menu_item.swatches = { num_swatches = 0 }
	menu_item.cur_idx = 0

	-- Make the request to build the menu
	vint_dataresponder_request("vcust_populate_wheel_grid_menu", "vehicle_cust_populate_tire_menu", 0, 10) -- 10 = VCUST_INTF_POPULATE_TIRE_MENU

	local idx = menu_item.cur_idx
	menu_grid_show(menu_data, menu_item)

	vehicle_cust_build_footer(menu_data)

	local insert_values = { [0] = idx + 1, }
	local tire_name = vint_insert_values_in_string("VCUST_TIRE_TREAD_NUMBER", insert_values)
	vehicle_cust_update_footer_component(tire_name, menu_item.swatches[idx].price, menu_item.swatches[idx].owned)
	Vehicle_cust_menu.btn_tips = Vehicle_cust_btns
end

function vehicle_cust_populate_tire_menu(display_name, image_crc, price, current)
	local swatches = Vehicle_cust_menu[0].swatches
	swatches[swatches.num_swatches] = {	label = display_name, swatch_crc = image_crc, price = price, owned = false }

	if price == 0 then
		swatches[swatches.num_swatches].owned = true
	end

	if current == true then
		Vehicle_cust_menu[0].cur_idx = swatches.num_swatches
	end
	swatches.num_swatches = swatches.num_swatches + 1
end

-----------------------
-- Create Hubcap Menu
function vehicle_cust_build_hubcap_menu(menu_data)
	Vehicle_cust_menu = menu_data
	-- New menu, clear out all items
	Vehicle_cust_menu.num_items = 1
	Vehicle_cust_menu.header_label_crc = nil
	Vehicle_cust_menu.header_label_str = "VCUST_HUBCAPS_TITLE"
	Vehicle_cust_menu.on_back = vehicle_cust_revert_hubcaps
	Vehicle_cust_menu.on_post_show = vehicle_cust_finalize_footer
	Vehicle_cust_menu.footer_height = 40

	-- Create the grid
	Vehicle_cust_menu[0] = { label = "", type = MENU_ITEM_TYPE_GRID, on_select = vehicle_cust_preview_wheel_changes, on_nav = vehicle_cust_nav_new_hubcap,
									 row_height = MENU_SWATCH_DEFAULT_ROW_HEIGHT, num_cols = 4, col_width = MENU_SWATCH_DEFAULT_COL_WIDTH, highlight_scale = 1, unhighlight_scale = 0.7}
	Vehicle_cust_menu[0].item_type = "hubcap"

	--	Initilaize the swatches
	local menu_item = Vehicle_cust_menu[0]
	menu_item.swatches = { }
	menu_item.swatches = { num_swatches = 0 }
	menu_item.cur_idx = 0

	-- Make the request to build the menu
	vint_dataresponder_request("vcust_populate_wheel_grid_menu", "vehicle_cust_populate_hubcap_menu", 0, 11) -- 11 = VCUST_INTF_POPULATE_HUBCAP_MENU

	local idx = menu_item.cur_idx
	menu_grid_show(menu_data, menu_item)
	vehicle_cust_build_footer(menu_data)
	vehicle_cust_update_footer_component(menu_item.swatches[idx].label, menu_item.swatches[idx].price, menu_item.swatches[idx].owned)

	Vehicle_cust_menu.btn_tips = Vehicle_cust_btns
	btn_tips_update()
end

function vehicle_cust_populate_hubcap_menu(display_name, image_crc, price, current)
	local swatches = Vehicle_cust_menu[0].swatches

	swatches[swatches.num_swatches]	= { price = price, owned = false }

	if price == 0 then
		swatches[swatches.num_swatches].owned = true
	end

	if image_crc == 0 then
		swatches[swatches.num_swatches].swatch_str = "ui_menu_none"
		swatches[swatches.num_swatches].label = "COMPONENT_NONE"
	else
		swatches[swatches.num_swatches].swatch_crc = image_crc

		local insert_values = {  }
		if swatches[0].swatch_str == "ui_menu_none" then
			insert_values[0] = swatches.num_swatches
		else
			insert_values[0] = swatches.num_swatches + 1
		end

		swatches[swatches.num_swatches].label = vint_insert_values_in_string("VCUST_HUBCAP_NUMBER", insert_values)
	end

	if current == true then
		Vehicle_cust_menu[0].cur_idx = swatches.num_swatches
	end

	swatches.num_swatches = swatches.num_swatches + 1
end

-----------------------
-- Create Spinners Menu
function vehicle_cust_build_spinners_menu(menu_data)
	Vehicle_cust_menu = menu_data
	-- New menu, clear out all items
	Vehicle_cust_menu.num_items = 1
	Vehicle_cust_menu.header_label_crc = nil
	Vehicle_cust_menu.header_label_str = "VCUST_SPINNERS_TITLE"
	Vehicle_cust_menu.on_back = vehicle_cust_revert_spinners
	Vehicle_cust_menu.on_post_show = vehicle_cust_finalize_footer
	Vehicle_cust_menu.footer_height = 40

	-- Create the grid
	Vehicle_cust_menu[0] = { label = "", type = MENU_ITEM_TYPE_GRID, on_select = vehicle_cust_preview_wheel_changes, on_nav = vehicle_cust_nav_new_spinner,
									 row_height = MENU_SWATCH_DEFAULT_ROW_HEIGHT, num_cols = 4, col_width = MENU_SWATCH_DEFAULT_COL_WIDTH, highlight_scale = 1, unhighlight_scale = 0.7}
	Vehicle_cust_menu[0].item_type = "hubcap" -- Although these are spinners, you can't have both hubcaps and spinners

	--	Initilaize the swatches
	local menu_item = Vehicle_cust_menu[0]
	menu_item.swatches = { }
	menu_item.swatches = { num_swatches = 0 }
	menu_item.cur_idx = 0

	-- Make the request to build the menu
	vint_dataresponder_request("vcust_populate_wheel_grid_menu", "vehicle_cust_populate_spinners_menu", 0, 12) -- 12 = VCUST_INTF_POPULATE_SPINNERS_MENU

	local idx = menu_item.cur_idx
	menu_grid_show(menu_data, menu_item)

	vehicle_cust_build_footer(menu_data)
	vehicle_cust_update_footer_component(menu_item.swatches[idx].label, menu_item.swatches[idx].price, menu_item.swatches[idx].owned)
	Vehicle_cust_menu.btn_tips = Vehicle_cust_btns
end

function vehicle_cust_populate_spinners_menu(display_name, image_crc, price, current)
	local swatches = Vehicle_cust_menu[0].swatches

	swatches[swatches.num_swatches]	= { price = price, owned = false }

	if price == 0 then
		swatches[swatches.num_swatches].owned = true
	end

	if image_crc == 0 then
		swatches[swatches.num_swatches].swatch_str = "ui_menu_none"
		swatches[swatches.num_swatches].label = "COMPONENT_NONE"
	else

		swatches[swatches.num_swatches].swatch_crc = image_crc
		local insert_values = { }
		if swatches[0].label == "COMPONENT_NONE" then
			insert_values[0] = swatches.num_swatches
		else
			insert_values[0] = swatches.num_swatches + 1
		end

		swatches[swatches.num_swatches].label = vint_insert_values_in_string("VCUST_SPINNER_NUMBER", insert_values)
	end

	if current == true then
		Vehicle_cust_menu[0].cur_idx = swatches.num_swatches
	end



	swatches.num_swatches = swatches.num_swatches + 1
end

----------------------------
-- Preview Wheels as a whole
function vehicle_cust_preview_wheel_changes(menu_label, menu_data)
	local swatches = menu_data.swatches
	local idx = menu_data.cur_row * menu_data.num_cols + menu_data.cur_col
	if idx < swatches.num_swatches then
		if menu_data.item_type == "rim" then
			Vehicle_cust_rim_price = swatches[idx].price
		elseif menu_data.item_type == "tire" then
			Vehicle_cust_tire_price = swatches[idx].price
		elseif menu_data.item_type == "hubcap" then
			Vehicle_cust_hubcap_price = swatches[idx].price
		end
	end
	menu_show(Vehicle_cust_wheel_menu, MENU_TRANSITION_SWEEP_RIGHT)
end

-------------------------------
-- Purchase the wheels for real
function vehicle_cust_purchase_wheels(menu_label, menu_data)
	if Vehicle_cust_wheel_price == 0 then
		vcust_purchase_wheels(Vehicle_cust_wheel_price)
		menu_show(Vehicle_cust_axle_menu.parent_menu, MENU_TRANSITION_SWEEP_LEFT)
	elseif Style_cluster_player_cash >= Vehicle_cust_wheel_price then -- Confirm the purchase if we can afford it
		Vehicle_cust_style_to_award = Vehicle_cust_wheel_price

		local insert = { [0] = format_cash(Vehicle_cust_wheel_price) }
		local body = vint_insert_values_in_string("VCUST_PURCHASE_WHEELS_PROMPT", insert)
		local heading = "MENU_TITLE_CONFIRM"
		dialog_box_confirmation(heading, body, "vehicle_cust_purchase_wheels_confirm")
	else
		dialog_box_message("MENU_TITLE_NOTICE", "HUD_SHOP_INSUFFICIENT_FUNDS")
	end
end


-- Make the purchase for realz
function vehicle_cust_purchase_wheels_confirm(result, action)
	if action ~= DIALOG_ACTION_CLOSE then
		return
	end

	if result == 0 then
		if Vehicle_cust_style_to_award ~= 0 then
			award_style("veh_comp", Vehicle_cust_style_to_award)
		end

		Vehicle_cust_rim_price = 0
		Vehicle_cust_tire_price	= 0
		Vehicle_cust_hubcap_price = 0

		vcust_purchase_wheels(Vehicle_cust_wheel_price)
		audio_play(Menu_sound_purchase)
		menu_show(Vehicle_cust_axle_menu.parent_menu, MENU_TRANSITION_SWEEP_LEFT)
	end
end

-----------------------
-- Get/Show each menu
function vehicle_cust_get_rims(menu_label, menu_data)
	Vehicle_cust_menu_c.parent_menu = Menu_active
	Vehicle_cust_menu_c.on_show = vehicle_cust_build_rim_menu
	Vehicle_cust_menu_c.on_nav = nil
	Vehicle_cust_menu_c.on_post_show = nil
	Vehicle_cust_menu_c.footer_height = 0

	menu_show(Vehicle_cust_menu_c, MENU_TRANSITION_SWEEP_LEFT)
end

function vehicle_cust_get_rim_grid(menu_label, menu_data)
	Vehicle_cust_menu_d.parent_menu = Vehicle_cust_menu_c
	Vehicle_cust_menu_d.on_show = vehicle_cust_build_rim_grid
	Vehicle_cust_menu_d.footer_height = 40
	Vehicle_cust_menu_d.on_nav = nil

	Vehicle_cust_rim_family =	menu_data.id
	Vehicle_cust_rim_index = Vehicle_cust_menu.highlighted_item
	if Vehicle_cust_current_peg ~= "" then
		peg_unload(Vehicle_cust_current_peg)
		Vehicle_cust_current_peg = ""
	end
	Vehicle_cust_current_peg = VEHICLE_CUST_RIM_PEG .. Vehicle_cust_rim_family + 1
	peg_load(Vehicle_cust_current_peg)
	menu_show(Vehicle_cust_menu_d, MENU_TRANSITION_SWEEP_LEFT)
end

function vehicle_cust_get_tires(menu_label, menu_data)
	Vehicle_cust_menu_d.parent_menu = Menu_active
	Vehicle_cust_menu_d.on_show = vehicle_cust_build_tire_menu
	Vehicle_cust_menu_d.on_nav = vehicle_cust_nav_new_tire

	if Vehicle_cust_current_peg ~= "" then
		peg_unload(Vehicle_cust_current_peg)
		Vehicle_cust_current_peg = ""
	end
	Vehicle_cust_current_peg = VEHICLE_CUST_TIRE_PEG
	peg_load(Vehicle_cust_current_peg)

	menu_show(Vehicle_cust_menu_d, MENU_TRANSITION_SWEEP_LEFT)
end

function vehicle_cust_get_hubcaps(menu_label, menu_data)
	Vehicle_cust_menu_d.parent_menu = Menu_active
	Vehicle_cust_menu_d.on_show = vehicle_cust_build_hubcap_menu
	Vehicle_cust_menu_d.on_nav = vehicle_cust_nav_new_hubcap

	if Vehicle_cust_current_peg ~= "" then
		peg_unload(Vehicle_cust_current_peg)
		Vehicle_cust_current_peg = ""
	end
	Vehicle_cust_current_peg = VEHICLE_CUST_HUBCAP_PEG
	peg_load(Vehicle_cust_current_peg)

	menu_show(Vehicle_cust_menu_d, MENU_TRANSITION_SWEEP_LEFT)
end

function vehicle_cust_get_spinners(menu_label, menu_data)
	Vehicle_cust_menu_d.parent_menu = Menu_active
	Vehicle_cust_menu_d.on_show = vehicle_cust_build_spinners_menu
	Vehicle_cust_menu_d.on_nav = vehicle_cust_nav_new_spinner

	if Vehicle_cust_current_peg ~= "" then
		peg_unload(Vehicle_cust_current_peg)
		Vehicle_cust_current_peg = ""
	end

	Vehicle_cust_current_peg = VEHICLE_CUST_SPINNER_PEG .. Vehicle_cust_rim_family + 1
	peg_load(Vehicle_cust_current_peg)

	menu_show(Vehicle_cust_menu_d, MENU_TRANSITION_SWEEP_LEFT)
end

-----------------------
-- Preview wheel choices
function vehicle_cust_nav_new_rim(menu_label, menu_data)
	local swatches = menu_data.swatches
	local idx = menu_data.cur_row * menu_data.num_cols + menu_data.cur_col
	if idx < swatches.num_swatches then
		local insert_values = { [0] = idx + 1, }
		local rim_name = vint_insert_values_in_string("VCUST_RIM_NUMBER", insert_values)
		vehicle_cust_update_footer_component(rim_name, swatches[idx].price, swatches[idx].owned)
		vcust_preview_component(2, 0, Vehicle_cust_rim_index, idx)
	end
end

function vehicle_cust_nav_new_tire(menu_label, menu_data)
	local swatches = menu_data.swatches
	local idx = menu_data.cur_row * menu_data.num_cols + menu_data.cur_col
	if idx < swatches.num_swatches then
		vcust_preview_component(2, 1, idx)
		local insert_values = { [0] = idx + 1, }
		local tire_name = vint_insert_values_in_string("VCUST_TIRE_TREAD_NUMBER", insert_values)
		vehicle_cust_update_footer_component(tire_name, swatches[idx].price, swatches[idx].owned)
	end
end

function vehicle_cust_nav_new_hubcap(menu_label, menu_data)
	local swatches = menu_data.swatches
	local idx = menu_data.cur_row * menu_data.num_cols + menu_data.cur_col
	if idx < swatches.num_swatches then
		vcust_preview_component(2, 2, idx)
		vehicle_cust_update_footer_component(swatches[idx].label, swatches[idx].price, swatches[idx].owned)
	end
end

function vehicle_cust_nav_new_spinner(menu_label, menu_data)
	local swatches = menu_data.swatches
	local idx = menu_data.cur_row * menu_data.num_cols + menu_data.cur_col
	if idx < swatches.num_swatches then
		vcust_preview_component(2, 3, idx)
		vehicle_cust_update_footer_component(swatches[idx].label, swatches[idx].price, swatches[idx].owned)
	end
end

-----------------------
-- Revert wheel choices
function vehicle_cust_revert_rims(menu_data)
	vcust_revert_wheel_choice(0)
	menu_show(Menu_active.parent_menu, MENU_TRANSITION_SWEEP_RIGHT)
	audio_play(Menu_sound_back)
end

function vehicle_cust_revert_tires(menu_data)
	vcust_revert_wheel_choice(1)
	menu_show(Menu_active.parent_menu, MENU_TRANSITION_SWEEP_RIGHT)
	audio_play(Menu_sound_back)
end

function vehicle_cust_revert_hubcaps(menu_data)
	vcust_revert_wheel_choice(2)
	menu_show(Menu_active.parent_menu, MENU_TRANSITION_SWEEP_RIGHT)
	audio_play(Menu_sound_back)
end

function vehicle_cust_revert_spinners(menu_data)
	vcust_revert_wheel_choice(3)
	menu_show(Menu_active.parent_menu, MENU_TRANSITION_SWEEP_RIGHT)
	audio_play(Menu_sound_back)
end

---------------
-- MENU DATA --
---------------
Vehicle_cust_btns = {
	a_button 	= 	{ label = "CONTROL_SELECT", 	enabled = btn_tips_default_a, },
	b_button 	= 	{ label = "MENU_BACK", 		enabled = btn_tips_default_a, },
	right_stick =  	{ label = "CONTROL_ZOOM_AND_ROTATE", 	enabled = true },
}

Vehicle_cust_btns_top = {
	a_button 	= 	{ label = "CONTROL_SELECT", 	enabled = btn_tips_default_a, },
	b_button 	= 	{ label = "CONTROL_RESUME", 	enabled = btn_tips_default_a, },
	right_stick =  	{ label = "CONTROL_ZOOM_AND_ROTATE", 	enabled = true },
}
-------[ Menus ]-------
Vehicle_cust_menu_a = {
	on_show = vehicle_cust_build_menu,
	on_back = vehicle_cust_exit,
}

Vehicle_cust_menu_b = {
	on_show = vehicle_cust_build_menu,
	on_back = vehicle_cust_exit,
}

Vehicle_cust_menu_c = {
	on_release = vehicle_cust_release,

}

Vehicle_cust_menu_d = {
	on_release = vehicle_cust_release,
}

Vehicle_cust_region_menu = {
	on_release = vehicle_cust_release,

}
----[ Wheel Menus ]----
rim_size_text_slider	=	{ num_values = 0, cur_value = 0, }
wheel_size_text_slider	= 	{ num_values = 0, cur_value = 0, }
wheel_width_text_slider	=	{ num_values = 0, cur_value = 0, }


Vehicle_cust_wheel_menu = {
	header_label_str = "VCUST_WHEELS_TITLE",
	on_show = vehicle_cust_build_wheel_menu,
	on_back = vehicle_cust_revert_wheels,
	on_release = vehicle_cust_release,
	on_post_show = vehicle_cust_finalize_footer,

	num_items = 8,
	[0] = { label="VCUST_RIM_STYLE_OPTION", type=MENU_ITEM_TYPE_INFO_BOX, on_select = vehicle_cust_get_rims, info_text_str = "temp" },
	[1] = { label="VCUST_TIRE_TREAD_OPTION", type=MENU_ITEM_TYPE_INFO_BOX, on_select = vehicle_cust_get_tires, info_text_str = "temp" },
	[2] = { label="VCUST_HUBCAP_OPTION", type=MENU_ITEM_TYPE_INFO_BOX, on_select = vehicle_cust_get_hubcaps, info_text_str = "temp" },
	[3] = { label="VCUST_SPINNER_OPTION", type=MENU_ITEM_TYPE_INFO_BOX, on_select = vehicle_cust_get_spinners, info_text_str = "temp" },
	[4] = { label="VCUST_RIM_SIZE_OPTION", type=MENU_ITEM_TYPE_TEXT_SLIDER, text_slider_values = rim_size_text_slider, on_value_update = vehicle_cust_rim_profile_update},
	[5] = { label="VCUST_WHEEL_SIZE_OPTION", type=MENU_ITEM_TYPE_TEXT_SLIDER, text_slider_values = wheel_size_text_slider, on_value_update = vehicle_cust_wheel_size_update}, -- on_select
	[6] = { label="VCUST_WHEEL_WIDTH_OPTION", type=MENU_ITEM_TYPE_TEXT_SLIDER, text_slider_values = wheel_width_text_slider, on_value_update = vehicle_cust_wheel_width_update}, -- on_select
	[7] = { label="VCUST_PURCHASE_OPTION", type=MENU_ITEM_TYPE_SELECTABLE, on_select = vehicle_cust_purchase_wheels },

	footer_height = 40,
}

Vehicle_cust_axle_menu = {
	header_label_str = "VCUST_AXLES_TITLE",
	num_items = 3,
	on_show = vehicle_cust_reset_wheels,

	[0] = { label="VCUST_BOTH_AXLES_OPTION", type=MENU_ITEM_TYPE_SUB_MENU, sub_menu = Vehicle_cust_wheel_menu, on_select = vehicle_cust_select_axle },
	[1] = { label="VCUST_FRONT_AXLE_OPTION", type=MENU_ITEM_TYPE_SUB_MENU, sub_menu = Vehicle_cust_wheel_menu, on_select = vehicle_cust_select_axle },
	[2] = { label="VCUST_REAR_AXLE_OPTION" , type=MENU_ITEM_TYPE_SUB_MENU, sub_menu = Vehicle_cust_wheel_menu, on_select = vehicle_cust_select_axle },

	btn_tips = Vehicle_cust_btns,
}

----[ Color Menus ]----
Vehicle_cust_color_palette = {
	header_label_str = "VCUST_COLOR_PALETTE_TITLE",
	on_show = vehicle_cust_build_palette,
	on_back = vehicle_cust_return_palette,
	on_post_show = vehicle_cust_finalize_footer,
	on_release = vehicle_cust_release,
	num_items = 1,
	[0] = { label = "", type = MENU_ITEM_TYPE_GRID, on_select = vehicle_cust_select_color_grid, on_nav = vehicle_cust_nav_new_palette,
		update_swatch=vehicle_cust_update_palette_swatch, row_height = 50, num_cols = 6, col_width = 64, highlight_scale = 1, unhighlight_scale = 0.77},

	footer_height = 40,
	btn_tips = Vehicle_cust_btns,
}

Vehicle_cust_color_select_menu = {
	header_label_str = "VCUST_COLOR_GRID_TITLE",
	on_show = vehicle_cust_build_color_grid,
	on_back = vcehicle_cust_revert_color,
	on_release = vehicle_cust_color_select_release,
	on_post_show = vehicle_cust_finalize_footer,

	num_items = 1,
	[0] = { label = "", type = MENU_ITEM_TYPE_GRID, on_select = vehicle_cust_select_color, on_nav = vehicle_cust_nav_new_color,
		update_swatch=vehicle_cust_update_palette_swatch, row_height = 56, num_cols = 6, col_width = 59, highlight_scale = 1, unhighlight_scale = 0.7},

	footer_height = 40,
	btn_tips = Vehicle_cust_btns,
}

-----[ Horizontal Menu ]------
Vehicle_cust_horz_menu = {
	current_selection = 0,
	num_items = 0,
	on_nav = vehicle_cust_nav_horz_menu,
}

-----[ Specifics ]-----
Vehicle_cust_menu_ops = {
	num_ops = 7,
	--	VCUST_INTF_TYPE_CATEGORY
	[0] = { on_select = vehicle_cust_select_category, type = MENU_ITEM_TYPE_SUB_MENU , sub_menu = Vehicle_cust_menu_c },
	-- VCUST_INTF_TYPE_SLOT
	[1] = { on_nav = vehicle_cust_nav_slot, on_select = vehicle_cust_select_slot, type = MENU_ITEM_TYPE_SUB_MENU, sub_menu = Vehicle_cust_menu_c },
	-- VCUST_INTF_TYPE_COMPONENT
	[2] = { on_select = vehicle_cust_select_component , type = VEHICLE_COMPONENT_LINE, sub_menu = Vehicle_cust_menu_c },
	-- VCUST_INTF_TYPE_COLOR_REGION
	[3] = { on_nav = vehicle_cust_nav_slot, on_select = vehicle_cust_select_region, type = MENU_ITEM_TYPE_SUB_MENU , sub_menu = Vehicle_cust_region_menu },
	-- VCUST_INTF_TYPE_COLOR_PALETTE
	[4] = { on_select = vehicle_cust_select_advanced_region, type = MENU_ITEM_TYPE_SUB_MENU , sub_menu = Vehicle_cust_color_palette },
	--	VCUST_INTF_TYPE_COLOR_GRID
	[5] = { on_select = nil, type = MENU_ITEM_TYPE_SUB_MENU , sub_menu = Vehicle_cust_color_select_menu},
	-- VCUST_INTF_TYPE_WHEEL
	[6] = { on_select = nil, type = MENU_ITEM_TYPE_SUB_MENU, sub_menu = Vehicle_cust_axle_menu},

}

Vehicle_menu_controls = {
	[VEHICLE_COMPONENT_LINE] = {
		on_show 		=	vehicle_component_line_on_show,
		on_select 		=	menu_control_on_select,
		on_nav_up		=	vehicle_component_line_nav_up,
		on_nav_down		=	vehicle_component_line_nav_down,
		on_release		=  vehicle_component_line_on_release,
		get_width		=	vehicle_component_line_get_width,
--		get_height	=	vehicle_component_line_get_height,
	},
}
