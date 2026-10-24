-- mm_benchmark_sr.lua: Benchmark [nclok1405]
-- Based on "fr_checkSR.lua"

BENCHMARK_PLAY_EFFECTS = true			-- Play fire effects
BENCKMARK_RUN_CONTINUOUSLY = false		-- Run endlessly

-- Groups --
GROUP1 = "mm_benchmark_sr_$npc_group"
GROUP2 = "mm_benchmark_sr_$vehicle_group"
PASSENGER_GROUP1 = {"mm_benchmark_sr_$human_6"}
PASSENGER_GROUP2 = {"mm_benchmark_sr_$human_7"}
PASSENGER_GROUP3 = {"mm_benchmark_sr_$human_8"}
PASSENGER_GROUP4 = {"mm_benchmark_sr_$human_9"}
PASSENGER_GROUP5 = {"mm_benchmark_sr_$human_10"}
PASSENGER_GROUP6 = {"mm_benchmark_sr_$human_11"}

-- Variables
BenchmarkTimedOut = false
BenchmarkTotalTime = 0
BenchmarkTotalFrames = 0
BenchmarkMaxFrameTime = 0
BenchmarkThreadHandle = -1
BenchmarkEffectHandles = {}

-- Main Mission Function --
function mm_benchmark_sr_start(checkpoint, is_restart)
	-- Start trigger is hit... the activate button was hit
	set_mission_author("Mod by nclok1405, original by Brendan Hanna Holloway")

	-- Try to clear on-screen messages
	mission_help_clear()

	-- Fade Out
	mission_start_fade_out()

	-- Hide Players
	character_hide(LOCAL_PLAYER)
	if coop_is_active() then
		character_hide(REMOTE_PLAYER)
	end

	-- Disable Spawning
	spawning_vehicles(false)
	spawning_pedestrians(false)
	action_nodes_enable(false)
	ambient_cop_spawn_enable(false)
	spawning_allow_cop_ambient_spawns(false)
	ambient_gang_spawn_enable(false)
	spawning_allow_gang_ambient_spawns(false)

	-- Lock Notoriety to Zero
	notoriety_set("Police",0)
	notoriety_set_min("Police", 0)
	notoriety_set_max("Police", 0)
	notoriety_set("Samedi",0)
	notoriety_set_min("Samedi", 0)
	notoriety_set_max("Samedi", 0)
	notoriety_set("Ronin",0)
	notoriety_set_min("Ronin", 0)
	notoriety_set_max("Ronin", 0)
	notoriety_set("Brotherhood",0)
	notoriety_set_min("Brotherhood", 0)
	notoriety_set_max("Brotherhood", 0)

	-- Set Time to Night (Night always has worse framerate)
	set_time_of_day(0, 0)

	-- Lock Weather
	set_weather(0, true)

	-- Disallow Weapons
	inv_weapon_disable_all_but_this_slot(WEAPON_SLOT_UNARMED)

	-- Teleport Players
	teleport_coop("mm_benchmark_sr_$camera", "mm_benchmark_sr_$camera")

	-- point camera to navpoint
	camera_look_through("mm_benchmark_sr_$camera")

	-- spawn some groups
	group_create(GROUP2, true)
	group_create(GROUP1, true)

	-- place passengers in vehicles
	vehicle_enter_group_teleport(PASSENGER_GROUP1, "mm_benchmark_sr_$vehicle_0")
	vehicle_enter_group_teleport(PASSENGER_GROUP2, "mm_benchmark_sr_$vehicle_1")
	vehicle_enter_group_teleport(PASSENGER_GROUP3, "mm_benchmark_sr_$vehicle_2")
	vehicle_enter_group_teleport(PASSENGER_GROUP4, "mm_benchmark_sr_$vehicle_3")
	vehicle_enter_group_teleport(PASSENGER_GROUP5, "mm_benchmark_sr_$vehicle_4")
	vehicle_enter_group_teleport(PASSENGER_GROUP6, "mm_benchmark_sr_$vehicle_5")

	-- start effects
	if (BENCHMARK_PLAY_EFFECTS) then
		BenchmarkEffectHandles[1] = effect_play("CarDamage-Fire", "mm_benchmark_sr_$vehicle_nav_1", true)
		BenchmarkEffectHandles[2] = effect_play("CarDamage-Fire", "mm_benchmark_sr_$vehicle_nav_2", true)
		BenchmarkEffectHandles[3] = effect_play("CarDamage-Fire", "mm_benchmark_sr_$vehicle_nav_3", true)
		BenchmarkEffectHandles[4] = effect_play("CarDamage-Fire", "mm_benchmark_sr_$vehicle_nav_4", true)
		BenchmarkEffectHandles[5] = effect_play("CarDamage-Fire", "mm_benchmark_sr_$vehicle_nav_5", true)
	end

	-- Make sure players are still hidden
	character_hide(LOCAL_PLAYER)
	if coop_is_active() then
		character_hide(REMOTE_PLAYER)
	end

	mission_start_fade_in()
	-- Fade In

	-- Start Benchmark Thread
	BenchmarkThreadHandle = thread_new("mm_benchmark_sr_benchmark_thread_function")

	if (BENCKMARK_RUN_CONTINUOUSLY) then
		while (true) do
			thread_yield()
		end
	else
		-- Start Timer
		BenchmarkTimedOut = false
		hud_timer_set(0, 30*1000, "mm_benchmark_sr_timeout")

		-- Wait until timeout
		while not BenchmarkTimedOut do
			thread_yield()
		end

 		-- Clear Timer
 		hud_timer_stop(0)
	end

	-- Display Final Result
	local a = BenchmarkTotalTime/BenchmarkTotalFrames
	local fps = BenchmarkTotalFrames/BenchmarkTotalTime
	objective_text(1, "", "Average: "..tostring(a), "", SYNC_ALL)
	objective_text(0, "", "FPS: "..tostring(fps), "", SYNC_ALL)
	mission_help_table("Average Frame Time: "..tostring(a).."\nMax Frame Time: "..tostring(BenchmarkMaxFrameTime).."\nTotal Frames: "..tostring(BenchmarkTotalFrames).."\nFPS: "..tostring(fps))
	delay(10)

	-- end the mission
	mission_end_success("mm_benchmark_sr")
end

-- Benchmark Thread
function mm_benchmark_sr_benchmark_thread_function()
	local update_frame = 0
	BenchmarkTotalTime = 0
	BenchmarkTotalFrames = 0
	BenchmarkMaxFrameTime = 0

	while not BenchmarkTimedOut do
		local f = get_frame_time()

		BenchmarkTotalTime = BenchmarkTotalTime + f
		BenchmarkTotalFrames = BenchmarkTotalFrames + 1
		update_frame = update_frame + 1

		if f > BenchmarkMaxFrameTime then
			BenchmarkMaxFrameTime = f
		end

		if update_frame >= 4 then
			-- Show FPS for every 4 frames
			local fps = BenchmarkTotalFrames/BenchmarkTotalTime
			objective_text(0, "", "FPS: "..fps, "", SYNC_ALL)
			update_frame = 0
		end

		thread_yield()
	end
end

function mm_benchmark_sr_timeout()
	BenchmarkTimedOut = true
end

function mm_benchmark_sr_success()
	-- Called when the mission has ended with success
end

function mm_benchmark_sr_cleanup()
	-- Kill Thread
	if BenchmarkThreadHandle ~= -1 then
		thread_kill(BenchmarkThreadHandle)
		BenchmarkThreadHandle = -1
	end

	-- stop effects
	if (BENCHMARK_PLAY_EFFECTS) then
		effect_stop(BenchmarkEffectHandles[1])
		effect_stop(BenchmarkEffectHandles[2])
		effect_stop(BenchmarkEffectHandles[3])
		effect_stop(BenchmarkEffectHandles[4])
		effect_stop(BenchmarkEffectHandles[5])
	end

	-- Cleanup the HUD
	hud_timer_stop(0)
	objective_text_clear(0)
	objective_text_clear(1)

	-- despawn groups
	group_destroy(GROUP1)
	group_destroy(GROUP2)

	-- Show Player
	character_show(LOCAL_PLAYER)
	if coop_is_active() then
		character_show(REMOTE_PLAYER)
	end

	-- Enable Spawning
	spawning_vehicles(true)
	spawning_pedestrians(true)
	action_nodes_enable(true)
	ambient_cop_spawn_enable(true)
	spawning_allow_cop_ambient_spawns(true)
	ambient_gang_spawn_enable(true)
	spawning_allow_gang_ambient_spawns(true)

	-- Enable Notoriety
	notoriety_set_min("Police", 0)
	notoriety_set_max("Police", 5)
	notoriety_set_min("Samedi", 0)
	notoriety_set_max("Samedi", 5)
	notoriety_set_min("Ronin", 0)
	notoriety_set_max("Ronin", 5)
	notoriety_set_min("Brotherhood", 0)
	notoriety_set_max("Brotherhood", 5)

	-- Restore Weather to Normal
	set_weather(-1)

	-- Enable Weapons
	inv_weapon_enable_or_disable_all_slots(true)

	-- Return camera to normal
	camera_end_look_through(true)
end
