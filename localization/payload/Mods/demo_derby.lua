-- demo_derby.lua: Demolition Derby menu
-- Demo Derby Store Interface

-- "global" variables

Demo_derby_bonus_preview_update_thread_handle = -1	-- Bonus derby preview update thread handle [nclok1405]

Demo_derby_car_slider_values = { }

Demo_derby_offense_slider_values = {
	num_values = 3,
	cur_value = 0,

	[0] = { label = "NONE", },
	[1] = { label = "DEMO_DERBY_LEVEL_1", },
	[2] = { label = "DEMO_DERBY_LEVEL_2", },
--	[3] = { label = "DEMO_DERBY_LEVEL_3", },
}

Demo_derby_defense_slider_values = {
	num_values = 3,
	cur_value = 0,

	[0] = { label = "NONE", },
	[1] = { label = "DEMO_DERBY_LEVEL_1", },
	[2] = { label = "DEMO_DERBY_LEVEL_2", },
--	[3] = { label = "DEMO_DERBY_LEVEL_3", },
}

Demo_derby_speed_slider_values = {
	num_values = 3,
	cur_value = 0,

	[0] = { label = "NONE", },
	[1] = { label = "DEMO_DERBY_LEVEL_1", },
	[2] = { label = "DEMO_DERBY_LEVEL_2", },
--	[3] = { label = "DEMO_DERBY_LEVEL_3", },
}

Demo_derby_footer = { }

Demo_derby_max_points = 0
Demo_derby_points_spent = 0
Demo_derby_special = false
Demo_derby_which_menu = 0

----------------------
--	SYSTEM FUNCTIONS --
----------------------
--[ INITIALIZE AND SHUTDOWN ]--
-------------------------------
--	Initialize the menu
function demo_derby_init()
	--Button tips
	if Completion_is_coop() == true then
		-- I think this disables the cancel button for co-op client
		Demo_derby_btn_tips.b_button.enabled = false
	end

	local which_menu = demo_derby_get_menu_type()
	Demo_derby_which_menu = which_menu

	if which_menu == 0 then
		-- Normal Derby Setup Menu
		menu_init()

		--Demo_derby_horz_menu[0].sub_menu = Demo_derby_menu
		--Demo_derby_horz_menu[0].label = "DEMO_DERBY_TITLE"

		menu_horz_init(Demo_derby_horz_menu)

		event_tracking_interface_enter("Demo Derby")

		Sui_demo_derby_menu = true	-- Demo Derby menu active [nclok1405]
	elseif which_menu == 1 then
		-- Bonus Derby Event Menu

		--Demo_derby_btn_tips.right_stick.enabled = false -- You cannot rotate the vehicle in Bonus Derby [nclok1405]
		--Demo_derby_horz_menu[0].sub_menu = Demo_derby_bonus_derby_menu
		--Demo_derby_horz_menu[0].label = "DEMO_DERBY_BONUS_DERBY"

		menu_init()
		menu_show(Demo_derby_bonus_derby_menu)

		event_tracking_interface_enter("Demo Derby: Bonus")

		Sui_demo_derby_menu = true	-- Demo Derby menu active [nclok1405]
	elseif which_menu == 2 then
		-- Bonus Derby Vehicle Menu

		--Demo_derby_btn_tips.right_stick.enabled = false -- You cannot rotate the vehicle in Bonus Derby [nclok1405]
		--Demo_derby_horz_menu[0].sub_menu = Demo_derby_bonus_vehicle_menu
		--Demo_derby_horz_menu[0].label = "DEMO_DERBY_BONUS_DERBY"

		-- Query what vehicles are available [nclok1405]
		Demo_derby_bonus_vehicle_menu.num_items = 0
		vint_dataresponder_request("demo_derby_populate_bonus_menu", "demo_derby_populate_vehicle_menu", 0, 1) -- 0 = Populate vehicle menu

		if Demo_derby_bonus_vehicle_menu.num_items >= 2 then
			-- If two or more vehicles are selectable, show the menu
			menu_init()
			menu_show(Demo_derby_bonus_vehicle_menu)
			event_tracking_interface_enter("Demo Derby: Vehicle Menu")
			Sui_demo_derby_menu = true	-- Demo Derby menu active [nclok1405]
		else
			-- If there's only one vehicle, skip it [nclok1405]
			--debug_print("Skipping Vehicle Select Menu\n")
			thread_yield()	-- Wait one frame or we'll stuck in the empty garage
			vint_document_unload(vint_document_find("demo_derby"))
		end
	else
		debug_print("vint", "Invalide Menu Choice\n")
	end
end

-- Shutdown and cleanup the menu
function demo_derby_cleanup()
	--debug_print("demo_derby_cleanup\n")

	if Demo_derby_bonus_preview_update_thread_handle ~= -1 then
		thread_kill(Demo_derby_bonus_preview_update_thread_handle)
		Demo_derby_bonus_preview_update_thread_handle = -1
	end

	Sui_demo_derby_menu = false	-- Demo Derby menu no longer active [nclok1405]
end

--------------------------
-- FOOTER FUNCTIONALITY --
--------------------------
function demo_derby_build_footer(menu_data)
	local grp = vint_object_clone(vint_object_find("style_footer", nil, MENU_BASE_DOC_HANDLE), Menu_option_labels.control_parent)
	vint_set_property(grp, "visible", true)

	if menu_data.footer ~= nil and menu_data.footer.footer_grp ~= nil and menu_data.footer.footer_grp ~= 0 then
		vint_object_destroy(menu_data.footer.footer_grp)
	end

	menu_data.footer = { }
	menu_data.footer.footer_grp = grp

	Demo_derby_footer.label_h = vint_object_find("price_label", grp)
	Demo_derby_footer.price_h = vint_object_find("price_amount", grp)
	Demo_derby_footer.style_h = vint_object_find("style_amount", grp)

	vint_set_property(Demo_derby_footer.label_h , "visible", true)
	vint_set_property(Demo_derby_footer.price_h , "visible", true)
	vint_set_property(Demo_derby_footer.style_h, "visible", false)

	vint_set_property(Demo_derby_footer.label_h, "text_tag", "DEMO_DERBY_POINTS_INDICATOR")
end

function demo_derby_update_footer()
	if Demo_derby_special == false then
		vint_set_property(Demo_derby_footer.price_h, "text_tag", Demo_derby_points_spent .. "[color:grey]/" .. Demo_derby_max_points)

		if Demo_derby_points_spent > Demo_derby_max_points then
			vint_set_property(Demo_derby_footer.price_h, "tint", MENU_FOOTER_CASH_BROKE_COLOR.R, MENU_FOOTER_CASH_BROKE_COLOR.G, MENU_FOOTER_CASH_BROKE_COLOR.B)
		else
			vint_set_property(Demo_derby_footer.price_h, "tint", MENU_FOOTER_CASH_NORMAL_COLOR.R, MENU_FOOTER_CASH_NORMAL_COLOR.G, MENU_FOOTER_CASH_NORMAL_COLOR.B)
		end
	end
end

function demo_derby_finalize_footer(menu_data)
	if Demo_derby_special == false then
		vint_set_property(Demo_derby_footer.price_h, "anchor", menu_data.menu_width - 20, 0)
	end
end

function demo_derby_release_footer(menu_data)
	if menu_data.footer ~= nil then
		vint_object_destroy(menu_data.footer.footer_grp)
		menu_data.footer = nil
	end
end
----------------------------
--	NORMAL DEMO DERBY MENU --
----------------------------
function demo_derby_build_menu(menu_data)
	Demo_derby_car_slider_values.num_values = 0

	--	The first parameter is the dataresponder in C
	vint_dataresponder_request("demo_derby_populate_cars", "demo_derby_populate_cars", 0)
	vint_dataresponder_request("demo_derby_set_levels", "demo_derby_set_levels", 0)

	if Demo_derby_special == true then
		for i = 1, 3 do
			Demo_derby_menu[i].cur_value = 0
			Demo_derby_menu[i].disabled = true
			Demo_derby_menu[i].text_slider_values[0].label = "STORE_NOT_AVAILABLE"
			Demo_derby_menu[i].text_slider_values.num_values = 1
		end

		Demo_derby_menu[4].disabled = true
	else
		demo_derby_build_footer(menu_data)
		demo_derby_update_footer()
	end
end

function demo_derby_populate_cars(label)
	Demo_derby_car_slider_values[Demo_derby_car_slider_values.num_values] = { label = label }
	Demo_derby_car_slider_values.num_values = Demo_derby_car_slider_values.num_values + 1
end

function demo_derby_set_levels(offense_level, defense_level, speed_level, points_spent, max_points, special_tournament, derby_level)

	Demo_derby_menu[1].text_slider_values.cur_value = offense_level
	Demo_derby_menu[2].text_slider_values.cur_value = defense_level
	Demo_derby_menu[3].text_slider_values.cur_value = speed_level

	Demo_derby_max_points = max_points
	Demo_derby_points_spent = points_spent
	Demo_derby_special = special_tournament

	if derby_level == 0 then
		Demo_derby_menu.header_label_str = "DEMO_DERBY_TITLE"
	else
		local insert_values = { [0] = derby_level }
		Demo_derby_menu.header_label_str = vint_insert_values_in_string("DEMO_DERBY_TITLE_LEVEL", insert_values)
	end
end

function demo_derby_update(menu_label, menu_data)
	if (Demo_derby_special == true and menu_data.id == 0) or Demo_derby_special == false then
		local points = demo_derby_update_options(menu_data.id, menu_data.text_slider_values.cur_value)

		if points ~= nil and Demo_derby_special == false then
			Demo_derby_points_spent = points
			demo_derby_update_footer()
		end
	end
end

function demo_derby_reset_upgrades(menu_label, menu_data)
	Demo_derby_menu[1].text_slider_values.cur_value = 0
	Demo_derby_menu[2].text_slider_values.cur_value = 0
	Demo_derby_menu[3].text_slider_values.cur_value = 0

	menu_text_slider_update_value(Menu_option_labels[1], Demo_derby_menu[1])	-- This will change if it ever scrolls
	menu_text_slider_update_value(Menu_option_labels[2], Demo_derby_menu[2])
	menu_text_slider_update_value(Menu_option_labels[3], Demo_derby_menu[3])

	demo_derby_update_options(1, 0)
	demo_derby_update_options(2, 0)
	demo_derby_update_options(3, 0)
	Demo_derby_points_spent = 0
	demo_derby_update_footer()
end

function demo_derby_enter_derby(menu_label, menu_data)

	if Demo_derby_points_spent > Demo_derby_max_points and demo_derby_validate_points() == true then
		--dialog_box_message("MENU_TITLE_NOTICE", "DEMO_DERBY_NOT_ENOUGH_POINTS")
		-- Cheat! [nclok1405]
		local msg = vint_insert_values_in_string("{0}\n{1}", {[0] = "DEMO_DERBY_NOT_ENOUGH_POINTS", [1] = "CELL_CHEAT_ACTIVIATE_DIALOG_HEADER"})
		dialog_box_confirmation("DEMO_DERBY_ENTER_DERBY_TITLE", msg, "demo_derby_enter_derby_confirm")
	else
		--dialog_box_confirmation("DEMO_DERBY_ENTER_DERBY_TITLE", "DEMO_DERBY_ENTER_DERBY_PROMPT", "demo_derby_enter_derby_confirm")
		menu_close(demo_derby_enter_derby_final)
	end
end

function demo_derby_enter_derby_confirm(result, action)
	if action ~= DIALOG_ACTION_CLOSE then
		return
	end

	if result == 0 then
		menu_close(demo_derby_enter_derby_final)
	end
end

function demo_derby_enter_derby_final()
	vint_document_unload(vint_document_find("demo_derby"))
end

----------------------
-- BONUS DERBY MENU --
----------------------

-- Bonus Derby Preview Update Thread [nclok1405]
function demo_derby_bonus_preview_update_thread()
	--debug_print("demo_derby_bonus_preview_update_thread start")
	--delay(0.1)
	thread_yield()

	if Demo_derby_bonus_derby_menu[Demo_derby_bonus_derby_menu.highlighted_item].id ~= -1 then
		--debug_print("demo_derby_bonus_preview_update_thread update")
		demo_derby_update_options(0, Demo_derby_bonus_derby_menu.highlighted_item)
	end

	--debug_print("demo_derby_bonus_preview_update_thread end")
end

function demo_derby_build_bonus_menu(menu_data)
	Demo_derby_bonus_derby_menu.num_items = 0
	vint_dataresponder_request("demo_derby_populate_bonus_menu", "demo_derby_populate_bonus_menu", 0, 0) -- 0 = Populate derby menu

	-- Select the last bonus derby played. [nclok1405]
	Demo_derby_bonus_derby_menu.highlighted_item = Sui_last_bonus_derby_played

	btn_tips_footer_attach(menu_data)	-- Footer [nclok1405]

	-- Update vehicle preview (one frame delay) [nclok1405]
	if Demo_derby_bonus_derby_menu.highlighted_item ~= 0 then
		Demo_derby_bonus_preview_update_thread_handle = thread_new("demo_derby_bonus_preview_update_thread")
	end
end

function demo_derby_select_bonus_derby(menu_label, menu_data)
	Sui_last_bonus_derby_played = Demo_derby_bonus_derby_menu.highlighted_item
	demo_derby_sp_tournament_select(menu_data.id)
	demo_derby_enter_derby_final()
end

function demo_derby_populate_bonus_menu(label)
	Demo_derby_bonus_derby_menu[Demo_derby_bonus_derby_menu.num_items] = { label = label,
		type = MENU_ITEM_TYPE_SELECTABLE, on_select = demo_derby_select_bonus_derby, id = Demo_derby_bonus_derby_menu.num_items }

	Demo_derby_bonus_derby_menu.num_items = Demo_derby_bonus_derby_menu.num_items + 1
end

function demo_derby_start_vehicle_menu()
	menu_show(Demo_derby_bonus_vehicle_menu, MENU_TRANSITION_SWAP)
end

function demo_derby_build_vehicle_menu(menu_data)
	--Demo_derby_bonus_vehicle_menu.num_items = 0
	--vint_dataresponder_request("demo_derby_populate_bonus_menu", "demo_derby_populate_vehicle_menu", 0, 1) -- 0 = Populate vehicle menu

	btn_tips_footer_attach(menu_data)	-- Footer [nclok1405]
end

function demo_derby_nav_vehicle(menu_data)
	if Demo_derby_bonus_preview_update_thread_handle ~= -1 then
		thread_kill(Demo_derby_bonus_preview_update_thread_handle)
		Demo_derby_bonus_preview_update_thread_handle = -1
	end

	if menu_data[menu_data.highlighted_item].id ~= -1 then
		local points = demo_derby_update_options(0, menu_data.highlighted_item)
	end
end

function demo_derby_vehicle_select(menu_label, menu_data)
	menu_close()

	--	These should probably be in menu_close and not menu_horz close.
	menu_release_input()

	vint_document_unload(vint_document_find("demo_derby"))
end

function demo_derby_populate_vehicle_menu(label)
	Demo_derby_bonus_vehicle_menu[Demo_derby_bonus_vehicle_menu.num_items] = { label = label,
		type = MENU_ITEM_TYPE_SELECTABLE, on_select = demo_derby_vehicle_select }
	Demo_derby_bonus_vehicle_menu.num_items = Demo_derby_bonus_vehicle_menu.num_items + 1
end

function demo_derby_cancel_derby_confirm(result,action)
	if action ~= DIALOG_ACTION_CLOSE then
		return
	end

	if result == 0 then
		demo_derby_cancel()
	end
end

function demo_derby_cancel_derby()
	if Completion_is_coop() == true then
		return
	end

	if Demo_derby_which_menu == 1 then
		-- Exit Bonus Derby List without dialog. This does not cause a Game Over screen even in vanilla SR2. [nclok1405]
		demo_derby_cancel()
		return
	end

	--dialog_box_confirmation("DEMO_DERBY_EXIT_DERBY_TITLE", "DEMO_DERBY_EXIT_DERBY_PROMPT", "demo_derby_cancel_derby_confirm")

	-- Exit derby menu. Skip the fail screen that comes up. [nclok1405]
	Sui_skip_activity_cancel_fail_screen = true
	demo_derby_cancel()
end


function Demo_derby_coop_quit()
	if Completion_is_coop() == true then
		dialog_open_pause_display(true)	-- Call C-side for disconnect functionality
	end
end

---------------
-- MENU DATA --
---------------
Demo_derby_btn_tips = {
	a_button 	= 	{ label = "CONTROL_SELECT",		enabled = btn_tips_default_a, },
	b_button 	= 	{ label = "COMPLETION_EXIT",	enabled = btn_tips_default_b, },
	right_stick =  	{ label = "CONTROL_ROTATE", 	enabled = true },
}

Demo_derby_menu = {
	header_label_str = "ACT_DEMO_DERBY_MAIN_MENU",
	on_show = demo_derby_build_menu,
	on_post_show = demo_derby_finalize_footer,
	on_back = demo_derby_cancel_derby,
	btn_tips = Demo_derby_btn_tips,
	on_pause = Demo_derby_coop_quit,
	num_items = 6,

	[0] = { label = "DEMO_DERBY_CAR_OPTION", 				type = MENU_ITEM_TYPE_TEXT_SLIDER, text_slider_values = Demo_derby_car_slider_values, on_value_update = demo_derby_update, id = 0 },
	[1] = { label = "DEMO_DERBY_OFFENSE_OPT", 			type = MENU_ITEM_TYPE_TEXT_SLIDER, text_slider_values = Demo_derby_offense_slider_values, on_value_update = demo_derby_update, id = 1 },
	[2] = { label = "DEMO_DERBY_DEFENSE_OPT", 			type = MENU_ITEM_TYPE_TEXT_SLIDER, text_slider_values = Demo_derby_defense_slider_values, on_value_update = demo_derby_update, id = 2 },
	[3] = { label = "DEMO_DERBY_SPEED_OPT", 				type = MENU_ITEM_TYPE_TEXT_SLIDER, text_slider_values = Demo_derby_speed_slider_values, on_value_update = demo_derby_update, id = 3 },
	[4] = { label = "DEMO_DERBY_RESET_UPGRADES_OPT",	type = MENU_ITEM_TYPE_SELECTABLE, on_select = demo_derby_reset_upgrades },
	[5] = { label = "DEMO_DERBY_ENTER_DERBY_OPT", 		type = MENU_ITEM_TYPE_SELECTABLE, on_select = demo_derby_enter_derby },

	footer_height = 40
}

Demo_derby_bonus_derby_menu = {
	header_label_str = "DEMO_DERBY_BONUS_DERBY",
	max_height = 503,	-- Default: 375 [nclok1405]
	on_show = demo_derby_build_bonus_menu,
	on_nav = demo_derby_nav_vehicle,
	on_back = demo_derby_cancel_derby,
	btn_tips = Demo_derby_btn_tips,
}

Demo_derby_bonus_vehicle_menu = {
	header_label_str = "DEMO_DERBY_SELECT_VEHICLE",
	on_show = demo_derby_build_vehicle_menu,
	on_nav = demo_derby_nav_vehicle,
	on_back = demo_derby_cancel_derby,
	btn_tips = Demo_derby_btn_tips,
}

Demo_derby_horz_menu = {
	num_items = 1,
	current_selection = 0,
	[0] = { label = "DEMO_DERBY_TITLE", 		sub_menu = Demo_derby_menu},
}
