-- hud_mayhem.lua: Mayhem/Septic Avenger/Taxi Driver Cash Effect

Hud_mayhem_elements = {
	in_game_grp_h = -1,
	bonus_grp_h = -1,
	bonus_item_grp_h = -1,
	bonus_grp_start_x = -1,
	bonus_grp_start_y = -1,
}

Hud_mayhem_anims = {
	rise_anim_h = -1,
	bonus_item_grp_anim_h = -1
}

Hud_mayhem_world_cash_status = {
	depth = 0,
	text_intensity = 0,
	color_r = .89,
	color_g = .749,
	color_b = .05,
}
Hud_mayhem_world_cash = {}

Hud_mayhem_bonus_mod_status = {
	current_index = 0,
	cleared_index = 0,
	line_height = 25,
}

Hud_mayhem_bonus_mods = {}


Hud_mayhem_world_cash_colors = {
	["WHITE"] 		= { ["r"] = .898, ["g"] = .894, ["b"] = .874}, 	--White
	["YELLOW"] 		= { ["r"] = .89, 	["g"] = .749, ["b"] = .05}, 	--Yellow
	["ORANGE"]		= { ["r"] = .984, ["g"] = .509, ["b"] = .054}, 	--Orange
	["RED"]			= { ["r"] = .780, ["g"] = 0, 	["b"] = .004}, 	--Red
	["BLUE"]			= { ["r"] = .26,	["g"] = .501, 	["b"] = .835},
	["MID_BLUE"]	= { ["r"] = .145,	["g"] = .419, 	["b"] = .811},
	["DARK_BLUE"]	= { ["r"] = .027,	["g"] = .341, 	["b"] = .788},
}

function hud_mayhem_init()

	--debug_print("vint", "hud_mayhem_init()\n")

	--Find and store elements
	local h = vint_object_find("mayhem_grp")

	--In world cash
	Hud_mayhem_elements.in_game_grp_h = vint_object_find("cash_grp")
	Hud_mayhem_anims.rise_anim_h = vint_object_find("mayhem_rise_anim")

	--Bonus Items
	Hud_mayhem_elements.bonus_grp_h = vint_object_find("bonus_grp", h)
	Hud_mayhem_elements.bonus_item_grp_h = vint_object_find("bonus_item_grp", h)
	Hud_mayhem_anims.bonus_item_grp_anim_h = vint_object_find("bonus_item_grp_anim")

	--Get initial y value for bonus group.
	local x, y = vint_get_property(Hud_mayhem_elements.bonus_grp_h, "anchor")
	Hud_mayhem_elements.bonus_grp_start_x = x
	Hud_mayhem_elements.bonus_grp_start_y = y

	--Pause Animations
	vint_set_property(Hud_mayhem_anims.rise_anim_h, "is_paused", true)
	vint_set_property(Hud_mayhem_anims.bonus_item_grp_anim_h, "is_paused", true)

	--Subscribe to data items
	vint_datagroup_add_subscription("mayhem_local_player_bonus_modifiers", "update", "hud_mayhem_bonus_mod_update")
	vint_datagroup_add_subscription("mayhem_local_player_world_cash", "insert", "hud_mayhem_world_cash_update")
	vint_datagroup_add_subscription("mayhem_local_player_world_cash", "update", "hud_mayhem_world_cash_update")
	vint_datagroup_add_subscription("mayhem_local_player_world_cash", "remove", "hud_mayhem_world_cash_remove")
end

--function hud_mayhem_bonus_mod_update(bonus_type, is_multiplier, bonus_text_crc, multiplier, di_h)

function hud_mayhem_bonus_mod_update(di_h)
	local bonus_type, is_multiplier, bonus_text_crc, multiplier = vint_dataitem_get(di_h)

	--[[
	VINT_PROP_TYPE_ENUM            - Bonus type (Vehicle == 0, Weapon == 1, Team == 2)
	VINT_PROP_TYPE_BOOL              - True means this is a multiplier, false means this is just a straight cash bonus
	VINT_PROP_TYPE_UINT               - The owned string hash for the localized name of what gave the bonus (car/weapon/team name)
	VINT_PROP_TYPE_INT                  - Bonus multiplier or cash value depending on the second element
	]]

	--Clone object
	local grp_h = vint_object_clone(Hud_mayhem_elements.bonus_item_grp_h)

	--Set Initial object properties
	vint_set_property(grp_h, "visible", true)

	--calculate its y value
	local grp_y = Hud_mayhem_bonus_mod_status.current_index * Hud_mayhem_bonus_mod_status.line_height
	vint_set_property(grp_h, "anchor", 0, grp_y)


	local x, y = vint_get_property(Hud_mayhem_elements.bonus_grp_h, "anchor")

	--Clone Animation
	local anim_h = vint_object_clone(Hud_mayhem_anims.bonus_item_grp_anim_h)

	--Retarget Animation
	vint_set_property(anim_h, "target_handle", grp_h)

	--Set Callback
	local callback_twn_h = vint_object_find("cash_txt_alpha_twn_2", anim_h)
	vint_set_property(callback_twn_h , "end_event", "hud_mayhem_bonus_mod_destroy")

	--Get text objects
	local bonus_cash_txt_h = vint_object_find("bonus_cash_txt", grp_h)
	local description_txt_h = vint_object_find("description_txt", grp_h)

	--Set Bonus Text
	vint_set_property(description_txt_h, "text_tag_crc", bonus_text_crc)

	if is_multiplier == false then
		--Use Cash
		local cash = format_cash(multiplier)
		vint_set_property(bonus_cash_txt_h, "text_tag", "$" .. cash)
	else
		--Multiplier
		vint_set_property(bonus_cash_txt_h, "text_tag", multiplier .. "x")
	end

	--Play Anim
	lua_play_anim(anim_h, 0)

	--Store Data
	Hud_mayhem_bonus_mods[di_h] = {
		idx = Hud_mayhem_bonus_mod_status.current_index,
		grp_h = grp_h,
		anim_h = anim_h,
		callback_twn_h = callback_twn_h,
		slide_twn_h = -1,
	}

	--Increment index
	Hud_mayhem_bonus_mod_status.current_index = Hud_mayhem_bonus_mod_status.current_index + 1
end

function hud_mayhem_bonus_mod_destroy(twn_h, event)
	for idx, val in Hud_mayhem_bonus_mods do
		if val.callback_twn_h == twn_h then
			--Destroy animation and text object
			vint_object_destroy(val.grp_h)
			vint_object_destroy(val.anim_h)

			--Increment Cleared Index
			Hud_mayhem_bonus_mod_status.cleared_index = Hud_mayhem_bonus_mod_status.cleared_index + 1

			--Destroy stored value
			Hud_mayhem_bonus_mods[idx] = nil
		end
	end

	--Slide the bonus mods up using a tween.
	hud_mayhem_bonus_mod_slide()
end

Hud_mayhem_bon_sl_twn_h = -1	--Reference to the bonus sliding twn

function hud_mayhem_bonus_mod_slide()

	--Need to verify if tween already exists. Destroy it if so.
	if Hud_mayhem_bon_sl_twn_h ~= -1 then
		vint_object_destroy(Hud_mayhem_bon_sl_twn_h)
		Hud_mayhem_bon_sl_twn_h = -1
	end

	local bonus_index = Hud_mayhem_bonus_mod_status.cleared_index

	local start_x, start_y = vint_get_property(Hud_mayhem_elements.bonus_grp_h, "anchor")
	local target_x = start_x
	local target_y = Hud_mayhem_elements.bonus_grp_start_y -(bonus_index * Hud_mayhem_bonus_mod_status.line_height)

	local twn_h = vint_object_create("tween" .. bonus_index, "tween", vint_object_find("root_animation"))
	vint_set_property(twn_h, "duration", .2)
	vint_set_property(twn_h, "target_handle", Hud_mayhem_elements.bonus_grp_h)
	vint_set_property(twn_h, "target_property", "anchor")
	vint_set_property(twn_h, "start_value", start_x, start_y)
	vint_set_property(twn_h, "end_value", target_x, target_y)
	vint_set_property(twn_h, "start_time",	vint_get_time_index())
	vint_set_property(twn_h, "is_paused", false)
	vint_set_property(twn_h, "end_event", "hud_mayhem_bonus_mod_slide_end")

	Hud_mayhem_bon_sl_twn_h = twn_h
end

function hud_mayhem_bonus_mod_slide_end(twn_h, event)

	--Destroy Tween and its reference
	vint_object_destroy(twn_h)
	Hud_mayhem_bon_sl_twn_h = -1

	--Check to see if we can reset the bonus mod positions
	local bonus_count = 0
	for idx, val in Hud_mayhem_bonus_mods do
		bonus_count = bonus_count + 1
		break
	end

	if bonus_count == 0 then
		--Reset Indexes
		Hud_mayhem_bonus_mod_status.current_index = 0
		Hud_mayhem_bonus_mod_status.cleared_index = 0

		local x, y = vint_get_property(Hud_mayhem_elements.bonus_grp_h, "anchor")

		--reset bonus group position
		vint_set_property(Hud_mayhem_elements.bonus_grp_h, "anchor", Hud_mayhem_elements.bonus_grp_start_x, Hud_mayhem_elements.bonus_grp_start_y)

		local x, y =  vint_get_property(Hud_mayhem_elements.bonus_grp_h, "anchor")
	end
end

function hud_mayhem_world_cash_update(di_h)
	--[[
		VINT_PROP_TYPE_FLOAT          - World position (x)
		VINT_PROP_TYPE_FLOAT          - World position (y)
		VINT_PROP_TYPE_FLOAT          - World position (z)
		VINT_PROP_TYPE_VECTOR2F    	- Screen position
		VINT_PROP_TYPE_INT            - Cash value
		VINT_PROP_TYPE_FLOAT          - Text intensity
		VINT_PROP_TYPE_INT        		- Multiplier value
		VINT_PROP_TYPE_INT            - Type 0 = $$, 1 = Points, 2 = Seconds

	]]
	local world_x, world_y, world_z, screen_pos_x, screen_pos_y, cash_value, text_intensity, multiplier, display_type = vint_dataitem_get(di_h)

	--debug_print("vint", "hud_mayhem_world_cash_update: di_h " .. di_h .. "\n")
	--debug_print("vint", "hud_mayhem_world_cash_update: cash_value $" .. cash_value .. "\n")

	if display_type == nil then
		display_type = 0
	end

	--Don't do anything else if this is a dummy object.
	if cash_value == 0 then
		--reset text color
		hud_mayhem_text_color_change(text_intensity)
		return
	end
	if Hud_mayhem_world_cash[di_h] ~= nil then
		--Element already exists... simply update its position and its all good in the hood baby.
		vint_set_property(Hud_mayhem_world_cash[di_h].grp_h, "anchor", screen_pos_x, screen_pos_y)
	else
		--Reset text color
		hud_mayhem_text_color_change(text_intensity)

		--Clone New item
		local grp_h = vint_object_clone(Hud_mayhem_elements.in_game_grp_h)
		local sub_grp_h = vint_object_find("cash_sub_grp", grp_h)
		local cash_txt_h = vint_object_find("cash_txt", grp_h)
		local multiplier_txt_h = vint_object_find("multiplier_txt", grp_h)
		local anim_h = vint_object_clone(Hud_mayhem_anims.rise_anim_h)

		--Reposition, rotate and set depth
		vint_set_property(grp_h, "anchor", screen_pos_x, screen_pos_y)
		vint_set_property(grp_h, "rotation", rand_float(0.249, -0.249))
		vint_set_property(grp_h, "depth", Hud_mayhem_world_cash_status.depth)

		--Hide the group for the first frame since it takes a frame for tweens to play.
		vint_set_property(sub_grp_h, "alpha", 0)

		--Retarget Tweens
		vint_set_property(anim_h, "target_handle", grp_h)

		--Randomize Tween Direction
		local twn_h = vint_object_find("txt_anchor_twn_1", anim_h)
		vint_set_property(twn_h, "end_value", rand_int(-20, 20), rand_int(-0,-30))

		--Callback tween to kill objects and stuff
		local callback_twn_h = vint_object_find("txt_anchor_twn_1", anim_h)
		vint_set_property(callback_twn_h, "end_event", "hud_mayhem_cash_destroy")

		--Tint Cash Text
		vint_set_property(cash_txt_h, "tint", Hud_mayhem_world_cash_status.color_r, Hud_mayhem_world_cash_status.color_g, Hud_mayhem_world_cash_status.color_b)

		-- +{0}sec   HUD_AMT_SECS
		-- +{0}points   HUD_AMT_POINTS

		--HUD_AMT_POINTS
		local insertion_text = { [0] = cash_value }
		local amt = ""

		if display_type == 0 then
			--Cash
			amt =  "$" .. cash_value
		elseif display_type == 1 then
			--Points
			amt = vint_insert_values_in_string("HUD_AMT_POINTS", insertion_text)
		elseif display_type == 2 then
			--Seconds
			amt = vint_insert_values_in_string("HUD_AMT_SECS", insertion_text)
		elseif display_type == 3 then
			--seconds + green
			amt = vint_insert_values_in_string("HUD_AMT_SECS", insertion_text)
			--Force green text
			vint_set_property(cash_txt_h, "tint", 0, 1, 0.25)
		end

		vint_set_property(cash_txt_h, "text_tag", amt)


		--Format Text with or without multiplier
		if multiplier ~= 0 then
			--Show Multiplier and Align text

			--Set MultiplierText Value
			vint_set_property(multiplier_txt_h, "text_tag", "X" .. multiplier)

			--Alignment
			local spacing = 5
			local c_w, c_h = vint_get_property(cash_txt_h, "screen_size")
			local c_x, c_y = vint_get_property(cash_txt_h, "anchor")
			local m_w, m_h = vint_get_property(multiplier_txt_h, "screen_size")
			local m_x, m_y = vint_get_property(multiplier_txt_h, "anchor")
			local half_w = (c_w + m_w + spacing) / 2
			local c_x = 0 - half_w
			local m_x = c_x + c_w + spacing

			--Set Properties
			vint_set_property(cash_txt_h, "anchor", c_x, c_y)
			vint_set_property(multiplier_txt_h, "anchor", m_x, m_y)
		else
			--Hide multiplier and center text

			vint_set_property(multiplier_txt_h, "visible", false)

			--Alignment
			local c_w, c_h = vint_get_property(cash_txt_h, "screen_size")
			local c_x, c_y = vint_get_property(cash_txt_h, "anchor")
			local c_x = 0 - (c_w / 2)

			--Set Properties
			vint_set_property(cash_txt_h, "anchor", c_x, c_y)
		end

		--play tween in animation
		lua_play_anim(anim_h, 0)

		--Decrement depth
		Hud_mayhem_world_cash_status.depth = Hud_mayhem_world_cash_status.depth - 1

		--Store values and handles to process later
		Hud_mayhem_world_cash[di_h] = {
			di_h = di_h,
			grp_h = grp_h,
			sub_grp_h = sub_grp_h,
			anim_h = anim_h,
			twn_h = callback_twn_h
		}

	end
end

function hud_mayhem_text_color_change(text_intensity)
	--Combo Color update
	--Prepare color morphing based on intensity
	local color1, color2, morph_value
	if text_intensity < 0.5 then
		if MP_enabled == true then
			color1 = Hud_mayhem_world_cash_colors["BLUE"]
			color2 = Hud_mayhem_world_cash_colors["MID_BLUE"]
		else
			color1 = Hud_mayhem_world_cash_colors["YELLOW"]
			color2 = Hud_mayhem_world_cash_colors["ORANGE"]
		end
		morph_value = text_intensity / 0.5
	else
		if text_intensity > 1 then
			text_intensity = 1
		end

		if MP_enabled == true then
			color1 = Hud_mayhem_world_cash_colors["MID_BLUE"]
			color2 = Hud_mayhem_world_cash_colors["DARK_BLUE"]
		else
			color1 = Hud_mayhem_world_cash_colors["ORANGE"]
			color2 = Hud_mayhem_world_cash_colors["RED"]
		end
		morph_value = (text_intensity - 0.5) / 0.5
	end

	Hud_mayhem_world_cash_status.color_r = color1.r - ((color1.r - color2.r) * morph_value)
	Hud_mayhem_world_cash_status.color_g = color1.g - ((color1.g - color2.g) * morph_value)
	Hud_mayhem_world_cash_status.color_b = color1.b - ((color1.b - color2.b) * morph_value)
	Hud_mayhem_world_cash_status.text_intensity = text_intensity
end

function hud_mayhem_world_cash_remove(di_h)
	--Destroy objects, animation and values
	if Hud_mayhem_world_cash[di_h] ~= nil then
		--Destroy animation
		vint_object_destroy(Hud_mayhem_world_cash[di_h].anim_h)
		--Destroy group object
		vint_object_destroy(Hud_mayhem_world_cash[di_h].grp_h)
		--Destroy stored values
		Hud_mayhem_world_cash[di_h] = nil
	end
end

--Destroys world cash text
function hud_mayhem_cash_destroy(twn_h, event)
	for idx, val in Hud_mayhem_world_cash do
		if val.twn_h == twn_h then

			--Destroy animation, text object and Data item
			vint_object_destroy(val.anim_h)
			vint_object_destroy(val.grp_h)
			if val.di_h ~= -1 then
				vint_datagroup_remove_item("mayhem_local_player_world_cash", val.di_h)
			end

			--Destroy stored values
			Hud_mayhem_world_cash[idx] = nil
		end
	end

	--reset values if this is the last cash item
	local cash_item_count = 0
	local is_last_item = true
	for idx, val in Hud_mayhem_world_cash do
		cash_item_count = cash_item_count + 1
		is_last_item = false
		break
	end
end


function hud_mayhem_bonus_test()
	local bonus_type = 0
	local is_multiplier = false
	local bonus_text_crc = "Vehicle Bonus"
	local multiplier = rand_int(2000, 3000)
	local di_h = rand_int(0, 10000)
	hud_mayhem_bonus_mod_update(bonus_type, is_multiplier, bonus_text_crc, multiplier, di_h)
end
