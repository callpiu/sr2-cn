-- building_purchase.lua: Store/Crib Purchase Confirmation Dialog and Purchased Screen

Building_purchase_elements = { }
Building_purchase_anims 	= { }
Building_purchase_subs 		= { }
Building_purchasing_data 	= { }
Building_purchase_is_crib	= false
Menu_sound_confirm			= audio_get_audio_id("SYS_HUD_CONF_SERIOUS")	-- Confirmation/warning dialog opens
Building_purchase_sound 	= audio_get_audio_id("SYS_MENU_BUY_BUILDING")

function building_purchase_init()
	Building_purchase_is_crib = building_purchase_is_crib_being_purchased()

	--Find objects
	Building_purchase_elements.ctrl_info_grp_h = vint_object_find("ctrl_info_grp")
	Building_purchase_elements.store_subtitle_txt_h = vint_object_find("store_subtitle_txt")
	Building_purchase_elements.store_title_txt_h = vint_object_find("store_title_txt")
	Building_purchase_elements.description_grp_h = vint_object_find("description_grp")
	Building_purchase_elements.description_txt_h = vint_object_find("description_txt")

	--Set Scaler for screen
	local h = vint_object_find("main")
	local scale_x, scale_y = vint_get_property(h, "scale")
	--Store and pause animations
	Building_purchase_anims.main_anim_h = vint_object_find("main_anim")

	vint_set_property(Building_purchase_anims.main_anim_h, "is_paused", true)

	--Set alpha on all objects to 0
	vint_set_property(Building_purchase_elements.ctrl_info_grp_h, "alpha", 0)
	vint_set_property(Building_purchase_elements.store_subtitle_txt_h, "alpha", 0)
	vint_set_property(Building_purchase_elements.store_title_txt_h, "alpha", 0)
	vint_set_property(Building_purchase_elements.description_grp_h, "alpha", 0)

	Building_purchase_subs[0] = vint_subscribe_to_input_event(nil, "all_unassigned",	"bp_nothing")

	if Building_purchase_is_crib == true then
		vint_dataresponder_request("crib_purchase_get_crib_info", "update_building_purchase_text", 0)
	else
		vint_dataresponder_request("shop_purchase_get_shop_info", "update_building_purchase_text", 0)
	end
end

function building_purchase_clean()
	building_purchase_cleanup(0, DIALOG_ACTION_CLOSE)
end

function building_purchase_cleanup(result, action)
	if action ~= DIALOG_ACTION_CLOSE then
		return
	end

	for index, value in Building_purchase_subs do
		vint_unsubscribe_to_input_event(value)
	end

	vint_document_unload(vint_document_find("building_purchase"))
end

function update_building_purchase_text(building_name, description_txt, store_cost, player_cash, profit)
	Building_purchasing_data.name = building_name
	Building_purchasing_data.description_txt = description_txt
	Building_purchasing_data.store_cost = store_cost
	Building_purchasing_data.player_cash = player_cash

	if Building_purchase_is_crib == false then
		Building_purchasing_data.profit = profit
	end

	if player_cash < store_cost then
		-- Show Dialog that says you can't afford it.
		-- Show price [nclok1405]
		local header = "MENU_TITLE_NOTICE"
		local insert_values = { [0] = "ACT_DEMO_DERBY_GARAGE_NOT_ENOUGH_CASH", [1] = "CARDEALER_FOOTER_PRICE", [2] = format_cash(store_cost) }
		local body = vint_insert_values_in_string("{0}\n{1} ${2}", insert_values)
		local options = { [0] = "CONTROL_CONTINUE" }
		dialog_box_open(header, body, options, "building_purchase_cleanup")
	else
		--	Ask player if they really want to purchase it.
		local header = "MENU_TITLE_CONFIRM"
		local body
		local insert_values = { [0] = building_name, [1] = format_cash(store_cost) }
		if Building_purchase_is_crib == true then
			body = vint_insert_values_in_string("BUILDING_PURCHASE_CRIB", insert_values)
		elseif building_name == 0 then
			-- Mod Vehicle Dealers have no building names [nclok1405]
			body = vint_insert_values_in_string("CRIB_CUSTOMIZE_PURCHASE_PROMPT", {[0] = "MAP_ICON_CAR_DEALER", [1] = format_cash(store_cost)})
		else
			body = vint_insert_values_in_string("BUILDING_PURCHASE_BUILDING", insert_values)
		end
		dialog_box_confirmation(header, body, "building_purchased")
	end



end

function building_purchased(result, action)
	if action ~= DIALOG_ACTION_CLOSE then
		return
	end

	if result == 0 then
		if Building_purchase_is_crib == true then
			crib_purchase_purchase_crib()
		else
			shop_purchase_purchase_shop()
		end

		audio_play(Building_purchase_sound)

		if (not Building_purchase_is_crib) and (Building_purchasing_data.name == 0) then
			-- Mod Vehicle Dealers have no building names [nclok1405]
			vint_set_property(Building_purchase_elements.store_title_txt_h, "text_tag", "MAP_ICON_CAR_DEALER")
		elseif Building_purchase_is_crib and (Building_purchasing_data.name == 0) then
			-- Mod Cribs [nclok1405]
			local mod_crib_name = "MAP_ICON_CRIB"
			if Building_purchasing_data.store_cost == 500000 then
				mod_crib_name = "Ultor Yacht"
			elseif Building_purchasing_data.store_cost == 1000000 then
				mod_crib_name = "Phillips Building"
			end
			vint_set_property(Building_purchase_elements.store_title_txt_h, "text_tag", mod_crib_name)
		else
			vint_set_property(Building_purchase_elements.store_title_txt_h, "text_tag_crc", Building_purchasing_data.name)
		end

		--Play text purchased animation
		lua_play_anim(Building_purchase_anims.main_anim_h, .5)

		--	Set the text properly
		vint_set_property(Building_purchase_elements.description_txt_h, "text_tag_crc", Building_purchasing_data.description_txt)
		if Building_purchase_is_crib == false then
			vint_set_property(Building_purchase_elements.description_txt_h, "insert_values", Building_purchasing_data.profit)
		end

		-- get the right button
		local button_h = vint_object_find("ctrl_btn", Building_purchase_elements.ctrl_info_grp_h)
		vint_set_property(button_h, "image", get_a_button())
		local button_highlight_h = vint_object_find("ctrl_btn_highlight", Building_purchase_elements.ctrl_info_grp_h)
		vint_set_property(button_highlight_h, "image", get_a_button())

		Building_purchase_subs[1] = vint_subscribe_to_input_event(nil, "select", "building_purchase_clean")

		--get coords and heights, then move the button tips
		local width, height = element_get_actual_size(Building_purchase_elements.description_txt_h)
		local x, y = vint_get_property(Building_purchase_elements.description_grp_h, "anchor")
		local ctrl_x, ctrl_y = vint_get_property(Building_purchase_elements.ctrl_info_grp_h, "anchor")
		local gap = 30

		vint_set_property(Building_purchase_elements.ctrl_info_grp_h, "anchor", ctrl_x, height + y + gap)
	else
		building_purchase_cleanup(0, DIALOG_ACTION_CLOSE)
	end
end
