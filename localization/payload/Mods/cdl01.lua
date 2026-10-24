-- cdl01.lua: Car Dealership
										-----------------------
										--[ CAR  DEALERSHIP ]--
										-----------------------

--[ SYSTEM FUNCTIONS ]--

function cdl01_init()
	local store_name_crc, store_name_str = cdl_store_info()

	if store_name_crc ~= 0 then
		Cdl01_car_menu.header_label_crc = store_name_crc
	else
		Cdl01_car_menu.header_label_str = "MAP_ICON_CAR_DEALER"
	end

	menu_store_init(true)
	menu_init()
	menu_show(Cdl01_car_menu)

	--Event Tracking (Register Interface)
	event_tracking_interface_enter("Car Dealership")
end

-- Shutdown and cleanup the menu
function cdl01_cleanup()

end

function cdl01_store_exit()
	--dialog_box_confirmation("STORE_EXIT_WARNING_HEADER", "STORE_EXIT_WARNING_BODY", "cdl01_exit_confirm")
	menu_close(cdl01_exit_final_final) -- Exit without dialog [nclok1405]
end

function cdl01_exit_confirm(result, action)
	if action == DIALOG_ACTION_CLOSE and result == DIALOG_RESULT_YES then
		cdl01_exit_final()
	end
end

function cdl01_exit_final()
	menu_close(cdl01_exit_final_final)
end

function cdl01_exit_final_final()
	vint_document_unload(vint_document_find("cdl01"))
end

--[ FOOTER FUNCTIONALITY ]--

function cdl01_build_footer(menu_data)
	local grp = vint_object_clone(vint_object_find("style_footer"), Menu_option_labels.control_parent)
	vint_set_property(grp, "visible", true)

	if menu_data.footer ~= nil and menu_data.footer.footer_grp ~= nil then
		vint_object_destroy(menu_data.footer.footer_grp)
	end

	menu_data.footer = {}
	menu_data.footer.footer_grp = grp
	menu_data.footer.label_h = vint_object_find("price_label", grp)
	menu_data.footer.price_h = vint_object_find("price_amount", grp)
	menu_data.footer.style_h = vint_object_find("style_amount", grp)

	--Build second horizontal rule
	local bg_h = vint_object_find("menu_bg_header_hr", Menu_option_labels.control_parent)
	bg_h = vint_object_clone(bg_h, grp)
	vint_object_rename(bg_h, "footer_line")
	vint_set_property(bg_h, "anchor", -17, 48)
	menu_data.footer.line_h = bg_h

	--Attach button tips to this footer_grp
	menu_data.footer.btn_tips, menu_data.footer.btn_tips_width = btn_tips_footer_build(grp, -5, 57)

	vint_set_property(menu_data.footer.price_h , "visible", true)
end

function cdl01_update_car_footer(menu_data)
	local price, style, label
	local car_item = Cdl01_car_menu[Cdl01_car_menu.highlighted_item]

	if car_item.price ~= nil then
		price = "$"..format_cash(car_item.price)
		style = award_style("vehicle", car_item.price, true)

		if menu_store_get_player_cash() < car_item.price then
			vint_set_property(menu_data.footer.price_h, "tint", 1, 0, 0)
		else
			vint_set_property(menu_data.footer.price_h, "tint", 0.88, 0.749, 0.05)
		end

		vint_set_property(menu_data.footer.price_h, "visible", true)
		vint_set_property(menu_data.footer.style_h, "visible", true)
		vint_set_property(menu_data.footer.label_h, "visible", true)

		vint_set_property(menu_data.footer.price_h, "text_tag", price)
		vint_set_property(menu_data.footer.style_h, "insert_values", style, 0)
	else
		vint_set_property(menu_data.footer.price_h, "visible", false)
		vint_set_property(menu_data.footer.style_h, "visible", false)
		vint_set_property(menu_data.footer.label_h, "visible", false)
	end
end

function cdl01_update_color_footer(menu_data)
end

function cdl01_finalize_footer(menu_data)
	vint_set_property(menu_data.footer.price_h, "anchor", menu_data.menu_width - 10, 0)

	--Scale extra line for button tips
	local source_x, source_y = vint_get_property(menu_data.footer.line_h, "source_se")
	vint_set_property(menu_data.footer.line_h, "source_se", menu_data.menu_width + 10, source_y)
end

function cdl01_footer_release(menu_data)
	if menu_data.footer.footer_grp ~= nil then
		vint_object_destroy(menu_data.footer.footer_grp)
	end
end

--[ CAR MENU FUNCTIONS ]--

function cdl01_car_menu_show(menu_data)
	cdl01_build_footer(menu_data)
	Cdl01_car_menu.num_items = 0

	if Cdl01_car_menu.highlighted_item  == nil then
		Cdl01_car_menu.highlighted_item = 0
	end

	vint_dataresponder_request("CDL_CARS", "cdl01_add_car_record", 0)

	if Cdl01_car_menu.num_items == 0 then
		Cdl01_car_menu[0] = { label = "No Cars Available", type = MENU_ITEM_TYPE_SELECTABLE }
		Cdl01_car_menu.num_items = 1
	end

	cdl01_car_menu_nav(menu_data)
end

function cdl01_add_car_record(name_str, car_index, car_price)
	local c = Cdl01_car_menu.num_items
	Cdl01_car_menu[c] = { label = name_str, type = MENU_ITEM_TYPE_SELECTABLE, car_index = car_index, price = car_price, on_select = cdl01_car_menu_select }

	c = c + 1
	Cdl01_car_menu.num_items = c
end

function cdl01_car_menu_nav(menu_data)
	cdl_preview_car(menu_data[menu_data.highlighted_item].car_index)
	cdl01_update_car_footer(menu_data)
end

function cdl01_car_menu_back(menu_data)
	cdl01_store_exit()
end

function cdl01_car_menu_release(menu_data)
	cdl01_footer_release(menu_data)
end

function cdl01_car_menu_finalize(menu_data)
	cdl01_finalize_footer(menu_data)
end

function cdl01_car_menu_select(menu_label, menu_data)
	if menu_data.price > menu_store_get_player_cash() then
		dialog_box_message("MENU_TITLE_NOTICE", "HUD_SHOP_INSUFFICIENT_FUNDS")
		return
	end

	--make sure this car is loaded, otherwise you can't buy it yet!
	if cdl_car_loaded() == true then
		dialog_box_confirmation("CARDEALER_PURCHASE_CONFIRM_TITLE", "CARDEALER_PURCHASE_CONFIRM_BODY", "cdl01_purchase_confirm")
	end
end

function cdl01_car_menu_get_width(menu_data)
	--Returns the max size of the menu which also includes the button tips.
	local width = menu_data.footer.btn_tips_width
	if Menu_option_labels.max_label_w ~= nil then
		if width < Menu_option_labels.max_label_w then
			width = Menu_option_labels.max_label_w
		end
	end
	return width
end

--[ COLOR MENU FUNCTIONS ]--

function cdl01_color_menu_show(menu_data)
end

function cdl01_add_color_record(name, index, base_r, base_g, base_b, spec_col_r, spec_col_g, spec_col_b, spec_alpha, fres_col_r, fres_col_g, fres_col_b, fres_con, refl)
end

function cdl01_color_swatch_update(swatch)
end

function cdl01_color_menu_nav(menu_label, menu_data)
end

function cdl01_color_menu_select(menu_label, menu_data)
end

function cdl01_exit_deferred()
	delay(.5)
	while vint_document_find("menu_style_dialog") ~= 0 do
		thread_yield()
	end
	cdl01_exit_final()
end

function cdl01_purchase_confirm(result, action)
	if action ~= DIALOG_ACTION_CLOSE then
		return
	end

	if result == 0 then
		cdl_purchase_car()
		award_style("vehicle", Cdl01_car_menu[Cdl01_car_menu.highlighted_item].price)
		thread_new("cdl01_exit_deferred")
	end
end

function cdl01_color_menu_back(menu_data)
end

function cdl01_color_menu_release(menu_data)
end

function cdl01_color_menu_finalize(menu_data)
end

--[ MENU DATA ]--

Cdl01_car_menu = {
	header_label_str	= "NONE",
	max_height = 535,	-- Default: 375 [nclok1405]

	on_show				= cdl01_car_menu_show,
	on_nav				= cdl01_car_menu_nav,
	on_back				= cdl01_car_menu_back,
	on_release			= cdl01_car_menu_release,
	on_post_show		= cdl01_car_menu_finalize,
	get_width			= cdl01_car_menu_get_width,

	footer_height 		= 83,
}
