-- garage.lua: Garage menu

----------------------
-- GARAGE INTERFACE --
----------------------
-- "global" variables

-- Vehicle Count [nclok1405]
Garage_count_normal = 0
Garage_count_reward = 0
String_vehicle_count_label = "VEHICLE COUNT"

----------------------
--	SYSTEM FUNCTIONS --
----------------------
--[ INITIALIZE AND SHUTDOWN ]--
-------------------------------
--	Initialize the menu
function garage_init()
	-- Localize Vehicle Count feature [nclok1405]
	if get_language() == "JP" or get_language() == "CH" then
		String_vehicle_count_label = vint_insert_values_in_string("{0}{1}", {[0] = "CELL_CHEAT_CAT_VEHICLES", [1] = "ACT_VANDAL_BONUS_TOTAL"})
	elseif get_language() ~= "US" then
		String_vehicle_count_label = vint_insert_values_in_string("{0} {1}", {[0] = "CELL_CHEAT_CAT_VEHICLES", [1] = "ACT_VANDAL_BONUS_TOTAL"})
	end
	Garage_btn_tips.x_button.label = String_vehicle_count_label

	--Event Tracking
	event_tracking_interface_enter("Garage")

	menu_store_init(false)

	if SUI_GARAGE_HORZ_BARS then
		menu_init()
		menu_horz_init(Garage_vehicle_horz_menu)
	else
		-- No horizontal bars [nclok1405]
		menu_init(0, -40)
		Garage_menu.max_height = 599
		menu_show(Garage_menu)
	end
end

-- Shutdown and cleanup the menu
function garage_cleanup()

end

--[ EXIT ]--
------------
function garage_exit(menu_data)
	local body = "GARAGE_EXIT_PROMPT"
	local heading = "MENU_TITLE_WARNING"

	--dialog_box_confirmation(heading, body, "garage_exit_confirm")
	menu_close(garage_exit_final)	-- Exit without dialog [nclok1405]
end
function garage_exit_confirm(result, action)
	if action ~= DIALOG_ACTION_CLOSE then
		return
	end

	if result == 0 then
		menu_close(garage_exit_final)
	end
end
function garage_exit_final()
	vint_document_unload(vint_document_find("garage"))
end

------------------------
--	MENU FUNCTIONALITY --
------------------------

function garage_show(menu_data)
	menu_data.num_items = 0

	Garage_count_normal = 0
	Garage_count_reward = 0

	vint_dataresponder_request("garage_populate", "garage_populate", 0)

	-- Show vehicle count [nclok1405]
	local total = Garage_count_normal + Garage_count_reward
	local insert_values = {[0] = "INFO_UNLOCKABLES_VEHICLES", [1] = total}
	menu_data.header_label_str = vint_insert_values_in_string("{0}: {1}", insert_values)

	if menu_data.num_items == 0 then
		menu_data.num_items = 1
		menu_data.nothing = true
		menu_data[0] = { label = "GARAGE_NONE", type = MENU_ITEM_TYPE_SELECTABLE }
	end

	-- Footer [nclok1405]
	if not SUI_GARAGE_HORZ_BARS then
		btn_tips_footer_attach(menu_data)
	end
end

-- Show vehicle count [nclok1405]
function garage_show_vehicle_count()
	local total = Garage_count_normal + Garage_count_reward
	local insert_values = {
		[0] = "CUST_VARIANT_MAIN",
		[1] = Garage_count_normal,
		[2] = "INFO_UNLOCKABLES",
		[3] = Garage_count_reward,
		[4] = "ACT_VANDAL_SUMMARY_TOTAL",
		[5] = total,
	}
	local msg = vint_insert_values_in_string("{0}: {1}\n{2}: {3}\n{4}: {5}", insert_values)
	dialog_box_message(String_vehicle_count_label, msg)
end

function garage_post_show(menu_data)
	if menu_data.nothing == true then
		return
	end

	garage_preview_vehicle(menu_data[menu_data.highlighted_item].index)
end

function garage_populate(vehicle_name, repair_cost, reward_vehicle, vehicle_index)
	if reward_vehicle then
		Garage_count_reward = Garage_count_reward + 1
	else
		Garage_count_normal = Garage_count_normal + 1
	end

	local num_items = Garage_menu.num_items

	-- Set vehicle's label [nclok1405]
	local vehicle_label = vehicle_name
	if reward_vehicle then
		-- Highlight Reward Vehicle
		local insert_values = {[0] = vehicle_name}
		vehicle_label = vint_insert_values_in_string("[format][color:full_bright][image:ui_hud_diversion_star_gold]{0}[/format]", insert_values)
	end
	-- NOTE: repair_cost in this function do not work correctly. I had a perfectly fine Attrazione but repair_cost said $500!

	Garage_menu[num_items] = { label = vehicle_label, type = MENU_ITEM_TYPE_SELECTABLE, on_select = garage_show_vehicle_menu, repair_cost = repair_cost, reward_vehicle = reward_vehicle, index = vehicle_index, vehicle_name = vehicle_name }
	Garage_menu.num_items = num_items + 1
end

function garage_show_vehicle_menu()
	if garage_get_repair_cost() == false then
		return
	end

	Garage_vehicle_menu.parent_menu = Menu_active
	menu_show(Garage_vehicle_menu, MENU_TRANSITION_SWEEP_LEFT)

end

function garage_nav(menu_data)
	if menu_data.nothing == true then
		return
	end

	local hl_item = menu_data.highlighted_item
	garage_preview_vehicle(menu_data[hl_item].index)
end

function garage_vehicle_show(menu_data)
	local last_data = Menu_active[Menu_active.highlighted_item]
	menu_data.header_label_str = last_data.vehicle_name
	local repair_cost = garage_get_repair_cost()

	if repair_cost ~= 0 then
		-- Damaged Vehicle
		local insert_values = { [0] = repair_cost }
		local tag = vint_insert_values_in_string("GARAGE_REPAIR_RETRIEVE", insert_values)
		menu_data[0].label = tag
		menu_data[0].on_select = garage_repair_retrieve
		menu_data[0].repair_cost = repair_cost

		-- Show an option to retrieve the vehicle unrepaired [nclok1405]
		menu_data[1].label = "GARAGE_RETRIEVE_VEHICLE"
		menu_data[1].on_select = garage_retrieve

		if last_data.reward_vehicle then
			menu_data[2].label = vint_insert_values_in_string("[format][color:red]{0}[/format]",{[0] = "GARAGE_REMOVE_VEHICLE"})
			menu_data[2].on_select = garage_remove_reward_vehicle
		else
			menu_data[2].label = "GARAGE_REMOVE_VEHICLE"
			menu_data[2].on_select = garage_remove
		end

		menu_data.num_items = 3
	else
		-- Undamaged Vehicle
		menu_data[0].label = "GARAGE_RETRIEVE_VEHICLE"
		menu_data[0].on_select = garage_retrieve

		if last_data.reward_vehicle then
			menu_data[1].label = vint_insert_values_in_string("[format][color:red]{0}[/format]",{[0] = "GARAGE_REMOVE_VEHICLE"})
			menu_data[1].on_select = garage_remove_reward_vehicle
		else
			menu_data[1].label = "GARAGE_REMOVE_VEHICLE"
			menu_data[1].on_select = garage_remove
		end

		menu_data.num_items = 2
	end

	menu_data.highlighted_item = 0

	-- Footer [nclok1405]
	if not SUI_GARAGE_HORZ_BARS then
		btn_tips_footer_attach(menu_data)
	end
end

function garage_retrieve_unrepaired(result, action)
	if action ~= DIALOG_ACTION_CLOSE then
		return
	end

	if result == 0 then
		garage_retrieve_vehicle()
		menu_close(garage_exit_final)
	else
		menu_show(Garage_menu, MENU_TRANSITION_SWEEP_RIGHT)
		audio_play(Menu_sound_back)
	end
end

function garage_repair_retrieve(menu_label, menu_data)
	if Style_cluster_player_cash < menu_data.repair_cost then
		dialog_box_confirmation("STORE_TITLE_INSUFFICIENT_FUNDS", "GARAGE_TEXT_INSUFFICIENT_FUNDS", "garage_retrieve_unrepaired")
		return
	end

--[[
	local insert_values = { [0] = menu_data.repair_cost }
	local tag = vint_insert_values_in_string("GARAGE_REPAIR_PROMPT", insert_values)

	dialog_box_confirmation("GARAGE_REPAIR", tag, "garage_repair_confirm")
]]
	garage_repair_vehicle()
	garage_retrieve(menu_label, menu_data)
end

function garage_retrieve(menu_label, menu_data)
	garage_retrieve_vehicle()
	menu_close(garage_exit_final)
end

function garage_remove(menu_label, menu_data)
	dialog_box_confirmation("MENU_TITLE_WARNING", "GARAGE_REMOVE_PROMPT", "garage_remove_confirm")
end

-- Warning dialog for removing a reward vehicle [nclok1405]
function garage_remove_reward_vehicle(menu_label, menu_data)
	dialog_box_confirmation("MENU_TITLE_WARNING", "SUI_DELETE_REWARD_VEHICLE_WARNING", "garage_remove_confirm")
end

function garage_remove_confirm(result, action)
	if action ~= DIALOG_ACTION_CLOSE then
		return
	end

	if result == 0 then
		garage_remove_vehicle()
		menu_show(Garage_menu, MENU_TRANSITION_SWEEP_RIGHT)
		audio_play(Menu_sound_back)
	end
end

---------------
--Button Tips
--------------
Garage_btn_tips = {
	a_button 	= 	{ label = "CONTROL_SELECT", 	enabled = btn_tips_default_a, },
	b_button 	= 	{ label = "CONTROL_RESUME", 			enabled = btn_tips_default_a, },
	x_button 	= 	{ label = "VEHICLE COUNT", 	enabled = btn_tips_default_a, },
}

Garage_inner_btn_tips = {
	a_button 	= 	{ label = "CONTROL_SELECT", 	enabled = btn_tips_default_a, },
	b_button 	= 	{ label = "CONTROL_BACK", 			enabled = btn_tips_default_a, },
}


---------------
-- MENU DATA --
---------------
Garage_vehicle_menu = {
	header_label_str = "NONE",
	on_show = garage_vehicle_show,
	btn_tips = Garage_inner_btn_tips,
	num_items = 3,

	[0] = { label = "GARAGE_REPAIR_RETRIEVE", type = MENU_ITEM_TYPE_SELECTABLE, on_select = garage_repair_retrieve },
	[1] = { label = "GARAGE_RETRIEVE_VEHICLE", type = MENU_ITEM_TYPE_SELECTABLE, on_select = garage_retrieve },
	[2] = { label = "GARAGE_REMOVE_VEHICLE", type = MENU_ITEM_TYPE_SELECTABLE, on_select = garage_remove },
}

Garage_menu = {
	header_label_str = "GARAGE_CRIB_NAME",
	max_height = 503,	-- Default: 375 [nclok1405]
	on_show 	  		= garage_show,
	on_post_show 	= garage_post_show,
	on_nav			= garage_nav,
	on_back			= garage_exit,
	on_alt_select	= garage_show_vehicle_count,
	btn_tips			= Garage_btn_tips,
	num_items  		= 0,
}

Garage_vehicle_horz_menu = {
	num_items = 1,
	current_selection = 0,
	on_back = garage_exit,

	[0] = { label = "GARAGE_CRIB_NAME",	sub_menu = Garage_menu	},
}
