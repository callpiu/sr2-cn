-- mp_server_browser.lua: Multiplayer (Co-op and Competitive) Server Browser
-- Variable section
Mp_server_browser_data = {
	handles = {
					buttons = {},
					button_shine = {},
					button_fade_in = {},
					button_fade_out = {},
					},
	input_subscriptions = {},
	current_tab = 1,
	is_360 = false,
	refresh = false,
}

Mp_server_browser_colors = {
	yellow = { r = 229/255, g = 191/255, b = 13/255}
}

Mp_server_browser_refresh_thread = true

-- Init and cleanup functions
function mp_server_browser_init()

	-- Set up object handles
	Mp_server_browser_data.handles.tab_group_h = vint_object_find("tab_group")
	Mp_server_browser_data.handles.tab_text_h = vint_object_find("tab_text")
	Mp_server_browser_data.handles.stat_headings_h = vint_object_find("stat_headings")
	Mp_server_browser_data.handles.user_row_h = vint_object_find("user_row")
	Mp_server_browser_data.handles.spreadsheet_row_h = vint_object_find("spreadsheet_row")
	Mp_server_browser_data.heading_stat1_h = vint_object_find("heading_stat1")
	Mp_server_browser_data.heading_stat2_h = vint_object_find("heading_stat2")
	Mp_server_browser_data.heading_stat3_h = vint_object_find("heading_stat3")
	Mp_server_browser_data.scroll_group_h = vint_object_find("scroll_group")
	Mp_server_browser_data.scroll_bar_h = vint_object_find("scroll_bar")

	local header_text = vint_object_find("heading_player")
	vint_set_property(header_text, "text_tag", "MP_SERVER_NAME")

	-- Set up animation handles
	Mp_server_browser_data.handles.tab_slide_h = vint_object_find("tab_slide")
	vint_set_property(Mp_server_browser_data.handles.tab_slide_h, "is_paused", true)

	Mp_server_browser_data.handles.highlight_shine_anim_h = vint_object_find("highlight_shine_anim")
	vint_set_property(Mp_server_browser_data.handles.highlight_shine_anim_h, "is_paused", true)

	Mp_server_browser_data.handles.columns_fade_h = vint_object_find("columns_fade")
	vint_set_property(Mp_server_browser_data.handles.columns_fade_h, "is_paused", true)

	Mp_server_browser_data.visible_row = {}
	Mp_server_browser_data.current_tab = 1

	local left_trigger_h = vint_object_find("left_trigger")
	local right_trigger_h = vint_object_find("right_trigger")

	if Main_menu_searching_LAN_games == true then
		-- Ctrl and Shift keys does nothing on LAN so no point of showing it [nclok1405]
		vint_set_property(left_trigger_h, "visible", false)
		vint_set_property(right_trigger_h, "visible", false)

		-- No arrows either [nclok1405]
		sui_hide_object("arrow_left")
		sui_hide_object("arrow_right")
	else
		vint_set_property(left_trigger_h, "image", get_left_trigger())
		vint_set_property(right_trigger_h, "image", get_right_trigger())
	end

	Mp_server_browser_data.top100 = true
	Mp_server_browser_data.num_tabs = 0
	Mp_server_browser_data.current_column = 3
	Mp_server_browser_data.can_move = true

	if Main_menu_searching_LAN_games == true then
		-- LAN
		Mp_server_browser_data.tabs = {	[1] =	{ 	title = "", -- Tab Title, previously "ALL" [nclok1405]
											column_1 = "MP_SERVER_IP", -- IP servera
											column_2 = "MP_SERVER_PING", -- Ping do servera
											column_3 = "", -- Game mode and players count
											num_columns = 0,
											data = {[3] = "MP_GB"},
											conversion = Mp_server_browser_format_commas,
											default_column = 1,
											show_badge = false,
											game_mode = -1
										},
									}
	else
		if Main_menu_is_coop_game == true then
			-- ONLINE COOP
			Mp_server_browser_data.tabs = {	[1] =	{ 	title = "ALL", -- All coop games
												column_1 = "MP_SERVER_IP", -- IP servera
												column_2 = "MP_SERVER_PING", -- Ping do servera
												column_3 = "MP_GAME_MODE", -- Game mode and players count
												num_columns = 0,
												data = {[3] = "MP_GB"},
												conversion = Mp_server_browser_format_commas,
												default_column = 1,
												show_badge = true,
												game_mode = -1,
											},
												
											[2] =	{ 	title = "PUBLIC",  -- Coop games without password
												column_1 = "MP_SERVER_IP", -- IP servera
												column_2 = "MP_SERVER_PING", -- Ping do servera
												column_3 = "MP_GAME_MODE", -- Game mode and players count
												num_columns = 0,
												data = {[3] = "MP_TGB"},
												conversion = Mp_server_browser_format_commas,
												default_column = 1,
												show_badge = true,
												game_mode = -2,
											},
										}
		else
			-- ONLINE
			Mp_server_browser_data.tabs = {
											[1] =	{ 	title = "ALL", -- Gangsta Brawl
												column_1 = "MP_SERVER_IP", -- IP servera
												column_2 = "MP_SERVER_PING", -- Ping do servera
												column_3 = "MP_GAME_MODE", -- Game mode and players count
												num_columns = 0,
												data = {[3] = "MP_GB"},
												conversion = Mp_server_browser_format_commas,
												default_column = 1,
												show_badge = true,
												game_mode = -1
											},

											[2] =	{ 	title = "MULTI_MODE_13", -- Gangsta Brawl
												column_1 = "MP_SERVER_IP", -- IP servera
												column_2 = "MP_SERVER_PING", -- Ping do servera
												column_3 = "MP_GAME_MODE", -- Game mode and players count
												num_columns = 0,
												data = {[3] = "MP_GB"},
												conversion = Mp_server_browser_format_commas,
												default_column = 1,
												show_badge = true,
												game_mode = 11,
											},
												
											[3] =	{ 	title = "MULTI_MODE_14",  -- Team Gangsta Brawl
												column_1 = "MP_SERVER_IP", -- IP servera
												column_2 = "MP_SERVER_PING", -- Ping do servera
												column_3 = "MP_GAME_MODE", -- Game mode and players count
												num_columns = 0,
												data = {[3] = "MP_TGB"},
												conversion = Mp_server_browser_format_commas,
												default_column = 1,
												show_badge = true,
												game_mode = 12,
											},	
														
											[4] =	{	title = "MULTI_MODE_STRONGARM", -- Strong Arm
												column_1 = "MP_SERVER_IP", -- IP servera
												column_2 = "MP_SERVER_PING", -- Ping do servera
												column_3 = "MP_GAME_MODE", -- Game mode and players count
												num_columns = 0,
												data = {[3] = "MP_SA"},
												conversion = Mp_server_browser_format_commas,
												default_column = 1,
												show_badge = true,
												game_mode = 13,
											},

										}
		end
	end

	local tab_divider = 20
	local tab_left_placer = 0

	for idx, val in Mp_server_browser_data.tabs do
		-- Make a  clone of the tab heading
		Mp_server_browser_data.tabs[idx].heading_h = vint_object_clone(Mp_server_browser_data.handles.tab_text_h)

		-- Put the title name in the tab
		vint_set_property(Mp_server_browser_data.tabs[idx].heading_h, "text_tag", Mp_server_browser_data.tabs[idx].title)

		-- Get the size of the tab
		local x_size, y_size, x_anchor, y_anchor
		x_size, y_size = element_get_actual_size(Mp_server_browser_data.tabs[idx].heading_h)
		Mp_server_browser_data.tabs[idx].center = tab_left_placer + x_size/2

		-- Move the tab to the end of the list
		x_anchor, y_anchor = vint_get_property(Mp_server_browser_data.tabs[idx].heading_h, "anchor")
		vint_set_property(Mp_server_browser_data.tabs[idx].heading_h, "anchor", tab_left_placer, y_anchor)
		vint_set_property(Mp_server_browser_data.tabs[idx].heading_h, "visible", true)

		-- Save the full size of the whole list of tabs
		Mp_server_browser_data.tab_range = tab_left_placer + x_size

		-- Set up the positioning for the next space
		tab_left_placer = tab_left_placer + x_size + tab_divider
		Mp_server_browser_data.num_tabs = Mp_server_browser_data.num_tabs + 1
	end

	--Subscribe to input
	Mp_server_browser_data.input_subscriptions = {
		vint_subscribe_to_input_event(nil, "nav_up",				"Mp_server_browser_input", 50),
		vint_subscribe_to_input_event(nil, "nav_down",			"Mp_server_browser_input", 50),
		vint_subscribe_to_input_event(nil, "nav_left",			"Mp_server_browser_input", 50),
		vint_subscribe_to_input_event(nil, "nav_right",			"Mp_server_browser_input", 50),
		vint_subscribe_to_input_event(nil, "scroll_left",		"Mp_server_browser_input", 50),
		vint_subscribe_to_input_event(nil, "scroll_right",		"Mp_server_browser_input", 50),
		vint_subscribe_to_input_event(nil, "select",				"Mp_server_browser_input", 50),
		vint_subscribe_to_input_event(nil, "back",				"Mp_server_browser_input", 50),
		vint_subscribe_to_input_event(nil, "alt_select",		"Mp_server_browser_input", 50),
		vint_subscribe_to_input_event(nil, "exit",				"Mp_server_browser_input", 50),
		vint_subscribe_to_input_event(nil, "map",					"Mp_server_browser_input", 50),
		vint_subscribe_to_input_event(nil, "pause",				"Mp_server_browser_input", 50),
	}

	-- Start first spreadsheet lookup
	Mp_server_browser_change_spreadsheet(0)

	--Hijack button tips from previous menu
	if vint_document_find("main_menu") ~= 0 then
		--Hide previous menu
		vint_set_property(Menu_option_labels.frame, "visible", false)

		--Set button tips previous menu and update tips
		Menu_active.btn_tips = Mp_server_browser_btn_tips
		Mp_server_browser_update_btn_tips()
	end

	if Main_menu_searching_LAN_games == true then
		start_find_syslink_servers()
	else
		if Main_menu_is_coop_game == true then
			start_coop_matchmaking()
		else
			start_find_online_servers(Multi_ranked)
		end
	end

	Mp_server_browser_refresh_thread = true
	thread_new( "Mp_server_browser_refresh_data" ) -- one thread per all columns
end

function mp_server_browser_cleanup()

	-- Blow away all the objects and animations
	for idx, val in Mp_server_browser_data.visible_row do
		vint_object_destroy(Mp_server_browser_data.visible_row[idx].pulsate)
		vint_object_destroy(Mp_server_browser_data.visible_row[idx].line_h)
	end

	-- Blow away all the data
	for idx, val in Mp_server_browser_data.list_data do
		Mp_server_browser_data.list_data[idx] = nil
	end

	-- Kill subscriptions
	for idx, val in Mp_server_browser_data.input_subscriptions do
		vint_unsubscribe_to_input_event(idx)
	end
	Mp_server_browser_data.input_subscriptions = nil


	--Show button tips on main menu
	if vint_document_find("main_menu") ~= 0 and Menu_active ~= 0 then
		--reset button tips
		Menu_active.btn_tips = nil
		btn_tips_update()
		vint_set_property(Menu_option_labels.frame, "visible", true)
	end
end

function Mp_server_browser_input(target, event, accelleration)

	-- Make sure button presses are ok first
	if Mp_server_browser_data.can_move == true then

		if event == "nav_up" then
			-- Up button pressed
			audio_play(Menu_sound_item_nav)
			Mp_server_browser_change_row(-1)

		elseif event == "nav_down" then
			-- Down button presses
			audio_play(Menu_sound_item_nav)
			Mp_server_browser_change_row(1)

		elseif event == "scroll_left" then
			-- Left button pressed
			if Mp_server_browser_data.num_tabs > 1 then
				audio_play(Menu_sound_scroll)
				Mp_server_browser_change_spreadsheet(-1)
				Mp_server_browser_change_row(0)
			end

		elseif event == "scroll_right" then
			-- Right button presses
			if Mp_server_browser_data.num_tabs > 1 then
				audio_play(Menu_sound_scroll)
				Mp_server_browser_change_spreadsheet(1)
				Mp_server_browser_change_row(0)
			end

		elseif event == "nav_left" then
			-- Resort
			if Mp_server_browser_data.tabs[Mp_server_browser_data.current_tab].num_columns > 1 then
				audio_play(Menu_sound_value_nav)
				Mp_server_browser_change_column(-1)
			end

		elseif event == "nav_right" then
			-- Resort
			if Mp_server_browser_data.tabs[Mp_server_browser_data.current_tab].num_columns > 1 then
				audio_play(Menu_sound_value_nav)
				Mp_server_browser_change_column(1)
			end

		elseif event == "select" then
			if Mp_server_browser_data.list_data[Mp_server_browser_data.current_virtual_row] ~= nil then
				audio_play(Menu_sound_back)
				menu_input_block(false)
				--main_menu_restore()
				--dialog_box_force_close_all()
				local server_id = Mp_server_browser_data.list_data[Mp_server_browser_data.current_virtual_row].server_id

				-- enter the server
				if Main_menu_searching_LAN_games == true then
					join_syslink_game( server_id )
				else
					if Main_menu_is_coop_game == true then
						join_online_coop_game( server_id )
					else
						join_online_game( server_id, Multi_ranked )
					end
				end
				
				if Main_menu_searching_LAN_games == true then
					stop_find_syslink_servers()
				else
					--stop_find_online_servers()
				end

				vint_datagroup_remove_subscription("sr2_syslink_servers_group", "update", "mp_server_browser_list_update")
				vint_datagroup_remove_subscription("sr2_syslink_servers_group", "insert", "mp_server_browser_list_update")
				vint_datagroup_remove_subscription("sr2_syslink_servers_group", "remove", "mp_server_browser_list_update")

				Mp_server_browser_refresh_thread = false

				vint_document_unload(vint_document_find("mp_server_browser"))
			end

		elseif event == "back" then
			-- Animate out
			vint_datagroup_remove_subscription("sr2_syslink_servers_group", "update", "mp_server_browser_list_update")
			vint_datagroup_remove_subscription("sr2_syslink_servers_group", "insert", "mp_server_browser_list_update")
			vint_datagroup_remove_subscription("sr2_syslink_servers_group", "remove", "mp_server_browser_list_update")
			if Main_menu_searching_LAN_games == true then
				stop_find_syslink_servers()
			else
				stop_find_online_servers()
			end

			Mp_server_browser_refresh_thread = false

			vint_document_unload(vint_document_find("mp_server_browser"))
			audio_play(Menu_sound_back)
			menu_input_block(false)

		elseif event == "alt_select" then
			if Main_menu_searching_LAN_games == false then
				if Main_menu_is_coop_game == true then
					stop_find_online_servers()
					clear_sb_list();
					start_coop_matchmaking()
				else
					stop_find_online_servers()
					clear_sb_list();
					start_find_online_servers(Multi_ranked)
				end
			end
		elseif event == "exit" then
			-- Do nothing, just block menu base from seeing this
		end
	end
end

function mp_server_browser_cleanup_hints()
	local bx = 17
	local gap = 36

	-- Clean up their positions (lots of nasty magic numbers here because I copy/pasted it - jhg)
	local t1a, t1b = vint_get_property(Mp_server_browser_data.handles.A_text_h, "anchor")
	local t1x, t1y = element_get_actual_size(Mp_server_browser_data.handles.A_text_h)
	vint_set_property(Mp_server_browser_data.handles.X_btn_h, "anchor", t1a + t1x + gap, 498.0)

	local b2a, b2b = vint_get_property(Mp_server_browser_data.handles.X_btn_h, "anchor")
	vint_set_property(Mp_server_browser_data.handles.X_text_h, "anchor", bx + b2a + 16, t1b)

	local t2x, t2y = element_get_actual_size(Mp_server_browser_data.handles.X_text_h)
	local t2a, t2b = vint_get_property(Mp_server_browser_data.handles.X_text_h, "anchor")
	vint_set_property(Mp_server_browser_data.handles.B_btn_h, "anchor", t2a + t2x + gap, 498.0)

	local b3a, b3b = vint_get_property(Mp_server_browser_data.handles.B_btn_h, "anchor")
	vint_set_property(Mp_server_browser_data.handles.B_text_h, "anchor", b3a + bx + 16, t1b)

end

function Mp_server_browser_change_spreadsheet(idir)

	-- Set up new tab index
	Mp_server_browser_data.current_tab = Mp_server_browser_data.current_tab + idir

	-- Wrap index if necessary
	if Mp_server_browser_data.current_tab < 1 then
		Mp_server_browser_data.current_tab = Mp_server_browser_data.num_tabs

	elseif Mp_server_browser_data.current_tab > Mp_server_browser_data.num_tabs then
		Mp_server_browser_data.current_tab = 1
	end

	-- Blank out colors on all tabs
	for idx, val in Mp_server_browser_data.tabs do
		local clear_tab = Mp_server_browser_data.tabs[idx].heading_h
		vint_set_property(clear_tab, "tint",95/255,95/255,95/255)
	end

	-- Make new tab yellow
	local new_tab_h = Mp_server_browser_data.tabs[Mp_server_browser_data.current_tab].heading_h
	vint_set_property(new_tab_h, "tint", Mp_server_browser_colors.yellow.r, Mp_server_browser_colors.yellow.g, Mp_server_browser_colors.yellow.b)

	-- Set up animation to move the tabs
	local tab_tween_h = vint_object_find("tab_text_translate",Mp_server_browser_data.handles.tab_slide_h)
	local x, y = vint_get_property(Mp_server_browser_data.handles.tab_group_h,"anchor")
	vint_set_property(tab_tween_h, "start_value", x, 0.0)
	vint_set_property(Mp_server_browser_data.handles.stat_headings_h, "alpha", 0.0)

	if Mp_server_browser_data.num_tabs == 0 then
		debug_print("vint", "Should not be changing the spreadsheet when there are no tabs set!\n")
	else
		local frame_size = vint_get_property(vint_object_find("tab_clip"),"clip_size")
		frame_size = frame_size - 4 -- Safety buffer to make sure we don't accidentally cut the edges of any text
		local destination = 0

		-- Are we already showing all options to the left?
		if Mp_server_browser_data.tabs[Mp_server_browser_data.current_tab].center < frame_size/2 then
			destination = 0
		-- Are we already showing all options to the right?
		elseif Mp_server_browser_data.tabs[Mp_server_browser_data.current_tab].center > Mp_server_browser_data.tab_range - frame_size/2 then
			destination = - Mp_server_browser_data.tab_range + frame_size
		-- We're somewhere in the middle, just peg the current selection in the center
		else
			destination = - Mp_server_browser_data.tabs[Mp_server_browser_data.current_tab].center + frame_size/2
		end

		vint_set_property(tab_tween_h, "end_value", destination, 0.0)
	end

	-- Move the tabs
	lua_play_anim(Mp_server_browser_data.handles.tab_slide_h,0)
	lua_play_anim(Mp_server_browser_data.handles.columns_fade_h,0)

	-- Set the column texts
	local heading_1 = Mp_server_browser_data.tabs[Mp_server_browser_data.current_tab].column_1
	local heading_2 = Mp_server_browser_data.tabs[Mp_server_browser_data.current_tab].column_2
	local heading_3 = Mp_server_browser_data.tabs[Mp_server_browser_data.current_tab].column_3

	if heading_2 == nil then
		heading_2 = " "
	end

	if heading_3 == nil then
		heading_3 = " "
	end

	vint_set_property(Mp_server_browser_data.heading_stat1_h, "text_tag", heading_1)
	vint_set_property(Mp_server_browser_data.heading_stat2_h, "text_tag", heading_2)
	vint_set_property(Mp_server_browser_data.heading_stat3_h, "text_tag", heading_3)

	-- Zero out the spreadsheet cursors
	Mp_server_browser_data.current_virtual_row = 1
	Mp_server_browser_data.current_column = Mp_server_browser_data.tabs[Mp_server_browser_data.current_tab].default_column

	-- Refresh the column (which automatically refreshes the spreadsheet)
	Mp_server_browser_change_column(0)

end

function Mp_server_browser_change_row(idir)

	-- Set up virtual row
	Mp_server_browser_data.current_virtual_row = Mp_server_browser_data.current_virtual_row + idir

	-- Wrap virtual row
	if Mp_server_browser_data.current_virtual_row < 1 then
		Mp_server_browser_data.current_virtual_row = Mp_server_browser_data.num_virtual_rows
	elseif Mp_server_browser_data.current_virtual_row > Mp_server_browser_data.num_virtual_rows then
		Mp_server_browser_data.current_virtual_row = 1
	end

	-- Set up visible row
	if Mp_server_browser_data.num_virtual_rows > 10 then

		-- If we're at the top of the list, clamp things down and move the highlight toward the top
		if Mp_server_browser_data.current_virtual_row <= 5 then
			Mp_server_browser_data.top_virtual_row = 1
			Mp_server_browser_data.current_visible_row = Mp_server_browser_data.current_virtual_row

		-- If we're at the bottom of the list, clamp things and move the highlight toward the bottom
		elseif Mp_server_browser_data.current_virtual_row > Mp_server_browser_data.num_virtual_rows - 5 then
			Mp_server_browser_data.top_virtual_row = Mp_server_browser_data.num_virtual_rows - 9
			Mp_server_browser_data.current_visible_row = Mp_server_browser_data.current_virtual_row - Mp_server_browser_data.num_virtual_rows + 10

		-- We're scrolling somewhere in the middle, clamp the highlight and move the virtual list around it
		else
			Mp_server_browser_data.top_virtual_row = Mp_server_browser_data.current_virtual_row - 4
			Mp_server_browser_data.current_visible_row = 5
		end

		-- Redraw the row text
		Mp_server_browser_redraw_rows()

	else
		-- No chance of scrolling, so just modify the highlight
		Mp_server_browser_data.current_visible_row = Mp_server_browser_data.current_virtual_row
	end

	-- Draw in the highlight
	for i = 1, Mp_server_browser_data.num_visible_rows do
		if i == Mp_server_browser_data.current_visible_row then
			vint_set_property(Mp_server_browser_data.visible_row[i].highlight_h, "visible", true)
		else
			vint_set_property(Mp_server_browser_data.visible_row[i].highlight_h, "visible", false)
		end
	end

end

function Mp_server_browser_change_column(idir)

	local num_columns = Mp_server_browser_data.tabs[Mp_server_browser_data.current_tab].num_columns

	-- Blank out old column
	vint_set_property(Mp_server_browser_data.heading_stat1_h, "tint",160/255,160/255,160/255)
	vint_set_property(Mp_server_browser_data.heading_stat2_h, "tint",160/255,160/255,160/255)
	vint_set_property(Mp_server_browser_data.heading_stat3_h, "tint",160/255,160/255,160/255)

	if num_columns ~= 0 then
		-- Set up new column index
		Mp_server_browser_data.current_column = Mp_server_browser_data.current_column + idir

		-- Wrap if necessary
		if Mp_server_browser_data.current_column < 1 then
			Mp_server_browser_data.current_column = num_columns
		elseif Mp_server_browser_data.current_column > num_columns then
			Mp_server_browser_data.current_column = 1
		end

		-- Color in new column
		if Mp_server_browser_data.current_column == 1 then
			vint_set_property(Mp_server_browser_data.heading_stat1_h, "tint", Mp_server_browser_colors.yellow.r, Mp_server_browser_colors.yellow.g, Mp_server_browser_colors.yellow.b)
		elseif Mp_server_browser_data.current_column == 2 then
			vint_set_property(Mp_server_browser_data.heading_stat2_h, "tint", Mp_server_browser_colors.yellow.r, Mp_server_browser_colors.yellow.g, Mp_server_browser_colors.yellow.b)
		elseif Mp_server_browser_data.current_column == 3 then
			vint_set_property(Mp_server_browser_data.heading_stat3_h, "tint", Mp_server_browser_colors.yellow.r, Mp_server_browser_colors.yellow.g, Mp_server_browser_colors.yellow.b)
		end
	end
	Mp_server_browser_data.refresh = true
end

function Mp_server_browser_new_record( server_id, name, stat1, stat2, stat3, mode, pass )

	-- Increment the virtual row
	local i = Mp_server_browser_data.num_virtual_rows_all + 1

	-- Format the values (commas, $, distance)

	if stat2 == nil then
		stat2 = " "
	end

	if stat3 == nil then
		stat3 = " "
	end

	-- Format data
	local d = {
		rank = 1,
		badge = pass, -- holding pass/no pass here
		name = name,
		stat1 = stat1,
		stat2 = stat2,
		stat3 = stat3,
		is_friend = 0, -- Throw away friend variable because we couldn't use it the way we wanted to
		is_player = false,
		index = 0,
		server_id = server_id,
		game_mode = mode,
	}

	-- Assign the data to the local variable
	Mp_server_browser_data.list_data_all[i] = d
	Mp_server_browser_data.num_virtual_rows_all = i
	Mp_server_browser_data.refresh = true

end

-- Formats a distance string given an initial value in meters
function Mp_server_browser_format_distance(value)

	if use_imperial_units() then
		-- Convert to feet
		value = floor(value * 3.2808399)

		-- Format the feet string and display
		value = Mp_server_browser_format_commas(value)
		value = {[0] = value}
		return vint_insert_values_in_string("LUA_DISTANCE_FEET", value)
	else
		-- Format the meters string and display
		value = Mp_server_browser_format_commas(value)
		value = {[0] = value}
		return vint_insert_values_in_string("LUA_DISTANCE_METERS", value)
	end
end

-- Formats a time string given an intial value in seconds
function Mp_server_browser_format_time(time_in_seconds)

	-- Pull out hours, minutes, and seconds
	local hours = floor(time_in_seconds / 3600)
	local minutes = floor(time_in_seconds / 60) - (hours * 60)
	local seconds =  mod(time_in_seconds, 60)

	-- Pad minutes if less than 10 and there are hours
	if hours > 0 and minutes < 10 then
		minutes = "0" .. minutes
	end

	-- Pad seconds if needed
	if seconds < 10 then
		seconds = "0" .. seconds
	end

	-- Build the string
	if hours > 0 then
		return hours .. ":" .. minutes .. ":" .. seconds
	else
		return minutes .. ":" .. seconds
	end
end

-- Formats a given value into money with commas
function Mp_server_browser_format_money(value)
	return "$" .. format_cash(value)
end

-- Adds commas to a numerical value
function Mp_server_browser_format_commas(value)
	return format_cash(value)
end

function sort_server_table(table, size)
	if sort_by == 0 then --sort by name
		local temp_server = table[0];
		i = 0
		while i < size do
			j = 0
			while j < size do
				if table[i].name > table[j].name then
					temp_server = table[i]
					table[i] = table[j]
					table[j] = temp_server
				end
				j = j + 1
			end
			i = i + 1
		end
	end
end

function Mp_server_browser_refresh_data()
	-- Lock out changing
	--Mp_server_browser_data.can_move = false

	-- Blow away old physical lines
	for idx, val in Mp_server_browser_data.visible_row do
		vint_object_destroy(Mp_server_browser_data.visible_row[idx].pulsate)
		vint_object_destroy(Mp_server_browser_data.visible_row[idx].line_h)
	end

	-- Hide the player data
	vint_set_property(Mp_server_browser_data.handles.user_row_h, "visible", false)

	-- Get rid of the scroll bar
	vint_set_property(Mp_server_browser_data.scroll_group_h, "visible", false)

	Mp_server_browser_data.refresh = false

	vint_datagroup_add_subscription("sr2_syslink_servers_group", "update", "mp_server_browser_list_update")
	vint_datagroup_add_subscription("sr2_syslink_servers_group", "insert", "mp_server_browser_list_update")
	vint_datagroup_add_subscription("sr2_syslink_servers_group", "remove", "mp_server_browser_list_update")

	-- Blow away any old player data
	-- Zero out the number of vitual rows
	Mp_server_browser_data.top_virtual_row = 1
	Mp_server_browser_data.current_virtual_row = 1
	Mp_server_browser_data.current_visible_row = 1
	Mp_server_browser_data.num_virtual_rows = 0
	Mp_server_browser_data.num_virtual_rows_all = 0
	Mp_server_browser_data.list_data = { }
	Mp_server_browser_data.list_data_all = { }

	--Mp_server_browser_new_record( 0, "test", "IP_TEST", ">10ms", nil, 3 )

	while Mp_server_browser_refresh_thread == true do
		if Mp_server_browser_data.refresh == true then
			Mp_server_browser_data.refresh = false

			-- Blow away old physical lines
			for idx, val in Mp_server_browser_data.visible_row do
				vint_object_destroy(Mp_server_browser_data.visible_row[idx].pulsate)
				vint_object_destroy(Mp_server_browser_data.visible_row[idx].line_h)
			end
			Mp_server_browser_data.list_data = { }

			local sheet_game_mode = Mp_server_browser_data.tabs[Mp_server_browser_data.current_tab].game_mode
			local servers_count = 0
			for idx, server in Mp_server_browser_data.list_data_all do
				if sheet_game_mode == -1 or server.game_mode == sheet_game_mode then
					Mp_server_browser_data.list_data[servers_count+1] = server
					servers_count = servers_count + 1
				else
					if sheet_game_mode == -2 and server.badge == 0 then -- coop, public games only
						Mp_server_browser_data.list_data[servers_count+1] = server
						servers_count = servers_count + 1
					end
				end
			end
			Mp_server_browser_data.num_virtual_rows = servers_count

			--sort_server_table(Mp_server_browser_data.list_data, servers_count)

			-- Get the data name we're using
			local data = Mp_server_browser_data.tabs[Mp_server_browser_data.current_tab].data[Mp_server_browser_data.current_column]

			-- Set up number of visible rows
			Mp_server_browser_data.num_visible_rows = Mp_server_browser_data.num_virtual_rows

			-- We have more virtual rows than we can display
			if Mp_server_browser_data.num_visible_rows > 10 then

				-- Clamp visible rows to 10
				Mp_server_browser_data.num_visible_rows = 10

				-- Set up scroll bar translation scaler
				Mp_server_browser_data.scroll_bar_scaler =  18 + 185 * ((Mp_server_browser_data.num_virtual_rows - 11)/89)

				-- Set up scroll bar size
				local scale_y = 65 + 185 * ((100 - Mp_server_browser_data.num_virtual_rows)/89)
				local bar_h = vint_object_find("scroll_bar", Mp_server_browser_data.scroll_group_h)
				local bottom_h = vint_object_find("scroll_bar_bottom", bar_h)
				vint_set_property(bar_h, "source_se", 32.0, scale_y)
				vint_set_property(bottom_h, "anchor", 0.0, scale_y)

				-- Display the scroll bar
				vint_set_property(Mp_server_browser_data.scroll_group_h, "visible", true)
			else
				-- Declare anyway just in case
				Mp_server_browser_data.scroll_bar_scaler =  0
			end

			-- Hang on to position of top row
			local x,y = vint_get_property(Mp_server_browser_data.handles.spreadsheet_row_h, "anchor")

			-- Make all the new visible rows and set them up for code reference
			for i = 1, Mp_server_browser_data.num_visible_rows do

				-- Clone row and animation
				local line_h = vint_object_clone(Mp_server_browser_data.handles.spreadsheet_row_h)
				local pulsate = vint_object_clone(Mp_server_browser_data.handles.highlight_shine_anim_h)

				-- Apply animation
				local pulsate_tween = vint_object_find("highlight_shine_fade", pulsate)
				vint_set_property(pulsate_tween, "target_handle", vint_object_find("highlight_back_shine", line_h))

				-- Set all new handles
				local highlight_h = vint_object_find("highlight", line_h)
				local highlight_name_h = vint_object_find("highlight_name", line_h)
				local highlight_stat1_h = vint_object_find("highlight_stat1", line_h)
				local highlight_stat2_h = vint_object_find("highlight_stat2", line_h)
				local highlight_stat3_h = vint_object_find("highlight_stat3", line_h)
				local normal_rank_h = vint_object_find("normal_rank", line_h)
				local normal_badge_h = vint_object_find("normal_badge", line_h)
				local normal_name_h = vint_object_find("normal_name", line_h)
				local normal_stat1_h = vint_object_find("normal_stat1", line_h)
				local normal_stat2_h = vint_object_find("normal_stat2", line_h)
				local normal_stat3_h = vint_object_find("normal_stat3", line_h)

				-- Save everything in a nice table
				Mp_server_browser_data.visible_row[i] = {line_h = line_h,
																	pulsate = pulsate,
																	highlight_h = highlight_h,
																	highlight_name_h = highlight_name_h,
																	highlight_stat1_h = highlight_stat1_h,
																	highlight_stat2_h = highlight_stat2_h,
																	highlight_stat3_h = highlight_stat3_h,
																	normal_rank_h = normal_rank_h,
																	normal_badge_h = normal_badge_h,
																	normal_name_h = normal_name_h,
																	normal_stat1_h = normal_stat1_h,
																	normal_stat2_h = normal_stat2_h,
																	normal_stat3_h = normal_stat3_h,
																	}

				-- Draw the row
				vint_set_property(Mp_server_browser_data.visible_row[i].line_h, "anchor", x, y + (32 * (i - 1)))
				vint_set_property(Mp_server_browser_data.visible_row[i].line_h, "visible", true)
			end
			-- Fill in the lines based on position
			Mp_server_browser_redraw_rows()

			-- Return the cursor
			Mp_server_browser_change_row(0)
		end

		thread_yield()

	end

	-- Unlock changing
	--Mp_server_browser_data.can_move = true
end

function Mp_server_browser_redraw_rows()

	-- Fill data into all the spreadsheet based on how many visible rows there are
	for i = 1, Mp_server_browser_data.num_visible_rows do
		-- Hang on to virtualized number of the row
		local virtual = Mp_server_browser_data.top_virtual_row + i - 1

		-- Set all the graphics
		vint_set_property(Mp_server_browser_data.visible_row[i].highlight_name_h, "text_tag", Mp_server_browser_data.list_data[virtual].name)
		vint_set_property(Mp_server_browser_data.visible_row[i].highlight_stat1_h, "text_tag", Mp_server_browser_data.list_data[virtual].stat1)
		vint_set_property(Mp_server_browser_data.visible_row[i].highlight_stat2_h, "text_tag", Mp_server_browser_data.list_data[virtual].stat2)
		vint_set_property(Mp_server_browser_data.visible_row[i].highlight_stat3_h, "text_tag", Mp_server_browser_data.list_data[virtual].stat3)
		--vint_set_property(Mp_server_browser_data.visible_row[i].normal_rank_h, "text_tag", Mp_server_browser_data.list_data[virtual].rank)
		vint_set_property(Mp_server_browser_data.visible_row[i].normal_badge_h, "image", "ui_pc_server_locked" )
		vint_set_property(Mp_server_browser_data.visible_row[i].normal_name_h, "text_tag", Mp_server_browser_data.list_data[virtual].name)
		vint_set_property(Mp_server_browser_data.visible_row[i].normal_stat1_h, "text_tag", Mp_server_browser_data.list_data[virtual].stat1)
		vint_set_property(Mp_server_browser_data.visible_row[i].normal_stat2_h, "text_tag", Mp_server_browser_data.list_data[virtual].stat2)
		vint_set_property(Mp_server_browser_data.visible_row[i].normal_stat3_h, "text_tag", Mp_server_browser_data.list_data[virtual].stat3)

		-- Set badge visibility
		if Mp_server_browser_data.list_data[virtual].badge == 1 then
			vint_set_property( Mp_server_browser_data.visible_row[i].normal_badge_h, "visible",  true )
		else
			vint_set_property( Mp_server_browser_data.visible_row[i].normal_badge_h, "visible",  false )
		end

		vint_set_property( Mp_server_browser_data.visible_row[i].normal_rank_h, "visible", false )

		-- Set name and badge colors
--		if Mp_server_browser_data.list_data[virtual].is_player == true then
--			vint_set_property(Mp_server_browser_data.visible_row[i].normal_rank_h, "tint", Mp_server_browser_colors.yellow.r, Mp_server_browser_colors.yellow.g, Mp_server_browser_colors.yellow.b)
--			vint_set_property(Mp_server_browser_data.visible_row[i].normal_name_h, "tint", Mp_server_browser_colors.yellow.r, Mp_server_browser_colors.yellow.g, Mp_server_browser_colors.yellow.b)
--		else
--			vint_set_property(Mp_server_browser_data.visible_row[i].normal_rank_h, "tint", 95/255,95/255,95/255)
--			vint_set_property(Mp_server_browser_data.visible_row[i].normal_name_h, "tint", 95/255,95/255,95/255)
--		end

		-- Start with blank column colors
		if Mp_server_browser_data.list_data[virtual].is_player == true then
			vint_set_property(Mp_server_browser_data.visible_row[i].normal_stat1_h, "tint", Mp_server_browser_colors.yellow.r, Mp_server_browser_colors.yellow.g, Mp_server_browser_colors.yellow.b)
			vint_set_property(Mp_server_browser_data.visible_row[i].normal_stat2_h, "tint", Mp_server_browser_colors.yellow.r, Mp_server_browser_colors.yellow.g, Mp_server_browser_colors.yellow.b)
			vint_set_property(Mp_server_browser_data.visible_row[i].normal_stat3_h, "tint", Mp_server_browser_colors.yellow.r, Mp_server_browser_colors.yellow.g, Mp_server_browser_colors.yellow.b)

		else
			vint_set_property(Mp_server_browser_data.visible_row[i].normal_stat1_h, "tint", 95/255,95/255,95/255)
			vint_set_property(Mp_server_browser_data.visible_row[i].normal_stat2_h, "tint", 95/255,95/255,95/255)
			vint_set_property(Mp_server_browser_data.visible_row[i].normal_stat3_h, "tint", 95/255,95/255,95/255)
		end

		local num_columns = Mp_server_browser_data.tabs[Mp_server_browser_data.current_tab].num_columns

		if num_columns > 0 then
			-- Add column highlight color
			if Mp_server_browser_data.current_column == 1 then
				vint_set_property(Mp_server_browser_data.visible_row[i].normal_stat1_h, "tint", Mp_server_browser_colors.yellow.r, Mp_server_browser_colors.yellow.g, Mp_server_browser_colors.yellow.b)
			elseif Mp_server_browser_data.current_column == 2 then
				vint_set_property(Mp_server_browser_data.visible_row[i].normal_stat2_h, "tint", Mp_server_browser_colors.yellow.r, Mp_server_browser_colors.yellow.g, Mp_server_browser_colors.yellow.b)
			elseif Mp_server_browser_data.current_column == 3 then
				vint_set_property(Mp_server_browser_data.visible_row[i].normal_stat3_h, "tint", Mp_server_browser_colors.yellow.r, Mp_server_browser_colors.yellow.g, Mp_server_browser_colors.yellow.b
)
			end
		end
	end

	-- Set up destination for scroll bar
	local bar_y = 202 + (Mp_server_browser_data.scroll_bar_scaler * (Mp_server_browser_data.current_virtual_row - 1)/(Mp_server_browser_data.num_virtual_rows - 1))
	vint_set_property(Mp_server_browser_data.scroll_bar_h, "anchor", 991.0, bar_y)
end


function Mp_server_browser_update_btn_tips()

	--Call to menubase to update the button tips
	btn_tips_update()
end

function Mp_server_browser_btn_x_is_active()
	return (Main_menu_searching_LAN_games == false)
end

Mp_server_browser_btn_tips = {
	a_button 	= 	{ label = "CONTROL_SELECT", 	enabled = true},
	x_button 	= 	{ label = "REFRESH", 			enabled = Mp_server_browser_btn_x_is_active},
	b_button 	= 	{ label = "MENU_BACK", 			enabled = true},
}

Mp_server_browser_btn_temp_tips = {}

function mp_server_browser_list_update( di_h, event )

	local display_string, is_mp, id, ip_str, ping_str, mode, pass, mode_str = vint_dataitem_get(di_h)

	if Main_menu_showing_coop_games == true then
		if is_mp == true then
			mp_player_has_favorite_match_settings()
			return
		end
	elseif is_mp == false then
		mp_load_custom_match_settings_from_favorite()
		return
	end

	if event == "insert" then
		Mp_server_browser_new_record( id, display_string, ip_str, ping_str, mode_str, mode, pass )
	elseif event == "remove" then

	elseif event == "update" then

	end

end

function clear_sb_list()

	-- Blow away old physical lines
	for idx, val in Mp_server_browser_data.visible_row do
		vint_object_destroy(Mp_server_browser_data.visible_row[idx].pulsate)
		vint_object_destroy(Mp_server_browser_data.visible_row[idx].line_h)
	end

	-- Hide the player data
	vint_set_property(Mp_server_browser_data.handles.user_row_h, "visible", false)

	-- Get rid of the scroll bar
	vint_set_property(Mp_server_browser_data.scroll_group_h, "visible", false)

	Mp_server_browser_data.top_virtual_row = 1
	Mp_server_browser_data.current_virtual_row = 1
	Mp_server_browser_data.current_visible_row = 1
	Mp_server_browser_data.num_virtual_rows = 0
	Mp_server_browser_data.num_virtual_rows_all = 0
	Mp_server_browser_data.list_data = { }
	Mp_server_browser_data.list_data_all = { }
	--Mp_server_browser_data.refresh = true
end

