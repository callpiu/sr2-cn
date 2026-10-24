-- activity_level.lua: Level Selector for a Completed Activity

-----------------------
-- ACTIVITY LEVEL --
-----------------------

function activity_level_init()
	menu_store_use_hud(true)
	menu_init()
	menu_show(Activity_level_menu)
end

function activity_level_close()
	menu_close(activity_level_exit)
end

function activity_level_exit()
	vint_document_unload()
end

------------------------
--	MENU FUNCTIONALITY --
------------------------

function activity_level_menu_init(menu_data)
	Activity_level_menu.num_items = 0
	--vint_dataresponder_request("activity_level", "activity_level_add_item", 0, "list")

	-- Do not query which levels are available. This might help preventing freezes. [nclok1405]
	activity_level_add_item("ACT_LEVEL_1", 1, false)
	activity_level_add_item("ACT_LEVEL_2", 2, false)
	activity_level_add_item("ACT_LEVEL_3", 3, false)
	activity_level_add_item("ACT_LEVEL_4", 4, false)
	activity_level_add_item("ACT_LEVEL_5", 5, false)
	activity_level_add_item("ACT_LEVEL_6", 6, false)

	btn_tips_footer_attach(menu_data)
end

function activity_level_add_item(display_name, level, client_has_completed)
	-- special case: level -1 is actually the activity name
	if level == -1 then
		Activity_level_menu.header_label_str = display_name
		return
	end

	-- continue processing menu item
	local i = Activity_level_menu.num_items
	Activity_level_menu[i] = { label = display_name, type = MENU_ITEM_TYPE_SELECTABLE, level = level,
			client_has_completed = client_has_completed, on_select = activity_level_select }
	i = i + 1
	Activity_level_menu.num_items = i
end

function activity_level_select(menu_label, menu_data)
	vint_dataresponder_request("activity_level", "activity_level_add_item", 0, "select", menu_data.level)
	activity_level_close()
end

function activity_level_cancel()
	vint_dataresponder_request("activity_level", "activity_level_add_item", 0, "cancel")
	thread_new("activity_level_close")
end

function activity_level_get_menu_width(menu_data)
	local width = Menu_option_labels.max_label_w
	if menu_data.footer.width > width then
		width = menu_data.footer.width
	end
	return width
end

---------------
-- MENU DATA --
---------------
Activity_level_menu = {
	header_label_str	= "MULTI_MODE_ALL_CAPS_1", --"ACTIVITY_LEVEL_SELECTION",
	on_show 	  			= activity_level_menu_init,
	on_back 	  			= activity_level_cancel,
	get_width 			= activity_level_get_menu_width,
}
