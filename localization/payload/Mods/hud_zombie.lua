-- hud_zombie.lua: Zombie Uprising HUD
-- Zombie Uprising HUD Mod [nclok1405]

-- Disable All HUD
MOD_ZOMBIE_HUD_DISABLE = false

Hud_zombie = {
	handles = {},
}
--

function hide_stuff(name)
	local h = vint_object_find(name)
	if h > 0 then
		vint_set_property(h, "visible", false)
	end
end

function move_stuff(name, offsetX, offsetY)
	local h = vint_object_find(name)
	if h > 0 then
		local x, y = vint_get_property(h, "anchor")
		vint_set_property(h, "anchor", x + offsetX, y + offsetY)
	end
end

function hud_zombie_init()
	local h = -1

	peg_load("ui_hud_zombie")

	--players
	Hud_zombie.handles.players = vint_object_find("players")

		--player 1
		Hud_zombie.handles.player_1 = vint_object_find("player_1")
		h = Hud_zombie.handles.player_1
		Hud_zombie.handles.health_1 = vint_object_find("health_1", h)
		Hud_zombie.handles.head_1 = vint_object_find("head_1", h)

		--player 2
		Hud_zombie.handles.player_2 = vint_object_find("player_2")
		h = Hud_zombie.handles.player_2
		Hud_zombie.handles.health_2 = vint_object_find("health_2", h)
		Hud_zombie.handles.head_2 = vint_object_find("head_2", h)

	--score grp
	Hud_zombie.handles.score_grp = vint_object_find("score_grp")
	h = Hud_zombie.handles.score_grp
	Hud_zombie.handles.main_score_num = vint_object_find("main_score_num", h)
	Hud_zombie.handles.high_score_num = vint_object_find("high_score_num", h)

	--STATS zombies left + killed
	Hud_zombie.handles.stats = vint_object_find("stats")
	h = Hud_zombie.handles.stats
	Hud_zombie.handles.zombies_killed_num = vint_object_find("zombies_killed_num", h)
	Hud_zombie.handles.zombies_left_num = vint_object_find("zombies_left_num", h)

	vint_dataitem_add_subscription("sr2_local_player_hud_zombie", "update", "hud_zombie_update")

	-- Hide Everything [nclok1405]
	if MOD_ZOMBIE_HUD_DISABLE or (Sui_hud_enable < 2) then
		hide_stuff("zombie")
	end

	if Sui_normal_hud_in_zombie then
		hide_stuff("hud_work")
		hide_stuff("hud_btm")
		hide_stuff("grit_stats_1")
		hide_stuff("grit_stats_2")
		hide_stuff("grit_stats_3")
		hide_stuff("grit_stats_4")
		hide_stuff("grit_score_1")
		hide_stuff("grit_score_2")
		--hide_stuff("stats")
		hide_stuff("players")
		hide_stuff("score_grp")

		move_stuff("stats", 0, -455)

		--[[
		if vint_hack_is_std_res() == false then
			move_stuff("player_1", 950, 0)
			move_stuff("player_2", 740, 0)
		else
			move_stuff("player_1", 700, 0)
			move_stuff("player_2", 490, 0)
		end
		--]]
	end
end

function hud_zombie_cleanup()
	peg_unload("ui_hud_zombie")
end

function hud_zombie_update(di_h, event)

	local score, high_score, health_1, health_2, zombies_left, zombies_killed = vint_dataitem_get(di_h)

	-- Record current stats to global variables in vint_lib.lua [nclok1405]
	Sui_zombie_final_score = score
	Sui_zombie_final_kills = zombies_killed
	Sui_zombie_high_score = high_score

	local p1 = Hud_zombie.handles.player_1
	local p1_health = Hud_zombie.handles.health_1
	local p2 = Hud_zombie.handles.player_2
	local p2_health = Hud_zombie.handles.health_2

	--current score
	vint_set_property(Hud_zombie.handles.main_score_num, "text_tag", format_cash(score))

	--high score
	vint_set_property(Hud_zombie.handles.high_score_num, "text_tag", format_cash(high_score))

	--zombies
	vint_set_property(Hud_zombie.handles.zombies_killed_num, "text_tag", format_cash(zombies_killed))
	vint_set_property(Hud_zombie.handles.zombies_left_num, "text_tag", format_cash(zombies_left))

	--player 1
	vint_set_property(p1_health, "text_tag", ceil(health_1 * 100))

	--player 2
	if health_2 == -1 or health_2 < 0 then
		vint_set_property(p2, "visible", false)
	else
		vint_set_property(p2, "visible", true)
		vint_set_property(p2_health, "text_tag", ceil(health_2 * 100))
	end
end
