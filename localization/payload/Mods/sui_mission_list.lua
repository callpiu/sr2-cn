-- sui_mission_list.lua: Mod Mission List file, part of SuperUI mod by [nclok1405]
-- This file is loaded by mission_replay.lua for showing Mod Mission list.

-- List of Mod Missions
MOD_MISSION_LIST = {
	{
		internal_name = "mm_evilgat",			-- Internal Mission ID, must match with "sr2_city_missions.xtbl"
		display_name = "Evil Gat Clones",	-- Displayed Mission Name
		author = "nclok1405",			-- Mission Author Name
		description = "[format][color:red]Evil clones of Johnny Gat[/format] have been spotted at [format][color:teal]an old bar[/format]. Stop them.",	-- Mission Briefing
	},
	{
		internal_name = "mm_benchmark_sr",
		display_name = "Benchmark",
		author = "nclok1405, Brendan Hanna Holloway",
		description = "You can check the game's performance by using this test.",
	},
	{
		internal_name = "mm_triangulate",
		display_name = "Triangulate",
		author = "nclok1405, 452",
		description = "Display player's coordinates. Press {PREV_RADIO_IMG} to show Y position, or {NEXT_RADIO_IMG} to record all 3 components to the objective list.",
	},
	-- Add more missions here...

}

--[[

To make your custom missions loadable by the game, you must also make changes to "sr2_city_missions.xtbl".

Any new missions MUST be added AFTER the "mm_evilgat" mission.
Do NOT add any new missions before or middle of the vanilla missions!
Doing so will mess up the "Last Mission Played" display of Save/Load screens!

Let me explain about a mission definition in the "sr2_city_missions.xtbl" file...

	<Mission>
		<Name>mm_evilgat</Name> <- [!] Internal ID of the mission. Must match with your Lua filename but without ".lua" at the end.
		<Type>Stronghold</Type> <- Must be a Stronghold so your mission do not mess "Last Mission Played" status.
		<Team>Playas</Team> <- Mission icon and end screen background. Can be "Playas", "Brotherhood", "Ronin", "Samedi", or "Ultor".
		<Flags>
			<Flag>No Percentage Count</Flag> <- Must have this to prevent this mission from messing Game Complete Percentage.
			</Flags>
		<MissionStronghold>
			<display_group>none</display_group> <- Must be "none" to prevent this mission from appearing in a wrong category.
			<Cost>0</Cost> <- Respect requied to start this mission. Not used when playing a mission from a Clipboard so it should be 0.
			<Start>mm_evilgat_start</Start> <- [!] Mission's main function name. Should be named like "{Internal_ID}_start".
			<Cleanup>mm_evilgat_cleanup</Cleanup> <- [!] Mission's cleanup function name. Should be named like "{Internal_ID}_cleanup".
			<Success>mm_evilgat_success</Success> <- [!] Mission's success function name. Should be named like "{Internal_ID}_success".
			<Rewards> <- Mod Missions cannot have rewards because it is played as a "Mission Replay", so leave them empty.
				<Unlockables></Unlockables>
				</Rewards>
			<Prerequisites></Prerequisites> <- Prerequisites of unlocking this mission. Leave this empty.
			</MissionStronghold>
		<_Editor>
			<Category>zzzzz_OTHER_zzzzz</Category> <- Not used by the game but I recommend leaving it "zzzzz_OTHER_zzzzz" to make a mod mission stand out from vanilla mission difinitions.
			</_Editor>
		</Mission>

In short, you will need to...
* Change the <Name> to your mission's filename without a ".lua" at the end
* Change the prefix of <Start>, <Cleanup>, and <Success> function names

--]]
