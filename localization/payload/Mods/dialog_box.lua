-- dialog_box.lua: Message Dialogs, and Zombie Uprising Pause Screen
-- Menu Dialog

Dialog_box = {
	handles = { },
}

DIALOG_BOX_OPTION_OFFSET = 30	--	Space between options
DIALOG_BOX_MAX_WIDTH = 515	--	Maximum width of dialog box text
DIALOG_BOX_MIN_WIDTH = 192	--	Minimum width of dialog box text
DIALOG_BOX_BUTTON_WIDTH = 0	--Size of button to include with width of text
DIALOG_BOX_CENTER_SIZE = { X = -1, Y = -1 }
DIALOG_BOX_ANCHOR_OFFSET = { X = -1, Y = -1 }
DIALOG_BOX_UNSELECT_TEXT	= { ["R"] = 0.6235, ["G"] = 0.6353, ["B"] = 0.644 }	-- Color of text when not on the bar
DIALOG_BOX_HIGHLIGHT_TEXT 	= { ["R"] = 0, ["G"] = 0, ["B"] = 0 }								--	Color of text when on the bar

DIALOG_RESULT_INVALID 		= -1

DIALOG_ACTION_INVALID 		= -1
DIALOG_ACTION_NONE 			= 0
DIALOG_ACTION_FORCE_CLOSED = 1
DIALOG_ACTION_CLOSE 			= 2
DIALOG_ACTION_NAVIGATE 		= 3

DIALOG_PRIORITY_INFORMATION 		= 0
DIALOG_PRIORITY_ACTION 				= 1
DIALOG_PRIORITY_GAME_CRITICAL		= 2
DIALOG_PRIORITY_SYSTEM_CRITICAL	= 3

DIALOG_RESULT_YES = 0
DIALOG_RESULT_NO 	= 1

Dialog_input_block = false
Dialog_on_top = false
Dialog_menu_base_input_block = false
Dialog_pause_disconnect_dialog_handle = 0

-------------------------
--[ UTILITY FUNCTIONS ]--
-------------------------
-- helper function to set a text tag
function dialog_box_set_tag(handle, value)
	if type(value) == "number" then
		vint_set_property(handle, "text_tag_crc", value)
	elseif type(value) == "string" then
		vint_set_property(handle, "text_tag", value)
	else
	end
end

-------------------------------
--[ INITIALIZE AND SHUTDOWN ]--
-------------------------------
function dialog_box_init()
	debug_print("SuperUI for SR2 v"..tostring(SUI_VERSION).."\n")

	-- Find out if we're running SR2 rerelease [nclok1405]
	-- Check for proposed 'get_shared_variable' and 'set_shared_variable' functions
	local found_get_shared_variable = false
	local found_set_shared_variable = false

	for k, v in pairs(_G) do
		--debug_print(tostring(k) .. ":" .. tostring(v))
		if k == "get_shared_variable" then
			found_get_shared_variable = true
		end
		if k == "set_shared_variable" then
			found_set_shared_variable = true
		end
	end
	if found_get_shared_variable and found_set_shared_variable then
		Sui_sr2_rerelease = true
		debug_print("SR2 Rerelease Detected\n")

		-- Add SuperUI version to the shared variable so the gameplay context knows about our existence
		set_shared_variable("sui_version", SUI_VERSION)
	else
		debug_print("SR2 is 2009 Version\n")
	end

	--debug_print("vint", "Dialog Init Start()\n")

	local dialog_h = vint_object_find("dialog_box")
	local d = Dialog_box
	d.handles = { }
	d.handles["dialog"] 		= dialog_h
	d.handles["box"] 			=  vint_object_find("box", dialog_h)
	d.handles["background"] =  vint_object_find("background", dialog_h)
	d.handles["heading"]		 = vint_object_find("header_text", dialog_h)
	d.handles["body"]			= vint_object_find("body_text", dialog_h)
	d.handles["spinner"]			= vint_object_find("spinner", dialog_h)
	d.handles["option"]		= vint_object_find("option_text", dialog_h)
	d.handles["select"]		= vint_object_find("select_bar", dialog_h)
	d.handles["selections"]	= vint_object_find("selections", dialog_h)
	d.handles["sel_bar_e"] = vint_object_find("sel_bar_e", dialog_h)
	d.handles["sel_bar_e_highlight"] = vint_object_find("sel_bar_e_highlight", dialog_h)
	d.handles["sel_bar_w"] = vint_object_find("sel_bar_w", dialog_h)
	d.handles["sel_bar_w_highlight"] = vint_object_find("sel_bar_w_highlight", dialog_h)

	d.heading_x, d.heading_y = vint_get_property(d.handles["heading"]	, "anchor")
	d.body_x, d.body_y = vint_get_property(d.handles["body"]	, "anchor")

	local box_h = vint_object_find("static_elements", dialog_h)
	d.handles["box_c"] = vint_object_find("box_c", box_h)
	d.handles["box_e"] = vint_object_find("box_e", box_h)
	d.handles["box_n"] = vint_object_find("box_n", box_h)
	d.handles["box_ne"] = vint_object_find("box_ne", box_h)
	d.handles["box_w"] = vint_object_find("box_w", box_h)
	d.handles["box_s"] = vint_object_find("box_s", box_h)
	d.handles["box_sw"] = vint_object_find("box_sw", box_h)
	d.handles["box_se"] = vint_object_find("box_se", box_h)

	--Animations
	d.handles["fade_in_anim"] = vint_object_find("fade_in")
	d.handles["fade_out_anim"] = vint_object_find("fade_out")
	vint_set_property(d.handles["fade_in_anim"], "is_paused", true)
	vint_set_property(d.handles["fade_out_anim"], "is_paused", true)

	--Paused stuff
	d.handles["paused"] = vint_object_find("paused")
	d.handles["game_paused_text"] = vint_object_find("game_paused_text", d.handles["paused"])
	d.handles["partner_paused"] = vint_object_find("partner_paused", d.handles["paused"])
	d.handles["paused_background"] = vint_object_find("background", d.handles["paused"])

	--Coop invite message
	d.handles.player_invited_you = vint_object_find("player_invited_you")
	d.handles.player_invited_you_text = vint_object_find("invite_text", d.handles.player_invited_you)

	--..Coop invite fade out
	d.handles.coop_invite_fade_out = vint_object_find("coop_invite_fade_out")
	vint_set_property(d.handles.coop_invite_fade_out, "is_paused", true)

	--end callback
	local twn_h = vint_object_find("background_alpha_twn_1", d.handles["fade_out_anim"])
	vint_set_property(twn_h, "end_event", "dialog_box_close_thesequel")

	--Initialize Spinner
	dialog_box_use_spinner(false)

	DIALOG_BOX_CENTER_SIZE.X, DIALOG_BOX_CENTER_SIZE.Y = element_get_actual_size(d.handles["box_c"])
	DIALOG_BOX_ANCHOR_OFFSET.X, DIALOG_BOX_ANCHOR_OFFSET.Y = vint_get_property(d.handles["box"], "anchor")

	--Hide all elements until needed.
	vint_set_property(d.handles["paused"], "visible", false)
	vint_set_property(dialog_h, "visible", false)

	--Set A Button
	local btn_h = vint_object_find("btn_select")
	vint_set_property(btn_h, "image", get_a_button())

	if get_platform() == "PC" then
		vint_set_property(btn_h, "visible", false)
	end

	local btn_h = vint_object_find("btn_select_highlight")
	vint_set_property(btn_h, "image", get_a_button())

	if get_platform() == "PC" then
		vint_set_property(btn_h, "visible", false)
	end

	--This is evil, but will help with menu swapping.
	thread_new("vint_menu_swap_thread")

	if SUI_DEBUG_SHOW_VINT_DOC_LIST then
		-- DEBUG: Show the list of loaded vint_doc [nclok1405]
		thread_new("dialog_box_debug_update_vint_doc_list")
	else
		-- Stopwatch Tool [nclok1405]
		thread_new("dialog_box_stopwatch_tool_thread")
	end
end

-- Stopwatch Tool [nclok1405]
function dialog_box_stopwatch_tool_thread()
	local d = Dialog_box
	local audio_3 = false
	local audio_2 = false
	local audio_1 = false

	while true do
		thread_yield()

		if Sui_stopwatch_enabled then
			if not Sui_stopwatch_countdown_finished then
				-- Start Countdown
				Sui_stopwatch_countdown = Sui_stopwatch_countdown - get_frame_time()
				if Sui_stopwatch_countdown < 0 then
					Sui_stopwatch_countdown = 0
				end

				vint_set_property(d.handles["paused"], "visible", true)
				vint_set_property(d.handles["paused"], "alpha", 1)
				vint_set_property(d.handles["paused_background"], "visible", true)
				vint_set_property(d.handles["game_paused_text"], "text_tag", "[format][color:green]" .. sui_get_human_readable_time_float(Sui_stopwatch_countdown) .. "[/format]")
				vint_set_property(d.handles["partner_paused"], "visible", true)
				vint_set_property(d.handles["partner_paused"], "text_tag", "READY")

				if (not audio_3) and (Sui_stopwatch_countdown <= 3) then
					audio_play("SFX_DEMODERBY_3")
					audio_3 = true
				end
				if (not audio_2) and (Sui_stopwatch_countdown <= 2) then
					audio_play("SFX_DEMODERBY_2")
					audio_2 = true
				end
				if (not audio_1) and (Sui_stopwatch_countdown <= 1) then
					audio_play("SFX_DEMODERBY_1")
					audio_1 = true
				end
				if Sui_stopwatch_countdown <= 0 then
					audio_play("SFX_DEMODERBY_GO")
					Sui_stopwatch_countdown_finished = true
				end
			else
				Sui_stopwatch_timer = Sui_stopwatch_timer - get_frame_time()

				if Sui_stopwatch_timer <= 0 then
					Sui_stopwatch_enabled = false
					audio_play("SFX_GRENADE_EXP")
					audio_3 = false
					audio_2 = false
					audio_1 = false
					Sui_stopwatch_countdown_finished = false

					vint_set_property(d.handles["paused"], "visible", true)
					vint_set_property(d.handles["paused"], "alpha", 1)
					vint_set_property(d.handles["paused_background"], "visible", true)
					vint_set_property(d.handles["game_paused_text"], "text_tag", "[format][color:red]" .. sui_get_human_readable_time_float(0) .. "[/format]")
					vint_set_property(d.handles["partner_paused"], "visible", true)
					vint_set_property(d.handles["partner_paused"], "text_tag", "DIVERSION_STREAKING_RAN_OUT_OF_TIME_TEXT")
					delay(1)

					vint_set_property(d.handles["paused"], "visible", false)
					vint_set_property(d.handles["paused"], "alpha", 0)
					vint_set_property(d.handles["paused_background"], "visible", false)
					vint_set_property(d.handles["game_paused_text"], "text_tag", "")
					vint_set_property(d.handles["partner_paused"], "visible", false)
					vint_set_property(d.handles["partner_paused"], "text_tag", "")
				else
					vint_set_property(d.handles["paused"], "visible", true)
					vint_set_property(d.handles["paused"], "alpha", 1)
					vint_set_property(d.handles["paused_background"], "visible", true)
					vint_set_property(d.handles["game_paused_text"], "text_tag", "[format][color:yellow]" .. sui_get_human_readable_time_float(Sui_stopwatch_timer) .. "[/format]")
					vint_set_property(d.handles["partner_paused"], "visible", true)
					vint_set_property(d.handles["partner_paused"], "text_tag", "SUI_STOPWATCH_TEST")
				end
			end
		end
	end
end

-- DEBUG: Show the list of loaded vint_doc [nclok1405]
function dialog_box_debug_update_vint_doc_list()
	local d = Dialog_box

	while true do
		local s = ""

		for k, v in pairs(SUI_VINT_DOC_LIST) do
			if vint_document_find(v) ~= 0 then
				s = s .. v .. "\n"
			end
		end

		vint_set_property(d.handles["paused"], "visible", true)
		vint_set_property(d.handles["paused"], "alpha", 1)
		vint_set_property(d.handles["paused_background"], "visible", false)
		vint_set_property(d.handles["game_paused_text"], "text_tag", "")
		vint_set_property(d.handles["partner_paused"], "visible", true)
		vint_set_property(d.handles["partner_paused"], "text_tag", s)

		thread_yield()
	end
end

function dialog_box_cleanup()

end

---------------------
--[ FUNCTIONALITY	]--
---------------------
function dialog_box_grab_input()
	if Dialog_box.input_subs ~= nil then
		return
	end

	local subscription_priority = 125
	if Dialog_on_top == true then
		subscription_priority = 200
	end

	--	Subscribe to the input
	Dialog_box.input_subs = {
		vint_subscribe_to_input_event(nil, "nav_up",				"dialog_box_input", subscription_priority),
		vint_subscribe_to_input_event(nil, "nav_down",			"dialog_box_input", subscription_priority),
		vint_subscribe_to_input_event(nil, "select",				"dialog_box_input", subscription_priority),
		vint_subscribe_to_input_event(nil, "pause",				"dialog_box_input", subscription_priority),
		vint_subscribe_to_input_event(nil, "back",				"dialog_box_input", subscription_priority),
		vint_subscribe_to_input_event(nil, "all_unassigned",	"dialog_box_input", subscription_priority),
	}
end

function dialog_box_release_input()
	if Dialog_box.input_subs == nil then
		return
	end

	--	Unsubscribe to input
	for idx, val in Dialog_box.input_subs do
		vint_unsubscribe_to_input_event(val)
	end
	Dialog_box.input_subs = nil
end

function dialog_box_open(header, body, options, callback, default, priority, is_confirmation, is_spinner, is_close_on_death, is_close_on_damage)
	if Dialog_menu_base_input_block == false then
		if vint_document_find("menu_base") ~= 0 then
			Dialog_menu_base_input_block = true
			menu_input_block(true)
		end
	end

	if priority == nil then
		priority = DIALOG_PRIORITY_ACTION
	end

	if callback == nil then
		callback = "dialog_box_do_nothing"
	end

	if is_confirmation ~= true then
		is_confirmation = false
	end

	if is_spinner ~= true then
		is_spinner = false
	end

	if is_close_on_death == nil then
		is_close_on_death = true
	end
	if is_close_on_damage == nil then
		is_close_on_damage = false
	end

	local handle = dialog_box_create_internal(header, body, callback, priority, is_confirmation, is_spinner, options[0], options[1], options[2], options[3], default, is_close_on_death, is_close_on_damage)
	Dialog_input_block = false

	return handle
end

function dialog_box_open_internal(handle, header, body, default, is_spinner, is_confirmation, priority, fullscreen_fade, option_1, option_2, option_3, option_4)
	--debug_print("header:"..tostring(header))
	--debug_print("body:"..tostring(body))

	-- Show "Single Player" for "Waiting for Player" dialog (experimental) [nclok1405]
	-- 2026-10-18 ZH fix: Juice used a fabricated tag -- SUI_LAN / COOP_SP --
	-- that exists in NO language table, so the raw tag leaked onto the screen.
	-- Use the real official tag MENU_TITLE_NOTICE instead, properly localized.
	if sui_compare_string(body, "MULTI_COOP_WAITING_PLAYER_2") and (option_2 == nil) then
		header = body
		body = "MENU_TITLE_NOTICE"
		option_2 = "CONTROL_CANCEL"
	end

	-- Dialog Fix for More Mission Checkpoints mod [nclok1405]
	if sui_compare_string(header, "NULL") and sui_compare_string(body, "NULL") and (get_game_play_mode() == "Mission") then
		header = "MISSION_COOP_SKIP_PROMPT"
		if (get_language() == "US") then
			body = "Do you wish to skip this mission?"
		elseif (get_language() == "JP") then
			body = vint_insert_values_in_string("{0}?", {[0] = "REPLAY_LEVEL_SKIP"})
		else
			body = vint_insert_values_in_string("{0} {1}?", {[0] = "MISSION_COOP_SKIP_PROMPT", [1] = "MULTI_MODE_5"})
		end
		option_1 = "OPTION_YES"
		option_2 = "OPTION_NO"
	end

	-- Mod Mission Play Prompt [nclok1405]
	if (Sui_mod_mission_title ~= "") and sui_compare_string(body, "STRONGHOLD_RESTART_PROMPT") then
		header = Sui_mod_mission_title
		body = "SUI_MOD_MISSION_CONFIRM"
	end

	-- Stronghold cancel prompt during Mod Missions [nclok1405]
	if (Sui_mod_mission_title ~= "") and sui_compare_string(header, "STRONG_CANCEL_TITLE") then
		header = "MISSION_CANCEL_TITLE"
		body = "MISSION_CANCEL_TEXT"
	end

	local d = Dialog_box
	d.handle 	= handle

	-- Store the header and body
	d.header = header
	d.body = body
	d.is_confirmation = is_confirmation

	-- Make sure we deleted old options (chained dialogs)
	if d.options ~= nil then
		-- Delete the clones, 1st one isn't a clone
		for i = 1, d.options.num_options - 1 do
			vint_object_destroy(d.options[i].label_h)
		end
		d.options.num_options = 0
	end

	--	Store the options
	d.options = { num_options = 0 }
	if option_1 ~= nil then
		d.options[d.options.num_options] = { label = option_1 }
		d.options.num_options = d.options.num_options + 1
	end
	if option_2 ~= nil then
		d.options[d.options.num_options] = { label = option_2 }
		d.options.num_options = d.options.num_options + 1
	end
	if option_3 ~= nil then
		d.options[d.options.num_options] = { label = option_3 }
		d.options.num_options = d.options.num_options + 1
	end
	if option_4 ~= nil then
		d.options[d.options.num_options] = { label = option_4 }
		d.options.num_options = d.options.num_options + 1
	end

	d.cur_idx = 0

	--	Set the current item selected in the dialog
	if default < d.options.num_options and default >= 0 then
		d.cur_idx = default
	end

	--	Get the current position for the options
	local anchor = { }
	anchor.x, anchor.y = vint_get_property(d.handles["option"], "anchor")

	-- Set Text Tags and positions
	dialog_box_set_tag(d.handles["heading"], d.header)
	dialog_box_set_tag(d.handles["body"], d.body)

	--Reset header and spinersize
	vint_set_property(d.handles["heading"], "scale", 1, 1)
	vint_set_property(d.handles["spinner"], "scale", 1, 1)

	--Move body to original position
	vint_set_property(d.handles["body"], "anchor", d.body_x, d.body_y)

	--check width of box without word wrap
	vint_set_property(d.handles["body"], "word_wrap" , false)

	--Dialog box has to be smaller if we are using a spinner
	local dialog_box_max_width_internal = DIALOG_BOX_MAX_WIDTH
	if is_spinner == true then
		dialog_box_max_width_internal  = DIALOG_BOX_MAX_WIDTH - 33
	end

	--Get width / height of body of text in dialog
	local body_width, body_height =	element_get_actual_size(d.handles["body"])
	local heading_width, heading_height = element_get_actual_size(d.handles["heading"])
	local max_text_width = body_width

	if body_width > dialog_box_max_width_internal then
		--If text is larger than max width reset the word wrap to true
		vint_set_property(d.handles["body"], "word_wrap" , true)

		--Reset the wrap width
		vint_set_property(d.handles["body"], "wrap_width" , dialog_box_max_width_internal)
		max_text_width = dialog_box_max_width_internal
	end

	if heading_width > max_text_width then
		if heading_width > dialog_box_max_width_internal then
			--heading is too big... we need to resize it.
			local target_scale = dialog_box_max_width_internal / heading_width
			local og_heading_height = heading_height
			vint_set_property(d.handles["heading"], "scale", target_scale, target_scale)

			--reset sizes after we resized stuff
			heading_width, heading_height = element_get_actual_size(d.handles["heading"])

			--move position of body
			local body_vertical_offset = og_heading_height - heading_height

			vint_set_property(d.handles["body"], "anchor", d.body_x, d.heading_y + heading_height )
		end

		--Oh k... so the header is larger than where we want the body to be...
		vint_set_property(d.handles["body"], "wrap_width" , heading_width)
		max_text_width = heading_width
	end

	--Sizes likely have changed so lets verify everything.
	body_width, body_height =	element_get_actual_size(d.handles["body"])

	--	Adjust the position for the first option
	local body_anchor = { }
	body_anchor.x, body_anchor.y = vint_get_property(d.handles["body"], "anchor")

	local selections_anchor = {}
	selections_anchor.x, selections_anchor.y = vint_get_property(d.handles["selections"], "anchor")
	selections_anchor.y = body_anchor.y + body_height
	vint_set_property(d.handles["selections"], "anchor", selections_anchor.x, selections_anchor.y)

	local option_max_width = 0
	if d.options.num_options > 0 then
		--	Create the options
		d.options[0].label_h = d.handles["option"]

		dialog_box_set_tag(d.options[0].label_h, d.options[0].label)
		vint_set_property(d.options[0].label_h, "tint", DIALOG_BOX_UNSELECT_TEXT.R, DIALOG_BOX_UNSELECT_TEXT.G, DIALOG_BOX_UNSELECT_TEXT.B)
		vint_set_property(d.options[0].label_h, "anchor", anchor.x, anchor.y )
		vint_set_property(d.options[0].label_h, "visible", true)

		option_max_width = element_get_actual_size(d.options[0].label_h) + DIALOG_BOX_BUTTON_WIDTH
		if option_max_width > max_text_width then
			max_text_width = option_max_width
		end

		for i = 1, d.options.num_options - 1 do
			d.options[i].label_h = vint_object_clone(d.handles["option"])
			dialog_box_set_tag(d.options[i].label_h, d.options[i].label)
			anchor.y = anchor.y + DIALOG_BOX_OPTION_OFFSET
			vint_set_property(d.options[i].label_h, "anchor", anchor.x, anchor.y)
			vint_set_property(d.options[i].label_h, "tint", DIALOG_BOX_UNSELECT_TEXT.R, DIALOG_BOX_UNSELECT_TEXT.G, DIALOG_BOX_UNSELECT_TEXT.B)

			option_max_width = element_get_actual_size(d.options[i].label_h) + DIALOG_BOX_BUTTON_WIDTH
			if option_max_width > max_text_width then
				max_text_width = option_max_width
			end
		end
	end

	--	Resize the dialog to fit all the text
	local center_width = floor(max_text_width)
	local center_height = floor(anchor.y + selections_anchor.y)
	local se_x, se_y, anchor_x, anchor_y

	if center_width < DIALOG_BOX_MIN_WIDTH then
		center_width = DIALOG_BOX_MIN_WIDTH
	end

	--Add/subtract padding to accomodate for box padding

	center_width = center_width + 10
	center_height = center_height - 48

	if d.options.num_options == 0 then
		center_width = dialog_box_max_width_internal
	end

	element_set_actual_size(d.handles["box_c"], center_width, center_height)

	local WEST_TO_CENTER_OFFSET = 79
	local EAST_TO_CENTER_OFFSET = 72
	local EAST_TO_CENTER_BOTTOM_OFFSET = EAST_TO_CENTER_OFFSET + 6
	local CENTER_X, CENTER_Y = vint_get_property(d.handles["box_c"], "anchor")
	local CENTER_OFFSET = WEST_TO_CENTER_OFFSET + EAST_TO_CENTER_OFFSET

	--NORTH
	se_x, se_y = vint_get_property(d.handles["box_n"], "source_se")
	vint_set_property(d.handles["box_n"], "source_se", center_width - CENTER_OFFSET, se_y)

	--NORTHEAST
	anchor_x, anchor_y = vint_get_property(d.handles["box_ne"], "anchor")
	vint_set_property(d.handles["box_ne"], "anchor", center_width - EAST_TO_CENTER_OFFSET + CENTER_X , anchor_y)

	--EAST
	se_x, se_y = vint_get_property(d.handles["box_e"], "source_se")
	vint_set_property(d.handles["box_e"], "source_se", se_x, center_height)
	anchor_x, anchor_y = vint_get_property(d.handles["box_e"], "anchor")
	vint_set_property(d.handles["box_e"], "anchor", center_width + CENTER_X, anchor_y)

	--SOUTHEAST
	anchor_x, anchor_y = vint_get_property(d.handles["box_se"], "anchor")
	vint_set_property(d.handles["box_se"], "anchor", center_width - EAST_TO_CENTER_OFFSET + CENTER_X, center_height + CENTER_Y)

	--SOUTH
	se_x, se_y = vint_get_property(d.handles["box_s"], "source_se")
	vint_set_property(d.handles["box_s"], "source_se", center_width - EAST_TO_CENTER_BOTTOM_OFFSET - WEST_TO_CENTER_OFFSET, se_y)
	anchor_x, anchor_y = vint_get_property(d.handles["box_s"], "anchor")
	vint_set_property(d.handles["box_s"], "anchor", anchor_x, center_height + CENTER_Y)

	--SOUTHWEST
	anchor_x, anchor_y = vint_get_property(d.handles["box_sw"], "anchor")
	vint_set_property(d.handles["box_sw"], "anchor", anchor_x, center_height + CENTER_Y)

	--WEST
	se_x, se_y = vint_get_property(d.handles["box_w"], "source_se")
	vint_set_property(d.handles["box_w"], "source_se", se_x, center_height)

	-- Show the Dialog
	vint_set_property(d.handles["dialog"], "visible", true)

	--	Move the selector bar
	if d.options.num_options > 0 then
		local select_anchor = { }

		select_anchor.x, select_anchor.y = vint_get_property(d.options[d.cur_idx].label_h, "anchor")
		select_anchor.x = vint_get_property(d.handles["select"], "anchor")
		vint_set_property(d.handles["select"], "anchor", select_anchor.x, select_anchor.y)

		--	Adjust the position for the first option
		local body_anchor = { }
		body_anchor.x, body_anchor.y = vint_get_property(d.handles["body"], "anchor")

		local selections_anchor = {}
		selections_anchor.x, selections_anchor.y = vint_get_property(d.handles["selections"], "anchor")
		selections_anchor.y = body_anchor.y + body_height
		vint_set_property(d.handles["selections"], "visible", true)
		vint_set_property(d.handles["selections"], "anchor", selections_anchor.x, selections_anchor.y)
		vint_set_property(d.options[d.cur_idx].label_h, "tint", DIALOG_BOX_HIGHLIGHT_TEXT.R, DIALOG_BOX_HIGHLIGHT_TEXT.G, DIALOG_BOX_HIGHLIGHT_TEXT.B)
	else
		vint_set_property(d.handles["selections"], "visible", false)
	end

	local SELECTOR_BAR_WIDTH_OFFSET = 0
	--Resize selector bar
	se_x, se_y = vint_get_property(d.handles["sel_bar_w"] , "source_se")
	vint_set_property(d.handles["sel_bar_w"] , "source_se", center_width + SELECTOR_BAR_WIDTH_OFFSET , se_y)
	vint_set_property(d.handles["sel_bar_w_highlight"] , "source_se", center_width + SELECTOR_BAR_WIDTH_OFFSET , se_y)

	anchor_x, anchor_y = vint_get_property(d.handles["sel_bar_e"], "anchor")
	local selector_anchor = { }
	selector_anchor.x, selector_anchor.y = vint_get_property(d.handles["sel_bar_w"], "anchor")
	vint_set_property(d.handles["sel_bar_e"], "anchor", center_width + selector_anchor.x + SELECTOR_BAR_WIDTH_OFFSET , anchor_y)
	vint_set_property(d.handles["sel_bar_e_highlight"], "anchor", center_width + selector_anchor.x + SELECTOR_BAR_WIDTH_OFFSET , anchor_y)

	local original_offset = {}
	original_offset.x = DIALOG_BOX_ANCHOR_OFFSET.X + (DIALOG_BOX_CENTER_SIZE.X / 2 )
	original_offset.y = DIALOG_BOX_ANCHOR_OFFSET.Y + (DIALOG_BOX_CENTER_SIZE.Y / 2 )

	local current_offset = {}
	current_offset.x = DIALOG_BOX_ANCHOR_OFFSET.X + (center_width / 2 )
	current_offset.y = DIALOG_BOX_ANCHOR_OFFSET.Y + (center_height / 2 )

	vint_set_property(d.handles["box"], "anchor", DIALOG_BOX_ANCHOR_OFFSET.X - (current_offset.x - original_offset.x), DIALOG_BOX_ANCHOR_OFFSET.Y - (current_offset.y - original_offset.y))

	Dialog_input_block = false

	if priority == DIALOG_PRIORITY_SYSTEM_CRITICAL then
		Dialog_on_top = true
	else
		Dialog_on_top = false
	end

	--Set depth of pause/dialog
	if Dialog_on_top == true then
		vint_set_property(d.handles["dialog"], "depth", -10)
		vint_set_property(d.handles["paused"], "depth", 0)
	else
		vint_set_property(d.handles["dialog"], "depth", 0)
		vint_set_property(d.handles["paused"], "depth", -10)
	end

	dialog_box_grab_input()

	-- Play the open sound
	if d.options.num_options < 2 then
		audio_play(DIALOG_OPEN_SOUND)
	else
		audio_play(DIALOG_SERIOUS_SOUND)
	end

	-- Use the spinner if necessary
	dialog_box_use_spinner(is_spinner)

	--	 FADE IN ANIMATION GOES HERE
	if fullscreen_fade == true then
		vint_set_property(d.handles["background"], "alpha", 1)
		vint_set_property(d.handles["box"], "alpha", 1)
	else
		vint_set_property(d.handles["background"], "alpha", 0.5)
		vint_set_property(d.handles["fade_out_anim"], "is_paused", true)
		lua_play_anim(d.handles["fade_in_anim"], 0)
	end
end

function dialog_box_input(target, event, accelleration)
	if Dialog_input_block == true then
		return
	end
	local d = Dialog_box
	local old_idx = -1

	if d.options.num_options == 0 then
		-- this is a system dialog so no input
		return
	end

	-- Up
	if event == "nav_up" then
		old_idx = d.cur_idx				--	Store the old index
		if d.cur_idx == 0 then			--	Wrap around if we have to
			d.cur_idx = d.options.num_options - 1
		else
			d.cur_idx = d.cur_idx - 1	--	Otherwise move it up
		end
	-- Down
	elseif event == "nav_down" then
		old_idx = d.cur_idx				--	Store the old index
		if d.cur_idx == d.options.num_options - 1 then
			d.cur_idx = 0					--	Wrap around...
		else
			d.cur_idx = d.cur_idx + 1	--	Move it down
		end
	-- Select
	elseif event == "select" then
		Dialog_input_block = true
		dialog_box_select()
	-- Cancel
--	elseif event == "back" then
--		--if d.is_confirmation == true then
--		if d.options.num_options > 0 then
--			Dialog_input_block = true
--			dialog_box_set_result(d.handle, DIALOG_RESULT_INVALID, DIALOG_ACTION_FORCE_CLOSED)
--		end
	end

	-- Move the select bar if we changed options
	if old_idx ~= -1 then
		--	Get the anchor of the top one
		local anchor = { }
		anchor.x, anchor.y = vint_get_property(d.handles["option"], "anchor")
		anchor.x = vint_get_property(d.handles["select"], "anchor")

		--	Fix the color on the old option
		vint_set_property(d.options[old_idx].label_h, "tint", DIALOG_BOX_UNSELECT_TEXT.R, DIALOG_BOX_UNSELECT_TEXT.G, DIALOG_BOX_UNSELECT_TEXT.B)
		-- Move the selection bar
		vint_set_property(d.handles["select"], "anchor", anchor.x, anchor.y + (d.cur_idx * DIALOG_BOX_OPTION_OFFSET))
		--	Fix the tint on the new option
		vint_set_property(d.options[d.cur_idx].label_h, "tint", DIALOG_BOX_HIGHLIGHT_TEXT.R, DIALOG_BOX_HIGHLIGHT_TEXT.G, DIALOG_BOX_HIGHLIGHT_TEXT.B)
		dialog_box_set_result(d.handle, d.cur_idx, DIALOG_ACTION_NAVIGATE)
	end
end

function dialog_box_close(force)
	local d = Dialog_box
	if force == true then
		--	FORCE CLOSE
		dialog_box_close_thesequel()
	else
		-- DON'T FORCE CLOSE, JUST ANIMATE OUT, callback will occur
		lua_play_anim(d.handles["fade_out_anim"], 0)
	end
end

function dialog_box_close_thesequel()
	local d = Dialog_box

	if Dialog_menu_base_input_block == true then
		Dialog_menu_base_input_block = false
		if vint_document_find("menu_base") ~=0 then
			menu_input_block(false)
		end
	end

	if d.handles ~= nil then
		--	Hide the Dialog Box
		vint_set_property(d.handles["dialog"], "visible", false)
	end

	if d.options ~= nil then
		-- Delete the clones, 1st one isn't a clone
		for i = 1, d.options.num_options - 1 do
			vint_object_destroy(d.options[i].label_h)
		end
		d.options.num_options = 0
	end

	dialog_box_release_input()
end

function dialog_box_use_spinner(is_active)
	local d = Dialog_box
	if is_active == true then
		--show spinner and update layout
		vint_set_property(d.handles["spinner"], "visible", true)
		local w, h = element_get_actual_size(d.handles["spinner"])
		local s_w, s_h = vint_get_property(d.handles["heading"], "scale")
		local x = d.heading_x + w * s_w
		vint_set_property(d.handles["heading"], "anchor", x, d.heading_y)
	else
		--hide spinner and update layout
		vint_set_property(d.handles["heading"], "anchor", d.heading_x, d.heading_y)
		vint_set_property(d.handles["spinner"], "visible", false)
	end
end


function dialog_box_select()
	local d = Dialog_box

--	dialog_box_close()
	audio_play(Menu_sound_select)

	-- Send the selection to C
	dialog_box_set_result(d.handle, d.cur_idx, DIALOG_ACTION_CLOSE)
end

function dialog_box_do_nothing(option, action)
end

---------------------
--[	TEMPLATES	]--
---------------------
function dialog_box_confirmation(header, body, callback, is_close_on_death, is_close_on_damage)
	local default = 0
	local priority = DIALOG_PRIORITY_ACTION
	local options = { [0] = "CONTROL_YES", [1] = "CONTROL_NO" }
	return dialog_box_open(header, body, options, callback, default, priority, true, nil, is_close_on_death, is_close_on_damage)
end

function dialog_box_message(header, body, is_close_on_death, is_close_on_damage)
	local default = 0
	local priority = DIALOG_PRIORITY_ACTION
	local options = { [0] = "CONTROL_CONTINUE" }
	return dialog_box_open(header, body, options, nil, 0, priority, false, nil, is_close_on_death, is_close_on_damage)
end

function dialog_box_message_critical(header, body, is_close_on_death, is_close_on_damage)
	local default = 0
	local priority = DIALOG_PRIORITY_SYSTEM_CRITICAL
	local options = { [0] = "CONTROL_CONTINUE" }
	return dialog_box_open(header, body, options, nil, 0, priority, false, nil, is_close_on_death, is_close_on_damage)
end

---------------------
--[	PAUSED	]--
---------------------
Dialog_pause_input_subs = 0
Dialog_pause_partner_paused = false
Dialog_pause_input_block = false
Dialog_pause_allow_disconnect = false

function dialog_pause_show(partner_paused, just_show_disconnect)
	local d = Dialog_box
	vint_set_property(d.handles["paused"], "visible", true)
	vint_set_property(d.handles["paused"], "alpha", 1)
	vint_set_property(d.handles["paused_background"], "visible", true)
	vint_set_property(d.handles["game_paused_text"], "text_tag", "MENU_GAME_PAUSED")

	if Dialog_pause_input_subs ~= 0 then
		return
	end

	-- Pause Active [nclok1405]
	Sui_paused = true

	if partner_paused == true then
		Dialog_pause_partner_paused = true

		local coop_title = vint_insert_values_in_string("{0} {1}", {[0] = "COOP_TITLE", [1] = "PAUSEMENU_TITLE"})
		vint_set_property(d.handles["game_paused_text"], "text_tag", coop_title)

		vint_set_property(d.handles["partner_paused"], "visible", true)
		vint_set_property(d.handles["partner_paused"], "text_tag", "DIALOG_PAUSE_START_TO_DISCONNECT")

		if sui_is_zombie() then
			-- Zombie Uprising partner paused [nclok1405]
			local insert_values = {
				[0] = "ACT_ZOMBIE_HUD_HIGH_SCORE",
				[1] = format_cash(Sui_zombie_high_score),
				[2] = "ACT_ZOMBIE_HUD_SCORE",
				[3] = format_cash(Sui_zombie_final_score),
				[4] = "ACT_ZOMBIE_HUD_ZOMBIES_KILLED",
				[5] = format_cash(Sui_zombie_final_kills),
				[6] = "DIALOG_PAUSE_START_TO_DISCONNECT",
			}
			local msg = vint_insert_values_in_string("{0} {1}\n{2} {3}\n{4} {5}\n\n{6}", insert_values)
			vint_set_property(d.handles["partner_paused"], "text_tag", msg)
		end
	else
		Dialog_pause_partner_paused = false
	end

	if just_show_disconnect then
		Dialog_pause_allow_disconnect = true
		vint_set_property(d.handles["partner_paused"], "visible", true)
		vint_set_property(d.handles["partner_paused"], "text_tag", "COOP_DISCONNECT")
	else
		Dialog_pause_allow_disconnect = false
	end

	if not partner_paused and not just_show_disconnect then
		local msg = vint_insert_values_in_string("{PAUSE_MENU_IMG} {0}", {[0] = "MENU_RESUME"})

		if sui_is_zombie() then
			-- Zombie Uprising Messages [nclok1405]
			local title = vint_insert_values_in_string("{0} {1}", {[0] = "ACT_ZOMBIE_DISPLAY_NAME", [1] = "PAUSEMENU_TITLE"})
			vint_set_property(d.handles["game_paused_text"], "text_tag", title)

			local insert_values = {
				[0] = "ACT_ZOMBIE_HUD_HIGH_SCORE",
				[1] = format_cash(Sui_zombie_high_score),
				[2] = "ACT_ZOMBIE_HUD_SCORE",
				[3] = format_cash(Sui_zombie_final_score),
				[4] = "ACT_ZOMBIE_HUD_ZOMBIES_KILLED",
				[5] = format_cash(Sui_zombie_final_kills),
				[6] = "MENU_RESUME",
				[7] = "COMPLETION_QUIT_ZOMBIE",
				[8] = "DOWNLOADABLE_REMOVED_CANCEL",
			}
			msg = vint_insert_values_in_string("{0} {1}\n{2} {3}\n{4} {5}\n\n{PAUSE_MENU_IMG} {6}\n{CANCEL_ACTIVITY_IMG}{CANCEL_ACTIVITY_IMG}{CANCEL_ACTIVITY_IMG} {7}\n{MAP_MENU_IMG} {8}", insert_values)
		end

		vint_set_property(d.handles["partner_paused"], "text_tag", msg)
		vint_set_property(d.handles["partner_paused"], "visible", true)
	end

	--	Subscribe to the input
	Dialog_pause_input_subs = {
		vint_subscribe_to_input_event(nil, "pause",				"dialog_pause_input", 150),
		vint_subscribe_to_input_event(nil, "map",				"dialog_pause_input", 150),
		vint_subscribe_to_input_event(nil, "dpad_down",			"dialog_pause_input", 150),
		vint_subscribe_to_input_event(nil, "all_unassigned",	"dialog_pause_input", 150),
	}
	Dialog_pause_input_block = false
end

function dialog_pause_hide()
	local d = Dialog_box
	vint_set_property(d.handles["paused"], "visible", false)
	vint_set_property(d.handles["partner_paused"], "visible", false)
	vint_set_property(d.handles["paused_background"], "visible", false)
	if Dialog_pause_input_subs == 0 then
		return
	end

	-- Pause Not Active [nclok1405]
	Sui_paused = false

	if Dialog_pause_disconnect_dialog_handle  ~= 0 then
		dialog_box_force_close(Dialog_pause_disconnect_dialog_handle)
		Dialog_pause_disconnect_dialog_handle = 0
	end

	--	Unsubscribe to input
	for idx, val in Dialog_pause_input_subs do
		vint_unsubscribe_to_input_event(val)
	end
	Dialog_pause_input_subs = 0

end

function dialog_ps3_show()
end

function dialog_ps3_hide()
end

function dialog_pause_disconnect(result, action)
	if action ~= DIALOG_ACTION_CLOSE then
		return
	end

	if result == 0 then
		if Dialog_pause_partner_paused or Dialog_pause_allow_disconnect then
			dialog_box_disconnect()
		else
			debug_print("Exiting to Main Menu from Zombie Pause\n")
			pause_menu_quit_game_internal()
		end
	else
		Dialog_pause_input_block = false
	end

	Dialog_pause_disconnect_dialog_handle = 0
end

function dialog_pause_input(target, event, accelleration)
	if Dialog_pause_input_block == true then
		return
	end

	if Dialog_pause_partner_paused == true then
		if event == "map" then
			--Map is the button to exit out of a partner paused situation
			local options = { [0] = "CONTROL_YES", [1] = "CONTROL_NO" }
			Dialog_pause_disconnect_dialog_handle = dialog_box_open("MENU_TITLE_WARNING", "DIALOG_PAUSE_DISCONNECT_PROMPT", options, "dialog_pause_disconnect", 0, DIALOG_PRIORITY_SYSTEM_CRITICAL, true, nil, false, false)
			Dialog_pause_input_block = false
		end
	else
		if event == "map" and Dialog_pause_allow_disconnect == true then
			--Map is the button to exit out of a partner paused situation
			local options = { [0] = "CONTROL_YES", [1] = "CONTROL_NO" }
			Dialog_pause_disconnect_dialog_handle = dialog_box_open("MENU_TITLE_WARNING", "DIALOG_PAUSE_DISCONNECT_PROMPT", options, "dialog_pause_disconnect", 0, DIALOG_PRIORITY_SYSTEM_CRITICAL, true, nil, false, false)
			Dialog_pause_input_block = false
		elseif event == "map" and Dialog_pause_allow_disconnect == false then
			-- Exit to main menu dialog
			local options = { [0] = "CONTROL_YES", [1] = "CONTROL_NO" }
			Dialog_pause_disconnect_dialog_handle = dialog_box_open("CONTROL_QUIT_WITHOUT_SAVING", "PAUSE_MENU_QUIT_TEXT", options, "dialog_pause_disconnect", 0, DIALOG_PRIORITY_SYSTEM_CRITICAL, true, nil, false, false)
			Dialog_pause_input_block = false
		elseif event == "pause" or event == "dpad_down" then
			--Pause is the event in a normal paused situation.
			dialog_pause_unpause()
		end
	end
end



---------------------------
--[[ COOP INVITE MESSAGE ]]
---------------------------
Dialog_box_invite = { }

function dialog_show_coop_invite(player_name)
	audio_play(audio_get_audio_id("SYS_OBJECTIVE_COMPLETE"))
	local values = { [0] = player_name}
	local player_tag = vint_insert_values_in_string("PS3_INVITE_TEXT_CONFIRM", values)
	vint_set_property(Dialog_box.handles.player_invited_you_text, "text_tag", player_tag)
	vint_set_property(Dialog_box.handles.player_invited_you, "visible", true)
	lua_play_anim(Dialog_box.handles.coop_invite_fade_out, 0)
	local tween_h = vint_object_find("coop_invite_fade_3", Dialog_box.handles.coop_invite_fade_out)
	vint_set_property(tween_h, "end_event", "dialog_hide_coop_invite")
	Dialog_box_invite.pause_pressed = false

	--	Subscribe to the input
	local subscription_priority = 100

	Dialog_box_invite.input_subs = {
		vint_subscribe_to_input_event(nil, "pause",				"dialog_box_invite_input", subscription_priority),
	}

end

function dialog_box_invite_input(target, event, accelleration)
	if event == "pause" then
		Dialog_box_invite.pause_pressed = true
		dialog_hide_coop_invite()
		dialog_coop_invite_start_pressed()
	end
end

function dialog_hide_coop_invite()
	if Dialog_box_invite.input_subs ~= nil then
		--	Unsubscribe to input
		for idx, val in Dialog_box_invite.input_subs do
			vint_unsubscribe_to_input_event(val)
		end
		Dialog_box_invite.input_subs = nil
	end

	if Dialog_box_invite.pause_pressed ~= true then
		dialog_coop_invite_timeout()
	end

	vint_set_property(Dialog_box.handles.player_invited_you, "visible", false)
end
