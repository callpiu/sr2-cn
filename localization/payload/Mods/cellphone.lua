-- cellphone.lua: Cellphone in the pause menu
-- Fast Cellphone [nclok1405]

allcheatflag = 0

Cellphone_audio = {
	[0] =					audio_get_audio_id("SYS_CELL_0"),
	[1] = 				audio_get_audio_id("SYS_CELL_1"),
	[2] = 				audio_get_audio_id("SYS_CELL_2"),
	[3] = 				audio_get_audio_id("SYS_CELL_3"),
	[4] =					audio_get_audio_id("SYS_CELL_4"),
	[5] = 				audio_get_audio_id("SYS_CELL_5"),
	[6] = 				audio_get_audio_id("SYS_CELL_6"),
	[7] = 				audio_get_audio_id("SYS_CELL_7"),
	[8] = 				audio_get_audio_id("SYS_CELL_8"),
	[9] =					audio_get_audio_id("SYS_CELL_9"),
	["pound"] =			audio_get_audio_id("SYS_CELL_POUND"),
	["star"]  = 		audio_get_audio_id("SYS_CELL_STAR"),
	["bootup"]  =	 	audio_get_audio_id("SYS_CELL_BOOTUP"),
	["cheat"] = 		audio_get_audio_id("SYS_CELL_MENU_CHEAT"),
	["data_entry"] = 	audio_get_audio_id("SYS_CELL_SELECT"),
	["nav"] = 			audio_get_audio_id("SYS_CELL_UD"),
	["nav_back"] = 	audio_get_audio_id("SYS_CELL_BACK"),
}

-- Available phone services [nclok1405]
CELLPHONE_USABLE_SERVICES = {
	"CELL_EMERGENCY",	-- 911
	"CELL_JULIUS",	-- Dex
	"TAXI_CAB_1",	-- Big Willy's
	"CELL_COMPANY_OF_GYROS",
	"CELL_FRECKLE",
	"CELL_FIRE_DEPARTMENT",
	"CELL_HAZMAT",
	"CELL_POLICE",
	"CELL_PIMPS",
	"CELL_SHIP_IT",
}

CELLPHONE_SUBSCRIPTION_DEPTH = 1000

CELLPHONE_ITEM_TYPE_MAIN = 0

Cellphone = {
	handles = {}
}

Cellphone_phonebook_thread = -1
Cellphone_nav_blocked = 0
Cellphone_phonebook_anim_clones = {}
Cellphone_phonebook_anim_clones.anim_count = 0
Cellphone_tween_h = 0
Cellphone_intro_sound_thread = -1
Cellphone_intro_sound_instance = -1

Cellphone_previous_cheat_menu = {}	-- Previously shown cheat menu [nclok1405]
Cellphone_previous_cheat_category = 0	-- Previously shown cheat category number [nclok1405]

Cellphone_show_only_usable_services = true	-- Only display usable phone contacts [nclok1405]

-- Unicode Strings [nclok1405]
String_cheat_restore_pc_desc = vint_insert_values_in_string("{0}", {[0] = "CHEAT_CHARACTER_RESTORE_DESC"})	-- "Changes your player character back to normal."
String_cheat_npc_morph_desc = vint_insert_values_in_string("{0}", {[0] = "CHEAT_CHARACTER_DESC"})	-- "Changes your player character to this character."

function cellphone_end_in()
	vint_object_destroy(Cellphone_tween_h)
	vint_set_property(Menu_option_labels_inactive.frame, "visible", false)
end

function cellphone_init()
	-- Before mission 4 make homies icon black [nclok1405]
	if (Sui_missions_completed < 4) then
		Cellphone_menu_main[0].silhouette = true
	end

	peg_load("ui_cellphone")
	allcheatflag = 0

	Cellphone_nav_blocked = 1
	Cellphone.cur_idx = 0
	Cellphone.subheader_active = false
	Cellphone.initialized = false

	Cellphone.loaded_peg = -1 		--Flag for loading pegs.
	Cellphone.number_called = ""	--Current number in use or last used, could be a name or formatted number
	Cellphone.cheat_selected_idx = 0 	--Last cheat that was selected.
	Cellphone.cheat_selected_desc = 0 	--Last cheat that was selected.

	--Find Objects
	Cellphone_menu_main.handles.grp = vint_object_find("main_grp")
	Cellphone_menu_main.handles.main_item = vint_object_find("main_item", Cellphone_menu_main.handles.grp)
	Cellphone.handles.book_grp = vint_object_find("book_grp")
	Cellphone.handles.sub_header = vint_object_find("sub_header")
	Cellphone.handles.sub_header_text = vint_object_find("sub_head_text", Cellphone.handles.sub_header)

	--Dial Objects
	Cellphone_menu_dial.handles.grp = vint_object_find("dial_grp")
	Cellphone_menu_dial.handles.dial_number = vint_object_find("dial_number_text", Cellphone_menu_dial.handles.grp)
	vint_set_property(Cellphone_menu_dial.handles.grp, "visible", false)

	--Call Objects
	Cellphone_menu_call.handles.grp = vint_object_find("call_grp")
	Cellphone.handles.calling_grp = vint_object_find("calling_grp", Cellphone_menu_call.handles.grp )
	Cellphone.handles.speaking_grp = vint_object_find("speaking_grp", Cellphone_menu_call.handles.grp )
	Cellphone.handles.call_dots = vint_object_find("dots", Cellphone_menu_call.handles.grp )
	Cellphone.handles.call_number_1 = vint_object_find("call_number_text", Cellphone_menu_call.handles.grp )
	Cellphone.handles.call_number_2 = vint_object_find("calling_text", Cellphone.handles.speaking_grp )
	Cellphone.handles.call_text = vint_object_find("calling_text", Cellphone.handles.calling_grp )

	--Cheat Objects
	Cellphone_menu_cheat_activate.handles.grp = vint_object_find("cheat_activated_grp")
	Cellphone_menu_cheat_added.handles.grp = vint_object_find("cheat_added_grp")

	--Cheat Added Objects
	Cellphone.handles.cheat_added_title = vint_object_find("cheat_added_title", Cellphone_menu_cheat_added.handles.grp)
	Cellphone.handles.cheat_added_desc = vint_object_find("cheat_description_text", Cellphone_menu_cheat_added.handles.grp)

	--Cheat activated objects
	Cellphone.handles.cheat_activated_state = vint_object_find("activated_text")
	Cellphone.handles.cheat_activated_desc = vint_object_find("cheat_desc_text")
	Cellphone.handles.cheat_activated_title = vint_object_find("cheat_title_text")

	--Animations
	--Background Animation Program
	cellphone_bg_anim_init()

	--Bootup anims
	Cellphone.handles.intro_anim = vint_object_find("intro_anim")
	Cellphone.handles.main_menu_intro_anim = vint_object_find("main_menu_intro_anim")
	Cellphone.handles.main_menu_item_twn = vint_object_find("main_item_alpha_twn_1", Cellphone.handles.main_menu_intro_anim )
	Cellphone.handles.main_menu_pulse_anim = vint_object_find("main_item_pulse_anim_1")

	vint_set_property(Cellphone.handles.intro_anim, "is_paused", true)
	vint_set_property(Cellphone.handles.main_menu_intro_anim, "is_paused", true)
	vint_set_property(Cellphone.handles.main_menu_pulse_anim, "is_paused", true)

	--Bootup callback twns
	local twn_h = vint_object_find("intro_bg_alpha_twn_2", Cellphone.handles.intro_anim)
	vint_set_property(twn_h, "end_event", "cellphone_menu_main_fade_in")

	--Phone book anims
	Cellphone.handles.book_slider_anim = vint_object_find("book_slider_anim")
	Cellphone.handles.book_slider_tween = vint_object_find("book_slider_anchor_twn", Cellphone.handles.book_slider_anim)
	Cellphone.handles.book_text_select_anim = vint_object_find("book_text_select_anim")
	Cellphone.handles.book_text_deselect_anim = vint_object_find("book_text_deselect_anim")
	Cellphone.handles.book_image_select_anim = vint_object_find("book_image_select_anim")
	Cellphone.handles.book_image_deselect_anim = vint_object_find("book_image_deselect_anim")
	Cellphone.handles.book_item_pulse_anim = vint_object_find("book_item_pulse_anim")

	--Pause Animations
	vint_set_property(Cellphone.handles.book_slider_anim, "is_paused", true)
	vint_set_property(Cellphone.handles.book_text_select_anim, "is_paused", true)
	vint_set_property(Cellphone.handles.book_text_deselect_anim, "is_paused", true)
	vint_set_property(Cellphone.handles.book_image_select_anim, "is_paused", true)
	vint_set_property(Cellphone.handles.book_image_deselect_anim, "is_paused", true)
	vint_set_property(Cellphone.handles.book_item_pulse_anim, "is_paused", true)

	--Calling Animations
	Cellphone.handles.calling_to_speak_anim = vint_object_find("calling_to_speak_anim")
	vint_set_property(Cellphone.handles.calling_to_speak_anim, "is_paused", true)
	Cellphone.handles.calling_dot_anim = vint_object_find("calling_dot_anim")
	vint_set_property(Cellphone.handles.calling_dot_anim, "is_paused", true)
	Cellphone.handles.calling_dot_twn = vint_object_find("dot3_alpha_twn_2")
	vint_set_property(Cellphone.handles.calling_dot_twn, "end_event", "cellphone_call_dot_loop")

	--Callback for looping calling
	local twn_h = vint_object_find("book_item_text_dnscale_twn_1", Cellphone.handles.book_text_deselect_anim)
	vint_set_property(twn_h, "per_frame_event", "cellphone_phonebook_align")
	local twn_h = vint_object_find("book_item_text_upscale_twn_1", Cellphone.handles.book_text_select_anim)
	vint_set_property(twn_h, "end_event", "cellphone_phonebook_nav_end")

	--Dial animations
	Cellphone.handles.dial_selected_anim = vint_object_find("dial_selected")
	Cellphone.handles.dial_selected_twn = vint_object_find("dial_btn_2_alpha_twn_1", Cellphone.handles.dial_selected_anim)

	vint_set_property(Cellphone.handles.book_grp, "visible", false)

	Cellphone.player_cash = 0

	cellphone_clock_set()

	--Initialize all menus
	cellphone_menu_initialize()

	local intro_clip_h = vint_object_find("intro_clip")
	vint_set_property(intro_clip_h, "visible", false) -- true

	--Play Bootup animation
	--lua_play_anim(Cellphone.handles.intro_anim, .5)

	--Play Bootup Sound
	--cell_audio_play_delayed(Cellphone_audio["bootup"], .6)

	--when complete open up Cellphone_menu_main
	cellphone_menu_show(Cellphone_menu_main)
	cellphone_menu_main_item_nav(0,0)

	--Subscribe to player information for cash data
	vint_dataitem_add_subscription("sr2_local_player_status_infrequent", "update", "cellphone_cash_update")

	--Subscribe to input
	cellphone_subscribe_input()

	--Plays Main Menu intro animation directly [nclok1405]
	lua_play_anim(Cellphone.handles.main_menu_intro_anim)
end

function cellphone_subscribe_input()
	local c = Cellphone
	c.input_subs = {
		vint_subscribe_to_input_event(nil, "nav_up",				"cellphone_input_event", 50),
		vint_subscribe_to_input_event(nil, "nav_down",			"cellphone_input_event", 50),
		vint_subscribe_to_input_event(nil, "nav_right",			"cellphone_input_event", 50),
		vint_subscribe_to_input_event(nil, "nav_left",			"cellphone_input_event", 50),
		vint_subscribe_to_input_event(nil, "alt_select",				"cellphone_input_event", 50),	-- Spacebar [nclok1405]
		vint_subscribe_to_input_event(nil, "chat_all",				"cellphone_input_event", 50),	-- Chat All [nclok1405]
		vint_subscribe_to_input_event(nil, "chat_team",				"cellphone_input_event", 50),	-- Chat Team [nclok1405]
		vint_subscribe_to_input_event(nil, "select",				"cellphone_input_event", 50),
		vint_subscribe_to_input_event(nil, "pause",				"cellphone_input_event", 50),
		vint_subscribe_to_input_event(nil, "back",				"cellphone_input_event", 100),
	}
end

function cellphone_desubscribe_input()
	--	Unsubscribe to input
	local c = Cellphone
	for idx, val in c.input_subs do
		vint_unsubscribe_to_input_event(val)
	end
	c.input_subs = nil
end

function cellphone_menu_main_fade_in()
	--Plays Main Menu intro animation
	lua_play_anim(Cellphone.handles.main_menu_intro_anim)
end

function cellphone_menu_show(menu)
	local c = Cellphone

	--Make sure menu inactive is totally hidden
	if c.menu_inactive ~= nil then
		vint_set_property(c.menu_inactive.handles.grp, "alpha", 0)
	end

	c.menu_inactive = c.menu_active
	c.menu_active = menu
	Pause_cellphone_btn_tips.b_button.label = "MENU_BACK"

	if c.menu_active.menu_type == "main" then
		--Unload image peg if its loaded
		if Cellphone.loaded_peg ~= -1 then
			peg_unload(Cellphone.loaded_peg)
			Cellphone.loaded_peg = -1
		end

		--hide subheader
		cellphone_subheader_hide()

		Pause_cellphone_btn_tips.b_button.label = "CONTROL_RESUME"


		if c.menu_active.initialized == nil then
			local phone_h = vint_object_find("cell_phone")
			vint_set_property(phone_h, "visible", true)

			local t1 = Menu_active_anchor_end_x - Menu_inactive.menu_width
			local tween_h = menu_create_tween("cell_phone_custom_transition_in", phone_h, "anchor", 0.15)
			vint_set_property(tween_h, "start_value", t1, Menu_active_anchor_end_y)
			vint_set_property(tween_h, "end_value", Menu_active_anchor_end_x, Menu_active_anchor_end_y)
			vint_set_property(tween_h, "end_event", "cellphone_end_in")

			Cellphone_tween_h = tween_h

			c.cur_idx = c.menu_active.cur_idx
			c.menu_active.initialized = true

			Menu_active.menu_width = element_get_actual_size(phone_h)

			vint_set_property(c.menu_active.handles.grp, "visible", true)
			return
		end

	elseif c.menu_active.menu_type == "homies" or c.menu_active.menu_type == "phonebook"  then
		--Show the subheader
		cellphone_subheader_show(c.menu_active.header_string)

		--Create menu
		cellphone_phonebook_create()
	elseif c.menu_active.menu_type == "dial" then
		cellphone_dial_show()
	elseif c.menu_active.menu_type == "call" then
		cellphone_call_show()
	elseif c.menu_active.menu_type == "cheat_activated" then
		--Only update the header
		cellphone_subheader_hide()
	elseif c.menu_active.menu_type == "cheat_added" then
		--Only update the header
		cellphone_subheader_show(c.menu_active.header_string)
	end

	--Reset control index
	c.cur_idx = c.menu_active.cur_idx

	--Menu Transitions

	--Slide out old menu
	if c.menu_inactive ~= nil then
		vint_set_property(c.menu_inactive.handles.grp, "alpha", 0)
		vint_set_property(c.menu_inactive.handles.grp, "visible", false)
		if c.menu_inactive.cleanup ~= nil then
			c.menu_inactive.cleanup()
		end
	end

	--Then slide in new menu
	vint_set_property(c.menu_active.handles.grp, "visible", true)
	local twn_h = cellphone_create_tween("cleanout", c.menu_active.handles.grp, "alpha", .5)
	vint_set_property(twn_h, "start_value", 0)
	vint_set_property(twn_h, "end_value", 1)

	btn_tips_update()
end

function cell_phone_exit_tween(callback)
	local phone_h = vint_object_find("cell_phone")
	vint_set_property(phone_h, "visible", true)

	local t1 = Menu_active.menu_width - Menu_active_anchor_end_x
	local tween_h = menu_create_tween("cell_phone_custom_transition_out", phone_h, "anchor", 1.5)
	vint_set_property(tween_h, "start_value", t1, Menu_active_anchor_end_y)
	vint_set_property(tween_h, "end_value", 0, Menu_active_anchor_end_y)
	vint_set_property(tween_h, "end_event", callback)

	Cellphone_tween_h = tween_h
end

function cellphone_create_tween(name, target_h, target_prop, duration)
	local tween_h = vint_object_create(name, "tween", vint_object_find("root_animation"))

	vint_set_property(tween_h, "duration", duration)
	vint_set_property(tween_h, "target_handle", target_h)
	vint_set_property(tween_h, "target_property", target_prop)
	vint_set_property(tween_h, "start_time",	vint_get_time_index())
	vint_set_property(tween_h, "is_paused", false)
	vint_set_property(tween_h, "end_event", "cellphone_tween_cleanup")
	return tween_h
end

function cellphone_tween_cleanup(twn_h)
	--Destroy tweens for cellphone fade in
	vint_object_destroy(twn_h)
end

--Input event handler
function cellphone_input_event(target, event, accelleration)

	if get_platform() ~= "PC" then
		--Always handle unpausing
		if event == "pause" then
			pause_menu_exit()
			--vint_document_unload(vint_document_find("cellphone"))
		end
	end

	if event == "back" and Cellphone.initialized == false then
		--Only allow the user to go back if the nav isn't blocked before the cell is initialized
		cellphone_menu_main_back(0)
	end

	local c = Cellphone
	local old_idx = -1

	--Check if nav is blocked
	if cellphone_nav_is_blocked() == true then
		return
	end

	if c.cur_idx == nil then
		--don't handle any events if there is no index
		return
	end
	if event == "nav_up" then
		--Call nav function
		if c.menu_active.on_nav_up ~= nil then
			c.menu_active.on_nav_up(c.cur_idx)
		else
			old_idx = c.cur_idx

			if c.cur_idx == 0 then			--	Wrap around if we have to
				c.cur_idx = c.menu_active.num_items - 1
			else
				c.cur_idx = c.cur_idx - 1	--	Otherwise move it up
			end

			--Store index to menu
			c.menu_active.cur_idx = c.cur_idx
			if c.menu_active.on_nav ~= nil then
				c.menu_active.on_nav(c.cur_idx, old_idx)
			end
		end
	elseif event == "nav_down" then
		if c.menu_active.on_nav_down ~= nil then
			c.menu_active.on_nav_down(c.cur_idx)
		else
			old_idx = c.cur_idx

			if c.cur_idx == c.menu_active.num_items - 1 then			--	Wrap around if we have to
				c.cur_idx = 0
			else
				c.cur_idx = c.cur_idx + 1	--	Otherwise move it up
			end

			--Store index to menu
			c.menu_active.cur_idx = c.cur_idx

			--Call nav function
			if c.menu_active.on_nav ~= nil then
				c.menu_active.on_nav(c.cur_idx, old_idx)
			end
		end
	elseif event == "nav_right" then
		if c.menu_active.on_nav_right ~= nil then
			c.menu_active.on_nav_right(c.cur_idx)
		end
	elseif event == "nav_left" then
		if c.menu_active.on_nav_left ~= nil then
			c.menu_active.on_nav_left(c.cur_idx)
		end
	elseif event == "alt_select" then
		-- Spacebar [nclok1405]
		if c.menu_active.on_alt_select ~= nil then
			c.menu_active.on_alt_select(c.cur_idx)
		end
	elseif event == "chat_all" then
		-- Chat All [nclok1405]
		if c.menu_active.on_chat_all ~= nil then
			c.menu_active.on_chat_all(c.cur_idx)
		end
	elseif event == "chat_team" then
		-- Chat Team [nclok1405]
		if c.menu_active.on_chat_team ~= nil then
			c.menu_active.on_chat_team(c.cur_idx)
		end
	elseif event == "select" then
		if c.menu_active[c.cur_idx].on_select ~= nil then
			--Use menu items control
			c.menu_active[c.cur_idx].on_select(c.cur_idx)
		elseif c.menu_active.on_select ~= nil then
			--Use standard menu select
			c.menu_active.on_select(c.cur_idx)
		end
	elseif event == "back" then
		if c.menu_active.on_back ~= nil then
			--Use standard menu select
			c.menu_active.on_back(c.cur_idx)
		end
	end
end

function cellphone_menu_initialize()

	--Main Menu Init
	local menu_item, menu_item_grp_h, h
	--Get item width and height
	h = vint_object_find("main_border_line", Cellphone_menu_main.handles.main_item)

	--debug_print("vint", "main_border_line \n")

	local item_width, item_height = element_get_actual_size(h)
	local item_x, item_y = vint_get_property(Cellphone_menu_main.handles.main_item, "anchor")
	local item_spacing = 3

	for i = 0, Cellphone_menu_main.num_items - 1 do
		menu_item = Cellphone_menu_main[i]

		if i == 0 then
			menu_item.grp_h = Cellphone_menu_main.handles.main_item
		else
			--clone item
			menu_item.grp_h = vint_object_clone(Cellphone_menu_main.handles.main_item)

			--Clone intro tweens and target and time them
			local twn_h = vint_object_clone(Cellphone.handles.main_menu_item_twn, Cellphone.handles.main_menu_intro_anim)
			vint_set_property(twn_h, "target_handle", menu_item.grp_h)
			local start_offset = 0.166665
			local duration_offset = vint_get_property(twn_h, "duration") / 2
			local start = 0 -- start_offset + i * duration_offset
			vint_set_property(twn_h, "start_time", start)

			if i == Cellphone_menu_main.num_items - 1 then
				--Set Callback on last tween to unblock input
				vint_set_property(twn_h, "end_event", "cellphone_menu_intro_complete")
			end
		end

		--Reposition
		vint_set_property(menu_item.grp_h, "anchor", item_x, item_y + i * (item_height + item_spacing))

		--Change Elements
		h = vint_object_find("main_sel_text", menu_item.grp_h)
		vint_set_property(h, "text_tag", menu_item.label)

		--BMP
		h = vint_object_find("main_sel_icon", menu_item.grp_h)
		vint_set_property(h, "image", menu_item.bmp)

		--bmp_offset_x, bmp_offset_y
		vint_set_property(h, "offset", menu_item.bmp_offset_x, menu_item.bmp_offset_y)

		--Hide elements
		vint_set_property(menu_item.grp_h, "alpha", 0)
	end

	--Pause anim again because clones do not respond to the animation state
	vint_set_property(Cellphone.handles.main_menu_intro_anim, "is_paused", true)

	--Dial Interface
	Cellphone_menu_dial[0] 	= 	{h = vint_object_find("dial_btn_call"), 	btn_type = "call" }
	Cellphone_menu_dial[1] 	= 	{h = vint_object_find("dial_btn_call"), 	btn_type = "call" }
	Cellphone_menu_dial[2] 	= 	{h = vint_object_find("dial_btn_clr"), 	btn_type = "clr" }
	Cellphone_menu_dial[3] 	= 	{h = vint_object_find("dial_btn_1"), 		btn_type = "num", id=1 }
	Cellphone_menu_dial[4] 	= 	{h = vint_object_find("dial_btn_2"), 		btn_type = "num", id=2 }
	Cellphone_menu_dial[5] 	= 	{h = vint_object_find("dial_btn_3"), 		btn_type = "num", id=3 }
	Cellphone_menu_dial[6] 	= 	{h = vint_object_find("dial_btn_4"), 		btn_type = "num", id=4 }
	Cellphone_menu_dial[7] 	= 	{h = vint_object_find("dial_btn_5"), 		btn_type = "num", id=5 }
	Cellphone_menu_dial[8] 	= 	{h = vint_object_find("dial_btn_6"), 		btn_type = "num", id=6 }
	Cellphone_menu_dial[9] 	= 	{h = vint_object_find("dial_btn_7"), 		btn_type = "num", id=7 }
	Cellphone_menu_dial[10] = 	{h = vint_object_find("dial_btn_8"), 		btn_type = "num", id=8 }
	Cellphone_menu_dial[11] = 	{h = vint_object_find("dial_btn_9"), 		btn_type = "num", id=9 }
	Cellphone_menu_dial[12] = 	{h = vint_object_find("dial_btn_star"), 	btn_type = "star", id="*"}
	Cellphone_menu_dial[13] = 	{h = vint_object_find("dial_btn_oper"), 	btn_type = "num", id=0 }
	Cellphone_menu_dial[14] = 	{h = vint_object_find("dial_btn_pound"), 	btn_type = "pound", id="#"}
	Cellphone_menu_dial.num_items = 15
	Cellphone_menu_dial.num_cols = 3
	Cellphone_menu_dial.num_rows = 5
end

function cellphone_menu_main_item_nav(idx, old_idx)

	local menu_active = Cellphone.menu_active
	local grp_h, h

	if old_idx ~= idx then
		--unhighlight old
		grp_h = menu_active[old_idx].grp_h

		--change text highlight
		h = vint_object_find("main_sel_text", grp_h)
		vint_set_property(h, "alpha", .5)

		--bmp
		h = vint_object_find("main_sel_icon", grp_h)
		if menu_active[old_idx].silhouette then
			vint_set_property(h, "tint", 0, 0, 0)	-- Silhouette [nclok1405]
		else
			vint_set_property(h, "tint", .64, .64, .64)
		end

		--border
		h = vint_object_find("main_border", grp_h)
		vint_set_property(h, "alpha", .2)
	end

	--highlight new
	grp_h = menu_active[idx].grp_h

	--change text highlight
	h = vint_object_find("main_sel_text", grp_h)
	vint_set_property(h, "alpha", 1)

	--bmp
	h = vint_object_find("main_sel_icon", grp_h)
	if menu_active[idx].silhouette then
		vint_set_property(h, "tint", 0, 0, 0)	-- Silhouette [nclok1405]
	else
		vint_set_property(h, "tint", 1, 1, 1)
	end

	--border
	h = vint_object_find("main_border", grp_h)
	vint_set_property(h, "alpha", .8)

	vint_set_property(Cellphone.handles.main_menu_pulse_anim, "target_handle", grp_h)
	lua_play_anim(Cellphone.handles.main_menu_pulse_anim, 0)
	audio_play(Cellphone_audio["nav"])
end

--Event to load the submenu based on the idx of the menu item
function cellphone_menu_main_item_select(idx)
	Cellphone_show_only_usable_services = true

	--Always set current index of submenu to zero here
	Cellphone.menu_active[idx].sub_menu.cur_idx = 0
	cellphone_menu_show(Cellphone.menu_active[idx].sub_menu)

	--Play Data Entry sound
	audio_play(Cellphone_audio["data_entry"])
end

-- Spacebar on main cellphone menu [nclok1405]
function cellphone_menu_main_item_alt_select(idx)
	-- Phone Book
	if idx == 2 then
		Cellphone_show_only_usable_services = false	-- Show all phone contacts
		Cellphone.menu_active[idx].sub_menu.cur_idx = 0
		cellphone_menu_show(Cellphone.menu_active[idx].sub_menu)
		audio_play(Cellphone_audio["data_entry"])
	end
end

function cellphone_menu_main_back(idx)
	--Exit the pause menu
	vint_document_unload(vint_document_find("cellphone"))
	pause_menu_exit()
end

function cellphone_menu_intro_complete()
	Cellphone.initialized = true
	cellphone_nav_block(false)
end

--Numbers to cull out
CELLPHONE_MAX_PHONEBOOK_NUMBERS = 11	-- Increased from 10 to prevent graphical glitches [nclok1405]


-------------------------------------
-- Phone Book
-------------------------------------
function cellphone_phonebook_create()
	if cellphone_nav_is_blocked() == true then
		cellphone_nav_block(false)
	end

	local c = Cellphone
	local menu_data = Cellphone.menu_active

	--Create a clone of the menu
	menu_data.handles.grp = vint_object_clone(Cellphone.handles.book_grp)
	menu_data.handles.scrollbar = vint_object_find("scrollbar_bmp", menu_data.handles.grp)

	--Initialize menu if the menu is suspposed to be dynamic
	if	menu_data.dynamic_menu == true then
		menu_data.num_items = 0
		if menu_data.book_type == 3 then
			--Populating Cheats
			local category_index = Cellphone.number_called
			if Cellphone.number_called == 5 then
				category_index = 0	-- Request "Player Ability" for NPC Morph [nclok1405]
			end
			vint_dataresponder_request("pause_menu_populate", "cellphone_phonebook_populate_cheats", 0, 16, menu_data.book_type, category_index)
		elseif menu_data.book_type == 4 then
			--debug_print("vint", "populate_garage\n")
			--Populate Garage List
			vint_dataresponder_request("pause_menu_populate", "cellphone_phonebook_populate_garage", 0, 16, 4)
		elseif menu_data.book_type == 1 then
			--Populate Services list [nclok1405]
			vint_dataresponder_request("pause_menu_populate", "cellphone_phonebook_populate_usable_services", 0, 16, menu_data.book_type)
		else
			--Populate Homie list
			vint_dataresponder_request("pause_menu_populate", "cellphone_phonebook_populate", 0, 16, menu_data.book_type)
		end

		--Always reset to index of zero if the menu is dynamically generated
		menu_data.cur_idx = 0
		local slider_h = vint_object_find("book_slider", menu_data.handles.grp)
		vint_set_property(slider_h, "anchor", 0, 0)
	end
	--debug_print("vint", "menu_data.num_items: " .. menu_data.num_items .. "\n")

	--Load phone images
	menu_data.image_peg = -1	-- Disabled. I could not make the faster menus work with the homie images. [nclok1405]
--[[
	if menu_data.image_peg ~= -1 then
		--Unload last image in case it was loaded
		if Cellphone.loaded_peg ~= -1 then
			peg_unload(Cellphone.loaded_peg)
			Cellphone.loaded_peg = -1
		end

		--Load new peg
		peg_load(menu_data.image_peg)
		Cellphone.loaded_peg = menu_data.image_peg
	end
--]]

	local menu_item_h = vint_object_find("book_item", menu_data.handles.grp)
	vint_set_property(menu_item_h, "visible", false)
	local h, x, y, width, height
	local menu_item, old_h, text_h, bmp_h, text_x, text_y
	local item_spacing = 0

	local contact_text_tag = ""

	--Now create each item from the menu data
	for i = 0, menu_data.num_items - 1 do
		if (i > CELLPHONE_MAX_PHONEBOOK_NUMBERS) then
			--Too many for the screen
			menu_data[i].grp_h = -1
		else
			cellphone_phonebook_add_to_list(i, false)
		end
	end

	--highlight cur idx and make the cur index selectable
	local menu_item = menu_data[menu_data.cur_idx]
	local text_h = vint_object_find("book_item_text", menu_item.grp_h)
	local bmp_h = vint_object_find("book_image", menu_item.grp_h)
	width, height = vint_get_property(bmp_h, "source_se")
	vint_set_property(text_h, "tint", .529, .725, .815)

	local text_string = vint_get_property(text_h, "text_tag")

--[[
	if menu_data.image_peg ~= -1 then
		height = 98
		vint_set_property(bmp_h, "source_se", width, height)
		vint_set_property(bmp_h, "alpha", 1)
		vint_set_property(text_h, "anchor", 0, height)
	end
--]]

	--Align all items
	cellphone_phonebook_align()
	cellphone_phonebook_update_layout()
end



function cellphone_phonebook_nav(idx, old_idx)
	local menu_data = Cellphone.menu_active
	local grp_h, h

	if menu_data.num_items <= 1 then
		--No Items or one item in list in list reset the index
		menu_data.cur_idx = old_idx
		Cellphone.cur_idx = old_idx
		return
	end

	if menu_data.num_items >= 11 then
		-- Disallow wrap-around only when there's a scrolling [nclok1405]
		local nav_distance = abs(idx - old_idx)
		if nav_distance > 1 then
			--reset the index
			menu_data.cur_idx = old_idx
			Cellphone.cur_idx = old_idx
			return
		end
	end

	--Block input
	--cellphone_nav_block(true)

	local h, x, y, width, height
	local menu_item, old_h, text_h
	local item_spacing = 0

	local temp

	--Highlight New
	menu_item = menu_data[idx]

	--Retarget and Play selected animation
	text_h = vint_object_find("book_item_text", menu_item.grp_h)

	--resize the tween targets if necessary
	local text_string = vint_get_property(text_h, "text_tag")

	-- Highlight the newly selected option [nclok1405]
	vint_set_property(text_h, "alpha", 1.0)
	vint_set_property(text_h, "tint", .529, .725, .815)

	--Colaps the previous item
	if old_idx ~= idx then

		--Colaps old
		menu_item = menu_data[old_idx]

		--Reset alpha stat of text from pulsing animation
		local text_h = vint_object_find("book_item_text", menu_item.grp_h)
		vint_set_property(text_h, "tint", 0.1294, 0.1765, 0.204)	-- Set previous option's tint [nclok1405]
		vint_set_property(text_h, "alpha", 1)

		--resize the tween targets if necessary
		local text_string = vint_get_property(text_h, "text_tag")

		--Align all items [nclok1405]
		cellphone_phonebook_align()

		-- Do scroll
		cellphone_phonebook_update_layout()
	end

	audio_play(Cellphone_audio["nav"])
end

function cellphone_phonebook_update_layout()
	local menu_data = Cellphone.menu_active

	if menu_data.num_items == 0 then
		--No items so there is nothing to update and there is no scrollbar
		vint_set_property(Cellphone.menu_active.handles.scrollbar, "visible", false)
		return
	end

	--Current Index
	local idx = menu_data.cur_idx
	local line_height = 0
	local text_h = vint_object_find("book_item_text", menu_data[idx].grp_h)

	local text_string = vint_get_property(text_h, "text_tag")
	local temp, line_height = element_get_actual_size(text_h)
	line_height = line_height

	-- Slide menu
	local CELLPHONE_BOOK_TOP_LOCK
	local CELLPHONE_BOOK_BOTTOM_LOCK
	local DISPLAY_MAX_ITEMS

	--Does the book use images or not?
	if menu_data.image_peg == -1 then
		--No image defaults
		CELLPHONE_BOOK_TOP_LOCK = 4
		CELLPHONE_BOOK_BOTTOM_LOCK = 6
		DISPLAY_MAX_ITEMS = 10.5
	else
		--With Image Defaults
		CELLPHONE_BOOK_TOP_LOCK = 2
		CELLPHONE_BOOK_BOTTOM_LOCK = 5
		DISPLAY_MAX_ITEMS = 7
	end

	local bottom_lock = menu_data.num_items - CELLPHONE_BOOK_BOTTOM_LOCK
	local bottom_lock_locker = menu_data.num_items - CELLPHONE_BOOK_BOTTOM_LOCK - CELLPHONE_BOOK_TOP_LOCK

	local SCROLLBAR_MAX_HEIGHT = 304
	local SCROLLBAR_MIN_HEIGHT = 100

	local max_items = menu_data.num_items - CELLPHONE_BOOK_BOTTOM_LOCK

	-- Scroll Bar Height
	local max_vis = (menu_data.num_items) / DISPLAY_MAX_ITEMS 	--	Get the total items and divide it by the max that can be seen
	local height = SCROLLBAR_MAX_HEIGHT / max_vis 					-- The height is the area of the scroll bar divided by the ratio of max items to visible items

	local first_item_to_scroll = idx - CELLPHONE_BOOK_TOP_LOCK	-- Account for the lock at the top
	local scrolling_item = first_item_to_scroll

	-- Make sure everything lines up correctly.
	if first_item_to_scroll < 0 then
		scrolling_item = 0
	elseif idx > max_items then
		scrolling_item = max_items - CELLPHONE_BOOK_TOP_LOCK
	end

	-- Index of the highlighted item * The area height (minus the bar height, to account for the space it takes) / The amount of actual items the bar scrolls on
	local position = (scrolling_item * (SCROLLBAR_MAX_HEIGHT - height)) / (max_items - CELLPHONE_BOOK_TOP_LOCK)

	local scrollbar_is_visible

	if menu_data.num_items >= DISPLAY_MAX_ITEMS then
		scrollbar_is_visible = true
	else
		scrollbar_is_visible = false
	end

	-- Put it in the oven for baby and me.
	--Update scrollbar
	local scrollbar_h = Cellphone.menu_active.handles.scrollbar
	element_set_actual_size(scrollbar_h, 8, height)
	vint_set_property(scrollbar_h, "anchor", 0, position)
	vint_set_property(scrollbar_h, "visible", scrollbar_is_visible)

	local slide_flag = false
	local slide_y = 0
	if idx < CELLPHONE_BOOK_TOP_LOCK then
		--Lock to top
		slide_y = 0
	elseif idx > bottom_lock then
		--Lock to bottom
		slide_y = bottom_lock_locker * - line_height
	else
		--Nav normally
		slide_y = (idx -  CELLPHONE_BOOK_TOP_LOCK) * - line_height
		slide_flag = true
	end

	if menu_data.num_items < DISPLAY_MAX_ITEMS then
		--Do not scroll if the items are less than what can be displayed on the screen
		return
	end

	-- Don't do the rest when no scroll actually happens [nclok1405]
	if not slide_flag then
		return
	end

	--TODO: Occlude/show items
	local item_min = idx - CELLPHONE_MAX_PHONEBOOK_NUMBERS
	local item_max = idx + CELLPHONE_MAX_PHONEBOOK_NUMBERS
	if item_min < 0 then
		item_min = 0
	end
	if item_max > menu_data.num_items - 1 then
		item_max = menu_data.num_items - 1
	end

	--Occlude items
	for i = 0, menu_data.num_items - 1 do
		if i < item_min or i > item_max then

			if menu_data[i].grp_h ~= -1 then
				--Remove if it exists
				cellphone_phonebook_remove_from_list(i)
			end
		end
	end

	--Make sure all the items are visible
	for i = 0, menu_data.num_items - 1 do
		if i >= item_min and i <= item_max then
			if menu_data[i].grp_h == -1 then
				--Add item if it doesn't exist
				cellphone_phonebook_add_to_list(i, true)
			end
		end
	end

	--Slide menu
	local slide_box = vint_object_find("book_slider", menu_data.handles.grp)
	local x, y = vint_get_property(slide_box, "anchor")
	vint_set_property(Cellphone.handles.book_slider_tween, "start_value", x, y)
	vint_set_property(Cellphone.handles.book_slider_tween, "end_value", 0, slide_y)
	vint_set_property(Cellphone.handles.book_slider_tween, "target_handle", slide_box)
	lua_play_anim(Cellphone.handles.book_slider_anim, 0)
end

function cellphone_phonebook_nav_end()
	-- Unblock input
	cellphone_nav_block(false)
end

function cellphone_phonebook_align()
	local menu_data = Cellphone.menu_active

	if menu_data.num_items == 0 then
		--No items so there is nothing to align
		return
	end

	local h, x, y, width, height
	local menu_item, old_h, text_h, text_x, text_y

	for i = 0, menu_data.num_items - 1 do
		menu_item = menu_data[i]
		if old_h ~= nil and menu_item.grp_h ~= -1 and old_h ~= -1 then
			--Get Previous text size
			text_h = vint_object_find("book_item_text", old_h)
			text_x, text_y = vint_get_property(text_h, "anchor")
			local text_string = vint_get_property(text_h, "text_tag")
			if text_string ~= nil then
				width, height = element_get_actual_size(text_h)
				x, y = vint_get_property(old_h, "anchor")

				y = y + text_y + height
				vint_set_property(menu_item.grp_h, "anchor", x, y)
			end
		end
		old_h = menu_item.grp_h
	end
	old_h = nil
end

-- Add a new option to the list
-- isnew: false if the option is added right at the beginning, true if the option came later by scrolling
function cellphone_phonebook_add_to_list(idx, isnew)
		if (isnew == nil) then
			isnew = false
		end

		local menu_data = Cellphone.menu_active

		local menu_item_h = vint_object_find("book_item", menu_data.handles.grp)
		local h, x, y, width, height
		local menu_item, old_h, text_h, bmp_h, text_x, text_y

		local item_spacing = 0
		menu_item = menu_data[idx]

		local contact_text_tag = ""

		menu_item.grp_h = vint_object_clone(menu_item_h)
		vint_set_property(menu_item.grp_h , "visible", true)

		--Is the item on the top or bottom of the list?
		if idx == 0 then
			-- this is the first item in the list
			vint_set_property(menu_item.grp_h, "anchor", 0, 0)
		elseif menu_data[idx - 1].grp_h == -1 and idx + 1 ~= menu_data.num_items then
			--This is on the top but not the first item and not the last item
			old_h = menu_data[idx + 1].grp_h
			text_h = vint_object_find("book_item_text", old_h)
			text_x, text_y = vint_get_property(text_h, "anchor")
			local text_string = vint_get_property(text_h, "text_tag")
			--debug_print("vint", "text10: " .. var_to_string(text_string)  .. "\n")
			if text_string ~= nil then
				width, height = element_get_actual_size(text_h)
				x, y = vint_get_property(old_h, "anchor")
				y = y - text_y - height - item_spacing
				vint_set_property(menu_item.grp_h, "anchor", x, y)
			end

		end
		--Does it even matter where the item is? haha but we need to initialize it


		--Change text on elements
		text_h = vint_object_find("book_item_text", menu_item.grp_h)
		if menu_item.is_active == true then
			local values = { [0] = menu_item.contact_name}
			contact_text_tag = vint_insert_values_in_string("CELL_CHEAT_OPTION_ACTIVE", values)
		else
			contact_text_tag  = menu_item.contact_name
		end
		vint_set_property(text_h, "text_tag", contact_text_tag)

		--Change bitmaps if we use an image peg
		menu_data.image_peg = -1 -- Disabled. [nclok1405]
--[[
		if menu_data.image_peg ~= -1 then
			bmp_h = vint_object_find("book_image", menu_item.grp_h)
			vint_set_property(bmp_h, "image_crc", menu_item.bmp_crc)
		end
--]]
		--Need to initialize all the elements
		--i.e. make them all one line

		--Image size
		h = vint_object_find("book_image", menu_item.grp_h)
		width, height = vint_get_property(h, "source_se")
		height = 0
		vint_set_property(h, "source_se", width, height)
		vint_set_property(h, "alpha", 0)
		x, y = vint_get_property(text_h, "anchor")
		y = 0
		vint_set_property(text_h, "anchor", x, y)

		local text_string = vint_get_property(text_h, "text_tag")

		if not isnew then
			vint_set_property(text_h, "tint", 0.1294, 0.1765, 0.204)
		else
			--vint_set_property(text_h, "tint", 1, 0, 0)	-- Make late-coming options red for debugging graphical glitches... [nclok1405]
			vint_set_property(text_h, "tint", 0.1294, 0.1765, 0.204)
		end
		vint_set_property(text_h, "alpha", 1)
end

function cellphone_phonebook_remove_from_list(idx)
	local menu_data = Cellphone.menu_active
	local menu_item = menu_data[idx]
	vint_object_destroy(menu_item.grp_h)
	menu_item.grp_h = -1
end

function cellphone_phonebook_call()
	local menu_data = Cellphone.menu_active

	if menu_data.num_items == 0 then
		--not allowed to call if nobody to talk too...
		return
	end

	local index = menu_data[menu_data.cur_idx].index

	--Set strings for call
	Cellphone.number_called = menu_data[menu_data.cur_idx].contact_name

	cellphone_menu_show(Cellphone_menu_call)

	--Place call to C and arrange callbacks
	cellphone_dial(menu_data.book_type, index, "cellphone_dial_connection_cb", "cellphone_call_hangup")

	--Play Data Entry sound
	audio_play(Cellphone_audio["data_entry"])
end


function cellphone_phonebook_cleanup()
	--Remove all objects associated with the  current phonebook
	--This is a pretty shameful hack because we only support one instance of the phonebook...

	--Pause All animations
	vint_set_property(Cellphone.handles.book_slider_anim, "is_paused", true)
	vint_set_property(Cellphone.handles.book_text_select_anim, "is_paused", true)
	vint_set_property(Cellphone.handles.book_text_deselect_anim, "is_paused", true)
	vint_set_property(Cellphone.handles.book_image_select_anim, "is_paused", true)
	vint_set_property(Cellphone.handles.book_image_deselect_anim, "is_paused", true)
	vint_object_destroy(Cellphone.menu_inactive.handles.grp)

	if cellphone_nav_is_blocked() == true then
		cellphone_nav_block(false)
	end

	if Cellphone_phonebook_thread ~= -1 then
		thread_kill(Cellphone_phonebook_thread)
		Cellphone_phonebook_thread = -1
	end
end

-- Returns true if the specified telephone contact is a "usable service" that spawns a vehicle [nclok1405]
function cellphone_is_usable_service(name)
	for k, v in pairs(CELLPHONE_USABLE_SERVICES) do
		if sui_compare_string(v, name) then
			return true
		end
	end
	return false
end

-- Populate service list [nclok1405]
function cellphone_phonebook_populate_usable_services(contact_name, bmp_crc, description, index)
	local menu_data = Cellphone.menu_active
	local idx = menu_data.num_items

	-- If only showing usable phone contacts...
	if Cellphone_show_only_usable_services then
		-- ...and this contact is NOT one of those usable services, reject!
		if not cellphone_is_usable_service(contact_name) then
			return
		end
	end

	menu_data[idx] = {contact_name = contact_name, bmp_crc = bmp_crc, description = description, index = index}
	menu_data.num_items = menu_data.num_items + 1
end

function cellphone_phonebook_populate(contact_name, bmp_crc, description, index)
	local menu_data = Cellphone.menu_active
	local idx = menu_data.num_items

	-- Localize homie names and add an icon [nclok1405]
	local head_image = "ui_hud_recruit_coop"
	local homie_name = contact_name

	if sui_compare_string(contact_name, "Tobias") then
		head_image = "ui_hud_recruit_drug_tobias"
		homie_name = "UNL_SS03_TOBIAS"
	elseif sui_compare_string(contact_name, "Johnny Gat") then
		head_image = "ui_hud_recruit_story_jgat"
		homie_name = "UNL_RONIN_VICTORY6"
	elseif sui_compare_string(contact_name, "Pierce") then
		head_image = "ui_hud_recruit_story_pierce"
		homie_name = "UNL_BRO_VICTORY6"
	elseif sui_compare_string(contact_name, "Shaundi") then
		head_image = "ui_hud_recruit_story_shaundi"
		homie_name = "UNL_SAMEDI_VICTORY6"
	elseif sui_compare_string(contact_name, "Jane Valderama") then
		head_image = "ui_hud_recruit_homie_jane"
		homie_name = "UNL_MUGGING2"
	elseif sui_compare_string(contact_name, "Troy") then
		head_image = "ui_hud_recruit_story_troy"
		homie_name = "UNL_FIGHTCLUB_2_WHOLE"
	elseif sui_compare_string(contact_name, "PAUSE_MENU_DRIVEUP_HOMIE") then
		head_image = "ui_hud_recruit_homie_lee"
	elseif sui_compare_string(contact_name, "Aisha") then
		head_image = "ui_hud_recruit_ho_hispanic"
	elseif sui_compare_string(contact_name, "Carlos") then
		head_image = "ui_hud_recruit_story_carlos"
	elseif sui_compare_string(contact_name, "Luz") then
		head_image = "ui_hud_recruit_misc_luz"
	elseif sui_compare_string(contact_name, "Mr Wong") then
		head_image = "ui_hud_recruit_misc_bouncer"
	elseif sui_compare_string(contact_name, "PAUSE_MENU_ZOMBIE_HOMIE") then
		head_image = "ui_hud_recruit_story_carlos_z"
	elseif sui_compare_string(contact_name, "Donnie's Delivery Service") then
		head_image = "ui_hud_recruit_story_donnie"
	elseif sui_compare_string(contact_name, "Maero") then
		head_image = "ui_hud_recruit_story_maero"
	elseif sui_compare_string(contact_name, "Jessica") then
		head_image = "ui_hud_recruit_story_jessica"
	elseif sui_compare_string(contact_name, "Julius") then
		head_image = "ui_hud_recruit_story_julius"
	elseif sui_compare_string(contact_name, "Carlos (Jail Outfit)") then
		head_image = "ui_hud_recruit_story_carlos"
	elseif sui_compare_string(contact_name, "Richie") then
		head_image = "ui_hud_recruit_misc_richie"
	elseif sui_compare_string(contact_name, "Shaundi (Repair Outfit)") then
		head_image = "ui_hud_recruit_story_shaundi"
	elseif sui_compare_string(contact_name, "Laura") then
		head_image = "ui_hud_recruit_homie_laura"
	end

	if head_image ~= "" and homie_name ~= "" then
		contact_name = vint_insert_values_in_string("[format][color:full_bright][scale:0.5][image:"..head_image.."][/format]{0}", {[0] = homie_name})
	end

	menu_data[idx] = {contact_name = contact_name, bmp_crc = bmp_crc, description = description, index = index}
	menu_data.num_items = menu_data.num_items + 1
end

function cellphone_phonebook_populate_cheats(contact_name, description, is_active, index, doesnt_flag_cheat)
	-- Reject/Accept NPC Morph cheats based on the selected category and description. [nclok1405]
	-- Yeah I know this is crazy. The game gives UNICODE strings to us that cannot be compared directly!
	-- Thankfully, "vint_insert_values_in_string" let us create an arbitrary Unicode string that can actually be compared.
	local desc = vint_insert_values_in_string("{0}", {[0] = description})	-- Cheat Description

	if ((desc == String_cheat_restore_pc_desc) or (desc == String_cheat_npc_morph_desc)) and (Cellphone.number_called == 0) then
		return	-- On Player Ability, reject any morph cheats
	elseif (desc ~= String_cheat_restore_pc_desc) and (desc ~= String_cheat_npc_morph_desc) and (Cellphone.number_called == 5) then
		return	-- On Character, reject anything but morph cheats
	end

	--Populate Cheat
	local menu_data = Cellphone.menu_active
	local idx = menu_data.num_items

	menu_data[idx] = {index = index, contact_name = contact_name, description = description, is_active = is_active, doesnt_flag_cheat = doesnt_flag_cheat}
	menu_data.num_items = menu_data.num_items + 1
end

function cellphone_phonebook_populate_garage(index, vehicle_name, repair_cost)
	--Populate Garage List
	local menu_data = Cellphone.menu_active
	local idx = menu_data.num_items
	menu_data[idx] = {index = index, contact_name = vehicle_name, repair_cost = repair_cost}
	menu_data.num_items = menu_data.num_items + 1
end

function cellphone_garage_get_car()
	local menu_data = Cellphone.menu_active

	if menu_data.num_items == 0 then
		--not cars available if no cars available too...
		return
	end

	--Play Audio
	audio_play(Cellphone_audio["data_entry"])

	--Called when selecting an option from the garage
	local repair_cost = menu_data[menu_data.cur_idx].repair_cost

	--Check if player has enough cash
	if Cellphone.player_cash < repair_cost then
		--Not enough cash dialog
		dialog_box_message("CELL_VEHICLE_DIALOG_NO_CASH_HEADER","CELL_VEHICLE_DIALOG_NO_CASH_BODY")
		return
	end

	--Repair and Deliver if player has enough cash.
	if repair_cost == 0 then
		--Deliver if repair price = 0
		cellphone_choose_vehicle(menu_data[menu_data.cur_idx].index)
		cellphone_menu_show(Cellphone_menu_main)
		return
	end

	--Car needs repairs, prepare localized dialog and display

	if repair_cost ~= 0 then
		local values = {[0] = repair_cost}
		local dialog_repairs_body = vint_insert_values_in_string("CELL_VEHICLE_DIALOG_REPAIRS_BODY", values)
		dialog_box_confirmation("CELL_VEHICLE_DIALOG_REPAIRS_HEADER", dialog_repairs_body, "cellphone_garage_get_car_dialog_cb")
	else
		local index = Cellphone.menu_active[Cellphone.menu_active.cur_idx].index
		cellphone_choose_vehicle(index)
		cellphone_menu_show(Cellphone_menu_main)
	end
end

function cellphone_garage_get_car_dialog_cb(result, action)
	if action ~= DIALOG_ACTION_CLOSE then
		return
	end
	if result == 0 then
		local index = Cellphone.menu_active[Cellphone.menu_active.cur_idx].index
		cellphone_choose_vehicle(index)
	end

	cellphone_menu_show(Cellphone_menu_main)
end

function cellphone_garage_get_car_dialog()
end

-------------------------------------
--Dial
-------------------------------------
function cellphone_dial_show()
	local menu_data = Cellphone.menu_active

	--Show Subheader
	 cellphone_subheader_show(menu_data.header_string)
	--Show controls

	--Initialize Control
	menu_data.dial_number = {}
	menu_data.dial_number_dirty_digits = 0
	menu_data.dial_number_digits = 0
	menu_data.dial_number_string = ""
	menu_data.cur_idx = 0
	menu_data.cur_row = 0
	menu_data.cur_col = 0

	--Clear out dial part
	vint_set_property(Cellphone_menu_dial.handles.dial_number, "text_tag", "")

	--dim out all the buttons
	for i=0, menu_data.num_items -1 do
		cellphone_dial_btn_dim(menu_data[i].h)
	end
	cellphone_dial_btn_bright(menu_data[0].h)
end

-- Dial button handler [nclok1405]
function cellphone_dial_button_handler(btn_pressed)
	local menu_data = Cellphone.menu_active

	--What button was pressed
	local update_number = true

	if btn_pressed.btn_type == "call" then
		--Return if there is no number to call
		if menu_data.dial_number_digits == 0 then
			return
		end

		--Store the dial string to global
		Cellphone.number_called = menu_data.dial_number_string

		--Probably need to store some data somewhere for the call part
		cellphone_menu_show(Cellphone_menu_call)

		local dial_string = ""
		for i=0, menu_data.dial_number_digits - 1 do
			dial_string = dial_string .. menu_data.dial_number[i]
		end

		if dial_string == "#1337" then
			allcheatflag = 1
			--debug_print("I heard you like cheats, so I put some cheats in your cheats")


			-- Player Ability and World Cheats
			for i = 1, 20 do
				if i == 4 or i == 10 or i == 13 or i == 14 or i == 17 then  --leaving out 4 so it's next to 35 (add gang notoriety) later
					--debug_print("There is no "..i.." code. Do nothing")
				else
					local countercheat = ("#"..i)
					cellphone_dial_number(countercheat, "cellphone_dial_connection_cb", "cellphone_call_hangup")
					--debug_print("added cheat "..countercheat)
				end
			end

			cellphone_dial_number("#36", "cellphone_dial_connection_cb", "cellphone_call_hangup") --out of order so that the notoriety ones are grouped together
			--debug_print("added cheat #36")

			cellphone_dial_number("#4", "cellphone_dial_connection_cb", "cellphone_call_hangup")
			--debug_print("added cheat #4")
			cellphone_dial_number("#35", "cellphone_dial_connection_cb", "cellphone_call_hangup")
			--debug_print("added cheat #35")
			cellphone_dial_number("#50", "cellphone_dial_connection_cb", "cellphone_call_hangup")
			--debug_print("added cheat #50")
			cellphone_dial_number("#51", "cellphone_dial_connection_cb", "cellphone_call_hangup")
			--debug_print("added cheat #51")

			for i = 200, 202 do
				local countercheat = ("#"..i)
				cellphone_dial_number(countercheat, "cellphone_dial_connection_cb", "cellphone_call_hangup")
				--debug_print("added cheat "..countercheat)
			end

			cellphone_dial_number("#2274666399", "cellphone_dial_connection_cb", "cellphone_call_hangup")
			--debug_print("added cheat #2274666399")
			--debug_print("Player and World Cheats Added!")

			-- PC Morph Cheats
			for i = 75, 182 do
				local countercheat = ("#"..i)
				cellphone_dial_number(countercheat, "cellphone_dial_connection_cb", "cellphone_call_hangup")
				--debug_print("added cheat "..countercheat)
			end
			--debug_print("PC Morph Cheats Added!")

			-- Time Cheats
				cellphone_dial_number("#1200", "cellphone_dial_connection_cb", "cellphone_call_hangup")
				--debug_print("added cheat #1200")

				cellphone_dial_number("#2400", "cellphone_dial_connection_cb", "cellphone_call_hangup")
				--debug_print("added cheat #2400")

				cellphone_dial_number("#2500", "cellphone_dial_connection_cb", "cellphone_call_hangup")
				--debug_print("added cheat #2500")
				--debug_print("Time Cheats Added!")


			-- Weather Cheats
			for i = 78664, 78670 do
				if i == 78667 then
					--debug_print("There is no 78667 code. Do nothing")
				else
					local countercheat = ("#"..i)
					cellphone_dial_number(countercheat, "cellphone_dial_connection_cb", "cellphone_call_hangup")
					--debug_print("added cheat "..countercheat)
				end
			end
			--last weather cheat
			cellphone_dial_number("#666", "cellphone_dial_connection_cb", "cellphone_call_hangup")
			--debug_print("added cheat #666")
			--debug_print("Weather Cheats Added!")


			--Weapon Cheats
			cellphone_dial_number("#923", "cellphone_dial_connection_cb", "cellphone_call_hangup")
			--debug_print("added cheat #923")
			cellphone_dial_number("#927", "cellphone_dial_connection_cb", "cellphone_call_hangup")
			--debug_print("added cheat #927")
			cellphone_dial_number("#928", "cellphone_dial_connection_cb", "cellphone_call_hangup")
			--debug_print("added cheat #928")
			cellphone_dial_number("#929", "cellphone_dial_connection_cb", "cellphone_call_hangup")
			--debug_print("added cheat #929")
			cellphone_dial_number("#931", "cellphone_dial_connection_cb", "cellphone_call_hangup")
			--debug_print("added cheat #931")
			cellphone_dial_number("#934", "cellphone_dial_connection_cb", "cellphone_call_hangup")
			--debug_print("added cheat #934")
			cellphone_dial_number("#938", "cellphone_dial_connection_cb", "cellphone_call_hangup")
			--debug_print("added cheat #938")
			cellphone_dial_number("#939", "cellphone_dial_connection_cb", "cellphone_call_hangup")
			--debug_print("added cheat #939")

			for i = 944, 951 do
				if i == 948 then
					--debug_print("There is no 948 code. Do nothing")
				else
					local countercheat = ("#"..i)
					cellphone_dial_number(countercheat, "cellphone_dial_connection_cb", "cellphone_call_hangup")
					--debug_print("added cheat "..countercheat)
				end
			end

			cellphone_dial_number("#958", "cellphone_dial_connection_cb", "cellphone_call_hangup")
			--debug_print("added cheat #958")
			cellphone_dial_number("#969", "cellphone_dial_connection_cb", "cellphone_call_hangup")
			--debug_print("added cheat #969")

			for i = 55550, 55559 do
				local countercheat = ("#"..i)
				cellphone_dial_number(countercheat, "cellphone_dial_connection_cb", "cellphone_call_hangup")
				--debug_print("added cheat "..countercheat)
			end
			--debug_print("Weapon Cheats Added!")

			--Vehicle Cheats
			cellphone_dial_number("#1056", "cellphone_dial_connection_cb", "cellphone_call_hangup")
			--debug_print("added cheat #1056")
			cellphone_dial_number("#4976", "cellphone_dial_connection_cb", "cellphone_call_hangup")
			--debug_print("added cheat #4976")
			cellphone_dial_number("#728237", "cellphone_dial_connection_cb", "cellphone_call_hangup")
			--debug_print("added cheat #728237")
			allcheatflag = 2 --last cheat coming up so we want to set this flag so the final dialog box appears with sound
			cellphone_dial_number("#7266837", "cellphone_dial_connection_cb", "cellphone_call_hangup")
			--debug_print("added cheat #7266837")
			--debug_print("Vehicle Cheats Added!")

		else

			--Place call to C and arrange callbacks
			cellphone_dial_number(dial_string, "cellphone_dial_connection_cb", "cellphone_call_hangup")

			update_number = false

			--play data entry sounds
			audio_play(Cellphone_audio["data_entry"])

		end -- end new if then block for #1337 number to add all cheats


	elseif btn_pressed.btn_type  == "clr" then
		--Check if number was dirty
		local num = menu_data.dial_number[menu_data.dial_number_digits - 1]
		if num == "#" or num == "*" then
			menu_data.dial_number_dirty_digits = menu_data.dial_number_dirty_digits -1
		end

		menu_data.dial_number_digits = menu_data.dial_number_digits - 1
		if menu_data.dial_number_digits <= 0 then
			menu_data.dial_number_digits = 0
		end

		--play clear sounds
		audio_play(Cellphone_audio["data_entry"])
	else
		if menu_data.dial_number_digits == menu_data.dial_number_max_digits then
			--No more key pressing!
			return
		end
		--Standard Key was pressed

		--Dirty digit was pressed
		if btn_pressed.btn_type == "pound" or btn_pressed.btn_type == "star" then
			menu_data.dial_number_dirty_digits = menu_data.dial_number_dirty_digits + 1
			--Play off key sound.
			audio_play(Cellphone_audio[btn_pressed.btn_type])
		else
			--Play key sound.
			audio_play(Cellphone_audio[btn_pressed.id])
		end



		menu_data.dial_number[menu_data.dial_number_digits] = btn_pressed.id
		menu_data.dial_number_digits = menu_data.dial_number_digits + 1
	end

	--Update the number in the display window
	if update_number == true then
		local do_formatting = true
		menu_data.dial_number_string = ""
		for i=0, menu_data.dial_number_digits - 1 do

			if menu_data.dial_number_digits > 10 or menu_data.dial_number_dirty_digits > 0 then
				--No Formatting
			elseif menu_data.dial_number_digits >= 8 then
				--Area Code Style String
				if i == 0 then
					menu_data.dial_number_string = "("
				end
				if i == 3 then
					menu_data.dial_number_string = menu_data.dial_number_string .. ") "
				end
				if i == 6 then
					menu_data.dial_number_string = menu_data.dial_number_string .. "-"
				end
			else
				--Local Number String
				if i==3 or i==7 then
					menu_data.dial_number_string = menu_data.dial_number_string .. "-"
				end
			end
			menu_data.dial_number_string = menu_data.dial_number_string .. menu_data.dial_number[i]
		end
		--update Number
		vint_set_property(Cellphone_menu_dial.handles.dial_number, "text_tag", menu_data.dial_number_string)
	end
end

-- Spacebar on dialer screen [nclok1405]
function cellphone_dial_alt_select()
	cellphone_dial_button_handler(Cellphone_menu_dial[0])
end

-- Button input on dialer screen
function cellphone_dial_select()
	local menu_data = Cellphone.menu_active

	--What button was pressed
	local btn_pressed = menu_data[menu_data.cur_idx]

	cellphone_dial_button_handler(btn_pressed)
end

function cellphone_dial_nav_left()
	local menu_data = Cellphone.menu_active
	local col = menu_data.cur_col

	col = col - 1
	if col < 0 then
		col = menu_data.num_cols - 1
	end

	--menu_grid_update_highlighted(menu_data, col, menu_data.cur_row)
	cellphone_dial_update_highlighted(col, menu_data.cur_row)
	audio_play(Cellphone_audio["nav"])
end

function cellphone_dial_nav_right()
	local menu_data = Cellphone.menu_active
	local col = menu_data.cur_col

	col = col + 1
	if col > menu_data.num_cols - 1 then
		col = 0
	end
	cellphone_dial_update_highlighted(col, menu_data.cur_row)
	audio_play(Cellphone_audio["nav"])
end

function cellphone_dial_nav_up()
	local menu_data = Cellphone.menu_active
	local row = menu_data.cur_row

	row = row - 1
	if row < 0 then
		row = menu_data.num_rows - 1
	end

	--menu_grid_update_swatches(menu_data, row)
	cellphone_dial_update_highlighted(menu_data.cur_col, row)
	audio_play(Cellphone_audio["nav"])
end

function cellphone_dial_nav_down()
	local menu_data = Cellphone.menu_active
	local row = menu_data.cur_row

	row = row + 1
	if row > menu_data.num_rows - 1 then
		row = 0
	end

	--	menu_grid_update_swatches(menu_data, row)
	cellphone_dial_update_highlighted(menu_data.cur_col, row)
	audio_play(Cellphone_audio["nav"])
end

function cellphone_dial_update_highlighted(new_col, new_row)
	local menu_data = Cellphone.menu_active
	local new_idx = new_row * menu_data.num_cols + new_col
	local old_idx = menu_data.cur_row * menu_data.num_cols + menu_data.cur_col
	if new_idx >= menu_data.num_items then
		return
	end

	local idx = new_row * menu_data.num_cols + new_col

	--Skip extra call button
	if (old_idx ~= 0 and idx == 1) then
		idx = 0
		new_row = 0
		new_col = 0
	elseif (old_idx == 0 and idx == 1) then
		idx = 2
		new_row = 0
		new_col = 2
	end

	--highlight new and darken old
	cellphone_dial_btn_bright(menu_data[idx].h)
	cellphone_dial_btn_dim(menu_data[old_idx].h)


	--Update global menu data
	menu_data.cur_row = new_row
	menu_data.cur_col = new_col
	menu_data.cur_idx = idx
end

function cellphone_dial_btn_dim(item_h)
	--Set button state to dim
	local h
	h = vint_object_find("selected", item_h)
	vint_set_property(h, "alpha", 0)

	h = vint_object_find("unselected", item_h)
	vint_set_property(h, "alpha", 1)

	h = vint_object_find("number", item_h)
	if h ~= 0 then
		vint_set_property(h, "tint", 0.1529, 0.3216, 0.424)

	end

	h = vint_object_find("extra_text", item_h)
	if h ~= 0 then
		vint_set_property(h, "tint", 0.1529, 0.3216, 0.424)
	end

	vint_set_property(item_h, "alpha", .5)
end

function cellphone_dial_btn_bright(item_h)
	--Set button state to highlight
	local h
	h = vint_object_find("selected", item_h)
	vint_set_property(h, "alpha", 1)

	h = vint_object_find("unselected", item_h)
	vint_set_property(h, "alpha", 0)

	h = vint_object_find("number", item_h)
	if h ~= 0 then
		vint_set_property(h, "tint", 0.3608, 0.6353, 0.764)
	end

	h = vint_object_find("extra_text", item_h)
	if h ~= 0 then
		vint_set_property(h, "tint", 0.3608, 0.6353, 0.764)
	end

	vint_set_property(Cellphone.handles.dial_selected_twn, "target_handle", item_h)
	lua_play_anim(Cellphone.handles.dial_selected, 0)
end

function cellphone_dial_connection_cb(success, name, description)

	if success == -1 then
		--wrong number
		--use invalid number screen
		cellphone_call_connected(Cellphone.number_called)
	elseif success == 0 then
		--cheat unlocked
		--description = cheat description
		cellphone_cheat_added_show(name, description)
	elseif success == 1 then
		--Connection has been made, string of store name to display is stored in name
		cellphone_call_connected(name)
	elseif success == 2 then
		--Show garage Menu
		cellphone_menu_show(Cellphone_menu_garage)
	end
end

function cellphone_dial_exit()
end

-------------------------------------
--Calling
-------------------------------------
function cellphone_call_show()

	--Set subheader to no title
	cellphone_subheader_show("")

	--Set Text fields to the number dialed
	vint_set_property(Cellphone.handles.call_number_1, "text_tag", Cellphone.number_called)
	vint_set_property(Cellphone.handles.call_number_2, "text_tag", Cellphone.number_called)

	--Resize text fields if they are too large
	vint_set_property(Cellphone.handles.call_number_2, "scale", 1, 1)
	local width, height = element_get_actual_size(Cellphone.handles.call_number_2)
	if width > 245 then
		local scale = 245/width
		vint_set_property(Cellphone.handles.call_number_2, "scale", scale, scale)
	end

	vint_set_property(Cellphone.handles.calling_grp, "alpha", 1)
	vint_set_property(Cellphone.handles.speaking_grp, "alpha", 0)

	--move dots
	local x, y = vint_get_property(Cellphone.handles.call_text, "anchor")
	local text_string = vint_get_property(Cellphone.handles.call_text, "text_tag")
	--debug_print("vint", "text5: " .. var_to_string(text_string)  .. "\n")

	if text_string ~= nil then
		local width, height = element_get_actual_size(Cellphone.handles.call_text)
		x = x + width + 2
		vint_set_property(Cellphone.handles.call_dots, "anchor", x,y)
	end

	vint_set_property(vint_object_find("dot1", Cellphone.handles.call_dots), "alpha", 0)
	vint_set_property(vint_object_find("dot2", Cellphone.handles.call_dots), "alpha", 0)
	vint_set_property(vint_object_find("dot3", Cellphone.handles.call_dots), "alpha", 0)

	--Play dot animations
	lua_play_anim(Cellphone.handles.calling_dot_anim, 0)
end

function cellphone_call_connected()
	--Calling to speak animation
	lua_play_anim(Cellphone.handles.calling_to_speak_anim, 0)

	--Stop dot animation
	vint_set_property(Cellphone.handles.calling_dot_anim, "is_paused", false)
end
function cellphone_call_hangup()
	cellphone_end_call()
	cellphone_menu_show(Cellphone_menu_main)
end

function cellphone_call_dot_loop()
	lua_play_anim(Cellphone.handles.calling_dot_anim, 0)
end

-------------------------------------
--Cheats
-------------------------------------
function cellphone_cheat_cat_select()
	local idx = Cellphone.menu_active.cur_idx
	Cellphone.number_called = idx
	Cellphone_menu_cheat_spec.header_string = Cellphone_menu_cheat_cat[idx].contact_name
	cellphone_menu_show(Cellphone_menu_cheat_spec)

	--Play Data Entry sound
	audio_play(Cellphone_audio["data_entry"])
end

function cellphone_cheat_spec_back()
	audio_play(Cellphone_audio["nav_back"])
	cellphone_menu_show(Cellphone_menu_cheat_cat)
end

-- Chat All key on cheat list (set shortcut) [nclok1405]
function cellphone_cheat_spec_chat_all()
	local menu_data = Cellphone.menu_active
	local menu_item = menu_data[menu_data.cur_idx]
	if menu_data.num_items == 0 then
		return
	end

	Sui_cheat_shortcut_chat_all = menu_item.index

	local insert_values = {[0] = "MULTI_CHAT_ALL", [1] = menu_item.contact_name}

	dialog_box_message("SUI_CHEAT_SHORTCUT_TITLE", vint_insert_values_in_string("SUI_CHEAT_SHORTCUT_SET_CHAT", insert_values))
end

-- Chat Team key on cheat list (set shortcut) [nclok1405]
function cellphone_cheat_spec_chat_team()
	local menu_data = Cellphone.menu_active
	local menu_item = menu_data[menu_data.cur_idx]
	if menu_data.num_items == 0 then
		return
	end

	Sui_cheat_shortcut_chat_team = menu_item.index

	local insert_values = {[0] = "MULTI_CHAT_TEAM", [1] = menu_item.contact_name}

	dialog_box_message("SUI_CHEAT_SHORTCUT_TITLE", vint_insert_values_in_string("SUI_CHEAT_SHORTCUT_SET_CHAT_TEAM", insert_values))
end

function cellphone_cheat_spec_select()
	--Do the dialog box question...
	local menu_data = Cellphone.menu_active

	local menu_item = menu_data[menu_data.cur_idx]

	if menu_data.num_items == 0 then
		--No calls allowed if no items are in the list
		return
	end

	-- Remember the cheat category [nclok1405]
	Cellphone_previous_cheat_category = Cellphone.number_called

	--Store cheat data into globals for following screen
	Cellphone.cheat_selected_idx = menu_item.index
	Cellphone.cheat_selected_desc = menu_item.description
	Cellphone.number_called = menu_item.contact_name

	--Insert values
	local values = {[0] = menu_item.contact_name, [1] = menu_item.description}

	--Determine wheather we de activate or activeate
	local heading
	local body_tag
	if menu_item.is_active == false then
		heading = "CELL_CHEAT_ACTIVIATE_DIALOG_HEADER"
		body_tag = vint_insert_values_in_string("CELL_CHEAT_ACTIVIATE_DIALOG_BODY", values)

		-- Low Gravity Warning [nclok1405]
		if sui_compare_string(menu_item.contact_name, "LOW_GRAVITY") then
			heading = "MENU_TITLE_WARNING"
			body_tag = "SUI_LOW_GRAVITY_WARNING"
		end

	else
		heading = "CELL_CHEAT_DEACTIVATE_DIALOG_HEADER"
		body_tag = vint_insert_values_in_string("CELL_CHEAT_DEACTIVATE_DIALOG_BODY", values)
	end

	if sui_compare_string(Cellphone.cheat_selected_desc, String_cheat_npc_morph_desc) then
		-- Instantly unpause the game on NPC transform cheats (avoid black screen) [nclok1405]
		audio_play(Cellphone_audio["cheat"])
		cellphone_activate_cheat(Cellphone.cheat_selected_idx)
		cellphone_menu_main_back(0)
	elseif menu_item.doesnt_flag_cheat == true then
		--No acheivement warnings... activate/deactivate cheat
		Cellphone_previous_cheat_menu = Cellphone.menu_active
		local is_active = cellphone_activate_cheat(Cellphone.cheat_selected_idx)
		cellphone_cheat_activated_show(is_active)
	else
		--Acheivement warnings for 360 and PC
		dialog_box_confirmation(heading, body_tag, "cellphone_cheat_activation_cb")
	end
end

function cellphone_cheat_activation_cb(result, action)
	if action ~= DIALOG_ACTION_CLOSE then
		return
	end

	if result == 0 then
		Cellphone_previous_cheat_menu = Cellphone.menu_active

		--Activate cheat
		local is_active = cellphone_activate_cheat(Cellphone.cheat_selected_idx)

		--Now display the next menu
		cellphone_cheat_activated_show(is_active)
	else
		--do nothing
	end
end

function cellphone_cheat_added_show(name, description)

	if allcheatflag == 1 then
		--debug_print("all cheats initialized don't play audio") ---part of a mass of cheat adds

	else

		if allcheatflag == 2 then -- the final cheat was added let's display new unlock text.
			name = "ALL CHEATS ADDED!"
			description = "I heard you like cheats so I put some cheats in your cheats."
		end

		--Added cheat...
		local desc_add_tag = "CELL_CHEAT_ACTIVATE_INSTRUCTIONS"

		local values = { [0] = description, [1] = "CELL_CHEAT_ACTIVATE_INSTRUCTIONS" }
		local desc_tag = vint_insert_values_in_string("{0}\n \n{1}", values)

		vint_set_property(Cellphone.handles.cheat_added_title, "text_tag", name)
		vint_set_property(Cellphone.handles.cheat_added_desc, "text_tag", desc_tag)
		cellphone_menu_show(Cellphone_menu_cheat_added)

		local text_string = vint_get_property(Cellphone.handles.cheat_added_title, "text_tag")
		--debug_print("vint", "text6: " .. var_to_string(text_string)  .. "\n")

		local gap = 0

		if text_string ~= nil then
			local title_w, title_h = element_get_actual_size(Cellphone.handles.cheat_added_title)
			if title_h > 40 then
				gap = 60
			end
		end

		local desc_x, desc_y = vint_get_property(Cellphone.handles.cheat_added_desc, "anchor")
		vint_set_property(Cellphone.handles.cheat_added_desc, "anchor", desc_x, desc_y + gap)

		--Play Added Sound
		audio_play(Cellphone_audio["cheat"])

	end
end

function cellphone_cheat_activated_show(is_active)
	--Update cheat information
	--Set activation type based on whether we are activating the cheat is active or not

	--Set Cheat type
	vint_set_property(Cellphone.handles.cheat_activated_title, "text_tag", Cellphone.number_called)

	local text_string = vint_get_property(Cellphone.handles.cheat_activated_title, "text_tag")
	--debug_print("vint", "text7: " .. var_to_string(text_string)  .. "\n")

	local gap = 0

	if text_string ~= nil then
		local title_w, title_h = element_get_actual_size(Cellphone.handles.cheat_activated_title)

		if title_h > 40 then
			gap = 60
		end
	end

	local state_x, state_y = vint_get_property(Cellphone.handles.cheat_activated_state, "anchor")
	local desc_x, desc_y = vint_get_property(Cellphone.handles.cheat_activated_desc, "anchor")

	vint_set_property(Cellphone.handles.cheat_activated_state, "anchor", state_x, state_y + gap)
	vint_set_property(Cellphone.handles.cheat_activated_desc, "anchor", desc_x, desc_y + gap)

	--Set text based on active state
	if is_active == true then
		vint_set_property(Cellphone.handles.cheat_activated_state, "text_tag", "CELL_HEADER_ACTIVATED")
		vint_set_property(Cellphone.handles.cheat_activated_desc, "text_tag", Cellphone.cheat_selected_desc)
	else
		vint_set_property(Cellphone.handles.cheat_activated_state, "text_tag", "CELL_HEADER_DEACTIVATED")
		vint_set_property(Cellphone.handles.cheat_activated_desc, "text_tag", "")
	end

	cellphone_menu_show(Cellphone_menu_cheat_activate)

	--Play Activate sound
	audio_play(Cellphone_audio["cheat"])
end

-- Exit from Cheat Activated screen [nclok1405]
function cellphone_cheat_activated_exit()
	audio_play(Cellphone_audio["nav_back"])
	Cellphone.number_called = Cellphone_previous_cheat_category
	cellphone_menu_show(Cellphone_previous_cheat_menu)
end

-------------------------------------
--SUBHEADER
-------------------------------------
function cellphone_subheader_show(header_string)

	if header_string == false then
		return
	end

	--Replace subheader string
	vint_set_property(Cellphone.handles.sub_header_text, "text_tag", header_string)

	if Cellphone.subheader_active == false then
		--Animate in
		vint_set_property(Cellphone.handles.sub_header, "alpha", 1)
		Cellphone.subheader_active = true
	end
end

function cellphone_subheader_hide()
	--Animate Out
	vint_set_property(Cellphone.handles.sub_header, "alpha", 0)

	Cellphone.subheader_active = false
end



-------------------------------------
--CLEANUP
-------------------------------------
function cellphone_cleanup()
	cellphone_desubscribe_input()

	peg_unload("ui_cellphone")
	--peg_unload("ui_cell_homies")

	--Unload our loaded peg in case we still have one loaded
	if Cellphone.loaded_peg ~= -1 then
		peg_unload(Cellphone.loaded_peg)
		Cellphone.loaded_peg = -1
	end

	--kill intro audio
	if Cellphone_intro_sound_thread ~= -1 then
		thread_kill(Cellphone_intro_sound_thread)
	end

	if Cellphone_intro_sound_instance ~= -1 then
		audio_fade_out(Cellphone_intro_sound_instance, .25)
	end
end

function cellphone_menu_sub_exit()
	audio_play(Cellphone_audio["nav_back"])
	cellphone_menu_show(Cellphone_menu_main)
end

-------------------------------------
--UTILITY
-------------------------------------
function cellphone_format_number(phone_number)
	local phone_string = ""
	local phone_temp = phone_number
	if phone_string >= 10000000000 then
		phone_number = phone_number
	else
		local p = 0
		local p_string = ""
		if phone_temp >= 10000000 then
			p = floor(phone_temp / 10000000)
			phone_string = "(" .. phone_string .. p .. ") "
			phone_temp = phone_temp - p * 10000000
		end
		if phone_temp >= 10000 then
			p = floor(phone_temp / 10000)
			phone_string = phone_string .. p .. "-"
			phone_temp = phone_temp - p * 10000
		end
		if cash_temp >= 0 then
			phone_string = phone_string .. phone_temp
		end
	end
	return phone_string
end

--#######################################
--Clock
--#######################################
function cellphone_clock_set()

	local hour, minute = cellphone_get_time()
	local pm = false
	if hour > 12 then
		hour = hour - 12
		pm = true
	end

	if hour == 12 then
		pm = true
	end

	local minute_str

	if minute < 10 then
		minute_str = "0" .. minute
	else
		minute_str = minute
	end

	local clock_time = hour .. ":" .. minute_str

	if pm == true then
		clock_time = clock_time .. " PM"
	else
		clock_time = clock_time .. " AM"
	end

	local time_h = vint_object_find("time_text")
	vint_set_property(time_h, "text_tag", clock_time)
end



--#######################################
--Block navigation
--#######################################
function cellphone_nav_block(block)
	if block == true then
		Cellphone_nav_blocked = Cellphone_nav_blocked + 1
	else
		Cellphone_nav_blocked = Cellphone_nav_blocked - 1
	end
end

function cellphone_nav_is_blocked()
	return Cellphone_nav_blocked > 0
end

--#######################################
--Background Animations
--#######################################

function cellphone_bg_anim_init()
	--hide bg anim peices
	local h
	h = vint_object_find("bg_p_1")
	vint_set_property(h, "alpha", 0)
	h = vint_object_find("bg_p_2")
	vint_set_property(h, "alpha", 0)
	h = vint_object_find("bg_p_3")
	vint_set_property(h, "alpha", 0)
	h = vint_object_find("bg_p_4")
	vint_set_property(h, "alpha", 0)
	h = vint_object_find("bg_p_5")
	vint_set_property(h, "alpha", 0)
	h = vint_object_find("bg_s_1")
	vint_set_property(h, "alpha", 0)
	h = vint_object_find("bg_s_2")
	vint_set_property(h, "alpha", 0)
	h = vint_object_find("bg_s_3")
	vint_set_property(h, "alpha", 0)
	h = vint_object_find("bg_s_4")
	vint_set_property(h, "alpha", 0)
	h = vint_object_find("bg_s_5")
	vint_set_property(h, "alpha", 0)

	--Anims
	Cellphone.bg_num_anims = 10
	local p_1_anim = vint_object_find("bg_p_1_anim_1")
	local p_2_anim = vint_object_find("bg_p_2_anim_1")
	local p_3_anim = vint_object_find("bg_p_3_anim_1")
	local p_4_anim = vint_object_find("bg_p_4_anim_1")
	local p_5_anim = vint_object_find("bg_p_5_anim_1")
	local s_1_anim = vint_object_find("bg_s_1_anim_1")
	local s_2_anim = vint_object_find("bg_s_2_anim_1")
	local s_3_anim = vint_object_find("bg_s_3_anim_1")
	local s_4_anim = vint_object_find("bg_s_4_anim_1")
	local s_5_anim = vint_object_find("bg_s_5_anim_1")

	--last tweens
	local p_1_twn = vint_object_find("bg_p_1_alpha_twn_2")
	local p_2_twn = vint_object_find("bg_p_2_alpha_twn_2")
	local p_3_twn = vint_object_find("bg_p_3_alpha_twn_2")
	local p_4_twn = vint_object_find("bg_p_4_alpha_twn_2")
	local p_5_twn = vint_object_find("bg_p_5_alpha_twn_2")
	local s_1_twn = vint_object_find("bg_s_1_alpha_twn_2")
	local s_2_twn = vint_object_find("bg_s_2_alpha_twn_2")
	local s_3_twn = vint_object_find("bg_s_3_alpha_twn_2")
	local s_4_twn = vint_object_find("bg_s_4_alpha_twn_2")
	local s_5_twn = vint_object_find("bg_s_5_alpha_twn_2")

	Cellphone.bg_anims = {
		[p_1_twn] = p_1_anim,
		[p_2_twn] = p_2_anim,
		[p_3_twn] = p_3_anim,
		[p_4_twn] = p_4_anim,
		[p_5_twn] = p_5_anim,
		[s_1_twn] = s_1_anim,
		[s_2_twn] = s_2_anim,
		[s_3_twn] = s_3_anim,
		[s_4_twn] = s_4_anim,
		[s_5_twn] = s_5_anim,
	}

	Cellphone.bg_anims_indexed = {
		[0] = p_1_anim,
		[1] = p_2_anim,
		[2] = p_3_anim,
		[3] = p_4_anim,
		[4] = p_5_anim,
		[5] = s_1_anim,
		[6] = s_2_anim,
		[7] = s_3_anim,
		[8] = s_4_anim,
		[9] = s_5_anim,
	}

	Cellphone.bg_anims_active = {}
	--Pause all Anims
	for idx, val in Cellphone.bg_anims_indexed do
		vint_set_property(val, "is_paused", true)
	end

	--Set tween callbacks
	for idx, val in Cellphone.bg_anims do
		vint_set_property(idx, "end_event", "cellphone_bg_anim_twn_end")
	end

	cellphone_bg_anim_random_play(0)
	cellphone_bg_anim_random_play(4)
	cellphone_bg_anim_random_play(8)
	cellphone_bg_anim_random_play(12)
	cellphone_bg_anim_random_play(16)
end

function cellphone_bg_anim_random_play(time_offset)
	local random_anim_idx, anim_h
	local anim_not_playing = false

	--Select random animation until we find one that isn't already playing
	local prevent_infinite = 0
	while true do
		random_anim_idx = rand_int(0, Cellphone.bg_num_anims - 1)
		anim_h = Cellphone.bg_anims_indexed[random_anim_idx]
		if Cellphone.bg_anims_active[anim_h] == nil then
			break
		end
		prevent_infinite = prevent_infinite + 1
		if prevent_infinite == Cellphone.bg_num_anims then
			break
		end
	end

	--Play animation
	lua_play_anim(anim_h, time_offset)

	--Set animation to active
	Cellphone.bg_anims_active[anim_h] = true
end

function cellphone_bg_anim_twn_end(twn_h, event)
	local anim_h = Cellphone.bg_anims[twn_h]

	--Remove animation from playing animation list
	Cellphone.bg_anims_active[anim_h] = nil
	--Select another animation to play
	cellphone_bg_anim_random_play(0)
end

--#######################################
--Player Cash Data
--#######################################
function cellphone_cash_update(di_h)
	local cash = vint_dataitem_get(di_h)
	Cellphone.player_cash = floor(cash)
end

--#######################################
--Special Cell Audio functions
--#######################################
function cell_audio_play_delayed(sound_id, offset)
	Cellphone_intro_sound_thread = thread_new("audio_play_delayed_thread", sound_id, offset)
end

function audio_play_delayed_thread(sound_id, offset)
	delay(offset)
	Cellphone_intro_sound_instance = audio_play(sound_id)
	Cellphone_intro_sound_thread = -1
end


--#######################################
--Button Tips
--#######################################

--#######################################
--MENUS
--#######################################
Cellphone_menu_dial = {
	menu_type="dial",
	header_string = "",
	dial_number = {},
	dial_number_max_digits = 18,
	dial_number_digits = 0,
	dial_number_dirty_digits = 0,
	dial_number_string = "",
	num_items = 0,
	handles = {},
	cur_idx = 0,
	cur_row = 0,
	cur_col = 0,
	num_cols = 3,
	num_rows = 5,
	num_items = 0,
	on_alt_select = cellphone_dial_alt_select,	-- Spacebar [nclok1405]
	on_select = cellphone_dial_select,
	on_nav_up = cellphone_dial_nav_up,
	on_nav_down = cellphone_dial_nav_down,
	on_nav_left = cellphone_dial_nav_left,
	on_nav_right = cellphone_dial_nav_right,
	on_back = cellphone_menu_sub_exit,
}

Cellphone_menu_call = {
	menu_type = "call",
	header_string = "",
	calling_string = "",
	handles = {},
	on_select = cellphone_call_hangup,
	on_back = cellphone_call_hangup,
	cur_idx = 0,
	num_items = 1,
	[0] = {dummy_item = -1}
}


Cellphone_menu_homies = {
	menu_type = "phonebook",
	header_string = "CELL_OPTION_HOMIES",
	dynamic_menu = true,
	book_type = 0,
	num_items = 3,
	cur_idx = 0,
	handles = {},
--	image_peg = "ui_cell_homies",
	image_peg = -1,
	on_select = cellphone_phonebook_call,
	on_nav = cellphone_phonebook_nav,
	on_back = cellphone_menu_sub_exit,
	cleanup = cellphone_phonebook_cleanup,
	[0] = { contact_name = "Lisa Evans", contact_id = 53252, bmp_crc = "homie_x", grp_h = 0 },
	[1] = { contact_name = "Kimberly Reyes", contact_id = 53252, bmp_crc = "homie_x", grp_h = 0  },
	[2] = { contact_name = "Jack Cassity", contact_id = 53252, bmp_crc = "homie_x", grp_h = 0  },
}

Cellphone_menu_garage = {
	menu_type = "phonebook",
	header_string = "CELL_HEADER_GARAGE",
	dynamic_menu = true,
	book_type = 4,
	num_items = 0,
	cur_idx = 0,
	handles = {},
	image_peg = -1,
	on_select = cellphone_garage_get_car,
	on_nav = cellphone_phonebook_nav,
	on_back = cellphone_menu_sub_exit,
	cleanup = cellphone_phonebook_cleanup,
	[0] = { contact_name = "Lisa Evans", contact_id = 53252, bmp_crc = "homie_x", grp_h = 0 },
	[1] = { contact_name = "Kimberly Reyes", contact_id = 53252, bmp_crc = "homie_x", grp_h = 0  },
	[2] = { contact_name = "Jack Cassity", contact_id = 53252, bmp_crc = "homie_x", grp_h = 0  },
}

Cellphone_menu_book = {
	menu_type = "phonebook",
	header_string = "CELL_OPTION_PHONEBOOK",
	dynamic_menu = true,
	cur_idx = 0,
	book_type = 1,
	num_items = 1,
	handles = {},
	image_peg = -1,
	on_select = cellphone_phonebook_call,
	on_nav = cellphone_phonebook_nav,
	on_back = cellphone_menu_sub_exit,
	cleanup = cellphone_phonebook_cleanup,
	[0] = { contact_name = "Jonny Gat", contact_id =53252, bmp_crc = "homie_x" },
}

Cellphone_menu_cheat_cat = {
	menu_type = "phonebook",
	header_string = "CELL_OPTION_CHEATS",
	dynamic_menu = false,
	book_type = 3,
	cur_idx = 0,
	num_items = 6,
	handles = {},
	image_peg = -1,
	on_select = cellphone_cheat_cat_select,
	on_nav = cellphone_phonebook_nav,
	on_back = cellphone_menu_sub_exit,
	cleanup = cellphone_phonebook_cleanup,
	[0] = { contact_name = "CELL_CHEAT_CAT_PLAYERABILITY"},
	[1] = { contact_name = "CELL_CHEAT_CAT_VEHICLES"},
	[2] = { contact_name = "CELL_CHEAT_CAT_WEAPONS"},
	[3] = { contact_name = "CELL_CHEAT_CAT_WEATHER"},
	[4] = { contact_name = "CELL_CHEAT_CAT_WORLD"},
	[5] = { contact_name = "CELL_CHEAT_CAT_CHARACTER"},	-- NPC Morph [nclok1405]
}

Cellphone_menu_cheat_spec = {
	menu_type = "phonebook",
	header_string = "",
	dynamic_menu = true,
	book_type = 3,
	cur_idx = 0,
	num_items = 1,
	handles = {},
	image_peg = -1,
	on_select = cellphone_cheat_spec_select,
	on_nav = cellphone_phonebook_nav,
	on_back = cellphone_cheat_spec_back,
	cleanup = cellphone_phonebook_cleanup,
	on_chat_all = cellphone_cheat_spec_chat_all,	-- Chat All [nclok1405]
	on_chat_team = cellphone_cheat_spec_chat_team,	-- Chat Team [nclok1405]
	[0] = { contact_name = "cheat1"},
}

Cellphone_menu_cheat_added = {
	menu_type = "cheat_added",
	header_string = "CELL_HEADER_CHEAT_ADDED",
	cur_idx = 0,
	num_items = 1,
	handles = {},
	on_select = cellphone_menu_sub_exit,
	on_back = cellphone_menu_sub_exit,
	[0] = {dummy_data = -1}
}

Cellphone_menu_cheat_activate = {
	menu_type = "cheat_activated",
	header_string = "CELL_HEADER_CHEAT_ACTIVATED",
	cur_idx = 0,
	num_items = 1,
	handles = {},
	on_select = cellphone_cheat_activated_exit,
	on_back = cellphone_cheat_activated_exit,
	[0] = {dummy_data = -1}
}

Cellphone_menu_main = {
	menu_type = "main",
	header_string = "",
	num_items = 4,
	cur_idx = 0,
	on_nav = cellphone_menu_main_item_nav,
	on_select = cellphone_menu_main_item_select,
	on_alt_select = cellphone_menu_main_item_alt_select,	-- Spacebar [nclok1405]
	on_back = cellphone_menu_main_back,
	handles = {},
	[0] = { label = "CELL_OPTION_HOMIES", sub_menu = Cellphone_menu_homies, bmp = "ui_menu_cell_homies", bmp_offset_x = 0, bmp_offset_y = 0, grp_h = 0, silhouette = false },
	[1] = { label = "CELL_OPTION_DIAL", sub_menu = Cellphone_menu_dial, bmp = "ui_menu_cell_dial", bmp_offset_x = 44, bmp_offset_y = 0, grp_h = 0, silhouette = false },
	[2] = { label = "CELL_OPTION_PHONEBOOK", sub_menu = Cellphone_menu_book, bmp = "ui_menu_cell_phonebook", bmp_offset_x = 78, bmp_offset_y = 0, grp_h = 0, silhouette = false },
	[3] = { label = "CELL_OPTION_CHEATS", sub_menu = Cellphone_menu_cheat_cat, bmp = "ui_menu_cell_cheats", bmp_offset_x = 62, bmp_offset_y = 0, grp_h = 0, silhouette = false },
}


