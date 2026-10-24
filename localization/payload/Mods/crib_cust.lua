-- crib_cust.lua: Crib Customization
------------------------
--	Crib Customization --
------------------------

-- "defines"
CRIB_CUST_GENERATE_CRIB_MENU 	= 0
CRIB_CUST_GENERATE_LEVEL_MENU = 1

-- "globals"
Crib_cust_current_set_selected 	= 0	--	Current set menu if we're not on the main menu.
Crib_cust_current_item_selected 	= 0	--	Item selected when purchasing
Crib_cust_menu_add_index			= 0	--	Used to index the menu items when building

-------------------------
--	SYSTEMISH FUNCTIONS --
-------------------------
function crib_cust_init()
	menu_store_init(true)

	menu_init()

	--menu_horz_init(Crib_cust_horz_menu)	-- Do not use horizontal bar [nclok1405]
	menu_show(Crib_cust_crib_menu)

	--crib_cust_build_crib_menu()

	local level, percent, bonus = pcu_purchase_slot(-1)

	--Event Tracking
	event_tracking_interface_enter("Crib Customization")
end

function crib_cust_cleanup()
end

-----------------------------
--	SELECTION FUNCTIONALITY --
-----------------------------
-- exit
function crib_cust_exit_final()
	vint_document_unload(vint_document_find("crib_cust"))
end

function crib_cust_exit(menu_data)
	-- Exit without dialog [nclok1405]
	menu_close()
	menu_release_input()
	if Sui_hud_enable == 0 then
		hud_hide(true)
	else
		hud_hide(false)
	end
	crib_cust_exit_final()
end

-----------------------
--	Preview Functions --
-----------------------
function crib_cust_update_camera(menu_data)
	crib_customization_update_camera(menu_data.highlighted_item)
end

function crib_cust_update_preview(menu_data)
	if Crib_cust_current_set_selected == 0 then
		menu_input_block(true)
	end
	crib_customization_update_preview(Crib_cust_current_set_selected, Crib_cust_level_menu.highlighted_item)
	menu_footer_update_style_footer(Crib_cust_level_menu[Crib_cust_level_menu.highlighted_item].price, Crib_cust_level_menu[Crib_cust_level_menu.highlighted_item].style, Crib_cust_level_menu[Crib_cust_level_menu.highlighted_item].can_afford)
	if Crib_cust_level_menu[Crib_cust_level_menu.highlighted_item].price == 0 then
		vint_set_property(Menu_footer_price_h, "text_tag", "STORE_ITEM_OWNED")
		vint_set_property(Menu_footer_price_h, "tint", 0.88, 0.749, 0.05)
		vint_set_property(Menu_footer_label_h, "visible", false)
		vint_set_property(Menu_footer_style_h, "visible", false)
	end
end

function crib_cust_revert_unchanged_props(menu_data)
	if Crib_cust_current_set_selected == 0 then
		menu_input_block(true)
	end
	crib_customization_revert_prop(Crib_cust_current_set_selected)
	menu_footer_remove_style_footer(menu_data)
	menu_show(Menu_active.parent_menu, MENU_TRANSITION_SWEEP_RIGHT)
	audio_play(Menu_sound_back)
end

-------------------
--	MENU CREATION --
-------------------
--	Trigger the Crib Menu to build
function crib_cust_build_crib_menu(menu_data)
	Crib_cust_menu_add_index = 0	--	Reset the index to add at.
	--	Request the data, giving parameter 0 which is GENERATE_CRIB_MENU. 0 Records means return all.
	vint_dataresponder_request("sr2_crib_store_data_responder", "crib_cust_add_items_crib_menu", 0, CRIB_CUST_GENERATE_CRIB_MENU)
	Crib_cust_crib_menu.num_items = Crib_cust_menu_add_index --	After the request is finished, set the number of items

	btn_tips_footer_attach(menu_data)	-- Append Button Footer [nclok1405]
end

--	Callback function for the data request when building the crib menu
function crib_cust_add_items_crib_menu(label_str)
	--	Add each menu item returned from the dataresponder to the menu.
	Crib_cust_crib_menu[Crib_cust_menu_add_index] = { label = label_str, type = MENU_ITEM_TYPE_SUB_MENU, sub_menu = Crib_cust_level_menu, on_select = crib_cust_select_set, cust_item_index = Crib_cust_menu_add_index }
	Crib_cust_menu_add_index = Crib_cust_menu_add_index + 1 --	Next index
end

--	Same as creating the Crib Menu, but for each level of the items
function crib_cust_build_level_menu(menu_data)
	crib_cust_update_item_list()
	menu_footer_build_style_footer(menu_data)	--	Build the footer for respect/cost
	crib_cust_update_preview(Crib_cust_level_menu)	--	Update the preview/price/style
end

function crib_cust_update_item_list()
	Crib_cust_menu_add_index = 0
	Crib_cust_level_menu.highlighted_item = 0
	vint_dataresponder_request("sr2_crib_store_data_responder", "crib_cust_add_items_level_menu", 0, CRIB_CUST_GENERATE_LEVEL_MENU, Crib_cust_current_set_selected)
	Crib_cust_level_menu.num_items = Crib_cust_menu_add_index
end

--	Callback for the level menu
function crib_cust_add_items_level_menu(label_str, cost, respect, is_disabled, is_affordable, is_current_level)
	Crib_cust_level_menu[Crib_cust_menu_add_index] = {
		label = label_str, type = MENU_ITEM_TYPE_SELECTABLE, on_select = crib_cust_select_level,
		cust_item_index = Crib_cust_menu_add_index, price = cost, style = award_style("crib", cost, true),
		enable = is_disabled, can_afford = is_affordable
	}

	if is_current_level == true then 	--	Select the current level
		Crib_cust_level_menu.highlighted_item = Crib_cust_menu_add_index
	end
	Crib_cust_menu_add_index = Crib_cust_menu_add_index + 1
end

------------------------
--	MENU FUNCTIONALITY --
------------------------

--	When something is selected on the Crib menu, build the specific crib menu
function crib_cust_select_set(menu_label, menu_data)
	Crib_cust_current_set_selected = menu_data.cust_item_index
	Crib_cust_level_menu.header_label_str = menu_data.label
end

-- purchase
function crib_cust_purchase_confirm(result, action)

	if action ~= DIALOG_ACTION_CLOSE then
		return
	end

	if result == 0 and action == 2 then
		-- make the purchase
		crib_customization_make_purchase(Crib_cust_current_set_selected, Crib_cust_current_item_selected.cust_item_index) -- C function
		award_style("crib", Crib_cust_current_item_selected.price)

		crib_cust_update_item_list(Crib_cust_level_menu)
		menu_show(Crib_cust_crib_menu, MENU_TRANSITION_SWEEP_RIGHT)

		audio_play(Menu_sound_purchase)
	end
end

--	Show the dialog confirming the purchase
function crib_cust_select_level(menu_label, menu_data)
	if Style_cluster_player_cash < menu_data.price then
		dialog_box_message("MENU_TITLE_NOTICE", "HUD_SHOP_INSUFFICIENT_FUNDS")
		return
	end
--	if menu_data.disabled == true then
	--	dialog_box_message("ERROR", "You already own this upgrade, or a better upgrade")
	--	return
--	end

	Crib_cust_current_item_selected = menu_data

	if menu_data.price == 0 then
		crib_customization_make_purchase(Crib_cust_current_set_selected, Crib_cust_current_item_selected.cust_item_index) -- C function
		crib_cust_update_item_list(Crib_cust_level_menu)
		menu_show(Crib_cust_crib_menu, MENU_TRANSITION_SWEEP_RIGHT)
	else
		local insert = { [0] = Crib_cust_level_menu.header_label_str, [1] = format_cash(menu_data.price) }
		local body = vint_insert_values_in_string("CRIB_CUSTOMIZE_PURCHASE_PROMPT", insert)
		local heading = "MENU_TITLE_CONFIRM"

		dialog_box_confirmation(heading, body, "crib_cust_purchase_confirm")
	end
end

---------------
--Button Tips
--------------
Crib_cust_btn_tips = {
	a_button 	= 	{ label = "CONTROL_SELECT", 	enabled = btn_tips_default_a, },
	b_button 	= 	{ label = "MENU_RESUME", 			enabled = btn_tips_default_a, },
}

Crib_cust_inner_btn_tips = {
	a_button 	= 	{ label = "CONTROL_SELECT", 	enabled = btn_tips_default_a, },
	b_button 	= 	{ label = "MENU_BACK", 			enabled = btn_tips_default_a, },
}


----------------
-- MAIN MENUS --
----------------
Crib_cust_level_menu = {
	header_label_str = "NONE",
	on_back = crib_cust_revert_unchanged_props,
	on_nav  = crib_cust_update_preview,
	on_show = crib_cust_build_level_menu,
	on_post_show = menu_footer_finalize_style_footer,
	btn_tips = Crib_cust_inner_btn_tips,
	footer_height = 40,
}

Crib_cust_crib_menu = {
	header_label_str = "CRIBS_TABLE_HEADER",
	on_back = crib_cust_exit,
	on_show = crib_cust_build_crib_menu,
	on_nav  = crib_cust_update_camera,
	btn_tips = Crib_cust_btn_tips,
}

Crib_cust_horz_menu = {
	num_items = 1,
	current_selection = 0,
	on_back = crib_cust_exit,

	[0] = { label = "CRIBS_TABLE_HEADER",	sub_menu = Crib_cust_crib_menu	},
}


