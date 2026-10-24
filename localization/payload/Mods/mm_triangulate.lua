-- mm_triangulate.lua: Triangulate [nclok1405]
-- Special Thanks to 452 for the triangulate code: https://saintsrow.fandom.com/wiki/User_talk:SaintsRow1Fan
triangulate_thread = -1

-- Main Mission Function
function mm_triangulate_start(checkpoint, is_restart)
	local cp = checkpoint

	set_mission_author("nclok1405, 452")
	debug_print("*** TRIANGULATE MISSION START ***\n")

	-- Fade Out
	mission_start_fade_out()

	--if not is_restart then
		--teleport_coop("mm_triangulate_$Ncalc_A", "mm_triangulate_$Ncalc_A")
	--end

	triangulate_thread = thread_new("triangulate")

	mission_start_fade_in()
	-- Fade In
end

-- Called when the mission ends with a success
function mm_triangulate_success()
end

-- Cleanup
function mm_triangulate_cleanup()
	if triangulate_thread ~= -1 then
		thread_kill(triangulate_thread)
		triangulate_thread = -1
	end

	objective_text_clear(0)
	objective_text_clear(1)

	debug_print("*** TRIANGULATE MISSION END ***\n")
end

function triangulate()
	while true do
		thread_yield()

		local calc_dA = get_dist_char_to_nav(LOCAL_PLAYER, "mm_triangulate_$Ncalc_A")
		local calc_dB = get_dist_char_to_nav(LOCAL_PLAYER, "mm_triangulate_$Ncalc_B")
		local calc_dC = get_dist_char_to_nav(LOCAL_PLAYER, "mm_triangulate_$Ncalc_C")
		local calc_dD = get_dist_char_to_nav(LOCAL_PLAYER, "mm_triangulate_$Ncalc_D")
		local calc_X = ((calc_dA * calc_dA) - (calc_dB * calc_dB) + 1000000) / 2000
		local calc_Z = ((calc_dA * calc_dA) - (calc_dC * calc_dC) + 1000000) / 2000
		local calc_Y = ((calc_dA * calc_dA) - (calc_dD * calc_dD) + 1000000) / 2000

		objective_text(1, "", "X: "..tostring(calc_X), "", SYNC_ALL)
		objective_text(0, "", "Z: "..tostring(calc_Z), "", SYNC_ALL)

		if player_button_just_pressed(29) then
			-- prev radio key
			local s = "Y: "..tostring(calc_Y)
			mission_help_table_nag(s)
		end
		if player_button_just_pressed(30) then
			-- next radio key
			local s = "X:"..tostring(calc_X)..", Y:"..tostring(calc_Y)..", Z:"..tostring(calc_Z)
			mission_help_table(s)

			-- Dump current position into Powertools with *.cts format. (Useful for modders)
			s = "$Pos: <"..tostring(calc_X).." "..tostring(calc_Y).." "..tostring(calc_Z)..">\n"
			debug_print(s)
		end
	end
end
