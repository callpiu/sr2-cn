-- hud_msg.lua: Messages in HUD

-- Has to match the enum in hud_message.h
HUD_REGION_DEBUG		= 0
HUD_REGION_HELP			= 1
HUD_REGION_DIVERSION	= 2
HUD_REGION_SUBTITLES	= 3
HUD_REGION_CUTSCENE_HELP	= 4
HUD_NUM_REGIONS			= 5

HUD_MSG_DIR_UP			= 0
HUD_MSG_DIR_DOWN		= 1
HUD_MSG_DIR_CENTER		= 2

Hud_msg_std_text 		= { scale = 0.6, wrap_width = 0 }
Hud_msg_help_text		= { scale = 0.7, wrap_width = 390 }
Hud_msg_subtitle_text	= { scale = 0.7, wrap_width = 0 }	-- Needs to match subtitles.cpp

Hud_msg_regions = {
	[HUD_REGION_DEBUG]		= {
		text_fmt = Hud_msg_std_text,
		direction = HUD_MSG_DIR_CENTER,	max_msgs = 10,
		anchor = "msg_debug_anchor",
		msgs = { num_msgs = 0 }
	},

	[HUD_REGION_HELP]		= {
		text_fmt = Hud_msg_help_text,
		direction = HUD_MSG_DIR_CENTER,
		max_msgs = 3,
		anchor = "msg_help_anchor",
		msgs = { num_msgs = 0 }
	},

	[HUD_REGION_DIVERSION]	= {
		text_fmt = Hud_msg_std_text,
		direction = HUD_MSG_DIR_UP,
		max_msgs = 7,
		anchor = "msg_diversion_anchor",
		msgs = { num_msgs = 0 }
	},

	[HUD_REGION_SUBTITLES]	= {
		text_fmt = Hud_msg_subtitle_text,
		direction = HUD_MSG_DIR_CENTER,
		max_msgs = 3,
		anchor = "msg_subtitle_anchor",
		msgs = { num_msgs = 0 }
	},

	[HUD_REGION_CUTSCENE_HELP]	= {
		text_fmt = Hud_msg_help_text,
		direction = HUD_MSG_DIR_CENTER,
		max_msgs = 2,
		anchor = "cs_help_anchor",
		msgs = { num_msgs = 0 }
	},
}

-- all messages are stored here with the data item handle as index
Hud_msgs = { }

-- Change Clothes Nag Message [nclok1405]
String_nag_clothes = vint_insert_values_in_string("{0}", {[0] = "TUT_NAG_CHANGE_CLOTHES"})

-- Stash Nag Message [nclok1405]
String_nag_stash = vint_insert_values_in_string("{0}", {[0] = "TUT_NAG_CRIB_STASH"})
-- Replacement Message "Stash Transfer complete" [nclok1405]
String_custom_stash = vint_insert_values_in_string("{0} {1}", {[0] = "HELP_TEXT_STASH_TITLE", [1] = "MSN_SH_BH_AIRPORT_TRANSFERCOMPLETE"})
-- Replacement Message "StashTransfer complete" for asian languages (No Spaces) [nclok1405]
String_custom_stash_asian = vint_insert_values_in_string("{0}{1}", {[0] = "HELP_TEXT_STASH_TITLE", [1] = "MSN_SH_BH_AIRPORT_TRANSFERCOMPLETE"})
-- Replacement Message "Stash Available" (English Only) [nclok1405]
String_custom_stash_en = "Stash Available"

-- Other Nag Messages [nclok1405]
String_nag_cruise_control = vint_insert_values_in_string("{0}", {[0] = "TUT_NAG_CRUISE_CONTROL"})
String_nag_fine_aim = vint_insert_values_in_string("{0}", {[0] = "TUT_NAG_FINE_AIM"})
String_nag_human_shield = vint_insert_values_in_string("{0}", {[0] = "TUT_NAG_HUMAN_SHIELD"})
String_nag_improvised_weapons = vint_insert_values_in_string("{0}", {[0] = "TUT_NAG_IMPROV_WEAPONS"})
String_nag_power_attacks = vint_insert_values_in_string("{0}", {[0] = "TUT_NAG_POWER_ATTACKS"})
String_nag_sprinting = vint_insert_values_in_string("{0}", {[0] = "TUT_NAG_SPRINTING"})
String_nag_taunting = vint_insert_values_in_string("{0}", {[0] = "TUT_NAG_TAUNTING"})

function hud_msg_init()
	-- resolve the anchors out to handles
	for i, v in Hud_msg_regions do
		v.anchor = vint_object_find(v.anchor)
	end

	--Resize help region if we are in hd
	if vint_hack_is_std_res() == false then
		--HD mode
		Hud_msg_help_text.wrap_width = 635
	end

	Hud_msg_subtitle_text.scale = SUI_SUBTITLE_SIZE	-- Subtitle Size Override [nclok1405]

	vint_datagroup_add_subscription("hud_messages", "insert", "hud_msg_new_message")
	vint_datagroup_add_subscription("hud_messages", "update", "hud_msg_update_message")
	vint_datagroup_add_subscription("hud_messages", "remove", "hud_msg_remove_message")
end

function hud_msg_process()
	for i, region in Hud_msg_regions do
		if region.is_dirty == true then
			hud_msg_update_region(region)
			region.is_dirty = false
		end
	end
end

function hud_msg_update_region(region)
	local pos_x, pos_y = 0, 0
	local msgs_displayed = 0

	for msg_i = 0, region.msgs.num_msgs - 1 do
		local msg = region.msgs[msg_i]
		local o = msg.text_obj_h

		if msgs_displayed >= region.max_msgs then
			if o ~= 0 then
				vint_object_destroy(o)
			end
			msg.text_obj_h = 0
		else

			-- create a text item if needed
			if o == 0 then
				o = vint_object_create("hud_msg", "text", region.anchor)
				vint_set_property(o, "text_tag", msg.text)
				vint_set_property(o, "font", "thin_overlay")
				vint_set_property(o, "text_scale", region.text_fmt.scale, region.text_fmt.scale)

				local auto_offset, halign
				if region.direction == HUD_MSG_DIR_CENTER then
					auto_offset = "nw"
					halign = "center"
				elseif region.direction == HUD_MSG_DIR_UP then
					auto_offset = "sw"
					halign = "left"
				else	-- HUD_MSG_DIR_DOWN
					auto_offset = "nw"
					halign = "left"
				end

				if region.text_fmt.wrap_width > 0 then
					vint_set_property(o, "word_wrap", true)
					vint_set_property(o, "wrap_width", region.text_fmt.wrap_width)
				end

				vint_set_property(o, "auto_offset", auto_offset)
				vint_set_property(o, "horz_align", halign)
				vint_set_property(o, "line_frame_enable", true)
				vint_set_property(o, "line_frame_w", "ui_hud_hlp_bg_w")
				vint_set_property(o, "line_frame_m", "ui_hud_hlp_bg_m")
				vint_set_property(o, "line_frame_e", "ui_hud_hlp_bg_e")

				if msg.audio_id ~= -1 then
					audio_play(msg.audio_id, msg.audio_type)
				end

				msg.text_obj_h = o
			end

			-- place the text
			vint_set_property(o, "anchor", pos_x, pos_y)

			local w, h = vint_get_property(o, "unscaled_size")

			-- figure position of next element
			if region.direction == HUD_MSG_DIR_UP then
				pos_y = pos_y - h
			else	-- HUD_MSG_DIR_DOWN or HUD_MSG_DIR_CENTER
				pos_y = pos_y + h
			end

		end

		msgs_displayed = msgs_displayed + 1
	end
end

-- Returns true if the text should be rejected [nclok1405]
function hud_msg_should_be_rejected(text)
	-- Reject everything when HUD is disabled [nclok1405]
	if (not Sui_hud_messages_enable) then
		return true
	end

	-- Reject "Change Clothes" Nag [nclok1405]
	if (text == String_nag_clothes) then
		return true
	end

	-- If tutorials are disabled [nclok1405]
	if (Sui_tutorial ~= 2) then
		-- Reject other nag messages
		if (text == String_nag_cruise_control) or (text == String_nag_fine_aim) or (text == String_nag_human_shield) or (text == String_nag_improvised_weapons) or (text == String_nag_power_attacks) or (text == String_nag_sprinting) or (text == String_nag_taunting) then
			return true
		end
	end

	return false
end

-- Handle special SuperUI Custom HUD commands [nclok1405]
function hud_msg_handle_sui_commands(text)
	if sui_compare_string(text, "SUI_CMD_ENABLE_CUSTOM_HUD") then
		-- SUI_CMD_ENABLE_CUSTOM_HUD
		-- Enable/Reset Custom HUD
		Sui_custom_hud_active = true
		Sui_custom_hud_timer_active = false
		Sui_custom_hud_timer_value = 0
		Sui_custom_hud_number_active = false
		Sui_custom_hud_number_value = 0
		return true
	elseif sui_compare_string(text, "SUI_CMD_DISABLE_CUSTOM_HUD") then
		-- SUI_CMD_DISABLE_CUSTOM_HUD
		-- Disable Custom HUD
		Sui_custom_hud_active = false
		Sui_custom_hud_timer_active = false
		Sui_custom_hud_timer_value = 0
		Sui_custom_hud_number_active = false
		Sui_custom_hud_number_value = 0
		return true
	elseif sui_compare_string(text, "SUI_CMD_STOP_TIMER") then
		-- SUI_CMD_STOP_TIMER
		-- Stop Timer
		Sui_custom_hud_timer_active = false
		Sui_custom_hud_timer_value = 0
		return true
	elseif sui_compare_string(text, "SUI_CMD_STOP_NUMBER") then
		-- SUI_CMD_STOP_NUMBER
		-- Stop Number Display
		Sui_custom_hud_number_active = false
		Sui_custom_hud_number_value = 0
		return true
	elseif sui_compare_string(text, "SUI_CMD_REGION_SUBTITLE") then
		-- SUI_CMD_REGION_SUBTITLE
		-- Force the next message to be displayed in the subtitles area
		Sui_force_message_region = HUD_REGION_SUBTITLES
		return true
	elseif sui_compare_string(text, "SUI_CMD_REGION_DIVERSION") then
		-- SUI_CMD_REGION_DIVERSION
		-- Force the next message to be displayed in the diversion area (aka. Checkpoint Reached area)
		Sui_force_message_region = HUD_REGION_DIVERSION
		return true
	end

	if Sui_custom_hud_active then
		-- SUI_CMD_SET_NUMBER_*
		-- Number set commands (0-1000)
		for i = 0, 1000, 1 do
			if sui_compare_string(text, "SUI_CMD_SET_NUMBER_"..tostring(i)) then
				Sui_custom_hud_number_value = i
				Sui_custom_hud_number_active = true
				return true
			end
		end

		-- SUI_CMD_START_TIMER_*
		-- Timer commands (minimum 0 seconds, up to 600 seconds)
		for i = 0, 600, 1 do
			if sui_compare_string(text, "SUI_CMD_START_TIMER_"..tostring(i)) then
				Sui_custom_hud_timer_value = i
				Sui_custom_hud_timer_active = true
				return true
			end
		end
	end

	return false
end

function hud_msg_new_message(di_h)
	local region_index, priority, text, fade_time, audio_type, audio_id = vint_dataitem_get(di_h)

	-- Handle special SuperUI custom HUD messages (do not display it on the screen) [nclok1405]
	if hud_msg_handle_sui_commands(text) then
		return
	end

	-- Reject tutorial messages [nclok1405]
	if hud_msg_should_be_rejected(text) then
		return
	end

	-- Replace Stash Nag [nclok1405]
	if (text == String_nag_stash) or (text == String_custom_stash) or (text == String_custom_stash_asian) or (text == String_custom_stash_en) then
		if sui_is_zombie() then
			-- Reject in Zombie Uprising. Even if you win, the time rewinds before stash was added. [nclok1405]
			return
		end

		region_index = HUD_REGION_DIVERSION

		if get_language() == "JP" or get_language() == "CH" then
			text = String_custom_stash_asian
		elseif get_language() == "US" then
			text = String_custom_stash_en
		else
			text = String_custom_stash
		end
	end

	-- Region Override [nclok1405]
	if Sui_force_message_region ~= -1 and (region_index == HUD_REGION_HELP) then
		region_index = Sui_force_message_region
		Sui_force_message_region = -1
	end

	local region = Hud_msg_regions[region_index]

	if region == nil then
		debug_print("vint", "Message placed in invalid region, discarding\n")
		return
	end

	-- initialize message
	local msg = {
		di_h = di_h,
		region_index = region_index,
		priority = priority,
		text = text,
		audio_type = audio_type,
		audio_id = audio_id,
		text_obj_h = 0,
	}

	-- insert in region list in priority order
	local	insert_index = region.msgs.num_msgs
	for i = 0, region.msgs.num_msgs - 1 do
		local m = region.msgs[i]
		if m.priority < priority then
			insert_index = i
			break
		end
	end

	-- shift the list down
	for i = region.msgs.num_msgs, insert_index + 1, -1  do
		region.msgs[i] = region.msgs[i - 1]
	end

	-- insert new msg
	region.msgs[insert_index] = msg
	region.msgs.num_msgs = region.msgs.num_msgs + 1
	Hud_msgs[di_h] = msg
	region.is_dirty = true

	hud_msg_fade_process(msg, fade_time)
end

function hud_msg_update_message(di_h)
	local region_index, priority, text, fade_time = vint_dataitem_get(di_h)

	-- Handle special SuperUI custom HUD messages (do not display it on the screen) [nclok1405]
	if hud_msg_handle_sui_commands(text) then
		return
	end

	-- Reject tutorial messages [nclok1405]
	if hud_msg_should_be_rejected(text) then
		return
	end

	-- Replace Stash Nag [nclok1405]
	if (text == String_nag_stash) or (text == String_custom_stash) or (text == String_custom_stash_asian) or (text == String_custom_stash_en) then
		if sui_is_zombie() then
			-- Reject in Zombie Uprising. Even if you win, the time rewinds before stash was added. [nclok1405]
			return
		end

		region_index = HUD_REGION_DIVERSION

		if get_language() == "JP" or get_language() == "CH" then
			text = String_custom_stash_asian
		elseif get_language() == "US" then
			text = String_custom_stash_en
		else
			text = String_custom_stash
		end
	end

	-- Region Override [nclok1405]
	if Sui_force_message_region ~= -1 and (region_index == HUD_REGION_HELP) then
		region_index = Sui_force_message_region
		Sui_force_message_region = -1
	end

	local msg = Hud_msgs[di_h]

	if msg == nil then
		-- we have no record of this data item
		hud_msg_new_message(di_h)
		return
	end

	local region = Hud_msg_regions[msg.region_index]

	-- update the text item if it's changed
	if msg.text ~= text then
		msg.text = text
		if msg.text_obj_h ~= 0 then
			vint_set_property(msg.text_obj_h, "text_tag", text)
		end
	end

	hud_msg_fade_process(msg, fade_time)

	region.is_dirty = true
end

function hud_msg_remove_message(di_h)
	local msg = Hud_msgs[di_h]

	if msg ~= nil then
		-- clean up any existing fade tween
		if msg.fade_tween_h ~= nil then
			vint_object_destroy(msg.fade_tween_h)
		end

		-- destroy text object
		if msg.text_obj_h ~= 0 then
			vint_object_destroy(msg.text_obj_h)
		end

		-- find msg in region
		local region = Hud_msg_regions[msg.region_index]
		local msg_index = -1
		for i = 0, region.msgs.num_msgs - 1 do
			if di_h == region.msgs[i].di_h then
				msg_index = i
				break
			end
		end

		-- remove it
		if msg_index > -1 then
			for i = msg_index + 1, region.msgs.num_msgs - 1 do
				region.msgs[i - 1] = region.msgs[i]
			end

			region.msgs.num_msgs = region.msgs.num_msgs - 1
			region.is_dirty = true
		end
	end

	Hud_msgs[di_h] = nil
end

function hud_msg_fade_process(msg, new_fade)
	local is_fading = (msg.fade_time ~= nil and msg.fade_time ~= 0)
	local should_be_fading = (new_fade > 0)

	if is_fading ~= should_be_fading then
		-- clean up any existing tween
		if msg.fade_tween_h ~= nil then
			vint_object_destroy(msg.fade_tween_h)
		end

		if should_be_fading == true then
			-- start fading
			local o = vint_object_create("msg_fade", "tween", vint_object_find("root_animation"))
			vint_set_property(o, "target_handle", msg.text_obj_h)
			vint_set_property(o, "target_property", "alpha")
			vint_set_property(o, "duration", new_fade)
			vint_set_property(o, "start_value", 1)
			vint_set_property(o, "end_value", 0)
			vint_set_property(o, "start_time", vint_get_time_index())
			msg.fade_tween_h = o
		else
			-- stop fading
			vint_set_property(msg.text_obj_h, "alpha", 1)
		end
	end

	msg.fade_time = new_fade
end

function hud_msg_hide_region(region, hide)
	local region = Hud_msg_regions[region]

	if region ~= nil then
		vint_set_property(region.anchor, "visible", hide == false)
	end
end
