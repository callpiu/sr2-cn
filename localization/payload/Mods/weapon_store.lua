-- weapon_store.lua: Weapon Store and Weapons Cache

------------------
-- WEAPON STORE --
------------------
-- "global" variables
Weapon_menu_footer_ammo_meter_h 		= 0
Weapon_menu_footer_price_h 			= 0
Weapon_menu_footer_weapon_label_h 	= 0

Weapon_store_menu_add_index = 0
Weapon_menu_cache_only = false	-- true if we're in crib
Weapon_menu_is_cache_menu = false
Weapon_menu_active_horz_menu = { }
Active_menu 					 = { }
Weapon_category_to_purchase = { }
Weapon_index_of_purchase 	 = { }

Weapon_store_name = "MENU_SWAP_WEAPONS_STORE"
WEAPON_STORE_DOC_H = vint_document_find("weapon_store")

Equipped_thrown_weapon = {valid = false}	-- Currently equipped thrown weapon [nclok1405]

------------------
--- ANIMATIONS ---
------------------
--
Weapon_menu_anims = {
	icon_highlight_anim_h = -1,
	icon_dw_0_hl_anim_h = -1,
	icon_dw_1_hl_anim_h = -1,
}

----------------------
--	SYSTEM FUNCTIONS --
----------------------
--[ INITIALIZE AND SHUTDOWN ]--
-------------------------------
--	Initialize the menu
function weapon_store_init()
	Sui_weapon_store_active = true	-- Weapon Store is now active [nclok1405]

	--Find and store animations
	Weapon_menu_anims.icon_highlight_anim_h = vint_object_find("icon_highlight_anim")
	Weapon_menu_anims.icon_dw_0_hl_anim_h = vint_object_find("icon_dw_0_hl_anim")
	Weapon_menu_anims.icon_dw_1_hl_anim_h = vint_object_find("icon_dw_1_hl_anim")
	Weapon_menu_anims.icon_purchase_anim_h = vint_object_find("icon_purchase_anim")


	if Menu_swap_hud_hidden == true then
		if Sui_hud_enable == 0 then
			hud_hide(true)
		else
			hud_hide(false)
		end
		Menu_swap_hud_hidden = false
	end

	--Pause some of the anims
	vint_set_property(Weapon_menu_anims.icon_purchase_anim_h, "is_paused", true)

	--Check what kind of interface mode we are in? weapons only?
	Weapon_menu_cache_only = weapon_store_get_is_cache()
	if Weapon_menu_cache_only == true then
		Weapon_menu_is_cache_menu = true

		vint_dataresponder_request("weapon_store_populate_weapons", "equipped_thrown_weapon_check_callback", 0, "thrown")
	end

	-- Only have the melee weapons available in Brass Knuckles
	if weapon_store_is_melee_store() == true then
		Weapon_store_horz_menu.num_items = 1
		Weapon_store_horz_menu[0] = Weapon_store_horz_menu[1]	-- Swap melee with ammo
	elseif Weapon_menu_cache_only then
		-- Crib Store, only ammo is available [nclok1405]
		Weapon_store_horz_menu.num_items = 1
	else
		-- Friendly Fire
		for i = 1, Weapon_store_horz_menu.num_items - 1 do
			Weapon_store_horz_menu[i] = Weapon_store_horz_menu[i + 1]
		end
		Weapon_store_horz_menu.num_items = Weapon_store_horz_menu.num_items - 1
	end

	--Event Tracking
	if Weapon_menu_is_cache_menu == true then
		event_tracking_interface_enter("Weapons Cache")
	else
		event_tracking_interface_enter("Weapons Store")
	end

	weapons_store_show()
end


-- Shutdown and cleanup the menu
function weapon_store_cleanup()
	Sui_weapon_store_active = false	-- Weapon Store deactivated [nclok1405]
end

-- Callback for querying which thrown weapon is currently equipped [nclok1405]
function equipped_thrown_weapon_check_callback(name_str, icon_name, price, own, equipped, id, ammo_current, ammo_max, unlimited_ammo, dual_wield)
	if not equipped then
		return
	end

	Equipped_thrown_weapon = {
		valid = true,
		label_str = name_str, price = price, icon_name = icon_name, owned = own,
		equipped = equipped, id = id, ammo_current = ammo_current, ammo_max = ammo_max,
		clip_size = 1, unlimited_ammo = unlimited_ammo, dual_wield = false,
	}
end

--[ EXIT ]--
------------
function weapon_store_exit(menu_data)
	local body
	if Weapon_menu_cache_only == true then
		body = "WPN_CACHE_EXIT_PROMPT"
	else
		-- Still might be a cache
		if Weapon_menu_is_cache_menu then
			body = "WPN_CACHE_EXIT_PROMPT"
		else
			-- We're not in cache
			body = "WPN_STORE_EXIT_PROMPT"
		end
	end

	--dialog_box_confirmation("MENU_TITLE_WARNING", body, "weapon_store_exit_confirm")
	menu_close(weapon_store_exit_final) -- Exit without dialog [nclok1405]
end

function weapon_store_exit_confirm(result, action)
	if action ~= DIALOG_ACTION_CLOSE then
		return
	end

	if result == 0 then
		menu_close(weapon_store_exit_final)
	end
end

function weapon_store_exit_final()
	vint_document_unload(WEAPON_STORE_DOC_H)
end

-----------------------
-- MENU SWAPING 	  	--
-----------------------
function weapons_store_show()
	local use_style = false

	if Weapon_menu_is_cache_menu == true then
		Weapon_menu_active_horz_menu = Weapon_cache_horz_menu
		Weapon_store_name = "MENU_SWAP_WEAPONS_CACHE"

		--Set Button tip Labels
		Weapon_store_btn_tips.x_button.label = "MENU_SWAP_WEAPONS_STORE"
	else
		--Its a weapon store
		if Weapon_menu_cache_only then
			Weapon_store_name = "AMMUNATION.NET"
		elseif weapon_store_is_melee_store() then
			Weapon_store_name = "MELEE_WPN_STORE_NAME"
		else
			Weapon_store_name = "WPNSTOR_TITLE_FRIENDLY_FIRE"
		end

		Weapon_menu_active_horz_menu = Weapon_store_horz_menu
		-- RCS: 7/11/08, TDL 246474, weapon store no longer awards style points
--		use_style = true

		--Set Button tip Labels
		Weapon_store_btn_tips.x_button.label = "MENU_SWAP_WEAPONS_CACHE"
	end

	menu_store_init(use_style)
	menu_init()

	weapon_store_set_cache(Weapon_menu_is_cache_menu)

	menu_horz_init(Weapon_menu_active_horz_menu)

--[[
	if Weapon_menu_cache_only and (not Weapon_menu_is_cache_menu) then
		if Equipped_thrown_weapon.valid then
			dialog_box_message("Thrown Weapon", "ID:"..Equipped_thrown_weapon.id.."\nAmmo:"..Equipped_thrown_weapon.ammo_current.."/"..Equipped_thrown_weapon.ammo_max)
		else
			dialog_box_message("No Thrown Weapon", "No thrown weapon seems equipped.")
		end
	end
--]]
end

function weapons_store_switch_mode()
	if Weapon_menu_cache_only == true then
		--Only can switch modes if we aren't weapons cache only
		-- Always allow switch [nclok1405]
		--return
	end

	if Weapon_store_name == "MENU_SWAP_WEAPONS_CACHE" then
		if Weapon_menu_cache_only then
			Weapon_store_name = "AMMUNATION.NET"
		elseif weapon_store_is_melee_store() then
			Weapon_store_name = "MELEE_WPN_STORE_NAME"
		else
			Weapon_store_name = "WPNSTOR_TITLE_FRIENDLY_FIRE"
		end

		Weapon_menu_is_cache_menu = false

		if Weapon_menu_cache_only == true then
			-- When going to Crib Store, query which thrown weapon is currently equipped [nclok1405]
			vint_dataresponder_request("weapon_store_populate_weapons", "equipped_thrown_weapon_check_callback", 0, "thrown")
		end
	else
		Weapon_store_name = "MENU_SWAP_WEAPONS_CACHE"
		Weapon_menu_is_cache_menu = true
	end

	menu_swap_interface(Weapon_store_name, weapons_store_show)
end

------------------------
--	MENU FUNCTIONALITY --
------------------------
function weapon_store_select_new_item(menu_label, menu_data)
	local swatches = menu_data.swatches
	local idx = menu_data.cur_row * menu_data.num_cols + menu_data.cur_col
	local category = Weapon_menu_active_horz_menu[Weapon_menu_active_horz_menu.current_selection].category
	if idx < swatches.num_swatches then
		if Active_menu.footer_type ~= "ammo" then
			weapon_store_footer_update(swatches[idx], swatches[idx].owned, Active_menu.footer_type)
			weapon_store_change_weapon(category, swatches[idx].id, swatches[idx].dual_wield)
		elseif Active_menu.footer_type == "ammo" then
			local owned = false
			if swatches[idx].ammo_current >= swatches[idx].ammo_max then
				owned = true
			end

			--Retrigger highlight animation
			vint_set_property(Weapon_menu_anims.icon_highlight_anim_h, "target_handle", swatches[idx].swatch_h)
			lua_play_anim(Weapon_menu_anims.icon_highlight_anim_h, 0)
			vint_set_property(Weapon_menu_anims.icon_dw_0_hl_anim_h, "target_handle", swatches[idx].swatch_h)
			lua_play_anim(Weapon_menu_anims.icon_dw_0_hl_anim_h, 0)
			vint_set_property(Weapon_menu_anims.icon_dw_1_hl_anim_h, "target_handle", swatches[idx].swatch_h)
			lua_play_anim(Weapon_menu_anims.icon_dw_1_hl_anim_h, 0)

			weapon_store_change_weapon(category, swatches[idx].id, false)
			weapon_store_footer_update(swatches[idx], owned, "ammo")
		end
	end
end

function weapon_store_swatch_on_enter(new_swatch)
	--Retrigger highlight animation
	vint_set_property(Weapon_menu_anims.icon_highlight_anim_h, "target_handle", new_swatch.swatch_h)
	lua_play_anim(Weapon_menu_anims.icon_highlight_anim_h, 0)
	vint_set_property(Weapon_menu_anims.icon_dw_0_hl_anim_h , "target_handle", new_swatch.swatch_h)
	lua_play_anim(Weapon_menu_anims.icon_dw_0_hl_anim_h , 0)
	vint_set_property(Weapon_menu_anims.icon_dw_1_hl_anim_h, "target_handle", new_swatch.swatch_h)
	lua_play_anim(Weapon_menu_anims.icon_dw_1_hl_anim_h, 0)
end

function weapon_store_swatch_on_leave(old_swatch)
	--Remove highlight from old swatch
	local icon_highlight = vint_object_find("icon_highlight", old_swatch.swatch_h )
	vint_set_property(icon_highlight, "alpha", 0)
	local icon_dw_0_hl = vint_object_find("icon_dw_0_hl", old_swatch.swatch_h )
	local icon_dw_1_hl = vint_object_find("icon_dw_1_hl", old_swatch.swatch_h )
	vint_set_property(icon_dw_0_hl, "alpha", 0)
	vint_set_property(icon_dw_1_hl, "alpha", 0)

end

function weapon_store_footer_build(menu_data)
	local footer_master = vint_object_find("weapon_menu_footer", nil, WEAPON_STORE_DOC_H)
	local grp = vint_object_clone(footer_master, Menu_option_labels.control_parent)
	vint_set_property(grp, "visible", true)

	if menu_data.footer ~= nil and menu_data.footer.footer_grp ~= nil and menu_data.footer.footer_grp ~= 0 then
		vint_object_destroy(menu_data.footer.footer_grp)
	end

	menu_data.footer = { }
	menu_data.footer.footer_grp = grp

	Weapon_menu_footer_ammo_meter_h = vint_object_find("ammo_amount", grp)
	Weapon_menu_footer_price_h = vint_object_find("price_amount", grp)
	Weapon_menu_footer_weapon_label_h = vint_object_find("weapon_label", grp)

	if menu_data.footer_type == "ammo" then
		vint_set_property(Weapon_menu_footer_ammo_meter_h, "visible", true)
		vint_set_property(Weapon_menu_footer_price_h, "visible", true)
		vint_set_property(Weapon_menu_footer_weapon_label_h, "visible", true)
	elseif menu_data.footer_type == "weapon" then
		vint_set_property(Weapon_menu_footer_ammo_meter_h, "visible", false)
		vint_set_property(Weapon_menu_footer_price_h, "visible", true)
		vint_set_property(Weapon_menu_footer_weapon_label_h, "visible", true)
	elseif menu_data.footer_type == "cache" then
		vint_set_property(Weapon_menu_footer_ammo_meter_h, "visible", false)
		vint_set_property(Weapon_menu_footer_price_h, "visible", true)	-- false
		vint_set_property(Weapon_menu_footer_weapon_label_h, "visible", true)
	end
end

-- Update footer
function weapon_store_footer_update(swatch, owned, category)
	vint_set_property(Weapon_menu_footer_weapon_label_h, "visible", true)
	vint_set_property(Weapon_menu_footer_weapon_label_h, "text_tag", swatch.label_str)

	if (swatch.ammo_max > 0) and (not swatch.unlimited_ammo) then
		vint_set_property(Weapon_menu_footer_ammo_meter_h, "text_tag", swatch.ammo_current .. "/" .. swatch.ammo_max)
		vint_set_property(Weapon_menu_footer_ammo_meter_h, "visible", true)

		if (swatch.ammo_current < swatch.ammo_max) and (category == "ammo") then
			owned = false
		end
	else
		vint_set_property(Weapon_menu_footer_ammo_meter_h, "visible", false)
	end

	if swatch.price ~= nil and swatch.price > 0 then
		if owned then
			vint_set_property(Weapon_menu_footer_price_h, "tint", 0.3, 0.3, 0.3)	-- Owned weapon's price color [nclok1405]
		elseif Style_cluster_player_cash < swatch.price then
			vint_set_property(Weapon_menu_footer_price_h, "tint", MENU_FOOTER_CASH_BROKE_COLOR.R, MENU_FOOTER_CASH_BROKE_COLOR.G, MENU_FOOTER_CASH_BROKE_COLOR.B)
		else
			vint_set_property(Weapon_menu_footer_price_h, "tint", MENU_FOOTER_CASH_NORMAL_COLOR.R, MENU_FOOTER_CASH_NORMAL_COLOR.G, MENU_FOOTER_CASH_NORMAL_COLOR.B)
		end
		vint_set_property(Weapon_menu_footer_price_h, "text_tag", "$" .. format_cash(swatch.price))
		vint_set_property(Weapon_menu_footer_price_h, "visible", true)
	else
		vint_set_property(Weapon_menu_footer_price_h, "tint", 1.0, 1.0, 1.0)
		vint_set_property(Weapon_menu_footer_price_h, "visible", false)
	end

	-- Display free thrown ammo [nclok1405]
	local weapon_category = Weapon_menu_active_horz_menu[Weapon_menu_active_horz_menu.current_selection].category
	if (category == "cache") and (weapon_category == "thrown") then
		local num_free_ammo = weapon_store_get_free_thrown_ammo_amount()
		if (swatch.icon_name == "ui_hud_inv_w_satchelcharge") then
			num_free_ammo = 5
		end

		if (swatch.ammo_current < num_free_ammo) then
			local diff_free_ammo = num_free_ammo - swatch.ammo_current
			vint_set_property(Weapon_menu_footer_ammo_meter_h, "visible", true)

			local insert_values = {
				[0] = swatch.ammo_current,
				[1] = swatch.ammo_max,
				[2] = diff_free_ammo,
				[3] = "STORE_FREE",
			}
			local s = vint_insert_values_in_string("{0}/{1} [format][color:green](+{2} {3})[/format]", insert_values)
			vint_set_property(Weapon_menu_footer_ammo_meter_h, "text_tag", s)
		end
	end

	weapon_store_footer_resize_text()
end

function	weapon_store_footer_remove(menu_data)
	if menu_data.footer ~= nil then
		vint_set_property(menu_data.footer.footer_grp, "visible", false)
		vint_object_destroy(menu_data.footer.footer_grp)
	end
end

function weapon_store_footer_finalize(menu_data)
	vint_set_property(Weapon_menu_footer_price_h, "anchor", menu_data.menu_width - 20, 0)
	weapon_store_footer_resize_text()
end

function weapon_store_footer_resize_text()
	if Menu_active == 0 then
		return
	end

	if Menu_active.footer_height ~= 0 then
		vint_set_property(Weapon_menu_footer_weapon_label_h, "scale", 1.0, 1.0)
		local text_x, text_y = vint_get_property(Weapon_menu_footer_weapon_label_h, "anchor")
		local text_width, text_height = element_get_actual_size(Weapon_menu_footer_weapon_label_h)
		local price_anchor_x = vint_get_property(Weapon_menu_footer_price_h, "anchor")
		local price_width, price_height = element_get_actual_size(Weapon_menu_footer_price_h)
		local size_of_text = Menu_active.menu_width - price_width - 30
		local text_scale  = (size_of_text / (text_x + text_width))
		if text_x + text_width >= size_of_text then
			vint_set_property(Weapon_menu_footer_weapon_label_h, "scale", text_scale, text_scale)
		end
	end
end

---[ CACHE MENU ]---
--------------------
function weapon_store_confirm_cache_selection(menu_label, menu_data)
	local swatches = menu_data.swatches
	local idx = menu_data.cur_row * menu_data.num_cols + menu_data.cur_col
	local category = Weapon_menu_active_horz_menu[Weapon_menu_active_horz_menu.current_selection].category

	if idx < swatches.num_swatches then
		if category == "thrown" then
			-- For thrown weapons [nclok1405]

			if swatches[idx].equipped == false then
				-- Switch weapon
				weapon_store_purchase_weapon(category, swatches[idx].id)
				-- Update the swatched to show it is equipped
				weapon_store_set_equipped(swatches, idx)
			end

			-- Give some free ammo for thrown weapons because non-equipped thrown ammos are not saved. [nclok1405]

			-- Set the number of ammo given for free based on the game progress
			local num_free_ammo = weapon_store_get_free_thrown_ammo_amount()
			if (swatches[idx].icon_name == "ui_hud_inv_w_satchelcharge") then
				-- Only 5 can be given for Satchel Charge because its ammo count will immediately drop back to 5 if it has 6 or more
				num_free_ammo = 5
			end

			-- Give ammo
			if (swatches[idx].ammo_current < num_free_ammo) and (not swatches[idx].unlimited_ammo) then
				while (swatches[idx].ammo_current < num_free_ammo) do
					-- The game adds 1 thrown ammo for each call of weapon_store_purchase_weapon, even in weapons cache.
					weapon_store_purchase_weapon(category, swatches[idx].id)
					swatches[idx].ammo_current = swatches[idx].ammo_current + 1
				end
				weapon_store_weapon_update_swatch(swatches[idx])
				weapon_store_footer_update(swatches[idx], true, Active_menu.footer_type)
				audio_play("SYS_PICKUP_WEP")	-- Play weapon pickup sound to inform the player that they received something
			end
		elseif swatches[idx].equipped == false then
			weapon_store_purchase_weapon(category, swatches[idx].id)
			--	Update the swatched to show it is equipped
			weapon_store_set_equipped(swatches, idx)

			-- Update what's equipped now [nclok1405]
			local category_num = Weapon_menu_active_horz_menu.current_selection + 1
			Sui_weapon_bmp[category_num] = swatches[idx].icon_name
			Sui_weapon_dual[category_num] = swatches[idx].dual_wield
			Sui_weapon_infinite[category_num] = swatches[idx].unlimited_ammo

			--debug_print("cache category_num:"..tostring(category_num)..", icon_name:"..tostring(swatches[idx].icon_name)..", dual_wield:"..tostring(swatches[idx].dual_wield).."\n")
		end
	end
end

-- Get the number of free thrown ammo [nclok1405]
function weapon_store_get_free_thrown_ammo_amount()
	local num_free_ammo = 5
	if (Sui_missions_completed >= 56) then
		num_free_ammo = 50
	elseif (Sui_missions_completed >= 49) then
		num_free_ammo = 40
	elseif (Sui_missions_completed >= 34) then
		num_free_ammo = 30
	elseif (Sui_missions_completed >= 19) then
		num_free_ammo = 20
	elseif (Sui_missions_completed >= 4) then
		num_free_ammo = 10
	end
	return num_free_ammo
end

---[ WEAPON MENU ]---
---------------------
function weapon_store_update_weapon_menu(menu_item)
	Weapon_store_menu_add_index = 0
	menu_item.swatches = { num_swatches = 0 }
	menu_item.cur_idx = 0

	local category = Weapon_menu_active_horz_menu[Weapon_menu_active_horz_menu.current_selection].category

	if category == "thrown" then
		vint_dataresponder_request("weapon_store_populate_weapons", "weapon_store_weapon_menu_add_thrown_items", 0, category)
	else
		vint_dataresponder_request("weapon_store_populate_weapons", "weapon_store_weapon_menu_add_items", 0, category)
	end

	menu_item.swatches.num_swatches = Weapon_store_menu_add_index
end

function weapon_store_build_weapon_menu(menu_data)
	Active_menu = menu_data
	local menu_item = menu_data[0]

	menu_item.type=MENU_ITEM_TYPE_GRID
	menu_item.label = ""
	if Weapon_menu_is_cache_menu == true then
		menu_item.on_select = weapon_store_confirm_cache_selection
	else
		if Weapon_menu_active_horz_menu[Weapon_menu_active_horz_menu.current_selection].category ~= "thrown" then
			menu_item.on_select = weapon_store_confirm_weapon_selection
		else
			menu_item.on_select = weapon_store_confirm_throwing_weapon_selection
		end
	end
	menu_item.on_nav = weapon_store_select_new_item
	menu_data.footer_height = 40

	weapon_store_update_weapon_menu(menu_item)

	menu_data.header_label_str = Weapon_menu_active_horz_menu[Weapon_menu_active_horz_menu.current_selection].label

	if menu_item.swatches.num_swatches > 0 then
		local master_swatch = vint_object_find("swatch_weapon", nil, WEAPON_STORE_DOC_H)
		local category = Weapon_menu_active_horz_menu[Weapon_menu_active_horz_menu.current_selection].category
		--debug_print("category:"..tostring(category).."\n")

		if menu_item.swatches.num_swatches < 11 and menu_item.swatches.num_swatches > 8 then
			menu_item.num_cols = 5
		else
			menu_item.num_cols = 4
		end

		-- Hide arrows on Melee and Pistol cache. [nclok1405]
		-- This is a workaround/sacrifice to prevent various graphical glitches found on these two tabs.
		-- Glitches include some or all arrows not displaying, button background not showing up, weapon icon missing, etc...
		-- This is most likely caused by game's hard-limit of UI objects.
		-- In vanilla SR2 there were not many weapons in these categories so devs did not allocate many slots for additional UI objects.
		-- However in GotR there are many weapons here, so the game sometimes fail to allocate new UI objects for them.
		local hide_arrows = false
		if Weapon_menu_is_cache_menu and ((category == "melee") or (category == "pistol")) then
			hide_arrows = true
		end

		menu_grid_show(menu_data, menu_item, master_swatch, false, hide_arrows)

		weapon_store_footer_build(menu_data)

		--Play flashing animation on selected item
		local cur_idx = menu_item.cur_idx	-- Current weapon ID [nclok1405]
		vint_set_property(Weapon_menu_anims.icon_highlight_anim_h, "target_handle", menu_item.swatches[cur_idx].swatch_h)
		lua_play_anim(Weapon_menu_anims.icon_highlight_anim_h, 0)
		vint_set_property(Weapon_menu_anims.icon_dw_0_hl_anim_h, "target_handle", menu_item.swatches[cur_idx].swatch_h)
		lua_play_anim(Weapon_menu_anims.icon_dw_0_hl_anim_h, 0)
		vint_set_property(Weapon_menu_anims.icon_dw_1_hl_anim_h, "target_handle", menu_item.swatches[cur_idx].swatch_h)
		lua_play_anim(Weapon_menu_anims.icon_dw_1_hl_anim_h, 0)

		weapon_store_footer_update(menu_item.swatches[cur_idx], menu_item.swatches[cur_idx].owned, menu_data.footer_type)

		vint_set_property(Menu_footer_style_h, "visible", false)

		weapon_store_change_weapon(category, menu_item.swatches[cur_idx].id, menu_item.swatches[cur_idx].dual_wield)
	else
		menu_data[0].type=MENU_ITEM_TYPE_SELECTABLE
		menu_data[0].label="WPN_STORE_NO_WEAPONS_AVAILABLE"
		menu_data[0].on_select = nil
		menu_data[0].on_nav = nil
		menu_data.footer_height = 0
	end
end

function weapon_store_weapon_update_swatch(swatch)
	local ammo_icon = vint_object_find("ammo_icon", swatch.swatch_h)
	local ammo_count = vint_object_find("ammo_count", swatch.swatch_h)
	local icon = vint_object_find("icon", swatch.swatch_h)
	local icon_dw_0 = vint_object_find("icon_dw_0", swatch.swatch_h)
	local icon_dw_1 = vint_object_find("icon_dw_1", swatch.swatch_h)
	local icon_dw_0_hl = vint_object_find("icon_dw_0_hl", swatch.swatch_h)
	local icon_dw_1_hl = vint_object_find("icon_dw_1_hl", swatch.swatch_h)
	local icon_highlight = vint_object_find("icon_highlight", swatch.swatch_h)
	local icon_purchase = vint_object_find("icon_purchase", swatch.swatch_h)

	local ammo_current = swatch.ammo_current
	local ammo_max = swatch.ammo_max
	local ammo_percent, ammo_angle
	local equipped_ammo_fill = vint_object_find("equipped_ammo_fill", swatch.swatch_h)
	local equipped_ammo_bg = vint_object_find("equipped_ammo_bg", swatch.swatch_h)
	local equipped_ammo_base = vint_object_find("equipped_ammo_base", swatch.swatch_h)
	local equipped_ammo_inf  = vint_object_find("equipped_ammo_inf", swatch.swatch_h)

	local owned = vint_object_find("check_owned", swatch.swatch_h)

	--Stop Highlight animation
	vint_set_property(Weapon_menu_anims.icon_highlight_anim_h, "is_paused", true)
	vint_set_property(Weapon_menu_anims.icon_highlight_anim_h, "target_handle", nil)

	--Stop DW Highlight animation
--	vint_set_property(Weapon_menu_anims.icon_dw_0_hl_anim_h, "is_paused", true)
--	vint_set_property(Weapon_menu_anims.icon_dw_0_hl_anim_h, "target_handle", nil)
--	vint_set_property(Weapon_menu_anims.icon_dw_1_hl_anim_h, "is_paused", true)
--	vint_set_property(Weapon_menu_anims.icon_dw_1_hl_anim_h, "target_handle", nil)

	vint_set_property(ammo_icon, "visible", false)
	vint_set_property(ammo_count, "visible", false)
	vint_set_property(equipped_ammo_inf, "visible", false)
	vint_set_property(icon, "image", swatch.icon_name)
	vint_set_property(icon_highlight, "image", swatch.icon_name)
	vint_set_property(icon_highlight, "alpha", 0)
	vint_set_property(icon_dw_0, "image", swatch.icon_name)
	vint_set_property(icon_dw_0_hl, "image", swatch.icon_name)
	vint_set_property(icon_dw_0_hl, "alpha", 0)
	vint_set_property(icon_dw_1, "image", swatch.icon_name)
	vint_set_property(icon_dw_1_hl, "image", swatch.icon_name)
	vint_set_property(icon_dw_1_hl, "alpha", 0)
	vint_set_property(icon_purchase, "image", swatch.icon_name)

	if swatch.dual_wield == true then
		vint_set_property(icon_dw_0, "visible", true)
		vint_set_property(icon_dw_1, "visible", true)
		vint_set_property(icon_dw_0_hl, "visible", true)
		vint_set_property(icon_dw_1_hl, "visible", true)
		vint_set_property(icon, "visible", false)
		vint_set_property(icon_highlight, "visible", false)
	else
		vint_set_property(icon_dw_0, "visible", false)
		vint_set_property(icon_dw_1, "visible", false)
		vint_set_property(icon_dw_0_hl, "visible", false)
		vint_set_property(icon_dw_1_hl, "visible", false)
		vint_set_property(icon, "visible", true)
		vint_set_property(icon_highlight, "visible", true)
	end

	if swatch.equipped == true then
		vint_set_property(equipped_ammo_base, "visible", true)
		if ammo_max ~= 0 then
			if swatch.unlimited_ammo == true then
				vint_set_property(equipped_ammo_inf, "visible", true)
				vint_set_property(equipped_ammo_bg, "visible", false)
				vint_set_property(equipped_ammo_fill, "visible", false)
			else
				vint_set_property(equipped_ammo_inf, "visible", false)
				vint_set_property(equipped_ammo_fill, "visible", true)
				vint_set_property(equipped_ammo_bg, "visible", true)
			end
		else
			vint_set_property(equipped_ammo_inf, "visible", false)
			vint_set_property(equipped_ammo_fill, "visible", false)
			vint_set_property(equipped_ammo_bg, "visible", false)
		end
	else
		vint_set_property(equipped_ammo_inf, "visible", false)
		vint_set_property(equipped_ammo_fill, "visible", false)
		vint_set_property(equipped_ammo_bg, "visible", false)
		vint_set_property(equipped_ammo_base, "visible", false)
	end

	if swatch.owned == true and Weapon_menu_is_cache_menu == false and swatch.equipped == false then
		vint_set_property(owned, "visible", true)
	else
		vint_set_property(owned, "visible", false)
	end


	--Set the fill of ammo bar
	ammo_percent = ammo_current/ammo_max
	ammo_angle = -4.7 + (-3.14 + 4.7) * ammo_percent
	vint_set_property(equipped_ammo_fill, "start_angle", ammo_angle)
end

function weapon_store_set_equipped(swatches, idx)
	--Set Equipped indicator on the swatch

	--Find and show indicator elements
	local	equipped_ammo_fill = vint_object_find("equipped_ammo_fill", swatches[idx].swatch_h)
	local	equipped_ammo_bg = vint_object_find("equipped_ammo_bg", swatches[idx].swatch_h)
	local	equipped_ammo_base = vint_object_find("equipped_ammo_base", swatches[idx].swatch_h)
	local 	equipped_ammo_inf  = vint_object_find("equipped_ammo_inf", swatches[idx].swatch_h)

	vint_set_property(equipped_ammo_base, "visible", true)
	if swatches[idx].ammo_max ~= 0 then
		if swatches[idx].unlimited_ammo == true then
			vint_set_property(equipped_ammo_inf, "visible", true)
			vint_set_property(equipped_ammo_bg, "visible", false)
			vint_set_property(equipped_ammo_fill, "visible", false)
		else
			vint_set_property(equipped_ammo_inf, "visible", false)
			vint_set_property(equipped_ammo_fill, "visible", true)
			vint_set_property(equipped_ammo_bg, "visible", true)
		end
	else
		vint_set_property(equipped_ammo_inf, "visible", false)
		vint_set_property(equipped_ammo_fill, "visible", false)
		vint_set_property(equipped_ammo_bg, "visible", false)
	end

	--Hide old equipped Indicator
	for i = 0, swatches.num_swatches - 1 do
		if swatches[i].equipped == true and i ~= idx then
			equipped_ammo_inf = vint_object_find("equipped_ammo_inf", swatches[i].swatch_h)
			equipped_ammo_fill = vint_object_find("equipped_ammo_fill", swatches[i].swatch_h)
			equipped_ammo_bg = vint_object_find("equipped_ammo_bg", swatches[i].swatch_h)
			equipped_ammo_base = vint_object_find("equipped_ammo_base", swatches[i].swatch_h)
			vint_set_property(equipped_ammo_inf, "visible", false)
			vint_set_property(equipped_ammo_fill, "visible", false)
			vint_set_property(equipped_ammo_bg, "visible", false)
			vint_set_property(equipped_ammo_base, "visible", false)
			swatches[i].equipped = false
		end
	end

	swatches[idx].equipped = true
end

--Resets all the owned swatches
function weapon_store_reset_owned(swatches)

	--Show old owned Indicator
	for i = 0, swatches.num_swatches - 1 do
		local owned_h = vint_object_find("check_owned", swatches[i].swatch_h)
		if swatches[i].owned == true and swatches[i].equipped == false then
			vint_set_property(owned_h, "visible", true)
		else
			vint_set_property(owned_h, "visible", false)
		end
	end

end

-- Make the purchase
function weapon_purchase_confirm(result, action)
	if action ~= DIALOG_ACTION_CLOSE then
		return
	end



	if result == 0 then
		local category = Weapon_menu_active_horz_menu[Weapon_menu_active_horz_menu.current_selection].category

		--	Purchase the weapon
		weapon_store_purchase_weapon(category, Weapon_category_to_purchase[Weapon_index_of_purchase].id)

		--	Update the swatched to show it is equipped and owned
		-- RCS: 7/11/08, TDL 246474, weapon store no longer awards style points
--		award_style("weapon", Weapon_category_to_purchase[Weapon_index_of_purchase].price)
		weapon_store_set_equipped(Weapon_category_to_purchase, Weapon_index_of_purchase)
		weapon_store_reset_owned(Weapon_category_to_purchase)
		Weapon_category_to_purchase[Weapon_index_of_purchase].owned = true

		--Play purchase animation (Find swatch, retarget & play)
		local swatch_current_h = Weapon_category_to_purchase[Weapon_index_of_purchase].swatch_h
		vint_set_property(Weapon_menu_anims.icon_purchase_anim_h, "is_paused", true)
		vint_set_property(Weapon_menu_anims.icon_purchase_anim_h, "target_handle", swatch_current_h)
		lua_play_anim(Weapon_menu_anims.icon_purchase_anim_h, 0)

		--play the purchase sound
		audio_play(Menu_sound_purchase)

		--	Update the footer to reflect that it is owned
		if Active_menu.footer_type == "ammo" then
			local owned = false
			Weapon_category_to_purchase[Weapon_index_of_purchase].ammo_current = Weapon_category_to_purchase[Weapon_index_of_purchase].ammo_current + Weapon_category_to_purchase[Weapon_index_of_purchase].clip_size
			if Weapon_category_to_purchase[Weapon_index_of_purchase].ammo_current >= Weapon_category_to_purchase[Weapon_index_of_purchase].ammo_max then
				owned = true
			end
			weapon_store_footer_update(Weapon_category_to_purchase[Weapon_index_of_purchase], owned, "ammo")
		else
			weapon_store_footer_update(Weapon_category_to_purchase[Weapon_index_of_purchase], true, Active_menu.footer_type)
		end
	end
end

--	The purchase was decided
function weapon_store_confirm_weapon_selection(menu_label, menu_data)
	local swatches = menu_data.swatches
	local idx = menu_data.cur_row * menu_data.num_cols + menu_data.cur_col

	if idx < swatches.num_swatches then
		if swatches[idx].owned == false then
			if Style_cluster_player_cash >= swatches[idx].price then
				local insert = { [0] = swatches[idx].label_str, [1] = format_cash(swatches[idx].price) }
				local body = vint_insert_values_in_string("WPN_STORE_PURCHASE_PROMPT", insert)
				local heading = "MENU_TITLE_CONFIRM"
				Weapon_category_to_purchase = swatches
				Weapon_index_of_purchase = idx
				dialog_box_confirmation(heading, body, "weapon_purchase_confirm")
			else
				dialog_box_message("MENU_TITLE_NOTICE", "HUD_SHOP_INSUFFICIENT_FUNDS")
			end
		else
			-- Owned
			--dialog_box_message("MENU_TITLE_NOTICE", "WPNSTOR_TEXT_MAX_WEAPONS_STORE")
		end
	end
end

function weapon_store_confirm_throwing_weapon_selection(menu_label, menu_data)
	local swatches = menu_data.swatches
	local idx = menu_data.cur_row * menu_data.num_cols + menu_data.cur_col
	if idx < swatches.num_swatches then
		if (swatches[idx].owned == true) and (swatches[idx].icon_name == "ui_hud_inv_w_satchelcharge") then
			-- NOPE! Do not buy Satchel here! [nclok1405]
			if swatches[idx].equipped then
				dialog_box_message("MENU_TITLE_NOTICE", "SUI_SATCHEL_CANNOT_BUY_AMMO_HERE")
			else
				dialog_box_message("MENU_TITLE_NOTICE", "SUI_SATCHEL_MUST_EQUIP_FOR_AMMO")
			end
		elseif (swatches[idx].owned == false or swatches[idx].equipped == false) and Style_cluster_player_cash >= swatches[idx].price
			and swatches[idx].ammo_current < swatches[idx].ammo_max then
			-- Buying a new thrown weapon
			local insert = { [0] = swatches[idx].label_str, [1] = format_cash(swatches[idx].price) }
			local body = vint_insert_values_in_string("WPN_STORE_PURCHASE_PROMPT", insert)
			local heading = "MENU_TITLE_CONFIRM"
			Weapon_category_to_purchase = swatches
			Weapon_index_of_purchase = idx
			dialog_box_confirmation(heading, body, "weapon_purchase_confirm")
		elseif swatches[idx].owned == true and swatches[idx].ammo_current < swatches[idx].ammo_max then
			-- Buying an already equipped thrown weapon
			if Style_cluster_player_cash >= swatches[idx].price then
				local saved_cash = Style_cluster_player_cash
				local category = Weapon_menu_active_horz_menu[Weapon_menu_active_horz_menu.current_selection].category
				weapon_store_purchase_weapon(category, swatches[idx].id)
				swatches[idx].ammo_current = swatches[idx].ammo_current + swatches[idx].clip_size

				local owned = false
				if swatches[idx].ammo_current >= swatches[idx].ammo_max then
					swatches[idx].ammo_current = swatches[idx].ammo_max
					owned = true
				end

				weapon_store_weapon_update_swatch(swatches[idx])
				weapon_store_footer_update(swatches[idx], owned, Active_menu.footer_type)
				if Style_cluster_player_cash - swatches[idx].price < swatches[idx].price and saved_cash == Style_cluster_player_cash then
					vint_set_property(Weapon_menu_footer_price_h, "tint", 1, 0, 0)
				end

				--dialog_box_message("Throwing Weapon Purchased", "Category:"..category.."\nID:"..swatches[idx].id.."\nAmmo:"..swatches[idx].ammo_current.."/"..swatches[idx].ammo_max.."\nPrice:"..swatches[idx].price)
			else
				dialog_box_message("MENU_TITLE_NOTICE", "HUD_SHOP_INSUFFICIENT_FUNDS")
			end
		elseif swatches[idx].owned == true and swatches[idx].ammo_current >= swatches[idx].ammo_max then
			-- Max Ammo
			--dialog_box_message("MENU_TITLE_NOTICE", "WPNSTOR_TEXT_MAX_AMMO_STORE")
		else
			dialog_box_message("MENU_TITLE_NOTICE", "HUD_SHOP_INSUFFICIENT_FUNDS")
		end
	end
end

function weapon_store_weapon_menu_add_items(name_str, icon_name, price, own, equipped, id, ammo_current, ammo_max, unlimited_ammo, dual_wield)
	local eq = equipped

	-- Can't trust the equipped status in Weapons Cache [nclok1405]
	if Weapon_menu_is_cache_menu then
		eq = false

		local category_num = Weapon_menu_active_horz_menu.current_selection + 1

		if (icon_name == Sui_weapon_bmp[category_num]) and (dual_wield == Sui_weapon_dual[category_num]) and (unlimited_ammo == Sui_weapon_infinite[category_num]) then
			eq = true
			--debug_print("category_num:"..tostring(category_num)..", icon_name:"..tostring(icon_name)..", dual_wield:"..tostring(dual_wield)..", equip:"..tostring(Sui_weapon_bmp[category_num]).."\n")
		end
	end

	local swatches = Active_menu[0].swatches
	swatches[Weapon_store_menu_add_index] = {
		label_str = name_str, price = price, icon_name = icon_name, owned = own,
		equipped = eq, id = id, ammo_current = ammo_current, ammo_max = ammo_max,
		unlimited_ammo = unlimited_ammo, dual_wield = dual_wield,
	}

	if Weapon_menu_is_cache_menu and eq then
		Active_menu[0].cur_idx = Weapon_store_menu_add_index	-- Set cursor to equipped weapon [nclok1405]
	end

	Weapon_store_menu_add_index = Weapon_store_menu_add_index + 1
end

function weapon_store_weapon_menu_add_thrown_items(name_str, icon_name, price, own, equipped, id, ammo_current, ammo_max, unlimited_ammo, dual_wield)
	local swatches = Active_menu[0].swatches

	swatches[Weapon_store_menu_add_index] = {
		label_str = name_str, price = price, icon_name = icon_name, owned = own,
		equipped = equipped, id = id, ammo_current = ammo_current, ammo_max = ammo_max,
		clip_size = 1, unlimited_ammo = unlimited_ammo, dual_wield = dual_wield,
	}

	if Weapon_menu_is_cache_menu and equipped then
		Active_menu[0].cur_idx = Weapon_store_menu_add_index	-- Set cursor to equipped weapon [nclok1405]
	end

	Weapon_store_menu_add_index = Weapon_store_menu_add_index + 1
end

function weapon_store_release_menu(menu_data)
	weapon_store_footer_remove(menu_data)
	if menu_data[0].type == MENU_ITEM_TYPE_GRID then
		menu_grid_release(menu_data[0])
	end
end

---[ AMMO MENU ]---
-------------------
function weapon_store_update_ammo_menu(menu_data)
	local menu_item = menu_data[0]
	Weapon_store_menu_add_index = 0
	menu_item.swatches = { num_swatches = 0 }
	menu_item.cur_idx = 0

	vint_dataresponder_request("weapon_store_populate_ammo", "weapon_store_ammo_menu_add_items", 0)

	-- Add thrown weapon ammo to the Crib Store [nclok1405]
	if Weapon_menu_cache_only and (not Weapon_menu_is_cache_menu) and Equipped_thrown_weapon.valid then
		local e = Equipped_thrown_weapon
		weapon_store_ammo_menu_add_items(e.label_str, e.icon_name, "ui_menu_ammo_grenade", e.price, e.clip_size, e.ammo_current, e.ammo_max, 1000)
	end

	menu_item.swatches.num_swatches = Weapon_store_menu_add_index
end

function weapon_store_build_ammo_menu(menu_data)
	Active_menu = menu_data
	local menu_item = menu_data[0]
	menu_item.type = MENU_ITEM_TYPE_GRID
	menu_item.label = ""
	menu_item.on_select = weapon_store_confirm_ammo_selection
	menu_item.on_nav = weapon_store_select_new_item
	menu_data.footer_height = 40

	weapon_store_update_ammo_menu(menu_data)

	if menu_data[0].swatches.num_swatches == 0 then
		menu_data[0].type=MENU_ITEM_TYPE_SELECTABLE
		menu_data[0].label="WPN_STORE_NO_WEAPONS_AVAILABLE"
		menu_data[0].on_select = nil
		menu_data[0].on_nav = nil
		menu_data.footer_height = 0
		return
	end

	local master_swatch = vint_object_find("swatch_weapon", nil, WEAPON_STORE_DOC_H)
	menu_grid_show(menu_data, menu_item, master_swatch)

	weapon_store_footer_build(menu_data)

	local owned = false

	if menu_item.swatches[0].ammo_current >= menu_item.swatches[0].ammo_max then
		owned = true
	end

	--Play flashing animation on selected item
	vint_set_property(Weapon_menu_anims.icon_highlight_anim_h, "target_handle", menu_item.swatches[0].swatch_h)
	lua_play_anim(Weapon_menu_anims.icon_highlight_anim_h, 0)


	weapon_store_footer_update(menu_item.swatches[0], owned, "ammo")
	weapon_store_change_weapon("ammo", menu_item.swatches[0].id, false)
	vint_set_property(Menu_footer_style_h, "visible", false)
end

function weapon_store_ammo_update_swatch(swatch)
	local ammo_icon = vint_object_find("ammo_icon", swatch.swatch_h)
	local ammo_count = vint_object_find("ammo_count", swatch.swatch_h)
	local icon = vint_object_find("icon", swatch.swatch_h)
	local icon_highlight = vint_object_find("icon_highlight", swatch.swatch_h)
	local icon_purchase = vint_object_find("icon_purchase", swatch.swatch_h)

	local equipped_ammo_fill = vint_object_find("equipped_ammo_fill", swatch.swatch_h)
	local equipped_ammo_bg = vint_object_find("equipped_ammo_bg", swatch.swatch_h)
	local equipped_ammo_base = vint_object_find("equipped_ammo_base", swatch.swatch_h)

	local owned = vint_object_find("check_owned", swatch.swatch_h)

	vint_set_property(ammo_icon, "visible", true)
	vint_set_property(ammo_icon, "image", swatch.ammo_icon)

	vint_set_property(ammo_count, "visible", true)
	vint_set_property(ammo_count, "text_tag", swatch.clip_size)

	local swatch_scale = vint_get_property(swatch.swatch_h, "scale")
	local scaler = Menu_scaler / swatch_scale

	local ammo_icon_x, ammo_icon_y  = vint_get_property(ammo_icon, "anchor")
	local ammo_count_x, ammo_count_y  = vint_get_property(ammo_count, "anchor")
	local ammo_count_width, ammo_count_height  = vint_get_property(ammo_count, "screen_size")
	local ammo_icon_x = ammo_count_x + ((ammo_count_width + 3)* scaler)
	vint_set_property(ammo_icon, "anchor", ammo_icon_x, ammo_icon_y)

	--Hide equipped Icons
	vint_set_property(equipped_ammo_fill, "visible", false)
	vint_set_property(equipped_ammo_bg, "visible", false)
	vint_set_property(equipped_ammo_base, "visible", false)

	vint_set_property(owned, "visible", false)

	--Stop highlight animation
	vint_set_property(Weapon_menu_anims.icon_highlight_anim_h, "is_paused", true)
	vint_set_property(Weapon_menu_anims.icon_highlight_anim_h, "target_handle", nil)

	vint_set_property(icon, "image", swatch.icon_name)
	vint_set_property(icon_highlight, "image", swatch.icon_name)
	vint_set_property(icon_highlight, "alpha", 0)
	vint_set_property(icon_purchase, "image", swatch.icon_name)

end

function weapon_store_confirm_ammo_selection(menu_label, menu_data)
	local swatches = menu_data.swatches
	local idx = menu_data.cur_row * menu_data.num_cols + menu_data.cur_col

	if idx < swatches.num_swatches then
		if swatches[idx].ammo_current < swatches[idx].ammo_max then
			if Style_cluster_player_cash >= swatches[idx].price then
				local saved_cash = Style_cluster_player_cash
				weapon_store_purchase_ammo(swatches[idx].id)
				swatches[idx].ammo_current = swatches[idx].ammo_current + swatches[idx].clip_size
				local owned = false
				if swatches[idx].ammo_current >= swatches[idx].ammo_max then
					swatches[idx].ammo_current = swatches[idx].ammo_max
					owned = true
				end

				--Play purchase animation (Find swatch, retarget & play)
				local swatch_current_h = swatches[idx].swatch_h
				vint_set_property(Weapon_menu_anims.icon_purchase_anim_h, "target_handle", swatch_current_h)
				lua_play_anim(Weapon_menu_anims.icon_purchase_anim_h, 0)

				--play the purchase sound
				audio_play(Menu_sound_purchase)

				weapon_store_footer_update(swatches[idx], owned, "ammo")
				if Style_cluster_player_cash - swatches[idx].price < swatches[idx].price and saved_cash == Style_cluster_player_cash then
					vint_set_property(Weapon_menu_footer_price_h, "tint", 1, 0, 0)
				end

				--dialog_box_message("Ammo Purchased", "ID:"..swatches[idx].id.."\nAmmo:"..swatches[idx].ammo_current.."/"..swatches[idx].ammo_max.."\nPrice:"..swatches[idx].price)
			else
				dialog_box_message("MENU_TITLE_NOTICE", "HUD_SHOP_INSUFFICIENT_FUNDS")
			end
		else
			-- Max Ammo
			--dialog_box_message("MENU_TITLE_NOTICE", "WPNSTOR_TEXT_MAX_AMMO_STORE")
		end
	end
end

function weapon_store_ammo_menu_add_items(name, icon_name, ammo_icon, price, clip_size, current_amount, max_amount, id)
	local swatches = Weapon_store_ammo_menu[0].swatches
	swatches[Weapon_store_menu_add_index] = {
		label_str = name, price = price, icon_name = icon_name, ammo_icon = ammo_icon, clip_size = clip_size, ammo_current = current_amount, ammo_max = max_amount, id = id, unlimited_ammo = false
	}

	Weapon_store_menu_add_index = Weapon_store_menu_add_index + 1
end

function weapon_store_ammo_menu_release(menu_data)
	weapon_store_footer_remove(menu_data)
	menu_grid_release(menu_data[0])
end


function weapon_store_is_not_cache_only()
	--Awesome logic, to determine to display button tips
--[[
	if Weapon_menu_cache_only == true then
		return false
	else
		return true
	end
--]]
	-- Always allow switch [nclok1405]
	return true
end

---------------
-- MENU DATA --
---------------
-- Button Tips
------------------
Weapon_store_btn_tips = {
	a_button 	= 	{ label = "CONTROL_SELECT", 				enabled = btn_tips_default_a, },
	x_button 	= 	{ label = "MENU_SWAP_WEAPONS_CACHE", 	enabled = weapon_store_is_not_cache_only, },
	b_button 	= 	{ label = "MENU_RESUME", 						enabled = btn_tips_default_a, },
}

--	Ammo Menu
-------------------
Weapon_store_ammo_menu = {
	header_label_str 	 = "WPN_STORE_AMMO_TITLE",
	num_items 	 	= 1,
	on_show		 	= weapon_store_build_ammo_menu,
	on_post_show 	= weapon_store_footer_finalize,
	on_release	 	= weapon_store_release_menu,
	on_back		 	= weapon_store_exit,
	on_alt_select	= weapons_store_switch_mode,

	[0] = { label = "", type = MENU_ITEM_TYPE_GRID, on_select = weapon_store_confirm_ammo_selection, on_nav = weapon_store_select_new_item,
		row_height = MENU_SWATCH_DEFAULT_ROW_HEIGHT, num_cols = 4, col_width = MENU_SWATCH_DEFAULT_COL_WIDTH, highlight_scale = 1,
		unhighlight_scale = 0.8, update_swatch = weapon_store_ammo_update_swatch, on_enter = weapon_store_swatch_on_enter,
		on_leave = weapon_store_swatch_on_leave },

	btn_tips = Weapon_store_btn_tips,
	footer_type	  = "ammo",
	footer_height = 40,
}


--	Weapon Menu
--------------
Weapon_store_weapon_menu_a = {
	header_label_str 	 = "NOT SET",
	num_items 	 = 1,
	on_show		 = weapon_store_build_weapon_menu,
	on_release	 = weapon_store_release_menu,
	on_back		 = weapon_store_exit,
	on_post_show = weapon_store_footer_finalize,
	on_alt_select	= weapons_store_switch_mode,

	[0] = { label = "", type = MENU_ITEM_TYPE_GRID, on_select = weapon_store_confirm_weapon_selection, on_nav = weapon_store_select_new_item,
		row_height = MENU_SWATCH_DEFAULT_ROW_HEIGHT, num_cols = 4, col_width = MENU_SWATCH_DEFAULT_COL_WIDTH, highlight_scale = 1, unhighlight_scale = 0.8,
		update_swatch = weapon_store_weapon_update_swatch,	on_enter = weapon_store_swatch_on_enter, on_leave = weapon_store_swatch_on_leave },

	btn_tips = Weapon_store_btn_tips,
	footer_type	  = "weapon",
	footer_height = 40,
}

Weapon_store_weapon_menu_b = {
	header_label_str 	 = "NOT SET",
	num_items 	 = 1,
	on_show		 = weapon_store_build_weapon_menu,
	on_post_show = weapon_store_footer_finalize,
	on_release	 = weapon_store_release_menu,
	on_back		 = weapon_store_exit,
	on_alt_select	= weapons_store_switch_mode,

	[0] = { label = "", type = MENU_ITEM_TYPE_GRID, on_select = weapon_store_confirm_weapon_selection, on_nav = weapon_store_select_new_item,
		row_height = MENU_SWATCH_DEFAULT_ROW_HEIGHT, num_cols = 4, col_width = MENU_SWATCH_DEFAULT_COL_WIDTH, highlight_scale = 1, unhighlight_scale = 0.8, update_swatch = weapon_store_weapon_update_swatch,
		on_enter = weapon_store_swatch_on_enter, on_leave = weapon_store_swatch_on_leave },

	btn_tips = Weapon_store_btn_tips,
	footer_type	  = "weapon",
	footer_height = 40,
}

Weapon_store_weapon_menu_throwing = {
	header_label_str 	 = "NOT SET",
	num_items 	 = 1,
	on_show		 = weapon_store_build_weapon_menu,
	on_release	 = weapon_store_release_menu,
	on_back		 = weapon_store_exit,
	on_post_show = weapon_store_footer_finalize,
	on_alt_select	= weapons_store_switch_mode,

	[0] = { label = "", type = MENU_ITEM_TYPE_GRID, on_select = weapon_store_confirm_throwing_weapon_selection, on_nav = weapon_store_select_new_item,
		row_height = MENU_SWATCH_DEFAULT_ROW_HEIGHT, num_cols = 4, col_width = MENU_SWATCH_DEFAULT_COL_WIDTH, highlight_scale = 1,
		unhighlight_scale = 0.8, update_swatch = weapon_store_weapon_update_swatch, on_enter = weapon_store_swatch_on_enter, on_leave = weapon_store_swatch_on_leave },

	btn_tips = Weapon_store_btn_tips,
	footer_type	  = "ammo",
	footer_height = 40,
}

Weapon_store_cache_menu_a = {
	header_label_str 	 = "NOT SET",
	num_items 	 	= 1,
	on_show		 	= weapon_store_build_weapon_menu,
	on_post_show 	= weapon_store_footer_finalize,
	on_release	 	= weapon_store_release_menu,
	on_back		 	= weapon_store_exit,
	on_alt_select	= weapons_store_switch_mode,

	btn_tips = Weapon_store_btn_tips,
	[0] = { label = "", type = MENU_ITEM_TYPE_GRID, on_select = weapon_store_confirm_cache_selection, on_nav = weapon_store_select_new_item,
		row_height = MENU_SWATCH_DEFAULT_ROW_HEIGHT, num_cols = 4, col_width = MENU_SWATCH_DEFAULT_COL_WIDTH, highlight_scale = 1, unhighlight_scale = 0.8, update_swatch = weapon_store_weapon_update_swatch,
		on_enter = weapon_store_swatch_on_enter, on_leave = weapon_store_swatch_on_leave },

	footer_type	  = "cache",
	footer_height = 40,
}

Weapon_store_cache_menu_b = {
	header_label_str 	 = "NOT SET",
	num_items 	 	= 1,
	on_show		 	= weapon_store_build_weapon_menu,
	on_post_show 	= weapon_store_footer_finalize,
	on_release	 	= weapon_store_release_menu,
	on_back		 	= weapon_store_exit,
	on_alt_select	= weapons_store_switch_mode,

	btn_tips = Weapon_store_btn_tips,
	[0] = { label = "", type = MENU_ITEM_TYPE_GRID, on_select = weapon_store_confirm_cache_selection, on_nav = weapon_store_select_new_item,
		row_height = MENU_SWATCH_DEFAULT_ROW_HEIGHT, num_cols = 4, col_width = MENU_SWATCH_DEFAULT_COL_WIDTH, highlight_scale = 1, unhighlight_scale = 0.8, update_swatch = weapon_store_weapon_update_swatch,
		on_enter = weapon_store_swatch_on_enter, on_leave = weapon_store_swatch_on_leave },

	footer_type	  = "cache",
	footer_height = 40,
}

Weapon_store_cache_menu_c = {
	header_label_str 	 = "NOT SET",
	num_items 	 	= 1,
	on_show		 	= weapon_store_build_weapon_menu,
	on_post_show 	= weapon_store_footer_finalize,
	on_release	 	= weapon_store_release_menu,
	on_back		 	= weapon_store_exit,
	on_alt_select	= weapons_store_switch_mode,

	btn_tips = Weapon_store_btn_tips,
	[0] = { label = "", type = MENU_ITEM_TYPE_GRID, on_select = weapon_store_confirm_cache_selection, on_nav = weapon_store_select_new_item,
		row_height = MENU_SWATCH_DEFAULT_ROW_HEIGHT, num_cols = 4, col_width = 83, highlight_scale = 1, unhighlight_scale = 0.8, update_swatch = weapon_store_weapon_update_swatch,
		on_enter = weapon_store_swatch_on_enter, on_leave = weapon_store_swatch_on_leave },

	footer_type	  = "cache",
	footer_height = 40,
}


--	Horizontal Menu
------------------
Weapon_store_horz_menu = {
	num_items = 8,
	current_selection = 0,

	[0] = { label = "WPN_STORE_AMMO_TITLE", 		sub_menu = Weapon_store_ammo_menu, 		category = "ammo"  		},
	[1] = { label = "WPN_STORE_MELEE_TITLE",		sub_menu = Weapon_store_weapon_menu_a, 	category = "melee" 		},
	[2] = { label = "WPN_STORE_PISTOL_TITLE",	 	sub_menu = Weapon_store_weapon_menu_b, 	category = "pistol"		},
	[3] = { label = "WPN_STORE_SMG_TITLE", 			sub_menu = Weapon_store_weapon_menu_a, 	category = "smg" 		},
	[4] = { label = "WPN_STORE_SHOTGUN_TITLE",		sub_menu = Weapon_store_weapon_menu_b, 	category = "shotgun" 	},
	[5] = { label = "WPN_STORE_RIFLE_TITLE", 		sub_menu = Weapon_store_weapon_menu_a, 	category = "rifle" 		},
	[6] = { label = "WPN_STORE_SPECIAL_TITLE",	 	sub_menu = Weapon_store_weapon_menu_b, 	category = "special" 	},
	[7] = { label = "WPN_STORE_THROWN_TITLE", 		sub_menu = Weapon_store_weapon_menu_throwing, category = "thrown" },
}

Weapon_cache_horz_menu = {
	num_items = 7,
	current_selection = 0,

	[0] = { label = "WPN_STORE_MELEE_TITLE", 	sub_menu = Weapon_store_cache_menu_a, category = "melee"	},
	[1] = { label = "WPN_STORE_PISTOL_TITLE", 	sub_menu = Weapon_store_cache_menu_b, category = "pistol" 	},
	[2] = { label = "WPN_STORE_SMG_TITLE", 		sub_menu = Weapon_store_cache_menu_a, category = "smg"		},
	[3] = { label = "WPN_STORE_SHOTGUN_TITLE",	sub_menu = Weapon_store_cache_menu_b, category = "shotgun"	},
	[4] = { label = "WPN_STORE_RIFLE_TITLE", 	sub_menu = Weapon_store_cache_menu_a, category = "rifle" 	},
	[5] = { label = "WPN_STORE_SPECIAL_TITLE", 	sub_menu = Weapon_store_cache_menu_c, category = "special" 	},
	[6] = { label = "WPN_STORE_THROWN_TITLE", 	sub_menu = Weapon_store_cache_menu_b, category = "thrown" 	},

}
