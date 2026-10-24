-- gang_cust.lua: Gang Customization menu

------------------------
-- Gang Customization --
------------------------

-- List of gang vehicles wanted by Chop Shop [nclok1405]
CARS_WANTED_BY_CHOPSHOP = {
	"Betsy",
	"Compton",
	"Cosmos",
	"Go!",
	"Voyage",
	"Magma",
	"Mockingbird",
	"Hammerhead",
	"Venom Classic",
	"Attrazione",
	"Bezier",
	"Bulldog",
	"Justice",
	"Superiore",
	"Cruiser",
	"Quota",
	"Status Quo",
}

-- Vehicle Slot Text [nclok1405]
Gang_cust_string_slot1 = vint_insert_values_in_string("{0} 1", {[0] = "VEHICLE_TYPE_TITLE"})
Gang_cust_string_slot2 = vint_insert_values_in_string("{0} 2", {[0] = "VEHICLE_TYPE_TITLE"})
Gang_cust_string_slot3 = vint_insert_values_in_string("{0} 3", {[0] = "VEHICLE_TYPE_TITLE"})

-- "global" variables

--	Menu stuff
Gang_menu_add_index = 0
-- Tag stuff
Gang_tag_icon_pegs = { }
Gang_tag_icon_count = 0
Gang_tag_preview_peg = ""
Gang_tag_preview_h = 0
--	Sign Stuff
Gang_signs_number_of_signs = 0
--	Vehicle stuff
Vehicle_slot = 0

Gang_cust_is_fully_loaded = true

----------------------
--	SYSTEM FUNCTIONS --
----------------------
--[ INITIALIZE AND SHUTDOWN ]--
-------------------------------
--	Initialize the menu
function gang_cust_init()
	--Event Tracking
	event_tracking_interface_enter("Gang Customization")

	menu_init()
	--menu_horz_init(Gang_cust_horz_menu)
	peg_load("ui_spinner_lg")

	Gang_tag_preview_h = vint_object_find("gang_tag_large_preview")

	--	Load the tag icons
	gang_cust_gang_tag_init_swatches()

	local cash_style_grp_h = vint_object_find("cash_style_cluster", nil, MENU_BASE_DOC_HANDLE)
	vint_set_property(cash_style_grp_h, "visible", false)

	vint_datagroup_add_subscription("gang_cust_current_object_is_loaded", "insert", "gang_cust_current_object_update")
	vint_datagroup_add_subscription("gang_cust_current_object_is_loaded", "update", "gang_cust_current_object_update")

	menu_show(Gang_cust_gang_menu)
end

-- Shutdown and cleanup the menu
function gang_cust_cleanup()
	peg_unload("ui_spinner_lg")

	if Gang_tag_preview_peg ~= nil then
		peg_unload(Gang_tag_preview_peg)
	end
end

--[ EXIT ]--
------------
function gang_cust_exit(menu_data)
	local body = "GANG_CUST_EXIT_PROMPT"
	local heading = "MENU_TITLE_WARNING"
	local options = { [0] = "OPTION_YES", [1] = "OPTION_NO"	}

	--dialog_box_open(heading, body, options, "gang_cust_exit_confirm", 0)
	-- Exit without dialog [nclok1405]
	menu_close(gang_cust_exit_final)
	local loading_image = vint_object_find("gang_cust_loading_image")
	vint_set_property(loading_image, "visible", false)
end

function gang_cust_exit_confirm(result, action)
	if action ~= DIALOG_ACTION_CLOSE then
		return
	end

	if result == 0 then
		menu_close(gang_cust_exit_final)
		local loading_image = vint_object_find("gang_cust_loading_image")
		vint_set_property(loading_image, "visible", false)
	end
end
function gang_cust_exit_final()
	gang_cust_gang_tag_cleanup_swatches()
	vint_document_unload(vint_document_find("gang_cust"))
end

------------------------
--	MENU FUNCTIONALITY --
------------------------
---[ GANG MENU ]---
-------------------
function gang_cust_gang_nav(menu_data)
	local selection = Gang_cust_gang_menu.highlighted_item

	if selection == 0 or selection == 1 then
		-- Style or Sign
		if Gang_tag_preview_peg ~= "" then
			vint_set_property(Gang_tag_preview_h, "visible", false)
			peg_unload(Gang_tag_preview_peg)
			Gang_tag_preview_peg = ""
		end
		gang_customization_show_gang()
	elseif selection == 2 then
		-- Tag
		vint_dataresponder_request("gang_cust_tag_data_responder", "gang_cust_gang_tag_get_current", 0, 1) -- 1 - get default
		vint_set_property(Gang_tag_preview_h, "visible", true)
		gang_customization_show_tag()
	else
		-- Vehicles
		if Gang_tag_preview_peg ~= "" then
			vint_set_property(Gang_tag_preview_h, "visible", false)
			peg_unload(Gang_tag_preview_peg)
			Gang_tag_preview_peg = ""
		end

		Vehicle_slot = selection - 3
		gang_customization_show_vehicle(Vehicle_slot)
	end
end

function gang_cust_gang_show(menu_data)
	gang_cust_gang_nav(menu_data)
	btn_tips_footer_attach(menu_data)	-- Footer [nclok1405]
end

-------------
--	Gang Style
function gang_cust_gang_style_build_menu(menu_data)
	Gang_menu_add_index = 0
 	Gang_cust_gang_style_menu.highlighted_item = Gang_menu_add_index
	vint_dataresponder_request("gang_cust_gang_style_data_responder", "gang_cust_gang_style_add_items", 0)
	Gang_cust_gang_style_menu.num_items = Gang_menu_add_index

	btn_tips_footer_attach(menu_data)	-- Footer [nclok1405]
end

function gang_cust_gang_style_add_items(name, is_current_gang)
	Gang_cust_gang_style_menu[Gang_menu_add_index] =
		{	label = name, type = MENU_ITEM_TYPE_SELECTABLE, on_select = gang_cust_gang_style_confirm_selection }
	if is_current_gang == true then
		Gang_cust_gang_style_menu.highlighted_item = Gang_menu_add_index
	end
	Gang_menu_add_index = Gang_menu_add_index + 1
end

function gang_cust_gang_style_select_new_gang()
	gang_customization_select_gang_style(Gang_cust_gang_style_menu.highlighted_item)
end

function gang_cust_gang_style_confirm_selection()
	menu_show(Gang_cust_gang_menu, MENU_TRANSITION_SWEEP_RIGHT)
end

function gang_cust_gang_style_revert_selection()
	gang_customization_revert_to_old_gang()
	menu_show(Menu_active.parent_menu, MENU_TRANSITION_SWEEP_RIGHT)
end

------------
--	Gang Tags
function gang_cust_gang_tag_build_menu(menu_data)
	local menu_item = Gang_cust_tag_menu[0]
	menu_item.swatches = { num_swatches = 0 }
	menu_item.cur_idx = 0
	Gang_menu_add_index = 0

	-- Add the swatches
	vint_dataresponder_request("gang_cust_tag_data_responder", "gang_cust_gang_tag_add_items"	, 0)

	menu_item.swatches.num_swatches = Gang_menu_add_index
	local master_swatch = vint_object_find("swatch_skin", nil, MENU_BASE_DOC_HANDLE)
	menu_grid_show(menu_data, menu_item, master_swatch)

	btn_tips_footer_attach(menu_data)	-- Footer [nclok1405]
end

function gang_cust_gang_tag_init_swatches()
	peg_load("ui_gang_tags")
end

function gang_cust_gang_tag_cleanup_swatches()
	peg_unload("ui_gang_tags")
end

function gang_cust_gang_tag_get_current(name_str, icon_name, preview_image_peg, preview_image, current)
		if Gang_tag_preview_peg == preview_image_peg then
			vint_set_property(Gang_tag_preview_h, "image", preview_image .. ".tga")
			return
		end
		if Gang_tag_preview_peg ~= "" then
			peg_unload(Gang_tag_preview_peg)
		end
		Gang_tag_preview_peg = preview_image_peg
		peg_load(Gang_tag_preview_peg)
		vint_set_property(Gang_tag_preview_h, "image", preview_image .. ".tga")
		vint_set_property(Gang_tag_preview_h, "scale", 1.25, 1.25)
end

function gang_cust_gang_tag_add_items(name_str, icon_name, preview_image_peg, preview_image, current)
	local swatches = Gang_cust_tag_menu[0].swatches
	swatches[Gang_menu_add_index] = {
		label = name_str, swatch_str = icon_name, preview_peg_str = preview_image_peg, preview_str = preview_image
	}
	if current == true then
		Gang_cust_tag_menu[0].cur_idx = Gang_menu_add_index
	end

	Gang_menu_add_index = Gang_menu_add_index + 1
end

function gang_cust_gang_tag_select_new_tag(menu_label, menu_data)
	--	Update the tag displayed
	local swatches = menu_data.swatches
	local idx = menu_data.cur_row * menu_data.num_cols + menu_data.cur_col

	if idx < swatches.num_swatches then
		if Gang_tag_preview_peg ~= "" then
			peg_unload(Gang_tag_preview_peg)
			Gang_tag_preview_peg = ""
		end

		Gang_tag_preview_peg = swatches[idx].preview_peg_str
		peg_load(Gang_tag_preview_peg)
		gang_customization_change_tag()
		--	Update the bitmap
		vint_set_property(Gang_tag_preview_h, "image", swatches[idx].preview_str .. ".tga")
		vint_set_property(Gang_tag_preview_h, "visible", true)
	end
	vint_set_property(Gang_tag_preview_h, "scale", 1.25, 1.25)
end

function gang_cust_gang_tag_confirm_selection(menu_label, menu_data)
	local swatches = menu_data.swatches
	local idx = menu_data.cur_row * menu_data.num_cols + menu_data.cur_col

	if idx < swatches.num_swatches then
		gang_customization_select_gang_tag(idx)
	end

	menu_show(Gang_cust_gang_menu, MENU_TRANSITION_SWEEP_RIGHT)
	vint_set_property(Gang_tag_preview_h, "scale", 1.25, 1.25)
end

function gang_cust_gang_tag_revert_selection()
	gang_customization_revert_gang_tag()
	menu_show(Menu_active.parent_menu, MENU_TRANSITION_SWEEP_RIGHT)
end

function gang_cust_gang_tag_release()
	menu_grid_release(Gang_cust_tag_menu[0])

end

-------------
--	Gang Signs
function gang_cust_gang_sign_build_menu(menu_data)
 	Gang_cust_gang_style_menu.highlighted_item = 0
	Gang_signs_number_of_signs = 0
	Gang_cust_gang_sign_menu.num_items = 0
	vint_dataresponder_request("gang_cust_gang_sign_data_responder", "gang_cust_gang_sign_add_items", 0)

	btn_tips_footer_attach(menu_data)	-- Footer [nclok1405]
end

function gang_cust_gang_sign_add_items(sign_type, name, is_current)
	if sign_type == 0 then
		Gang_cust_gang_sign_menu[Gang_signs_number_of_signs] =
			{	label = name, type = MENU_ITEM_TYPE_SELECTABLE, on_select = gang_cust_gang_sign_confirm_selection }
		if is_current == true then
			Gang_cust_gang_sign_menu.highlighted_item = Gang_signs_number_of_signs
		end
		Gang_signs_number_of_signs = Gang_signs_number_of_signs + 1
		Gang_cust_gang_sign_menu.num_items = Gang_signs_number_of_signs
	end
end

function gang_cust_gang_sign_update_pose(menu_label, menu_data)
	gang_customization_select_gang_sign(0, Gang_cust_gang_sign_menu.highlighted_item)
end

function gang_cust_gang_sign_nav()
	if Gang_cust_gang_sign_menu.highlighted_item == 0 then
		gang_cust_gang_sign_update_pose(nil, Gang_cust_gang_sign_menu[0])
	end
end

function gang_cust_gang_sign_confirm_selection(menu_label, menu_data)
	local idx = Gang_cust_gang_sign_menu.highlighted_item

	gang_customization_confirm_gang_sign(idx)
	 menu_show(Menu_active.parent_menu, MENU_TRANSITION_SWEEP_RIGHT)
	--menu_show(Gang_cust_gang_menu, MENU_TRANSITION_SWEEP_RIGHT)
	--vint_set_property(Gang_tag_preview_h, "scale", 1.25, 1.25)

end

function gang_cust_gang_revert_selection()
	gang_customization_revert_gang_sign()
	menu_show(Menu_active.parent_menu, MENU_TRANSITION_SWEEP_RIGHT)
end

--[ VEHICLE MENU ]--
--------------------
function gang_cust_vehicle_select_slot()
	Vehicle_slot = Gang_cust_gang_menu.highlighted_item - 3
	gang_customization_show_vehicle(Vehicle_slot)
end

function gang_cust_vehicle_select_new_vehicle()
	gang_customization_select_vehicle(Gang_cust_vehicle_submenu.highlighted_item, Vehicle_slot)
end

function gang_cust_vehicle_revert_selection()
	gang_customization_revert_vehicle(Vehicle_slot)
	menu_show(Menu_active.parent_menu, MENU_TRANSITION_SWEEP_RIGHT)
end

function gang_cust_vehicle_confirm_selection()
	gang_customization_confirm_vehicle(Vehicle_slot)
	menu_show(Menu_active.parent_menu, MENU_TRANSITION_SWEEP_RIGHT)
end

function gang_cust_vehicle_build_submenu(menu_data)
	if Vehicle_slot == 0 then
		Gang_cust_vehicle_submenu.header_label_str = Gang_cust_string_slot1
	elseif Vehicle_slot == 1 then
		Gang_cust_vehicle_submenu.header_label_str = Gang_cust_string_slot2
	elseif Vehicle_slot == 2 then
		Gang_cust_vehicle_submenu.header_label_str = Gang_cust_string_slot3
	end

	Gang_menu_add_index = 0
	Gang_cust_vehicle_submenu.highlighted_item = Gang_menu_add_index
	vint_dataresponder_request("gang_cust_vehicle_data_responder", "gang_cust_vehicle_add_items", 0, Vehicle_slot)
	Gang_cust_vehicle_submenu.num_items = Gang_menu_add_index

	btn_tips_footer_attach(menu_data)	-- Footer [nclok1405]
end

-- Returns true if the specified vehicle is wanted by a Chop Shop [nclok1405]
function gang_cust_check_vehicle_wanted_by_chopshop(name)
	for k, chop_shop_car_name in pairs(CARS_WANTED_BY_CHOPSHOP) do
		if sui_compare_string(name, chop_shop_car_name) then
			return true
		end
	end
	return false
end

function gang_cust_vehicle_add_items(name, is_vehicle_in_slot)
	-- Check if the vehicle is wanted by a Chop Shop, and change the font color if so [nclok1405]
	local vehicle_is_wanted_by_chopshop = gang_cust_check_vehicle_wanted_by_chopshop(name)
	local vehicle_label = name
	if vehicle_is_wanted_by_chopshop then
		vehicle_label = vint_insert_values_in_string("[format][color:cyan]{0}[/format]", {[0] = name})
	end

	Gang_cust_vehicle_submenu[Gang_menu_add_index] = { label = vehicle_label, type = MENU_ITEM_TYPE_SELECTABLE, on_select=gang_cust_vehicle_confirm_selection }
	if is_vehicle_in_slot == true then 	--	Select the current level
		Gang_cust_vehicle_submenu.highlighted_item = Gang_menu_add_index
	end
	Gang_menu_add_index = Gang_menu_add_index + 1
end

function gang_cust_show_vehicle()
	if Gang_tag_preview_peg ~= "" then
		peg_unload(Gang_tag_preview_peg)
		Gang_tag_preview_peg = ""
		vint_set_property(Gang_tag_preview_h, "visible", false)
	end

	gang_customization_show_vehicle(Vehicle_slot)
end


function gang_cust_current_object_update(di_h)
	local is_loaded  = vint_dataitem_get(di_h)
	if Gang_cust_is_fully_loaded ~= is_loaded then
		local loading_image = vint_object_find("gang_cust_loading_image")
		--debug_print("freese","loading_image = " .. loading_image .. ".\n")
		if is_loaded == true then
			vint_set_property(loading_image, "visible", false)
		else
			vint_set_property(loading_image, "visible", true)
		end
		Gang_cust_is_fully_loaded = is_loaded
	end
end

---------------
-- MENU DATA --
---------------

----[ Button Tips for the Menus ]----
Gang_Customization_main_menu_btn_tips = {
	a_button 	= 	{ label = "CONTROL_SELECT", 	enabled = btn_tips_default_a, },
	b_button 	= 	{ label = "CONTROL_RESUME", 			enabled = btn_tips_default_a, },
}

----[ Button Tips for the Menus ]----
Gang_Customization_sub_menu_btn_tips = {
	a_button 	= 	{ label = "CONTROL_SELECT", 	enabled = btn_tips_default_a, },
	b_button 	= 	{ label = "CONTROL_BACK", 			enabled = btn_tips_default_a, },
}


---[ GANG MENU ]---

-- Submenus
Gang_cust_gang_style_menu = {
	header_label_str = "GANG_CUST_GANG_STYLE_TITLE",
	on_show 			= gang_cust_gang_style_build_menu,
	on_nav  			= gang_cust_gang_style_select_new_gang,
	on_back				= gang_cust_gang_style_revert_selection,

	btn_tips 			= Gang_Customization_sub_menu_btn_tips,
}

Gang_cust_tag_menu = {
	header_label_str = "GANG_CUST_GANG_TAG_TITLE",
	on_show 		= gang_cust_gang_tag_build_menu,
	on_release	= gang_cust_gang_tag_release,
	on_back 		= gang_cust_gang_tag_revert_selection,
	num_items	= 1,

	[0] = { label = "", type = MENU_ITEM_TYPE_GRID, on_select = gang_cust_gang_tag_confirm_selection, on_nav = gang_cust_gang_tag_select_new_tag,
		row_height = 72, num_cols = 4, col_width = 83, highlight_scale = 1, unhighlight_scale = 0.8},

	btn_tips 			= Gang_Customization_sub_menu_btn_tips,
}

Gang_cust_gang_sign_menu = {
	header_label_str = "GANG_CUST_GANG_SIGN_TITLE",
	max_height = 535,	-- Default: 375 [nclok1405]
	on_show 	= gang_cust_gang_sign_build_menu,
	on_nav 		= gang_cust_gang_sign_update_pose,
	on_back 	= gang_cust_gang_revert_selection,
--	on_nav	 = gang_cust_gang_sign_nav,

	btn_tips 	= Gang_Customization_sub_menu_btn_tips,
}

-- Vehicle Sub Menu
Gang_cust_vehicle_submenu = {
	header_label_str = "VEHICLE_TYPE_TITLE",
	max_height = 535,	-- Default: 375 [nclok1405]
	on_show 		= gang_cust_vehicle_build_submenu,
	on_nav 			= gang_cust_vehicle_select_new_vehicle,
	on_back 		= gang_cust_vehicle_revert_selection,
	btn_tips 			= Gang_Customization_sub_menu_btn_tips,
}

-- Top Level Menu
Gang_cust_gang_menu = {
	header_label_str = "GANG_CUST_TITLE",
	highlighted_item = 0,
	on_show = gang_cust_gang_show,
	on_nav  = gang_cust_gang_nav,
	on_back = gang_cust_exit,
	num_items = 6,

	[0] =	{ label = "GANG_CUST_GANG_STYLE_OPT", 	type = MENU_ITEM_TYPE_SUB_MENU, sub_menu = Gang_cust_gang_style_menu, },
	[1] = { label = "GANG_CUST_GANG_SIGN_OPT",	type = MENU_ITEM_TYPE_SUB_MENU, sub_menu = Gang_cust_gang_sign_menu,  },
	[2] = { label = "GANG_CUST_GANG_TAG_OPT",	 	type = MENU_ITEM_TYPE_SUB_MENU, sub_menu = Gang_cust_tag_menu,			 },
	[3] = { label = Gang_cust_string_slot1, type = MENU_ITEM_TYPE_SUB_MENU, sub_menu = Gang_cust_vehicle_submenu },
	[4] = { label = Gang_cust_string_slot2, type = MENU_ITEM_TYPE_SUB_MENU, sub_menu = Gang_cust_vehicle_submenu },
	[5] = { label = Gang_cust_string_slot3, type = MENU_ITEM_TYPE_SUB_MENU, sub_menu = Gang_cust_vehicle_submenu },

	btn_tips 			= Gang_Customization_main_menu_btn_tips,
}

--[ VEHICLE MENU ]--
--------------------

--Top Level Menu
--[[
Gang_cust_vehicle_menu = {
	header_label_str = "VEHICLE_CUSTOMIZATION_TITLE",
	on_show 	= gang_cust_show_vehicle,
	on_back 	= gang_cust_exit,
	on_nav 	= gang_cust_vehicle_select_slot,
	num_items = 3,

	[0] = { label = "GANG_CUST_SLOT_1", type = MENU_ITEM_TYPE_SUB_MENU, sub_menu = Gang_cust_vehicle_submenu },
	[1] = { label = "GANG_CUST_SLOT_2", type = MENU_ITEM_TYPE_SUB_MENU, sub_menu = Gang_cust_vehicle_submenu },
	[2] = { label = "GANG_CUST_SLOT_3", type = MENU_ITEM_TYPE_SUB_MENU, sub_menu = Gang_cust_vehicle_submenu },

	btn_tips 			= Gang_Customization_main_menu_btn_tips,
}
--]]

--	Horizontal Menu
Gang_cust_horz_menu = {
	num_items = 1,

	[0] = { label = "GANG_CUST_GANG_TITLE", 	sub_menu = Gang_cust_gang_menu    },
	--[1] = { label = "GANG_CUST_VEHICLE_TITLE", sub_menu = Gang_cust_vehicle_menu },

}
