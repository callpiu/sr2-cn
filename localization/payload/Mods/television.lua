-- television.lua: Television (Cutscene Replayer and Zombie Uprising Entrance)
-----------------------
--  CUTSCENE REPLAY  --
-----------------------

-- Activity Cutscene List [nclok1405]
ACTIVITY_CUTSCENES = {
	"Demo_Derby_Arena",
	"CrowdControl_Hotels","Crowd_Control_Suburbs",
	"Drug_Dealing_Hotels","Drug_Airport",
	"Escort_redlight_sykeout","Escort_University",
	"Fight_Club_Prison","Fightclub_Arena",
	"Fuzz_Suburbs_Fame","Fuzz_Projects",
	"InsuranceFraud_Factories","Insurance_Fraud_Museum",
	"Mayhem_NukePlant","Mayhem_UGShantytown_ratings",
	"Septic_Avenger_Suburbs","SepticAvenger_RedLight",
	"Snatch_Chinatown","Snatch_Downtown",
	"Torch_apartments","HumanTorch_Downtown",
	"Heli_For_Hire_Barrio","Heli_For_Hire_Trailerpark",
}

Television_building_menu = 0

----------------------
--	SYSTEM FUNCTIONS --
----------------------

--	Initialize the menu
function television_init()
	television_build_all_menus()

	menu_store_use_hud(false)
	menu_init()

	--Event Tracking
	event_tracking_interface_enter("Crib Television")

	menu_horz_init(Television_horz)

	interface_effect_begin("pause")
end

function television_build_all_menus()
	-- build the menus dynamically
	television_menu_build({"tssp-intro2", "tssp0"}, "HELP_CAT_PROL")
	television_menu_build({"br"}, "GANG_NAME_TB")
	television_menu_build({"ro"}, "GANG_NAME_TR")
	television_menu_build({"ss"}, "GANG_NAME_SOS")
	television_menu_build({"tsse"}, "HELP_CAT_EPI")
	television_menu_build({"bon"}, "MAINMENU_EXTRAS")
	television_menu_build({"activity"}, "INFO_ACTIVITIES_TITLE")	-- Activity Cutscenes [nclok1405]
	television_menu_build({"video_games"}, "Videogames")

	local i = 0

	if Television_menus["tssp-intro2"] ~= nil then
		Television_horz[i] = {
			label = "HELP_CAT_PROL",
			type = MENU_ITEM_TYPE_SUB_MENU,
			sub_menu = Television_menus["tssp-intro2"]
		}

		Television_menus["tssp-intro2"].on_back = television_exit

		i = i + 1
	end

	if Television_menus["br"] ~= nil or Television_menus["ro"] ~= nil or Television_menus["ss"] ~= nil then
		local j = 0
		local gangs_menu = {
			header_label_str = "HELP_CAT_GANGS",
			on_back = television_exit,
		}

		if Television_menus["br"] ~= nil then
			gangs_menu[j] = {
				label = "GANG_NAME_TB",
				type = MENU_ITEM_TYPE_SUB_MENU,
				sub_menu = Television_menus["br"]
			}

			j = j + 1
		end

		if Television_menus["ro"] ~= nil then
			gangs_menu[j] = {
				label = "GANG_NAME_TR",
				type = MENU_ITEM_TYPE_SUB_MENU,
				sub_menu = Television_menus["ro"]
			}

			j = j + 1
		end

		if Television_menus["ss"] ~= nil then
			gangs_menu[j] = {
				label = "GANG_NAME_SOS",
				type = MENU_ITEM_TYPE_SUB_MENU,
				sub_menu = Television_menus["ss"]
			}

			j = j + 1
		end

		gangs_menu.num_items = j

		Television_horz[i] = {
			label = "HELP_CAT_GANGS",
			type = MENU_ITEM_TYPE_SUB_MENU,
			sub_menu = gangs_menu,
		}

		i = i + 1
	end

	if Television_menus["tsse"] ~= nil then
		Television_horz[i] = {
			label = "HELP_CAT_EPI",
			type = MENU_ITEM_TYPE_SUB_MENU,
			sub_menu = Television_menus["tsse"]
		}

		Television_menus["tsse"].on_back = television_exit

		i = i + 1
	end

	if Television_menus["bon"] ~= nil then
		Television_horz[i] = {
			label = "MAINMENU_EXTRAS",
			type = MENU_ITEM_TYPE_SUB_MENU,
			sub_menu = Television_menus["bon"]
		}

		Television_menus["bon"].on_back = television_exit

		i = i + 1
	end

	-- Activity Cutscenes [nclok1405]
	-- Unlocks when at least one gang cutscene is available
	if (Television_menus["activity"] ~= nil) and (Television_menus["br"] ~= nil or Television_menus["ro"] ~= nil or Television_menus["ss"] ~= nil) then
		Television_horz[i] = {
			label = "INFO_ACTIVITIES_TITLE",
			type = MENU_ITEM_TYPE_SUB_MENU,
			sub_menu = Television_menus["activity"]
		}

		Television_menus["activity"].on_back = television_exit

		i = i + 1
	end

	if Television_menus["video_games"] ~= nil then
		Television_horz[i] = {
			label = "Videogames",
			type = MENU_ITEM_TYPE_SUB_MENU,
			sub_menu = Television_menus["video_games"]
		}

		Television_menus["video_games"].on_back = television_exit

		i = i + 1
	end

	Television_horz.num_items = i

	--debug_print("vint", "built "..i.." menus\n")
end

-- Shutdown and cleanup the menu
function television_cleanup()
	interface_effect_end()
end

function television_exit()
	--dialog_box_confirmation("MENU_TITLE_WARNING", "STORE_EXIT_TELEVISION", "television_exit_confirm")
	menu_close(television_exit_final)	-- Exit without dialog [nclok1405]
end

function television_exit_confirm(result, action)
	if action == DIALOG_ACTION_CLOSE and result == 0 then
		menu_close(television_exit_final)
	end
end

function television_exit_final()
	vint_document_unload(vint_document_find("television"))
end

------------------------
-- MENU FUNCTIONALITY --
------------------------

-- support
function television_consume_data(internal_name, display_name, prompt, close_on_activate)
	local item = {
		type = MENU_ITEM_TYPE_SELECTABLE,
		internal_name = internal_name,
		label = display_name,
		close_on_activate = close_on_activate,
		prompt = prompt,
		on_select = television_scene_select,
	}

	local i = Television_building_menu.num_items
	Television_building_menu[i] = item
	Television_building_menu.num_items = i + 1
end

function television_menu_build(menu_name, display_name)

	Television_building_menu = {
		num_items = 0,
		max_height = 503,	-- Default: 375 [nclok1405]
	}

	for k, v in menu_name do
		if (v == "activity") then
			-- Activity Cutscenes [nclok1405]
			for i, activity_name in pairs(ACTIVITY_CUTSCENES) do
				local display_name = activity_name

				-- Fix Heli Assault cutscene names; devs used early name "Heli For Hire" for cutscene titles
				if (activity_name == "Heli_For_Hire_Barrio") then
					display_name = vint_insert_values_in_string("{0} ({1})", {[0] = "ACT_HELI_NAME", [1] = "DISTRICT_BARRIO"})
				elseif (activity_name == "Heli_For_Hire_Trailerpark") then
					display_name = vint_insert_values_in_string("{0} ({1})", {[0] = "ACT_HELI_NAME", [1] = "DISTRICT_TRAILER_PARK"})
				end

				television_consume_data(activity_name, display_name, "THEATER_PLAY_CONFIRM_EXPO", false)
			end
		else
			-- Vanilla Cutscenes
			vint_dataresponder_request("television", "television_consume_data", 0, "list_scenes", v)
		end
	end

	if Television_building_menu.num_items ~= 0 then
		Television_building_menu.header_label_str = display_name
		Television_menus[menu_name[1]] = Television_building_menu
	end

	Television_building_menu = 0

	interface_effect_begin("pause")
end

function television_play_scene(scene_name)
	interface_effect_end()

	local sf = vint_object_find("safe_frame")
	local sf2 = vint_object_find("safe_frame", nil, MENU_BASE_DOC_HANDLE)

	menu_release_input()
	vint_set_property(sf, "visible", false)
	vint_set_property(sf2, "visible", false)
	vint_dataresponder_request("television", "", 0, "start_scene", scene_name)
	vint_set_property(sf, "visible", true)
	vint_set_property(sf2, "visible", true)
	menu_grab_input()
end

function television_game_play_success(s)
	if s == true then
		menu_close(television_exit_final)
	end
end

function television_game_play_start(name)
	vint_dataresponder_request("television", "television_game_play_success", 0, "start_scene", name)
end

function television_replay_response(response, action)
	if action == DIALOG_ACTION_CLOSE and response == DIALOG_RESULT_YES then
		local item = Menu_active[Menu_active.highlighted_item]

		if item.close_on_activate == true then
			thread_new("television_game_play_start", item.internal_name)
		else
			thread_new("television_play_scene", item.internal_name)
		end
	end
end

function television_scene_select()
	local item = Menu_active[Menu_active.highlighted_item]
	--dialog_box_confirmation("MISSION_COOP_REPLAY_PROMPT", item.prompt, "television_replay_response")

	if item.close_on_activate == true then
		-- Zombie Uprising
		dialog_box_confirmation("ACT_ZOMBIE_NAME", item.prompt, "television_replay_response")
	else
		-- Play a Cutscene without dialog [nclok1405]
		thread_new("television_play_scene", item.internal_name)
	end
end

---------------
-- MENU DATA --
---------------

-- all dynamically built
Television_menus = { }

Television_horz = { num_items = 0 }
