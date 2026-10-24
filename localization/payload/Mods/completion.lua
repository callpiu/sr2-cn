-- completion.lua: Mission Complete/Failed Screens
Completion = {
	handles = {},
	pegs = { },
	input = { },
	num_pegs = 0,

	input_block = false,
	num_unlocks = 0,
	cur_unlock = 0,

	a_available = false,
	b_available = false,
	x_available = false,
}

Completion_Gang_Names = {
	[0] = "GANG_SAINTS",
	[1] = "GANG_NAME_TB",
	[2] = "GANG_NAME_TR",
	[3] = "GANG_NAME_SOS",
	-- [4] is police/civilians/etc (unused here)
	-- [5] is police/civilians/etc (unused here)
	[6] = "GANG_ULTOR",
}

Completion_Activity_Images = {
	"demoderby",	-- 0
	"demoderby",	-- 1
	"escort", 		-- 2
	"fightclub",	-- 3
	"insfraud",		-- 4
	"fuzz",			-- 5
	"angel",		-- 6 Guardian angel?
	"humantorch",	-- 7
	"snatch",		-- 8
	"piracy",		-- 9
	"drug",			-- 10
	"crowdcontrol",	-- 11
	"septic",		-- 12
	"zombie",		-- 13
	"racing",		-- 14 Another hmmm?
	"heli",			-- 15
	"mayhem",		-- 16
}

Completion_Gang_Images = {
	[0] = "saints",
	[1] = "bhood",
	[2] = "ronin",
	[3] = "samedi",
	-- [4] is police/civilians/etc (unused here)
	-- [5] is police/civilians/etc (unused here)
	[6] = "ultor",
}
--[[
function Completion_is_coop()
	return true
end
]]
Completion_audio = {
	top_3 = audio_get_audio_id("SYS_COMPLETION_START"),
	top_2 = audio_get_audio_id("SYS_COMPLETION_START_2"),
	cash = audio_get_audio_id("SYS_COMPLETION_CASH"),
	respect = audio_get_audio_id("SYS_COMPLETION_RESPECT"),
	image = audio_get_audio_id("SYS_COMPLETION_OBJECT"),
	text = audio_get_audio_id("SYS_COMPLETION_TEXT"),
	tips = audio_get_audio_id("SYS_COMPLETION_MENU"),
	unlock = audio_get_audio_id("SYS_COMPLETION_UNLOCK"),
	fail = audio_get_audio_id("SYS_COMPLETION_FAIL"),
	cash_count = audio_get_audio_id("SYS_COMPLETION_CASH_COUNT"),
	respect_count = audio_get_audio_id("SYS_COMPLETION_RESPECT_COUNT"),
	cash_hit = audio_get_audio_id("SYS_COMPLETION_CASH_HIT"),
	respect_hit = audio_get_audio_id("SYS_COMPLETION_RESPECT_HIT"),
	respect_end = audio_get_audio_id("SYS_HUD_DIVERSION_COMPLETE"),

}

Completion_respect = {
--this stores the different variables from the activity respect bonus
}

Completion_cash_reward = {
--this stores the one time cash bonus
}

Completion_cash_per_day = {
--this stores the cash earned per day
}

Completion.handles.level_number = -1 --init this for Special Derby check
Completion_allow_to_shut_off_layers = true
Completion_is_last_screen = false
Completion_show_respect_screen = false
Completion.is_respect_screen = false
Completion_is_hood_screen = false
Completion_is_animating = true --used for skipping animations
Completion_force_skip = false --set the init to not force skip
Completion.just_unlocks_really = false


Completion_coop_disconnected = false

COMPLETION_LOAD_DELAY = 2			--Time to wait on all animations to play

COMPLETION_UNLOCK_SPACE = 20

SUCCESS_MISSION 		= 0
SUCCESS_STRONGHOLD 		= 1
SUCCESS_ACTIVITY 		= 2
FAILURE_MISSION 		= 3
FAILURE_STRONGHOLD 		= 4
FAILURE_ACTIVITY 		= 5
JUST_UNLOCKS			= 6
UNLOCK_REWARD 			= 7
SUCCESS_PUSHBACK		= 8

COMPLETION_RADIAN = 3.141

COMPLETION_AUDIO_DELAY = .2

COMPLETION_RESTART							= 0
COMPLETION_RESTART_FROM_CHECKPOINT		= 1
COMPLETION_EXIT								= 2
COMPLETION_CONTINUE							= 3


-- Mission has been failed before reaching a checkpoint, or the co-op partner disconnected
function completion_coop_disconnected()
	Completion_coop_disconnected = true

	if Completion.type == FAILURE_MISSION then
		completion_init_buttons("COMPLETION_RESTART_BEGINNING", nil, "COMPLETION_EXIT_MISSION")
		if Completion.handles.image_base == "tss01" then
			completion_init_buttons("COMPLETION_RESTART_BEGINNING", nil, nil)
		end
	elseif Completion.type == FAILURE_STRONGHOLD then
		if Sui_mod_mission_title ~= "" then
			-- Mod Mission [nclok1405]
			completion_init_buttons("COMPLETION_RESTART_BEGINNING", nil, "COMPLETION_EXIT_MISSION")
		else
			completion_init_buttons("COMPLETION_RETRY_STRONGHOLD", nil, "COMPLETION_EXIT_STRONGHOLD")
		end
	end
end

function completion_load_peg(peg_name)
	peg_load("" .. peg_name)
	Completion.pegs[Completion.num_pegs] = peg_name
	Completion.num_pegs = Completion.num_pegs + 1
end

function completion_unload_pegs()
	for idx, val in Completion.pegs do
		peg_unload(val)
	end

	Completion.num_pegs = 0
end

function completion_finish()
	Sui_player_dead = false	-- Reset player dead flag [nclok1405]
	Completion_finalize_fade()
	vint_document_unload(vint_document_find("completion"))
end

function completion_cleanup()
	peg_unload("ui_c_wall_" .. Completion.handles.wall)
	completion_unload_pegs()
	completion_release_input()
	if Sui_hud_enable == 0 then
		hud_hide(true)
	else
		hud_hide(false)
	end
end

function completion_init()
	local h = -1
	hud_hide(true)

	--safe frame
	Completion.handles.safe_frame = vint_object_find("safe_frame")

	--Cash & Respect
	Completion.handles.cash_respect_h = vint_object_find("cash_respect")
	h = Completion.handles.cash_respect_h
	Completion.handles.cash_t_h = vint_object_find("cash_t", h)
	Completion.handles.cash_v_h = vint_object_find("cash_v", h)
	Completion.handles.respect_t_h = vint_object_find("respect_t", h)
	Completion.handles.respect_v_h = vint_object_find("respect_v", h)
	-- ++ Respect bar sub group ++
	Completion.handles.respect_b_grp_h = vint_object_find("respect_b_grp", h)
	h = Completion.handles.respect_b_grp_h
	Completion.handles.respect_b_0_h = vint_object_find("respect_b_0", h)
	Completion.handles.respect_b_1_h = vint_object_find("respect_b_1", h)
	Completion.handles.respect_b_bg_h = vint_object_find("respect_b_bg", h)
	Completion.handles.respect_multi_grp = vint_object_find("multi_grp")
	h = Completion.handles.respect_multi_grp
	Completion.handles.respect_multiplier = vint_object_find("respect_mult", h)
	-- ++ Style Group ++
	Completion.handles.style_grp = vint_object_find("style_grp")
	h = Completion.handles.style_grp
	Completion.handles.style_txt = vint_object_find("style_txt", h)

	Completion.handles.black_1_h = vint_object_find("black_1")
	Completion.handles.black_2_h = vint_object_find("black_2")

	--Fail message
	Completion.handles.fail_msg_h = vint_object_find("fail_msg")

	--Tips
	Completion.handles.tips_h = vint_object_find("tips")
	h = Completion.handles.tips_h
	Completion.handles.btn_1_h = vint_object_find("btn_1", h)
	Completion.handles.btn_2_h = vint_object_find("btn_2", h)
	Completion.handles.btn_3_h = vint_object_find("btn_3", h)
	Completion.handles.tip_1_h = vint_object_find("tip_1", h)
	Completion.handles.tip_2_h = vint_object_find("tip_2", h)
	Completion.handles.tip_3_h = vint_object_find("tip_3", h)
	--..Waiting
	Completion.handles.waiting = vint_object_find("waiting", h)
	vint_set_property(Completion.handles.waiting, "text_tag", "MP_COMPLETION_WAITING")

	--..Back : Quit to Main Menu
	Completion.handles.quit_to_main	= vint_object_find("quit_to_main")
	h = Completion.handles.quit_to_main
	Completion.handles.quit_to_main_btn = vint_object_find("btn_4", h)
	Completion.handles.quit_to_main_text = vint_object_find("tip_4", h)

	--Top Group of location, name, level
	Completion.handles.top_grp_h = vint_object_find("top_grp")
	h = Completion.handles.top_grp_h
	Completion.handles.top_1_h = vint_object_find("top_1", h)
	Completion.handles.top_2_h = vint_object_find("top_2", h)
	Completion.handles.top_3_h = vint_object_find("top_3", h)

	--Unlockable group
	Completion.handles.unlock_h = vint_object_find("unlock")
	h = Completion.handles.unlock_h
	Completion.handles.t_unlock_h = vint_object_find("t_unlocked", h)
	Completion.handles.thing_desc_h = vint_object_find("thing_desc", h)
	Completion.handles.thing_image_h = vint_object_find("thing_image", h)
	Completion.handles.thing_name_h = vint_object_find("thing_name", h)
	-- ++ Hood Cash and Hoods Owned ++ --
	Completion.handles.hood_cash_t_h = vint_object_find("hood_cash_t", h)
	Completion.handles.hood_cash_v_h = vint_object_find("hood_cash_v", h)
	Completion.handles.hood_owned_t_h = vint_object_find("hood_owned_t", h)
	Completion.handles.hood_owned_v_h = vint_object_find("hood_owned_v", h)

	--Wall
	Completion.handles.wall_h = vint_object_find("wall")

	--Find Animations, pause and store to globals
	Completion.handles.audio_anim = vint_object_find("audio_anim")
	Completion.handles.black_1_anim_h = vint_object_find("black_1_anim")
	Completion.handles.black_2_anim_h = vint_object_find("black_2_anim")
	Completion.handles.cr_cash_fade_in_anim_h = vint_object_find("cr_cash_fade_in")
	Completion.handles.cr_cash_fade_out_anim_h = vint_object_find("cr_cash_fade_out")
	Completion.handles.cr_respect_fade_in_anim_h = vint_object_find("cr_respect_fade_in")
	Completion.handles.cr_respect_fade_out_anim_h = vint_object_find("cr_respect_fade_out")
	Completion.handles.fail_fade_in_anim_h = vint_object_find("fail_fade_in_anim")
	Completion.handles.hood_cash_fade_in_anim_h = vint_object_find("hood_cash_fade_in_anim")
	Completion.handles.hood_cash_fade_out_anim_h = vint_object_find("hood_cash_fade_out_anim")
	Completion.handles.hood_owned_fade_in_anim_h = vint_object_find("hood_owned_fade_in_anim")
	Completion.handles.hood_owned_fade_out_anim_h = vint_object_find("hood_owned_fade_out_anim")
	Completion.handles.news_clip_fade_in_anim_h = vint_object_find("news_clip_fade_in_anim")
	Completion.handles.news_clip_fade_out_anim_h = vint_object_find("news_clip_fade_out_anim")
	Completion.handles.style_grp_anim = vint_object_find("style_grp_anim")
	Completion.handles.style_grp_fade_out_anim = vint_object_find("style_grp_fade_out_anim")
	Completion.handles.tips_fade_in_anim_h = vint_object_find("tips_fade_in_anim")
	Completion.handles.tips_fade_out_anim_h = vint_object_find("tips_fade_out_anim")
	Completion.handles.top_grp_anim_h = vint_object_find("top_grp_anim")
	Completion.handles.top2_grp_anim_h = vint_object_find("top2_grp_anim") --used for Diversion Unlocks
	Completion.handles.top_grp_fade_out_anim_h = vint_object_find("top_grp_fade_out_anim")
	Completion.handles.unlock_fade_in_anim_h = vint_object_find("unlock_fade_in_anim")
	Completion.handles.unlock_fade_out_anim_h = vint_object_find("unlock_fade_out_anim")
	Completion.handles.unlock_desc_fade_in_anim_h = vint_object_find("unlock_desc_fade_in_anim")
	Completion.handles.unlock_desc_fade_out_anim_h = vint_object_find("unlock_desc_fade_out_anim")
	Completion.handles.waiting_anim = vint_object_find("waiting_anim")
	Completion.handles.waiting_fade_in = vint_object_find("waiting_fade_in")
	Completion.handles.waiting_fade_out = vint_object_find("waiting_fade_out")
	Completion.handles.wall_anim_h = vint_object_find("wall_anim")

	local tween_h = vint_object_find("black_2_alpha_in", Completion.handles.black_2_anim_h)
	vint_set_property(tween_h, "end_event", "completion_shut_off_all_layers")

	vint_set_property(Completion.handles.black_1_anim_h, "is_paused", true)
	vint_set_property(Completion.handles.black_2_anim_h, "is_paused", true)
	vint_set_property(Completion.handles.black_3_anim_h, "is_paused", true)
	vint_set_property(Completion.handles.cr_cash_fade_in_anim_h, "is_paused", true)
	vint_set_property(Completion.handles.cr_cash_fade_out_anim_h, "is_paused", true)
	vint_set_property(Completion.handles.cr_respect_fade_in_anim_h, "is_paused", true)
	vint_set_property(Completion.handles.cr_respect_fade_out_anim_h, "is_paused", true)
	vint_set_property(Completion.handles.fail_fade_in_anim_h, "is_paused", true)
	vint_set_property(Completion.handles.hood_cash_fade_in_anim_h, "is_paused", true)
	vint_set_property(Completion.handles.hood_cash_fade_out_anim_h, "is_paused", true)
	vint_set_property(Completion.handles.hood_owned_fade_in_anim_h , "is_paused", true)
	vint_set_property(Completion.handles.hood_owned_fade_out_anim_h, "is_paused", true)
	vint_set_property(Completion.handles.news_clip_fade_in_anim_h, "is_paused", true)
	vint_set_property(Completion.handles.news_clip_fade_out_anim_h, "is_paused", true)
	vint_set_property(Completion.handles.style_grp_anim, "is_paused", true)
	vint_set_property(Completion.handles.style_grp_fade_out_anim, "is_paused", true)
	vint_set_property(Completion.handles.tips_fade_in_anim_h , "is_paused", true)
	vint_set_property(Completion.handles.tips_fade_out_anim_h, "is_paused", true)
	vint_set_property(Completion.handles.top_grp_anim_h , "is_paused", true)
	vint_set_property(Completion.handles.top2_grp_anim_h , "is_paused", true)
	vint_set_property(Completion.handles.top_grp_fade_out_anim_h, "is_paused", true)
	vint_set_property(Completion.handles.unlock_fade_in_anim_h , "is_paused", true)
	vint_set_property(Completion.handles.unlock_fade_out_anim_h , "is_paused", true)
	vint_set_property(Completion.handles.unlock_desc_fade_in_anim_h , "is_paused", true)
	vint_set_property(Completion.handles.unlock_desc_fade_out_anim_h , "is_paused", true)
	vint_set_property(Completion.handles.waiting_anim , "is_paused", true)
	vint_set_property(Completion.handles.waiting_fade_in , "is_paused", true)
	vint_set_property(Completion.handles.waiting_fade_out , "is_paused", true)
	vint_set_property(Completion.handles.wall_anim_h , "is_paused", true)

	--SAFE FRAME screen shake animation
	Completion.handles.screen_shake = vint_object_find("screen_shake")
	vint_set_property(Completion.handles.screen_shake, "is_paused", true)

	--------- Respect Screen
	--handles
	Completion.handles.gangs_grp_h = vint_object_find("gangs_grp")
	local h = Completion.handles.gangs_grp_h
	Completion.handles.st_h = vint_object_find("3st", h)
	Completion.handles.bh_h = vint_object_find("bh", h)
	Completion.handles.ep_h = vint_object_find("ep", h)
	Completion.handles.rn_h = vint_object_find("rn", h)
	Completion.handles.ss_h = vint_object_find("ss", h)
	Completion.handles.you_got_respect_h = vint_object_find("you_got_respect", h)

	--Animations
	Completion.handles.gang_zoom_st_h = vint_object_find("gang_zoom_3st")
	Completion.handles.gang_zoom_bh_h = vint_object_find("gang_zoom_bh")
	Completion.handles.gang_zoom_ep_h = vint_object_find("gang_zoom_ep")
	Completion.handles.gang_zoom_rn_h = vint_object_find("gang_zoom_rn")
	Completion.handles.gang_zoom_ss_h = vint_object_find("gang_zoom_ss")
	Completion.handles.you_got_respect_fade_in_anim_h = vint_object_find("you_got_respect_fade_in_anim")
	local tween_h = vint_object_find("you_got_respect_fade_in", Completion.handles.you_got_respect_fade_in_anim_h)
	vint_set_property(tween_h, "start_event", "completion_text_sound")

--	vint_set_property(tween_h, "end_event", "completion_reward_screen_finished")

	--Pause Animations
	vint_set_property(Completion.handles.gang_zoom_st_h, "is_paused", true)
	vint_set_property(Completion.handles.gang_zoom_bh_h, "is_paused", true)
	vint_set_property(Completion.handles.gang_zoom_ep_h, "is_paused", true)
	vint_set_property(Completion.handles.gang_zoom_rn_h, "is_paused", true)
	vint_set_property(Completion.handles.gang_zoom_ss_h, "is_paused", true)
	vint_set_property(Completion.handles.you_got_respect_fade_in_anim_h, "is_paused", true)
	vint_set_property(Completion.handles.gangs_grp_h, "visible", false)

	--SHAKERS WOOT WOOT
	--the top stuff
		--line 1
		tween_h = vint_object_find("top_1_pos", Completion.handles.top_grp_anim_h)
		vint_set_property(tween_h, "end_event", "completion_screen_shake")


		--line 2
		tween_h = vint_object_find("top_2_pos", Completion.handles.top_grp_anim_h)
		vint_set_property(tween_h, "end_event", "completion_screen_shake")

		--line 3
		tween_h = vint_object_find("top_3_pos", Completion.handles.top_grp_anim_h)
		vint_set_property(tween_h, "end_event", "completion_screen_shake")

	--unlockable animation
		--unlocked
		tween_h = vint_object_find("unlock_1_t_pos", Completion.handles.unlock_fade_in_anim_h)

		--name
		tween_h = vint_object_find("unlock_2_name_pos", Completion.handles.unlock_fade_in_anim_h)
		vint_set_property(tween_h, "end_event", "completion_screen_shake")

		--reward image
		tween_h = vint_object_find("unlock_3_image_pos", Completion.handles.unlock_fade_in_anim_h)
		vint_set_property(tween_h, "end_event", "completion_screen_shake")
		--local tween_h = vint_object_find("unlock_3_image_pos", Completion.handles.unlock_fade_in_anim_h)


	--hood gained / mission cash reward stuff
		--news image
		tween_h = vint_object_find("news_image_scale", Completion.handles.news_clip_fade_in_anim_h)
		vint_set_property(tween_h, "end_event", "completion_screen_shake")


		--cash reward title
		tween_h = vint_object_find("hood_cash_t_pos", Completion.handles.hood_cash_fade_in_anim_h)
		vint_set_property(tween_h, "end_event", "completion_screen_shake")

		--hoods owned title
		tween_h = vint_object_find("hood_owned_t_pos", Completion.handles.hood_owned_fade_in_anim_h)
		vint_set_property(tween_h, "end_event", "completion_screen_shake")

	--cash respect
		--cash title
		tween_h = vint_object_find("cash_t_pos", Completion.handles.cr_cash_fade_in_anim_h)
		vint_set_property(tween_h, "end_event", "completion_screen_shake")

		--respect title
		tween_h = vint_object_find("respect_t_pos", Completion.handles.cr_respect_fade_in_anim_h)
		vint_set_property(tween_h, "end_event", "completion_screen_shake")

		--style bonus
		tween_h = vint_object_find("style_ender", Completion.handles.style_grp_anim)
		vint_set_property(tween_h, "end_event", "completion_screen_shake")

	--gang respect
		--saints
		tween_h = vint_object_find("3st_offset", Completion.handles.gang_zoom_st_h)
		vint_set_property(tween_h, "end_event", "completion_screen_shake")

		--brotherhood
		tween_h = vint_object_find("bh_offset", Completion.handles.gang_zoom_bh_h)
		vint_set_property(tween_h, "end_event", "completion_screen_shake")

		--ronin
		tween_h = vint_object_find("rn_offset", Completion.handles.gang_zoom_rn_h)
		vint_set_property(tween_h, "end_event", "completion_screen_shake")

		--samedi
		tween_h = vint_object_find("ss_offset", Completion.handles.gang_zoom_ss_h)
		vint_set_property(tween_h, "end_event", "completion_screen_shake")

		--ultor
		tween_h = vint_object_find("ep_offset", Completion.handles.gang_zoom_ep_h)
		vint_set_property(tween_h, "end_event", "completion_screen_shake")

	--if this is international, scale and reposition some shit

	if get_language() ~= "US" and get_language() ~= "UK" then
		local x = .84
		local y = .84

		local top_x, top_y = vint_get_property(Completion.handles.top_grp_h, "anchor")
		vint_set_property(Completion.handles.top_grp_h, "anchor",  top_x, top_y + 2)

		vint_set_property(Completion.handles.top_1_h, "text_scale", x, y )
		vint_set_property(Completion.handles.top_2_h, "text_scale", .84, .84 )
		local t_2_x, t_2_y = vint_get_property(Completion.handles.top_2_h, "anchor")
		vint_set_property(Completion.handles.top_2_h, "anchor",  t_2_x, t_2_y + 13)
		vint_set_property(Completion.handles.top_3_h, "text_scale", .75, .75 )
		local t_3_x, t_3_y = vint_get_property(Completion.handles.top_3_h, "anchor")
		vint_set_property(Completion.handles.top_3_h, "anchor",  t_3_x, t_3_y + 21)

		vint_set_property(Completion.handles.thing_name_h, "text_scale", x, y )
		local name_x, name_y = vint_get_property(Completion.handles.thing_name_h, "anchor")
		vint_set_property(Completion.handles.thing_name_h, "anchor", name_x, name_y + 10)

		local desc_x, desc_y = vint_get_property(Completion.handles.thing_desc_h, "anchor")
		vint_set_property(Completion.handles.thing_desc_h, "anchor", desc_x, desc_y + 10)

		local fail_x, fail_y = vint_get_property(Completion.handles.fail_msg_h , "anchor")
		vint_set_property(Completion.handles.fail_msg_h, "anchor", fail_x, fail_y + 16)
	end

	completion_shut_off_all_layers()
	completion_grab_input()
	vint_dataresponder_request("completion_populate", "completion_initialize", 0)

end


function completion_reward_screen_finished()
	Completion_reset_respect_screen()
end

function completion_do_respect_screen()

	Completion_is_last_screen = true
	Completion_is_hood_screen = false
	Completion.is_respect_screen = true
	Completion_force_skip = false
	Completion_is_animating = true
	Completion.input_block = true
	Completion.num_unlocks = 0

	vint_set_property(Completion.handles.you_got_respect_h, "text_tag", "COMPLETION_ENOUGH_RESPECT")

	completion_cr_cash_fade_out(0)
	completion_cr_respect_fade_out(0)
	completion_hood_cash_fade_out(0)
	completion_hood_owned_fade_out(0)
	completion_news_clip_fade_out(0)
	completion_tips_fade_out(0)
	completion_unlock_fade_out(0)
	completion_unlock_desc_fade_out(0)

	local tween_h = vint_object_find("tips_fade_out_ender", Completion.handles.tips_fade_out_anim_h)
	vint_set_property(tween_h, "end_event", "completion_load_respect_icons")

	--saints
	lua_play_anim(Completion.handles.gang_zoom_st_h, 1)
	local tween_h = vint_object_find("st_ender", Completion.handles.gang_zoom_st_h)
	vint_set_property(tween_h, "start_event", "completion_respect_sound")
	--brotherhood
	lua_play_anim(Completion.handles.gang_zoom_bh_h, 1.5)
	local tween_h = vint_object_find("bh_ender", Completion.handles.gang_zoom_bh_h)
	vint_set_property(tween_h, "start_event", "completion_respect_sound")
	--ronin
	lua_play_anim(Completion.handles.gang_zoom_rn_h, 2 )
	local tween_h = vint_object_find("rn_ender", Completion.handles.gang_zoom_rn_h)
	vint_set_property(tween_h, "start_event", "completion_respect_sound")
	--samedi
	lua_play_anim(Completion.handles.gang_zoom_ss_h, 2.5)
	local tween_h = vint_object_find("ss_ender", Completion.handles.gang_zoom_ss_h)
	vint_set_property(tween_h, "start_event", "completion_respect_sound")
	--ultor
	lua_play_anim(Completion.handles.gang_zoom_ep_h, 3)
	local tween_h = vint_object_find("ep_ender", Completion.handles.gang_zoom_ep_h)
	vint_set_property(tween_h, "start_event", "completion_respect_sound")

	lua_play_anim(Completion.handles.you_got_respect_fade_in_anim_h, 3.5)

	local tween_h = vint_object_find("you_got_respect_ender", Completion.handles.you_got_respect_fade_in_anim_h)
	vint_set_property(tween_h, "end_event", "completion_tips_fade_in")

end

function completion_load_respect_icons()
	if Completion.type == SUCCESS_ACTIVITY or Completion.reward_source == SUCCESS_ACTIVITY then
		if Completion.last_level == true then
			if Completion.handles.activity_type == 13 then
				completion_init_buttons("COMPLETION_QUIT_ZOMBIE", nil, nil)
			else
				completion_init_buttons("COMPLETION_EXIT_ACTIVITY", nil, nil)
			end
		else
			completion_init_buttons("COMPLETION_CONTINUE_ACTIVITY", nil, "COMPLETION_EXIT_ACTIVITY")
		end
	else
		completion_init_buttons("COMPLETION_CONTINUE")
	end


	Completion.input_block = false
	vint_set_property(Completion.handles.tips_h, "anchor", 104, 392)
	vint_set_property(Completion.handles.gangs_grp_h, "visible", true)
	completion_load_peg("ui_c_respect_icons")
end

function completion_retry_mission_checkpoint(result, action)
	if action ~= DIALOG_ACTION_CLOSE then
		return
	end

	if result == 0 then
		completion_call_callback(COMPLETION_RESTART_FROM_CHECKPOINT)
		Completion.exiting = true
		completion_fade_out_all(0)
	end
end

function completion_exit_callback(result, action)
	if action ~= DIALOG_ACTION_CLOSE then
		return
	end

	if result == 0 then
		completion_call_callback(COMPLETION_EXIT)
		Completion.exiting = true
		completion_fade_out_all(0)

	end
end

function completion_retry_mission_beginning(result, action)
	if action ~= DIALOG_ACTION_CLOSE then
		return
	end

	if result == 0 then
		completion_call_callback(COMPLETION_RESTART)
		Completion.exiting = true
		completion_fade_out_all(0)
	end
end


function completion_grab_input()
	Completion.input[0] = vint_subscribe_to_input_event(nil, "select", 			"completion_process_input")
	Completion.input[1] = vint_subscribe_to_input_event(nil, "back", 				"completion_process_input")
	Completion.input[2] = vint_subscribe_to_input_event(nil, "alt_select", 		"completion_process_input")
	Completion.input[3] = vint_subscribe_to_input_event(nil, "all_unassigned", "completion_process_input")
	Completion.input[4] = vint_subscribe_to_input_event(nil, "map", 				"completion_process_input")
end

function completion_process_input(target, event, accel)
	local process_event = false
	local default = 0
	local priority = DIALOG_PRIORITY_ACTION

	if Completion.input_block == true then
		return
	end

	if Completion_is_animating == false then

		if event == "map" and Completion_is_coop() == true then
			local options = { [0] = "CONTROL_YES", [1] = "CONTROL_NO" }
			dialog_box_open("MENU_TITLE_WARNING", "DIALOG_PAUSE_DISCONNECT_PROMPT", options, "dialog_pause_disconnect", 0, DIALOG_PRIORITY_SYSTEM_CRITICAL, true, nil, false, false)
			return
		end

		if event == "select" then
			if Completion.is_respect_screen == true and Completion_is_coop() == false then
				completion_call_callback(COMPLETION_CONTINUE)
				process_event = true
			elseif Completion.a_available == true  then
				if Completion_cash_per_day.hood_name ~= nil and Completion_cash_per_day.finished ~= true then
					Completion_cash_per_day.finished = true
					-- Fade out the news image
					Completion_force_skip = false
					Completion_is_animating = true
					Completion_is_hood_screen = true
					completion_hood_cash_fade_out(0)
					completion_news_clip_fade_out(0)
					completion_tips_fade_out(0)
					Completion.input_block = true
					--set the call back that will unlock the hood
					local tween_h = vint_object_find("news_image_alpha", Completion.handles.news_clip_fade_out_anim_h)
					vint_set_property(tween_h, "end_event", "completion_shut_off_all_layers")

					local tween_h = vint_object_find("news_image_fade_out_ender", Completion.handles.news_clip_fade_out_anim_h)
					vint_set_property(tween_h, "start_event", "completion_unload_pegs")

					local tween_h = vint_object_find("news_image_fade_out_ender", Completion.handles.news_clip_fade_out_anim_h)
					vint_set_property(tween_h, "end_event", "completion_hood_unlock")
					return

				elseif Completion.cur_unlock < Completion.num_unlocks then
					--	Need to do this so we know if the player was in an activity or not.
					if Completion.cur_unlock == 0 then
						Completion.reward_source = Completion.type
					end
					Completion_force_skip = false
					Completion_is_animating = true
					vint_dataresponder_request("completion_populate", "completion_initialize", 0, Completion.cur_unlock)
					Completion.cur_unlock = Completion.cur_unlock + 1
					return

				elseif Completion_show_respect_screen == true and Completion.is_respect_screen == false then
					if Completion.type <= 2 or Completion.type == 7 then
						completion_do_respect_screen()
						return
					end
				elseif Completion_is_coop() == false then

					--redundant continue callback, just to make sure all bases are covered
					completion_call_callback(COMPLETION_CONTINUE)

					-- Retry failure, no prompz
					if Completion.type == FAILURE_MISSION or Completion.type == FAILURE_STRONGHOLD then

						if Completion_coop_disconnected == false then
							completion_call_callback(COMPLETION_RESTART_FROM_CHECKPOINT)
						else
							completion_call_callback(COMPLETION_RESTART)
						end
					elseif (Completion.type == FAILURE_ACTIVITY or Completion.type == SUCCESS_ACTIVITY) and Completion.handles.level_number == 0 then
						completion_call_callback(COMPLETION_EXIT)	-- Exit Special Derby [nclok1405]
					elseif Completion.type == FAILURE_ACTIVITY then
						completion_call_callback(COMPLETION_RESTART)
					elseif Completion.type == SUCCESS_ACTIVITY and Completion.last_level == true then
						completion_call_callback(COMPLETION_EXIT)
					end
					process_event = true
				end

			end
		elseif event == "back" and Completion.b_available == true and Completion_is_coop() == false then

			if Completion.handles.level_number ~= 0 then -- if this isn't a level 0 (special derby), then do this stuff

				-- Quit Activity
				if Completion.type == FAILURE_ACTIVITY or Completion.type == SUCCESS_ACTIVITY then
					if Completion.handles.activity_type == 13 then
						--local options = { [0] = "COMPLETION_QUIT_ZOMBIE", [1] = "CONTROL_NO" }
						--dialog_box_open("COMPLETION_QUIT_ZOMBIE", "COMPLETION_QUIT_ZOMBIE_CONFIRMATION", options, "completion_exit_callback", default, priority, true, nil, false, false)
						completion_call_callback(COMPLETION_EXIT)	-- Exit without dialog [nclok1405]
						process_event = true
					else
						--local options = { [0] = "COMPLETION_EXIT_ACTIVITY", [1] = "CONTROL_NO" }
						--dialog_box_open("COMPLETION_EXIT_ACTIVITY", "COMPLETION_EXIT_ACTIVITY_CONFIRMATION", options, "completion_exit_callback", default, priority, true, nil, false, false)
						completion_call_callback(COMPLETION_EXIT)	-- Exit without dialog [nclok1405]
						process_event = true
					end
				--Quit Level 3 Activity Reward Screen
				elseif Completion.reward_source == SUCCESS_ACTIVITY and Completion.type == UNLOCK_REWARD then
					--local options = { [0] = "COMPLETION_EXIT_ACTIVITY", [1] = "CONTROL_NO" }
					--dialog_box_open("COMPLETION_EXIT_ACTIVITY", "COMPLETION_EXIT_ACTIVITY_CONFIRMATION", options, "completion_exit_callback", default, priority, true, nil, false, false)
					completion_call_callback(COMPLETION_EXIT)	-- Exit without dialog [nclok1405]
					process_event = true
				-- Quit Mission
				elseif Completion.type == FAILURE_MISSION then
					if Completion_coop_disconnected then
						completion_call_callback(COMPLETION_EXIT)	-- Exit without dialog [nclok1405]
						process_event = true
					else
						local options = { [0] = "COMPLETION_EXIT_MISSION", [1] = "CONTROL_NO" }
						dialog_box_open("COMPLETION_EXIT_MISSION", "COMPLETION_EXIT_MISSION_CONFIRMATION", options, "completion_exit_callback", default, priority, true, nil, false, false)
						return
					end

				-- Quit Stronghold
				elseif Completion.type == FAILURE_STRONGHOLD then
					if Completion_coop_disconnected then
						completion_call_callback(COMPLETION_EXIT)	-- Exit without dialog [nclok1405]
						process_event = true
					elseif Sui_mod_mission_title ~= "" then
						-- Mod Mission [nclok1405]
						local options = { [0] = "COMPLETION_EXIT_MISSION", [1] = "CONTROL_NO" }
						dialog_box_open("COMPLETION_EXIT_MISSION", "COMPLETION_EXIT_MISSION_CONFIRMATION", options, "completion_exit_callback", default, priority, true, nil, false, false)
						return
					else
						local options = { [0] = "COMPLETION_EXIT_STRONGHOLD", [1] = "CONTROL_NO" }
						dialog_box_open("COMPLETION_EXIT_STRONGHOLD", "COMPLETION_EXIT_STRONGHOLD_CONFIRMATION", options, "completion_exit_callback", default, priority, true, nil, false, false)
						return
					end
				else
					process_event = true
				end
			else
				--this is just for Level 0 stuff (Special Derby)
				completion_call_callback(COMPLETION_EXIT)
				process_event = true
			end
		elseif event == "alt_select" and Completion_is_coop() == false and Completion.x_available == true  then
			-- Retry from beginning (missions and sh)
			local options = { [0] = "COMPLETION_RESTART_BEGINNING", [1] = "CONTROL_NO" }
			dialog_box_open("SGI_RETRY", "HUD_RETRY_MISSION_MESSAGE_FULL", options, "completion_retry_mission_beginning", default, priority, true, nil, false, false)
			return
		end


		if process_event == true then
			Completion.input_block = true
			Completion.exiting = true
			completion_fade_out_all(0)
		end

	end


	--skip screens if i play A before the end
	if Completion_is_animating == true then
		if event == "select" or event == "back" then
			--is an animation playing?
			Completion_is_animating = false
			Completion_force_skip = true
			completion_tips_fade_in(0)
			--Attempting to skip everything


			if Completion.is_respect_screen ~= true then

				if Completion.type == SUCCESS_ACTIVITY then

					local tween_h = vint_object_find("top_ender", Completion.handles.top_grp_anim_h)
					vint_set_property(tween_h, "end_event", nil)

					local tween_h = vint_object_find("cash_ender", Completion.handles.cr_cash_fade_in_anim_h)
					vint_set_property(tween_h, "end_event", nil)

					local tween_h = vint_object_find("respect_ender", Completion.handles.cr_respect_fade_in_anim_h)
					vint_set_property(tween_h, "end_event", nil)

					local tween_h = vint_object_find("style_ender", Completion.handles.style_grp_anim)
					vint_set_property(tween_h, "end_event", nil)

					completion_cr_cash_fade_in()

					--Pop in cash
					if Completion_cash_reward.cash > 0 then
						vint_set_property(Completion.handles.cash_v_h, "text_tag", "$" .. format_cash(Completion_cash_reward.cash))
						vint_set_property(Completion.handles.cash_t_h, "alpha", 1)
						vint_set_property(Completion.handles.cash_v_h, "alpha", 1)
						vint_set_property(Completion.handles.cash_t_h, "visible", true)
						vint_set_property(Completion.handles.cash_v_h, "visible", true)
					else
						vint_set_property(Completion.handles.cash_v_h, "text_tag", "")
						vint_set_property(Completion.handles.cash_t_h, "alpha", 0)
						vint_set_property(Completion.handles.cash_v_h, "alpha", 0)
						vint_set_property(Completion.handles.cash_t_h, "visible", false)
						vint_set_property(Completion.handles.cash_v_h, "visible", false)
					end

					--Respect if exists
					if Completion_cash_reward.has_respect == true then

						completion_cr_respect_fade_in()

						--Pop in respect
						local bonus_style = Completion_respect.bonus_style
						local new_respect = Completion_respect.new_respect
						local cur_respect = Completion_respect.cur_respect
						local props_to_unlock = Completion_respect.props_to_unlock
						local respect_bonus = new_respect - cur_respect - bonus_style -- how much respect did i win

						--whats my respect multiplier on start
						local multiplier = floor(Completion_respect.new_respect / props_to_unlock)

						--set the init angle value
						local new_angle = ((new_respect - (props_to_unlock * multiplier)) / props_to_unlock) * COMPLETION_RADIAN

						--call the function that sets the angle and multiplier, just this once
						completion_respect_meter_set(new_angle, multiplier, new_respect - cur_respect)

						vint_set_property(Completion.handles.respect_t_h, "alpha", 1)
						vint_set_property(Completion.handles.respect_v_h, "alpha", 1)
						vint_set_property(Completion.handles.respect_b_grp_h, "alpha", 1)

						--Respect bonus ?
						if bonus_style > 0 then
							completion_style_bonus_fade_in()
							vint_set_property(Completion.handles.style_grp, "visible", true)
							vint_set_property(Completion.handles.style_grp, "alpha", 1)
						else
							vint_set_property(Completion.handles.style_grp, "visible", false)
						end
					end

				elseif Completion.type == SUCCESS_MISSION then

					if Completion_is_hood_screen == false then
						--clear callbacks
						local tween_h = vint_object_find("top_ender", Completion.handles.top_grp_anim_h)
						vint_set_property(tween_h, "end_event", nil)
						local tween_h = vint_object_find("news_image_ender", Completion.handles.news_clip_fade_in_anim_h)
						vint_set_property(tween_h, "end_event", nil)
						local tween_h = vint_object_find("hood_cash_ender", Completion.handles.hood_cash_fade_in_anim_h)
						vint_set_property(tween_h, "end_event", nil)

						vint_set_property(Completion.handles.hood_cash_v_h, "text_tag",  "$" .. format_cash(Completion_cash_reward.cash))
						vint_set_property(Completion.handles.hood_cash_t_h, "text_tag", "COMPLETION_CASH")

						completion_news_clip_fade_in()
						completion_hood_cash_fade_in()

					else

						--clear callbacks
						local tween_h = vint_object_find("unlock_ender", Completion.handles.unlock_fade_in_anim_h)
						vint_set_property(tween_h, "end_event", nil)
						local tween_h = vint_object_find("hood_cash_ender", Completion.handles.hood_cash_fade_in_anim_h)
						vint_set_property(tween_h, "end_event", nil)
						local tween_h = vint_object_find("hood_owned_ender", Completion.handles.hood_owned_fade_in_anim_h)
						vint_set_property(tween_h, "end_event", nil)

						Completion_cash_per_day.finished = true

						vint_set_property(Completion.handles.unlock_h, "visible", true)
						completion_unlock_fade_in()
						completion_hood_cash_fade_in()
						vint_set_property(Completion.handles.hood_cash_v_h, "text_tag", "$" .. format_cash(Completion_cash_per_day.cash))
						vint_set_property(Completion.handles.hood_owned_t_h, "visible", true)
						vint_set_property(Completion.handles.hood_owned_v_h, "visible", true)
						completion_hood_owned_fade_in(0)

					end

				elseif Completion.type == SUCCESS_STRONGHOLD then

					if Completion_is_hood_screen == false then
						--clear callbacks
						local tween_h = vint_object_find("top_ender", Completion.handles.top_grp_anim_h)
						vint_set_property(tween_h, "end_event", nil)
						local tween_h = vint_object_find("news_image_ender", Completion.handles.news_clip_fade_in_anim_h)
						vint_set_property(tween_h, "end_event", nil)
						local tween_h = vint_object_find("hood_cash_ender", Completion.handles.hood_cash_fade_in_anim_h)
						vint_set_property(tween_h, "end_event", nil)

						vint_set_property(Completion.handles.hood_cash_v_h, "text_tag",  "$" .. format_cash(Completion_cash_reward.cash))
						vint_set_property(Completion.handles.hood_cash_t_h, "text_tag", "COMPLETION_CASH")

						completion_news_clip_fade_in()
						completion_hood_cash_fade_in()

					else
						local tween_h = vint_object_find("unlock_ender", Completion.handles.unlock_fade_in_anim_h)
						vint_set_property(tween_h, "end_event", nil)
						local tween_h = vint_object_find("hood_cash_ender", Completion.handles.hood_cash_fade_in_anim_h)
						vint_set_property(tween_h, "end_event", nil)
						local tween_h = vint_object_find("hood_owned_ender", Completion.handles.hood_owned_fade_in_anim_h)
						vint_set_property(tween_h, "end_event", nil)

						Completion_cash_per_day.finished = true

						vint_set_property(Completion.handles.unlock_h, "visible", true)
						completion_unlock_fade_in()
						completion_hood_cash_fade_in()
						vint_set_property(Completion.handles.hood_cash_v_h, "text_tag", "$" .. format_cash(Completion_cash_per_day.cash))
						vint_set_property(Completion.handles.hood_owned_t_h, "visible", true)
						vint_set_property(Completion.handles.hood_owned_v_h, "visible", true)
						completion_hood_owned_fade_in(0)
					end

				elseif Completion.type == FAILURE_MISSION then

					completion_fail_fade_in()

				elseif Completion.type == FAILURE_STRONGHOLD then

					completion_fail_fade_in()

				elseif Completion.type == FAILURE_ACTIVITY then

					completion_fail_fade_in()

				elseif Completion.type == JUST_UNLOCKS then

					completion_unlock_fade_in()
					completion_unlock_desc_fade_in()

				elseif Completion.type == UNLOCK_REWARD then

					local tween_h = vint_object_find("unlock_ender", Completion.handles.unlock_fade_in_anim_h)
					vint_set_property(tween_h, "end_event", nil)

					local tween_h = vint_object_find("unlock_desc_ender", Completion.handles.unlock_desc_fade_in_anim_h)
					vint_set_property(tween_h, "end_event", nil)

					completion_unlock_fade_in()
					completion_unlock_desc_fade_in()

			--	elseif Completion_show_reward_screen() == true and Completion.type ~= SUCCESS_ACTIVITY then

				end

			else

				local tween_h = vint_object_find("st_ender", Completion.handles.gang_zoom_st_h)
				vint_set_property(tween_h, "start_event", nil)

				local tween_h = vint_object_find("bh_ender", Completion.handles.gang_zoom_bh_h)
				vint_set_property(tween_h, "start_event", nil)

				local tween_h = vint_object_find("rn_ender", Completion.handles.gang_zoom_rn_h)
				vint_set_property(tween_h, "start_event", nil)

				local tween_h = vint_object_find("ss_ender", Completion.handles.gang_zoom_ss_h)
				vint_set_property(tween_h, "start_event", nil)

				local tween_h = vint_object_find("ep_ender", Completion.handles.gang_zoom_ep_h)
				vint_set_property(tween_h, "start_event", nil)

				local tween_h = vint_object_find("you_got_respect_ender", Completion.handles.you_got_respect_fade_in_anim_h)
				vint_set_property(tween_h, "end_event", nil)

			end

			--speed up time to kill any animations
			audio_play(Completion_audio.tips)
			local current_time = vint_get_time_index()
			local future_time = current_time + 10
			vint_set_time_index(future_time)

		end
	end
end

function completion_release_input()
	for idx, val in Completion.input do
		vint_unsubscribe_to_input_event(val)
	end
	Completion.input = { }
end

function completion_init_mission_success(mission_number, team, mission_name, cash_reward, image_base, cur_respect, props_to_unlock, cash_per_day, hoods_owned, hoods_total, hood_name)
	Completion.handles.failure = false
	Completion_is_hood_screen = false
	--local insertion_text 	= { [0] = mission_number }
	local insertion_text2 	= { [0] = mission_name }


	Completion.handles.cur_respect = cur_respect
	Completion.handles.props_to_unlock = props_to_unlock

	-- Only show "You have enough respect" on the initial completion and not on dlc05 [nclok1405]
	if (cur_respect >= props_to_unlock) and (cash_reward > 0) and (image_base ~= "dlc05") then
		Completion_show_respect_screen = true
	end

	if Completion.num_unlocks == 0 and cur_respect < props_to_unlock and hood_name == nil then
		Completion_is_last_screen = true
	end

	--local pretitle = vint_insert_values_in_string("COMPLETION_MISSION_NUMBER", insertion_text)
	local subtitle = vint_insert_values_in_string("COMPLETION_MISSION_COMPLETE", insertion_text2 )

	Completion_force_skip = false
	Completion_is_animating = true
	Completion_is_hood_screen = false

	completion_init_title("COMPLETION_MISSION_NUMBER", Completion_Gang_Names[team], subtitle)
	local wall = Completion_Gang_Images[team]
	if (image_base == "dlc05") then
		wall = "mp"	-- Change winning background of dlc05 to the image based on SR2 boxart since this is the final mission [nclok1405]
	end
	completion_init_wall(wall)
	completion_init_buttons("COMPLETION_CONTINUE")

	completion_move_unlockable_text(true)

	--store one time cash reward
	Completion_cash_reward.cash = cash_reward

	--store hood cash per day that shit. we'll initialize later
	Completion_cash_per_day.cash = cash_per_day
	Completion_cash_per_day.image_base = image_base
	Completion_cash_per_day.hood_name = hood_name
	Completion_cash_per_day.hoods_owned = hoods_owned
	Completion_cash_per_day.hoods_total = hoods_total
	--completion_init_hood(cash_per_day, image_base, hood_name, hoods_owned, hoods_total)

	--cash reward init
	if cash_reward > 0 then
		vint_set_property(Completion.handles.hood_cash_v_h, "text_tag", "$0")
		vint_set_property(Completion.handles.hood_cash_t_h, "text_tag", "COMPLETION_CASH")
	else
		vint_set_property(Completion.handles.hood_cash_v_h, "text_tag", "")
		vint_set_property(Completion.handles.hood_cash_t_h, "text_tag", "")
	end

	--load the image
	if image_base ~= nil then
		completion_load_peg("ui_c_news_" .. image_base)
		vint_set_property(Completion.handles.thing_image_h, "image", "ui_ct_news_" .. image_base)	--	Newspaper clipping
	end

	-- Animate in the main stuff
	completion_fade_in_wall_and_top(1)

	--animate the newspaper
	local tween_h = vint_object_find("top_ender", Completion.handles.top_grp_anim_h)
	vint_set_property(tween_h, "end_event", "completion_news_clip_fade_in")

	--callback for cash reward fade in
	local tween_h = vint_object_find("news_image_ender", Completion.handles.news_clip_fade_in_anim_h)
	vint_set_property(tween_h, "end_event", "completion_hood_cash_fade_in")

	--shut off the images at fade out
	local tween_h = vint_object_find("news_image_alpha", Completion.handles.news_clip_fade_out_anim_h)
	vint_set_property(tween_h, "end_event", "completion_shut_off_all_layers")

	--callback for the animate cash reward function
	local tween_h = vint_object_find("hood_cash_ender", Completion.handles.hood_cash_fade_in_anim_h)
	vint_set_property(tween_h, "end_event", "completion_animate_reward_cash")

	completion_move_mission_tips()
end

function completion_init_pushback_success(team, hood_name, cash, respect)

	Completion_force_skip = false
	Completion_is_animating = true

	--some initializing stuff
	Completion.handles.failure = false
	completion_init_title(hood_name, Completion_Gang_Names[team], "PUSHBACK_SUCCESS_2")
	completion_init_wall(Completion_Gang_Images[team])
	completion_init_buttons("COMPLETION_CONTINUE")
	completion_init_cash_respect(0, nil)

	--fade in stuff
	completion_fade_in_wall_and_top(1)

	Completion_cash_reward.cash = cash

	local tween_h = vint_object_find("top_ender", Completion.handles.top_grp_anim_h)
	vint_set_property(tween_h, "end_event", "completion_cr_cash_fade_in")

	local tween_h = vint_object_find("cash_ender", Completion.handles.cr_cash_fade_in_anim_h)
	vint_set_property(tween_h, "end_event", "completion_animate_cash")

	completion_move_activity_tips(0, 0, 0)

	-- remove this when you implement it.
	--vint_document_unload(vint_document_unload(vint_document_find("completion"))
end

function completion_move_mission_tips()
	--move button tips
	local unlock_x, unlock_y = vint_get_property(Completion.handles.unlock_h, "anchor")
	local gap = 15
	local tax, tay = vint_get_property(Completion.handles.tips_h, "anchor")  --store tax for later
	local imagew, imageh = element_get_actual_size(Completion.handles.thing_image_h)
	local imagex, imagey = vint_get_property(Completion.handles.thing_image_h, "anchor")

	local height = 0

	if imageh > 412 then
		imageh = 412
	elseif Completion_is_hood_screen == true then
		imageh = 300
	end

	local height = imagey + imageh + unlock_y + gap

	vint_set_property(Completion.handles.tips_h, "anchor", tax, height)
end


function completion_init_stronghold_success(team, stronghold_name, hood_name, cash_per_day, hoods_owned, hoods_total, image_base, cash_reward, cur_respect, props_to_unlock)
	-- Override title if in a mod mission [nclok1405]
	local mission_type_name = "COMPLETION_STRONGHOLD"
	if Sui_mod_mission_title ~= "" then
		stronghold_name = Sui_mod_mission_title
		mission_type_name = "SUI_MOD_MISSION"
	end

	Completion.handles.failure = false

	local insertion_text = { [0] = stronghold_name }
	local subtitle = vint_insert_values_in_string("COMPLETION_MISSION_COMPLETE", insertion_text )

	Completion.handles.cur_respect = cur_respect
	Completion.handles.props_to_unlock = props_to_unlock

	-- Only show "You have enough respect" on the initial completion [nclok1405]
	if (cur_respect >= props_to_unlock) and (cash_reward > 0) then
		Completion_show_respect_screen = true
	end

	if Completion.num_unlocks == 0 and cur_respect < props_to_unlock and hood_name == nil then
		Completion_is_last_screen = true
	end

	completion_move_unlockable_text(true)

	completion_init_title(mission_type_name, Completion_Gang_Names[team], subtitle)
	completion_init_wall(Completion_Gang_Images[team])

	Completion_force_skip = false
	Completion_is_animating = true
	Completion_is_hood_screen = false
	completion_init_buttons("COMPLETION_CONTINUE")

	--store one time cash reward
	Completion_cash_reward.cash = cash_reward

	--store hood cash per day that shit. we'll initialize later
	Completion_cash_per_day.cash = cash_per_day
	Completion_cash_per_day.image_base = image_base
	Completion_cash_per_day.hood_name = hood_name
	Completion_cash_per_day.hoods_owned = hoods_owned
	Completion_cash_per_day.hoods_total = hoods_total
	--completion_init_hood(cash_per_day, image_base, hood_name, hoods_owned, hoods_total)

	--cash reward init
	if cash_reward > 0 then
		vint_set_property(Completion.handles.hood_cash_v_h, "text_tag", "$0")
		vint_set_property(Completion.handles.hood_cash_t_h, "text_tag", "COMPLETION_CASH")
	else
		vint_set_property(Completion.handles.hood_cash_v_h, "text_tag", "")
		vint_set_property(Completion.handles.hood_cash_t_h, "text_tag", "")
	end

	--load the image
	if image_base ~= nil then
		completion_load_peg("ui_c_news_" .. image_base)
		vint_set_property(Completion.handles.thing_image_h, "image", "ui_ct_news_" .. image_base)	--	Newspaper clipping
	end

	-- Animate in the main stuff
	completion_fade_in_wall_and_top(1)

	--animate the newspaper
	local tween_h = vint_object_find("top_ender", Completion.handles.top_grp_anim_h)
	vint_set_property(tween_h, "end_event", "completion_news_clip_fade_in")

	--callback for cash reward fade in
	local tween_h = vint_object_find("news_image_ender", Completion.handles.news_clip_fade_in_anim_h)
	vint_set_property(tween_h, "end_event", "completion_hood_cash_fade_in")

	--callback for the animate cash reward function
	local tween_h = vint_object_find("hood_cash_ender", Completion.handles.hood_cash_fade_in_anim_h)
	vint_set_property(tween_h, "end_event", "completion_animate_reward_cash")

	--shut off the images at fade out
	local tween_h = vint_object_find("news_image_alpha", Completion.handles.news_clip_fade_out_anim_h)
	vint_set_property(tween_h, "end_event", "completion_shut_off_all_layers")

	completion_move_mission_tips()
end

function completion_init_activity_success(district, activity_name, level_number, cash, cur_respect, new_respect, style_level, bonus_style, props_to_unlock, activity_type, last_level)
	if activity_type == 13 then
		-- Zombie Uprising [nclok1405]
		district = vint_insert_values_in_string("{0} {1}", {[0] = "ACT_ZOMBIE_HUD_HIGH_SCORE", [1] = format_cash(Sui_zombie_high_score)})
		activity_name = format_cash(Sui_zombie_final_score)
	elseif activity_type == 0 or activity_type == 1 or activity_type == 4 or activity_type == 11 or activity_type == 12 or activity_type == 16 then
		-- Activity Score [nclok1405]
		district = "$"..format_cash(Sui_activity_score).."/$"..format_cash(Sui_activity_requirement)
	end

	Completion_force_skip = false
	Completion_is_animating = true

	-- Only show the "You have enough respect" screen on initial completion [nclok1405]
	if (new_respect >= props_to_unlock) and (new_respect - cur_respect > 0) then
		Completion_show_respect_screen = true
	end

	Completion.handles.cur_respect = new_respect
	Completion.handles.props_to_unlock = props_to_unlock

	--debug_print("vint", "cur" .. var_to_string(new_respect) .. "\n")
	--debug_print("vint", "props_to_unlock" .. var_to_string(props_to_unlock) .. "\n")

	--some initializing stuff
	Completion.handles.failure = false
	local insertion_text = { [0] = level_number }
	completion_init_title(district, activity_name, vint_insert_values_in_string("COMPLETION_ACTIVITY_LEVEL_COMPLETE", insertion_text))
	completion_init_cash_respect(cash, new_respect - cur_respect)
	completion_init_wall(Completion_Activity_Images[activity_type + 1])
	Completion.last_level = last_level

	if last_level == true and Completion.num_unlocks == 0 then
		--	If we have no unlocks, and there is no more activity to continue, show just exit
		Completion_is_last_screen = true
		if Completion_show_respect_screen ~= true then
			completion_init_buttons("COMPLETION_EXIT_ACTIVITY", nil, nil)
		else
			completion_init_buttons("COMPLETION_CONTINUE", nil, nil)
		end
		if activity_type == 13 then
			--change tips if zombie has no unlocks
			completion_init_buttons("COMPLETION_CONTINUE", nil, nil)
		end
	elseif Completion.num_unlocks > 0 or Completion_show_respect_screen == true then
		--	Continue if there are unlocks coming up
		-- or continue if we are showing the respect screen
		--completion_tips_fade_in(1.5 + COMPLETION_LOAD_DELAY)
		completion_init_buttons("COMPLETION_CONTINUE", nil, nil)
	else
		--	Otherwise, show the proper "Continue Activity" or "Exit Activity"
		Completion_is_last_screen = true
		completion_init_buttons("COMPLETION_CONTINUE_ACTIVITY", nil, "COMPLETION_EXIT_ACTIVITY")
	end


	if activity_type == 13 then
		--change the top line if this is Zombie, just show respect...
		Completion.handles.activity_type = 13

		local victory_msg
		if get_language() == "JP" then
			victory_msg = vint_insert_values_in_string("{0}! {1}: {2}", {[0] = "MP_WINNERS_YOU_WIN", [1] = "STAT_GAME_ZOMBIE_KILLED", [2] = format_cash(Sui_zombie_final_kills)})
		else
			victory_msg = vint_insert_values_in_string("{0}! {1} {2} {3}", {[0] = "MP_WINNERS_YOU_WIN", [1] = "PAUSE_MAP_FILTER_ALL", [2] = format_cash(Sui_zombie_final_kills), [3] = "STAT_GAME_ZOMBIE_KILLED"})
		end

		vint_set_property(Completion.handles.top_3_h, "text_tag", victory_msg)
		vint_set_property(Completion.handles.cash_t_h, "visible", false)
		vint_set_property(Completion.handles.cash_v_h, "visible", false)
		local cr_x, cr_y = vint_get_property(Completion.handles.cash_respect_h, "anchor")
		vint_set_property(Completion.handles.cash_respect_h, "anchor", -85, cr_y)
	elseif level_number == 0 then
		-- Special Derby
		vint_set_property(Completion.handles.top_1_h, "text_tag", "$"..format_cash(Sui_activity_score).."/$"..format_cash(Sui_activity_requirement))
		Completion.handles.level_number = 0
		vint_set_property(Completion.handles.top_3_h, "text_tag", "COMPLETION_COMPLETE")
		if Completion_is_coop() then -- PC fix: client must display WAIT FOR HOST
			completion_coop_waiting()
		else
			-- Changed to Enter [nclok1405]
			--completion_init_buttons(nil, nil, "COMPLETION_EXIT_ACTIVITY")
			completion_init_buttons("COMPLETION_CONTINUE", nil, nil)
		end
	end

	--fade in stuff
	completion_fade_in_wall_and_top(1)

	--store the globals I'm gonna need for later
	Completion_respect.new_respect = new_respect
	Completion_respect.cur_respect = cur_respect
	Completion_respect.props_to_unlock = props_to_unlock
	Completion_respect.bonus_style = bonus_style
	Completion_cash_reward.cash = cash

	--debug_print("vint", "cash" .. var_to_string(cash) .. "\n\n\n")

	if cash > 0 then
		local tween_h = vint_object_find("top_ender", Completion.handles.top_grp_anim_h)
		vint_set_property(tween_h, "end_event", "completion_cr_cash_fade_in")
		local tween_h = vint_object_find("cash_ender", Completion.handles.cr_cash_fade_in_anim_h)
		vint_set_property(tween_h, "end_event", "completion_animate_cash")
	elseif cash <= 0 and new_respect > cur_respect then
		completion_cr_respect_fade_in(3.25)
	elseif cash <= 0 and new_respect == cur_respect then
		completion_tips_fade_in_offset(3.25)
	end

	if new_respect > cur_respect then
		--tell the completion_animate_cash function that there should be respect
		Completion_cash_reward.has_respect = true
		--set up the respect count call back
		local tween_h = vint_object_find("respect_ender", Completion.handles.cr_respect_fade_in_anim_h)
		vint_set_property(tween_h, "end_event", "completion_animate_respect")
	else
		Completion_cash_reward.has_respect = false
		--turn the respect stuff off
		vint_set_property(Completion.handles.respect_b_grp_h, "visible", false)
		vint_set_property(Completion.handles.respect_t_h, "visible", false)
		vint_set_property(Completion.handles.respect_v_h, "visible", false)
	end


	--whats my respect multiplier on start
	local old_multiplier = floor(cur_respect / props_to_unlock)

	--set the init angle value
	local old_angle = ((cur_respect - (props_to_unlock * old_multiplier)) / props_to_unlock) * COMPLETION_RADIAN

	--my respect always counts from 0
	local old_respect = 0

	--call the function that sets the angle and multiplier, just this once
	completion_respect_meter_set(old_angle, old_multiplier, old_respect)

	completion_move_activity_tips(cur_respect, new_respect, bonus_style)

end

function completion_move_activity_tips(cur_respect, new_respect, bonus_style)
	local tax, tay = vint_get_property(Completion.handles.tips_h, "anchor")
	local content_y = 300

	if new_respect > cur_respect then
		content_y = 380
	end

	if bonus_style > 0 then
		content_y = 436
	end

	vint_set_property(Completion.handles.tips_h, "anchor", tax, content_y)

end


--+++++++++++++++++++++++++++++++++++++++
-----------------------------------------
--ACTIVITY CASH REWARD
-----------------------------------------
--+++++++++++++++++++++++++++++++++++++++
function completion_animate_cash()
   thread_new("completion_animate_cash_thread")
end

function completion_animate_cash_thread()
	--this is for activities

	--init stuff
	local start_cash = 0
	local cash_this_frame = -1
	local is_complete = false

	--get the variables from the global
	local cash = Completion_cash_reward.cash

	local amt_min = 100
	local amt_max = 5000

	local time_min = 300
	local time_max = 2999
	local init_time = floor(vint_get_time_index() * 1000)
	local cur_time = init_time
	local time_to_count = floor(time_min + ((time_max - time_min) * (cash / amt_max)))

	if time_to_count > time_max then
		time_to_count = time_max
	end

	--Force close thread
	if Completion_force_skip == true then
		Completion_force_skip = false
		return
	end

	--init sound IDs
	local activity_cash_count = 0
	local activity_cash_hit = 0

	if cash > 0 then
		activity_cash_count = audio_play(Completion_audio.cash_count)
	end

	while is_complete == false do

		local cur_time = floor(vint_get_time_index() * 1000) - init_time

		--Force close thread
		if Completion_force_skip == true then
			Completion_force_skip = false
			audio_fade_out(activity_cash_count, 50)
			audio_fade_out(activity_cash_hit, 50)
			return
		end

		--set my values
		cash_this_frame = cash * (cur_time / time_to_count)
		vint_set_property(Completion.handles.cash_v_h, "text_tag", "$" .. format_cash(cash_this_frame))

		if cur_time >= time_to_count then
			audio_fade_out(activity_cash_count, 50)
			activity_cash_hit = audio_play(Completion_audio.cash_hit)
			vint_set_property(Completion.handles.cash_v_h, "text_tag", "$" .. format_cash(cash))
			is_complete = true
			--audio_stop(Completion_audio.cash_count, 50)
			if Completion_cash_reward.has_respect == true then
				--fade in the respect
				completion_cr_respect_fade_in(.4)
			else
				--nah... show the buttons instead
				vint_set_property(Completion.handles.style_grp, "visible", false)
				completion_tips_fade_in_offset(.4)
			end
		end
		thread_yield()
	end
end



function completion_respect_meter_set(end_angle, multiplier, respect)

	--set the current angle and multiplier of respect bar
	vint_set_property(Completion.handles.respect_b_0_h, "end_angle", end_angle)
	vint_set_property(Completion.handles.respect_b_1_h, "end_angle", end_angle)
	vint_set_property(Completion.handles.respect_multi_grp, "rotation", -end_angle)
	vint_set_property(Completion.handles.respect_multiplier, "rotation", end_angle)
	if multiplier == 0 then
		vint_set_property(Completion.handles.respect_multiplier, "visible", false)
	else
		vint_set_property(Completion.handles.respect_multiplier, "visible", true)
		vint_set_property(Completion.handles.respect_multiplier, "text_tag", "x" .. multiplier)
	end
	vint_set_property(Completion.handles.respect_v_h, "text_tag", format_cash(respect))

end

--+++++++++++++++++++++++++++++++++++++++
-----------------------------------------
--ACTIVITY RESPECT COUNT UP
-----------------------------------------
--+++++++++++++++++++++++++++++++++++++++

function completion_animate_respect()
   thread_new("completion_animate_respect_thread")
end

function completion_animate_respect_thread()
	--init stuff
	local start_respect = 0
	local respect = -1
	local multiplier = -1
	local end_angle = -1
	local respect_this_frame = -1
	local is_complete = false

	--get the variables from the global
	local bonus_style = Completion_respect.bonus_style
	local new_respect = Completion_respect.new_respect
	local cur_respect = Completion_respect.cur_respect
	local props_to_unlock = Completion_respect.props_to_unlock
	local respect_bonus = new_respect - cur_respect - bonus_style -- how much respect did i win

	local amt_max = 14000

	local time_min = 300
	local time_max = 2999
	local init_time = floor(vint_get_time_index() * 1000)
	local cur_time = init_time
	local time_to_count = floor(time_min + ((time_max - time_min) * (respect_bonus / amt_max)))

	if time_to_count > time_max then
		time_to_count = time_max
	end

	--Force close thread
	if Completion_force_skip == true then
		Completion_force_skip = false
		return
	end

	--init sounds
	local activity_respect_count = 0
	local activity_respect_hit = 0
	local activity_respect_end = 0
	activity_respect_count = audio_play(Completion_audio.respect_count)

	local multiplier_new = 999

	while is_complete == false do

		local cur_time = floor(vint_get_time_index() * 1000) - init_time

		--Force close thread
		if Completion_force_skip == true then
			Completion_force_skip = false
			audio_fade_out(activity_respect_count, 50)
			audio_fade_out(activity_respect_hit, 50)
			return
		end

		--set my values
		respect_this_frame = respect_bonus * (cur_time / time_to_count)
		vint_set_property(Completion.handles.respect_v_h, "text_tag", "" .. format_cash(respect_this_frame))
		respect = cur_respect + respect_this_frame

		multiplier = floor(respect/ props_to_unlock)
		if multiplier > multiplier_new then
			activity_respect_hit = audio_play(Completion_audio.respect_hit)
		end
		multiplier_new = multiplier

		end_angle = ((respect - (props_to_unlock * multiplier)) / props_to_unlock) * COMPLETION_RADIAN

		--call the function to display this shit
		completion_respect_meter_set(end_angle, multiplier, respect_this_frame)

		if cur_time  >= time_to_count then
			audio_fade_out(activity_respect_count, 50)
			audio_fade_out(activity_respect_hit, 35)
			activity_respect_end = audio_play(Completion_audio.respect_end)
			vint_set_property(Completion.handles.respect_v_h, "text_tag", "" .. format_cash(respect_bonus))
			is_complete = true
			if bonus_style > 0 then
				--play the style bonus graphic
				completion_style_bonus_fade_in()
				local tween_h = vint_object_find("style_ender", Completion.handles.style_grp_anim)
				vint_set_property(tween_h, "end_event", "completion_animate_style")
			else
				vint_set_property(Completion.handles.style_grp, "visible", false)
				completion_tips_fade_in_offset(.4)
			end
		end
		thread_yield()
	end
end

--+++++++++++++++++++++++++++++++++++++++
-----------------------------------------
--ACTIVITY RESPECT STYLE BONUS
-----------------------------------------
--+++++++++++++++++++++++++++++++++++++++

function completion_animate_style()
   thread_new("completion_animate_style_thread")
end

function completion_animate_style_thread()
		--init stuff
	local start_respect = 0
	local respect = -1
	local respect_this_frame = -1
	local multiplier = -1
	local end_angle = -1
	local respect_this_frame = -1
	local is_complete = false

	--get the variables from the global
	local bonus_style = Completion_respect.bonus_style
	local new_respect = Completion_respect.new_respect
	local cur_respect = Completion_respect.cur_respect
	local props_to_unlock = Completion_respect.props_to_unlock
	local respect_bonus = new_respect - cur_respect - bonus_style -- how much respect did i win

	start_respect = cur_respect + respect_bonus

	local amt_max = 10000

	local time_min = 150
	local time_max = 1498
	local init_time = floor(vint_get_time_index() * 1000)
	local cur_time = init_time
	local time_to_count = floor(time_min + ((time_max - time_min) * (bonus_style / amt_max)))

	if time_to_count > time_max then
		time_to_count = time_max
	end

	local activity_style_count = 0
	local activity_style_hit = 0

	activity_style_count = audio_play(Completion_audio.respect_count)

	local multiplier_new = 999

	while is_complete == false do

		local cur_time = floor(vint_get_time_index() * 1000) - init_time

		--Force close thread
		if Completion_force_skip == true then
			Completion_force_skip = false
			audio_fade_out(activity_style_count, 50)
			audio_fade_out(activity_style_hit, 50)
			return
		end


		respect_this_frame = bonus_style * (cur_time / time_to_count)
		respect = start_respect + respect_this_frame

		multiplier = floor(respect / props_to_unlock)
		if multiplier > multiplier_new  and multiplier_new ~= nil then
			activity_style_hit = audio_play(Completion_audio.respect_hit)
		end

		multiplier_new = multiplier

		end_angle = ((respect - (props_to_unlock * multiplier)) / props_to_unlock) * COMPLETION_RADIAN

		--call the function to display this shit
		completion_respect_meter_set(end_angle, multiplier, (respect_this_frame + respect_bonus))

		if cur_time  >= time_to_count then
			audio_fade_out(activity_style_count, 50)
			activity_style_hit = audio_play(Completion_audio.respect_hit)
			vint_set_property(Completion.handles.respect_v_h, "text_tag", "" .. format_cash(respect_bonus + bonus_style))
			is_complete = true
			completion_tips_fade_in(.4)
		end
		thread_yield()
	end
end

--+++++++++++++++++++++++++++++++++++++++
-----------------------------------------
--HOOD UNLOCK, CASH PER DAY
-----------------------------------------
--+++++++++++++++++++++++++++++++++++++++

function completion_animate_hood_cash()
   thread_new("completion_animate_hood_cash_thread")
end

function completion_animate_hood_cash_thread()

	--init stuff
	local start_cash = 0
	local cash_this_frame = -1
	local is_complete = false

	--get the variables from the global
	local cash = Completion_cash_per_day.cash

	local amt_min = 100
	local amt_max = 33000

	local time_min = 300
	local time_max = 2999
	local init_time = floor(vint_get_time_index() * 1000)
	local cur_time = init_time
	local time_to_count = floor(time_min + ((time_max - time_min) * (cash / amt_max)))

	if time_to_count > time_max then
		time_to_count = time_max
	end

	--Force close thread
	if Completion_force_skip == true then
		Completion_force_skip = false
		return
	end

	--init sound IDs
	local hood_cash_count = 0
	local hood_cash_hit = 0

	if cash > 0 then
		hood_cash_count = audio_play(Completion_audio.cash_count)

		while is_complete == false do

			local cur_time = floor(vint_get_time_index() * 1000) - init_time

			--Force close thread
			if Completion_force_skip == true then
				Completion_force_skip = false
				audio_fade_out(hood_cash_count, 50)
				audio_fade_out(hood_cash_hit, 50)
				return
			end

			--set my values
			cash_this_frame = cash * (cur_time / time_to_count)
			vint_set_property(Completion.handles.hood_cash_v_h, "text_tag", "$" .. format_cash(cash_this_frame))

			if cur_time >= time_to_count then

				audio_fade_out(hood_cash_count, 50)
				hood_cash_hit = audio_play(Completion_audio.cash_hit)

				is_complete = true

				--this will be checked in the process_input
				Completion_cash_per_day.finished = true

				--force the values
				vint_set_property(Completion.handles.hood_cash_v_h, "text_tag", "$" .. format_cash(cash))
				vint_set_property(Completion.handles.hood_owned_t_h, "visible", true)
				vint_set_property(Completion.handles.hood_owned_v_h, "visible", true)
				completion_hood_owned_fade_in(.4)

			end
			thread_yield()
		end
	else
		completion_hood_owned_fade_in(.4)
	end

	local tween_h = vint_object_find("hood_owned_ender", Completion.handles.hood_owned_fade_in_anim_h)
	vint_set_property(tween_h, "end_event", "completion_tips_fade_in")

end

--+++++++++++++++++++++++++++++++++++++++
-----------------------------------------
--MISSIONS, ONE TIME CASH REWARD
-----------------------------------------
--+++++++++++++++++++++++++++++++++++++++
function completion_animate_reward_cash()
   thread_new("completion_animate_reward_cash_thread")
end

function completion_animate_reward_cash_thread()
	--init stuff
	local start_cash = 0
	local cash_this_frame = -1
	local is_complete = false

	--get the variables from the global
	local cash = Completion_cash_reward.cash

	local amt_min = 100
	local amt_max = 33000

	local time_min = 300
	local time_max = 2999
	local init_time = floor(vint_get_time_index() * 1000)
	local cur_time = init_time
	local time_to_count = floor(time_min + ((time_max - time_min) * (cash / amt_max)))

	if time_to_count > time_max then
		time_to_count = time_max
	end

	vint_set_property(Completion.handles.hood_owned_t_h, "visible", false)
	vint_set_property(Completion.handles.hood_owned_v_h, "visible", false)

	--Force close thread
	if Completion_force_skip == true then
		Completion_force_skip = false
		return
	end

	--init sound IDs
	local reward_cash_count = 0
	local reward_cash_hit = 0

	if cash > 0 then
		reward_cash_count = audio_play(Completion_audio.cash_count)

		while is_complete == false do
			local cur_time = floor(vint_get_time_index() * 1000) - init_time

			--Force close thread
			if Completion_force_skip == true then
				Completion_force_skip = false
				audio_fade_out(reward_cash_count, 50)
				audio_fade_out(reward_cash_hit, 50)
				return
			end

			--set my values
			cash_this_frame = cash * (cur_time / time_to_count)
			vint_set_property(Completion.handles.hood_cash_v_h, "text_tag", "$" .. format_cash(cash_this_frame))

			if cur_time >= time_to_count then

				audio_fade_out(reward_cash_count, 50)
				reward_cash_hit = audio_play(Completion_audio.cash_hit)
				vint_set_property(Completion.handles.hood_cash_v_h, "text_tag", "$" .. format_cash(cash))
				is_complete = true
				--button tips
				completion_tips_fade_in_offset(.4)
			end
			thread_yield()
		end
	else
		completion_tips_fade_in_offset(.4)
	end
end



function	completion_init_mission_failure(mission_number, team, mission_name, failure_text, image_base)
	Completion_is_last_screen = true
	Completion.handles.failure = true
	--local insertion_text = { [0] = mission_number }
	local insertion_text2 = { [0] = mission_name }

	Completion.handles.image_base = image_base
	Completion.handles.mission_number = mission_number
	Completion.handles.team = team

	--debug_print("vint", "team " .. var_to_string(team) .. "\n")
	--debug_print("vint", "mission_number " .. var_to_string(mission_number) .. "\n")
	--debug_print("vint", "image_base " .. var_to_string(image_base) .. "\n")

	local subtitle = vint_insert_values_in_string("COMPLETION_MISSION_FAILED", insertion_text2)

	completion_init_title("COMPLETION_MISSION_NUMBER", Completion_Gang_Names[team], subtitle)
	completion_init_fail_message(failure_text)
	completion_init_wall(Completion_Gang_Images[team])

	if Completion_coop_disconnected == true then
		--this is also called in Single Player if the checkpoint hasn't been reached
		completion_coop_disconnected()
	else
		if Completion.handles.image_base == "tss01" then
			completion_init_buttons("COMPLETION_RESTART_CHECKPOINT", "COMPLETION_RESTART_BEGINNING", nil)
		else
			completion_init_buttons("COMPLETION_RESTART_CHECKPOINT", "COMPLETION_RESTART_BEGINNING", "COMPLETION_EXIT_MISSION")
		end
	end

	--fade in stuff
	completion_fade_in_wall_and_top(1)
	completion_fail_fade_in(3)

	completion_tips_fade_in_offset(3.5)

	Completion_force_skip = false
	Completion_is_animating = true
end

function completion_init_stronghold_failure(team, stronghold_name, failure_text)
	-- Override title if in a mod mission [nclok1405]
	local mission_type_name = "COMPLETION_STRONGHOLD"
	if Sui_mod_mission_title ~= "" then
		stronghold_name = Sui_mod_mission_title
		mission_type_name = "SUI_MOD_MISSION"

		-- Override cancel text
		if sui_compare_string(failure_text, "STRONGHOLD_FAILURE_CANCEL_TEXT") then
			failure_text = "MISSION_CANCEL_SUB_TEXT"
		end
	end

	Completion_is_last_screen = true
	Completion.handles.failure = true
	local insertion_text = { [0] = stronghold_name }
	local subtitle = vint_insert_values_in_string("COMPLETION_MISSION_FAILED", insertion_text)

	Completion_force_skip = false
	Completion_is_animating = true

	completion_init_title(mission_type_name, Completion_Gang_Names[team], subtitle)
	completion_init_fail_message(failure_text)
	completion_init_wall(Completion_Gang_Images[team])

	if Sui_mod_mission_title ~= "" then
		-- Mod Mission [nclok1405]
		completion_init_buttons("COMPLETION_RESTART_CHECKPOINT", "COMPLETION_RESTART_BEGINNING", "COMPLETION_EXIT_MISSION")
	else
		completion_init_buttons("COMPLETION_RESTART_CHECKPOINT", "COMPLETION_RETRY_STRONGHOLD", "COMPLETION_EXIT_STRONGHOLD")
	end

	if Completion_coop_disconnected == true then
		completion_coop_disconnected()
	end

	--fade in stuff
	completion_fade_in_wall_and_top(1)
	completion_fail_fade_in(3)

	completion_tips_fade_in_offset(3.5)

	Completion_force_skip = false
	Completion_is_animating = true

end

function completion_init_activity_failure(district, activity_name, level, failure_text, activity_type)
	local fail_reason = failure_text	-- Original Failure Text

	if activity_type == 13 then
		-- Replace fail text of the zombie uprising to final stats [nclok1405]
		district = vint_insert_values_in_string("{0} {1}", {[0] = "ACT_ZOMBIE_HUD_HIGH_SCORE", [1] = format_cash(Sui_zombie_high_score)})
		activity_name = format_cash(Sui_zombie_final_score)
		failure_text = vint_insert_values_in_string("{0}: {1}", {[0] = "STAT_GAME_ZOMBIE_KILLED", [1] = format_cash(Sui_zombie_final_kills)})
	elseif activity_type == 0 or activity_type == 1 or activity_type == 4 or activity_type == 11 or activity_type == 12 or activity_type == 16 then
		-- Activity Score [nclok1405]
		district = "$"..format_cash(Sui_activity_score).."/$"..format_cash(Sui_activity_requirement)
	end

	Completion_is_last_screen = true
	Completion.handles.failure = true
	local insertion_text = { [0] = level }
	completion_init_title(district, activity_name, vint_insert_values_in_string("COMPLETION_ACTIVITY_LEVEL_FAILED", insertion_text))
	completion_init_fail_message(failure_text)
	completion_init_wall(Completion_Activity_Images[activity_type + 1])

	Completion_force_skip = false
	Completion_is_animating = true

	--if this is level 0, then it's a Special Derby... change the button tips
	if level ~= 0 then
		completion_init_buttons("COMPLETION_RETRY_ACTIVITY", nil, "COMPLETION_EXIT_ACTIVITY")
	else
		Completion.handles.level_number = 0
		vint_set_property(Completion.handles.top_3_h, "text_tag", "COMPLETION_FAILED")

		-- Special Derby (changed to Enter) [nclok1405]
		--completion_init_buttons(nil, nil, "COMPLETION_EXIT_ACTIVITY")
		completion_init_buttons("COMPLETION_CONTINUE", nil, nil)
	end

	--change the fail message and tips if this is zombie
	if activity_type == 13 then
		Completion.handles.activity_type = 13
		--vint_set_property(Completion.handles.top_1_h, "text_tag", "")
		vint_set_property(Completion.handles.top_3_h, "text_tag", fail_reason)
		completion_init_buttons("COMPLETION_RETRY_ZOMBIE", nil, "COMPLETION_QUIT_ZOMBIE")
	end

	--fade in stuff
	completion_fade_in_wall_and_top(1)
	completion_fail_fade_in(3)

	completion_tips_fade_in_offset(3.5)

	Completion_force_skip = false
	Completion_is_animating = true

end

function completion_initialize(completion_type, unlockables_to_follow, param3, param4, param5, param6, param7, param8, param9, param10, param11, param12, param13)
	Completion.num_unlocks = unlockables_to_follow
	Completion.type = completion_type

	--[[
	--debug_print("vint", "completion_type: " .. var_to_string( completion_type ) .. "\n" ..
						"unlockables_to_follow: " .. var_to_string( unlockables_to_follow ) .. "\n" ..
						"param3: " .. var_to_string( param3 ) .. "\n" ..
						"param4: " .. var_to_string( param4 ) .. "\n" ..
						"param5: " .. var_to_string( param5 ) .. "\n" ..
						"param6: " .. var_to_string( param6 ) .. "\n" ..
						"param7: " .. var_to_string( param7 ) .. "\n" ..
						"param8: " .. var_to_string( param8 ) .. "\n" ..
						"param9: " .. var_to_string( param9 ) .. "\n" ..
						"param10: " .. var_to_string( param10 ) .. "\n" ..
						"param11: " .. var_to_string( param11 ) .. "\n" ..
						"param12: " .. var_to_string( param12 ) .. "\n" ..
						"param13: " .. var_to_string( param13 ) .. "\n\n")
	]]

	-- Skip activity cancel failure screen (for demo derby) [nclok1405]
	if Sui_skip_activity_cancel_fail_screen and (completion_type == FAILURE_ACTIVITY) and sui_compare_string(param6, "ACTIVITY_FAILURE_CANCEL_TEXT") and (not Completion_is_coop()) then
		Sui_skip_activity_cancel_fail_screen = false
		completion_call_callback(COMPLETION_EXIT)
		Completion.exiting = true
		thread_yield()
		completion_finish()
		if Sui_hud_enable == 0 then
			hud_hide(true)
		else
			hud_hide(false)
		end
		return
	end

	-- If Special Derby is failed, exit quickly and show the fail text in freeroam (the only option was exit anyway) [nclok1405]
	-- param5 = level, param6 = failure_text
	if (completion_type == FAILURE_ACTIVITY) and (param5 == 0) and (not Completion_is_coop()) then
		Sui_mission_fail_text = vint_insert_values_in_string("{0}\n${1}/${2}", {[0] = param6, [1] = format_cash(Sui_activity_score), [2] = format_cash(Sui_activity_requirement)})
		completion_call_callback(COMPLETION_EXIT)
		Completion.exiting = true
		thread_yield()
		completion_finish()
		if Sui_hud_enable == 0 then
			hud_hide(true)
		else
			hud_hide(false)
		end
		return
	end

	if completion_type == SUCCESS_MISSION then
		completion_init_mission_success(param3, param4, param5, param6, param7, param8, param9, param10, param11, param12, param13)
	elseif completion_type == SUCCESS_STRONGHOLD then
		completion_init_stronghold_success(param3, param4, param5, param6, param7, param8, param9, param10, param11, param12)
	elseif completion_type == SUCCESS_ACTIVITY then
		completion_init_activity_success(param3, param4, param5, param6, param7, param11, param9, param10, param8, param12, param13)
	elseif completion_type == FAILURE_MISSION then
		Completion_coop_disconnected = param8
		completion_init_mission_failure(param3, param4, param5, param6, param7)
	elseif completion_type == FAILURE_STRONGHOLD then
		Completion_coop_disconnected = param6
		completion_init_stronghold_failure(param3, param4, param5)
	elseif completion_type == FAILURE_ACTIVITY then
		completion_init_activity_failure(param3, param4, param5, param6, param7)
	elseif completion_type == JUST_UNLOCKS then
		completion_init_just_unlocks(param3, param4)
	elseif completion_type == UNLOCK_REWARD then
		--	Do something yo'
		completion_init_unlock(param3, param4, param5)
	elseif completion_type == SUCCESS_PUSHBACK then
		completion_init_pushback_success(param3, param4, param5, param6)
	end

end

--Top Area
function completion_init_title(pretitle, title, subtitle)
	if pretitle == nil then
		vint_set_property(Completion.handles.top_1_h, "visible", false)
		local top_x, top_y = vint_get_property(Completion.handles.top_grp_h, "anchor")
		top_y = top_y - 26
		vint_set_property(Completion.handles.top_grp_h, "anchor", top_x,  top_y)
	else
		vint_set_property(Completion.handles.top_1_h, "text_tag", pretitle)
	end

	vint_set_property(Completion.handles.top_2_h, "text_tag", title)
	vint_set_property(Completion.handles.top_3_h, "text_tag", subtitle)
end

-- Cash/Respect
function completion_init_cash_respect(cash, respect)
	if (cash ~= nil) and (cash > 0) then
		vint_set_property(Completion.handles.cash_t_h, "text_tag", "COMPLETION_CASH")
		vint_set_property(Completion.handles.cash_v_h, "text_tag", "$0")
	else
		vint_set_property(Completion.handles.cash_t_h, "text_tag", "")
		vint_set_property(Completion.handles.cash_v_h, "text_tag", "")
	end

	if (respect ~= nil) and (respect > 0) then
		vint_set_property(Completion.handles.respect_t_h, "text_tag", "COMPLETION_RESPECT")
		vint_set_property(Completion.handles.respect_v_h, "text_tag", "0")
	else
		-- Hide the respect
		vint_set_property(Completion.handles.respect_v_h, "visible", false)
	end
end

function completion_move_unlockable_text(move_up)
	if move_up == true then
		vint_set_property(Completion.handles.unlock_h, "anchor", 104, 162)
	else
		vint_set_property(Completion.handles.unlock_h, "anchor", 104, 202)
	end
end

function completion_init_just_unlocks(title, description)
	--title = "TITLE"
	--description = "DESCRIPTION"
	completion_init_title(nil, title, description)
	completion_init_wall("blank")
	Completion.just_unlocks = true
	Completion.just_unlocks_really = true

	Completion_force_skip = false
	Completion_is_animating = true

	completion_move_unlockable_text(true)

	--fade in stuff
	completion_fade_in_wall_and_top(0)

	vint_dataresponder_request("completion_populate", "completion_initialize", 0, Completion.cur_unlock)
	Completion.cur_unlock = Completion.cur_unlock + 1
end

-- Unlocks
function completion_init_unlock(name, image, description)
	Completion.unlock = {
		name = name,
		description = description,
		image = image,
	}

	if Completion.just_unlocks == true then
		completion_finish_unlock()
		return
	end

	--block input for the fade outs
	Completion.input_block = true

	-- Fade out everything
	completion_cr_cash_fade_out(0)
	completion_cr_respect_fade_out(0)
	completion_hood_cash_fade_out(0)
	completion_hood_owned_fade_out(0)
	completion_news_clip_fade_out(0)
	completion_tips_fade_out(0)
	completion_unlock_fade_out(0)
	completion_unlock_desc_fade_out(0)

	--unload the old pegs on call back

	local tween_h = vint_object_find("t_unlock_fade_out", Completion.handles.unlock_fade_out_anim_h)
	vint_set_property(tween_h, "end_event", "completion_shut_off_all_layers")

	local tween_h = vint_object_find("unlock_fade_out_ender", Completion.handles.unlock_fade_out_anim_h)
	vint_set_property(tween_h, "start_event", "completion_unload_pegs")

	--load the new peg, start the next function
	local tween_h = vint_object_find("unlock_fade_out_ender", Completion.handles.unlock_fade_out_anim_h)
	vint_set_property(tween_h, "end_event", "completion_finish_unlock")

end



function completion_finish_unlock()
	if Completion.is_respect_screen == true then
		return
	end

	--allow inputs so the animations can be skipped
	Completion.input_block = false

	completion_load_peg(Completion.unlock.image)

	completion_move_unlockable_text(false)

	--	was this started by just unlocks?  if so, set the first delay time to be .5
	local delay_time = .50

	if Completion.just_unlocks_really == true and Completion.just_unlocks == true then
		delay_time = 2.5
	end

	Completion.just_unlocks = false

	Completion_force_skip = false
	Completion_is_animating = true
	Completion_is_hood_screen = false

	local text_anchor = 305

	vint_set_property(Completion.handles.t_unlock_h, "text_tag", "COMPLETION_UNLOCKED")
	vint_set_property(Completion.handles.thing_name_h, "text_tag", Completion.unlock.name)
	vint_set_property(Completion.handles.thing_desc_h, "text_tag", Completion.unlock.description )
	vint_set_property(Completion.handles.thing_image_h, "image", Completion.unlock.image .. "")

	vint_set_property(Completion.handles.t_unlock_h, "anchor", text_anchor, 0)

	local name_x, name_y = vint_get_property(Completion.handles.thing_name_h, "anchor")
	vint_set_property(Completion.handles.thing_name_h, "anchor", text_anchor, name_y)

	local desc_x, desc_y = vint_get_property(Completion.handles.thing_desc_h, "anchor")
	vint_set_property(Completion.handles.thing_desc_h, "anchor", text_anchor, desc_y)

	vint_set_property(Completion.handles.thing_image_h, "anchor", -10, 0 )
	vint_set_property(Completion.handles.tips_h, "anchor", 104.5, 610)

	-- Fade in things
	completion_unlock_fade_in(delay_time)

	local tween_h = vint_object_find("unlock_ender", Completion.handles.unlock_fade_in_anim_h)
	vint_set_property(tween_h, "end_event", "completion_unlock_desc_fade_in")

	local tween_h = vint_object_find("unlock_desc_ender", Completion.handles.unlock_desc_fade_in_anim_h)
	vint_set_property(tween_h, "end_event", "completion_tips_fade_in")

	if Completion.handles.cur_respect ~= nil and Completion.handles.props_to_unlock ~= nil then
		if Completion.num_unlocks == Completion.cur_unlock and Completion.handles.cur_respect < Completion.handles.props_to_unlock then
			Completion_is_last_screen = true
		end
	end

	if Completion.cur_unlock == Completion.num_unlocks then

		if Completion.reward_source == SUCCESS_ACTIVITY then
			if Completion.last_level == true then
				if Completion.handles.activity_type == 13 then
					completion_init_buttons("COMPLETION_QUIT_ZOMBIE", nil, nil)
				else
					completion_init_buttons("COMPLETION_EXIT_ACTIVITY", nil, nil)
				end
			else
				completion_init_buttons("COMPLETION_CONTINUE_ACTIVITY", nil, "COMPLETION_EXIT_ACTIVITY")
			end
		else
			completion_init_buttons("COMPLETION_CONTINUE")
		end

	else
		completion_init_buttons("COMPLETION_CONTINUE", nil, nil)
	end

	if Completion_show_respect_screen == true then
		completion_init_buttons("COMPLETION_CONTINUE", nil, nil)
	end

	completion_move_mission_tips()

end


--hood unlock only
function completion_hood_unlock()


	local tween_h = vint_object_find("news_image_alpha", Completion.handles.news_clip_fade_out_anim_h)
	vint_set_property(tween_h, "end_event", nil)

	local tween_h = vint_object_find("news_image_fade_out_ender", Completion.handles.news_clip_fade_out_anim_h)
	vint_set_property(tween_h, "start_event", nil)

	local tween_h = vint_object_find("news_image_fade_out_ender", Completion.handles.news_clip_fade_out_anim_h)
	vint_set_property(tween_h, "end_event", nil)

	local cur_respect = 	Completion.handles.cur_respect
	local props_to_unlock = Completion.handles.props_to_unlock


	if Completion.num_unlocks == 0 and cur_respect < props_to_unlock then
		Completion_is_last_screen = true
	end


	--init the hood
	local cash_per_day =	Completion_cash_per_day.cash
	local image_base = 		Completion_cash_per_day.image_base
	local hood_name =		Completion_cash_per_day.hood_name
	local hoods_owned =		Completion_cash_per_day.hoods_owned
	local hoods_total =		Completion_cash_per_day.hoods_total

	Completion.input_block = false

	completion_init_hood(cash_per_day, image_base, hood_name, hoods_owned, hoods_total)

	Completion.just_unlocks = false
	Completion_is_hood_screen = true
	Completion_force_skip = false
	Completion_is_animating = true

	completion_init_buttons("COMPLETION_CONTINUE", nil, nil)


	completion_move_unlockable_text(false)

	-- Fade in things
	vint_set_property(Completion.handles.unlock_h, "visible", true)
	completion_unlock_fade_in(.5)

	--hood cash callback
	local tween_h = vint_object_find("unlock_ender", Completion.handles.unlock_fade_in_anim_h)
	vint_set_property(tween_h, "end_event", "completion_hood_cash_fade_in")

	--animate hood_cash callback
	local tween_h = vint_object_find("hood_cash_ender", Completion.handles.hood_cash_fade_in_anim_h)
	vint_set_property(tween_h, "end_event", "completion_animate_hood_cash")

	completion_move_mission_tips()

end

-- Hood
function completion_init_hood(cash_per_day, image_base, hood_name, hoods_owned, hoods_total)

	--load the post card peg
	if image_base ~= nil then
		completion_load_peg("ui_c_hood_" .. image_base)
		vint_set_property(Completion.handles.thing_image_h, "image", "ui_ct_hood_" .. image_base .. ".tga")
	end

	if hood_name ~= nil then
		vint_set_property(Completion.handles.t_unlock_h, "text_tag", "COMPLETION_NEIGHBORHOOD_GAINED")
		vint_set_property(Completion.handles.thing_name_h, "text_tag", hood_name)
	end

	if get_language() ~= "US" and get_language() ~= "UK" then
		local name_x, name_y = vint_get_property(Completion.handles.thing_name_h, "anchor")
		vint_set_property(Completion.handles.thing_name_h, "anchor", name_x, name_y)

		local image_x, image_y = vint_get_property(Completion.handles.thing_image_h, "anchor")
		vint_set_property(Completion.handles.thing_image_h, "anchor", image_x, image_y + 12)

		vint_set_property(Completion.handles.unlock_h, "anchor", 104, 222)
	end

	vint_set_property(Completion.handles.hood_cash_v_h, "text_tag", "$0")

	if hoods_owned ~= nil and hoods_total ~= nil then
		vint_set_property(Completion.handles.hood_cash_t_h, "text_tag", "COMPLETION_CASH_PER_DAY")
		vint_set_property(Completion.handles.hood_owned_t_h, "text_tag", "COMPLETION_NEIGHBORHOODS_OWNED")
		vint_set_property(Completion.handles.hood_owned_v_h, "text_tag", (hoods_owned + 1) .. "/" .. hoods_total)
	end

end

function completion_init_cash_reward()
	vint_set_property(Completion.handles.hood_cash_v_h, "text_tag", "$0")
	vint_set_property(Completion.handles.hood_cash_t_h, "text_tag", "COMPLETION_CASH")
end

-- Specific to mission/activity
function completion_init_wall(name)
	peg_load("ui_c_wall_" .. name)
	Completion.handles.wall = name
	vint_set_property(Completion.handles.wall_h, "image", "ui_ct_wall_" .. name .. ".tga")
end

--tips
function completion_init_buttons(a_button, x_button, b_button)

	if Completion_is_last_screen == true and Completion_is_coop() == true then
		completion_coop_waiting()
	else
		if a_button ~= nil then
			Completion.a_available = true
			vint_set_property(Completion.handles.tip_1_h, "visible", true)
			vint_set_property(Completion.handles.btn_1_h, "visible", true)
			vint_set_property(Completion.handles.tip_1_h, "text_tag", a_button)
			vint_set_property(Completion.handles.btn_1_h, "image", get_a_button())
		else
			Completion.a_available = false
			vint_set_property(Completion.handles.tip_1_h, "visible", false)
			vint_set_property(Completion.handles.btn_1_h, "visible", false)
		end

		if x_button ~= nil then
			Completion.x_available = true
			vint_set_property(Completion.handles.tip_2_h, "visible", true)
			vint_set_property(Completion.handles.btn_2_h, "visible", true)
			vint_set_property(Completion.handles.tip_2_h, "text_tag", x_button)
			vint_set_property(Completion.handles.btn_2_h, "image", get_x_button())
		else
			Completion.x_available = false
			vint_set_property(Completion.handles.tip_2_h, "visible", false)
			vint_set_property(Completion.handles.btn_2_h, "visible", false)
		end

		if b_button ~= nil then
			Completion.b_available = true
			local tip_h, btn_h
			if x_button == nil then
				tip_h = Completion.handles.tip_2_h
				btn_h = Completion.handles.btn_2_h
			else
				tip_h = Completion.handles.tip_3_h
				btn_h = Completion.handles.btn_3_h
			end
			vint_set_property(tip_h, "visible", true)
			vint_set_property(btn_h, "visible", true)

			vint_set_property(btn_h, "image", get_b_button())
			vint_set_property(tip_h, "text_tag", b_button)
		else
			Completion.b_available = false
		end

		if b_button == nil or x_button == nil then
			vint_set_property(Completion.handles.tip_3_h, "visible", false)
			vint_set_property(Completion.handles.btn_3_h, "visible", false)
		end

	end

	--do the back (quit to main menu) button
	if Completion_is_coop() == true then
		local button = "ui_ctrl_360_btn_back"
		if SUI_PLATFORM == "PS3" then
			button = "ui_ctrl_ps3_btn_select"
		elseif SUI_PLATFORM == "PC" then
			button = "ui_ctrl_PC_key_tab"
		end
		vint_set_property(Completion.handles.quit_to_main_btn, "image", button)
		local w, h = element_get_actual_size(Completion.handles.quit_to_main_text)
		vint_set_property(Completion.handles.quit_to_main_btn, "anchor", -w, 1)
		vint_set_property(Completion.handles.quit_to_main, "visible", true)
	else
		vint_set_property(Completion.handles.quit_to_main, "visible", false)
	end


end

--coop, hides the button tips, shows the waiting message
function completion_coop_waiting()
		lua_play_anim(Completion.handles.waiting_anim , 0)
		lua_play_anim(Completion.handles.waiting_fade_in , 0)
		vint_set_property(Completion.handles.waiting, "visible", true)
		vint_set_property(Completion.handles.btn_1_h, "visible", false)
		vint_set_property(Completion.handles.btn_2_h, "visible", false)
		vint_set_property(Completion.handles.btn_3_h, "visible", false)
		vint_set_property(Completion.handles.tip_1_h , "visible", false)
		vint_set_property(Completion.handles.tip_2_h , "visible", false)
		vint_set_property(Completion.handles.tip_3_h , "visible", false)
end

--Fail message
function completion_init_fail_message(message)
	vint_set_property(Completion.handles.top_3_h, "tint", 0.7, 0, 0)		--turn 'subtitle' text red
	vint_set_property(Completion.handles.top_3_h, "visible", true)
	vint_set_property(Completion.handles.fail_msg_h , "text_tag", message)

	local w,h = element_get_actual_size(Completion.handles.fail_msg_h)
	local x, y = vint_get_property(Completion.handles.fail_msg_h, "anchor")
	x = vint_get_property(Completion.handles.tips_h, "anchor")

	vint_set_property(Completion.handles.tips_h, "anchor", x, y + h + COMPLETION_UNLOCK_SPACE)
end


--animation functions

function completion_screen_shake()

	lua_play_anim(Completion.handles.screen_shake, 0)
end

function completion_fade_in_wall_and_top(offset)
	Completion_is_animating = true

	vint_set_property(Completion.handles.top_grp_h, "visible", true)
	vint_set_property(Completion.handles.wall_h, "visible", true)
	--set up the sound stuff
	local tween_h = vint_object_find("top_1_pos", Completion.handles.top_grp_anim_h)

		if Completion.handles.failure == true then
			--play the fail sound
			vint_set_property(tween_h, "start_event", "completion_top_fail_sound")
		elseif Completion.just_unlocks == true then
			--play just top 2 sound
			local tween_h = vint_object_find("top_2_pos", Completion.handles.top_grp_anim_h)
			vint_set_property(tween_h, "start_event", "completion_top_2_sound")
		else
			--play all top 3 sound
			vint_set_property(tween_h, "start_event", "completion_top_3_sound")
		end


	--do the animations
	lua_play_anim(Completion.handles.black_1_anim_h, offset )
	lua_play_anim(Completion.handles.wall_anim_h, offset + 0.33 )
	lua_play_anim(Completion.handles.top_grp_anim_h, offset + 1)

end



function completion_fail_fade_in(offset)
	vint_set_property(Completion.handles.fail_msg_h, "visible", true)

	lua_play_anim(Completion.handles.fail_fade_in_anim_h, offset)

	if Completion_force_skip == false then

		local	tween_h = vint_object_find("fail_fade_in", Completion.handles.fail_fade_in_anim_h)
		vint_set_property(tween_h, "start_event", "completion_text_sound")
	end
end


function completion_cr_cash_fade_in()
	vint_set_property(Completion.handles.cash_respect_h, "visible", true)

	lua_play_anim(Completion.handles.cr_cash_fade_in_anim_h, 0)
	if Completion_force_skip == false then
		local	tween_h = vint_object_find("cash_t_alpha", Completion.handles.cr_cash_fade_in_anim_h)
		vint_set_property(tween_h, "start_event", "completion_cash_sound")
	end
end

function completion_cr_cash_fade_out(offset)
	lua_play_anim(Completion.handles.cr_cash_fade_out_anim_h, offset)
end

function completion_cr_respect_fade_in(offset)
	vint_set_property(Completion.handles.cash_respect_h, "visible", true)
	lua_play_anim(Completion.handles.cr_respect_fade_in_anim_h, offset)
	if Completion_force_skip == false then
		local	tween_h = vint_object_find("respect_t_alpha", Completion.handles.cr_respect_fade_in_anim_h)
		vint_set_property(tween_h, "start_event", "completion_respect_sound")
	end
end

function completion_cr_respect_fade_in_now()
	vint_set_property(Completion.handles.cash_respect_h, "visible", true)

	lua_play_anim(Completion.handles.cr_respect_fade_in_anim_h, 0)
	if Completion_force_skip == false then
		local	tween_h = vint_object_find("respect_t_alpha", Completion.handles.cr_respect_fade_in_anim_h)
		vint_set_property(tween_h, "start_event", "completion_respect_sound")
	end

end

function completion_style_bonus_fade_in()
	vint_set_property(Completion.handles.style_grp, "visible", true)

	lua_play_anim(Completion.handles.style_grp_anim, .4)

	if Completion_force_skip == false then
		local	tween_h = vint_object_find("style_alpha", Completion.handles.style_grp_anim)
		vint_set_property(tween_h, "start_event", "completion_respect_sound")
	end
end

function completion_cr_respect_fade_out(offset)
	lua_play_anim(Completion.handles.cr_respect_fade_out_anim_h, offset)
	lua_play_anim(Completion.handles.style_grp_fade_out_anim, offset)
end

function completion_hood_cash_fade_in()
	vint_set_property(Completion.handles.hood_cash_t_h, "visible", true)
	vint_set_property(Completion.handles.hood_cash_v_h, "visible", true)

	lua_play_anim(Completion.handles.hood_cash_fade_in_anim_h, 0)
	if Completion_force_skip == false then
		local	tween_h = vint_object_find("hood_cash_t_alpha", Completion.handles.hood_cash_fade_in_anim_h)
		vint_set_property(tween_h, "start_event", "completion_cash_sound")
	end
end

function completion_hood_cash_fade_out(offset)
	lua_play_anim(Completion.handles.hood_cash_fade_out_anim_h, offset)
end

function completion_hood_owned_fade_in(offset)
	vint_set_property(Completion.handles.hood_owned_t_h, "visible", true)
	vint_set_property(Completion.handles.hood_owned_v_h, "visible", true)

	lua_play_anim(Completion.handles.hood_owned_fade_in_anim_h, offset)

	if Completion_force_skip == false then
		local	tween_h = vint_object_find("hood_owned_t_alpha", Completion.handles.hood_owned_fade_in_anim_h)
		vint_set_property(tween_h, "start_event", "completion_respect_sound")
		local	tween_h = vint_object_find("hood_owned_v_alpha", Completion.handles.hood_owned_fade_in_anim_h)
		vint_set_property(tween_h, "start_event", "completion_text_sound")
	end

end

function completion_hood_owned_fade_out(offset)
	lua_play_anim(Completion.handles.hood_owned_fade_out_anim_h, offset)
end

function completion_news_clip_fade_in()
	vint_set_property(Completion.handles.thing_image_h, "visible", true)

	lua_play_anim(Completion.handles.news_clip_fade_in_anim_h, 0)
	if Completion_force_skip == false then

		local tween_h = vint_object_find("news_image_scale", Completion.handles.news_clip_fade_in_anim_h)
		vint_set_property(tween_h, "start_event", "completion_image_sound")
	end

end

function completion_news_clip_fade_out(offset)
	lua_play_anim(Completion.handles.news_clip_fade_out_anim_h, offset)
end

function completion_hide_image()
	vint_set_property(Completion.handles.thing_image_h, "visible", false)
end


function completion_unlock_fade_in(offset)
	if offset == nil then
		offset = 0
	end

	vint_set_property(Completion.handles.unlock_h, "visible", true)
	vint_set_property(Completion.handles.t_unlock_h, "visible", true)
	vint_set_property(Completion.handles.thing_name_h, "visible", true)
	vint_set_property(Completion.handles.thing_image_h, "visible", true)

	lua_play_anim(Completion.handles.unlock_fade_in_anim_h, offset)

	if Completion_force_skip == false then

		local tween_h = vint_object_find("unlock_1_t_pos", Completion.handles.unlock_fade_in_anim_h)
		vint_set_property(tween_h, "start_event", "completion_top_2_sound")

		local tween_h = vint_object_find("unlock_3_image_pos", Completion.handles.unlock_fade_in_anim_h)
		vint_set_property(tween_h, "start_event", "completion_image_sound")
	end
end


function completion_unlock_fade_out(offset)
	lua_play_anim(Completion.handles.unlock_fade_out_anim_h, offset)
end

function completion_unlock_desc_fade_in()
	vint_set_property(Completion.handles.thing_desc_h, "visible", true)

	lua_play_anim(Completion.handles.unlock_desc_fade_in_anim_h, 0)
	if Completion_force_skip == false then

		local tween_h = vint_object_find("thing_desc_alpha_in", Completion.handles.unlock_desc_fade_in_anim_h)
		vint_set_property(tween_h, "start_event", "completion_text_sound")
	end
end

function completion_unlock_desc_fade_out(offset)
	lua_play_anim(Completion.handles.unlock_desc_fade_out_anim_h, offset)

end

function completion_tips_fade_in()
	--debug_print("freese", "Completion_allow_to_shut_off_layers set to true in completion_tips_fade_in\n")
	Completion_allow_to_shut_off_layers = true
	Completion_is_animating = false
	vint_set_property(Completion.handles.tips_h, "visible", true)
	lua_play_anim(Completion.handles.tips_fade_in_anim_h, 0)
	if Completion_force_skip == false then
		local tween_h = vint_object_find("tips_fade_in", Completion.handles.tips_fade_in_anim_h)
		vint_set_property(tween_h, "start_event", "completion_tips_sound")

	end
	if Completion_is_coop() == true and Completion_is_last_screen == true then
		completion_coop_waiting()
	end
end

function completion_tips_fade_in_offset(offset)
	--debug_print("freese", "Completion_allow_to_shut_off_layers set to true in completion_tips_fade_in_offset\n")
	Completion_allow_to_shut_off_layers = true
	vint_set_property(Completion.handles.tips_h, "visible", true)
	lua_play_anim(Completion.handles.tips_fade_in_anim_h, offset)
	if Completion_force_skip == false then
		local tween_h = vint_object_find("tips_fade_in", Completion.handles.tips_fade_in_anim_h)
		vint_set_property(tween_h, "start_event", "completion_tips_sound")

	end
	if Completion_is_coop() == true and Completion_is_last_screen == true then
		completion_coop_waiting()
	end

	local tween_h = vint_object_find("tips_fade_in", Completion.handles.tips_fade_in_anim_h)
	vint_set_property(tween_h, "end_event", "completion_animating_false")
end

function completion_animating_false()
	Completion_is_animating = false
end

function completion_tips_fade_out(offset)
	lua_play_anim(Completion.handles.waiting_fade_out , offset)
	lua_play_anim(Completion.handles.tips_fade_out_anim_h, offset )
end

function completion_fade_out_all(offset)
	lua_play_anim(Completion.handles.black_2_anim_h, offset)
end

function completion_top_grp_fade_out(offset)
	lua_play_anim(Completion.handles.top_grp_fade_out_anim_h, offset)
end

function completion_shut_off_all_layers()
	--debug_print("freese", "Testing Completion_allow_to_shut_off_layers in completion_shut_off_all_layers.... ")

	if Completion_allow_to_shut_off_layers == false then
		--debug_print("freese", "not allowed \n")
		return
	end



	--debug_print("freese", "allowed allowed setting false for later.\n")
	Completion_allow_to_shut_off_layers = false

	--turn off all layers
	vint_set_property(Completion.handles.cash_respect_h, "visible", false)
	vint_set_property(Completion.handles.fail_msg_h, "visible", false)
	vint_set_property(Completion.handles.tips_h, "visible", false)
	--vint_set_property(Completion.handles.unlock_h, "visible", false)
	vint_set_property(Completion.handles.t_unlock_h, "visible", false)
	vint_set_property(Completion.handles.thing_desc_h, "visible", false)
	vint_set_property(Completion.handles.thing_image_h, "visible", false)
	vint_set_property(Completion.handles.thing_name_h, "visible", false)
	vint_set_property(Completion.handles.hood_cash_t_h, "visible", false)
	vint_set_property(Completion.handles.hood_cash_v_h, "visible", false)
	vint_set_property(Completion.handles.hood_owned_t_h, "visible", false)
	vint_set_property(Completion.handles.hood_owned_v_h, "visible", false)
	vint_set_property(Completion.handles.style_grp, "visible", false)

	if Completion.is_respect_screen == true then
		Completion_reset_respect_screen()
	end

	if Completion.exiting == true then
		vint_set_property(Completion.handles.top_grp_h, "visible", false)
		vint_set_property(Completion.handles.black_1_h, "visible", true)
		vint_set_property(Completion.handles.wall_h, "visible", false)
		completion_finish()
	end


end

-------------------------------
--SOUND


function completion_top_3_sound()
	if Completion_is_animating == true then
		audio_play(Completion_audio.top_3)
	end
end

function completion_top_2_sound()
	if Completion_is_animating == true then
		audio_play(Completion_audio.top_2)
	end
end

function completion_top_fail_sound()
	if Completion_is_animating == true then
		audio_play(Completion_audio.fail)
	end
end

function completion_image_sound()
	if Completion_is_animating == true then
		audio_play(Completion_audio.image)
	end
end

function completion_text_sound()
	if Completion_is_animating == true then
		audio_play(Completion_audio.text)
	end
end

function completion_respect_sound()
	if Completion_is_animating == true then
		audio_play(Completion_audio.respect)
	end
end

function completion_cash_sound()
	if Completion_is_animating == true then
		audio_play(Completion_audio.cash)
	end
end

function completion_tips_sound()
	--if Completion_is_animating == true then
		audio_play(Completion_audio.tips)
--	end
end

function completion_cash_count_sound()
	if Completion_is_animating == true then
		audio_play(Completion_audio.cash_count)
	end
end

function completion_respect_count_sound()
	if Completion_is_animating == true then
		audio_play(Completion_audio.respect_count)
	end
end


--------------------------------------------
--Store count of animation threads
Completion_anim_thread_count = 0
Completion_force_skip = false

function completion_anim_threads_is_killed()
	return Completion_force_skip
end

function completion_anim_threads_kill()
	Completion_force_skip = true
end

function completion_anim_threads_unkill()

end


--------------------------------------------
--sound delay stuff
function completion_sound_play_delay(sound_id, offset)
	thread_new("completion_sound_play_thread", sound_id, offset)
end

function completion_sound_play_thread(sound_id, offset)
	delay(offset)
	audio_play(sound_id)
end
