-- mm_evilgat.lua: Evil Gat Clones [nclok1405]
-- Mod Mission Example

-- Navpoints
NAVPOINT_LOCAL_START = "mm_evilgat_$Nstart"
NAVPOINT_REMOTE_START = "mm_evilgat_$Ncoop_start"
NAVPOINT_OLDBAR = "mm_evilgat_$Noldbar"

-- Groups
GROUP_COURTESY_CAR = "mm_evilgat_$Gcourtesy_car"
GROUP_COURTESY_CAR_COOP = "mm_evilgat_$Gcourtesy_car_coop"
GROUP_GATS = "mm_evilgat_$Ggats"

-- NPCs
CHARACTERS_GATS = {"mm_evilgat_$Cgat1", "mm_evilgat_$Cgat2", "mm_evilgat_$Cgat3", "mm_evilgat_$Cgat4", "mm_evilgat_$Cgat5"}
CHARACTERS_GATS_COUNT = sizeof_table(CHARACTERS_GATS)

-- Checkpoints
CHECKPOINT_START = MISSION_START_CHECKPOINT
CHECKPOINT_EVILGATS = "CHECKPOINT_EVILGATS"

-- Variables
EvilGatKills = 0

-- Main Mission Function
function mm_evilgat_start(checkpoint, is_restart)
	local cp = checkpoint

	set_mission_author("nclok1405")

	-- Fade Out
	mission_start_fade_out()

	group_create(GROUP_COURTESY_CAR, true)	-- Load the courtesy car
	if coop_is_active() then
		group_create(GROUP_COURTESY_CAR_COOP, true)	-- Load the courtesy car for co-op
	end

	if cp == CHECKPOINT_START then
		-- Teleport players to the start
		teleport_coop(NAVPOINT_LOCAL_START, NAVPOINT_REMOTE_START)
		group_create(GROUP_GATS)			-- Load Evil Gat Clones in background
	elseif cp == CHECKPOINT_EVILGATS then
		group_create(GROUP_GATS, true)		-- Load Evil Gat Clones and block until done
	end

	mission_start_fade_in()
	-- Fade In

	if cp == CHECKPOINT_START then
		-- Guide players to go Sea Roses
		mission_help_table("Go to [format][color:teal]Sea Roses[/format]")

		marker_add_navpoint(NAVPOINT_OLDBAR, MINIMAP_ICON_LOCATION, INGAME_EFFECT_LOCATION, SYNC_ALL)
		mission_waypoint_add(NAVPOINT_OLDBAR, SYNC_ALL)

		while (get_dist_closest_player_to_object(NAVPOINT_OLDBAR) > 5) do
			-- Wait until the players reach the pub
			thread_yield()
		end

		mission_waypoint_remove(SYNC_ALL)
		marker_remove_navpoint(NAVPOINT_OLDBAR, SYNC_ALL)

		mission_set_checkpoint(CHECKPOINT_EVILGATS)
		cp = CHECKPOINT_EVILGATS
	end

	if cp == CHECKPOINT_EVILGATS then
		-- Kill evil gats
		EvilGatKills = 0
		mission_help_table("Kill all [format][color:red]Evil Gat Clones[/format]")

		for index, npc in pairs(CHARACTERS_GATS) do
			if (not character_exists(npc)) or character_is_dead(npc) then
				-- If this Gat is already dead or doesn't exist for some reason, increase the kill count
				EvilGatKills = EvilGatKills + 1
			else
				-- Mark Evil Gats as required kills
				marker_add_npc(npc, MINIMAP_ICON_KILL, INGAME_EFFECT_KILL, SYNC_ALL)
				on_death("mm_evilgat_on_gat_death", npc)
			end
		end

		-- Show Kill Count on HUD
		mm_evilgat_update_gat_kill_hud()

		while (EvilGatKills < CHARACTERS_GATS_COUNT) do
			-- Wait until all Gat clones are dead
			thread_yield()
		end

		objective_text_clear(0)
	end

	-- end the mission
	mission_end_success("mm_evilgat")
end

-- Update Kill Count HUD
function mm_evilgat_update_gat_kill_hud()
	objective_text(0, "bh07_lts_killed", EvilGatKills, CHARACTERS_GATS_COUNT)
end

-- Callback when an Evil Gat is killed
function mm_evilgat_on_gat_death(npc)
	on_death("", npc)
	marker_remove_npc(npc)
	EvilGatKills = EvilGatKills + 1
	mm_evilgat_update_gat_kill_hud()
end

-- Called when the mission ends with a success
function mm_evilgat_success()
end

-- Cleanup
function mm_evilgat_cleanup()
	for index, npc in pairs(CHARACTERS_GATS) do
		on_death("", npc)
	end

	release_to_world(GROUP_GATS)
	release_to_world(GROUP_COURTESY_CAR)
	if coop_is_active() then
		release_to_world(GROUP_COURTESY_CAR_COOP)
	end

	objective_text_clear(0)
	mission_waypoint_remove(SYNC_ALL)
end
