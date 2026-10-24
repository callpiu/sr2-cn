-- music_store.lua: "Scratch That" Music Store
-----------------
-- MUSIC STORE --
-----------------
-- "global" variables
MUSIC_STORE_FOOTER_FADE_TIME = .25

Music_store_data = { }
Music_store_footer = { }
Music_store_current_selection = 0
Music_store_menu = { }
MUSIC_STORE_DOC_HANDLE = vint_document_find("music_store")
Music_store_sort_data = { sort_by_artist = true, sorted_menu = -1 }
Music_store_dont_preview = false

----------------------
--	SYSTEM FUNCTIONS --
----------------------
--[ INITIALIZE AND SHUTDOWN ]--
-------------------------------
--	Initialize the menu
function music_store_init()

	--Event Tracking
	event_tracking_interface_enter("Music Store")

	menu_store_init(true)

	music_store_build_horz_menu()

	menu_init()
	menu_horz_init(Music_store_horz_menu)
end

-- Shutdown and cleanup the menu
function music_store_cleanup()
end

--[ EXIT ]--
------------
function music_store_exit(menu_data)
	local body = "MUSIC_STORE_EXIT_PROMPT"
	local heading = "MENU_TITLE_WARNING"

	--dialog_box_confirmation(heading, body, "music_store_exit_confirm")
	-- Exit without dialog [nclok1405]
	menu_close(music_store_exit_final)
end
function music_store_exit_confirm(result, action)
	if action ~= DIALOG_ACTION_CLOSE then
		return
	end

	if result == 0 then
		menu_close(music_store_exit_final)
	end
end
function music_store_exit_final()
	vint_document_unload(MUSIC_STORE_DOC_HANDLE)
end
--------------------------
-- FOOTER FUNCTIONALITY --
--------------------------
function music_store_clean_footer()
		vint_set_property(Music_store_footer.artist_h, "offset", 0, 0)
		vint_set_property(Music_store_footer.artist_h, "alpha", 1)
		vint_set_property(Music_store_footer.track_h, "offset", 0, 0)
		vint_set_property(Music_store_footer.track_h, "alpha", 1)

		--	Clean up stale threads/tweens
		if Music_store_footer.restart_thread ~= nil then
			thread_kill(Music_store_footer.restart_thread)
			Music_store_footer.track_thread = nil
		end

		if Music_store_footer.fade_thread ~= nil then
			thread_kill(Music_store_footer.fade_thread)
			Music_store_footer.fade_thread = nil
		end

		if Music_store_footer.track_fade_twn ~= nil then
			vint_object_destroy(Music_store_footer.track_fade_twn)
			Music_store_footer.track_fade_twn = nil
		end

		if Music_store_footer.track_twn ~= nil then
			vint_object_destroy(Music_store_footer.track_twn)
			Music_store_footer.track_twn = nil
		end

		if Music_store_footer.artist_fade_twn ~= nil then
			vint_object_destroy(Music_store_footer.artist_fade_twn)
			Music_store_footer.artist_fade_twn = nil
		end

		if Music_store_footer.artist_twn ~= nil then
			vint_object_destroy(Music_store_footer.artist_twn)
			Music_store_footer.artist_twn = nil
		end
end

function music_store_build_footer(menu_data)
	if menu_data.footer_height ~= nil and menu_data.footer_height ~= 0 then

		music_store_clean_footer()

		Music_store_footer.clip_width = nil

		--	Find the footer
		local grp = vint_object_clone(vint_object_find("music_store_footer"), Menu_option_labels.control_parent)
		vint_set_property(grp, "visible", true)

		--	Destroy the stale footer
		if menu_data.footer ~= nil and menu_data.footer.footer_grp ~= nil and menu_data.footer.footer_grp ~= 0 then
			vint_object_destroy(menu_data.footer.footer_grp)
		end

		menu_data.footer = { }
		menu_data.footer.footer_grp = grp

		-- Initialize everything
		Music_store_footer.clip_h = vint_object_find("music_footer_clip", grp)
		Music_store_footer.artist_h = vint_object_find("artist_label", grp)
		Music_store_footer.track_h = vint_object_find("track_label", grp)
		Music_store_footer.price_h = vint_object_find("price_amount", grp)

		vint_set_property(Music_store_footer.artist_h, "offset", 0, 0)
		vint_set_property(Music_store_footer.track_h, "offset", 0, 0)

		vint_set_property(Music_store_footer.artist_h, "visible", true)
		vint_set_property(Music_store_footer.track_h, "visible", true)
		vint_set_property(Music_store_footer.price_h , "visible", true)
	end
end

function music_store_update_footer(idx)
	local menu_item = Music_store_menu[idx]
	--	Make sure we have a footer
	if Music_store_menu.footer_height ~= nil and Music_store_menu.footer_height ~= 0 then
		-- Tint it according to the price (if the player can afford it
		if menu_store_get_player_cash() < menu_item.price then
			vint_set_property(Music_store_footer.price_h, "tint", 1, 0, 0)
		else
			vint_set_property(Music_store_footer.price_h, "tint", 0.88, 0.749, 0.05)
		end
		--	Set the other properties to reflect the track
		vint_set_property(Music_store_footer.price_h, "text_tag", "$" .. format_cash(menu_item.price))
		vint_set_property(Music_store_footer.artist_h, "text_tag", menu_item.artist_name)
		vint_set_property(Music_store_footer.track_h, "text_tag", menu_item.track_name)
	end
end

function music_store_finalize_footer(menu_data)
	--	Make sure we have a footer
	if menu_data.footer_height ~= nil and menu_data.footer_height ~= 0 then
		local price_size_x, price_size_y = vint_get_property(Music_store_footer.price_h, "screen_size")
		local clip_width = menu_data.menu_width - price_size_x - 23
		Music_store_footer.clip_width = clip_width

		--	Correct the position of the price
		vint_set_property(Music_store_footer.price_h, "anchor", menu_data.menu_width - 20, 0)
		vint_set_property(Music_store_footer.clip_h, "clip_size", clip_width, 60)

		music_store_scroll_footer()
	end

	btn_tips_update()
end

function music_store_scroll_footer()
	music_store_clean_footer()

	-- If the clip_width is messed up, carry on
	if Music_store_footer.clip_width == nil or Music_store_footer.clip_width == 0 then
		return
	end

	if Music_store_menu.footer_height ~= nil and Music_store_menu.footer_height ~= 0 then
		local artist_duration = 0
		local track_duration = 0
		local duration = 0
		local twn = 0

		-- Cleaning up a mess a little bit by putting these 2 together.
		for i = 0, 1 do
			local handle = 0
			if i == 0 then
				handle = Music_store_footer.artist_h
			else
				handle = Music_store_footer.track_h
			end

			local text_width, text_height = element_get_actual_size(handle, "screen_size")
			local clipped_width = text_width - Music_store_footer.clip_width

			-- Doesn't need to scroll if clipped width is under 0
			if clipped_width > 0 then
				clipped_width = clipped_width + 15
				duration = MENU_MARQUEE_SPEED * clipped_width 	--	Store the duration

				twn = vint_object_create("footer_tween", "tween", vint_object_find("root_animation", nil, MUSIC_STORE_DOC_HANDLE))
				vint_set_property(twn, "target_handle", handle)
				vint_set_property(twn, "target_property", "offset")
				vint_set_property(twn, "start_value", 0, 0)
				vint_set_property(twn, "end_value", 0 - clipped_width, 0)
				vint_set_property(twn, "duration", duration)
				vint_set_property(twn, "start_time", vint_get_time_index() + MENU_MARQUEE_DELAY)

				if i == 0 then
					artist_duration = duration
					Music_store_footer.artist_twn = twn
					Music_store_footer.artist_clipped_width = clipped_width
				else
					track_duration = duration
					Music_store_footer.track_twn = twn
					Music_store_footer.track_clipped_width = clipped_width
				end
			end
		end

		--	Set the call back on the longer one
		if (Music_store_footer.artist_twn == nil or Music_store_footer.artist_twn == 0) and (Music_store_footer.track_twn == nil or Music_store_footer.track_twn == 0) then
			return
		end

		if artist_duration > track_duration then
			twn = Music_store_footer.artist_twn
		else
			twn = Music_store_footer.track_twn
		end

		vint_set_property(twn, "end_event", "music_footer_scroll_twn_end")
	end
end

function music_footer_scroll_twn_end()
   if Music_store_footer.fade_thread ~= nil then
		thread_kill(Music_store_footer.fade_thread)
	end

	Music_store_footer.fade_thread = thread_new("music_footer_fade_twn_start")
end

function music_footer_fade_twn_start()
	delay(MENU_MARQUEE_DELAY)
	local twn = 0

	if Music_store_footer.artist_twn ~= nil and Music_store_footer.artist_twn ~= 0 then
		twn =	vint_object_create("footer_fade_twn", "tween", vint_object_find("root_animation", nil, MUSIC_STORE_DOC_HANDLE))
		vint_set_property(twn, "target_handle", Music_store_footer.artist_h)
		vint_set_property(twn, "target_property", "alpha")
		vint_set_property(twn, "start_value", 1)
		vint_set_property(twn, "end_value", 0)
		vint_set_property(twn, "duration", MUSIC_STORE_FOOTER_FADE_TIME)
		vint_set_property(twn, "start_time", vint_get_time_index())
		vint_set_property(twn, "end_event", "music_footer_fade_twn_end")
	end

	if Music_store_footer.artist_fade_twn ~= nil and Music_store_footer.artist_fade_twn ~= 0 then
		vint_object_destroy(Music_store_footer.artist_fade_twn)
	end

	Music_store_footer.artist_fade_twn = twn
	twn = 0

	if Music_store_footer.track_twn ~= nil and Music_store_footer.track_twn ~= 0 then
		twn =	vint_object_create("footer_fade_twn", "tween", vint_object_find("root_animation", nil, MUSIC_STORE_DOC_HANDLE))
		vint_set_property(twn, "target_handle", Music_store_footer.track_h)
		vint_set_property(twn, "target_property", "alpha")
		vint_set_property(twn, "start_value", 1)
		vint_set_property(twn, "end_value", 0)
		vint_set_property(twn, "duration", MUSIC_STORE_FOOTER_FADE_TIME)
		vint_set_property(twn, "start_time", vint_get_time_index())
		if Music_store_footer.artist_fade_twn == 0 then
			vint_set_property(twn, "end_event", "music_footer_fade_twn_end")
		end
	end

	if Music_store_footer.track_fade_twn ~= nil and Music_store_footer.track_fade_twn ~= 0 then
		vint_object_destroy(Music_store_footer.track_fade_twn)
	end

	Music_store_footer.track_fade_twn = twn
end

function music_footer_fade_twn_end()
   if Music_store_footer.restart_thread ~= nil then
		thread_kill(Music_store_footer.restart_thread)
	end

	Music_store_footer.restart_thread = thread_new("music_footer_twn_restart")
end

function music_footer_twn_restart()
	delay(MENU_MARQUEE_DELAY)
	vint_set_property(Music_store_footer.artist_h, "offset", 0, 0)
	vint_set_property(Music_store_footer.track_h, "offset", 0, 0)

	vint_set_property(Music_store_footer.artist_h, "alpha", 1)
	vint_set_property(Music_store_footer.track_h, "alpha", 1)

	delay(MENU_MARQUEE_DELAY)
	if Music_store_footer.artist_twn ~= 0 and Music_store_footer.artist_twn ~= nil then
		vint_set_property(Music_store_footer.artist_twn, "state", "waiting")
		vint_set_property(Music_store_footer.artist_twn, "start_time", vint_get_time_index())
	end

	if Music_store_footer.track_twn ~= 0 and Music_store_footer.track_twn ~= nil then
		vint_set_property(Music_store_footer.track_twn, "state", "waiting")
		vint_set_property(Music_store_footer.track_twn, "start_time", vint_get_time_index())
	end
end

function	music_store_release(menu_data)
	-- Clean up the group when the menu is released
	if menu_data.footer_height ~= 0 and menu_data.footer_height ~= nil and menu_data.footer ~= nil then
		vint_set_property(menu_data.footer.footer_grp, "visible", false)
		vint_object_destroy(menu_data.footer.footer_grp)
	end
end

------------------------
--	MENU FUNCTIONALITY --
------------------------
function music_store_build_horz_menu()
	Music_store_horz_menu.num_items = 0
	--	Get all the genres for the top menu
	vint_dataresponder_request("music_store_populate_genres", "music_store_add_genres", 0)
	local unlockable = table_clone(Music_store_horz_menu[0])
	for i = 0, Music_store_horz_menu.num_items - 2 do
		Music_store_horz_menu[i] = 	table_clone(Music_store_horz_menu[i + 1])
	end

--	Music_store_horz_menu[Music_store_horz_menu.num_items - 1] = table_clone(unlockable)
--	DAD 7/30/08 - Remove unlockables altogether. TDL 254954
	Music_store_horz_menu.num_items = Music_store_horz_menu.num_items - 1

end

function music_store_add_genres(display_name)
	local new_table = table_clone(Music_store_menu_a)

	--	Set the genre
	Music_store_horz_menu[Music_store_horz_menu.num_items] = { label = display_name, genre = Music_store_horz_menu.num_items,  sub_menu=new_table }
	--	Increment the count
	Music_store_horz_menu.num_items = Music_store_horz_menu.num_items + 1
end

function music_store_sort_menu(menu_data)

	if Music_store_btns.x_button == nil then
		return
	end

	-- Toggle what to sort by
	if Music_store_sort_data.sort_by_artist == true then
		Music_store_sort_data.sort_by_artist = false
	else
		Music_store_sort_data.sort_by_artist = true
	end

	--	Store the name of the artist and track so that we can highlight the same track after sorting
	Music_store_sort_data.sorted_artist = Music_store_menu[Music_store_menu.highlighted_item].artist_name
	Music_store_sort_data.sorted_track  = Music_store_menu[Music_store_menu.highlighted_item].track_name

	Music_store_dont_preview = true
	--	Rebuild the menu, sorted
	music_store_rebuild_menu(menu_data)
end

function music_store_rebuild_menu(menu_data)
	local menu_to_use
	local swapped

	--	Swap out the real menu with the a 3rd menu and store whether or not we've done that
	if Music_store_sort_data.sorted_menu == false then
		menu_to_use = Music_store_menu_c
		swapped = true
	else
		menu_to_use = Music_store_horz_menu[Music_store_horz_menu.current_selection].sub_menu
		swapped = false
	end

	-- Show the sorted menu
	menu_show(menu_to_use, MENU_TRANSITION_SWEEP_LEFT)

	--	Make sure we keep the fact it was sorted
	Music_store_sort_data.sorted_menu = swapped
	music_store_finalize_footer(menu_to_use)
end

function music_store_build_menu(menu_data)
	Music_store_menu = menu_data
	Music_store_sort_data.sorted_menu = false
	Music_store_menu.num_items = 0

	--	Build the menu
	vint_dataresponder_request("music_store_populate_tracks", "music_store_add_tracks", 0, Music_store_horz_menu[Music_store_horz_menu.current_selection].genre, Music_store_sort_data.sort_by_artist)

	--	No footer if there are no tracks
	if Music_store_menu.num_items == 0 then
		Music_store_menu.num_items = 1
		Music_store_menu[0] = { label = "STORE_MUSIC_NOT_UNLOCKED", type=MENU_ITEM_TYPE_SELECTABLE }
		Music_store_menu.footer_height = 0
		Music_store_btns.x_button = nil
	else
		Music_store_menu.footer_height = 40

		if Music_store_sort_data.sort_by_artist == false then
			Music_store_btns.x_button = { label = "MP3_PLAYLIST_OPTIONS_SORT_ARTIST", enabled = btn_tips_default_x, }
		else
			Music_store_btns.x_button = { label = "MP3_PLAYLIST_OPTIONS_SORT_TITLE", enabled = btn_tips_default_x, }
		end
	end

	--	Update the header
	menu_data.highlighted_item = 0
	menu_data.header_label_str = Music_store_horz_menu[Music_store_horz_menu.current_selection].label

	-- Select the same track if we just sorted
	if Music_store_sort_data.sorted_artist ~= 0 and Music_store_sort_data.sorted_artist ~= nil then
		for i = 0, menu_data.num_items - 1 do
			-- We found it, so highlight it, reset the stored artist/track and exit the loop
			if menu_data[i].artist_name == Music_store_sort_data.sorted_artist and menu_data[i].track_name == Music_store_sort_data.sorted_track then
				menu_data.highlighted_item = i
				Music_store_sort_data.sorted_artist = nil
				Music_store_sort_data.sorted_track_name = nil
				i = menu_data.num_items
			end
		end
	end

	-- Build the footer and correct the data
	music_store_build_footer(menu_data)
	music_store_update_footer(menu_data.highlighted_item)

	--	If we have a footer, that means its a real menu, and preview the track
	if (Music_store_menu.footer_height ~= nil and Music_store_menu.footer_height ~= 0) or Music_store_menu[Music_store_menu.highlighted_item].id ~= nil then
		if Music_store_dont_preview == true then
			Music_store_dont_preview = false
		else
			music_store_preview_track(Music_store_menu[Music_store_menu.highlighted_item].id)
		end
	else
		music_store_preview_track(-1)
	end
end

function music_store_add_tracks(artist_name, track_name, price)
	local display_name

	--	Display the correct thing according to sort
	if Music_store_sort_data.sort_by_artist == true then
		display_name = artist_name
	else
		display_name = track_name
	end

	Music_store_menu[Music_store_menu.num_items] = { label = display_name, type = MENU_ITEM_TYPE_SELECTABLE, on_select = music_store_purchase, on_nav = music_store_nav_item, price = price, id = Music_store_menu.num_items, artist_name=artist_name, track_name=track_name }
	Music_store_menu.num_items = Music_store_menu.num_items + 1
end

function music_store_purchase(menu_label, menu_data)
	-- Confirm the purchase if we can afford it
	if menu_store_get_player_cash() >= menu_data.price then
--		local body = "Do you wish to purchase " .. menu_data.artist_name .. " - " .. menu_data.track_name .. " for " .. format_cash(menu_data.price) .. "?"
		local insertion_values = { [0] = menu_data.artist_name, [1] = menu_data.track_name, [2] = format_cash(menu_data.price) }
		local body = vint_insert_values_in_string("MUSIC_STORE_PURCHASE_PROMPT", insertion_values)
		local heading = "MENU_TITLE_CONFIRM"
		dialog_box_confirmation(heading, body, "music_store_confirm_selection")
		Music_store_current_selection = menu_data
	else
		dialog_box_message("MENU_TITLE_NOTICE", "HUD_SHOP_INSUFFICIENT_FUNDS")
	end
end

function music_store_confirm_selection(result, action)
	if action ~= DIALOG_ACTION_CLOSE then
		return
	end

	-- If they want it, then buy it, and rebuild the menu to reflect that its no longer on the menu
	if result == 0 then
		award_style("music", Music_store_current_selection.price)
		music_store_make_purchase(Music_store_current_selection.id)
		music_store_rebuild_menu(Music_store_menu)
		audio_play(Menu_sound_purchase)
	end
end

function music_store_nav_item(menu_data)
	if Music_store_menu.footer_height ~= nil then
		vint_set_property(Music_store_footer.artist_h, "offset", 0, 0)
		vint_set_property(Music_store_footer.track_h, "offset", 0, 0)

		if Music_store_footer.artist_twn ~= nil then
			vint_object_destroy(Music_store_footer.artist_twn)
			Music_store_footer.artist_twn = nil
		end
		if Music_store_footer.artist_thread ~= nil then
			thread_kill(Music_store_footer.artist_thread)
			Music_store_footer.artist_thread = nil
		end

		if Music_store_footer.track_twn ~= nil then
			vint_object_destroy(Music_store_footer.track_twn)
			Music_store_footer.track_twn = nil
		end
		if Music_store_footer.track_thread ~= nil then
			thread_kill(Music_store_footer.track_thread)
			Music_store_footer.track_thread = nil
		end

		-- When traversing the menu, update the preview and footer when nav'ing
		if (Music_store_menu.footer_height ~= nil and Music_store_menu.footer_height ~= 0) or Music_store_menu[Music_store_menu.highlighted_item].id ~= nil then
			music_store_preview_track(Music_store_menu[Music_store_menu.highlighted_item].id)
		end

		music_store_update_footer(Music_store_menu[Music_store_menu.highlighted_item].id)

		music_store_scroll_footer()
	end
end

---------------
-- MENU DATA --
---------------
Music_store_btns = {
	a_button = { label = "CONTROL_SELECT", enabled = btn_tips_default_a, },
	x_button = { label = "MP3_PLAYLIST_OPTIONS_SORT_TITLE", enabled = btn_tips_default_x, },
	b_button = { label = "CONTROL_RESUME", enabled = btn_tips_default_b, },
}

Music_store_menu_a = {
	header_str 		= "NONE",
	max_height = 471,	-- Default: 375 [nclok1405]

	on_show 	  		= music_store_build_menu,
	on_back 	  		= music_store_exit,
	on_release 	  	= music_store_release,
	on_nav			= music_store_nav_item,
	on_alt_select 	= music_store_sort_menu,
	on_post_show	= music_store_finalize_footer,
	num_items  		= 0,

	btn_tips 		= Music_store_btns,
	footer_height 	= 40,
}

Music_store_menu_b = {
	header_str 		= "NONE",
	max_height = 471,	-- Default: 375 [nclok1405]

	on_show 	  		= music_store_build_menu,
	on_back 	  		= music_store_exit,
	on_release 	  	= music_store_release,
	on_nav			= music_store_nav_item,
	on_alt_select 	= music_store_sort_menu,
	on_post_show	= music_store_finalize_footer,
	num_items  		= 0,

	btn_tips 		= Music_store_btns,
	footer_height = 40,
}

Music_store_menu_c = {
	header_str 		= "NONE",
	max_height = 471,	-- Default: 375 [nclok1405]

	on_show 	  		= music_store_build_menu,
	on_back 	  		= music_store_exit,
	on_release 	  	= music_store_release,
	on_nav			= music_store_nav_item,
	on_alt_select 	= music_store_sort_menu,
	on_post_show	= music_store_finalize_footer,
	num_items  		= 0,

	btn_tips 		= Music_store_btns,
	footer_height = 40,
}


Music_store_horz_menu = {
	num_items = 0,
	current_selection = 0,

}
