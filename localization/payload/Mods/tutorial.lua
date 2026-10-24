-- tutorial.lua: Tutorial Popup Dialogs

Tutorial = {}
Tutorial_hud_doc = -1
Tutorial_hud_prunings = {}

Tutorial_hud_anim_cleanup = {}
Tutorial_hud_anim_obj_count = 0

function tutorial_init()

	--Find Objects
	Tutorial.handles = {}
	Tutorial.handles.window = vint_object_find("tutorial")
	Tutorial.handles.bg = vint_object_find("background")
	Tutorial.handles.safe_frame = vint_object_find("safe_frame")
	vint_set_property(Tutorial.handles.safe_frame, "visible", false)
	--Text Elements
	Tutorial.handles.footer_grp = vint_object_find("footer_grp")
	Tutorial.handles.header_text = vint_object_find("tutorial_header_text")
	Tutorial.handles.body_text = vint_object_find("tutorial_body_text")
	Tutorial.handles.footer_text = vint_object_find("tutorial_footer_text")

	--Frame Elements
	Tutorial.handles.side_l = vint_object_find("tutorial_frame_brdr_l")
	Tutorial.handles.side_r = vint_object_find("tutorial_frame_brdr_r")
	Tutorial.handles.middle = vint_object_find("menu_frame_middle")
	Tutorial.handles.bottom = vint_object_find("menu_bottom")


	--Highlight stuff
	Tutorial.handles.arrow = vint_object_find("arrow")
	--Animations
	vint_set_property(vint_object_find("pulse_glow_anim"), "is_paused", true)

	Tutorial_hud_doc = -1

	Tutorial_hud_prunings.num_elements = 0

	--Alignment Properties
	Tutorial.alignment_settings = {}
	Tutorial.alignment_settings["center"] = { x = 0, y = 0, offset="w", vdoc_name = "align_center" }
	Tutorial.alignment_settings["notoriety"] = { x = 0, y = 0, offset="sw", vdoc_name = "loc_notoriety" }
	Tutorial.alignment_settings["health"] = { x = 0, y = 0, offset="ne", vdoc_name = "loc_health" }
	Tutorial.alignment_settings["follower"] = { x = 0, y = 0, offset="ne", vdoc_name = "loc_follower" }
	Tutorial.alignment_settings["hud_txt"] = { x = 0, y = 0, offset="sw", vdoc_name = "loc_hud_txt" }
	Tutorial.alignment_settings["radial"] = { x = 0, y = 0, offset="e", vdoc_name = "loc_radial" }
	Tutorial.alignment_settings["diversion"] = { x = 0, y = 0, offset="ne", vdoc_name = "loc_div" }

	--Custom Popups/animations
	--HUD_TEXT
	vint_set_property(vint_object_find("help_txt_anim"), "is_paused", true)
	vint_set_property(vint_object_find("case_hud_txt_grp"), "visible", false)

	--Diversions
	vint_set_property(vint_object_find("diversion_anim"), "is_paused", true)
	vint_set_property(vint_object_find("case_div_grp"), "visible", false)

	--Initialize Frame size
	Tutorial.height = 0
	Tutorial.windows = {}
	Tutorial.windows.num_items = 0
	Tutorial.windows.cur_idx = 0
	Tutorial.scaler = vint_get_property(Tutorial.handles.window, "scale")

	--Set default tutorial stuff
	tutorial_alignment_set("center")

	tutorial_frame_resize()

	--hide frame and background
	vint_set_property(Tutorial.handles.window, "alpha", 0)
	vint_set_property(Tutorial.handles.bg, "alpha", 0)

end

function tutorial_open()
	Tutorial_hud_doc = vint_document_find("hud")
--	tutorial_input_subscribe()

	--Populate and show the tutorial window
	vint_dataresponder_request("tutorial_responder", "tutorial_update", 0, 1)
end

function tutorial_close()
	tutorial_input_unsubscribe()

	--Fail safe tohide the misc cases
	tutorial_case_hide()

	--hide frame and background
	vint_set_property(Tutorial.handles.safe_frame, "visible", false)
end

function tutorial_update(tutorial_ready, header_txt, body_txt, tutorial_type)
	tutorial_input_unsubscribe()

	--	We don't have any tutorials left to display so exit.
	if tutorial_ready == false then
		tutorial_close()
		return
	end

	-- If tutorial is disabled and not in Strong Arm Tutorial Mode, pretend the player pushed the Esc key and go to the next tutorial without showing it [nclok1405]
	if not get_is_tutorial() then
		local in_mission = (get_game_play_mode() == "Mission")
		if (Sui_tutorial == 0) or ((Sui_tutorial == 1) and (not in_mission)) then
			vint_dataresponder_request("tutorial_responder", "tutorial_update", 0)
			return
		end
	end

	-- Update the window information
	Tutorial.window = {
		header_txt = header_txt,
		body_txt = body_txt,
		tutorial_type = tutorial_type,
		footer_txt = "TUT_CONTINUE_MSG"
	}

	-- If there are, show them.
	tutorial_show()
end

function tutorial_show()
	--Make a new window
	local tut = Tutorial.window
	tutorial_input_subscribe()


	vint_set_property(Tutorial.handles.safe_frame, "visible", true)
	tutorial_case_show()
	tutorial_update_text(tut.header_txt, tut.body_txt, tut.footer_txt)

	local Tutorial_sound = audio_get_audio_id("SYS_HUD_CONF_SERIOUS")
	audio_play(Tutorial_sound)
end

function tutorial_update_text(header_txt, body_txt, footer_txt)
	--debug_print("header_txt:"..tostring(header_txt))
	--debug_print("body_txt:"..tostring(body_txt))
	--debug_print("footer_txt:"..tostring(footer_txt))

	-- Extend the first tutorial text to include move and camera controls [nclok1405]
	if sui_compare_string(body_txt, "TUT_COMBAT_MELEE_1") then
		body_txt = vint_insert_values_in_string("{0}.\n{1}.\n{2}", {[0] = "HUD_USE_LEFT_STICK_MESSAGE", [1] = "HUD_USE_RIGHT_STICK_MESSAGE", [2] = "TUT_COMBAT_MELEE_1"})
	end
	-- Autosave Warning [nclok1405]
	if sui_compare_string(body_txt, "TUT_AUTOSAVE_GAME") then
		body_txt = vint_insert_values_in_string("{0}\n{1}", {[0] = "TUT_AUTOSAVE_GAME", [1] = "SAVELOAD_SAVE_WARNING"})
	end

	vint_set_property(Tutorial.handles.header_text, "text_tag", header_txt)
	vint_set_property(Tutorial.handles.body_text, "text_tag", body_txt)
	vint_set_property(Tutorial.handles.footer_text, "text_tag", footer_txt)
	tutorial_frame_resize()
end

function tutorial_frame_resize()
	--Resize tutorial frame
	--Update footer vint_get_property(Tutorial.handles.body_text, "screen_size", Tutorial.handles.body_text) --
	local x, y = vint_get_property(Tutorial.handles.body_text, "anchor")
	local width, height = element_get_actual_size(Tutorial.handles.body_text)
	local footer_x, footer_y = vint_get_property(Tutorial.handles.footer_grp, "anchor")
	local footer_y = y + height
	vint_set_property(Tutorial.handles.footer_grp, "anchor", footer_x, footer_y)

	Tutorial.height = footer_y

	--Bottom of frame
	x, y = vint_get_property(Tutorial.handles.bottom, "anchor")
	local bottom_y = footer_y + 26
	vint_set_property(Tutorial.handles.bottom, "anchor", x, bottom_y)

	--Background
	local se_x, se_y
	local source_y = footer_y + 35

	--Left Side of bg
	se_x, se_y = vint_get_property(Tutorial.handles.side_l, "source_se")
	vint_set_property(Tutorial.handles.side_l, "source_se", se_x, source_y )

	--Right Side of BG
	se_x, se_y = vint_get_property(Tutorial.handles.side_r, "source_se")
	vint_set_property(Tutorial.handles.side_r, "source_se", se_x, source_y )
	vint_set_property(Tutorial.handles.side_r, "scale", -1, 1)
	vint_set_property(Tutorial.handles.side_r, "offset", -17, 0)

	--Middle of BG
	se_x, se_y = element_get_actual_size(Tutorial.handles.middle)
	element_set_actual_size(Tutorial.handles.middle, se_x, source_y)

	--Reset Frame positioning relative to alignment
	x = Tutorial.alignment.x
	y = Tutorial.alignment.y
	height = bottom_y * Tutorial.scaler --Bottom_y is our lowest point so lets use that as our base height
	width = 528	* Tutorial.scaler			--Hardcode width for alignment

	if Tutorial.alignment.offset == "w" then
		y = y - (height/2)
		--West/Ceneter
	elseif Tutorial.alignment.offset == "sw" then
		--Southwest
		y = y - height
	elseif Tutorial.alignment.offset == "nw" then
		--Northwest use same values
	elseif Tutorial.alignment.offset == "ne" then
		x = x - width
		y = y
	elseif Tutorial.alignment.offset == "e" then
		x = x - width
		y = y - (height/2)
	end
	vint_set_property(Tutorial.handles.window, "anchor", x, y)
end

function tutorial_cleanup()
end

function tutorial_alignment_set(alignment_string)
	Tutorial.alignment = Tutorial.alignment_settings[alignment_string]
	if Tutorial.alignment == nil then
		--debug_print("vint", "Alignment configuration doesn't exist for tutorial_alignment_set()\nUsing Default alignment 'Center'")
		Tutorial.alignment = Tutorial.alignment_settings["center"]
	else
		local loc_x, loc_y = vint_get_property(vint_object_find(Tutorial.alignment.vdoc_name), "anchor" )
		Tutorial.alignment.x = loc_x
		Tutorial.alignment.y = loc_y
	end
end

function tutorial_input_subscribe()
	if Tutorial.input_subs ~= nil then
		-- already good to go
		return
	end

	--	Subscribe to the input
	Tutorial.input_subs = {
		vint_subscribe_to_input_event(nil, "pause",				"tutorial_input", 50),
		vint_subscribe_to_input_event(nil, "all_unassigned",	"tutorial_input", 50),
	}
end

function tutorial_input(target, event, accelleration)
	--close
	if event == "pause" then

		tutorial_case_hide()

		-- Find out if there are any more tutorials
		vint_dataresponder_request("tutorial_responder", "tutorial_update", 0)
	end
end

function tutorial_input_unsubscribe()
	if Tutorial.input_subs == nil then
		return
	end

	--	Unsubscribe to input
	for idx, val in Tutorial.input_subs do
		vint_unsubscribe_to_input_event(val)
	end
	Tutorial.input_subs = nil
end


--------------------------------------
---SPECIAL CASES
--
function tutorial_case_show()
	if Tutorial_hud_doc == -1 then
		--No hud loaded
		return
	end

	--Show highlight if needed
	if Tutorial_special_cases[Tutorial.window.tutorial_type] ~= nil then
		local tutorial_case = Tutorial_special_cases[Tutorial.window.tutorial_type]
		--show thing
		tutorial_case.show()

		--Reset alignment
		tutorial_alignment_set(tutorial_case.align)

		if tutorial_case.arrow ~= nil then
			--Align arrow to specific point
			local arrow_ref_h =  vint_object_find(tutorial_case.arrow)
			local arrow_x, arrow_y = vint_get_property(arrow_ref_h, "anchor")
			vint_set_property(Tutorial.handles.arrow, "anchor", arrow_x, arrow_y)

			--Set rotation
			local rotation
			if tutorial_case.arrow_rotation == "w" then
				rotation = -3.141592654
			elseif tutorial_case.arrow_rotation == "e" then
				rotation = 0
			elseif tutorial_case.arrow_rotation == "s" then
				rotation = 1.570796327
			elseif tutorial_case.arrow_rotation == "n" then
				rotation = -1.570796327
			end
			vint_set_property(Tutorial.handles.arrow, "rotation", rotation)

			--Show
			vint_set_property(Tutorial.handles.arrow, "visible", true)
		else
			vint_set_property(Tutorial.handles.arrow, "visible", false)
		end
	else
		vint_set_property(Tutorial.handles.arrow, "visible", false)
		tutorial_alignment_set("center")
	end
end

function tutorial_case_hide()
	if Tutorial_hud_doc == -1 then
		--No hud loaded
		return
	end

	--Clean up pruned objects
	for i = 0, Tutorial_hud_prunings.num_elements - 1 do
		if Tutorial.window.tutorial_type ~= 74 then
			--only reset the visibility if the item is not the radial menu
			vint_set_property(Tutorial_hud_prunings[i].source_h, "visible", Tutorial_hud_prunings[i].source_object_visibility)
		end
		vint_object_destroy(Tutorial_hud_prunings[i].clone_h)
	end

	--Reset Pruning numbers
	Tutorial_hud_prunings = {}
	Tutorial_hud_prunings.num_elements = 0


	--Wipe out all tweens and cloned objects
	for idx, val in Tutorial_hud_anim_cleanup do
		--debug_print("vint", "destroy: " .. val ..  "\n")
		vint_object_destroy(val)
	end
	Tutorial_hud_anim_cleanup = {}


	--Do any special hide functions if they exist
	local tutorial_case = Tutorial_special_cases[Tutorial.window.tutorial_type]
	if tutorial_case ~= nil then
		if tutorial_case.hide ~= nil then
			tutorial_case.hide()
		end
	end

	--Hide any misc shit...
	local hud_txt_grp_h = vint_object_find("case_hud_txt_grp")
	vint_set_property(hud_txt_grp_h, "visible", false)
end

function tutorial_case_prune_hud(target_object_name, target_object_parent, new_parent_obj)
	local source_object_h = vint_object_find(target_object_name, target_object_parent, Tutorial_hud_doc)
	local clone_object_h = vint_object_clone(source_object_h)
	vint_object_set_parent(clone_object_h, new_parent_obj)

	--original state
	local source_object_visibility = vint_get_property(source_object_h, "visible")

	--Hide original part
	vint_set_property(source_object_h, "visible", false)

	Tutorial_hud_prunings[Tutorial_hud_prunings.num_elements] = {clone_h = clone_object_h, source_h = source_object_h, source_object_visibility = source_object_visibility}
	Tutorial_hud_prunings.num_elements = Tutorial_hud_prunings.num_elements + 1
	return clone_object_h
end

function tutorial_case_add_grp(target_object_name, target_object_parent, grp_parent)
	local source_object_h = vint_object_find(target_object_name, target_object_parent, Tutorial_hud_doc)
	local x, y = vint_get_property(source_object_h, "anchor")
	local scale_x, scale_y = vint_get_property(source_object_h, "scale")
	local new_grp_h = vint_object_create("new_grp", "group", grp_parent)
	vint_set_property(new_grp_h, "anchor", x, y)
	vint_set_property(new_grp_h, "scale", scale_x, scale_y)
	return new_grp_h
end

function tutorial_case_highlight_object(target_object_h, do_scale)
	local anim_h = vint_object_find("pulse_glow_anim")
	local clone_anim_h = vint_object_clone(anim_h)
	local twn_1_h = vint_object_find("alpha_twn_1", clone_anim_h)
	local twn_2_h = vint_object_find("scale_twn_1", clone_anim_h)

	--Clone target object and set it to alpha
	local pulse_object_h = vint_object_clone(target_object_h)

	local x, y = vint_get_property(pulse_object_h, "anchor")

	vint_set_property(pulse_object_h, "anchor", x, y)

	vint_set_property(pulse_object_h, "render_mode", "additive_alpha")
	vint_set_property(pulse_object_h, "depth", -1000)

	--retarget_animmams
	vint_set_property(twn_1_h, "target_handle", pulse_object_h)
	vint_set_property(twn_2_h, "target_handle", pulse_object_h)

	if do_scale == false or do_scale == nil then

		--Set pulse to bounce
		vint_set_property(twn_1_h, "loop_mode", "bounce")
		local t = vint_get_property(twn_1_h, "duration")

		--Delete scale tween
		vint_object_destroy(twn_2_h)
	end

	--Store anim
	Tutorial_hud_anim_cleanup[Tutorial_hud_anim_obj_count] = clone_anim_h
	Tutorial_hud_anim_obj_count = Tutorial_hud_anim_obj_count + 1

	--store pulsed object
	Tutorial_hud_anim_cleanup[Tutorial_hud_anim_obj_count] = pulse_object_h
	Tutorial_hud_anim_obj_count = Tutorial_hud_anim_obj_count + 1

	--Play anim
	lua_play_anim(clone_anim_h, 0)
end

function tutorial_case_gang_noto_show()
	local gang_icon_grp = tutorial_case_add_grp("map_grp", nil, Tutorial.handles.safe_frame)
	local icon_1_h = tutorial_case_prune_hud("gang_noto_icon_1", nil, gang_icon_grp)
	local icon_2_h = tutorial_case_prune_hud("gang_noto_icon_2", nil, gang_icon_grp)
	local icon_3_h = tutorial_case_prune_hud("gang_noto_icon_3", nil, gang_icon_grp)
	local icon_4_h = tutorial_case_prune_hud("gang_noto_icon_4", nil, gang_icon_grp)
	local icon_5_h = tutorial_case_prune_hud("gang_noto_icon_5", nil, gang_icon_grp)

	vint_set_property(icon_1_h, "image", "ui_hud_not_brotherhood")
	vint_set_property(icon_2_h, "image", "ui_hud_not_brotherhood")
	vint_set_property(icon_3_h, "image", "ui_hud_not_brotherhood")
	vint_set_property(icon_4_h, "image", "ui_hud_not_brotherhood")
	vint_set_property(icon_5_h, "image", "ui_hud_not_brotherhood")
	vint_set_property(icon_1_h, "visible", true)
	vint_set_property(icon_2_h, "visible", true)
	vint_set_property(icon_3_h, "visible", true)
	vint_set_property(icon_4_h, "visible", true)
	vint_set_property(icon_5_h, "visible", true)
	vint_set_property(icon_1_h, "alpha", 1)
	vint_set_property(icon_2_h, "alpha", 1)
	vint_set_property(icon_3_h, "alpha", 1)
	vint_set_property(icon_4_h, "alpha", 1)
	vint_set_property(icon_5_h, "alpha", 1)

	tutorial_case_highlight_object(icon_1_h, true)
	tutorial_case_highlight_object(icon_2_h, true)
	tutorial_case_highlight_object(icon_3_h, true)
	tutorial_case_highlight_object(icon_4_h, true)
	tutorial_case_highlight_object(icon_5_h, true)
end

function tutorial_case_cop_noto_show()
	--debug_print("vint", "show_cop\n")
	local gang_icon_grp = tutorial_case_add_grp("map_grp", nil, Tutorial.handles.safe_frame)
	local icon_1_h = tutorial_case_prune_hud("police_noto_icon_1", nil, gang_icon_grp)
	local icon_2_h = tutorial_case_prune_hud("police_noto_icon_2", nil, gang_icon_grp)
	local icon_3_h = tutorial_case_prune_hud("police_noto_icon_3", nil, gang_icon_grp)
	local icon_4_h = tutorial_case_prune_hud("police_noto_icon_4", nil, gang_icon_grp)
	local icon_5_h = tutorial_case_prune_hud("police_noto_icon_5", nil, gang_icon_grp)

	vint_set_property(icon_1_h, "visible", true)
	vint_set_property(icon_2_h, "visible", true)
	vint_set_property(icon_3_h, "visible", true)
	vint_set_property(icon_4_h, "visible", true)
	vint_set_property(icon_5_h, "visible", true)
	vint_set_property(icon_1_h, "alpha", 1)
	vint_set_property(icon_2_h, "alpha", 1)
	vint_set_property(icon_3_h, "alpha", 1)
	vint_set_property(icon_4_h, "alpha", 1)
	vint_set_property(icon_5_h, "alpha", 1)

	tutorial_case_highlight_object(icon_1_h, true)
	tutorial_case_highlight_object(icon_2_h, true)
	tutorial_case_highlight_object(icon_3_h, true)
	tutorial_case_highlight_object(icon_4_h, true)
	tutorial_case_highlight_object(icon_5_h, true)
end

function tutorial_case_respect_show()
	--debug_print("vint", "show_cop\n")
	local respect_grp = tutorial_case_add_grp("health_grp", nil, Tutorial.handles.safe_frame)

	local bar_bg_h = tutorial_case_prune_hud("respect_bar_bg", nil, respect_grp)
	local bar_fill_1_h = tutorial_case_prune_hud("respect_bar_fill_0", nil, respect_grp)
	local bar_fill_2_h = tutorial_case_prune_hud("respect_bar_fill_1", nil, respect_grp)
	local respect_count_grp = tutorial_case_prune_hud("respect_count_grp", nil, respect_grp)
	local respect_count_txt = vint_object_find("respect_count_txt",respect_count_grp)

	vint_set_property(bar_bg_h, "alpha", 1)
	vint_set_property(bar_fill_1_h, "alpha", 1)
	vint_set_property(bar_fill_2_h, "alpha", 1)
	vint_set_property(respect_count_grp, "alpha", 1)
	vint_set_property(bar_bg_h, "alpha", 1)
	vint_set_property(bar_fill_1_h, "alpha", 1)
	vint_set_property(bar_fill_2_h, "alpha", 1)
	vint_set_property(respect_count_grp, "alpha", 1)

	--Set angles
	vint_set_property(bar_bg_h, "start_angle", 0.491725)
	vint_set_property(bar_bg_h, "end_angle", 3.1715)

	vint_set_property(bar_fill_1_h, "start_angle",  0.491725)
	vint_set_property(bar_fill_1_h, "end_angle", 3.1365)
	vint_set_property(bar_fill_1_h, "start_angle",  0.491725)
	vint_set_property(bar_fill_1_h, "end_angle", 3.1365)

	vint_set_property(respect_count_grp, "rotation", 3.83172)
	vint_set_property(respect_count_txt, "rotation",  2.44828)
	vint_set_property(respect_count_txt, "text_tag", "x2")
	vint_set_property(respect_count_txt, "visible", true)

	tutorial_case_highlight_object(bar_bg_h, false)
	tutorial_case_highlight_object(bar_fill_1_h, false)
	tutorial_case_highlight_object(bar_fill_2_h, false)
	tutorial_case_highlight_object(respect_count_txt, true)
end

function tutorial_case_health_show()
	local health_grp = tutorial_case_add_grp("health_grp", nil, Tutorial.handles.safe_frame)

	local h_bar_bg_h 		= tutorial_case_prune_hud("health_bar_bg", nil, health_grp)
	local h_bar_fill_1_h = tutorial_case_prune_hud("health_bar_fill_0", nil, health_grp)
	local h_bar_fill_2_h = tutorial_case_prune_hud("health_bar_fill_2", nil, health_grp)
	local s_bar_bg_h 		= tutorial_case_prune_hud("sprint_bar_bg", nil, health_grp)
	local s_bar_fill_1_h = tutorial_case_prune_hud("sprint_bar_fill_0", nil, health_grp)
	local s_bar_fill_2_h = tutorial_case_prune_hud("sprint_bar_fill_2", nil, health_grp)

	vint_set_property(h_bar_bg_h, "alpha", 1)
	vint_set_property(h_bar_fill_1_h, "alpha", 1)
	vint_set_property(h_bar_fill_2_h, "alpha", 1)
	vint_set_property(s_bar_bg_h, "alpha", 1)
	vint_set_property(s_bar_fill_1_h, "alpha", 1)
	vint_set_property(s_bar_fill_2_h, "alpha", 1)


	--Angles (Health)
	vint_set_property(h_bar_bg_h, "start_angle", 3.1265)
	vint_set_property(h_bar_bg_h, "end_angle", 6.298)
	vint_set_property(h_bar_fill_1_h, "start_angle", 3.1715)
	vint_set_property(h_bar_fill_1_h, "end_angle", 6.253)
	vint_set_property(h_bar_fill_2_h, "start_angle", 3.1715)
	vint_set_property(h_bar_fill_2_h, "end_angle", 6.253)

	--Angles (Sprint)
	vint_set_property(s_bar_bg_h, "start_angle", 3.1265)
	vint_set_property(s_bar_bg_h, "end_angle", 6.298)
	vint_set_property(s_bar_fill_1_h, "start_angle", 3.1715)
	vint_set_property(s_bar_fill_1_h, "end_angle", 6.253)
	vint_set_property(s_bar_fill_2_h, "start_angle", 3.1715)
	vint_set_property(s_bar_fill_2_h, "end_angle", 6.253)

	tutorial_case_highlight_object(h_bar_fill_1_h, false)
	tutorial_case_highlight_object(h_bar_fill_2_h, false)
	tutorial_case_highlight_object(s_bar_fill_1_h, false)
	tutorial_case_highlight_object(s_bar_fill_2_h, true)
end


function tutorial_case_followers_show()
	local followers_grp_h	 = tutorial_case_add_grp("followers", nil, Tutorial.handles.safe_frame)
	local follower_h 			 = tutorial_case_prune_hud("follower_grp_1", nil, followers_grp_h)

	--Clone anim
	local anim_h = vint_object_find("follow_anim_0", nil, Tutorial_hud_doc)
	local anim_clone_h = vint_object_clone(anim_h)

	local tutorial_doc = vint_document_find("tutorial")
	local root_anim = vint_object_find("root_animation", nil, tutorial_doc)
	vint_object_set_parent(anim_clone_h, root_anim)
	vint_set_property(anim_clone_h, "target_handle", follower_h)
	lua_play_anim(anim_clone_h, 0)

	local health_fill_h = vint_object_find("follower_health_fill")
	vint_set_property(health_fill_h, "start_angle", 1.57)
	vint_set_property(health_fill_h, "end_angle", 3.147)

	--setup callback for after thing animates in
	local twn_h = vint_object_find("follow_h_fill_alpha_tween_0")
	vint_set_property(twn_h, "end_event", "tutorial_case_followers_show_2")
end

function tutorial_case_followers_show_2()
	local follower_h = vint_object_find("follower_grp_1")
	tutorial_case_highlight_object(follower_h, true)
end

function tutorial_case_map_show()
	local game_map_h = tutorial_case_prune_hud("map_grp", nil, Tutorial.handles.safe_frame)
end

function tutorial_case_hud_text_show()
	local anim_h = vint_object_find("help_txt_anim")
	local hud_txt_grp_h = vint_object_find("case_hud_txt_grp")
	vint_set_property(hud_txt_grp_h, "visible", true)

	--set callback for looping
	local cb_twn_h = vint_object_find("hlp_line_3_alpha_twn_2", anim_h )
	vint_set_property(cb_twn_h, "end_event", "tutorial_case_hud_text_show")

	--Set text for exploration...
	local hlp_line_3_h = vint_object_find("hlp_line_3", hud_txt_grp_h)
	vint_set_property(hlp_line_3_h, "text_tag", "TUT_DIVERSION_EXPLORATION_HOOD")

	lua_play_anim(anim_h, 0)

end

function tutorial_case_hud_text_hide()
	local anim_h = vint_object_find("help_txt_anim")
	local hud_txt_grp_h = vint_object_find("case_hud_txt_grp")
	vint_set_property(anim_h, "is_paused", true)
	vint_set_property(hud_txt_grp_h, "visible", false)
end


Tutorial_radial_case = {}	--Global Table to highlight parts of the radial menu

function tutorial_case_radial_show()
	--Update the stick text for the radial menu
	vint_set_property(Hud_radial_menu.stick_text_h, "text_tag", get_control_stick_text())
	local radial_h = tutorial_case_prune_hud("radial_grp", nil, Tutorial.handles.safe_frame)

	--Hide popup text
	local desc_h = vint_object_find("slot_description")
	vint_set_property(desc_h, "visible", false)

	--Show base radial group because it may have been hidden
	vint_set_property(radial_h, "visible", true)

	--Clone animation and Slot select anim
	local slot_select_h = vint_object_find("slot_select", radial_h)
	local anim_h = vint_object_find("radial_select_glow", nil, Tutorial_hud_doc)
	local anim_clone_h = vint_object_clone(anim_h)
	local tutorial_doc = vint_document_find("tutorial")
	local root_anim = vint_object_find("root_animation", nil, tutorial_doc)

	vint_object_set_parent(anim_clone_h, root_anim)
	vint_set_property(anim_clone_h, "target_handle", slot_select_h)
	lua_play_anim(anim_clone_h, 0)

	--Set weapons...
	local slot_icons = {
		[0] = "ui_hud_inv_w_fist",
		[1] = "ui_hud_inv_w_nitestick",
		[2] = "ui_hud_inv_w_beretta",
		[3] = "ui_hud_inv_w_tek9",
		[4] = "ui_hud_inv_w_shotgun",
		[5] = "ui_hud_inv_w_m32",
		[6] = "ui_hud_inv_w_rpg",
		[7] = "ui_hud_inv_w_grenade",
	}

	local slot_bmp_1_h, slot_bmp_2_h, slot_h, dual_wield_h

	for i = 0, 7 do
		local image_name = slot_icons[i]
		local slot_h = vint_object_find("slot_" .. i, radial_h)
		local dual_wield_h = vint_object_find("inv_dual_wield_tmp", slot_h)
		local slot_bmp_1_h = vint_object_find("inv_icon_tmp", slot_h)

		if dual_wield_h ~= 0 then
			--Dual weild for whatever reason! Cheats??
			local slot_bmp_1_h = vint_object_find("inv_icon_0", dual_wield_h)
			local slot_bmp_2_h = vint_object_find("inv_icon_1", dual_wield_h)
			vint_set_property(slot_bmp_1_h, "image", image_name)
			vint_set_property(slot_bmp_1_h, "image", image_name)
			vint_set_property(dual_wield_h, "anchor", 0,0)
			vint_set_property(dual_wield_h, "scale", .75,.75)
		elseif  slot_bmp_1_h ~= 0 then
			--Single
			vint_set_property(slot_bmp_1_h, "image", image_name)
			vint_set_property(slot_bmp_1_h, "anchor", 0,0)
			vint_set_property(slot_bmp_1_h, "scale", .75,.75)
		else
			--Need to build icon regardless
			local inv_h = vint_object_find("inv_icon_tmp")
			local item_element_h = vint_object_clone(inv_h, slot_h)
			vint_set_property(item_element_h, "image", image_name)
			vint_set_property(item_element_h, "anchor", 0,0)
			vint_set_property(item_element_h, "scale", .75,.75)
		end
		Tutorial_radial_case[i] = slot_h
	end
	Tutorial_radial_case.num_positions = 8
	Tutorial_radial_case.cur_idx = 8
	Tutorial_radial_case.slot_select_h = slot_select_h
	Tutorial_radial_case.stick_h = vint_object_find("stick_grp", radial_h)

	Tutorial_radial_case.stick_positions = {
		[0] = {x = 0, y = -12},
		[1] = {x = 6, y = -6},
		[2] = {x = 12, y = 0},
		[3] = {x = 6, y = 6},
		[4] = {x = 0, y = 12},
		[5] = {x = -6, y = 6},
		[6] = {x = -12, y = 0},
		[7] = {x = -6, y = -6},
	}

	local anim_h = vint_object_find("radial_action_anim_1")
	lua_play_anim(anim_h, 0)

	local twn_h  = vint_object_find("radial_action_twn_1")
	vint_set_property(twn_h, "end_event", "tutorial_case_radial_loop_event")
	tutorial_case_radial_loop_event()
end

function tutorial_case_radial_loop_event()
	if Tutorial_radial_case.cur_idx >= Tutorial_radial_case.num_positions then
		Tutorial_radial_case.cur_idx = 0
	end

	--Move Highlight
	local target_slot_h = Tutorial_radial_case[Tutorial_radial_case.cur_idx]
	local x, y = vint_get_property(target_slot_h, "anchor")
	vint_set_property(Tutorial_radial_case.slot_select_h, "anchor", x, y)

	--Move Stick
	x = Tutorial_radial_case.stick_positions[Tutorial_radial_case.cur_idx].x
	y = Tutorial_radial_case.stick_positions[Tutorial_radial_case.cur_idx].y
	vint_set_property(Tutorial_radial_case.stick_h, "anchor", x, y)

	--Increment Radial Position
	Tutorial_radial_case.cur_idx = Tutorial_radial_case.cur_idx + 1

	--Retrigger Animation
	local anim_h = vint_object_find("radial_action_anim_1")
	lua_play_anim(anim_h, 0)
end

function tutorial_case_radial_hide()
	local anim_h = vint_object_find("radial_action_anim_1")
	vint_set_property(anim_h, "is_paused", true)
end

function tutorial_case_div_shoot_show()
	local div_grp = vint_object_find("case_div_grp")
	local div_stunt_text_h = vint_object_find("div_stunt", div_grp)
	vint_set_property(div_stunt_text_h, "text_tag", "DIVERSION_COMBAT_TRICKS_GANG_KILL")
	tutorial_case_div_start()
end

function tutorial_case_div_driving_show()
local div_grp = vint_object_find("case_div_grp")
	local div_stunt_text_h = vint_object_find("div_stunt", div_grp)
	vint_set_property(div_stunt_text_h, "text_tag", "DIVERSION_STUNT_JUMPING")
	tutorial_case_div_start()
end

function tutorial_case_div_start()

	--Show Grp
	local div_grp = vint_object_find("case_div_grp")
	vint_set_property(div_grp, "visible", true)

	--Align stars to text
	local div_stunt_text_h = vint_object_find("div_stunt", div_grp)
	local stars_h = vint_object_find("stars", div_grp)
	local width, height = element_get_actual_size(div_stunt_text_h)

	local x, y = vint_get_property(stars_h, "anchor")
	vint_set_property(stars_h, "anchor", 0 - width - 10, y)

	--Play Animation
	local anim_h = vint_object_find("diversion_anim")
	lua_play_anim(anim_h, 0)

	--Callback for looping animation
	local twn_h = vint_object_find("div_respect_count_alpha_twn_3")
	vint_set_property(twn_h, "end_event", "tutorial_case_div_loop_event")
end

function tutorial_case_div_hide()
	local anim_h = vint_object_find("diversion_anim")
	local div_grp = vint_object_find("case_div_grp")
	vint_set_property(anim_h, "is_paused", true)
	vint_set_property(div_grp, "visible", false)
end

function tutorial_case_div_loop_event()
	--Play Animation
	local anim_h = vint_object_find("diversion_anim")
	lua_play_anim(anim_h, 0)
end


Tutorial_special_cases = {
	--Gang Notoriety
	[2] = {show = tutorial_case_gang_noto_show, align = "notoriety", arrow = "arrow_gang", arrow_rotation = "w"},
	--Cop Notoriety
	[3] = {show = tutorial_case_cop_noto_show, align = "notoriety", arrow = "arrow_cop", arrow_rotation = "w"},

	--Combat Weapons(Radial Menu)
	[74] = {show = tutorial_case_radial_show, hide = tutorial_case_radial_hide, align = "radial", arrow = "arrow_radial", arrow_rotation = "e"},

	--Diversion Driving
	[79] = {show = tutorial_case_div_driving_show, hide = tutorial_case_div_hide, align = "diversion", arrow = "arrow_div", arrow_rotation = "n"},

	--Diverison Shooting
	[80] = {show = tutorial_case_div_shoot_show, hide = tutorial_case_div_hide, align = "diversion", arrow = "arrow_div", arrow_rotation = "n"},

	--Respect
	[89] = {show = tutorial_case_respect_show, align = "health", arrow = "arrow_respect", arrow_rotation = "e"},

	--Health/Sprint Meter
	[90] = {show = tutorial_case_health_show, align = "health", arrow = "arrow_health", arrow_rotation = "e"},

	--Map
	[92] = {show = tutorial_case_map_show, align = "notoriety", arrow = "arrow_minimap", arrow_rotation = "w"},

	--Followers
	[93] = {show = tutorial_case_followers_show, align = "follower", arrow = "arrow_follower", arrow_rotation = "e"},

	--Diversion Standard
	[94] = {show = tutorial_case_div_driving_show, hide = tutorial_case_div_hide,  align = "diversion", arrow = "arrow_div", arrow_rotation = "n"},

	--Hud Text
	[95] = {show = tutorial_case_hud_text_show, hide = tutorial_case_hud_text_hide, align = "hud_txt", arrow = "arrow_hud_txt", arrow_rotation = "s"},
}
