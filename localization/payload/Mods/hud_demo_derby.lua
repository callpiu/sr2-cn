-- hud_demo_derby.lua: Demolition Derby HUD, handles health bars of everyone

-- Modern HUD Options for Demolition Derby [nclok1405]

-- Tint the car icon to red depending on remaining health
MODERN_HUD_DD_TINT_CAR_ICON = true

Hud_dd_status = {

	--Player Info
	player_grp = { },

	player = {
		health_pct = -1,
	},
	health_bar = 	{ bg_h = 0, fill_0_h = 0,  fill_1_h = 0, fill_decay_h = 0,
						fill_start_angle = PI + 0.03, fill_end_angle = PI2  - 0.03, angle_offset = 0.045,
						anim = 0, anim_delay_start = .25, anim_delay = .25, anim_delay_decay = .9,
						is_flashing = false, hits = 0, last_hit_time = 0,

	},


	--Coop Info
	coop = {	health_pct = -1, grp_h = 0, fill_h = 0,  car_h = 0,
	},

	--Hostiles Info
	hostiles = { },

	hostile_elements = {
		grp_h = 0, fill_h = 0, border_h = 0,
	},

	anims = { },

	anim_elements = {
		hostile_anim_h = 0,
	},

	old_time = 0,

	handles = {},

}

Hud_dd_health_flash_status = {
	is_flashing = false,
	is_queued = false,
	last_flash_time_index = 0
}


function hud_demo_derby_init()
	peg_load("ui_demo_derby")

	--Player Health
	--handle
	local h = vint_object_find("health_grp")
	local bar = Hud_dd_status.health_bar
	bar.bg_h = vint_object_find("health_bar_bg", h)
	bar.fill_0_h = vint_object_find("health_bar_fill_0", h)
	bar.fill_1_h = vint_object_find("health_bar_fill_1", h)
	bar.fill_decay_h = vint_object_find("health_bar_fill_decay", h)

	Hud_dd_status.handles.health_grp = vint_object_find("health_grp")

	-- Move anything related to health bar [nclok1405]
	if Sui_hud_modern_layout then
		local hx, hy = vint_get_property(Hud_dd_status.handles.health_grp, "anchor")

		if vint_hack_is_std_res() == false then
			vint_set_property(Hud_dd_status.handles.health_grp, "anchor", hx - 5, hy + 460)	-- 16:9
		else
			vint_set_property(Hud_dd_status.handles.health_grp, "anchor", hx - 5, hy + 300)	-- 4:3
		end
	end

	--Reset angles on health meter
	vint_set_property(bar.bg_h, 			"start_angle",		bar.fill_start_angle - bar.angle_offset)
	vint_set_property(bar.bg_h, 			"end_angle", 		bar.fill_end_angle + bar.angle_offset)
	vint_set_property(bar.fill_0_h,		"start_angle", 	bar.fill_start_angle)
	vint_set_property(bar.fill_0_h, 		"end_angle", 		bar.fill_end_angle)
	vint_set_property(bar.fill_1_h, 		"start_angle",		bar.fill_start_angle)
	vint_set_property(bar.fill_1_h, 		"end_angle", 		bar.fill_end_angle)
	vint_set_property(bar.fill_decay_h, "start_angle",		bar.fill_start_angle)
	vint_set_property(bar.fill_decay_h, "end_angle", 		bar.fill_end_angle)

	--Coop Player
	local h = vint_object_find("coop_grp")
	Hud_dd_status.coop.grp_h = h
	Hud_dd_status.coop.fill_h = vint_object_find("coop_health_fill", h)
	Hud_dd_status.coop.car_h = vint_object_find("coop_car", h)
	Hud_dd_status.coop.health_bg = vint_object_find("coop_health_bg", h)

	--Hide Coop Indicator
	vint_set_property(Hud_dd_status.coop.grp_h, "visible", false)

	-- Move coop health [nclok1405]
	if Sui_hud_modern_layout then
		if vint_hack_is_std_res() == false then
			vint_set_property(Hud_dd_status.coop.grp_h, "anchor", 1040, 88)	-- 16:9
		else
			vint_set_property(Hud_dd_status.coop.grp_h, "anchor", 526, 58)	-- 4:3
		end
	end

	--Hostiles
	Hud_dd_status.hostile_elements.grp_h = vint_object_find("hostile_grp")
	Hud_dd_status.hostile_elements.fill_h = vint_object_find("hostile_health_fill")
	Hud_dd_status.hostile_elements.border_h = vint_object_find("hostile_border")
	Hud_dd_status.anim_elements.hostile_anim_h = vint_object_find("hostile_health_anim_1")

	--Pause animations
	vint_set_property(Hud_dd_status.anim_elements.hostile_anim_h, "is_paused", true)
	vint_set_property(vint_object_find("health_anim_0"), "is_paused", true)
	vint_set_property(vint_object_find("health_anim_1"), "is_paused", true)

	--Set callback for player health flashing animation
	local flash_twn = vint_object_find("health_fill_1")
	vint_set_property(flash_twn, "end_event", "hud_demo_derby_flash_end")


	--Set callback for player health decay
	local decay_twn = vint_object_find("health_fill_tween")
	vint_set_property(decay_twn, "end_event", "hud_demo_derby_decay_end")

	--Demo Derby Subscription
	vint_datagroup_add_subscription("sr2_local_player_demo_derby", "insert", "hud_dd_update")
	vint_datagroup_add_subscription("sr2_local_player_demo_derby", "update", "hud_dd_update")
	vint_datagroup_add_subscription("sr2_local_player_demo_derby", "remove", "hud_dd_update")
end

function hud_demo_derby_cleanup()
	peg_unload("ui_demo_derby")
end


function hud_dd_player_health_decrease_anim()

	local bar = Hud_dd_status.health_bar

	--Get the original angle before the hit
	local angle_before = vint_get_property(bar.fill_decay_h, "end_angle")
	local angle_end = vint_get_property(bar.fill_0_h, "end_angle")


	---Set tween values of decay animation, using the before and after values
	local fill_tween = vint_object_find("health_fill_tween")
	vint_set_property(fill_tween, "start_value", angle_before)
	vint_set_property(fill_tween, "end_value", angle_end)

	local bg_tween = vint_object_find("health_bg_tween")
	vint_set_property(bg_tween, "start_value", angle_before + bar.angle_offset)
	vint_set_property(bg_tween, "end_value", angle_end + bar.angle_offset)

	--play the animation, using the delay we setup
	lua_play_anim(vint_object_find("health_anim_0"), .5)


end


function hud_dd_update(di_h, event)
--debug_print("vint", "health_pct " .. Hud_dd_status.player.health_pct .. "\n")
	local key, index, screen_x, screen_y, z_depth, distance, health_pct, is_coop, is_player = vint_dataitem_get(di_h)

	if event == "update" then
		--Global reference
		local bar = Hud_dd_status.health_bar


		--PLAYER HEALTH
		if is_player == true then

			--store the angles of the bars for the decay
			local fill_end_angle = (bar.fill_end_angle - bar.fill_start_angle) * health_pct + bar.fill_start_angle
			local bg_end_angle = fill_end_angle + bar.angle_offset

			--#####
			--begin hit
			--#####
			if health_pct ~= Hud_dd_status.player.health_pct then

				--Set angles and fill of bar
				vint_set_property(bar.fill_0_h, "end_angle", fill_end_angle)
				vint_set_property(bar.fill_1_h, "end_angle", fill_end_angle)

				--Determine if health is greater or lesser than before
				if health_pct < Hud_dd_status.player.health_pct then

				else

				end


				--play the decay animation
				if health_pct < Hud_dd_status.player.health_pct then
					-- Flash health bar
					if Hud_dd_health_flash_status.is_flashing == true then
						--Compare current time index with previous
						local current_time_index = vint_get_time_index()
						local dif_time_index = current_time_index - Hud_dd_health_flash_status.last_flash_time_index
						if dif_time_index > .20 then
							Hud_dd_health_flash_status.is_queued = true
						end
					else
						--Play flashing animation
						hud_demo_derby_flash_play()
						Hud_dd_health_flash_status.is_flashing = true
					end
					--play the decay anim and be sure to the Global health pct
					Hud_dd_status.player.health_pct = health_pct
					hud_dd_player_health_decrease_anim()
				else
					--raise the decay fill and bg
					vint_set_property(bar.fill_decay_h, "end_angle", fill_end_angle)
					vint_set_property(bar.bg_h, "end_angle", bg_end_angle)
					--remove the queue if any
					Hud_dd_health_flash_status.is_queued = false
				end

				if health_pct == 0 then
					--Hide bg of meter if health is empty, and make the car icon transparent.
					--vint_set_property(bar.bg_h, "visible", false)
					vint_set_property(vint_object_find("weapon_icon"), "alpha", 0.5)

					if MODERN_HUD_DD_TINT_CAR_ICON then
						vint_set_property(vint_object_find("weapon_icon"), "tint", 1, 0, 0)
					end
				else
					vint_set_property(bar.bg_h, "visible", true)
					vint_set_property(bar.fill_0_h, "visible", true)
					vint_set_property(bar.fill_1_h, "visible", true)
					vint_set_property(vint_object_find("weapon_icon"), "alpha", 1)

					-- Tint the car icon to red depending on remaining health [nclok1405]
					if MODERN_HUD_DD_TINT_CAR_ICON then
						vint_set_property(vint_object_find("weapon_icon"), "tint", 1, health_pct, health_pct)
					end
				end

				--store the current  health pct so we can judge it later
				Hud_dd_status.player.health_pct = health_pct

			end

			-- Set visibility [nclok1405]
			vint_set_property(Hud_dd_status.handles.health_grp, "visible", (Sui_hud_enable == 2))
		end


		--COOP HEALTH
		if is_coop == true then

			--Creating reference to the Global...
			local coop_status = Hud_dd_status.coop

			--Make Coop Indicator visibile
			vint_set_property(coop_status.grp_h, "visible", (Sui_hud_enable == 2))

			--Update Health
			if health_pct ~= coop_status.health_pct then
				--local end_angle = 1.57 + (1.57 * health_pct)
				local end_angle = 1.63 + (1.57 * health_pct)
				vint_set_property(coop_status.fill_h, "end_angle", end_angle )
				Hud_dd_status.coop.health_pct = health_pct

				-- Do not show health bar until damaged [nclok1405]
				if ((health_pct >= 1) and (Sui_hud_autohide)) or (Sui_hud_enable < 2) then
					vint_set_property(coop_status.health_bg, "visible", false)
					vint_set_property(coop_status.fill_h, "visible", false)
				else
					vint_set_property(coop_status.health_bg, "visible", true)
					vint_set_property(coop_status.fill_h, "visible", true)
				end
			end

			if coop_status.health_pct == 0 then
				vint_set_property(coop_status.grp_h, "alpha", 0.5)
			else
				vint_set_property(coop_status.grp_h, "alpha", 1)
			end

			-- Tint the car icon to red depending on remaining health [nclok1405]
			if MODERN_HUD_DD_TINT_CAR_ICON then
				vint_set_property(Hud_dd_status.coop.car_h, "tint", 1, health_pct, health_pct)
			end

			--TODO: Make Car dim when coop is dead

		end


		--ENEMIES HEALTH
		if (is_player == false) and (is_coop == false) then

			--check to see if there is a hostile indicator for the index
			if Hud_dd_status.hostiles[index] == nil then


				--Doesn't currently exist so create the hostile indicator
				local grp_h = vint_object_clone(Hud_dd_status.hostile_elements.grp_h)
				local health_fill_h = vint_object_find("hostile_health_fill", grp_h)
				local border_h = vint_object_find("hostile_border", grp_h)

				--Create the animation clones
				local anim_0 = vint_object_find("hostile_health_anim_1")
				local anim_clone_0 = vint_object_clone(anim_0)
				local anim_0_tint_tween = vint_object_find("hostile_health_tween_1", anim_clone_0)
				vint_set_property(anim_0_tint_tween, "target_handle",	health_fill_h)

				Hud_dd_status.hostiles[index] = {
					grp_h = grp_h,
					health_fill_h = health_fill_h,
					border_h = border_h,
					anim_0 = anim_0,
					anim_clone_0 = anim_clone_0,
					anim_0_tint_tween = anim_0_tint_tween,
					health_pct = health_pct ,
					screen_x = screen_x,
					screen_y = screen_y,
					z_depth = z_depth,
					distance = distance,
				}

			end

			--Shorter name for ease of use
			local hostile = Hud_dd_status.hostiles[index]


			--Hide element if health is less than zero.
			if (hostile.health_pct <= 0) or (Sui_hud_enable < 2) then
				vint_set_property(hostile.grp_h, "visible", false)
			else
				vint_set_property(hostile.grp_h, "visible", true)
			end


			--Health Update
			if health_pct < hostile.health_pct then
				lua_play_anim(hostile.anim_clone_0, 0);
			end

			--Decrease health bar length
			vint_set_property(hostile.health_fill_h, "source_se", 86 * health_pct, 10)
			vint_set_property(hostile.border_h, "source_se", (86 * health_pct) + 4, 14)

			--Screen Position
			local grp_width = 106
			local x = screen_x - (grp_width * 0.5)
			local y = screen_y
			vint_set_property(hostile.grp_h, "anchor", x, y)


			--Scale
			local maxclamp = 0.40
			local minclamp = 0.1

			local maxscale = 1
			local minscale = 0.5

			--Clamp the distances
			if distance <= minclamp then
				distance = minclamp
				elseif distance >= maxclamp then
				distance = maxclamp
			end

			local newdist = (distance - minclamp)
			local ratio = 1 - (newdist / (maxclamp - minclamp))
			local scale = (ratio * (maxscale-minscale)) + minscale

			vint_set_property(hostile.grp_h, "scale", scale, scale)
			vint_set_property(hostile.grp_h, "alpha", scale)

			--Z Depth
			if z_depth ~= hostile.z_depth then
				vint_set_property(hostile.grp_h,  "depth", z_depth)
			end

			hostile.health_pct = health_pct
			hostile.screen_x = screen_x
			hostile.screen_y = screen_y
			hostile.z_depth = z_depth
			hostile.distance = distance


		end

	end

	--If you got a remove event, remove the clones
	if event == "remove" then
		debug_print("vint", "remove hostiles\n")
		local hostile = Hud_dd_status.hostiles[index]
		if hostile ~= nil then
			vint_object_destroy(hostile.grp_h)
			Hud_dd_status.hostiles[index] = nil
		end
	end

end

function hud_demo_derby_flash_play()
	local health_flash_anim = vint_object_find("health_anim_1")
	lua_play_anim(health_flash_anim, 0)
	Hud_dd_health_flash_status.last_flash_time_index = vint_get_time_index()
end


function hud_demo_derby_flash_end(tween_h, event)
	if Hud_dd_health_flash_status.is_queued == true then
		--Queued Flashing so, play another flash
		hud_demo_derby_flash_play()
		Hud_dd_health_flash_status.is_queued = false
	else
		--No queue so we aren't going to flash anymore.
		Hud_dd_health_flash_status.is_flashing = false
	end
end

function hud_demo_derby_decay_end(tween_h, event)
	local bar = Hud_dd_status.health_bar
	debug_print("vint", "decay end event")
	if Hud_dd_status.player.health_pct == 0 then
		vint_set_property(bar.bg_h, "visible", false)
	end
end


function hud_demo_derby_coop_test()
	local health_pct = 0
	local coop_status = Hud_dd_status.coop
	vint_set_property(coop_status.grp_h, "visible", true)
	local end_angle = 1.57 + (1.57 * health_pct)
	vint_set_property(coop_status.fill_h, "end_angle", end_angle )

	if health_pct == 0 then
		vint_set_property(coop_status.grp_h, "alpha", 0.5)
	else
		vint_set_property(coop_status.grp_h, "alpha", 1)
	end

	Hud_dd_status.coop.health_pct = health_pct
end


function hud_demo_derby_health_hide()
	vint_set_property(Hud_dd_status.handles.health_grp, "visible", false)
end

function hud_demo_derby_health_show()
	vint_set_property(Hud_dd_status.handles.health_grp, "visible", true)
end





