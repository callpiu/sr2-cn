-- clothing_store.lua: Clothing Stores, Tatoo Parlors, and Wardrobe

CRIB_CLOTHING_STORE_NAME = "ULTOR.COM"	-- Crib Store Display Name [nclok1405]
ITEM_CRC_FLASHER_COAT_WITH_MORPHS = 1145438989	-- CRC of "flasher coat with Morphs" [nclok1405]

Clothing_Wear_Test = "NOTWORN" -- Default state so clear preview isn't called unless the menu is rebuilt _IdolNinja
Accessory_Test = "NOTOUTFIT" -- Default state so accessory slots aren't cleared _IdolNinja
SlotEmptyLock = 0
LoopTest = 0
StreamTest = 0

Clothing_store_building_menu = 0
Clothing_store_current_area = -1
Clothing_store_current_category = -1
Clothing_store_current_item = -1
Clothing_store_current_color_index = -1

Clothing_store_original_value = -1
Clothing_store_item_update_value = -1
Clothing_store_item_update_thread = -1
Clothing_store_outfit_update_thread = -1

Clothing_store_allow_swap = false;

Clothing_store_waiting_update_value = -1
Clothing_store_update_type = 1;
--this variable is used to know what the next preview call to make on the player is
--1	this is an item
--2	this is an outfit from a store
--3	this is a player made outfit

Clothing_store_menu_when_done_updating = -1;
Clothing_store_menu_when_done_updating_safe = -1; -- the safe one is gaurrenteed not to change when while the update thread is executing

Clothing_store_top_menu = 0

-- need 2 footer objects for transitions
Clothing_store_footers = { [0] = { grp = 0 }, [1] = { grp = 0 } }


Clothing_store_cash_displayed = -1
Clothing_store_cash_anim_h = 0

Clothing_store_item_info = {
--[[ Initially empty but here are all of the fields that get populated
	slot_index
	item_index, item_name_*
	variant_index, variant_name_*, num_variants
	colors[3], num_colors, colors[n] == { index, red, green, blue }
	wear_option_index, wear_option_name_*, num_wear_options
	logo_index, logo_name_*, logo_color, logo_available
]]
	colors = { [0] = { }, [1] = { }, [2] = { } }
}

Clothing_store_is_wardrobe = true			-- avoid some string compares

CLOTHING_STORE_DOC_H = 0
CLOTHING_STORE_STYLE_FOOTER_HEIGHT = 40
CLOTHING_STORE_ITEM_UPDATE_VALUE_INVALID = -1
CLOTHING_STORE_INVALID_CATERGORY = -1
CLOTHING_STORE_INVALID_SLOT = -1 --slots are set up like this when a suit is selected (because the suit has no base slot)
CLOTHING_STORE_INVALID_INDEX = -1

Clothing_store_allow_wardrobe = true
CLOTHING_STORE_WARDROBE_DISPLAY_NAME = "MENU_SWAP_WARDROBE"
CLOTHING_STORE_NO_OUTFITS_DISPLAY_NAME = "NO_OUTFITS_DISPLAY_NAME"

Clothing_store_use_style = true

function clothing_store_delayed_allow_swap()
	delay(1.2)
	Clothing_store_allow_swap = true
end

function clothing_store_init()
	--debug_print("clothing_store_init")
	Clothing_store_allow_swap = false
	thread_new("clothing_store_delayed_allow_swap")
	if CLOTHING_STORE_DOC_H == 0 then
		CLOTHING_STORE_DOC_H = vint_document_find()
	end
	if Menu_swap_hud_hidden == true then
		if Sui_hud_enable == 0 then
			hud_hide(true)
		else
			hud_hide(false)
		end
		Menu_swap_hud_hidden = false
	end
	if Clothing_store_outfit_update_thread == -1 then
		Clothing_store_outfit_update_thread = thread_new("clothing_store_preview_update")
	end
	if (Clothing_store_name == "DEBUG_CLOTHING_STORE") then
		local start_wardrobe
		Clothing_store_name, Clothing_store_display_name, Clothing_store_allow_wardrobe, start_wardrobe = pcu_get_store_info()

		if start_wardrobe then
			Clothing_store_original_name = Clothing_store_name
			Clothing_store_original_display_name = Clothing_store_display_name;
			Clothing_store_name = "WARDROBE"
			Clothing_store_display_name = CLOTHING_STORE_WARDROBE_DISPLAY_NAME
			Clothing_store_is_wardrobe = true
		elseif Clothing_store_name ~= "WARDROBE" and Clothing_store_name ~= "Wardrobe" and Clothing_store_name ~= "wardrobe" then
			Clothing_store_original_name = Clothing_store_name
			Clothing_store_original_display_name = Clothing_store_display_name;
			Clothing_store_is_wardrobe = false
		else
			-- Crib Wardrobe [nclok1405]
			Clothing_store_original_name = "Branded" -- See optional_mod_stuff\modified\customization_stores.xtbl for list of stores
			Clothing_store_name = "WARDROBE"  --to save me case mismatch headaches
			Clothing_store_original_display_name = CRIB_CLOTHING_STORE_NAME	-- CLOTHING_STORE_WARDROBE_DISPLAY_NAME
			Clothing_store_allow_wardrobe = true	-- false
			Clothing_store_is_wardrobe = true
		end
	end
	if Clothing_store_allow_wardrobe == true then
		if Clothing_store_name == "WARDROBE" then
			Clothing_store_top_btn_tips.x_button = { label = "SWITCH_TO_STORE", 	enabled = btn_tips_default_a, }
			Clothing_store_untop_btn_tips.x_button = { label = "SWITCH_TO_STORE", 	enabled = btn_tips_default_a, }
			Clothing_store_is_wardrobe = true
		else
			Clothing_store_top_btn_tips.x_button = { label = "SWITCH_TO_WARDROBE", 	enabled = btn_tips_default_a, }
			Clothing_store_untop_btn_tips.x_button = { label = "SWITCH_TO_WARDROBE", 	enabled = btn_tips_default_a, }
			Clothing_store_is_wardrobe = false
		end
	end

	if mp_is_enabled() == true then
		Clothing_store_top_btn_tips.b_button = { label = "MENU_BACK", 	enabled = btn_tips_default_a, }
		Clothing_store_untop_btn_tips.b_button = { label = "MENU_BACK", 	enabled = btn_tips_default_a, }
		Clothing_store_original_display_name = "MENU_SWAP_CLOTHING_STORE";
	else
		Clothing_store_top_btn_tips.b_button = { label = "CONTROL_RESUME", 	enabled = btn_tips_default_a, }
		Clothing_store_untop_btn_tips.b_button = { label = "MENU_BACK", 	enabled = btn_tips_default_a, }
	end

	clothing_store_show()	--sets up Clothing_store_use_style, based on waredrobe and mp status.
	menu_store_init(Clothing_store_use_style)
	clothing_store_build_horz_menu()
	menu_init()
	menu_horz_init(Clothing_store_horz_menu)


	--Event Tracking
	if mp_is_enabled == true then
		--debug_print("VINT", "EVENT TRACK: MP: Clothing Store\n")
		event_tracking_interface_enter("MP: Clothing Store")
	else
		if Clothing_store_is_wardrobe == true then
			--debug_print("VINT", "EVENT TRACK: Wardrobe\n")
			event_tracking_interface_enter("Wardrobe")
		else
			--debug_print("VINT", "EVENT TRACK: Clothing Store\n")
			event_tracking_interface_enter("Clothing Store")
		end
	end

	if mp_is_enabled() then
		-- Make sure we back out by fading to black when viewing this in multiplayer mode
		--Menu_fade_to_black = true

		-- Hide the hud for the duration
		hud_fade_out()
	end
end

function clothing_store_show()
	--debug_print("clothing_store_show")
	Clothing_store_use_style = false

	if Clothing_store_is_wardrobe == false then
		if mp_is_enabled() == true then
			Clothing_store_use_style = false
		else
			Clothing_store_use_style = true
		end
	end

	if mp_is_enabled() == true then
		Clothing_store_top_btn_tips.b_button.label = "MENU_BACK"
	end
end

function clothing_store_cleanup()
	--debug_print("clothing_store_cleanup")
	peg_unload("ui_multiplayer")
	peg_unload("ui_cl_logos")
end

function clothing_store_exit()
	--debug_print("clothing_store_exit")

	if mp_is_enabled() then
		if Clothing_store_is_wardrobe then
			dialog_box_confirmation("STORE_EXIT_WARNING_HEADER", "CRIB_WARDROBE_EXIT", "clothing_store_confirm", true, true)
		else
			dialog_box_confirmation("STORE_EXIT_WARNING_HEADER", "STORE_EXIT_WARNING_BODY", "clothing_store_confirm", true, true)
		end
	else
		menu_close(clothing_store_exit_final)	-- In main game, exit without dialog [nclok1405]
	end
end

function clothing_store_exit_final()
	--debug_print("clothing_store_exit_final")
	Clothing_store_name = "DEBUG_CLOTHING_STORE"
	Clothing_store_original_name = "DEBUG_CLOTHING_STORE"
	vint_document_unload(vint_document_find("clothing_store"))
end

function clothing_store_confirm(result, action)
	--debug_print("clothing_store_confirm")
	if action ~= DIALOG_ACTION_CLOSE then
		return
	end

	if result == 0 then
		menu_close(clothing_store_exit_final)
	end
end

function clothing_store_build_horz_menu()
	--debug_print("clothing_store_build_horz_menu")
	--debug_print("vint", "building a horz menu\n")
	Clothing_store_horz_menu = { num_items = 0 }

	pcu_get_areas(Clothing_store_name, "clothing_store_add_horz_menu")
	if Clothing_store_is_wardrobe == true then
		--debug_print("vint", "adding an the special outfits tab because we're in the wardrobe\n")

		-- Crib Stores [nclok1405]
		if Clothing_store_original_display_name == CRIB_CLOTHING_STORE_NAME then
			Clothing_store_horz_menu[Clothing_store_horz_menu.num_items] =
				{ label = "PAUSE_MAP_FILTER_STORES", sub_menu =  Clothing_store_wardrobe_online_store_menu }
			Clothing_store_horz_menu.num_items = Clothing_store_horz_menu.num_items + 1
		end

		Clothing_store_horz_menu[Clothing_store_horz_menu.num_items] =
			{ label = "CUST_ICON_OUTFITS", sub_menu =  Clothing_store_wardrobe_outfit_menu }
		Clothing_store_horz_menu.num_items = Clothing_store_horz_menu.num_items + 1
	end

	if Clothing_store_is_wardrobe == true and mp_is_enabled() == true then
		Clothing_store_horz_menu[Clothing_store_horz_menu.num_items] =
			{ label = "CUST_ICON_BADGES", sub_menu = Clothing_store_mp_badges_menu }
		Clothing_store_horz_menu.num_items = Clothing_store_horz_menu.num_items + 1
	end
end

function clothing_store_dump_item_info_debug()
--[[
	local t = Clothing_store_item_info
	--debug_print("vint", "\n")
	--debug_print("vint", "slot_index "..var_to_string(t.slot_index).."\n")
	--debug_print("vint", "item_index "..var_to_string(t.item_index).."\n")
	--debug_print("vint", "item_name_crc "..var_to_string(t.item_name_crc).."\n")
	--debug_print("vint", "item_name_str "..var_to_string(t.item_name_str).."\n")
	--debug_print("vint", "num_variants "..var_to_string(t.num_variants).."\n")
	--debug_print("vint", "variant_index "..var_to_string(t.variant_index).."\n")
	--debug_print("vint", "variant_name_crc "..var_to_string(t.variant_name_crc).."\n")
	--debug_print("vint", "variant_name_str "..var_to_string(t.variant_name_str).."\n")
	--debug_print("vint", "colors.num_colors "..var_to_string(t.colors.num_colors).."\n")
	--debug_print("vint", "colors[0].index "..var_to_string(t.colors[0].index).."\n")
	--debug_print("vint", "colors[0].red "..var_to_string(t.colors[0].red).."\n")
	--debug_print("vint", "colors[0].green "..var_to_string(t.colors[0].green).."\n")
	--debug_print("vint", "colors[0].blue "..var_to_string(t.colors[0].blue).."\n")
	--debug_print("vint", "colors[1].index "..var_to_string(t.colors[1].index).."\n")
	--debug_print("vint", "colors[1].red "..var_to_string(t.colors[1].red).."\n")
	--debug_print("vint", "colors[1].green "..var_to_string(t.colors[1].green).."\n")
	--debug_print("vint", "colors[1].blue "..var_to_string(t.colors[1].blue).."\n")
	--debug_print("vint", "colors[2].index "..var_to_string(t.colors[2].index).."\n")
	--debug_print("vint", "colors[2].red "..var_to_string(t.colors[2].red).."\n")
	--debug_print("vint", "colors[2].green "..var_to_string(t.colors[2].green).."\n")
	--debug_print("vint", "colors[2].blue "..var_to_string(t.colors[2].blue).."\n")
	--debug_print("vint", "num_wear_options "..var_to_string(t.num_wear_options).."\n")
	--debug_print("vint", "wear_option_index "..var_to_string(t.wear_option_index).."\n")
	--debug_print("vint", "wear_option_name_crc "..var_to_string(t.wear_option_name_crc).."\n")
	--debug_print("vint", "wear_option_name_str "..var_to_string(t.wear_option_name_str).."\n")
	--debug_print("vint", "num_logos "..var_to_string(t.num_logos).."\n")
	--debug_print("vint", "logo_index "..var_to_string(t.logo_index).."\n")
	--debug_print("vint", "logo_name_crc "..var_to_string(t.logo_name_crc).."\n")
	--debug_print("vint", "logo_name_str "..var_to_string(t.logo_name_str).."\n")
	--debug_print("vint", "logo_color_index "..var_to_string(t.logo_color_index).."\n")
	--debug_print("vint", "logo_color_red "..var_to_string(t.logo_color_red).."\n")
	--debug_print("vint", "logo_color_green "..var_to_string(t.logo_color_green).."\n")
	--debug_print("vint", "logo_color_blue "..var_to_string(t.logo_color_blue).."\n")
	--debug_print("vint", "item_style "..var_to_string(t.item_style).."\n")
	--debug_print("vint", "item_price "..var_to_string(t.item_price).."\n")
	--debug_print("vint", "\n")
	]]
end

function clothing_store_get_slot_info(slot)
	--debug_print("clothing_store_get_slot_info")
	local t = Clothing_store_item_info
	local temp_logo_storage_color_index = t.logo_color_index
	local temp_logo_storage_color_red = t.logo_color_red
	local temp_logo_storage_color_green = t.logo_color_green
	local temp_logo_storage_color_blue = t.logo_color_blue

	t.slot_index, t.item_index, t.item_name_crc, t.item_name_str,
	t.num_variants, t.variant_index, t.variant_name_crc, t.variant_name_str,
	t.colors.num_colors,
	t.colors[0].index, t.colors[0].red, t.colors[0].green, t.colors[0].blue,
	t.colors[1].index, t.colors[1].red, t.colors[1].green, t.colors[1].blue,
	t.colors[2].index, t.colors[2].red, t.colors[2].green, t.colors[2].blue,
	t.num_wear_options, t.wear_option_index, t.wear_option_name_crc, t.wear_option_name_str,
	t.num_logos, t.logo_index, t.logo_name_crc, t.logo_name_str, t.logo_color_index, t.logo_color_red, t.logo_color_green, t.logo_color_blue,
	t.item_style, t.item_price,
	t.player_style_level, t.player_style_percent
	= pcu_get_slot_info(slot)

	-- Blacklist a problematic clothing item [nclok1405]
	if t.item_name_crc == ITEM_CRC_FLASHER_COAT_WITH_MORPHS then
		t.num_wear_options = 0
	end

	--do this to prevent logo color from being wiped when previewing the "no logo" logo
	if t.logo_index == CLOTHING_STORE_INVALID_INDEX then
		t.logo_color_index = temp_logo_storage_color_index
		t.logo_color_red = temp_logo_storage_color_red
		t.logo_color_green = temp_logo_storage_color_green
		t.logo_color_blue = temp_logo_storage_color_blue
	end
	clothing_store_dump_item_info_debug()
end

function clothing_store_get_item_defaults(item_index)
	--debug_print("clothing_store_get_item_defaults")
	local t = Clothing_store_item_info
	if item_index >= 0 then
		t.slot_index, t.item_index, t.item_name_crc, t.item_name_str,
		t.num_variants, t.variant_index, t.variant_name_crc, t.variant_name_str,
		t.colors.num_colors,
		t.colors[0].index, t.colors[0].red, t.colors[0].green, t.colors[0].blue,
		t.colors[1].index, t.colors[1].red, t.colors[1].green, t.colors[1].blue,
		t.colors[2].index, t.colors[2].red, t.colors[2].green, t.colors[2].blue,
		t.num_wear_options, t.wear_option_index, t.wear_option_name_crc, t.wear_option_name_str,
		t.num_logos, t.logo_index, t.logo_name_crc, t.logo_name_str, t.logo_color_index, t.logo_color_red, t.logo_color_green, t.logo_color_blue,
		t.item_style, t.item_price,
		t.player_style_level, t.player_style_percent
		= pcu_get_item_defaults(item_index)

		-- Blacklist a problematic clothing item [nclok1405]
		if t.item_name_crc == ITEM_CRC_FLASHER_COAT_WITH_MORPHS then
			t.num_wear_options = 0
		end
	else
		t.item_index = -1
	end

	clothing_store_dump_item_info_debug()
end

function clothing_store_get_owned_item_info(item_index, wardrobe_instance)  -- like get item defaults, but called when browsing the inventory
	--debug_print("clothing_store_get_owned_item_info")
	local t = Clothing_store_item_info
	if wardrobe_instance == nil then
		wardrobe_instance = -1  --this should never occur, but incase it does, this will make it assert instead of crash
	end
	if item_index >= 0 then
		t.slot_index, t.item_index, t.item_name_crc, t.item_name_str,
		t.num_variants, t.variant_index, t.variant_name_crc, t.variant_name_str,
		t.colors.num_colors,
		t.colors[0].index, t.colors[0].red, t.colors[0].green, t.colors[0].blue,
		t.colors[1].index, t.colors[1].red, t.colors[1].green, t.colors[1].blue,
		t.colors[2].index, t.colors[2].red, t.colors[2].green, t.colors[2].blue,
		t.num_wear_options, t.wear_option_index, t.wear_option_name_crc, t.wear_option_name_str,
		t.num_logos, t.logo_index, t.logo_name_crc, t.logo_name_str, t.logo_color_index, t.logo_color_red, t.logo_color_green, t.logo_color_blue
		= pcu_get_owned_item_info(item_index, wardrobe_instance)

		-- Blacklist a problematic clothing item [nclok1405]
		if t.item_name_crc == ITEM_CRC_FLASHER_COAT_WITH_MORPHS then
			t.num_wear_options = 0
		end
	else
		t.item_index = -1
	end

	clothing_store_dump_item_info_debug()
end

function clothing_store_preview_item(get_specific_variant)
	--debug_print("clothing_store_preview_item")
	local t = Clothing_store_item_info
	local unavailable_grp_h = vint_object_find("preview_unavailable_grp")
	local unavailable_txt_h = vint_object_find("preview_unavailable_txt", unavailable_grp_h)
	vint_set_property(unavailable_txt_h, "word_wrap", true)
	vint_set_property(unavailable_txt_h, "text_tag", "PREVIEW_UNAVAILABLE")

	--debug_print("vint", "the item's index"..var_to_string(t.item_index).."\n")

	if t.num_wear_options == 0 then
		vint_set_property(unavailable_grp_h, "visible", true)
	else
		vint_set_property(unavailable_grp_h, "visible", false)
		if type(Clothing_store_item_update_value) == "table" and Clothing_store_item_update_value.is_outfit == true then
			clothing_store_preview_store_outfit()
		else
			if mp_is_enabled() == true and Clothing_store_is_wardrobe == false then
				-- We may be looking for one variant, otherwise we're looking for *all* variants (pass in nil)
				local variant_index = get_specific_variant and Clothing_store_item_info.variant_index or nil

				if pcu_is_item_owned(Clothing_store_item_info.item_index, variant_index) == true then
					clothing_store_already_owned_true()
				else
					clothing_store_already_owned_false()
				end
			else
				clothing_store_already_owned_false()
			end

			clothing_store_preview_single_item()
		end
	end
end

function clothing_store_already_owned_true()
	--debug_print("clothing_store_already_owned_true")
	local unavailable_grp_h = vint_object_find("preview_unavailable_grp")
	local unavailable_txt_h = vint_object_find("preview_unavailable_txt", unavailable_grp_h)
	vint_set_property(unavailable_txt_h, "word_wrap", true)
	vint_set_property(unavailable_txt_h, "text_tag", "MP_ITEM_OWNED")
	vint_set_property(unavailable_grp_h, "visible", true)
end

function clothing_store_already_owned_false()
	--debug_print("clothing_store_already_owned_false")
	local unavailable_grp_h = vint_object_find("preview_unavailable_grp")
	vint_set_property(unavailable_grp_h, "visible", false)
end

function clothing_store_add_horz_menu(area_index, label_crc, label_str)
	-- OUTFITS freezes the menu in crib store so hide it [nclok1405]
	if (not mp_is_enabled()) and (Clothing_store_display_name == CRIB_CLOTHING_STORE_NAME) and (label_crc == 4203310142) then
		return
	end

	--debug_print("clothing_store_add_horz_menu")
	local menu_idx = Clothing_store_horz_menu.num_items

	-- add an empty menu for this area
	local new_menu = {
		num_items = 0, on_back = clothing_store_exit, on_show = clothing_store_build_category_menu, on_alt_select = clothing_store_switch_mode,
		on_nav = clothing_store_nav_category, area_id = area_index,  btn_tips = Clothing_store_top_btn_tips,
	}

	Clothing_store_category_menus[menu_idx] = new_menu

	-- add new horz item
	local new_item = { sub_menu = new_menu }
	Clothing_store_horz_menu[menu_idx] = new_item

	if (label_str == "Misc") and (get_language() ~= "US") then
		-- Localize "Misc" menu if not in English [nclok1405]
		new_menu.header_label_str = "SLOT_MISCELLANEOUS"
		new_item.label = "SLOT_MISCELLANEOUS"
	elseif label_crc ~= nil then
		new_menu.header_label_crc = label_crc
		new_item.label_crc = label_crc
	else
		new_menu.header_label_str = label_str
		new_item.label = label_str
	end

	Clothing_store_horz_menu.num_items = menu_idx + 1
end

function clothing_store_purge_pending_updates()
	--debug_print("clothing_store_purge_pending_updates")
	if Clothing_store_item_update_thread ~= nil then
		thread_kill(Clothing_store_item_update_thread)
		--debug_print("vint", "KILL Thread" .. Clothing_store_item_update_thread .. "\n")
	end
	Clothing_store_waiting_update_value = -1
end


function clothing_store_build_category_menu(menu_data)
	--debug_print("clothing_store_build_category_menu")
	Clothing_store_top_menu = menu_data
	Clothing_store_current_area = menu_data.area_id

	--debug_print("test variable val is  "..var_to_string(Clothing_Wear_Test).."\n")

	if Clothing_Wear_Test == "WORN" then  --wear_item function processed
		--debug_print("Clothing worn don't clear slot")
	else
		--debug_print("Clothing not worn so clear slot")
		pcu_clear_preview_slot()
		Clothing_Wear_Test = "NOTWORN"  --default to not worn state
	end


	pcu_category_nav_clear_slot(menu_data.area_id)
	Clothing_store_building_menu = menu_data
	--debug_print("vint","I think the menu ID is"..var_to_string(menu_data.area_id).."\n")
	clothing_store_purge_pending_updates()
	clothing_store_already_owned_false()


	menu_data.num_items = 0


	pcu_get_categories_in_area(menu_data.area_id, "clothing_store_add_category_item")

	if menu_data.num_items == 0 then
		menu_data[0] = { label = "NO_ITEMS_DISPLAY_NAME", type = MENU_ITEM_TYPE_SELECTABLE }
		menu_data.num_items = 1
		Clothing_store_current_category = CLOTHING_STORE_INVALID_CATERGORY
	else
		if menu_data.highlighted_item == nil then
			menu_data.highlighted_item = 0
		end
		if menu_data.highlighted_item >= menu_data.num_items then
			menu_data.highlighted_item = 0
		end
		local i = menu_data[menu_data.highlighted_item]
		pcu_set_active_category(i.cat_id, Clothing_store_current_area)
		Clothing_store_current_category = i.cat_id

		Clothing_store_item_list_menu.header_label_crc = i.label_crc
		Clothing_store_item_list_menu.header_label_str = i.label
	end
end

function clothing_store_add_category_item(category_id, label_crc, label_str)
	--debug_print("clothing_store_add_category_item")
	local new_item = { type = MENU_ITEM_TYPE_SUB_MENU, sub_menu = Clothing_store_item_list_menu, cat_id = category_id }
	local misc_insert_values = {[0] = "SLOT_MISCELLANEOUS"}

	new_item.label = nil
	new_item.label_crc = nil

	-- Localize Misc 1-3 and others [nclok1405]
	if label_str == "Misc 1" then
		new_item.label = vint_insert_values_in_string("{0} 1", misc_insert_values)
	elseif label_str == "Misc 2" then
		new_item.label = vint_insert_values_in_string("{0} 2", misc_insert_values)
	elseif label_str == "Misc 3" then
		new_item.label = vint_insert_values_in_string("{0} 3", misc_insert_values)
	elseif label_str == "Teeth" then
		new_item.label = "CUST_ITEM_HUMAN_TEETH"
	elseif label_crc ~= nil then
		new_item.label_crc = label_crc
	else
		new_item.label = label_str
	end

	local i = Clothing_store_building_menu.num_items
	Clothing_store_building_menu[i] = new_item
	Clothing_store_building_menu.num_items = i + 1
end

function clothing_store_nav_category(menu_data)
	--debug_print("clothing_store_nav_category")

	--debug_print("vint", "Naving Category\n")

	if pcu_is_streaming_done() and Clothing_store_waiting_update_value == -1 then

		--debug_print("vint", "the currently selected category is "..var_to_string(Clothing_store_current_category).."\n");
		if Clothing_store_current_category ~= CLOTHING_STORE_INVALID_CATERGORY then
			pcu_clear_preview_slot()
			Clothing_store_current_category = menu_data[menu_data.highlighted_item].cat_id
			pcu_set_active_category(Clothing_store_current_category, Clothing_store_current_area)

			local i = Menu_active[Menu_active.highlighted_item]
			Clothing_store_item_list_menu.header_label_crc = i.label_crc
			Clothing_store_item_list_menu.header_label_str = i.label
		end
	end
end

function clothing_store_build_style_footer(menu_data)
	--debug_print("clothing_store_build_style_footer")
	local grp = vint_object_find("style_footer", Menu_option_labels.control_parent)

	--[[
	--debug_print("vint", "clothing_store_build_style_footer()\n")
	--debug_print("vint", "menu_data.footer_height = "..var_to_string(menu_data.footer_height).."\n")
	--debug_print("vint", "menu_data.footer_height = "..var_to_string(menu_data.footer_height).."\n")
	--debug_print("vint", "grp = "..var_to_string(grp).."\n")
	]]

	if menu_data.footer_height == 0 then
		-- no active footer so hide the footer object
		if grp ~= nil then
			vint_set_property(grp, "visible", false)
		end

		return
	end

	-- clone if needed
	if grp == 0 then
		grp = vint_object_clone(vint_object_find("style_footer", nil, CLOTHING_STORE_DOC_H), Menu_option_labels.control_parent)
	end

	vint_set_property(grp, "visible", true)

	menu_data.footer = {
		footer_grp = grp,
		price = vint_object_find("price_amount", grp),
		style = vint_object_find("style_amount", grp),
	}

	vint_set_property(menu_data.footer.style, "visible", Clothing_store_use_style)
end

function clothing_store_update_style_footer(menu_data)
	--debug_print("clothing_store_update_style_footer")
	local item = Clothing_store_item_info
	local fr = menu_data.footer

	if fr == nil then
		return
	end

	if fr.price ~= nil then
		if item.item_price > menu_store_get_player_cash() then
			vint_set_property(fr.price, "tint", 1, 0, 0)
		else
			vint_set_property(fr.price, "tint", 0.88, 0.749, 0.05)
		end

		vint_set_property(fr.price, "text_tag", "$"..format_cash(item.item_price))

		if menu_data.menu_width ~= nil then
			vint_set_property(fr.price, "anchor", menu_data.menu_width - 20, 0)
		end
	end

	if fr.style ~= 0 then
		--Localize style
		local insert_value = {[0] = award_style("clothing", item.item_style, true)}
		local style_string = vint_insert_values_in_string("STORE_ITEM_STYLE_AWARD", insert_value)
		vint_set_property(fr.style, "text_tag", style_string)
	end
end

function clothing_store_confirm_remove_item()
	--debug_print("clothing_store_confirm_remove_item")
	dialog_box_confirmation("CUST_REMOVE_ITEM_TITLE", "CUST_REMOVE_ITEM_BODY", "clothing_store_remove_item_finalize")
end

function clothing_store_remove_item_finalize(result, action)
	--debug_print("clothing_store_remove_item_finalize")
	if action ~= DIALOG_ACTION_CLOSE then
		return
	end

	if result == 0 then
		pcu_set_slots_empty(Clothing_store_current_category, true)
	end
end

function clothing_store_remove_item_no_warning()
	--debug_print("clothing_store_remove_item_no_warning")
	pcu_set_slots_empty(Clothing_store_current_category, true)
end

function clothing_store_build_item_list_menu(menu_data)
	--debug_print("clothing_store_build_item_list_menu")
	--reset the update values
	Clothing_store_item_update_value = CLOTHING_STORE_ITEM_UPDATE_VALUE_INVALID
	Clothing_store_item_info.item_index = CLOTHING_STORE_INVALID_INDEX
	clothing_store_purge_pending_updates()
	--debug_print("vint", "string name is"..var_to_string(Clothing_store_current_category).."\n");
	if Clothing_store_is_wardrobe == true then
			menu_data.num_items = 1
			menu_data[0] = { label = "CUST_ITEM_NOTHING", type = MENU_ITEM_TYPE_SELECTABLE, on_select = clothing_store_remove_item_no_warning, item_id = -1}
	else
		menu_data.num_items = 0
	end

	menu_data.highlighted_item = nil

	Clothing_store_building_menu = menu_data
	pcu_get_items_in_category(Clothing_store_current_category, "clothing_store_add_item_list_item")

	if menu_data.num_items > 0 then
		if menu_data.highlighted_item == nil then
			menu_data.highlighted_item = 0
		end

		clothing_store_item_list_nav(menu_data)

		if Clothing_store_is_wardrobe == false then
			menu_data.footer_height = CLOTHING_STORE_STYLE_FOOTER_HEIGHT
			clothing_store_build_style_footer(menu_data)
		else
			menu_data.footer_height = 0
		end
	end
end

function clothing_store_item_list_select()
	--debug_print("clothing_store_item_list_select")
	Clothing_store_item_details_menu.highlighted_item = nil
	if pcu_is_streaming_done() == true and Clothing_store_item_update_thread == -1 and Clothing_store_waiting_update_value == -1 then
		menu_show(Clothing_store_item_details_menu, MENU_TRANSITION_SWEEP_LEFT)
	end
end

function clothing_store_item_notify_owned()
	--debug_print("clothing_store_item_notify_owned")
	--dialog_box_message("MENU_TITLE_NOTICE", "ALL_VARIANTS_ALREADY_OWNED", true, true)
end

function clothing_store_add_item_list_item(item_id, label_crc, label_str, is_outfit, price, style, inc_wardrobe_instance, is_available)
	-- Blacklist a problematic clothing item [nclok1405]
	if label_crc == ITEM_CRC_FLASHER_COAT_WITH_MORPHS then
		is_available = false
	end

	--debug_print("clothing_store_add_item_list_item")
	local i = Clothing_store_building_menu.num_items
	local new_item;
	--debug_print("vint", "availability = "..var_to_string(is_available).."\n")
	if is_available ~= false then
		if Clothing_store_is_wardrobe == false and mp_is_enabled() == true and pcu_is_item_owned(item_id, nil) == true then
			-- We own all of this item's styles, so you can't actually select details
			new_item = { type = MENU_ITEM_TYPE_SELECTABLE, on_select = clothing_store_item_notify_owned, item_id = item_id, wardrobe_instance = inc_wardrobe_instance }
		else
			new_item = { type = MENU_ITEM_TYPE_SELECTABLE, sub_menu = Clothing_store_item_details_menu, on_select = clothing_store_item_list_select, item_id = item_id, wardrobe_instance = inc_wardrobe_instance }
		end
	else
		new_item = { type = MENU_ITEM_TYPE_SELECTABLE, item_id = item_id, wardrobe_instance = inc_wardrobe_instance }
	end

	if label_crc ~= nil then
		new_item.label_crc = label_crc
	else
		new_item.label = label_str
	end
	if is_outfit ~= nil and is_outfit == true then
		if Clothing_store_is_wardrobe == false then
			new_item.is_outfit = true
			new_item.sub_menu = nil
			new_item.on_select = clothing_store_purchase_item
			new_item.item_price = price
			new_item.item_style = style
		else
			new_item.is_outfit = true
			new_item.sub_menu = nil
			new_item.on_select = clothing_store_wear_item
			new_item.item_price = nil    --for non outfits, these should be set in get_item_defaults
			new_item.item_style = nil
		end
	else
		new_item.is_outfit = false
		if pcu_is_wearing_item(item_id) == true then
			Clothing_store_building_menu.highlighted_item = i
		end
	end
	Clothing_store_building_menu[i] = new_item
	Clothing_store_building_menu.num_items = i + 1
end

function clothing_store_item_list_back()
	--debug_print("clothing_store_item_list_back")

	if pcu_is_streaming_done() then
		if Clothing_store_item_update_thread ~= -1 then
			thread_kill(Clothing_store_item_update_thread)
			Clothing_store_item_update_thread = -1
		end
		audio_play(Menu_sound_back)

		local unavailable_grp_h = vint_object_find("preview_unavailable_grp")
		vint_set_property(unavailable_grp_h, "visible", false)
		pcu_clear_preview_slot()

		-- If back was called from the outfit menu then kill all the misc slots so they don't carry back over _IdolNinja
		if Accessory_Test == "OUTFIT" then

			pcu_set_slots_empty(57) -- MISC 1
			pcu_set_slots_empty(58) -- MISC 2
			pcu_set_slots_empty(59) -- MISC 3
			Accessory_Test = "NOTOUTFIT" -- set back to default state
		end
		menu_show(Menu_active.parent_menu, MENU_TRANSITION_SWEEP_RIGHT)
	end
end

function clothing_store_delayed_item_update()

	--debug_print("clothing_store_delayed_item_update")
	delay(0.4)
	clothing_store_preview_item(false)
	Clothing_store_item_update_thread = -1
end

function clothing_store_item_list_nav(menu_data)
	if Accessory_Test == "OUTFIT" then -- set at the very end of preview_store_outfit so this will only run if you are currently looking at a store outfit
		--debug_print("The value of Accessory Test is"..var_to_string(Accessory_Test))

		Accessory_Test = "NOTOUTFIT" -- Set back to default state
	end


	--debug_print("clothing_store_item_list_nav")
	--debug_print("vint", "clothing_store_item_list_nav()\n")

	menu_palette_invalidate()

	if Clothing_store_item_update_thread ~= -1 then

		--debug_print("vint", "clothing_store_item_list_nav() : thread_kill(Clothing_store_item_update_thread)\n")
		thread_kill(Clothing_store_item_update_thread)
	end

	Clothing_store_item_update_value = menu_data[menu_data.highlighted_item]
	local i = menu_data[menu_data.highlighted_item]
	if i.is_outfit ~= true then                 --if it's not an outfit, we need to read in a bunch of values
		if Clothing_store_is_wardrobe == false then
			clothing_store_get_item_defaults(i.item_id)
		else
			if i.label == "CUST_ITEM_NOTHING" then
				Clothing_store_item_info.item_index = CLOTHING_STORE_INVALID_INDEX
			else
				clothing_store_get_owned_item_info(i.item_id, i.wardrobe_instance)
				Clothing_store_item_info.wardrobe_instance = i.wardrobe_instance --store the instance of the current item incase we need to discard
			end
		end
	else


		Clothing_store_item_info.item_price = i.item_price  --if it as an outfit, then we've already read in the price/style
		Clothing_store_item_info.item_style = i.item_style
		Clothing_store_item_info.item_slot = CLOTHING_STORE_INVALID_SLOT --this is done so you can't mistakingly think a suit is an item and call functions with it
		Clothing_store_item_info.slot_index = CLOTHING_STORE_INVALID_INDEX
	end

	Clothing_store_item_update_thread = thread_new("clothing_store_delayed_item_update")
	clothing_store_update_style_footer(menu_data)
end

function clothing_store_details_style_select()
	--debug_print("clothing_store_details_style_select")
	local m = Clothing_store_style_menu
	local i = Clothing_store_item_info
	m.num_items = 0
	m.parent_menu = Clothing_store_item_details_menu

	Clothing_store_original_value = i.variant_index

	pcu_get_variants(i.slot_index, "clothing_store_style_add")
	menu_show(m, MENU_TRANSITION_SWEEP_LEFT)
end

function clothing_store_style_delayed_set()
	--debug_print("clothing_store_style_delayed_set")
	delay(0.4)
	clothing_store_style_set(Clothing_store_item_update_value)
	Clothing_store_item_update_thread = -1
end

function clothing_store_style_nav(menu_data)
	--debug_print("clothing_store_style_nav")
	if Clothing_store_item_update_thread ~= -1 then
		thread_kill(Clothing_store_item_update_thread)
	end

	Clothing_store_item_update_value = menu_data[menu_data.highlighted_item].variant_index
	Clothing_store_item_update_thread = thread_new("clothing_store_style_delayed_set")
end

function clothing_store_style_set(variant_index)
	--debug_print("clothing_store_style_set")
	Clothing_store_item_info.variant_index = variant_index
	clothing_store_preview_item(true)
	--clothing_store_get_slot_info(Clothing_store_item_info.slot_index)
end

function clothing_store_style_select(menu_label, menu_data)
	--debug_print("clothing_store_style_select")
	Clothing_store_menu_when_done_updating = Clothing_store_item_details_menu;
	clothing_store_style_set(menu_data.variant_index)
end

function clothing_store_style_add(variant_index, name_crc, name_str)
	--debug_print("clothing_store_style_add")
	local m = Clothing_store_style_menu
	local n = m.num_items

	m[n] = {
		label = name_str, label_crc = name_crc, type = MENU_ITEM_TYPE_SELECTABLE, variant_index = variant_index,
		on_select = clothing_store_style_select
	}

	if variant_index == Clothing_store_item_info.variant_index then
		m.highlighted_item = n
	end

	m.num_items = n + 1
end

function clothing_store_style_back(menu_data)
	--debug_print("clothing_store_style_back")
	if Clothing_store_item_update_thread ~= -1 then
		thread_kill(Clothing_store_item_update_thread)
		Clothing_store_item_update_thread = -1
	end
	audio_play(Menu_sound_back)

	Clothing_store_item_info.variant_index = Clothing_store_original_value
	Clothing_store_menu_when_done_updating = Menu_active.parent_menu
	clothing_store_preview_item(true)
	--clothing_store_get_slot_info(Clothing_store_item_info.slot_index)

end

function clothing_store_outfit_menu_on_show()
	--debug_print("clothing_store_outfit_menu_on_show")
	clothing_store_purge_pending_updates()
	pcu_clear_obscured_slots()
	store_set_camera_pos("body", true)
	pcu_set_suits_active_category()
end

function clothing_store_purchase_item()
	--debug_print("clothing_store_purchase_item")
	if (pcu_is_streaming_done() and Clothing_store_waiting_update_value == -1 and Clothing_store_item_update_thread == -1) then
		clothing_store_purge_pending_updates()
		local item = Clothing_store_item_info

		if mp_is_enabled() == true and pcu_is_item_owned(item.item_index, item.variant_index) == true then
			--dialog_box_message("MENU_TITLE_NOTICE", "VARIANT_ALREADY_OWNED", true, true)
			return
		end

		if item.item_price > menu_store_get_player_cash() then
			dialog_box_message("MENU_TITLE_NOTICE", "HUD_SHOP_INSUFFICIENT_FUNDS", true, true)
			return
		end

		dialog_box_confirmation("STORE_TITLE_PURCHASING", "STORE_TEXT_CONFIRM_PURCHASE_BLANK", "clothing_store_purchase_finalize_1", true, true)
	end
end

function clothing_store_wear_item()
	--debug_print("clothing_store_wear_item")
	if pcu_is_streaming_done() and Clothing_store_waiting_update_value == -1 then
		pcu_wear_current_clothing()
		Clothing_Wear_Test = "WORN"
		menu_show(Clothing_store_top_menu, MENU_TRANSITION_SWEEP_LEFT)
	end
end

function clothing_store_discard_item()
	--debug_print("clothing_store_discard_item")
	--debug_print("vint", "I think the category is"..var_to_string(Clothing_store_current_category).."\n")
	if pcu_is_current_item_worn(Clothing_store_item_info.slot_index, Clothing_store_item_info.wardrobe_instance) then
		--debug_print("vint", "I'm wearing the item i'm about to discard\n")
		dialog_box_confirmation("STORE_TITLE_DISCARD", "STORE_TEXT_DISCARD", "clothing_store_discard_finalize1", true, true)
	else
		--debug_print("vint", "I don't think the item is worn.\n")
		dialog_box_confirmation("STORE_TITLE_DISCARD", "STORE_TEXT_DISCARD", "clothing_store_discard_finalize1", true, true)
	end
end

function clothing_store_purchase_finalize_1(response, action)
	--debug_print("clothing_store_purchase_finalize_1")
	if action ~= DIALOG_ACTION_CLOSE then
		return
	end

	if response ~= 0 then
		return
	end
	--there used to be item slot conflict checking here
	clothing_store_purchase_finalize_2(0, DIALOG_ACTION_CLOSE)


end

function clothing_store_purchase_finalize_2(response, action)
	--debug_print("clothing_store_purchase_finalize_2")
	if action ~= DIALOG_ACTION_CLOSE then
		return
	end

	if response ~= 0 then
		return
	end

	if mp_is_enabled() == false then
		award_style("clothing", Clothing_store_item_info.item_style)
	end

	--clothing_store_preview_item()
	if type(Clothing_store_item_update_value) == "table" and Clothing_store_item_update_value.is_outfit == true then
		--debug_print("vint", "trying to purchase outfit with ID: "..var_to_string(Clothing_store_item_update_value.item_id).."\n")
		pcu_purchase_outfit(Clothing_store_item_update_value.item_id)
	else
		--debug_print("vint", "trying to item in slot "..var_to_string(Clothing_store_item_info.slot_index).."\n")
		pcu_purchase_slot(Clothing_store_item_info.slot_index)
	end
	clothing_store_wear_item()
	menu_show(Clothing_store_top_menu, MENU_TRANSITION_SWEEP_LEFT)
	audio_play(Menu_sound_purchase)
end

function clothing_store_discard_finalize1(response, action)
	--debug_print("clothing_store_discard_finalize1")
	if action ~= DIALOG_ACTION_CLOSE then
		return
	end

	if response ~= 0 then
		return
	end
	if pcu_is_item_needed_for_outfit(Clothing_store_item_info.slot_index) then
		dialog_box_confirmation("STORE_TITLE_DISCARD_OUTFIT_WARNING", "STORE_TEXT_DISCARD_OUTFIT_WARNING", "clothing_store_discard_finalize2", true, true)
	else
		pcu_discard_slot(Clothing_store_item_info.slot_index, Clothing_store_item_info.wardrobe_instance)
		menu_show(Clothing_store_top_menu, MENU_TRANSITION_SWEEP_LEFT)
	end
end

function clothing_store_discard_finalize2(response, action)
	--debug_print("clothing_store_discard_finalize2")
	if action ~= DIALOG_ACTION_CLOSE then
		return
	end

	if response ~= 0 then
		return
	end

	pcu_discard_slot(Clothing_store_item_info.slot_index, Clothing_store_item_info.wardrobe_instance)
	menu_show(Clothing_store_top_menu, MENU_TRANSITION_SWEEP_LEFT)
end

function clothing_store_details_nav(menu_data)
	--debug_print("clothing_store_details_nav")
	menu_palette_invalidate()
end

function clothing_store_details_show(menu_data)
	--debug_print("clothing_store_details_show")
	-- kill preview thread
	if Clothing_store_item_update_thread ~= -1 then
		thread_kill(Clothing_store_item_update_thread)
		Clothing_store_item_update_thread = -1
	end

	-- set the header
	menu_data.header_label_crc = Clothing_store_item_info.item_name_crc
	menu_data.header_label_str = Clothing_store_item_info.item_name_str

	-- get info on the item
	clothing_store_preview_item(true)

	-- build the menu
	local num_items = 0
	local m = Clothing_store_item_details_menu
	local item = Clothing_store_item_info

	if item.colors.num_colors > 0 then
		local p = Clothing_store_clothing_palette
		local c = item.colors
		Clothing_store_clothing_palette.num_colors = c.num_colors

		for i = 0, c.num_colors - 1 do
			p[i].red		= c[i].red
			p[i].green	= c[i].green
			p[i].blue	= c[i].blue
		end

		local allow_color_selection = true  -- always allow color selection for everything -IdolNinja

		m[num_items] =	{
			label = "CUST_MENU_COLOR", type = MENU_ITEM_TYPE_PALETTE, palette_colors = p,
			on_select = clothing_store_palette_select, color_name = "clothing", disabled = (allow_color_selection == false)
		}

		num_items = num_items + 1
	end

	if item.num_variants > 1 then
		local allow_style_selection = Clothing_store_is_wardrobe == false or mp_is_enabled() == true
		m[num_items] = {
			label = "MENU_STYLE", type = MENU_ITEM_TYPE_INFO_BOX, on_select = clothing_store_details_style_select,
			info_text_str = item.variant_name_str, info_text_crc = item.variant_name_crc, disabled = (allow_style_selection == false)
		}
		num_items = num_items + 1
	end

	if item.num_logos > 0 then
		local allow_logo_selection = true -- always allow logo selection for everything -IdolNinja
		m[num_items] = { label = "CUST_MENU_LOGO", type = MENU_ITEM_TYPE_INFO_BOX, on_select = clothing_store_details_logo_select,
							disabled = (allow_logo_selection == false) }

		if Clothing_store_item_info.logo_index > -1 then
			m[num_items].info_text_str = Clothing_store_item_info.logo_name_str
			m[num_items].info_text_crc = Clothing_store_item_info.logo_name_crc

			local p = Clothing_store_logo_palette[0]
			p.red = Clothing_store_item_info.logo_color_red
			p.green = Clothing_store_item_info.logo_color_green
			p.blue = Clothing_store_item_info.logo_color_blue
		else
			m[num_items].info_text_str = "CUST_NO_ITEMS"
		end

		num_items = num_items + 1

		if item.logo_index > -1 then
			local allow_logo_color_selection = true -- always allow logo color selection for everything -IdolNinja
			m[num_items] = {
				label = "CUST_MENU_LOGO_COLOR", type = MENU_ITEM_TYPE_PALETTE, palette_colors = Clothing_store_logo_palette,
				on_select = clothing_store_palette_select, color_name = "logo", disabled = (allow_logo_color_selection == false)
			}
			num_items = num_items + 1
		end
	end

	if item.num_wear_options > 1 then
		m[num_items] = {
			label = "CUST_MENU_WEAR_OPTION", type = MENU_ITEM_TYPE_INFO_BOX, on_select = clothing_store_details_wear_option_select,
			info_text_str = item.wear_option_name_str, info_text_crc = item.wear_option_name_crc
		}
		num_items = num_items + 1
	end

	if Clothing_store_is_wardrobe == true then
		m[num_items] = { label = "CUST_ITEM_WEAR", type = MENU_ITEM_TYPE_SELECTABLE, on_select = clothing_store_wear_item }
		num_items = num_items + 1
		if mp_is_enabled()== false then
			m[num_items] = { label = "STORE_DISCARD_ITEM", type = MENU_ITEM_TYPE_SELECTABLE, on_select = clothing_store_discard_item }
			num_items = num_items + 1
		end
	else
		m[num_items] = { label = "STORE_PURCHASE_ITEM", type = MENU_ITEM_TYPE_SELECTABLE, on_select = clothing_store_purchase_item }
		num_items = num_items + 1
	end

	if Clothing_store_is_wardrobe == false then
		menu_data.footer_height = CLOTHING_STORE_STYLE_FOOTER_HEIGHT
		clothing_store_build_style_footer(menu_data)
	else
		menu_data.footer_height = 0
	end

	m.num_items = num_items
end

function clothing_store_details_logo_select()
	--debug_print("clothing_store_details_logo_select")
	Clothing_store_logo_list_menu.parent_menu = Menu_active
	menu_show(Clothing_store_logo_list_menu, MENU_TRANSITION_SWEEP_LEFT)
end

function clothing_store_palette_select(menu_label, menu_data)
	--debug_print("clothing_store_palette_select")
	if menu_data.color_name == "logo" and Clothing_store_item_info.logo_index < 0 then
		return
	end

	local i = menu_label.control.highlighted_index
	local m = Clothing_store_color_menu
	local p = menu_data.palette_colors[i]
	m.header_label_str = p.label_str
	m.header_label_crc = p.label_crc
	m.color_name = menu_data.color_name
	m.color_idx = i
	menu_show(Clothing_store_color_menu, MENU_TRANSITION_SWEEP_LEFT)
end

function clothing_store_wear_option_back(menu_data)
	--debug_print("clothing_store_wear_option_back")
	if Clothing_store_item_update_thread ~= -1 then
		thread_kill(Clothing_store_item_update_thread)
		Clothing_store_item_update_thread = -1
	end
	audio_play(Menu_sound_back)

	Clothing_store_item_info.wear_option_index = Clothing_store_original_value
	Clothing_store_menu_when_done_updating = Menu_active.parent_menu
	clothing_store_preview_item(true)
	--clothing_store_get_slot_info(Clothing_store_item_info.slot_index)


end

function clothing_store_wear_option_delayed_set()
	--debug_print("clothing_store_wear_option_delayed_set")
	delay(0.4)
	clothing_store_wear_option_set(Clothing_store_item_update_value)
	Clothing_store_item_update_thread = -1
end

function clothing_store_wear_option_nav(menu_data)
	--debug_print("clothing_store_wear_option_nav")
	if Clothing_store_item_update_thread ~= -1 then
		thread_kill(Clothing_store_item_update_thread)
	end

	Clothing_store_item_update_value = menu_data[menu_data.highlighted_item].option_index
	Clothing_store_item_update_thread = thread_new("clothing_store_wear_option_delayed_set")
end

function clothing_store_wear_option_set(option_index)
	--debug_print("clothing_store_wear_option_set")
	Clothing_store_item_info.wear_option_index = option_index
	clothing_store_preview_item(true)
	--clothing_store_get_slot_info(Clothing_store_item_info.slot_index)
end

function clothing_store_wear_option_select(menu_label, menu_data)
	--debug_print("clothing_store_wear_option_select")
	Clothing_store_menu_when_done_updating = Clothing_store_item_details_menu
	clothing_store_wear_option_set(menu_data.option_index)
end

function clothing_store_wear_option_add(option_index, name_crc, name_str)
	--debug_print("clothing_store_wear_option_add")
	local m = Clothing_store_wear_options_menu
	local n = m.num_items

	m[n] = {
		label = name_str, label_crc = name_crc, type = MENU_ITEM_TYPE_SELECTABLE, option_index = option_index,
		on_select = clothing_store_wear_option_select
	}

	if option_index == Clothing_store_item_info.wear_option_index then
		m.highlighted_item = n
	end

	m.num_items = n + 1
end

function clothing_store_details_wear_option_select(menu_label, menu_data)
	--debug_print("clothing_store_wear_option_select")
	local m = Clothing_store_wear_options_menu
	local i = Clothing_store_item_info
	m.num_items = 0
	m.parent_menu = Clothing_store_item_details_menu

	Clothing_store_original_value = Clothing_store_item_info.wear_option_index

	pcu_get_wear_options(i.slot_index, "clothing_store_wear_option_add")
	menu_show(m, MENU_TRANSITION_SWEEP_LEFT)
end

function clothing_store_color_grid_show(menu_data)
	--debug_print("clothing_store__color_grid_show")
	menu_data.parent_menu = Clothing_store_item_details_menu
	if menu_data.color_name == "logo" then
		Clothing_store_original_value = Clothing_store_item_info.logo_color_index
		Clothing_store_item_update_value = 0
	else
		Clothing_store_original_value = Clothing_store_item_info.colors[menu_data.color_idx].index
		Clothing_store_item_update_value = Clothing_store_item_info.colors[menu_data.color_idx].index
	end

	local menu_item = menu_data[0]

	menu_item.swatches = { num_swatches = 0 }
	Clothing_store_building_menu = menu_data
	pcu_report_item_colors("clothing_store_add_color", Clothing_store_item_info.item_index)

	local swatch_template = vint_object_find("swatch_color", nil, MENU_BASE_DOC_HANDLE)
	menu_grid_show(menu_data, menu_item, swatch_template)
	clothing_store_color_grid_nav(menu_data, menu_item)
end

function clothing_store_add_color(color_index, label_crc, label_str, red, green, blue)
	--debug_print("clothing_store_add_color")
	local item = {
		color_index = color_index, red = red, green = green, blue = blue, label_crc = label_crc, label_str = label_str
	}

	local swatches = Clothing_store_building_menu[0].swatches
	local n = swatches.num_swatches
	swatches[n] = item

	if Clothing_store_color_menu.color_name == "logo" then
		if Clothing_store_item_info.logo_color_index == color_index then
			Clothing_store_building_menu[0].cur_idx = n
		end
	else
		if Clothing_store_item_info.colors[Clothing_store_color_menu.color_idx].index == color_index then
			Clothing_store_building_menu[0].cur_idx = n
		end
	end

	swatches.num_swatches = n + 1
end

function clothing_store_color_grid_release(menu)
	--debug_print("clothing_store_color_grid_release")
	menu_grid_release(menu[0])
end

function clothing_store_color_grid_back(menu_data)
	--debug_print("clothing_store_color_grid_back")
	if Clothing_store_item_update_thread ~= -1 then
		thread_kill(Clothing_store_item_update_thread)
		Clothing_store_item_update_thread = -1
	end
	audio_play(Menu_sound_back)

	if menu_data.color_name == "logo" then
		Clothing_store_item_info.logo_color_index = Clothing_store_original_value
	else
		Clothing_store_item_info.colors[menu_data.color_idx].index = Clothing_store_original_value
	end
	Clothing_store_menu_when_done_updating = Menu_active.parent_menu
	clothing_store_preview_item(true)

end

function clothing_store_apply_item_color()
	--debug_print("clothing_store_apply_item_color")
	if Clothing_store_color_menu.color_name == "logo" then
		Clothing_store_item_info.logo_color_index = Clothing_store_item_update_value
	else
		Clothing_store_item_info.colors[Clothing_store_color_menu.color_idx].index =
			Clothing_store_item_update_value
	end

	clothing_store_preview_item(true)
	--clothing_store_get_slot_info(Clothing_store_item_info.slot_index)
end

function clothing_store_color_grid_select()
	--debug_print("clothing_store_color_grid_select")
	if Clothing_store_item_update_thread ~= -1 then
		thread_kill(Clothing_store_item_update_thread)
		Clothing_store_item_update_thread = -1
	end

	Clothing_store_menu_when_done_updating = Clothing_store_item_details_menu
	clothing_store_apply_item_color()
end

function clothing_store_delayed_color_update()
	--debug_print("clothing_store_delayed_color_update")
	delay(0.4)
	clothing_store_apply_item_color()
	Clothing_store_item_update_thread = -1
end

function clothing_store_color_grid_nav()
	--debug_print("clothing_store_color_grid_nav")
	if Clothing_store_item_update_thread ~= -1 then
		thread_kill(Clothing_store_item_update_thread)
	end

	local item = Clothing_store_color_menu[0]
	local swatches = item.swatches
	local cur_swatch = item.cur_row * item.num_cols + item.cur_col
	Clothing_store_item_update_value = swatches[cur_swatch].color_index
	Clothing_store_item_update_thread = thread_new("clothing_store_delayed_color_update")
end

function clothing_store_color_update_swatch(swatch)
	--debug_print("clothing_store_color_update_swatch")
	local fill = vint_object_find("fill", swatch.swatch_h)
	vint_set_property(fill, "tint", swatch.red, swatch.green, swatch.blue)
end

--------------------[ LOGO LIST GRID ]----------------------

function clothing_store_logo_list_add_swatch(logo_id, swatch_crc, label_crc, label_str)
	--debug_print("clothing_store_logo_list_add_swatch")
	local swatches = Clothing_store_building_menu[0].swatches
	local n = swatches.num_swatches

	swatches[n] = { logo_id = logo_id, swatch_crc = swatch_crc, label_crc = label_crc, label_str = label_str }

	--Match logo id with the item the player is wearing...
	if logo_id == Clothing_store_item_info.logo_index then
		Clothing_store_building_menu[0].cur_idx = n
	end

	swatches.num_swatches = n + 1
end

function clothing_store_logo_list_back(menu_option, menu_data)
	--debug_print("clothing_store_logo_list_back")
	if Clothing_store_item_update_thread > -1 then
		thread_kill(Clothing_store_item_update_thread)
		Clothing_store_item_update_thread = -1
	end
	audio_play(Menu_sound_back)

	Clothing_store_item_info.logo_index = Clothing_store_original_value
	Clothing_store_menu_when_done_updating = Menu_active.parent_menu
	clothing_store_preview_item(true);
	--clothing_store_get_slot_info(Clothing_store_item_info.slot_index)
end

function clothing_store_logo_list_delayed_update()
	--debug_print("clothing_store_logo_list_delayed_update")
	delay(0.4)
	clothing_store_logo_list_update()
	Clothing_store_item_update_thread = -1
end

function clothing_store_logo_list_nav(menu_option, menu_data)
	--debug_print("clothing_store_logo_list_nav")
	if Clothing_store_item_update_thread > -1 then
		thread_kill(Clothing_store_item_update_thread)
		Clothing_store_item_update_thread = -1
	end

	local swatches = menu_data.swatches
	local idx = menu_data.cur_row * menu_data.num_cols + menu_data.cur_col

	if idx < swatches.num_swatches then
		Clothing_store_item_update_value = swatches[idx].logo_id
		Clothing_store_item_update_thread = thread_new("clothing_store_logo_list_delayed_update")
	end
end

function clothing_store_logo_list_release(menu)
	--debug_print("clothing_store_logo_list_release")
	menu_grid_release(menu[0])
	--peg_unload("ui_cl_logos")
end

function clothing_store_logo_list_select(menu_option, menu_data)
	--debug_print("clothing_store_logo_list_select")
	if Clothing_store_item_update_thread > -1 then
		thread_kill(Clothing_store_item_update_thread)
		Clothing_store_item_update_thread = -1
	end
	Clothing_store_menu_when_done_updating = Clothing_store_item_details_menu
	clothing_store_logo_list_update()
end

function clothing_store_logo_list_show(menu_data)
	--debug_print("clothing_store_logo_list_show")
	Clothing_store_original_value = Clothing_store_item_info.logo_index
	Clothing_store_item_update_value = Clothing_store_item_info.logo_index
	local menu_item = menu_data[0]

	menu_item.swatches = { num_swatches = 1}
	menu_item.swatches[0] = { logo_id = -1, swatch_str = "ui_menu_none", label_str = "CUST_NO_ITEMS" }

	--Reseting current index for the menu item to nil to initialize the menu.
	menu_item.cur_idx = nil

	Clothing_store_building_menu = menu_data
	pcu_report_logos(Clothing_store_item_info.item_index, "clothing_store_logo_list_add_swatch")

	peg_load("ui_cl_logos")

	menu_grid_show(menu_data, menu_item)

	menu_data.footer_height = 0
end

function clothing_store_logo_list_update()
	--debug_print("clothing_store_logo_list_update")
	Clothing_store_item_info.logo_index = Clothing_store_item_update_value
	clothing_store_preview_item(true)
	--clothing_store_get_slot_info(Clothing_store_item_info.slot_index)
end

function clothing_store_switch_mode()
	--debug_print("clothing_store_switch_mode")
	if Clothing_store_allow_swap == true then
		if Menu_swap_interface_reload_name ~= 0 then 	--This means a swap is in progress
			return
		end
		if Clothing_store_allow_wardrobe == false then
			return
		end
		menu_input_block(true)

		if Clothing_store_name == "WARDROBE" then
			Clothing_store_name = Clothing_store_original_name
			Clothing_store_display_name = Clothing_store_original_display_name;
			Clothing_store_is_wardrobe = false
		else
			Clothing_store_name = "WARDROBE"
			Clothing_store_display_name = CLOTHING_STORE_WARDROBE_DISPLAY_NAME
			Clothing_store_is_wardrobe = true
		end

		Menu_swap_interface_unload_handle = CLOTHING_STORE_DOC_H
		Menu_swap_interface_reload_name = vint_document_get_name_from_handle(CLOTHING_STORE_DOC_H)
		Menu_swap_callback_function = clothing_store_switch_callback
		Menu_swap_in_progress = true
		menu_swap_interface(Clothing_store_display_name, vint_menu_swap_unload)
	end
end

function clothing_store_switch_callback()
	--debug_print("clothing_store_switch_callback")
	menu_input_block(false)
	pcu_reset_handle(CLOTHING_STORE_DOC_H)
end

function clothing_store_wardrobe_create_outfit_verify()
	--debug_print("clothing_store_wardrobe_create_outfit_verify")
	local success, reason_title, reason_body
	success, reason_title, reason_body = pcu_can_create_outfit()
	if success == true then
		clothing_store_wardrobe_create_outfit()
	else
		dialog_box_message(reason_title, reason_body)
	end
end

function clothing_store_wardrobe_create_outfit()
	--debug_print("clothing_store_wardrobe_create_outfit")
	vkeyboard_input("OUTFIT_NAME", "OUTFIT_NAME_DESC", 16, "OUTFIT_NAME_TAG", "clothing_store_outfit_name_cb", true)
end

function clothing_store_outfit_name_cb(success)
	--debug_print("clothing_store_outfit_name_cb")
	if success == true then
		pcu_create_outfit("VKEYBOARD_RESULTS")
	end
end

function clothing_store_remove_clothing()
	--debug_print("clothing_store_remove_clothing")
	dialog_box_confirmation("CUST_DIALOG_DISROBE_TITLE", "CUST_DIALOG_DISROBE_BODY", "clothing_store_remove_clothing_confirm", true, true)
end

function clothing_store_remove_clothing_confirm(result, action)
	--debug_print("clothing_store_remove_clothing_confirm")
	if action ~= DIALOG_ACTION_CLOSE then
		return
	end

	if result ~= 0 then
		return
	end

	pcu_remove_clothing()
end

-- Crib Store: Switch to Branded [nclok1405]
function crib_store_clothing()
	Clothing_store_original_name = "Branded"
	clothing_store_switch_mode()
end

-- Crib Store: Switch to On Thin Ice [nclok1405]
function crib_store_jewelry()
	Clothing_store_original_name = "On_Thin_Ice"
	clothing_store_switch_mode()
end

-- Crib Store: Switch to Rusty's Needle [nclok1405]
function crib_store_tattoo()
	Clothing_store_original_name = "Rusty's_Needle"
	clothing_store_switch_mode()
end

function clothing_store_view_outfits_show(menu_data)
	--debug_print("clothing_store_view_outfits_show")
	menu_data.num_items = 0

	pcu_report_outfits("clothing_store_view_outfits_add")

	if menu_data.num_items == 0 then
		menu_data.num_items = 1
		menu_data[0] = { label = CLOTHING_STORE_NO_OUTFITS_DISPLAY_NAME, type = MENU_ITEM_TYPE_SELECTABLE }
	else
		menu_data.highlighted_item = 0
		clothing_store_view_outfits_nav(menu_data)
	end
end

function clothing_store_view_outfits_add(outfit_idx)
	--debug_print("clothing_store_view_outfits_add")
	local i = Clothing_store_wardrobe_view_outfits_menu.num_items

	Clothing_store_wardrobe_view_outfits_menu[i] = { label = "{OUTFIT_NAME_"..outfit_idx.."}", type = MENU_ITEM_TYPE_SELECTABLE, outfit_index = outfit_idx, on_select = clothing_store_view_outfits_select}
	i = i + 1
	Clothing_store_wardrobe_view_outfits_menu.num_items = i
end

function clothing_store_view_outfits_nav(menu_data)
	--debug_print("clothing_store_view_outfits_nav")
	if menu_data[menu_data.highlighted_item].outfit_index ~= nil then
		Clothing_store_item_update_value = menu_data[menu_data.highlighted_item].outfit_index;

		if Clothing_store_item_update_thread ~= -1 then
			thread_kill(Clothing_store_item_update_thread)
		end

		Clothing_store_item_update_thread = thread_new("clothing_store_preview_player_outfit")
	else
		Clothing_store_item_update_value = CLOTHING_STORE_ITEM_UPDATE_VALUE_INVALID;
	end
end

function clothing_store_preview_single_item()
	--debug_print("clothing_store_preview_single_item")
	Clothing_store_waiting_update_value = -1 --this is done so that the update thread never processes incompelete data
	Clothing_store_update_type = 1
	Clothing_store_menu_when_done_updating_safe = Clothing_store_menu_when_done_updating
	Clothing_store_waiting_update_value = 1 -- this needs to not be = -1 so we know to update
end


function clothing_store_preview_store_outfit()
	--debug_print("clothing_store_preview_store_outfit")
	Clothing_store_waiting_update_value = -1
	Clothing_store_update_type = 2
	Clothing_store_menu_when_done_updating_safe = Clothing_store_menu_when_done_updating
	Clothing_store_menu_when_done_updating = -1
	Clothing_store_waiting_update_value = Clothing_store_item_update_value.item_id

	Accessory_Test = "OUTFIT" --set this so that if the user goes back a menu it will process the if then block in item_list_back() to unequip the misc slots

end

function clothing_store_preview_player_outfit()
	--debug_print("clothing_store_preview_player_outfit")
	Clothing_store_waiting_update_value = -1
	Clothing_store_update_type = 3
	Clothing_store_menu_when_done_updating_safe = Clothing_store_menu_when_done_updating
	Clothing_store_menu_when_done_updating = -1
	Clothing_store_waiting_update_value = Clothing_store_item_update_value
end



function clothing_store_preview_update()  --this thread should be always running in the background when suits are being previewed
	--debug_print("clothing_store_preview_update")
	while true do
	if LoopTest == 0 then
		--debug_print("WHILE LOOP PROCESSED")
		LoopTest = 1
	end
		if pcu_is_streaming_done() then

			if StreamTest == 0 then
				--debug_print("STREAMING DONE")
				StreamTest = 1
			end

			--delay(0.2)
			if Clothing_store_waiting_update_value ~= -1 then
				--debug_print("vint", "WAITING UPDATE VALUE IS "..var_to_string(Clothing_store_waiting_update_value).."\n")
				--debug_print("vint", "UPDATE TYPE IS "..var_to_string(Clothing_store_update_type).."\n")
				if Clothing_store_update_type == 1 then
					local t = Clothing_store_item_info
					--debug_print("vint", "updating single item with logo "..var_to_string(t.logo_index).."\n")
					if t.slot_index ~= CLOTHING_STORE_INVALID_INDEX then  --makes sure the item is initialized before trying to preview it
						if t.item_index < 0 or t.wear_option_index < 0 then
							pcu_set_slots_empty(Clothing_store_current_category)
						else
							pcu_set_slot_info(t.slot_index, t.item_index, t.variant_index, t.colors.num_colors, t.colors[0].index,
							t.colors[1].index, t.colors[2].index, t.wear_option_index, t.logo_index, t.logo_color_index, true)
						end
					end
					if t.slot_index ~= nil then
						clothing_store_get_slot_info(t.slot_index)
					end
				end
				if Clothing_store_update_type == 2 then
					--debug_print("vint", "updating store outfit\n")
					while SlotEmptyLock == 1 do
						thread_yield()
					end
					SlotEmptyLock = 1
					pcu_set_slots_empty(57) -- MISC 1
					pcu_set_slots_empty(58) -- MISC 2
					pcu_set_slots_empty(59) -- MISC 3
					delay(0.3)
					SlotEmptyLock = 0

					pcu_wear_store_outfit(Clothing_store_waiting_update_value)
				end
				if Clothing_store_update_type == 3 then
					--debug_print("vint", "updating player outfit\n")
					while SlotEmptyLock == 1 do
						thread_yield()
					end
					SlotEmptyLock = 1
					pcu_set_slots_empty(57) -- MISC 1
					pcu_set_slots_empty(58) -- MISC 2
					pcu_set_slots_empty(59) -- MISC 3
					delay(0.3)
					SlotEmptyLock = 0

					pcu_wear_outfit(Clothing_store_waiting_update_value)
				end
				if Clothing_store_menu_when_done_updating_safe ~= -1 then
					menu_show(Clothing_store_menu_when_done_updating_safe, MENU_TRANSITION_SWEEP_RIGHT)
					Clothing_store_menu_when_done_updating_safe = -1
					Clothing_store_menu_when_done_updating = -1
				end
			Clothing_store_waiting_update_value = -1
			end

		end
		thread_yield()
	end
end

function clothing_store_view_outfits_back()
	--debug_print("clothing_store_view_outfits_back")
	--pcu_clear_preview_slot()  --this may needed to be added back in, but it needs to be tested with outfits
	audio_play(Menu_sound_back)
	menu_show(Menu_active.parent_menu, MENU_TRANSITION_SWEEP_RIGHT)
	pcu_set_slots_empty(57) -- MISC 1
	pcu_set_slots_empty(58) -- MISC 2
	pcu_set_slots_empty(59) -- MISC 3
	delay(0.6)
end

function clothing_store_delete_outfit_show(menu_data)
	--debug_print("clothing_store_delete_outfit_show")
	menu_data.num_items = 0

	pcu_report_outfits("clothing_store_delete_outfit_add")

	if menu_data.num_items == 0 then
		menu_data.num_items = 1
		menu_data[0] = { label = "NO_OUTFITS_DISPLAY_NAME", type = MENU_ITEM_TYPE_SELECTABLE }
	else
		menu_data.highlighted_item = 0
		clothing_store_delete_outfits_nav(menu_data)
	end
end

function clothing_store_delete_outfit_add(outfit_idx)
	--debug_print("clothing_store_delete_outfit_add")
	local i = Clothing_store_wardrobe_delete_outfit_menu.num_items

	Clothing_store_wardrobe_delete_outfit_menu[i] =
		{ label = "{OUTFIT_NAME_"..outfit_idx.."}", type = MENU_ITEM_TYPE_SELECTABLE, outfit_index = outfit_idx, on_select = clothing_store_delete_outfits_select }
	i = i + 1
	Clothing_store_wardrobe_delete_outfit_menu.num_items = i
end

function clothing_store_delete_outfits_nav(menu_data)
	--debug_print("clothing_store_delete_outfits_nav")
	Clothing_store_item_update_value = menu_data[menu_data.highlighted_item].outfit_index

	if Clothing_store_item_update_thread ~= -1 then
		thread_kill(Clothing_store_item_update_thread)
	end

	Clothing_store_item_update_thread = thread_new("clothing_store_preview_player_outfit")
end

function clothing_store_delete_outfits_select()
	--debug_print("clothing_store_delete_outfits_select")
	dialog_box_confirmation("CUST_ITEM_DELETE_OUTFIT", "CONFIRM_DELETE_OUTFIT", "clothing_store_delete_outfit_confirm", true, true)
end

function clothing_store_delete_outfit_confirm(result, action)
	--debug_print("clothing_store_delete_outfit_confirm")
	if action ~= DIALOG_ACTION_CLOSE then
		return
	end

	if result ~= 0 then
		return
	end

	pcu_delete_outfit(Clothing_store_item_update_value)
	pcu_clear_preview_slot()
	menu_show(Clothing_store_wardrobe_outfit_menu, MENU_TRANSITION_SWEEP_LEFT)
end

function clothing_store_view_outfits_select()
	--debug_print("clothing_store_view_outfits_select")
	if (pcu_is_streaming_done()) then
		if Clothing_store_item_update_value ~= CLOTHING_STORE_ITEM_UPDATE_VALUE_INVALID then
			pcu_wear_outfit(Clothing_store_item_update_value)
			dialog_box_confirmation("WEAR OUTFIT", "CONFIRM_WEAR_OUTFIT", "clothing_store_wear_outfit_confirm")
		else
			if Clothing_store_item_update_thread ~= -1 then
				thread_kill(Clothing_store_item_update_thread)
				Clothing_store_item_update_thread = -1
			end
		end
	end
end

function clothing_store_wear_outfit_confirm(result, action)
	--debug_print("clothing_store_wear_outfit_confirm")
	if action ~= DIALOG_ACTION_CLOSE then
		return
	end

	if result ~= 0 then
		return
	end

	pcu_wear_outfit(Clothing_store_item_update_value, true)
	menu_show(Clothing_store_wardrobe_outfit_menu, MENU_TRANSITION_SWEEP_LEFT)
end

function clothing_store_badge_add(idx, bmp, name, current)
	--debug_print("clothing_store_badge_add")
	local s = Clothing_store_mp_badges_menu[0].swatches
	local i = s.num_swatches

	s[i] = { badge_id = idx, swatch_str = bmp, label_str = name }

	if current == true then
		Clothing_store_mp_badges_menu[0].cur_idx = i
	end

	s.num_swatches = i + 1
end

function clothing_store_badges_show(menu_data)
	--debug_print("clothing_store_badges_show")
	peg_load("ui_multiplayer")
	local menu_item = menu_data[0]

	-- setup the swatches
	menu_item.swatches = { num_swatches = 0, cur_row = 0, cur_col = 0 }
	pcu_report_avail_mp_badges("clothing_store_badge_add")
	menu_grid_show(menu_data, menu_item)
end

function clothing_store_badge_select(menu_label, menu_data)
	--debug_print("clothing_store_badge_select")
	local swatches = menu_data.swatches
	local idx = menu_data.cur_row * menu_data.num_cols + menu_data.cur_col

	if idx < swatches.num_swatches then
		pcu_set_mp_badge(swatches[idx].badge_id)

		local str1 = vint_insert_values_in_string("CUST_BADGE_SELECTED", { [0] = swatches[idx].label_str })
		local str2 = vint_insert_values_in_string("{0}\n\n{1}", { [0] = swatches[idx].label_str.."_DESC", [1] = str1 })
		dialog_box_message("CUST_ICON_BADGES", str2)
	end
end

function clothing_store_badge_nav(menu_label, menu_data)
	--debug_print("clothing_store_badge_nav")
	--Do nothing
end

function clothing_store_badges_release(menu_data)
	--debug_print("clothing_store_badges_release")
	peg_unload("ui_multiplayer")
	menu_grid_release(menu_data[0])
end


--------------------[ MENU DATA ]----------------------

Clothing_store_top_btn_tips = {
		a_button = { label = "CONTROL_SELECT", 		enabled = btn_tips_default_a, }, --switch to wardrobe is dynamically added on init
		right_stick =  	{ label = "CONTROL_ZOOM_AND_ROTATE", 	enabled = true },
																			--exit/ resume also dynamically added

}

Clothing_store_untop_btn_tips = {
		a_button = { label = "CONTROL_SELECT", 		enabled = btn_tips_default_a, },
		right_stick =  	{ label = "CONTROL_ZOOM_AND_ROTATE", 	enabled = true },
}

Clothing_store_clothing_palette = {
	num_colors = 3,

	[0] = { label_str = "CUST_PRIMARY_COLOR",	red = 1, green = 0, blue = 0 },
	[1] = { label_str = "CUST_SECONDARY_COLOR",	red = 0, green = 0, blue = 0 },
	[2] = { label_str = "CUST_TERTIARY_COLOR",	red = 0, green = 0, blue = 1 },
}

Clothing_store_logo_palette = {
	num_colors = 1,
	[0] = { label_str = "CUST_LOGO_COLOR",	red = 1, green = 1, blue = 0 },
}

Clothing_store_wardrobe_delete_outfit_menu = {
	header_label_str = "DELETE_OUTFIT",
	on_alt_select = clothing_store_switch_mode,
	on_show = clothing_store_delete_outfit_show,
	on_nav = clothing_store_delete_outfits_nav,
	btn_tips = Clothing_store_untop_btn_tips,
	num_items = 1,

	[0] = { label = "NO_OUTFITS_DISPLAY_NAME", type = MENU_ITEM_TYPE_SELECTABLE },
}

Clothing_store_wardrobe_view_outfits_menu = {
	header_label_str = "CUST_ICON_OUTFITS",
	max_height = 471,	-- Default: 375 [nclok1405]
	on_alt_select = clothing_store_switch_mode,
	on_nav = clothing_store_view_outfits_nav,
	on_show = clothing_store_view_outfits_show,
	on_back = clothing_store_view_outfits_back,
	btn_tips = Clothing_store_untop_btn_tips,
	num_items = 1,

	[0] = { label = "NO_OUTFITS_DISPLAY_NAME", type = MENU_ITEM_TYPE_SELECTABLE },
}

Clothing_store_wardrobe_outfit_menu = {
	header_label_str = "CUST_ICON_OUTFITS",
	on_back = clothing_store_exit,
	on_alt_select = clothing_store_switch_mode,
	btn_tips = Clothing_store_top_btn_tips,
	on_show = clothing_store_outfit_menu_on_show,
	num_items = 4,

	[0] = { label = "CUST_ITEM_VIEW_OUTFITS", type = MENU_ITEM_TYPE_SUB_MENU, sub_menu = Clothing_store_wardrobe_view_outfits_menu },
	[1] = { label = "CUST_ITEM_CREATE_OUTFIT", type = MENU_ITEM_TYPE_SELECTABLE, on_select = clothing_store_wardrobe_create_outfit_verify },
	[2] = { label = "CUST_ITEM_DELETE_OUTFIT", type = MENU_ITEM_TYPE_SUB_MENU, sub_menu = Clothing_store_wardrobe_delete_outfit_menu },
	[3] = { label = "CUST_ITEM_REMOVE_CLOTHING", type = MENU_ITEM_TYPE_SELECTABLE, on_select = clothing_store_remove_clothing },
}

-- Crib Store Menu [nclok1405]
Clothing_store_wardrobe_online_store_menu = {
	header_label_str = "PAUSE_MAP_FILTER_STORES",
	on_back = clothing_store_exit,
	on_alt_select = clothing_store_switch_mode,
	btn_tips = Clothing_store_top_btn_tips,
	on_show = clothing_store_outfit_menu_on_show,
	num_items = 3,

	[0] = { label = "MENU_SWAP_CLOTHING_STORE", type = MENU_ITEM_TYPE_SELECTABLE, on_select = crib_store_clothing },
	[1] = { label = "MAP_ICON_JEWELRY", type = MENU_ITEM_TYPE_SELECTABLE, on_select = crib_store_jewelry },
	[2] = { label = "MAP_ICON_TATTOO_PARLOR", type = MENU_ITEM_TYPE_SELECTABLE, on_select = crib_store_tattoo },
}

Clothing_store_style_menu = {
	header_label_str = "MENU_STYLE",
	on_nav = clothing_store_style_nav,
	on_back = clothing_store_style_back,
	on_alt_select = clothing_store_switch_mode,
	btn_tips = Clothing_store_untop_btn_tips,
}

Clothing_store_wear_options_menu = {
	header_label_str = "CUST_MENU_WEAR_OPTION",
	on_nav = clothing_store_wear_option_nav,
	on_back = clothing_store_wear_option_back,
	on_alt_select = clothing_store_switch_mode,
	btn_tips = Clothing_store_untop_btn_tips,
}

Clothing_store_color_menu = {
	header_label_str = "CUST_MENU_COLOR",
	on_show = clothing_store_color_grid_show,
	on_release = clothing_store_color_grid_release,
	on_back = clothing_store_color_grid_back,
	on_alt_select = clothing_store_switch_mode,
	btn_tips = Clothing_store_untop_btn_tips,
	num_items = 1,
	footer_height = 30,
	[0] = { label = "", type = MENU_ITEM_TYPE_GRID, on_select = clothing_store_color_grid_select, on_nav = clothing_store_color_grid_nav,
		row_height = 41, num_cols = 6, col_width = 65, highlight_scale = 1, unhighlight_scale = 0.8,
		update_swatch = clothing_store_color_update_swatch
	}
}

Clothing_store_logo_list_menu = {
	header_label_str = "CUST_MENU_LOGO",
	on_show = clothing_store_logo_list_show,
	on_release = clothing_store_logo_list_release,
	on_back = clothing_store_logo_list_back,
	on_alt_select = clothing_store_switch_mode,
	btn_tips = Clothing_store_untop_btn_tips,
	num_items = 1,
	[0] = { label = "", type = MENU_ITEM_TYPE_GRID, on_select = clothing_store_logo_list_select, on_nav = clothing_store_logo_list_nav,
		row_height = MENU_SWATCH_DEFAULT_ROW_HEIGHT, num_cols = 4, col_width = MENU_SWATCH_DEFAULT_COL_WIDTH, highlight_scale = 1, unhighlight_scale = 0.8},
}

Clothing_store_item_details_menu = {
	header_label_str = "CUST_PURCHASE_ITEM",
	on_show = clothing_store_details_show,
	on_nav = clothing_store_details_nav,
	on_post_show = clothing_store_update_style_footer,
	on_alt_select = clothing_store_switch_mode,
	btn_tips = Clothing_store_untop_btn_tips,
}

Clothing_store_item_list_menu = {
	max_height = 471,	-- Default: 375 [nclok1405]
	on_show = clothing_store_build_item_list_menu,
	on_back = clothing_store_item_list_back,
	on_alt_select = clothing_store_switch_mode,
	on_nav = clothing_store_item_list_nav,
	on_post_show = clothing_store_update_style_footer,
	btn_tips = Clothing_store_untop_btn_tips,
}

Clothing_store_mp_badges_menu = {
	header_label_str = "CUST_ICON_BADGES",
	num_items = 1,
	on_back = clothing_store_exit,
	on_show = clothing_store_badges_show,
	on_alt_select = clothing_store_switch_mode,
	on_release = clothing_store_badges_release,
	btn_tips = Clothing_store_top_btn_tips,
	footer_height = 30,

	[0] = {
		label = "",
		type = MENU_ITEM_TYPE_GRID,
		on_select = clothing_store_badge_select,
		on_nav = clothing_store_badge_nav,
		row_height = 72,
		num_cols = 4,
		col_width = 83,
		highlight_scale = 1,
		unhighlight_scale = 0.8
	},
}

Clothing_store_category_menus = { }	-- dynamically built

Clothing_store_horz_menu = { }		-- built dynamically in clothing_store_init()
