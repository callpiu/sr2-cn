-- hud.lua: Head Up Display, also handles weapon switching via Q key

HUD_DOC_HANDLE = -1


-- this structure is all the data needed to display and track the status of the notoriety display
TWEEN_STATE_IDLE = 0
TWEEN_STATE_RUNNING = 1
TWEEN_STATE_PAUSED = 2
TWEEN_STATE_DISABLE = 3

--Threads
Sprint_cool_down_thread = -1

Hud_process_thread = -1

--Globals
MP_enabled = false

Hud_sounds = {
	radial_open 			= audio_get_audio_id("SYS_WEP_MENU"),
	radial_select 			= audio_get_audio_id("SYS_WEP_SCROLL"),
	radial_equip_weapon 	= audio_get_audio_id("SYS_RADIAL_WEAPON_EQUIP"),
	radial_equip_food 	= audio_get_audio_id("SYS_RADIAL_DRUG_EQUIP"),
}

Hud_noto_data = {
	gangs = {
		cur_team = 0,
		cur_level = -1,
		cur_meter = 0,
		base_icon_name = "gang_noto_icon_",

		teams = {
			["brotherhood"]	= {icon_image = "ui_hud_not_brotherhood",	bar_0_color = {0.5843, 0.0000, 0.004},	bar_1_color = {0.8039, 0.0000, 0.004}, noto_level = -1},
			["ronin"]	= {icon_image = "ui_hud_not_ronin",			bar_0_color = {0.7255, 0.6157, 0.184},	bar_1_color = {0.8980, 0.8667, 0.004}, noto_level = -1},
			["samedi"]	= {icon_image = "ui_hud_not_samedi",		bar_0_color = {0.0196, 0.4235, 0.004},	bar_1_color = {0.0353, 0.7098, 0.004}, noto_level = -1},

			-- local_player is for mp only
			["local_player"]	= {icon_image = "ui_hud_not_samedi",		bar_0_color = {0.0196, 0.4235, 0.004},	bar_1_color = {0.0353, 0.7098, 0.004}, noto_level = -1},
		},

		icons = {
			[1] = {tween_end = 0, anim_0 = 0, anim_1 = 0, anim_2 = 0, anim_3 = 0, bmp_clone_0 = 0, bmp_clone_1 = 0},
			[2] = {tween_end = 0, anim_0 = 0, anim_1 = 0, anim_2 = 0, anim_3 = 0, bmp_clone_0 = 0, bmp_clone_1 = 0},
			[3] = {tween_end = 0, anim_0 = 0, anim_1 = 0, anim_2 = 0, anim_3 = 0, bmp_clone_0 = 0, bmp_clone_1 = 0},
			[4] = {tween_end = 0, anim_0 = 0, anim_1 = 0, anim_2 = 0, anim_3 = 0, bmp_clone_0 = 0, bmp_clone_1 = 0},
			[5] = {tween_end = 0, anim_0 = 0, anim_1 = 0, anim_2 = 0, anim_3 = 0, bmp_clone_0 = 0, bmp_clone_1 = 0}
		},

		meter = { meter_fill_0_h = 0, meter_fill_1_h = 0, meter_bg_h = 0, start_angle = 3.141592654, end_angle = 6.283185307, cw = true, tween = 0 },
	},

	police = {
		cur_team = 0,
		cur_level = -1,
		cur_meter = 0,
		base_icon_name = "police_noto_icon_",

		teams = {
			["police"]	= {icon_image = "ui_hud_not_police",		bar_0_color = {0.0000, 0.0000, 0.324},	bar_1_color = {0.0000, 0.0000, 0.754}, noto_level = -1},
			["ultor"]	= {icon_image = "ui_hud_not_ultor",			bar_0_color = {0.2549, 0.2549, 0.254},	bar_1_color = {0.4706, 0.4706, 0.474}, noto_level = -1},
		},

		icons = {
			[1] = {tween_end = 0, anim_0 = 0, anim_1 = 0, anim_2 = 0, anim_3 = 0, bmp_clone_0 = 0, bmp_clone_1 = 0},
			[2] = {tween_end = 0, anim_0 = 0, anim_1 = 0, anim_2 = 0, anim_3 = 0, bmp_clone_0 = 0, bmp_clone_1 = 0},
			[3] = {tween_end = 0, anim_0 = 0, anim_1 = 0, anim_2 = 0, anim_3 = 0, bmp_clone_0 = 0, bmp_clone_1 = 0},
			[4] = {tween_end = 0, anim_0 = 0, anim_1 = 0, anim_2 = 0, anim_3 = 0, bmp_clone_0 = 0, bmp_clone_1 = 0},
			[5] = {tween_end = 0, anim_0 = 0, anim_1 = 0, anim_2 = 0, anim_3 = 0, bmp_clone_0 = 0, bmp_clone_1 = 0}
		},

		meter = { meter_fill_0_h = 0, meter_fill_1_h = 0, meter_bg_h = 0, start_angle = 0, end_angle = 3.141592654, cw = false, tween = 0 },
	},
}

Hud_player_status = {
	cash = 0,
	health_pct = 1.0,
	health_recovering = false,
	sprint_pct = 1.0,
	respect = -1,
	respect_needed = -1,
	respect_int = 0,	-- Current respect level [nclok1405]
	respect_bar_percent = 0,	-- Current percentage of respect bar [nclok1405]
	sprint_enabled = true,
	is_sprinting = false,
	orientation = 0,
	inventory_disabled = false,
	cruise_control_active = -1,
	cruise_control_h = -1,
	cruise_control_anim = -1,
	health_bar = 	{ bg_h = 0, fill_0_h = 0,  fill_1_h = 0, fill_decay_h = 0,
							fill_start_angle = PI + 0.03, fill_end_angle = PI2 - 0.03, angle_offset = 0.045,
							anim = 0, anim_delay_start = .25, anim_delay = .25, anim_delay_decay = .9,
							is_flashing = false},
	sprint_bar = 	{ bg_h = 0, fill_0_h = 0, fill_1_h = 0,
							fill_start_angle = PI + 0.03, fill_end_angle = PI2 - 0.03, angle_offset = 0.045,
							bar_0_color = {0, 0, 0},	bar_1_color = {0, 0, 0},
							is_flashing = false,
						},
	respect_bar =	{ bg_h = 0, fill_0_h = 0, fill_1_h = 0, txt_grp = 0, txt = 0,
							fill_start_angle = 0 + 0.025, fill_end_angle = PI - 0.005, angle_offset = 0.035,
						},

}


Hud_enemy_status = {
	grp_h = 0,
	count_txt_h = 0,

	grp_x = 0,
	grp_y = 0,
}

Hud_weapon_status = {
	wpn_ready = true,
	fine_aim_transition = 0,
	sniper_visible = -1,
	ammo_text_h = 0,
	single_wpn_icon_h = 0,
	dual_wpn_icon_1_h = 0,
	dual_wpn_icon_2_h = 0
}

Hud_followers = {
	main_grp_h = -1,
	slot_arrange = {1, 2, 3},
	slot_objects = { {}, {}, {} },
	follower_data = {
		[1] = { head_img_name = "" },
		[2] = { head_img_name = "" },
		[3] = { head_img_name = "" },
	},
}

Hud_balance_status = {
	active = -1,
	position = 0,
	balance_grp_h = 0,
	base_image_h = 0,
	arrow_image_h = 0,
	min_angle = -0.466,
	max_angle = 0.466,
	color_base = {0.2000, 0.7529, 0.014},
	color_alarm = {0.5569, 0.1451, 0.004}
}

Hud_vignettes = {
	health = {
		grp_h = -1,
		fade_anim_h = -1,
		fade_twn_h = -1,
		tint_anim_h = -1,
		tint_twn_h = -1
	},
	fine_aim_dim = {
		grp_h = -1,
	}
}

Reticule_hits = {}
Hud_hit_elements = {
	main = -1,
	minor = -1,
	major = -1,
	anim = -1,
}

Hud_mp_snatch_elements = {
	main_grp_h = -1,
	head_img_bg_h = -1,
	recruitment_fill_h = -1,
}

Hud_radial_menu = {
	radial_grp_h = -1,
	ammo_angle_full = -3.2,
	ammo_angle_empty = -4.7,
	stick_grp_h = -1,
	dpad_highlight_h = -1,
	dpad_highlight_anim_h = -1,
	stick_text_h = -1,
	selector_h = -1,
	stick_mag = 0,
	slot_selected = 5,
	slot_equipped = 0,
	slot_desc_h = -1,
	slots = {},
}

Hud_smoked_busted = {}

Hud_inventory = {}

Hud_current_veh_logo = 0
Hud_current_radio_station = 0
Hud_radio_show = false
Hud_map = {}


Hud_lockon = {
	color_locked = {r=.7,g=0,b=0},
	color_unlocked = {r=0,g=.8,b=0},
	base_pixel_size =100
}

-- Initial HUD locations [nclok1405]
Modern_hud_weapon_circle_x = 0
Modern_hud_weapon_circle_y = 0
Modern_hud_cash_x = 0
Modern_hud_cash_y = 0
Modern_hud_radial_x = 0
Modern_hud_radial_y = 0
Modern_hud_followers_x = 0
Modern_hud_followers_y = 0

Modern_hud_last_weapon = "ui_hud_inv_w_fist"
Modern_hud_last_ammo_string = ""
Modern_hud_play_equip_sound = false

Modern_hud_weapon_unhiding = false
Modern_hud_weapon_frames = 0
Modern_hud_weapon_visibility = 100

Modern_hud_health_unhiding = false
Modern_hud_health_frames = 0
Modern_hud_health_visibility = 100

Modern_hud_sprint_unhiding = false
Modern_hud_sprint_frames = 0
Modern_hud_sprint_visibility = 100

Modern_hud_respect_unhiding = false
Modern_hud_respect_frames = 0
Modern_hud_respect_visibility = 100
Modern_hud_respect_last_percent = 0
Modern_hud_respect_last_level = 0

Modern_hud_cash_unhiding = false
Modern_hud_cash_frames = 0
Modern_hud_cash_visibility = 100
Modern_hud_cash_tint_red = 100
Modern_hud_cash_tint_green = 100
Modern_hud_cash_tint_blue = 100

Modern_hud_followers_unhiding = false
Modern_hud_followers_frames = 0
Modern_hud_followers_visibility = 100

Modern_hud_notobg_visibility = 100

Modern_hud_vehicle_surfing_time = 0

Modern_hud_active_gameplay_crc = 0
Modern_hud_active_gameplay_playtime = 0
Modern_hud_active_gameplay_start_cash = 0

Modern_hud_diversion_thread = -1

-- Get radio station logo [nclok1405]
function hud_get_radio_station_logo(radio_station)
	if sui_compare_string("RADIO_OFF", radio_station) then
		return "ui_menu_none"	-- OFF
	elseif sui_compare_string("RADIO_STATION_MY_RADIO", radio_station) then
		return ""	-- MY RADIO 85.5
	elseif sui_compare_string("RADIO_POLICE", radio_station) then
		return ""	-- STILWATER POLICE DISPATCH
	elseif sui_compare_string("RADIO_FBI", radio_station) then
		return ""	-- STILWATER FBI DISPATCH
	elseif sui_compare_string("105.0 EZZZY FM", radio_station) then
		return "ui_radio_105_ezzzy"
	elseif sui_compare_string("89.0 ULTOR FM", radio_station) then
		return "ui_radio_89_ultor"
	elseif sui_compare_string("89.0 GENERATION X", radio_station) then
		return "ui_radio_89_gen_x"
	elseif sui_compare_string("95.4 KRhyme FM", radio_station) then
		return "ui_radio_954_khryme"
	elseif sui_compare_string("97.6 K12 FM", radio_station) then
		return "ui_radio_976_k12"
	elseif sui_compare_string("FUNK 98.4", radio_station) then
		return "ui_radio_984_funk"
	elseif sui_compare_string("99.0 THE UNDERGROUND", radio_station) then
		return "ui_radio_99_underground"
	elseif sui_compare_string("102.4 KLASSIC FM", radio_station) then
		return "ui_radio_1024_klassic"
	elseif sui_compare_string("103.6 420 FM", radio_station) then
		return "ui_radio_1036_four_20"
	elseif sui_compare_string("105.0 THE WORLD", radio_station) then
		return "ui_radio_105_world"
	elseif sui_compare_string("THE KRUNCH 106.66", radio_station) then
		return "ui_radio_10666_krunch"
	elseif sui_compare_string("107.77 THE MIX FM", radio_station) then
		return "ui_radio_10777_the_mix"
	elseif sui_compare_string("KEEPIN' IT EZZZY", radio_station) then
		return "ui_radio_105_ezzzy"
	elseif sui_compare_string("VETERAN'S VAULT GENX", radio_station) then
		return "ui_radio_89_gen_x"
	elseif sui_compare_string("ADVERT FM", radio_station) then
		return "ui_radio_advertfm"
	end

	return ""
end

function hud_init()

	--Store document handle
	HUD_DOC_HANDLE = vint_document_find("hud")

	peg_load("ui_radio_logos")	-- Load radio logos [nclok1405]

	MP_enabled = mp_is_enabled()

	--Pause all animations
	vint_set_property(vint_object_find("noto_anim_0"), "is_paused", true)
	vint_set_property(vint_object_find("noto_anim_1"), "is_paused", true)
	vint_set_property(vint_object_find("noto_anim_2"), "is_paused", true)
	vint_set_property(vint_object_find("noto_anim_3"), "is_paused", true)

	vint_set_property(vint_object_find("health_anim_0"), "is_paused", true)
	vint_set_property(vint_object_find("health_anim_1"), "is_paused", true)

	vint_set_property(vint_object_find("sprint_anim_0"), "is_paused", true)
	vint_set_property(vint_object_find("sprint_anim_1"), "is_paused", true)

	vint_set_property(vint_object_find("follow_anim_0"), "is_paused", true)
	vint_set_property(vint_object_find("follow_anim_1"), "is_paused", true)
	vint_set_property(vint_object_find("follow_rev_anim_0"), "is_paused", true)

	vint_set_property(vint_object_find("dpad_highlight_anim_1"), "is_paused", true)

	vint_set_property(vint_object_find("gsi_xy_anim_in"), "is_paused", true)

	vint_set_property(vint_object_find("vehicle_logo_anim_1"), "is_paused", true)
	vint_set_property(vint_object_find("radio_station_anim_1"), "is_paused", true)

	--Notoriety Meters
	Hud_noto_data.gangs.meter.meter_fill_0_h = vint_object_find("gang_noto_fill_0")
	Hud_noto_data.gangs.meter.meter_fill_1_h = vint_object_find("gang_noto_fill_1")
	Hud_noto_data.police.meter.meter_fill_0_h = vint_object_find("police_noto_fill_0")
	Hud_noto_data.police.meter.meter_fill_1_h = vint_object_find("police_noto_fill_1")
	Hud_noto_data.gangs.meter.meter_bg_h = vint_object_find("gang_noto_bg")
	Hud_noto_data.police.meter.meter_bg_h = vint_object_find("police_noto_bg")

	-- Get health/weapon circle group [nclok1405]
	Hud_player_status.base_grp_h = vint_object_find("health_grp")
	Modern_hud_weapon_circle_x, Modern_hud_weapon_circle_y = vint_get_property(Hud_player_status.base_grp_h, "anchor")

	--sui_hide_object("health_base")
	--sui_hide_object("health_bar_bg")
	--sui_hide_object("sprint_bar_bg")
	--sui_hide_object("respect_bar_bg")

	--local health_base_h = vint_object_find("health_base")
	--vint_set_property(health_base_h, "source_se", 142, 142)	-- Source texture size
	--vint_set_property(health_base_h, "anchor", -142, 0)	-- X and Y positions

	--Health Meter
	Hud_player_status.health_bar.bg_h = vint_object_find("health_bar_bg")
	Hud_player_status.health_bar.fill_0_h = vint_object_find("health_bar_fill_0")
	Hud_player_status.health_bar.fill_1_h = vint_object_find("health_bar_fill_1")
	Hud_player_status.health_bar.fill_decay_h = vint_object_find("health_bar_fill_decay")

	--Map
	Hud_map.base_grp_h = vint_object_find("map_grp")
	Hud_map.bg_map_h = vint_object_find("bg_map")	-- Black circle around the minimap [nclok1405]
	Hud_map.base_bottom_h = vint_object_find("map_base_bottom")	-- Notoriety BG for Police [nclok1405]
	Hud_map.base_top_h = vint_object_find("map_base_top")	-- Notoriety BG for Gangs [nclok1405]

	-- Make black circle slightly bigger [nclok1405]
	vint_set_property(Hud_map.bg_map_h, "scale", 1.05, 1.05)
	-- By default top and left sides get more border than bottom and right, so move the circle a bit
	local bx, by = vint_get_property(Hud_map.bg_map_h, "anchor")
	vint_set_property(Hud_map.bg_map_h, "anchor", bx + 0.5, by + 0.5)

	--vint_set_property(Hud_map.base_bottom_h, "visible", false)
	--vint_set_property(Hud_map.base_top_h, "visible", false)

	--Sprint Meter
	Hud_player_status.sprint_bar.bg_h = vint_object_find("sprint_bar_bg")
	Hud_player_status.sprint_bar.fill_0_h = vint_object_find("sprint_bar_fill_0")
	Hud_player_status.sprint_bar.fill_1_h = vint_object_find("sprint_bar_fill_1")

	--Respect Mater
	Hud_player_status.respect_bar.bg_h = vint_object_find("respect_bar_bg")
	Hud_player_status.respect_bar.fill_0_h = vint_object_find("respect_bar_fill_0")
	Hud_player_status.respect_bar.fill_1_h = vint_object_find("respect_bar_fill_1")
	Hud_player_status.respect_bar.txt_grp = vint_object_find("respect_count_grp")
	Hud_player_status.respect_bar.txt = vint_object_find("respect_count_txt")

	--Reset angles on health meter
	local bar = Hud_player_status.health_bar
	vint_set_property(bar.bg_h, 		"start_angle", bar.fill_start_angle - bar.angle_offset)
	vint_set_property(bar.bg_h, 		"end_angle", 	bar.fill_end_angle + bar.angle_offset)
	vint_set_property(bar.fill_0_h,	"start_angle", bar.fill_start_angle)
	vint_set_property(bar.fill_0_h, 	"end_angle", 	bar.fill_end_angle)
	vint_set_property(bar.fill_1_h, 	"start_angle", bar.fill_start_angle)
	vint_set_property(bar.fill_1_h, 	"end_angle", 	bar.fill_end_angle)

	--Reset angles on sprint meter
	bar = Hud_player_status.sprint_bar
	vint_set_property(bar.bg_h, 		"start_angle", bar.fill_start_angle - bar.angle_offset)
	vint_set_property(bar.bg_h, 		"end_angle", 	bar.fill_end_angle + bar.angle_offset)
	vint_set_property(bar.fill_0_h,	"start_angle", bar.fill_start_angle)
	vint_set_property(bar.fill_0_h, 	"end_angle", 	bar.fill_end_angle)
	vint_set_property(bar.fill_1_h, 	"start_angle", bar.fill_start_angle)
	vint_set_property(bar.fill_1_h, 	"end_angle", 	bar.fill_end_angle)

	--Reset angles on Respect meter
	bar = Hud_player_status.respect_bar
	vint_set_property(bar.bg_h, 		"start_angle", bar.fill_start_angle - bar.angle_offset)
	vint_set_property(bar.bg_h, 		"end_angle", 	bar.fill_end_angle + bar.angle_offset)
	vint_set_property(bar.fill_0_h,	"start_angle", bar.fill_start_angle)
	vint_set_property(bar.fill_0_h, 	"end_angle", 	bar.fill_end_angle)
	vint_set_property(bar.fill_1_h, 	"start_angle", bar.fill_start_angle)
	vint_set_property(bar.fill_1_h, 	"end_angle", 	bar.fill_end_angle)

	--Store sprint colors from document information
	Hud_player_status.sprint_bar.bar_0_color[1], Hud_player_status.sprint_bar.bar_0_color[2], Hud_player_status.sprint_bar.bar_0_color[3] = vint_get_property(Hud_player_status.sprint_bar.fill_0_h,  "tint")
	Hud_player_status.sprint_bar.bar_1_color[1], Hud_player_status.sprint_bar.bar_1_color[2], Hud_player_status.sprint_bar.bar_1_color[3] = vint_get_property(Hud_player_status.sprint_bar.fill_1_h,  "tint")

	--Cash
	Hud_player_status.cash_h = vint_object_find("cash")

	-- Get cash position [nclok1405]
	Modern_hud_cash_x, Modern_hud_cash_y = vint_get_property(Hud_player_status.cash_h, "anchor")

	--Ammo/Weapons
	Hud_weapon_status.ammo_text_h = vint_object_find("ammo_status")
	Hud_weapon_status.single_wpn_icon_h = vint_object_find("weapon_icon")
	Hud_weapon_status.dual_wpn_icon_1_h = vint_object_find("dual_weapon_1")
	Hud_weapon_status.dual_wpn_icon_2_h = vint_object_find("dual_weapon_2")

	--Balance Meter
	local balance_meter = vint_object_find("balance_meter")
	Hud_balance_status.balance_grp_h = balance_meter
	Hud_balance_status.base_grp_h = vint_object_find("base_grp", balance_meter)
	Hud_balance_status.arrow_image_h = vint_object_find("arrow_grp", balance_meter)

	--Vignette
	local h = vint_object_find("vignettes")
	Hud_vignettes.health.grp_h = vint_object_find("vignette_health", h )
	Hud_vignettes.health.fade_anim_h = vint_object_find("vignette_fade_anim")
	Hud_vignettes.health.fade_twn_h = vint_object_find("vignette_alpha_twn")

	local vignette_doc = vint_document_find("vignette")
	Hud_vignettes.fine_aim_dim.grp_h = vint_object_find("vignette", nil, vignette_doc)
	vint_set_property(Hud_vignettes.health.fade_anim_h, "is_paused", true)

	--Pause Animations
	vint_set_property(vint_object_find("hit_anim"), "is_paused", true)

	--Followers
	Hud_followers.main_grp_h = vint_object_find("followers")
	Modern_hud_followers_x, Modern_hud_followers_y = vint_get_property(Hud_followers.main_grp_h, "anchor")

	local master_follower_anim_0 = vint_object_find("follow_anim_0")
	local master_follower_anim_1 = vint_object_find("follow_anim_1")
	local master_count_tween_alpha = vint_object_find("follow_rev_count_alpha_0")
	local master_count_tween_scale = vint_object_find("follow_rev_count_scale_0")
	vint_set_property(master_follower_anim_0, "is_paused", true)
	vint_set_property(master_follower_anim_1, "is_paused", true)

	for i = 1, 3 do
		local slot_object = Hud_followers.slot_objects[i]
		local grp = vint_object_find("follower_grp_" .. i)
		slot_object.name = i
		slot_object.head_img_h = vint_object_find("follower_head", grp)
		slot_object.frame_img_h = vint_object_find("follower_frame", grp)
		slot_object.health_img_bg_h = vint_object_find("follower_health_bg", grp)
		slot_object.health_img_fill_h = vint_object_find("follower_health_fill", grp)
		slot_object.revive_timer_h = vint_object_find("follower_count", grp)
		slot_object.visible = false -- -1
		slot_object.group_h = grp

		--clone animations into slots
		local anim_0 = vint_object_clone(master_follower_anim_0)
		local anim_1 = vint_object_clone(master_follower_anim_1)
		slot_object.anim_0 = anim_0
		slot_object.anim_1 = anim_1
		vint_set_property(anim_0, "is_paused", true)
		vint_set_property(anim_1, "is_paused", true)
		vint_set_property(anim_0, "target_handle", grp)
		vint_set_property(anim_1, "target_handle", grp)


		--Duplicate Tweens for Counting Anim
		vint_set_property(vint_object_clone(master_count_tween_alpha), "target_handle", slot_object.revive_timer_h)
		vint_set_property(vint_object_clone(master_count_tween_scale), "target_handle", slot_object.revive_timer_h)
	end

	--Radial Menu
	local slot_anchors = {}
	Hud_radial_menu.radial_grp_h = vint_object_find("radial_grp")
	Hud_radial_menu.stick_grp_h = vint_object_find("stick_grp", Hud_radial_menu.radial_grp_h)
	Hud_radial_menu.stick_text_h = vint_object_find("stick_text", Hud_radial_menu.radial_grp_h)
	Hud_radial_menu.selector_h = vint_object_find("slot_select", Hud_radial_menu.radial_grp_h)
	Hud_radial_menu.slot_desc_h = vint_object_find("slot_description")
	Hud_radial_menu.dpad_highlight_h = vint_object_find("dpad_highlight", Hud_radial_menu.radial_grp_h)
	Hud_radial_menu.dpad_highlight_anim_h = vint_object_find("dpad_highlight_anim_1")

	-- Get Radial Menu position [nclok1405]
	Modern_hud_radial_x, Modern_hud_radial_y = vint_get_property(Hud_radial_menu.radial_grp_h, "anchor")

	-- platform specific changes!
	local control_group_h = vint_object_find("control_stick", Hud_radial_menu.radial_grp_h)
	local control_base_h = vint_object_find("base", control_group_h)
	vint_set_property(control_base_h, "image", get_control_stick_base())
	local control_stick_group_h = vint_object_find("stick_grp", control_group_h)
	local control_stick_h = vint_object_find("stick", control_stick_group_h)
	vint_set_property(control_stick_h, "image", get_control_stick_thumb())
	local control_stick_text_h = vint_object_find("stick_text", control_stick_group_h)
	vint_set_property(control_stick_text_h, "text_tag", get_control_stick_text())

	local control_dpad_h = vint_object_find("dpad", Hud_radial_menu.radial_grp_h)
	vint_set_property(control_dpad_h, "image", get_dpad_image())


	local slot_grp_h
	local item_x, item_y

	--store slot locations skip over 0 and 8(These are templates)
	for i = 1, 7 do
		slot_grp_h = vint_object_find("slot_" .. i, Hud_radial_menu.radial_grp_h)


		item_x, item_y = vint_get_property(slot_grp_h, "anchor")
		slot_anchors[i] = { x = item_x, y = item_y}
		vint_object_destroy(slot_grp_h)
	end
	for i = 9, 11 do
		slot_grp_h = vint_object_find("slot_" .. i)
		item_x, item_y = vint_get_property(slot_grp_h, "anchor")
		slot_anchors[i] = { x = item_x, y = item_y}
		vint_object_destroy(slot_grp_h)
	end

	--Create template elements
	for i = 0, 11 do
		Hud_radial_menu.slots[i] = {
			grp_h = -1,
			ammo_bar_fill_h = -1,
			ammo_bar_bg_h = -1,
			item_element_h = -1,
			item_name_crc = -1,
			infinite_h = -1,
			bmp_name = -1,
			availability = -1,
			ammo_infinite = -1,
			dual_wield = -1,
			ammo_cur = -1,
			ammo_max = -1,
		}
	end

	--Now populate radial menu groups groups using templates 0 and 8
	Hud_radial_menu.slots[0].grp_h = vint_object_find("slot_0", Hud_radial_menu.radial_grp_h)
	Hud_radial_menu.slots[0].ammo_bar_fill_h = vint_object_find("ammo", Hud_radial_menu.slots[0].grp_h)
	Hud_radial_menu.slots[0].ammo_bar_bg_h = vint_object_find("ammo_bg", Hud_radial_menu.slots[0].grp_h)
	Hud_radial_menu.slots[0].infinite_h =  vint_object_find("infinite", Hud_radial_menu.slots[0].grp_h)

	Hud_radial_menu.slots[8].grp_h = vint_object_find("slot_8", Hud_radial_menu.radial_grp_h)
	Hud_radial_menu.slots[8].item_element_h = vint_object_find("inv_icon", Hud_radial_menu.slots[8].grp_h)

	--Radial Menu Weapon Slots
	for i = 1, 7 do
		slot_grp_h = vint_object_clone(Hud_radial_menu.slots[0].grp_h)
		vint_set_property(slot_grp_h, "anchor", slot_anchors[i].x, slot_anchors[i].y)
		Hud_radial_menu.slots[i].grp_h = slot_grp_h
		Hud_radial_menu.slots[i].ammo_bar_fill_h = vint_object_find("ammo", slot_grp_h)
		Hud_radial_menu.slots[i].ammo_bar_bg_h = vint_object_find("ammo_bg", slot_grp_h)
		Hud_radial_menu.slots[i].infinite_h = vint_object_find("infinite", slot_grp_h)
		vint_object_rename(slot_grp_h, "slot_" .. i)
	end

	--Radial Menu Food Slots
	for i = 9, 11 do
		slot_grp_h = vint_object_clone(Hud_radial_menu.slots[8].grp_h)
		vint_set_property(slot_grp_h, "anchor", slot_anchors[i].x, slot_anchors[i].y)
		Hud_radial_menu.slots[i].grp_h = slot_grp_h
		Hud_radial_menu.slots[i].item_element_h = vint_object_find("inv_icon", slot_grp_h)
	end

	--Hit Indicator
	Hud_hit_elements.main_h = vint_object_find("hits")
	h = Hud_hit_elements.main_h
	Hud_hit_elements.minor_h = vint_object_find("major", h)
	Hud_hit_elements.major_h = vint_object_find("major", h)
	Hud_hit_elements.anim_h = vint_object_find("hit_anim")

	--Cruise Control
	Hud_player_status.cruise_control_h = vint_object_find("cruise_control_grp")
	Hud_player_status.cruise_control_anim = vint_object_find("cruise_control_fade_anim")

	--Hud Lockon

	Hud_lockon.lock_h = vint_object_find("lockon")
	Hud_lockon.lock1_h = vint_object_find("lockon_1", Hud_lockon.lockon_h )
	Hud_lockon.lock2_h = vint_object_find("lockon_2", Hud_lockon.lockon_h )
	Hud_lockon.lock3_h = vint_object_find("lockon_3", Hud_lockon.lockon_h )
	Hud_lockon.lock4_h = vint_object_find("lockon_4", Hud_lockon.lockon_h )

	--lockon base screensize
	Hud_lockon.lock_base_width, Hud_lockon.lock_base_height = vint_get_property(Hud_lockon.lock1_h, "scale")

	-- Get "Enemy Respect" stuff that were never used in the vanilla game [nclok1405]
	-- I'll use it for Vehicle Surfing Timer
	Hud_enemy_status.grp_h = vint_object_find("enemy_respect_grp")
	Hud_enemy_status.count_txt_h = vint_object_find("enemy_respect_count_txt")

	vint_set_property(Hud_enemy_status.grp_h, "visible", true)
	vint_set_property(Hud_enemy_status.count_txt_h, "visible", true)
	vint_set_property(Hud_enemy_status.count_txt_h, "text_tag", "")
	Hud_enemy_status.grp_x, Hud_enemy_status.grp_y = vint_get_property(Hud_enemy_status.grp_h, "anchor")

	--Initialize Gameplay Status Indicator
	hud_gsi_init()

	--Initialize Mayhem Hud
	hud_mayhem_init()

	--Initialize Floating Healthbars (sewage version)
	hud_healthbars_init()

	--Initialize mp snatch system
	hud_mp_snatch_init()

	--Initialize reticule related stuff,
	hud_reticules_init()

	hud_collection_msg_init()
	hud_busted_init()

	--Subscribe to datagroups and dataitems

	--Notoriety`
	vint_datagroup_add_subscription("sr2_notoriety", "update", "hud_noto_change")
	vint_datagroup_add_subscription("sr2_notoriety", "insert", "hud_noto_change")

	--Hood
	vint_dataitem_add_subscription("sr2_local_player_hood", "update", "hud_player_hood_change")
	vint_dataitem_add_subscription("sr2_local_player_status", "update", "hud_player_status_change")


	--Followers
	vint_datagroup_add_subscription("sr2_local_player_followers", "insert", "hud_player_followers_change")
	vint_datagroup_add_subscription("sr2_local_player_followers", "update", "hud_player_followers_change")

	--Infrequent
	--..moving below followers, hopefully solves homie update issues (Derik)
	vint_dataitem_add_subscription("sr2_local_player_status_infrequent", "update", "hud_player_status_inf_change")

	--Radial Menu
	vint_datagroup_add_subscription("sr2_local_player_inventory", "insert", "hud_radial_menu_update")
	vint_datagroup_add_subscription("sr2_local_player_inventory", "update", "hud_radial_menu_update")

	--Weapons
	vint_dataitem_add_subscription("sr2_local_player_weapons", "update", "hud_player_weapon_change")
	vint_dataitem_add_subscription("sr2_local_player_frequent_weapon", "update", "hud_player_weapon_freq_change")

	--Lockon
	vint_dataitem_add_subscription("sr2_local_player_lockon", "update", "hud_player_lockon_update")



	--TODO: This shouldn't use the same data group anyways. Sean will need to fix this gameside
	if MP_enabled == false then
		vint_dataitem_add_subscription("sr2_local_player_respect", "update", "hud_player_respect_change")

	elseif MP_enabled == true then
		--Need to hide the respect meter
		vint_set_property(Hud_player_status.respect_bar.bg_h, "visible", false)
		vint_set_property(Hud_player_status.respect_bar.fill_0_h, "visible", false)
		vint_set_property(Hud_player_status.respect_bar.fill_1_h, "visible", false)
		vint_set_property(Hud_player_status.respect_bar.txt_grp, "visible", false)
		vint_set_property(Hud_player_status.respect_bar.txt, "visible", false)

		--Hide the food UI
		vint_set_property(vint_object_find("dpad"), "visible", false)
		for i = 8, 11 do
			vint_set_property(Hud_radial_menu.slots[i].grp_h, "visible", false)
		end

		--Hide cash element
		vint_set_property(Hud_player_status.cash_h, "visible", false)

		-- Hide followers
		vint_set_property(Hud_followers.slot_objects[1].group_h, "visible", false)
		vint_set_property(Hud_followers.slot_objects[2].group_h, "visible", false)
		vint_set_property(Hud_followers.slot_objects[3].group_h, "visible", false)
	end

	vint_dataitem_add_subscription("sr2_balance_meter", "update", "hud_balance_meter_change")

	--HUD Process Thread
	Hud_process_thread = thread_new("hud_process")

	-- Diversion Message Process Thread [nclok1405]
	Modern_hud_diversion_thread = thread_new("hud_diversion_process")
end

function hud_cleanup()

	--kill threads

	--Clean up hud
	hud_inventory_hide()
end

function hud_hide_map()
	vint_set_property(Hud_map.base_grp_h, "visible", false)
end

function hud_show_map()
	vint_set_property(Hud_map.base_grp_h, "visible", true)
end

function hud_inventory_input(event, value)
	--debug_print("vint", "Inventory Event: " .. event .. " : "  .. value .. "\n")
	--debug_print("vint", "Inventory is disabled: " .. lua_test_var(Hud_player_status.inventory_disabled) .. "\n")
	if event == "inventory" then
		if value > 0.5 then

			if Sui_fast_weapon_switch then
				-- We're doing a fast weapon switch if you tap the button
				if Hud_inventory.is_pressed == false then
					if Hud_inventory.tap_thread == nil then
						Hud_inventory.tap_thread = thread_new( "hud_inventory_delayed_show" )
					end
				end
			else
				--still want to keep track of is_pressed to show inventory when status is enabled
				Hud_inventory.is_pressed = true

				if Hud_player_status.inventory_disabled == false then
					hud_inventory_show()
				end
			end

		else

			Hud_inventory.is_pressed = false

			if Hud_inventory.tap_thread ~= nil then
				--only switch if the inventory is enabled
				if Hud_player_status.inventory_disabled == false then
					-- Counts as a tap, do a quick weapon switch
					--debug_print( "vint", "Inventory button was tapped, quick weapon switch\n" )
					inventory_switch_to_next_slot()
				end

				thread_kill( Hud_inventory.tap_thread )
				Hud_inventory.tap_thread = nil
			end

			if Hud_inventory.thread ~= nil then
				--Check to see if the item is selectable
				local slot = Hud_radial_menu.slots[Hud_radial_menu.slot_selected]
				if slot.availability == true and slot.bmp_name ~= nil and Hud_radial_menu.slot_selected ~= Hud_radial_menu.slot_equipped then
					--Slot is available and there is an item in the slot
					--Select item in game code
					use_radial_menu_item(Hud_radial_menu.slot_selected)
					if Hud_radial_menu.slot_selected < 8 then
						--If it wasn't a food item change the equipped slot
						Hud_radial_menu.slot_equipped = Hud_radial_menu.slot_selected
						local radial_is_visible =  vint_get_property(Hud_radial_menu.radial_grp_h, "visible")
						if radial_is_visible then
							if not Sui_weapon_switch_sound then
								audio_play(Hud_sounds.radial_equip_weapon)
							end
							Modern_hud_play_equip_sound = true
						end

					elseif Hud_radial_menu.slot_selected > 7 then
						--if a food item play sound for food.
						local radial_is_visible =  vint_get_property(Hud_radial_menu.radial_grp_h, "visible")
						if radial_is_visible then
							audio_play(Hud_sounds.radial_equip_food)
						end
					end
				end
				hud_inventory_hide()
			end
		end
	elseif event == "inventory_x" then
		Hud_inventory.x = value
		Hud_inventory.stale = true
	elseif event == "inventory_y" then
		Hud_inventory.y = value
		Hud_inventory.stale = true
	elseif event == "inventory_up" then
		--Note: Dpad events only occur on press and if the stick is not in use
		if value > 0.5 and Hud_radial_menu.stick_mag < 0.1 then
			Hud_radial_menu_change_select(8)
		end
	elseif event == "inventory_right" then
		if value > 0.5 and Hud_radial_menu.stick_mag < 0.1 then
			Hud_radial_menu_change_select(9)
		end
	elseif event == "inventory_down" then
		if value > 0.5 and Hud_radial_menu.stick_mag < 0.1 then
			Hud_radial_menu_change_select(10)
		end
	elseif event == "inventory_left" then
		if value > 0.5 and Hud_radial_menu.stick_mag < 0.1 then
			Hud_radial_menu_change_select(11)
		end
	end
end

function chat_input(target, event, accel)
	if mp_is_enabled() and (not get_is_tutorial()) then
		if event == "chat_all" then
			hud_open_chat_all_window()
		elseif event == "chat_team" then
			hud_open_chat_team_window()
		end
	elseif coop_is_active() then
		if event == "chat_all" and (Sui_cheat_shortcut_chat_all >= 0) then
			local is_active = cellphone_activate_cheat(Sui_cheat_shortcut_chat_all)

			if is_active then
				audio_play(DIALOG_SERIOUS_SOUND)
			else
				audio_play(DIALOG_OPEN_SOUND)
			end
		elseif event == "chat_team" then
			hud_open_chat_all_window()
		end
	else
		-- Cheat shortcut [nclok1405]
		if event == "chat_all" and (Sui_cheat_shortcut_chat_all >= 0) then
			local is_active = cellphone_activate_cheat(Sui_cheat_shortcut_chat_all)

			if is_active then
				audio_play(DIALOG_SERIOUS_SOUND)
			else
				audio_play(DIALOG_OPEN_SOUND)
			end
		elseif event == "chat_team" and (Sui_cheat_shortcut_chat_team >= 0) then
			local is_active = cellphone_activate_cheat(Sui_cheat_shortcut_chat_team)

			if is_active then
				audio_play(DIALOG_SERIOUS_SOUND)
			else
				audio_play(DIALOG_OPEN_SOUND)
			end
		end
	end
end

function hud_inventory_process()
	while true do
		if Hud_inventory.stale == true then

			local x = Hud_inventory.x
			local y = Hud_inventory.y
			local selected_weapon_index = 0
			local mag = sqrt((x * x) + (y * y))
			local pi = 3.14159

			if mag > 0.5 then

				-- Y resolves out so don't bother with it
				x = x/mag
				local radians = acos(x)

				if y < 0.0 then
					radians = pi + (pi - radians)
				end

				local eighth = pi / 8
				local fourth = pi / 4
				local selected_weapon_index = Hud_radial_menu.slot_equiped

				if radians < eighth then
					selected_weapon_index = 2;
				elseif radians < (fourth + eighth) then
					selected_weapon_index = 1
				elseif radians < (2.0 * fourth + eighth) then
					selected_weapon_index = 0
				elseif radians < (3.0 * fourth + eighth) then
					selected_weapon_index = 7
				elseif radians < (4.0 * fourth + eighth) then
					selected_weapon_index = 6
				elseif radians < (5.0 * fourth + eighth) then
					selected_weapon_index = 5
				elseif radians < (6.0 * fourth + eighth) then
					selected_weapon_index = 4;
				elseif radians < (7.0 * fourth + eighth) then
					selected_weapon_index = 3;
				else
					selected_weapon_index = 2;
				end

				--Change selected item in the menu
				Hud_radial_menu_change_select(selected_weapon_index)
			end

			--Update Stick location on radial menu
			local stick_pixel_mag = 12
			local x = Hud_inventory.x * stick_pixel_mag
			local y = -Hud_inventory.y * stick_pixel_mag
			vint_set_property(Hud_radial_menu.stick_grp_h, "anchor", x, y)

			Hud_radial_menu.stick_mag = mag
			Hud_inventory.stale = false
		end
		thread_yield()
	end
end

function hud_diversion_process()
	while true do
		-- If the player died wait until the death screen ends
		while Sui_player_dead do
			thread_yield()
		end

		-- Mission Failed
		if Sui_mission_fail_text ~= "" then
			delay(0.1)
			local title = vint_insert_values_in_string("[format][color:red]{0}[/format]", {[0] = "MISSION_FAILED"})
			hud_collection_msg_new(title, Sui_mission_fail_text, audio_get_audio_id("SYS_COMPLETION_FAIL"), -1)
			Sui_mission_fail_text = ""
		end

		-- Gameplay Changed
		if Sui_current_gameplay_title_crc ~= Modern_hud_active_gameplay_crc then
			if Modern_hud_active_gameplay_crc == 0 then
				-- New Gameplay Started
				if Sui_current_gameplay_title_crc == SUI_GAMEPLAY_CRC_TAXI then
					-- Taxi Started
					hud_collection_msg_new("DIVERSION_TAXI_TITLE", "TUT_DIV_INTRO_TAXI", DIALOG_OPEN_SOUND, -1)
				elseif Sui_current_gameplay_title_crc == SUI_GAMEPLAY_CRC_AMBULANCE then
					-- Ambulance EMT Started
					hud_collection_msg_new("DIVERSION_AMBULANCE_DIVERSION_TITLE_TEXT", "TUT_DIV_INTRO_AMBULANCE", DIALOG_OPEN_SOUND, -1)
				elseif Sui_current_gameplay_title_crc == SUI_GAMEPLAY_CRC_FIRETRUCK then
					-- Fire Truck Started
					hud_collection_msg_new("DIVERSION_FIRETRUCK_TITLE_TEXT", "TUT_DIV_INTRO_FIRE_TRUCK", DIALOG_OPEN_SOUND, -1)
				elseif Sui_current_gameplay_title_crc == SUI_GAMEPLAY_CRC_TOWTRUCK then
					-- Tow Truck Started
					hud_collection_msg_new("DIVERSION_TOW_TRUCK_DIVERSION_TITLE_TEXT", "TUT_DIV_INTRO_TOW_TRUCK", DIALOG_OPEN_SOUND, -1)
				elseif Sui_current_gameplay_title_crc == SUI_GAMEPLAY_CRC_DRIVEBY then
					-- Drive-by Started
					local msg = vint_insert_values_in_string("{0}\n{1}", {[0] = "DIVERSION_DRIVEBY_DIVERSION_DRIVE_BY_GANG_MEMBERS_STRING", [1] = "DIVERSION_DRIVEBY_DIVERSION_ONLY_KILLS_FROM_CAR_COUNT"})
					hud_collection_msg_new("DIVERSION_DRIVEBY_TITLE", msg, DIALOG_OPEN_SOUND, -1)
					Sui_driveby_bodycount = 0
				elseif Sui_current_gameplay_title_crc == SUI_GAMEPLAY_CRC_STREAKING then
					-- Streaking Started
					hud_collection_msg_new("DIVERSION_STREAKING_TITLE", "TUT_DIV_INTRO_STREAKING", DIALOG_OPEN_SOUND, -1)
					Sui_streaking_current_count = 0
					Sui_streaking_current_goal = 0
					Sui_streaking_confirmed_count = 0
				elseif Sui_current_gameplay_title_crc == SUI_GAMEPLAY_CRC_FLASHING then
					-- Flashing Started
					hud_collection_msg_new("DIVERSION_FLASHING_TITLE", "TUT_DIV_INTRO_STREAKING", DIALOG_OPEN_SOUND, -1)
					Sui_streaking_current_count = 0
					Sui_streaking_current_goal = 0
					Sui_streaking_confirmed_count = 0
				end
				Modern_hud_active_gameplay_playtime = 0
				Modern_hud_active_gameplay_start_cash = Sui_cash
			elseif Modern_hud_active_gameplay_crc == SUI_GAMEPLAY_CRC_TAXI then
				-- Taxi Ended
				local cash_earned = floor(Sui_cash - Modern_hud_active_gameplay_start_cash)
				local score_str = vint_insert_values_in_string("{0}: {1}\n{2}: ${3}\n{4}: {5}", {[0] = "DIVERSION_WHORING_LEVEL", [1] = Sui_current_gameplay_level, [2] = "STAT_TAXI_CASH", [3] = format_cash(cash_earned), [4] = "STAT_MP_TIME_PLAYED", [5] = sui_get_human_readable_time_float(Modern_hud_active_gameplay_playtime)})
				hud_collection_msg_new("DIVERSION_TAXI_TITLE", score_str, 0, -1)
				Modern_hud_active_gameplay_crc = 0
				Modern_hud_active_gameplay_playtime = 0
			elseif Modern_hud_active_gameplay_crc == SUI_GAMEPLAY_CRC_AMBULANCE then
				-- Ambulance EMT Ended
				local cash_earned = floor(Sui_cash - Modern_hud_active_gameplay_start_cash)
				local score_str = vint_insert_values_in_string("{0}: {1}\n{2}: ${3}\n{4}: {5}", {[0] = "DIVERSION_WHORING_LEVEL", [1] = Sui_current_gameplay_level, [2] = "MULTI_LEADERBOARD_MONEY", [3] = format_cash(cash_earned), [4] = "STAT_AMBULANCE_TIME", [5] = sui_get_human_readable_time_float(Modern_hud_active_gameplay_playtime)})
				hud_collection_msg_new("DIVERSION_AMBULANCE_DIVERSION_TITLE_TEXT", score_str, 0, -1)
				Modern_hud_active_gameplay_crc = 0
				Modern_hud_active_gameplay_playtime = 0
			elseif Modern_hud_active_gameplay_crc == SUI_GAMEPLAY_CRC_FIRETRUCK then
				-- Fire Truck Ended
				local cash_earned = floor(Sui_cash - Modern_hud_active_gameplay_start_cash)
				local score_str = vint_insert_values_in_string("{0}: {1}\n{2}: ${3}\n{4}: {5}", {[0] = "DIVERSION_WHORING_LEVEL", [1] = Sui_current_gameplay_level, [2] = "MULTI_LEADERBOARD_MONEY", [3] = format_cash(cash_earned), [4] = "STAT_FIRE_TIME", [5] = sui_get_human_readable_time_float(Modern_hud_active_gameplay_playtime)})
				hud_collection_msg_new("DIVERSION_FIRETRUCK_TITLE_TEXT", score_str, 0, -1)
				Modern_hud_active_gameplay_crc = 0
				Modern_hud_active_gameplay_playtime = 0
			elseif Modern_hud_active_gameplay_crc == SUI_GAMEPLAY_CRC_TOWTRUCK then
				-- Tow Truck Ended
				local cash_earned = floor(Sui_cash - Modern_hud_active_gameplay_start_cash)
				local score_str = vint_insert_values_in_string("{0}: {1}\n{2}: ${3}\n{4}: {5}", {[0] = "DIVERSION_WHORING_LEVEL", [1] = Sui_current_gameplay_level, [2] = "STAT_TOW_CASH", [3] = format_cash(cash_earned), [4] = "STAT_MP_TIME_PLAYED", [5] = sui_get_human_readable_time_float(Modern_hud_active_gameplay_playtime)})
				hud_collection_msg_new("DIVERSION_TOW_TRUCK_DIVERSION_TITLE_TEXT", score_str, 0, -1)
				Modern_hud_active_gameplay_crc = 0
				Modern_hud_active_gameplay_playtime = 0
			elseif Modern_hud_active_gameplay_crc == SUI_GAMEPLAY_CRC_DRIVEBY then
				-- Drive-by Ended
				local cash_earned = floor(Sui_cash - Modern_hud_active_gameplay_start_cash)
				local score_str = vint_insert_values_in_string("{0}: {1}\n{2} {3}\n{4}: ${5}\n{6}: {7}", {[0] = "DIVERSION_WHORING_LEVEL", [1] = Sui_current_gameplay_level, [2] = "DIVERSION_DRIVEBY_DIVERSION_BODY_COUNT_STRING", [3] = Sui_driveby_bodycount, [4] = "MULTI_LEADERBOARD_MONEY", [5] = format_cash(cash_earned), [6] = "STAT_MP_TIME_PLAYED", [7] = sui_get_human_readable_time_float(Modern_hud_active_gameplay_playtime)})
				hud_collection_msg_new("DIVERSION_DRIVEBY_TITLE", score_str, 0, -1)
				Modern_hud_active_gameplay_crc = 0
				Modern_hud_active_gameplay_playtime = 0
			elseif Modern_hud_active_gameplay_crc == SUI_GAMEPLAY_CRC_STREAKING then
				-- Streaking Ended
				local shocks = Sui_streaking_confirmed_count + Sui_streaking_current_count
				local score_str = vint_insert_values_in_string("{0}: {1}\n{2}: {3}\n{4}: {5}", {[0] = "DIVERSION_WHORING_LEVEL", [1] = Sui_current_gameplay_level, [2] = "STAT_STREAKING_PEOPLE", [3] = shocks, [4] = "STAT_MP_TIME_PLAYED", [5] = sui_get_human_readable_time_float(Modern_hud_active_gameplay_playtime)})
				hud_collection_msg_new("DIVERSION_STREAKING_TITLE", score_str, 0, -1)
				Modern_hud_active_gameplay_crc = 0
				Modern_hud_active_gameplay_playtime = 0
			elseif Modern_hud_active_gameplay_crc == SUI_GAMEPLAY_CRC_FLASHING then
				-- Flashing Ended
				local shocks = Sui_streaking_confirmed_count + Sui_streaking_current_count
				local score_str = vint_insert_values_in_string("{0}: {1}\n{2}: {3}\n{4}: {5}", {[0] = "DIVERSION_WHORING_LEVEL", [1] = Sui_current_gameplay_level, [2] = "STAT_FLASHING_PEOPLE", [3] = shocks, [4] = "STAT_MP_TIME_PLAYED", [5] = sui_get_human_readable_time_float(Modern_hud_active_gameplay_playtime)})
				hud_collection_msg_new("DIVERSION_FLASHING_TITLE", score_str, 0, -1)
				Modern_hud_active_gameplay_crc = 0
				Modern_hud_active_gameplay_playtime = 0
			end

			Modern_hud_active_gameplay_crc = Sui_current_gameplay_title_crc
		end

		-- Increase gameplay timer
		if not Sui_paused then
			Modern_hud_active_gameplay_playtime = Modern_hud_active_gameplay_playtime + get_frame_time()
		end

		thread_yield()
	end
end

function hud_process()

	local display_cash = Hud_player_status.cash - 1 --Subtract one so it gets formatted in the loop.
	local hud_had_focus = nil
	local old_hud_enable = -1

	-- Get Screen Edge Shadow handles [nclok1405]
	local vignette_h = vint_document_find("vignette")
	local vig_day_h = vint_object_find("vig_day", nil, vignette_h)
	local vig_scale_x, vig_scale_y = vint_get_property(vig_day_h, "scale")

	while true do
		thread_yield()

		-- HUD hide/enable
		if (not Sui_paused) and (old_hud_enable ~= Sui_hud_enable) then
			debug_print("HUD status changed from "..tostring(old_hud_enable).." to "..tostring(Sui_hud_enable).."\n")
			old_hud_enable = Sui_hud_enable
			if Sui_hud_enable == 0 then
				hud_hide(true)
			else
				hud_hide(false)
			end
		end

		-- Screen Edge Shadow [nclok1405]
		if Sui_vignette then
			vint_set_property(vig_day_h, "image", "ui_vignette_day")
			vint_set_property(vig_day_h, "scale", vig_scale_x, vig_scale_y)
		else
			vint_set_property(vig_day_h, "image", "ui_blank")

			-- Adjust the scale to make the blank square cover the entire screen (for fading effects)
			if vint_hack_is_std_res() then
				vint_set_property(vig_day_h, "scale", (640/16)+1, (480/16)+1)
			else
				vint_set_property(vig_day_h, "scale", (1280/16)+1, 768/16)
			end
		end

		-- Move HUD [nclok1405]
		if not Sui_hud_modern_layout then
			-- Classic
			vint_set_property(Hud_player_status.base_grp_h, "anchor", Modern_hud_weapon_circle_x, Modern_hud_weapon_circle_y)
			vint_set_property(Hud_player_status.cash_h, "anchor", Modern_hud_cash_x, Modern_hud_cash_y)
			vint_set_property(Hud_radial_menu.radial_grp_h, "anchor", Modern_hud_radial_x, Modern_hud_radial_y)
			vint_set_property(Hud_followers.main_grp_h, "anchor", Modern_hud_followers_x, Modern_hud_followers_y)
		elseif vint_hack_is_std_res() == false then
			-- Modern 16:9
			vint_set_property(Hud_player_status.base_grp_h, "anchor", Modern_hud_weapon_circle_x, Modern_hud_weapon_circle_y + 460)
			vint_set_property(Hud_player_status.cash_h, "anchor", Modern_hud_cash_x + 130, Modern_hud_cash_y)
			vint_set_property(Hud_radial_menu.radial_grp_h, "anchor", Modern_hud_radial_x - 360, Modern_hud_radial_y - 115)
			vint_set_property(Hud_followers.main_grp_h, "anchor", Modern_hud_followers_x + 45, Modern_hud_followers_y)
		else
			-- Modern 4:3
			vint_set_property(Hud_player_status.base_grp_h, "anchor", Modern_hud_weapon_circle_x, Modern_hud_weapon_circle_y + 300)
			vint_set_property(Hud_player_status.cash_h, "anchor", Modern_hud_cash_x + 80, Modern_hud_cash_y)
			vint_set_property(Hud_radial_menu.radial_grp_h, "anchor", Modern_hud_radial_x - 150, Modern_hud_radial_y - 85)
			vint_set_property(Hud_followers.main_grp_h, "anchor", Modern_hud_followers_x + 28, Modern_hud_followers_y)
		end

		if Sui_hud_enable < 2 then
			-- If HUD is disabled do not unhide things [nclok1405]
			Modern_hud_health_unhiding = false
			Modern_hud_sprint_unhiding = false
			Modern_hud_respect_unhiding = false
			Modern_hud_weapon_unhiding = false
			Modern_hud_followers_unhiding = false
			Modern_hud_cash_unhiding = false
		elseif not Sui_hud_autohide then
			-- If autohide is disabled always unhide everything [nclok1405]
			Modern_hud_health_unhiding = true
			Modern_hud_sprint_unhiding = true
			Modern_hud_respect_unhiding = true
			Modern_hud_weapon_unhiding = true
			Modern_hud_followers_unhiding = true
			Modern_hud_cash_unhiding = true
		end

		-- Autohide/Unhide Health [nclok1405]
		if (Sui_hud_enable == 2) and (Hud_player_status.health_pct > 0) and (Hud_player_status.health_pct < 1) then
			Modern_hud_health_unhiding = true
		end

		if Modern_hud_health_unhiding then
			Modern_hud_health_frames = 0
			Modern_hud_weapon_unhiding = true
			Modern_hud_health_visibility = Modern_hud_health_visibility + 10

			if (Modern_hud_health_visibility > 100) then
				Modern_hud_health_visibility = 100
				Modern_hud_health_unhiding = false
			end

			if (Hud_player_status.health_pct <= 0) then
				vint_set_property(Hud_player_status.health_bar.bg_h, "visible", false)
			else
				vint_set_property(Hud_player_status.health_bar.bg_h, "visible", true)
				vint_set_property(Hud_player_status.health_bar.bg_h, "alpha", Modern_hud_health_visibility / 100)
			end

			vint_set_property(Hud_player_status.health_bar.fill_0_h, "visible", true)
			vint_set_property(Hud_player_status.health_bar.fill_1_h, "visible", true)
			vint_set_property(Hud_player_status.health_bar.fill_decay_h, "visible", true)

			vint_set_property(Hud_player_status.health_bar.fill_0_h, "alpha", Modern_hud_health_visibility / 100)
			vint_set_property(Hud_player_status.health_bar.fill_1_h, "alpha", Modern_hud_health_visibility / 100)
			vint_set_property(Hud_player_status.health_bar.fill_decay_h, "alpha", Modern_hud_health_visibility / 100)
		else
			Modern_hud_health_frames = Modern_hud_health_frames + get_frame_time()

			if (Modern_hud_health_frames >= 2) then
				Modern_hud_health_visibility = Modern_hud_health_visibility - 5

				if (Modern_hud_health_visibility <= 0) then
					Modern_hud_health_visibility = 0
					vint_set_property(Hud_player_status.health_bar.bg_h, "visible", false)
					vint_set_property(Hud_player_status.health_bar.fill_0_h, "visible", false)
					vint_set_property(Hud_player_status.health_bar.fill_1_h, "visible", false)
					vint_set_property(Hud_player_status.health_bar.fill_decay_h, "visible", false)
				else
					vint_set_property(Hud_player_status.health_bar.bg_h, "visible", true)
					vint_set_property(Hud_player_status.health_bar.fill_0_h, "visible", true)
					vint_set_property(Hud_player_status.health_bar.fill_1_h, "visible", true)
					vint_set_property(Hud_player_status.health_bar.fill_decay_h, "visible", true)

					vint_set_property(Hud_player_status.health_bar.bg_h, "alpha", Modern_hud_health_visibility / 100)
					vint_set_property(Hud_player_status.health_bar.fill_0_h, "alpha", Modern_hud_health_visibility / 100)
					vint_set_property(Hud_player_status.health_bar.fill_1_h, "alpha", Modern_hud_health_visibility / 100)
					vint_set_property(Hud_player_status.health_bar.fill_decay_h, "alpha", Modern_hud_health_visibility / 100)
				end
			end
		end

		-- Autohide/Unhide Sprint
		if (Sui_hud_enable == 2) and (Hud_player_status.sprint_pct < 0.99) then
			Modern_hud_sprint_unhiding = true
		end

		if Modern_hud_sprint_unhiding then
			Modern_hud_sprint_frames = 0
			Modern_hud_weapon_unhiding = true
			Modern_hud_sprint_visibility = Modern_hud_sprint_visibility + 10

			if (Modern_hud_sprint_visibility > 100) then
				Modern_hud_sprint_visibility = 100
				Modern_hud_sprint_unhiding = false
			end

			if (Hud_player_status.sprint_pct <= 0) then
				vint_set_property(Hud_player_status.sprint_bar.bg_h, "visible", false)
				vint_set_property(Hud_player_status.sprint_bar.fill_0_h, "visible", false)
				vint_set_property(Hud_player_status.sprint_bar.fill_1_h, "visible", false)
			else
				vint_set_property(Hud_player_status.sprint_bar.bg_h, "visible", true)
				vint_set_property(Hud_player_status.sprint_bar.fill_0_h, "visible", true)
				vint_set_property(Hud_player_status.sprint_bar.fill_1_h, "visible", true)

				vint_set_property(Hud_player_status.sprint_bar.bg_h, "alpha", Modern_hud_sprint_visibility / 100)
				vint_set_property(Hud_player_status.sprint_bar.fill_0_h, "alpha", Modern_hud_sprint_visibility / 100)
				vint_set_property(Hud_player_status.sprint_bar.fill_1_h, "alpha", Modern_hud_sprint_visibility / 100)
			end
		else
			Modern_hud_sprint_frames = Modern_hud_sprint_frames + get_frame_time()

			if (Modern_hud_sprint_frames >= 2) then
				Modern_hud_sprint_visibility = Modern_hud_sprint_visibility - 5

				if (Modern_hud_sprint_visibility <= 0) then
					Modern_hud_sprint_visibility = 0
					vint_set_property(Hud_player_status.sprint_bar.bg_h, "visible", false)
					vint_set_property(Hud_player_status.sprint_bar.fill_0_h, "visible", false)
					vint_set_property(Hud_player_status.sprint_bar.fill_1_h, "visible", false)
				else
					vint_set_property(Hud_player_status.sprint_bar.bg_h, "alpha", Modern_hud_sprint_visibility / 100)
					vint_set_property(Hud_player_status.sprint_bar.fill_0_h, "alpha", Modern_hud_sprint_visibility / 100)
					vint_set_property(Hud_player_status.sprint_bar.fill_1_h, "alpha", Modern_hud_sprint_visibility / 100)
				end
			end
		end

		-- Autohide/Unhide Respect
		if (Modern_hud_respect_last_level ~= Hud_player_status.respect_int) then
			Modern_hud_respect_unhiding = true
			Modern_hud_weapon_unhiding = true
			Modern_hud_respect_last_level = Hud_player_status.respect_int
		end
		if (Modern_hud_respect_last_percent ~= Hud_player_status.respect_bar_percent) then
			Modern_hud_respect_unhiding = true
			Modern_hud_respect_last_percent = Hud_player_status.respect_bar_percent
		end

		-- Do not show respect on HUD disabled or Multiplayer
		if (Sui_hud_enable < 2) or mp_is_enabled() then
			Modern_hud_respect_unhiding = false
			Modern_hud_respect_frames = 5
			Modern_hud_respect_visibility = 0
		end

		if Modern_hud_respect_unhiding then
			Modern_hud_respect_frames = 0
			Modern_hud_respect_visibility = Modern_hud_respect_visibility + 10

			if (Modern_hud_respect_visibility >= 100) then
				Modern_hud_respect_visibility = 100
				Modern_hud_respect_unhiding = false
			end

			if (Hud_player_status.respect_bar_percent <= 0) then
				vint_set_property(Hud_player_status.respect_bar.bg_h, "visible", false)
			else
				vint_set_property(Hud_player_status.respect_bar.bg_h, "visible", true)
				vint_set_property(Hud_player_status.respect_bar.bg_h, "alpha", Modern_hud_respect_visibility / 100)
			end

			vint_set_property(Hud_player_status.respect_bar.fill_0_h, "visible", true)
			vint_set_property(Hud_player_status.respect_bar.fill_1_h, "visible", true)
			vint_set_property(Hud_player_status.respect_bar.txt_grp, "visible", true)
			vint_set_property(Hud_player_status.respect_bar.txt, "visible", true)

			vint_set_property(Hud_player_status.respect_bar.fill_0_h, "alpha", Modern_hud_respect_visibility / 100)
			vint_set_property(Hud_player_status.respect_bar.fill_1_h, "alpha", Modern_hud_respect_visibility / 100)
			vint_set_property(Hud_player_status.respect_bar.txt_grp, "alpha", Modern_hud_respect_visibility / 100)
			vint_set_property(Hud_player_status.respect_bar.txt, "alpha", Modern_hud_respect_visibility / 100)
		else
			Modern_hud_respect_frames = Modern_hud_respect_frames + get_frame_time()

			if (Modern_hud_respect_frames >= 5) then
				Modern_hud_respect_visibility = Modern_hud_respect_visibility - 5

				if (Modern_hud_respect_visibility <= 0) then
					Modern_hud_respect_visibility = 0
					vint_set_property(Hud_player_status.respect_bar.bg_h, "visible", false)
					vint_set_property(Hud_player_status.respect_bar.fill_0_h, "visible", false)
					vint_set_property(Hud_player_status.respect_bar.fill_1_h, "visible", false)
					vint_set_property(Hud_player_status.respect_bar.txt_grp, "visible", false)
					vint_set_property(Hud_player_status.respect_bar.txt, "visible", false)
				else
					if (Hud_player_status.respect_bar_percent <= 0) then
						vint_set_property(Hud_player_status.respect_bar.bg_h, "visible", false)
					else
						vint_set_property(Hud_player_status.respect_bar.bg_h, "visible", true)
						vint_set_property(Hud_player_status.respect_bar.bg_h, "alpha", Modern_hud_respect_visibility / 100)
					end

					vint_set_property(Hud_player_status.respect_bar.fill_0_h, "visible", true)
					vint_set_property(Hud_player_status.respect_bar.fill_1_h, "visible", true)
					vint_set_property(Hud_player_status.respect_bar.txt_grp, "visible", true)
					vint_set_property(Hud_player_status.respect_bar.txt, "visible", true)

					vint_set_property(Hud_player_status.respect_bar.fill_0_h, "alpha", Modern_hud_respect_visibility / 100)
					vint_set_property(Hud_player_status.respect_bar.fill_1_h, "alpha", Modern_hud_respect_visibility / 100)
					vint_set_property(Hud_player_status.respect_bar.txt_grp, "alpha", Modern_hud_respect_visibility / 100)
					vint_set_property(Hud_player_status.respect_bar.txt, "alpha", Modern_hud_respect_visibility / 100)
				end
			end
		end

		-- In HUD disabled, liquor store is active, or in Demolition Derby, always hide the weapon circle
		if (Sui_hud_enable < 2) or Sui_liquor_store_active or sui_is_demo_derby() then
			Modern_hud_weapon_unhiding = false
			Modern_hud_weapon_frames = 5
			Modern_hud_weapon_visibility = 0
		end

		-- Zombie Uprising
		if (Sui_hud_enable == 2) and sui_is_zombie() then
			if Sui_normal_hud_in_zombie and (not Sui_player_dead) then
				-- If Normal HUD in Zombie Uprising option is enabled, show map (unless player died)
				vint_set_property(Hud_map.base_grp_h, "visible", true)
				vint_set_property(Hud_map.base_grp_h, "alpha", 1)
			else
				-- Otherwise hide weapon circle as in vanilla game
				Modern_hud_weapon_unhiding = false
				Modern_hud_weapon_frames = 5
				Modern_hud_weapon_visibility = 0
				-- Also hide the map, which will reappear after buying a food in the Mall
				vint_set_property(Hud_map.base_grp_h, "alpha", 0)
			end
		end

		-- If the player died, force autohiding weapon circle
		if Sui_player_dead then
			Modern_hud_weapon_unhiding = false
			Modern_hud_weapon_frames = 5
		end

		-- Autohide Weapon Circle [nclok1405]
		if Modern_hud_weapon_unhiding then
			Modern_hud_weapon_frames = 0
			Modern_hud_weapon_visibility = Modern_hud_weapon_visibility + 10
			if (Modern_hud_weapon_visibility >= 100) then
				Modern_hud_weapon_visibility = 100
				Modern_hud_weapon_unhiding = false
			end
			vint_set_property(Hud_player_status.base_grp_h, "visible", true)
			vint_set_property(Hud_player_status.base_grp_h, "alpha", Modern_hud_weapon_visibility / 100)
		else
			Modern_hud_weapon_frames = Modern_hud_weapon_frames + get_frame_time()
			if (Modern_hud_weapon_frames >= 5) then
				Modern_hud_weapon_visibility = Modern_hud_weapon_visibility - 5

				if (Modern_hud_weapon_visibility <= 0) then
					Modern_hud_weapon_visibility = 0
					vint_set_property(Hud_player_status.base_grp_h, "visible", false)
				else
					vint_set_property(Hud_player_status.base_grp_h, "visible", true)
					vint_set_property(Hud_player_status.base_grp_h, "alpha", Modern_hud_weapon_visibility / 100)
				end
			end
		end

		-- Animate Cash
		local cur_cash = Hud_player_status.cash
		if sui_is_zombie() and Sui_normal_hud_in_zombie then
			-- Show score using cash display in Zombie Uprising new HUD
			cur_cash = Sui_zombie_final_score

			if (Sui_zombie_final_score == 0) then
				-- Reset Score Display
				display_cash = 0
				Modern_hud_cash_tint_red = 100
				Modern_hud_cash_tint_green = 100
				Modern_hud_cash_tint_blue = 100
				vint_set_property(Hud_player_status.cash_h, "text_tag", "0")
			end
		end

		if display_cash ~= cur_cash then
			Modern_hud_cash_unhiding = true

			local diff_cash = cur_cash - display_cash

			if (Modern_hud_cash_visibility >= 100) then
				if (diff_cash < 0) then
					-- Cash is Decreasing
					if SUI_CASH_TINT_DOWN then
						Modern_hud_cash_tint_red = 100
						Modern_hud_cash_tint_green = 0
						Modern_hud_cash_tint_blue = 0
					end
				elseif (diff_cash > 0) then
					-- Cash is Increasing
					if SUI_CASH_TINT_UP then
						Modern_hud_cash_tint_red = 0
						Modern_hud_cash_tint_green = 100
						Modern_hud_cash_tint_blue = 0
					end
				end

				if diff_cash > 5 or diff_cash < -5 then
					diff_cash = floor(diff_cash * 0.5)
				end

				display_cash = display_cash + diff_cash

				if sui_is_zombie() then
					vint_set_property(Hud_player_status.cash_h, "text_tag", format_cash(display_cash))
				else
					vint_set_property(Hud_player_status.cash_h, "text_tag", "$" .. format_cash(display_cash))
				end
			end
		end

		-- Set Cash Tint [nclok1405]
		vint_set_property(Hud_player_status.cash_h, "tint", Modern_hud_cash_tint_red / 100, Modern_hud_cash_tint_green / 100, Modern_hud_cash_tint_blue / 100)

		Modern_hud_cash_tint_red = Modern_hud_cash_tint_red + 1
		Modern_hud_cash_tint_green = Modern_hud_cash_tint_green + 1
		Modern_hud_cash_tint_blue = Modern_hud_cash_tint_blue + 1

		if (Modern_hud_cash_tint_red > 100) then
			Modern_hud_cash_tint_red = 100
		end
		if (Modern_hud_cash_tint_green > 100) then
			Modern_hud_cash_tint_green = 100
		end
		if (Modern_hud_cash_tint_blue > 100) then
			Modern_hud_cash_tint_blue = 100
		end

		-- Hide Cash in No HUD, MP, Demo Derby Menu, Original Zombie HUD, and Liquor Store [nclok1405]
		if (Sui_hud_enable < 2) or mp_is_enabled() or sui_is_demo_derby_menu() or (sui_is_zombie() and (not Sui_normal_hud_in_zombie)) or Sui_liquor_store_active then
			Modern_hud_cash_unhiding = false
			Modern_hud_cash_frames = 5
			Modern_hud_cash_visibility = 0
		end

		-- Autohide/Unhide Cash [nclok1405]
		if Modern_hud_cash_unhiding then
			Modern_hud_cash_frames = 0

			Modern_hud_cash_visibility = Modern_hud_cash_visibility + 10
			if (Modern_hud_cash_visibility >= 100) then
				Modern_hud_cash_visibility = 100
				Modern_hud_cash_unhiding = false
			end
			vint_set_property(Hud_player_status.cash_h, "visible", true)
			vint_set_property(Hud_player_status.cash_h, "alpha", Modern_hud_cash_visibility / 100)
		else
			Modern_hud_cash_frames = Modern_hud_cash_frames + get_frame_time()

			if (Modern_hud_cash_frames >= 5) then
				Modern_hud_cash_visibility = Modern_hud_cash_visibility - 5

				if (Modern_hud_cash_visibility <= 0) then
					Modern_hud_cash_visibility = 0
					vint_set_property(Hud_player_status.cash_h, "visible", false)
				else
					vint_set_property(Hud_player_status.cash_h, "visible", true)
					vint_set_property(Hud_player_status.cash_h, "alpha", Modern_hud_cash_visibility / 100)
				end
			end
		end

		-- Autohide/Unhide Homies [nclok1405]
		if (Sui_hud_enable < 2) or mp_is_enabled() or Sui_liquor_store_active or sui_is_demo_derby() or sui_is_zombie() then
			-- Do not display homies in Multiplayer, Liquor Store, Demo Derby, or Zombie
			Modern_hud_followers_unhiding = false
			Modern_hud_followers_frames = 10
			Modern_hud_followers_visibility = 0
		end

		if Modern_hud_followers_unhiding then
			Modern_hud_followers_frames = 0
			Modern_hud_followers_visibility = Modern_hud_followers_visibility + 10

			if (Modern_hud_followers_visibility >= 100) then
				Modern_hud_followers_visibility = 100
				Modern_hud_followers_unhiding = false
			end

			for i = 1, 3 do
				if Hud_followers.slot_objects[i].visible then
					vint_set_property(Hud_followers.slot_objects[i].group_h, "visible", true)
					vint_set_property(Hud_followers.slot_objects[i].group_h, "alpha", Modern_hud_followers_visibility / 100)
				end
			end
		else
			Modern_hud_followers_frames = Modern_hud_followers_frames + get_frame_time()

			local autohide_delay = 5
			if (Hud_followers.follower_data[1].head_img_name ~= nil) or (Hud_followers.follower_data[2].head_img_name ~= nil) or (Hud_followers.follower_data[3].head_img_name ~= nil) then
				autohide_delay = 10
			end

			if (Modern_hud_followers_frames >= autohide_delay) then
				Modern_hud_followers_visibility = Modern_hud_followers_visibility - 5

				if (Modern_hud_followers_visibility <= 0) then
					Modern_hud_followers_visibility = 0

					for i = 1, 3 do
						vint_set_property(Hud_followers.slot_objects[i].group_h, "visible", false)
					end
				else
					for i = 1, 3 do
						if Hud_followers.slot_objects[i].visible then
							vint_set_property(Hud_followers.slot_objects[i].group_h, "visible", true)
							vint_set_property(Hud_followers.slot_objects[i].group_h, "alpha", Modern_hud_followers_visibility / 100)
						end
					end
				end
			end
		end

		-- Set map background and notoriety visibility [nclok1405]
		-- Determine target background visibility
		local notobg_target_visibility = 0	-- No notoriety
		if (get_pending_game_play_mode() == "Braveheart") or (get_game_play_mode() == "Braveheart") then
			notobg_target_visibility = 100	-- Strongarm has notoriety-like "Tag" icons
		elseif (Hud_noto_data.gangs.cur_level >= 1) or (Hud_noto_data.police.cur_level >= 1) then
			notobg_target_visibility = 100	-- Level 1+ notoriety
		elseif (Hud_noto_data.gangs.cur_level > 0) or (Hud_noto_data.police.cur_level > 0) then
			notobg_target_visibility = 50	-- Level 0 notoriety
		end
		if (not Sui_hud_autohide) then
			notobg_target_visibility = 100	-- If autohide is disabled, always show BG
		end
		if (Sui_hud_enable < 2) then
			notobg_target_visibility = 0	-- If HUD disabled do not show BG
		end

		if (Modern_hud_notobg_visibility < notobg_target_visibility) then
			Modern_hud_notobg_visibility = Modern_hud_notobg_visibility + 5
			if (Modern_hud_notobg_visibility > notobg_target_visibility) then
				Modern_hud_notobg_visibility = notobg_target_visibility
			end
		elseif (Modern_hud_notobg_visibility > notobg_target_visibility) then
			Modern_hud_notobg_visibility = Modern_hud_notobg_visibility - 5
			if (Modern_hud_notobg_visibility < notobg_target_visibility) then
				Modern_hud_notobg_visibility = notobg_target_visibility
			end
		end

		vint_set_property(Hud_map.base_top_h, "visible", (Modern_hud_notobg_visibility > 0))
		vint_set_property(Hud_map.base_bottom_h, "visible", (Modern_hud_notobg_visibility > 0))
		vint_set_property(Hud_map.base_top_h, "alpha", Modern_hud_notobg_visibility / 100)
		vint_set_property(Hud_map.base_bottom_h, "alpha", Modern_hud_notobg_visibility / 100)

		if (Hud_noto_data.gangs.cur_level > 0) then
			vint_set_property(Hud_noto_data.gangs.meter.meter_fill_0_h, "visible", (Modern_hud_notobg_visibility > 0))
			vint_set_property(Hud_noto_data.gangs.meter.meter_fill_1_h, "visible", (Modern_hud_notobg_visibility > 0))
			vint_set_property(Hud_noto_data.gangs.meter.meter_fill_0_h, "alpha", Modern_hud_notobg_visibility / 100)
			vint_set_property(Hud_noto_data.gangs.meter.meter_fill_1_h, "alpha", Modern_hud_notobg_visibility / 100)
		else
			vint_set_property(Hud_noto_data.gangs.meter.meter_fill_0_h, "visible", false)
			vint_set_property(Hud_noto_data.gangs.meter.meter_fill_1_h, "visible", false)
		end
		if (Hud_noto_data.gangs.cur_meter > 0) then
			vint_set_property(Hud_noto_data.gangs.meter.meter_bg_h, "visible", (Modern_hud_notobg_visibility > 0))
			vint_set_property(Hud_noto_data.gangs.meter.meter_bg_h, "alpha", Modern_hud_notobg_visibility / 100)
		else
			vint_set_property(Hud_noto_data.gangs.meter.meter_bg_h, "visible", false)
		end

		if (Hud_noto_data.police.cur_level > 0) then
			vint_set_property(Hud_noto_data.police.meter.meter_fill_0_h, "visible", (Modern_hud_notobg_visibility > 0))
			vint_set_property(Hud_noto_data.police.meter.meter_fill_1_h, "visible", (Modern_hud_notobg_visibility > 0))
			vint_set_property(Hud_noto_data.police.meter.meter_fill_0_h, "alpha", Modern_hud_notobg_visibility / 100)
			vint_set_property(Hud_noto_data.police.meter.meter_fill_1_h, "alpha", Modern_hud_notobg_visibility / 100)
		else
			vint_set_property(Hud_noto_data.police.meter.meter_fill_0_h, "visible", false)
			vint_set_property(Hud_noto_data.police.meter.meter_fill_1_h, "visible", false)
		end
		if (Hud_noto_data.police.cur_meter > 0) then
			vint_set_property(Hud_noto_data.police.meter.meter_bg_h, "visible", (Modern_hud_notobg_visibility > 0))
			vint_set_property(Hud_noto_data.police.meter.meter_bg_h, "alpha", Modern_hud_notobg_visibility / 100)
		else
			vint_set_property(Hud_noto_data.police.meter.meter_bg_h, "visible", false)
		end

		-- If HUD is disabled, in Fight Club, in Demo Derby Menu, or the player died, hide map
		if (Sui_hud_enable < 2) or Sui_fight_club or sui_is_demo_derby_menu() or Sui_player_dead then
			vint_set_property(Hud_map.base_grp_h, "alpha", 0)
		end

		-- If HUD is disabled or in Demo Derby menu, hide GSI
		if (Sui_hud_enable < 2) or sui_is_demo_derby_menu() then
			vint_set_property(vint_object_find("gsi_base_grp"), "alpha", 0)
		end

		-- Custom Timer [nclok1405]
		if Sui_custom_hud_timer_active and (not Sui_paused) then
			Sui_custom_hud_timer_value = Sui_custom_hud_timer_value - get_frame_time()
			if Sui_custom_hud_timer_value < 0 then
				Sui_custom_hud_timer_value = 0
			end
		end

		if (Sui_hud_enable == 2) and Hud_balance_status.active and (not mp_is_enabled()) then
			-- Vehicle Surfing Time (do not enable on multiplayer)
			if not Sui_paused then
				Modern_hud_vehicle_surfing_time = Modern_hud_vehicle_surfing_time + get_frame_time()
			end

			local seconds = floor(Modern_hud_vehicle_surfing_time)
			local sub = Modern_hud_vehicle_surfing_time - seconds
			local sub2 = floor(sub * 10)
			local str = seconds .. "." .. sub2

			vint_set_property(Hud_enemy_status.count_txt_h, "text_tag", str)

			local x = 500
			if vint_hack_is_std_res() then
				x = 360
			end
			vint_set_property(Hud_enemy_status.grp_h, "anchor", Hud_enemy_status.grp_x + x, Hud_enemy_status.grp_y - 300)
		elseif (Sui_hud_enable == 2) and (not mp_is_enabled()) and Sui_custom_hud_active then
			-- Custom HUD [nclok1405]
			local custom_str = ""

			if Sui_custom_hud_timer_active then
				local timer_str = sui_get_human_readable_time_float(Sui_custom_hud_timer_value)

				if Sui_custom_hud_timer_value < 10 then
					custom_str = "[format][color:red]" .. timer_str .. "[/format]\n"
				else
					custom_str = "[format][color:yellow]" .. timer_str .. "[/format]\n"
				end
			end

			if Sui_custom_hud_number_active then
				custom_str = custom_str .. tostring(Sui_custom_hud_number_value)
			end

			vint_set_property(Hud_enemy_status.count_txt_h, "text_tag", custom_str)
			vint_set_property(Hud_enemy_status.grp_h, "anchor", Hud_enemy_status.grp_x, Hud_enemy_status.grp_y - 545)
		else
			vint_set_property(Hud_enemy_status.count_txt_h, "text_tag", "")
		end

		--[[
		local frame_time = get_frame_time()
		vint_set_property(Hud_enemy_status.count_txt_h, "text_tag", tostring(frame_time))
		vint_set_property(Hud_enemy_status.grp_h, "anchor", Hud_enemy_status.grp_x, Hud_enemy_status.grp_y - 545)
		--]]

		-- check to see if the hud has lost focus
		if hud_had_focus ~= Hud_has_focus then
			if Hud_has_focus == false then
				hud_inventory_disable()
			else
				hud_inventory_enable()

				-- Unhide HUD
				if (Sui_hud_enable == 2) then
					if (Hud_player_status.health_pct > 0) and (Hud_player_status.health_pct < 1) then
						Modern_hud_health_unhiding = true
					end
					if (Hud_player_status.sprint_pct < 0.99) then
						Modern_hud_sprint_unhiding = true
					end
					if (Hud_player_status.respect_int < 99) then
						Modern_hud_respect_unhiding = true
					end
					Modern_hud_weapon_unhiding = true
					Modern_hud_followers_unhiding = true
					Modern_hud_cash_unhiding = true

					-- Unhide Map unless Fight Club is active
					if (not Sui_fight_club) then
						vint_set_property(Hud_map.base_grp_h, "alpha", 1)
					end

					-- Unhide GSI
					vint_set_property(vint_object_find("gsi_base_grp"), "alpha", 1)
				end
			end
			hud_had_focus = Hud_has_focus
		end

		hud_msg_process()
	end
end

function hud_inventory_enable()
	if Hud_has_focus == true then
		--Can only enable inventory if HUD has focus
		Hud_inventory.subs = vint_subscribe_to_raw_input("inventory", "hud_inventory_input")

		Hud_inventory.subs_chat_all = vint_subscribe_to_input_event(nil, "chat_all", "chat_input")
		Hud_inventory.subs_chat_team = vint_subscribe_to_input_event(nil, "chat_team", "chat_input")
	end
end

function hud_inventory_disable()
	if Hud_inventory.thread ~= nil then
		--Hud lost focus so kill the inventory
		hud_inventory_hide()
	end

	if Hud_inventory.subs ~= nil then
		vint_unsubscribe_to_raw_input(Hud_inventory.subs)
	end
	if Hud_inventory.subs_chat_all ~= nil then
		vint_unsubscribe_to_input_event(Hud_inventory.subs_chat_all)
		vint_unsubscribe_to_input_event(Hud_inventory.subs_chat_team)
	end
	Hud_inventory = { }
end

-- Thread function to delay showing the inventory hud in case the player wants to tap the button
function hud_inventory_delayed_show()
	-- It's a tap if the button's released within 1/5 of a second
	delay( 0.2 )

	-- Double-check disabling before we actually open the inventory
	if not Hud_player_status.inventory_disabled then
		hud_inventory_show()
	end

	Hud_inventory.is_pressed = true

	Hud_inventory.tap_thread = nil
end

function hud_inventory_show()

	hud_update_inventory()

	if Hud_inventory.thread == nil then
		--Show Inventory

		vint_set_property(Hud_radial_menu.radial_grp_h, "visible", true)


		--Subscribe to input
		Hud_inventory.extra_buttons = {
			vint_subscribe_to_input_event(nil, "alt_select", "hud_inventory_input"),
			vint_subscribe_to_input_event(nil, "select", "hud_inventory_input"),
			vint_subscribe_to_input_event(nil, "exit", "hud_inventory_input"),
			vint_subscribe_to_input_event(nil, "back", "hud_inventory_input"),
			vint_subscribe_to_input_event(nil, "white", "hud_inventory_input"),
			vint_subscribe_to_input_event(nil, "black", "hud_inventory_input"),
			vint_subscribe_to_input_event(nil, "map", "hud_inventory_input"),
			vint_subscribe_to_input_event(nil, "pause", "hud_inventory_input"),
			vint_subscribe_to_input_event(nil, "scroll_up", "hud_inventory_input"),
			vint_subscribe_to_input_event(nil, "scroll_down", "hud_inventory_input"),
			--vint_subscribe_to_input_event(nil, "scroll_left", "hud_inventory_input"),
			--vint_subscribe_to_input_event(nil, "scroll_right", "hud_inventory_input"),
		}

		Hud_inventory.subs_x = vint_subscribe_to_raw_input("inventory_x", "hud_inventory_input")
		Hud_inventory.subs_y = vint_subscribe_to_raw_input("inventory_y", "hud_inventory_input")
		Hud_inventory.subs_up = vint_subscribe_to_raw_input("inventory_up", "hud_inventory_input")
		Hud_inventory.subs_right = vint_subscribe_to_raw_input("inventory_right", "hud_inventory_input")
		Hud_inventory.subs_down = vint_subscribe_to_raw_input("inventory_down", "hud_inventory_input")
		Hud_inventory.subs_left = vint_subscribe_to_raw_input("inventory_left", "hud_inventory_input")

		--Reset visual analog stick and get the proper text tag on it.
		Hud_inventory.x = 0
		Hud_inventory.y = 0
		vint_set_property(Hud_radial_menu.stick_grp_h, "anchor", 0, 0)
		--vint_set_property(Hud_radial_menu.stick_text_h, "text_tag", Hud_inv_select_stick)
		vint_set_property(Hud_radial_menu.stick_text_h, "text_tag", get_control_stick_text())
		Hud_radial_menu_change_select(Hud_radial_menu.slot_equipped)

		audio_play(Hud_sounds.radial_open)

		--vint_set_property(Hud_radial_menu.stick_grp_h,"anchor", 0, 0)
		Hud_inventory.thread = thread_new("hud_inventory_process")

		-- Unhide weapon circle [nclok1405]
		Modern_hud_weapon_unhiding = true
	end
end

function hud_inventory_hide()
	if Hud_inventory.thread ~= nil then
		--Hide Inventory
		vint_set_property(Hud_radial_menu.radial_grp_h, "visible", false)
		vint_unsubscribe_to_raw_input(Hud_inventory.subs_x)
		vint_unsubscribe_to_raw_input(Hud_inventory.subs_y)
		vint_unsubscribe_to_raw_input(Hud_inventory.subs_up)
		vint_unsubscribe_to_raw_input(Hud_inventory.subs_right)
		vint_unsubscribe_to_raw_input(Hud_inventory.subs_down)
		vint_unsubscribe_to_raw_input(Hud_inventory.subs_left)

		for idx, val in Hud_inventory.extra_buttons do
			vint_unsubscribe_to_input_event(val)
		end
		Hud_inventory.extra_buttons = nil
		thread_kill(Hud_inventory.thread)
		Hud_inventory.thread = nil
	end

	-- Kill a delayed show thread
	if Hud_inventory.tap_thread ~= nil then
		thread_kill( Hud_inventory.tap_thread )
		Hud_inventory.tap_thread = nil
	end

end

---------------------
--Food inventory for the food/liqour store
--------------------
function hud_inventory_food_show()
	--Show Inventory
	vint_set_property(Hud_radial_menu.radial_grp_h, "visible", true)
	vint_set_property(vint_object_find("control_stick", Hud_radial_menu.radial_grp_h), "visible", false)
	vint_set_property(Hud_radial_menu.slot_desc_h, "visible", false)
	vint_set_property(Hud_radial_menu.dpad_highlight_h, "visible", false)
	vint_set_property(Hud_radial_menu.selector_h, "visible", false)

	--Hide the radial slots...
	local slot_h
	for i = 0, 7 do
		vint_set_property(Hud_radial_menu.slots[i].grp_h, "visible", false)
	end
end



function hud_inventory_food_hide()
	--Hide Inventory
	vint_set_property(Hud_radial_menu.radial_grp_h, "visible", false)
	vint_set_property(vint_object_find("control_stick", Hud_radial_menu.radial_grp_h), "visible", true)
	vint_set_property(Hud_radial_menu.slot_desc_h, "visible", true)
	vint_set_property(Hud_radial_menu.dpad_highlight_h, "visible", true)
	vint_set_property(Hud_radial_menu.selector_h, "visible", true)

	--Reset to show the radial slots
	local slot_h
	for i = 0, 7 do
		vint_set_property(Hud_radial_menu.slots[i].grp_h, "visible", true)
	end
end

function hud_inventory_food_highlight_slot(slot_num)
	if slot_num == nil then
		vint_set_property(Hud_radial_menu.selector_h, "visible", false)
		hud_radial_menu_slot_scales_reset()
	else
		vint_set_property(Hud_radial_menu.selector_h, "visible", true)
		Hud_radial_menu_change_select(slot_num + 8, true)
	end
end


function hud_player_hood_change(data_item_handle, event_name)
	local hood_name, cur_hood_owner, orig_hood_owner, is_contested = vint_dataitem_get(data_item_handle)

	-- this will become relevant for pushbacks and display of notoriety since we always will show
	-- gang noto for mission/activity gang or hood owner if hood is contested
end

function hud_noto_change(data_item_h, event_name)
	local team_name, noto_level, noto_icon = vint_dataitem_get(data_item_h)

	local noto_data, display_data, icon_data, meter_data, team_data

	--	debug_print("vint", team_name.."/"..noto_level.."/"..noto_icon.."\n")

	-- find the interesting data for team
	for key, value in Hud_noto_data do
		if value.teams[team_name] ~= nil then
			noto_data = value
			display_data = value.teams[team_name]
			icon_data = value.icons
			meter_data = value.meter
			break
		end
	end

	if noto_data == nil then
		-- not an interesting team so outta here
		return
	end

	-- update the notoriety table
	display_data.noto_level = noto_level

	-- find the team in this group with highest notoriety
	noto_level = -1
	team_name = nil
	for key, value in noto_data.teams do
		if value.noto_level > noto_level then
			team_name = key
			noto_level = value.noto_level
			team_data = value
		end
	end

	-- better safe then sorry
	if team_name == nil then
		return
	end

	local base_new_noto = floor(noto_level)
	local base_old_noto = floor(noto_data.cur_level)
	local icon_h = 0

	-- new team, animate in all icons
	if team_name ~= noto_data.cur_team then
		for i = 1, 5 do
			icon_h = vint_object_find(noto_data.base_icon_name .. i)
			if base_new_noto >= i then
--				debug_print("vint", "team changed: new icon:" .. team_data.icon_image .. "\n")
				local icon

				if MP_enabled == true then
					icon = noto_icon
				else
					icon  = noto_data.teams[team_name].icon_image
				end

				vint_set_property(icon_h, "image", icon)
				hud_noto_show_icon(icon_h, noto_data.icons[i])
			else
				hud_noto_hide_icon(icon_h, noto_data.icons[i])
			end
		end

		noto_data.cur_team = team_name
		vint_set_property(meter_data.meter_fill_0_h, "tint", team_data.bar_0_color[1], team_data.bar_0_color[2], team_data.bar_0_color[3])
		vint_set_property(meter_data.meter_fill_1_h, "tint", team_data.bar_1_color[1], team_data.bar_1_color[2], team_data.bar_1_color[3])

		--debug_print("vint", "Changing to team " .. team_name .. "\n")

	-- noto on the rise, animate in all new icons
	elseif base_new_noto > base_old_noto then
		for i = 1, 5 do
			icon_h = vint_object_find(noto_data.base_icon_name .. i)
			if base_new_noto >= i and base_old_noto < i then
				vint_set_property_typed("string", icon_h, "image", team_data.icon_image)
				hud_noto_show_icon(icon_h, noto_data.icons[i])
			elseif base_new_noto < i then
				hud_noto_hide_icon(icon_h, noto_data.icons[i])
			end
		end

	-- noto falling, animate the highest active icon
	elseif base_new_noto < base_old_noto then
		for i = 1, 5 do
			icon_h = vint_object_find(noto_data.base_icon_name .. i)
			if base_new_noto == i then
				hud_noto_show_icon(icon_h, noto_data.icons[i])
			elseif base_new_noto < i then
				hud_noto_hide_icon(icon_h, noto_data.icons[i])
			end
		end
	end

	-- update meter
	local part_new_noto = noto_level - base_new_noto
	noto_data.cur_meter = part_new_noto

	if meter_data.cw == false then
		-- Lower Bar Update

		local start_angle = meter_data.end_angle + ((meter_data.start_angle - meter_data.end_angle) * part_new_noto)

		vint_set_property(meter_data.meter_fill_0_h, "start_angle", start_angle)
		vint_set_property(meter_data.meter_fill_1_h, "start_angle", start_angle)
		vint_set_property(meter_data.meter_bg_h, "start_angle", start_angle - 0.02)

	else
		-- Upper Bar Update
		local end_angle = meter_data.start_angle + ((meter_data.end_angle - meter_data.start_angle) * part_new_noto)
		vint_set_property(meter_data.meter_fill_0_h, "end_angle", end_angle)
		vint_set_property(meter_data.meter_fill_1_h, "end_angle", end_angle)
		vint_set_property(meter_data.meter_bg_h, "end_angle", end_angle + 0.02)

	end

	-- Now handled by hud_process [nclok1405]
	--[[
	if part_new_noto == 0 then
		-- If the meter is at 0 then we should hide it
		vint_set_property(meter_data.meter_fill_0_h, "visible", false)
		vint_set_property(meter_data.meter_fill_1_h, "visible", false)
		vint_set_property(meter_data.meter_bg_h, "visible", false)
	else
		--If the meter isn't at zero then make it visible
		vint_set_property(meter_data.meter_fill_0_h, "visible", true)
		vint_set_property(meter_data.meter_fill_1_h, "visible", true)
		vint_set_property(meter_data.meter_bg_h, "visible", true)
	end
	--]]

	noto_data.cur_level = noto_level
end

function hud_noto_hide_icon(icon_h, status)

	--	debug_print("vint", "noto_hide_icon: " .. icon_h .. "\n")

	vint_object_destroy(status.bmp_clone_0)
	vint_object_destroy(status.bmp_clone_1)
	vint_object_destroy(status.anim_0)
	vint_object_destroy(status.anim_1)
	vint_object_destroy(status.anim_2)
	vint_object_destroy(status.anim_3)

	--ANIMATE: Fade Icon Away
	local anim_3 = vint_object_find("noto_anim_3")
	local anim_clone_3 = vint_object_clone(anim_3)

	--Targets
	local anim_3_alpha_tween = vint_object_find("noto_alpha_3", anim_clone_3)
	vint_set_property(anim_3_alpha_tween, "target_handle",	icon_h)

	--Reset Tween value
	local alpha_val = vint_get_property(icon_h, "alpha")

	vint_set_property_typed("float", anim_3_alpha_tween, "start_value", alpha_val)

	--Callback
	vint_set_property(anim_3_alpha_tween, "end_event",		"hud_noto_icon_hide_end")

	lua_play_anim(anim_clone_3, 0);

	status.bmp_clone_0 = 0
	status.bmp_clone_1 = 0
	status.anim_0 = 0
	status.anim_1 = 0
	status.anim_2 = 0
	status.anim_3 = anim_clone_3
	status.tween_end = anim_3_alpha_tween
end

function hud_noto_icon_hide_end(tween_h, event_name)
	-- search for indicated tween and clean up
	for k, v in Hud_noto_data do
		for key, value in v.icons do
			if value.tween_alpha_out == tween_h then
				vint_object_destroy(value.bmp_clone_0)
				vint_object_destroy(value.bmp_clone_1)
				vint_object_destroy(value.anim_0)
				vint_object_destroy(value.anim_1)
				vint_object_destroy(value.anim_2)
				vint_object_destroy(value.anim_3)
				value.bmp_clone_0 = 0
				value.bmp_clone_1 = 0
				value.anim_0 = 0
				value.anim_1 = 0
				value.anim_2 = 0
				value.anim_3 = 0
				value.tween_show = 0
				return
			end
		end
	end
end

function hud_noto_show_icon(icon_h, status)

	--debug_print("vint", "hud_noto_show_icon: " .. icon_h .. "\n")

	vint_set_property(icon_h, "visible", true)

	--Destroy all objects if there are any currently being animated
	vint_object_destroy(status.bmp_clone_0)
	vint_object_destroy(status.bmp_clone_1)
	vint_object_destroy(status.anim_0)
	vint_object_destroy(status.anim_1)
	vint_object_destroy(status.anim_2)
	vint_object_destroy(status.anim_3)

	--Create bitmap clones for animation
	local bmp_clone_0 = vint_object_clone(icon_h)
	local bmp_clone_1 = vint_object_clone(icon_h)
	vint_set_property(bmp_clone_0, "depth",	-1)
	vint_set_property(bmp_clone_1, "depth",	-2)

	--Clone the notoriety anim and adjust the childs targets

	--ANIMATION: Large to small
	local anim_0 = vint_object_find("noto_anim_0")
	local anim_clone_0 = vint_object_clone(anim_0)

	--Target Tweens
	local anim_0_alpha_tween = vint_object_find("noto_alpha_0", anim_clone_0)
	local anim_0_scale_tween = vint_object_find("noto_scale_0", anim_clone_0)
	vint_set_property(anim_0_alpha_tween, "target_handle",	bmp_clone_0)
	vint_set_property(anim_0_scale_tween, "target_handle",	bmp_clone_0)

	--ANIMATION: Small To Large
	local anim_1 = vint_object_find("noto_anim_1");
	local anim_clone_1 = vint_object_clone(anim_1)

	--Target Tweens
	local anim_1_alpha_tween = vint_object_find("noto_alpha_1", anim_clone_1)
	local anim_1_scale_tween = vint_object_find("noto_scale_1", anim_clone_1)
	vint_set_property(anim_1_alpha_tween, "target_handle",	bmp_clone_1)
	vint_set_property(anim_1_scale_tween, "target_handle",	bmp_clone_1)

	--ANIMATION: BASIC FADE IN
	local anim_2 = vint_object_find("noto_anim_2")
	local anim_clone_2 = vint_object_clone(anim_2)

	--Target Tweens
	local anim_2_alpha_tween = vint_object_find("noto_alpha_2", anim_clone_2)
	vint_set_property(anim_2_alpha_tween, "target_handle",	icon_h)

	--Reset Properties to current value
	local alpha_val = vint_get_property(icon_h, "alpha")
	vint_set_property_typed("float", anim_2_alpha_tween, "start_value", alpha_val)

	--Setup callback
	vint_set_property(anim_0_scale_tween, "end_event",		"hud_noto_icon_show_end")

	--play anims
	lua_play_anim(anim_clone_0, 0);
	lua_play_anim(anim_clone_1, 0);
	lua_play_anim(anim_clone_2, 0);

	status.bmp_clone_0 = bmp_clone_0
	status.bmp_clone_1 = bmp_clone_1
	status.anim_0 = anim_clone_0
	status.anim_1 = anim_clone_1
	status.anim_2 = anim_clone_2
	status.anim_3 = 0
	status.tween_end = anim_0_scale_tween

end

function hud_noto_icon_show_end(tween_h, event_name)
	-- search for indicated tween and clean up
	for k, v in Hud_noto_data do
		for key, value in v.icons do
			if value.tween_end == tween_h then

				vint_object_destroy(value.bmp_clone_0)
				vint_object_destroy(value.bmp_clone_1)
				vint_object_destroy(value.anim_0)
				vint_object_destroy(value.anim_1)
				vint_object_destroy(value.anim_2)

				value.bmp_clone_0 = 0
				value.bmp_clone_1 = 0
				value.anim_0 = 0
				value.anim_1 = 0
				value.anim_2 = 0
				value.tween_show = 0

				return
			end
		end
	end
end

function hud_player_status_inf_change(di_h, event_name)

	local cash, max_followers, inventory_disabled, vehicle_logo, radio_station, cruise_control_active	= vint_dataitem_get(di_h)

	if inventory_disabled ~= Hud_player_status.inventory_disabled then
		if inventory_disabled == true and Hud_inventory.is_pressed == true then
			hud_inventory_hide()
		else
			if Hud_inventory.is_pressed == true then
				--button is pressed so open up the menu
				hud_inventory_show()
			end
		end
		Hud_player_status.inventory_disabled = inventory_disabled
	end

	--Update cash (this gets read through hud_process() so it counts up nicely)
	Hud_player_status.cash = floor(cash)
	Sui_cash = Hud_player_status.cash

	if vehicle_logo == nil then
		vehicle_logo = 0
	end

	if radio_station == nil then
		radio_station = 0
	end

	-- Display a new vehicle logo
	if Hud_current_veh_logo ~= vehicle_logo then
		if (Sui_hud_enable < 2) or (vehicle_logo == "__unloaded") or (vehicle_logo == 0) then
			local o = vint_object_find("vehicle_logo")
			vint_set_property(o, "visible", false)
		else
			local o = vint_object_find("vehicle_logo")
			vint_set_property(o, "image", vehicle_logo)
			lua_play_anim(vint_object_find("vehicle_logo_anim_1"), 0)
			vint_set_property(o, "visible", true)

			-- Make sure radio station displays again any time we get into a new car, even if it uses the same station you had
			Hud_current_radio_station = -1
		end
	end

	-- Display a new radio station
	if Hud_current_radio_station ~= radio_station then
		if (Sui_hud_enable == 2) and (radio_station ~= 0) then
			local radio_logo = hud_get_radio_station_logo(radio_station)

			local t
			if is_local_player_in_vehicle() then
				-- When in a vehicle, show Previous/Next Station Button [nclok1405]
				if radio_logo == "" then
					t = vint_insert_values_in_string("{PREV_RADIO_IMG} {0} {NEXT_RADIO_IMG}", {[0] = radio_station})
				else
					t = "{PREV_RADIO_IMG} [image: "..radio_logo.."] {NEXT_RADIO_IMG}"
				end
			else
				if radio_logo == "" then
					t = radio_station
				else
					t = "[image: "..radio_logo.."]"
				end
			end

			vint_set_property(vint_object_find("radio_station"), "text_tag", t)
			lua_play_anim(vint_object_find("radio_station_anim_1"))
		end
	end

	Hud_current_radio_station = radio_station
	Hud_current_veh_logo = vehicle_logo

	hud_cruise_control_update(cruise_control_active)
end

function hud_player_status_change(di_h, event_name)

	local sprint_enabled, health_pct, sprint_pct, is_sprinting, orientation	= vint_dataitem_get(di_h)

	--Health
	if health_pct ~= Hud_player_status.health_pct then

		local bar = Hud_player_status.health_bar
		local fill_end_angle = (bar.fill_end_angle - bar.fill_start_angle) * health_pct + bar.fill_start_angle
		local bg_end_angle = fill_end_angle + bar.angle_offset


		--if new health pct is less than current then do the animation of it dropping
		if health_pct < Hud_player_status.health_pct then

			--Decrease the health meter
			hud_player_health_decrease_anim(bar, fill_end_angle, bg_end_angle)

			if health_pct < .3 then
				--Full screen health effect gets even heavier if it drops below .3
				local vignette_alpha = .99 - health_pct
				hud_vignette_fade(vignette_alpha)

			elseif health_pct < .5 then
				--Full screen health effect if drops below .5
				local vignette_alpha = .75 - health_pct
				hud_vignette_fade(vignette_alpha)
			end
			Hud_player_status.health_recovering = false
		else
			--Increase the health meter
			hud_player_health_increase_anim(bar, fill_end_angle, bg_end_angle)

			if Hud_player_status.health_recovering == false then
				hud_vignette_fade(0)
				Hud_player_status.health_recovering = true
			end
		end

		--Hide bg of meter if health is empty.
		if health_pct <= 0 then
			vint_set_property(bar.bg_h, "visible", false)
		else
			vint_set_property(bar.bg_h, "visible", true)
		end

		Hud_player_status.health_pct = health_pct
	end

	--Sprint
	if sprint_enabled == true and sprint_pct ~= Hud_player_status.sprint_pct then
		local bar = Hud_player_status.sprint_bar
		local fill_end_angle = (bar.fill_end_angle - bar.fill_start_angle) * sprint_pct + bar.fill_start_angle
		local bg_end_angle = fill_end_angle + bar.angle_offset

		--Update angles for the sprint meter
		vint_set_property(bar.bg_h, "end_angle", bg_end_angle)

		--Hide bg of meter if sprint is empty.
		if sprint_pct <= 0 then
			vint_set_property(bar.bg_h, "visible", false)
		else
			vint_set_property(bar.bg_h, "visible", true)
		end

		vint_set_property(bar.fill_0_h, "end_angle", fill_end_angle)
		vint_set_property(bar.fill_1_h, "end_angle", fill_end_angle)
		Hud_player_status.sprint_pct = sprint_pct
	end

	if is_sprinting ~= Hud_player_status.is_sprinting then
		if is_sprinting == false then

			if Sprint_cool_down_thread ~= -1 then
				thread_kill(Sprint_cool_down_thread)
			end

			Sprint_cool_down_thread = thread_new("hud_player_sprint_cool_down")
		else

			--Lets kill the thread that resets everything
			if Sprint_cool_down_thread ~= -1 then
				thread_kill(Sprint_cool_down_thread)
			end

			--stop cooldown anim
			vint_set_property(vint_object_find("sprint_anim_1"), "is_paused", true)

			--If we aren't flashing then start flashing
			if Hud_player_status.sprint_bar.is_flashing == false then
				lua_play_anim(vint_object_find("sprint_anim_0"), 0)

				--Set flashing state to true
				Hud_player_status.sprint_bar.is_flashing = true
			end

		end

		Hud_player_status.is_sprinting = is_sprinting
	end

	-- not sure why we disable the sprint bar when we can just set it to zero but we live to serve
	if sprint_enabled ~= Hud_player_status.sprint_enabled then
		vint_set_property(Hud_player_status.sprint_bar.fill_0_h, "visible", sprint_enabled)
		vint_set_property(Hud_player_status.sprint_bar.fill_1_h, "visible", sprint_enabled)
		vint_set_property(Hud_player_status.sprint_bar.bg_h, "visible", sprint_enabled)
		Hud_player_status.sprint_enabled = sprint_enabled
	end

	if orientation ~= Hud_player_status.orientation then
		--Rotate Hit Indicators to player rotation
		orientation = 3.14 - orientation
		vint_set_property(Hud_hit_elements.main_h, "rotation", orientation)
		Hud_player_status.orientation = orientation
	end
end


function hud_player_sprint_cool_down()
	--Delay time to stop animation
	delay(.2)
	--If we haven't killed this thread by now we can

	--We stopped sprinting so lets stop the flashing
	local bar = Hud_player_status.sprint_bar

	--Pause Anim
	vint_set_property(vint_object_find("sprint_anim_0"), "is_paused", true)
	bar.is_flashing = false

	--play anim to cool down
	local color_0 = {[1] = -1, [2] = -1, [3] = -1}
	local color_1 = {[1] = -1, [2] = -1, [3] = -1}

	color_0[1], color_0[2], color_0[3] = vint_get_property(Hud_player_status.sprint_bar.fill_0_h, "tint")
	color_1[1], color_1[2], color_1[3] = vint_get_property(Hud_player_status.sprint_bar.fill_1_h, "tint")

	vint_set_property_typed("color", vint_object_find("sprint_flash_2_tween"), "start_value", color_0[1], color_0[2], color_0[3])
	vint_set_property_typed("color", vint_object_find("sprint_flash_3_tween"), "start_value", color_1[1], color_1[2], color_1[3])

	lua_play_anim(vint_object_find("sprint_anim_1"), 0)

	--Set flashing state to false
	Hud_player_status.sprint_bar.is_flashing = false

	--	Reset our  thread
	Sprint_cool_down_thread = -1
end


function hud_player_health_decrease_anim(bar, fill_end_angle, bg_end_angle)

	--Flash Health bar once
	local health_flash_anim = vint_object_find("health_anim_1")
	lua_play_anim(health_flash_anim, 0)

	--Setup Delay for animation
	if bar.anim ~= 0 then
		bar.anim_delay = bar.anim_delay -- * bar.anim_delay_decay
		if bar.anim_delay < 0 then

			bar.anim_delay = 0
		end
	else

		--Reset delay if we delayed the last animation finished
		bar.anim_delay = bar.anim_delay_start
	end

	--reset animation if its playing
	vint_object_destroy(bar.anim)

	--Pop beginning of second bar
	local angle_original = vint_get_property(bar.fill_0_h, "end_angle")


	--Reset Bars
	vint_set_property(bar.fill_0_h, "end_angle", fill_end_angle)
	vint_set_property(bar.fill_1_h, "end_angle", fill_end_angle)
	vint_set_property(bar.fill_decay_h, "start_angle", fill_end_angle)

	---Play Animation
	local anim = vint_object_find("health_anim_0")
	local anim_clone = vint_object_clone(anim)

	local fill_tween = vint_object_find("health_fill_tween", anim_clone)
	vint_set_property_typed("float", fill_tween, "start_value", angle_original)
	vint_set_property_typed("float", fill_tween, "end_value", fill_end_angle)

	local bg_tween = vint_object_find("health_bg_tween", anim_clone)
	vint_set_property_typed("float", bg_tween, "start_value", angle_original + bar.angle_offset)
	vint_set_property_typed("float", bg_tween, "end_value", bg_end_angle )

	--Callback
	vint_set_property(fill_tween, "end_event",	"hud_player_health_drop_anim_end")

	lua_play_anim(anim_clone, bar.anim_delay)

	--Reset delay if we are past our stop time
	if bar.anim_delay == 0 then
		bar.anim_delay = bar.anim_delay_start
	end

	--Store data for cleanup
	bar.anim = anim_clone
end

function hud_player_health_drop_anim_end(tween_h, event_name)

	--Destroy Animation
	local anim = Hud_player_status.health_bar.anim
	vint_object_destroy(anim)
	anim = 0

end

function hud_player_health_increase_anim(bar, fill_end_angle, bg_end_angle)

	--reset animation if its playing
	vint_object_destroy(bar.anim)

	--be sure to stop the flashing
	bar.is_flashing = false
	vint_set_property(bar.bg_h, "end_angle", bg_end_angle )
	vint_set_property(bar.fill_0_h, "end_angle", fill_end_angle)
	vint_set_property(bar.fill_1_h, "end_angle", fill_end_angle)

	vint_set_property(bar.fill_decay_h, "start_angle", fill_end_angle)

	vint_set_property(bar.fill_decay_h, "end_angle", fill_end_angle)

end


--#####################################################
--Weapon Changes
--#####################################################

function hud_player_weapon_change(di_h, event_name)
--[[
--	            di->set_element(0, wpn_bmp_name);                                 // weapon image name
--            di->set_element(1, ammo_ready);                                         // current ammo or < 0 if ammoless weapon
--            di->set_element(2, ammo_reserve);                                 // ammo capacity
--            di->set_element(3, wpn_ready);                                          // weapon ready
--            di->set_element(4, dual_wield);                                         // secondary weapon
--            di->set_element(5, ammoless_wpn);                                 // ammoless wpn
--            di->set_element(6, ammo_infinite);                                // infinite ammo
--            di->set_element(7, continuous_fire);                              // infinite ammo
--            di->set_element(8, no_magazine);                                  // continuous fire (like water gun or flame thrower)
--            di->set_element(9, pp->pflags.is_zoomed != 0);              // is the player vp zoomed (ala sniper rifle)
--            di->set_element(10, cur_wpn_name);                                // name of weapon
--           di->set_element(11, cur_wpn_category_name);                       // weapon category name
--            di->set_element(12, reticle_highlight);                           // enemy / friendly / none
--            di->set_element(13, cur_wpn_spread);                              // weapon spread

]]--
	local wpn_bmp_name, rdy_ammo, rsv_ammo, wpn_rdy, dual_wield, no_ammo, inf_ammo, cont_fire, no_mag, sniper_visible, wpn_name, wpn_category, reticule_highlight, wpn_spread, wpn_slot, y_screen_coord  = vint_dataitem_get(di_h)

	if wpn_bmp_name == nil then
		wpn_bmp_name = "ui_hud_inv_w_fist"
	end

	if dual_wield ~= Hud_weapon_status.dual_wield or wpn_bmp_name ~= Hud_weapon_status.wpn_icon_name then
		if dual_wield == true then
			vint_set_property(Hud_weapon_status.dual_wpn_icon_1_h, "image", wpn_bmp_name)
			vint_set_property(Hud_weapon_status.dual_wpn_icon_2_h, "image", wpn_bmp_name)
		else
			vint_set_property(Hud_weapon_status.single_wpn_icon_h, "image", wpn_bmp_name)
		end
		Hud_weapon_status.wpn_icon_name = wpn_bmp_name
	end

	if dual_wield ~= Hud_weapon_status.dual_wield then
		vint_set_property(Hud_weapon_status.dual_wpn_icon_1_h, "visible", dual_wield)
		vint_set_property(Hud_weapon_status.dual_wpn_icon_2_h, "visible", dual_wield)
		vint_set_property(Hud_weapon_status.single_wpn_icon_h, "visible", not dual_wield)
		Hud_weapon_status.dual_wield = dual_wield
	end

	--debug ammo
	--[[
	debug_print("vint", "\nAmmo Update\n")
	debug_print("vint", "wpn_bmp_name: " .. wpn_bmp_name .. "\n")
	debug_print("vint", "rdy_ammo: " .. rdy_ammo .. "\n")
	debug_print("vint", "rsv_ammo: " .. rsv_ammo .. "\n")
	debug_print("vint", "dual_wield: " .. var_to_string(dual_wield) .. "\n")
	debug_print("vint", "no_ammo: " .. var_to_string(no_ammo) .. "\n")
	debug_print("vint", "inf_ammo: " .. var_to_string(inf_ammo) .. "\n")
	debug_print("vint", "cont_fire: " .. var_to_string(cont_fire) .. "\n")
	debug_print("vint", "no_mag:" .. var_to_string(no_mag) .. "\n")
	debug_print("vint", "sniper_visible: " .. var_to_string(sniper_visible) .. "\n")
	]]

	--Update Ammo Count
	local ammo_string = ""

	-- If ammo count is 0 show it red [nclok1405]
	local rdy_ammo_str = tostring(rdy_ammo)
	if (rdy_ammo == 0) then
		rdy_ammo_str = "[format][color:red]0[/format]"
	end
	local rsv_ammo_str = tostring(rsv_ammo)
	if (rsv_ammo == 0) then
		rsv_ammo_str = "[format][color:red]0[/format]"
	end
	local rdy_ammo_floor_str = tostring(floor(rdy_ammo / 100))
	if (rdy_ammo == 0) then
		rdy_ammo_floor_str = "[format][color:red]0[/format]"
	end
	local rsv_ammo_floor_str = tostring(floor(rsv_ammo / 100))
	if (rsv_ammo == 0) then
		rsv_ammo_floor_str = "[format][color:red]0[/format]"
	end

	if no_ammo == false then
		if no_mag == true then
			if inf_ammo == false then
				local ammo_num_str = tostring(rdy_ammo + rsv_ammo)
				if (rdy_ammo + rsv_ammo == 0) then
					ammo_num_str = "[format][color:red]0[/format]"
				end
				ammo_string = ammo_num_str
			else
				ammo_string = "[image:ui_hud_infinity]"
			end
		else
			if inf_ammo == false then
				if cont_fire == false then
					ammo_string = rdy_ammo_str .. "/" .. rsv_ammo_str
				else
					--debug_print("vint", "this should fire for grenade")
					ammo_string = rdy_ammo_floor_str .. "/" .. rsv_ammo_floor_str
				end
			else
				if cont_fire == false then
					ammo_string = rdy_ammo_str .. "/[image:ui_hud_infinity]"
				else
					ammo_string = rdy_ammo_floor_str .. "/[image:ui_hud_infinity]"
				end
			end
		end
	end

	vint_set_property(Hud_weapon_status.ammo_text_h, "text_tag", ammo_string)

	if (Modern_hud_last_ammo_string ~= ammo_string) then
		Modern_hud_last_ammo_string = ammo_string
		Modern_hud_weapon_unhiding = true
	end

	--Dim Weapon if not ready
	if wpn_rdy ~= Hud_weapon_status.wpn_rdy then
		if wpn_rdy == true then
			--Show Weapon
			vint_set_property(Hud_weapon_status.ammo_text_h, "alpha", 1)
			vint_set_property(Hud_weapon_status.dual_wpn_icon_1_h, "alpha", 1)
			vint_set_property(Hud_weapon_status.dual_wpn_icon_2_h, "alpha", 1)
			vint_set_property(Hud_weapon_status.single_wpn_icon_h, "alpha", 1)

			if Hud_weapon_status.sniper_visible == false then
				--Show reticule
				vint_set_property(Hud_reticules.elements.reticule_h, "visible", true)
			end
		else
			--Dim Weapon
			vint_set_property(Hud_weapon_status.ammo_text_h, "alpha", .5)
			vint_set_property(Hud_weapon_status.dual_wpn_icon_1_h, "alpha", .5)
			vint_set_property(Hud_weapon_status.dual_wpn_icon_2_h, "alpha", .5)
			vint_set_property(Hud_weapon_status.single_wpn_icon_h, "alpha", .5)

			--Hide reticule
			vint_set_property(Hud_reticules.elements.reticule_h, "visible", false)
		end
	end

	--If sniper rifle is on then show the sniper rifle and not the standard reticule
	if sniper_visible ~= Hud_weapon_status.sniper_visible then
		if sniper_visible == true then
			vint_set_property(Hud_reticules.elements.sniper_h, "visible", true)
			vint_set_property(Hud_reticules.elements.reticule_h, "visible", false)
		else
			vint_set_property(Hud_reticules.elements.sniper_h, "visible", false)
			vint_set_property(Hud_reticules.elements.reticule_h, "visible", true)
		end

		Hud_weapon_status.sniper_visible = sniper_visible
	end

	--Change reticules if we have a different weapon
	if wpn_name ~= Hud_reticules.status.wpn_name or reticule_highlight ~= Hud_reticules.status.highlight  then
		Hud_reticule_update(wpn_name, wpn_category, reticule_highlight)
	end

	--Do Weapon Spread
	if wpn_spread ~= Hud_reticules.status.wpn_spread then
		hud_reticule_spread_update(wpn_spread, Hud_reticules.configs[Hud_reticules.status.config].spread)
	end

	--Weapon slot changes need to update the radial menu
	if wpn_slot ~= Hud_radial_menu.slot_selected then
		Hud_radial_menu_change_select(wpn_slot)
		Hud_radial_menu.slot_equipped = wpn_slot
	end

	--Change y screen coord of reticule
	hud_reticule_change_position(y_screen_coord)

	-- Play weapon switch sound [nclok1405]
	if (wpn_bmp_name ~= Modern_hud_last_weapon) then
		Modern_hud_last_weapon = wpn_bmp_name
		if Modern_hud_play_equip_sound then
			if Sui_weapon_switch_sound and (not Sui_weapon_store_active) and (not sui_is_demo_derby()) then
				audio_play(Hud_sounds.radial_equip_weapon)
			end
			Modern_hud_play_equip_sound = false
		else
			if Sui_weapon_switch_sound and (not Sui_weapon_store_active) and (not sui_is_demo_derby()) then
				audio_play(Hud_sounds.radial_select)
			end
		end
		Modern_hud_weapon_unhiding = true
	end

end


function hud_player_weapon_freq_change(di_h)
	local ammo_ready, reticle_highlight, cur_wpn_spread, fine_aim_transition, water_pressure = vint_dataitem_get(di_h)
	if fine_aim_transition ~= Hud_weapon_status.fine_aim_transition then
		hud_reticule_spread_update(cur_wpn_spread, Hud_reticules.configs[Hud_reticules.status.config].spread)
		if fine_aim_transition == nil then
			fine_aim_transition  = 0
		end
		Hud_weapon_status.fine_aim_transition = fine_aim_transition
	end

	--Update pressure
	hud_reticule_update_pressure(water_pressure)
end

function hud_player_respect_change(di_h)
	--[[
		current_respect	= current respect
		respect_needed		= respect points needed (for each/next mission?)
		respect_total		= total respect earned
	]]--

	local current_respect, respect_needed, respect_total = vint_dataitem_get(di_h)

	--Respect needed changed somehow, If this ever happens we need to update the visuals immediatly.
	if Hud_player_status.respect_needed ~= respect_needed then
		Hud_player_status.respect_needed = respect_needed
		--TODO: Connect this with the standard updates somehow
	end

	if current_respect ~= Hud_player_status.respect or Hud_player_status.respect_needed ~= respect_needed then

		--Calculate respect values for screen data
		if respect_needed > 0 then
			local respect_divide = current_respect / respect_needed
			Hud_player_status.respect_int = floor(respect_divide)
			Hud_player_status.respect_bar_percent = respect_divide - Hud_player_status.respect_int
		else
			Hud_player_status.respect_int = 99
			Hud_player_status.respect_bar_percent = 1
		end

		--Calculate target values for elemenet properties
		local bar = Hud_player_status.respect_bar
		local fill_start_angle = (bar.fill_start_angle - bar.fill_end_angle) * Hud_player_status.respect_bar_percent + bar.fill_end_angle
		local bg_start_angle = fill_start_angle - bar.angle_offset

		--Update angles for the respect meter
		vint_set_property(bar.bg_h, "start_angle", bg_start_angle)

		--Hide bg of meter if respect is empty.
		if Hud_player_status.respect_bar_percent == 0 then
			vint_set_property(bar.bg_h, "visible", false)
		else
			vint_set_property(bar.bg_h, "visible", true)
		end

		vint_set_property(bar.fill_0_h, "start_angle", fill_start_angle)
		vint_set_property(bar.fill_1_h, "start_angle", fill_start_angle)

		if fill_start_angle < 0.1 then
			--Right Side Lock
			vint_set_property(bar.txt_grp, "rotation", 3.14 + .3 )
			vint_set_property(bar.txt, "rotation", 3.14 - .3 )
		elseif fill_start_angle > 2.9 then
			--Left Side Lock
			vint_set_property(bar.txt_grp, "rotation", 3.14 + 3.1 )
			vint_set_property(bar.txt, "rotation", 3.14 - 3.1 )
		else
			--Normal Update
			vint_set_property(bar.txt_grp, "rotation", 3.14 + fill_start_angle + .2)
			vint_set_property(bar.txt, "rotation", 3.14 - fill_start_angle - .2)
		end

		--Update Respect Level Text
		if MP_enabled == false then
			if Hud_player_status.respect_int == 99 then
				vint_set_property(bar.txt, "text_tag", "[scale:1][image:ui_hud_base_smcirc_infinite]")
			elseif Hud_player_status.respect_int <= 0 then
				vint_set_property(bar.txt, "text_tag", "")
			else
				vint_set_property(bar.txt, "text_tag", "x" .. Hud_player_status.respect_int)
			end

			--Hide the level text if we don't have any filled bars.
			--if Hud_player_status.respect_int <= 0  then
			--	vint_set_property(bar.txt, "visible", false)
			--else
			--	vint_set_property(bar.txt, "visible", true)
			--end

		else
--			debug_print("vint", "my respect level:" .. current_respect .. "\n")
			vint_set_property(bar.txt, "text_tag", " " .. current_respect)
			vint_set_property(bar.txt, "visible", true)
		end

	end

end

function hud_player_followers_change(di_h)
	local slot, head_img_name, hlth_pct, revive_time, slot_visible = vint_dataitem_get(di_h)

	--No slots other than 1 to 3 allowed.
	if slot < 1 or slot > 3 then
		return
	end

	--Show or hide slot
	if slot_visible ~= Hud_followers.slot_objects[slot].visible then
		vint_set_property(Hud_followers.slot_objects[slot].group_h, "visible", slot_visible)
		Hud_followers.slot_objects[slot].visible = slot_visible
		Modern_hud_followers_unhiding = true
		--debug_print("Slot "..tostring(slot).." visible:"..tostring(slot_visible))
	end

	local data = Hud_followers.follower_data[slot]
	local objects = Hud_followers.slot_objects[slot]

	-- Replace default female homie head icon with Saints icon [nclok1405]
	if head_img_name == "ui_hud_recruit_wb_f_asian" then
		head_img_name = "ui_hud_recruit_coop"
	end

	if head_img_name ~= data.head_img_name then
		--debug_print("Slot "..tostring(slot).." head_img_name:"..tostring(head_img_name))

		if head_img_name == nil then
			--No homie head
			--hide the icon in the homie slot by playing the close animation
			vint_set_property(objects.anim_0, "is_paused", true)
			lua_play_anim(objects.anim_1, 0)

			--Be sure the timer is hidden too
			vint_set_property(objects.revive_timer_h, "visible", false)
		else
			if data.head_img_name == nil then
				vint_set_property(objects.anim_1, "is_paused", true)
				lua_play_anim(objects.anim_0, 0)
			end

			--Reset the head image
			vint_set_property(objects.head_img_h, "image", head_img_name)
		end
		data.head_img_name = head_img_name
		Modern_hud_followers_unhiding = true
	end

	--Update Health
	if hlth_pct ~= data.hlth_pct then
		local end_angle = 1.63 + (1.57 * hlth_pct)

		vint_set_property(objects.health_img_fill_h, "end_angle", end_angle )

		data.hlth_pct = hlth_pct
		Modern_hud_followers_unhiding = true
	end

	-- Show/Hide Health
	local should_display_health = true
	if (Sui_hud_enable < 2) or (head_img_name == nil) or ((Sui_hud_autohide) and (hlth_pct >= 1)) then
		should_display_health = false	-- Do not display health on full [nclok1405]
	end
	vint_set_property(objects.health_img_bg_h, "visible", should_display_health)
	vint_set_property(objects.health_img_fill_h, "visible", should_display_health)

	--Revives (This is the counter that shows up over the homie heads)
	revive_time = floor(revive_time)
	if revive_time ~= data.revive_time then
		if revive_time == 0 and data.revive_time ~= 0 then
			vint_set_property(objects.revive_timer_h, "visible", false)
			vint_set_property(vint_object_find("follow_rev_anim_0"),"is_paused", true)
		elseif revive_time ~= 0 and data.revive_time == 0 then
			vint_set_property(objects.revive_timer_h, "visible", true)
			vint_set_property(vint_object_find("follow_rev_anim_0"),"is_paused", false)
			vint_set_property(objects.health_img_fill_h, "end_angle", 1.57 )
		end

		--Update Revive Time
		local revive_time_str = tostring(revive_time)
		if (revive_time <= 0) then
			revive_time_str = ""
		elseif (revive_time <= 10) then
			revive_time_str = "[format][color:red]"..tostring(revive_time).."[/format]"
		end
		vint_set_property(objects.revive_timer_h, "text_tag", revive_time_str)
		data.revive_time = revive_time

		Modern_hud_followers_unhiding = true
	end
end

function hud_balance_meter_change(di_h)

	--	active		bool		is the meter active?
	--	position		float		-1 to 1 indicating the position on the meter
	local active, position = vint_dataitem_get(di_h)
	local force_update = false
--	debug_print("vint", "active: " .. var_to_string(active) .. "| position: " .. position .. "\n")

	--Update visibility
	if Hud_balance_status.active ~= active then
		if (Hud_balance_status.active == false) and (active == true) then
			-- Surfing Started
			Modern_hud_vehicle_surfing_time = 0
		elseif (Hud_balance_status.active == true) and (active == false) then
			-- Surfing Ended
			local seconds = floor(Modern_hud_vehicle_surfing_time)
			local sub = Modern_hud_vehicle_surfing_time - seconds
			local sub2 = floor(sub * 10)
			local str = seconds .. "." .. sub2
			local score_str = vint_insert_values_in_string("{0}{1}", {[0] = "ACT_ZOMBIE_HUD_SCORE", [1] = sui_get_human_readable_time_float(Modern_hud_vehicle_surfing_time)})
			hud_collection_msg_new("STAT_SURFING", score_str, 0, -1)
			vint_set_property(Hud_enemy_status.count_txt_h, "text_tag", "")
		end

		if active == true then
			vint_set_property(Hud_balance_status.balance_grp_h, "visible", true)
		else
			vint_set_property(Hud_balance_status.balance_grp_h, "visible", false)
		end
		force_update = true
		Hud_balance_status.active = active
	end

	--Update Position and Color
	if Hud_balance_status.position ~= position or force_update == true then

		--Calculate Angle
		local angle = position * Hud_balance_status.max_angle

		--Calculate Color
		local color_r, color_g, color_b
		local p_val = 0
		if position < 0 then
			p_val = position * -1
		else
			p_val = position
		end

		color_r = Hud_balance_status.color_base[1] - p_val * (Hud_balance_status.color_base[1] - Hud_balance_status.color_alarm[1])
		color_g = Hud_balance_status.color_base[2] - p_val * (Hud_balance_status.color_base[2] - Hud_balance_status.color_alarm[2])
		color_b = Hud_balance_status.color_base[3] - p_val * (Hud_balance_status.color_base[3] - Hud_balance_status.color_alarm[3])

		--Set Props
		vint_set_property(Hud_balance_status.arrow_image_h, "rotation", angle)
		vint_set_property(Hud_balance_status.base_grp_h, "tint", color_r, color_g, color_b)

		Hud_balance_status.position = position
	end
end

--Health Vignette
function hud_vignette_fade(target_alpha)
	local current_alpha = vint_get_property(Hud_vignettes.health.grp_h, "alpha")
	vint_set_property(Hud_vignettes.health.fade_twn_h, "start_value", current_alpha)
	vint_set_property(Hud_vignettes.health.fade_twn_h, "end_value", target_alpha)
	lua_play_anim(Hud_vignettes.health.fade_anim_h, 0)
end


--========================================================
--HUD Hits
--Things around the reticule
--========================================================
function Hud_hit_add(di_h)
	local hit_index = di_h
	local direction, strength = vint_dataitem_get(di_h)
	local hit_bmp_h, hit_anim_h, hit_twn_h, fade_time, stick_time

	--Check if major/minor hit
	if strength > .3 then
		hit_bmp_h = vint_object_clone(Hud_hit_elements.major_h)
		stick_time = .5
		fade_time = .5
	else
		hit_bmp_h = vint_object_clone(Hud_hit_elements.minor_h)
		stick_time = .25
		fade_time = .25
	end

	vint_set_property(hit_bmp_h, "visible", true)
	vint_set_property(hit_bmp_h, "rotation", direction)

	--Tween Fade out, Set Callback
	hit_anim_h = vint_object_clone(Hud_hit_elements.anim_h)
	hit_twn_h =  vint_object_find("hit_twn", hit_anim_h)
	vint_set_property(hit_twn_h, "target_handle", hit_bmp_h)
	vint_set_property(hit_twn_h, "duration", fade_time)
	vint_set_property(hit_twn_h, "end_event", "hud_hit_fade_end")

	lua_play_anim(hit_anim_h, stick_time)

	--Store Reticule Information for further processing
	Reticule_hits[hit_index] = {
		hit_bmp_h = hit_bmp_h,
		hit_twn_h = hit_twn_h,
		hit_anim_h = hit_anim_h,
		direction = direction,
		strength = strength,
	}
end

function hud_hit_fade_end(twn_h, event_name)
	--Clean up reticule hits
	for index, value in Reticule_hits do
		if value.hit_twn_h == twn_h then
			vint_object_destroy(value.hit_anim_h)
			vint_object_destroy(value.hit_twn_h)
			vint_object_destroy(value.hit_bmp_h)
			Reticule_hits[index] = nil
		end
	end
end

function hud_hits_updates_pos(y_screen_coord)
	--y screen coordinate
	local x, y = vint_get_property(Hud_hit_elements.main_h, "anchor")
	vint_set_property(Hud_hit_elements.main_h, "anchor", x, y_screen_coord)
end

--Clears all indicators if called, designed to be called via C++
function hud_hit_clear_all()
	for index, value in Reticule_hits do
		vint_object_destroy(value.hit_anim_h)
		vint_object_destroy(value.hit_twn_h)
		vint_object_destroy(value.hit_bmp_h)
	end
	Reticule_hits = {}
end

--#####################################################################
--Radial Menu
--#####################################################################
function hud_radial_menu_update(di_h)
	--[[
		slot_num:		Slot number of item
		availability:	Is the item available and can it be equipped?
		item_name_crc:	crc for the item name (if nil then the item is empty
		bmp_name:		bitmap representing the item
		ammo_cur:		current ammo for the item (Weapons Only)
		ammo_max:		max ammo for the item (Weapons Only)
		dual_wield:		bool (Weapons Only)
		ammo_infinite:	bool (Weapons Only)
	]]
	local slot_num, availability, item_name_crc, bmp_name, ammo_cur, ammo_max, dual_wield, ammo_infinite, is_current_wpn  = vint_dataitem_get(di_h)
	local slot = Hud_radial_menu.slots[slot_num]
	if slot_num < 8 and slot_num > -1 then
		--Weapon Slot
		--New weapon

		-- Update equipped weapon bitmap [nclok1405]
		if not Sui_weapon_store_active then
			--debug_print("slot:"..tostring(slot_num)..", bmp_name:"..tostring(bmp_name)..", dual_wield:"..tostring(dual_wield).."\n")
			Sui_weapon_bmp[slot_num] = bmp_name
			Sui_weapon_dual[slot_num] = dual_wield
			Sui_weapon_infinite[slot_num] = ammo_infinite
		end

		if item_name_crc ~= slot.item_name_crc or dual_wield ~= slot.dual_wield then
			--if bitmap is null slot is empty
			local item_element_h = -1
			--Clear out old slot icon
			if slot.item_element_h ~= -1 then
				vint_object_destroy(slot.item_element_h)
			end

			--If slot Zero bitmap name is nil then use the fist
			if slot_num == 0 and bmp_name == nil then
				bmp_name = "ui_hud_inv_w_fist"
			end

			if bmp_name == nil then
				--Hide the other elements
				vint_set_property(slot.infinite_h, "visible", false)
				vint_set_property(slot.ammo_bar_fill_h, "visible", false)
				vint_set_property(slot.ammo_bar_bg_h , "visible", false)
			else
				--Check if Dual wielding for formating differences
				if dual_wield == true then
					item_element_h = vint_object_clone(vint_object_find("inv_dual_wield_tmp", Hud_radial_menu.radial_grp_h), slot.grp_h)
					local item1_h = vint_object_find("inv_icon_0", item_element_h)
					local item2_h = vint_object_find("inv_icon_1", item_element_h)
					vint_set_property(item1_h,"image", bmp_name)
					vint_set_property(item2_h,"image", bmp_name)
				else
					local inv_h = vint_object_find("inv_icon_tmp")
					item_element_h = vint_object_clone(inv_h, slot.grp_h)
					vint_set_property(item_element_h,"image", bmp_name)
				end
				--Reposition/scale weapon icon
				vint_set_property(item_element_h, "visible", true)
				vint_set_property(item_element_h, "anchor", 0,0)
				vint_set_property(item_element_h, "scale", .75,.75)
			end

			if bmp_name == "ui_hud_inv_w_ar50grenade" or bmp_name == "ui_hud_inv_w_minigun" or bmp_name == "ui_hud_inv_w_flamethrower" then
				vint_set_property(item_element_h, "depth", -250)
			end

			slot.bmp_name = bmp_name
			slot.item_element_h = item_element_h
			slot.item_name_crc = item_name_crc
		end



		--[[
		debug_print("vint", "------------------------------------\n")
		debug_print("vint", "Hud_radial_menu.slot_selected: " .. var_to_string(Hud_radial_menu.slot_selected) .. "\n")
		debug_print("vint", "slot_num: " .. var_to_string(slot_num) .. "\n")
		debug_print("vint", "availability: " .. var_to_string(availability) .. "\n")


		debug_print("vint", "Hud_radial_menu.slot_selected: " .. var_to_string(Hud_radial_menu.slot_selected) .. "\n")
		debug_print("vint", "slot_num: " .. var_to_string(slot_num) .. "\n")
		debug_print("vint", "availability: " .. var_to_string(availability) .. "\n")
		debug_print("vint", "------------------------------------\n\n")
		]]

		--Weapon Availability
	--	if availability ~= slot.availability then
		local ran_out_of_ammo = false
		if (ammo_cur == 0) and (ammo_max > 0) and (not ammo_infinite) then
			ran_out_of_ammo = true
		end
		if slot.item_element_h ~= -1 then
			if (availability == true) and (not ran_out_of_ammo) then
				vint_set_property(slot.item_element_h, "tint", 1, 1, 1)
			elseif (availability == true) and (ran_out_of_ammo) then
				-- If this weapon is out of ammo, make it appear red [nclok1405]
				vint_set_property(slot.item_element_h, "tint", 1, 0, 0)
			else
				vint_set_property(slot.item_element_h, "tint", .25, .25, .25)
			end
		end
		slot.availability = availability
--		end

		if is_current_wpn == true then
			Hud_radial_menu.slot_equipped = slot_num
		end

		if Hud_radial_menu.slot_selected == slot_num and availability == true then
			hud_radial_menu_text_update(slot_num)
		end


		--Weapon Ammo
		if ammo_cur ~= slot.ammo_cur or ammo_max ~= slot.ammo_max or ammo_infinite ~= slot.ammo_infinite then
			if ammo_max == 0 then
				--No ammo clip, don't render ammo bar or infinity symbol
				vint_set_property(slot.infinite_h, "visible", false)
				vint_set_property(slot.ammo_bar_fill_h, "visible", false)
				vint_set_property(slot.ammo_bar_bg_h , "visible", false)
			else
				--Ammo Bar Fill
				local ammo_percent = ammo_cur/ammo_max
				local angle = Hud_radial_menu.ammo_angle_empty + (Hud_radial_menu.ammo_angle_full - Hud_radial_menu.ammo_angle_empty) * ammo_percent
				vint_set_property(slot.ammo_bar_fill_h, "start_angle", angle)

				--debug_print("vint", "slot: " .. slot_num .. " | bmp_name: " .. var_to_string(bmp_name) .. " | ammo_cur: " .. ammo_cur .. " | ammo_max: " .. ammo_max .. " | percent: " .. ammo_percent .. "\n")

				--Infinity Symbol or Ammo bar?
				if ammo_infinite == true then
					vint_set_property(slot.infinite_h, "visible", true)
					vint_set_property(slot.ammo_bar_fill_h, "visible", false)
					vint_set_property(slot.ammo_bar_bg_h , "visible", false)
				else
					vint_set_property(slot.infinite_h, "visible", false)
					vint_set_property(slot.ammo_bar_fill_h, "visible", true)
					vint_set_property(slot.ammo_bar_bg_h , "visible", true)
				end
			end
			slot.ammo_cur = ammo_cur
			slot.ammo_max = ammo_max
			slot.ammo_infinite = ammo_infinite
		end

	elseif slot_num > 7 then
		--Food Slot
		local item_element_h = slot.item_element_h
		if item_name_crc ~= slot.item_name_crc then
			if bmp_name == nil then
				vint_set_property(item_element_h, "visible", false)
			else
				vint_set_property(item_element_h, "visible", true)
				vint_set_property(item_element_h, "image", bmp_name)
			end
			slot.bmp_name = bmp_name
			slot.item_name_crc = item_name_crc
		end
		--Is the food item available?
		if availability ~= slot.availability then
			if availability == true then
				vint_set_property(slot.item_element_h, "tint", 1, 1, 1)
			else
				vint_set_property(slot.item_element_h, "tint", .25, .25, .25)
			end
			slot.availability = availability
		end
	end
end

function Hud_radial_menu_change_select(slot_num, is_liquor_store)
	local selector_h = Hud_radial_menu.selector_h

	if slot_num > 7 and is_liquor_store ~= true then
		if Hud_radial_menu.slots[slot_num].item_name_crc == 0 then
			--Food slot is empty so exit early and do not highlight anything.
			return
		elseif Hud_radial_menu.slots[slot_num].availability == false then
			--Food slot is unavailable so do not highlight it.
			return
		end
	end

	local selector_x, selector_y = vint_get_property(Hud_radial_menu.slots[slot_num].grp_h,"anchor")
	vint_set_property(selector_h, "anchor", selector_x, selector_y)

	hud_radial_menu_slot_scales_reset()

	--Then make groups bigger based on his current selection
	if slot_num ~= nil then
		if slot_num < 8 then
			vint_set_property(Hud_radial_menu.slots[slot_num].grp_h, "scale", 1.2, 1.2)
			vint_set_property(selector_h, "scale", 1.2, 1.2)
		else
			vint_set_property(Hud_radial_menu.slots[slot_num].grp_h, "scale", 1, 1)
			vint_set_property(selector_h, "scale", .9, .9)
		end
	end

	if is_liquor_store == true then
		return
	end

	--Move/Rotate dpad highlight if food
	if slot_num > 7 then
		if slot_num == 8 then
			--Up
			vint_set_property(Hud_radial_menu.dpad_highlight_h, "anchor", -64, -67)
			vint_set_property(Hud_radial_menu.dpad_highlight_h, "rotation", 0)
		elseif slot_num == 9 then
			--Right
			vint_set_property(Hud_radial_menu.dpad_highlight_h, "anchor", -59, -61)
			vint_set_property(Hud_radial_menu.dpad_highlight_h, "rotation", 1.571)
		elseif slot_num == 10 then
			--Down
			vint_set_property(Hud_radial_menu.dpad_highlight_h, "anchor", -65, -54)
			vint_set_property(Hud_radial_menu.dpad_highlight_h, "rotation", 3.142)
		elseif slot_num == 11 then
			--Left
			vint_set_property(Hud_radial_menu.dpad_highlight_h, "anchor", -69, -61)
			vint_set_property(Hud_radial_menu.dpad_highlight_h, "rotation", 4.712)
		end
		lua_play_anim(Hud_radial_menu.dpad_highlight_anim_h, 0)
	end

	hud_radial_menu_text_update(slot_num)

	if slot_num ~= Hud_radial_menu.slot_selected then
		local radial_is_visible = vint_get_property(Hud_radial_menu.radial_grp_h, "visible")

		if radial_is_visible then
			audio_play(Hud_sounds.radial_select)
		end

		Hud_radial_menu.slot_selected = slot_num
	end
end


function hud_radial_menu_text_update(slot_num)
	--Update text on radial menu
	local item_name_crc = Hud_radial_menu.slots[slot_num].item_name_crc
	local item_availability = Hud_radial_menu.slots[slot_num].availability

	--Set property of center bg
	if item_name_crc == 0 then
		vint_set_property(Hud_radial_menu.slot_desc_h, "visible", false)
	else
		vint_set_property(Hud_radial_menu.slot_desc_h, "text_tag_crc", item_name_crc)
		vint_set_property(Hud_radial_menu.slot_desc_h, "visible", true)

		if item_availability == false then
			vint_set_property(Hud_radial_menu.slot_desc_h, "alpha", .5)
			vint_set_property(Hud_radial_menu.slot_desc_h, "tint", .1,.1,.1)
			vint_set_property(Hud_radial_menu.slot_desc_h, "font", "thin")
		else
			vint_set_property(Hud_radial_menu.slot_desc_h, "alpha", 1)
			vint_set_property(Hud_radial_menu.slot_desc_h, "tint", 1,1,1)
			vint_set_property(Hud_radial_menu.slot_desc_h, "font", "thin_overlay")
		end
	end
end

function hud_radial_menu_slot_scales_reset()
	--Resets all the scales for all slots
	for i = 0, 7 do
		vint_set_property(Hud_radial_menu.slots[i].grp_h, "scale", 1, 1)
	end
	for i = 8, 11 do
		vint_set_property(Hud_radial_menu.slots[i].grp_h, "scale", .8, .8)
	end
end

--#####################################################################
--Showing/Hiding the hud
--#####################################################################

Hud_element_groups = {
	["HEALTH"] = {
		[0] = "health_grp"
	},
	["MAP"] = {
		[0] = "map_grp"
	},
	["CASH"] = {
		[0] = "cash"
	},
	["FOLLOWERS"] = {
		[0] = "followers"
	},
	["GSI"] = {
		[0] = "gsi_base_grp"
	},
	["RETICULE"] = {
		[0] = "hits",
		[1] = "reticules",
		[2] = "sniper",
	},
	["RADIAL"] = {
		[0] = "radial_grp"
	},
	["MISC"] = {
		[0] = "balance_meter",
		[1] = "mayhem_grp",
		[2] = "combo_grp",
		[3] = "vignettes"
	},
	["DEMODERBY"] = {
		[0] = "coop_grp",
		[1] = "health_grp",
	},
	["MESSAGES"] = {
		[0] = "msg_debug_anchor",
		[1] = "msg_diversion_anchor",
		[2] = "msg_help_anchor",
		[3] = "msg_multi_action_anchor",
		[4] = "msg_multi_chat_anchor",
		[5] = "msg_multi_subtitle_anchor",
	},
	["MP_HUD"] = {
		[0] = "perk_grp",
		[1] = "tagging_progress_grp",
		[2] = "voip_grp"
	}
}

Hud_elements = {
	[0] = "HEALTH",
	[1] = "MISC",
	[2] = "MAP",
	[3] = "CASH",
	[4] = "FOLLOWERS",
	[5] = "GSI",
	[6] = "RETICULE",
	[7] = "RADIAL",
	[8] = "DEMODERBY",
	[9] = "MESSAGES",
	[10] = "MP_HUD",

}

Hud_element_tweens = {}

--Fades a particular element
function hud_element_fade(element_id, fade, duration)
	-- Do not let the game show or hide health bar, cash, or homies; we do it in hud_process now [nclok1405]
	if (element_id == 0) or (element_id == "HEALTH") or (element_id == 3) or (element_id == "CASH") or (element_id == 4) or (element_id == "FOLLOWERS") then
		return
	end

	if duration == nil then
		duration = -1
	end
	--fade: 0 = hidden,	1 = transparent, 2 = visible
	local element_group
	local target_document_name = -1
	local element_id_type = type(element_id)
	local grp_name
	if element_id_type == "number" then
		grp_name = Hud_elements[element_id]
		element_group = Hud_element_groups[Hud_elements[element_id]]

		if element_id == 8 then
			--Hack for demo derby
			target_document_name = "hud_demo_derby"
		elseif element_id == 9 then
			--Hack for hud messages
			target_document_name = "hud_msg"
		elseif element_id == 10 then
			--Hack for MP HUD
			target_document_name = "mp_hud"
		end

	elseif element_id_type == "string" then
		grp_name = element_id
      element_group = Hud_element_groups[element_id]

		if element_id == "DEMODERBY" then
			--Hack for demo derby
			target_document_name = "hud_demo_derby"
		elseif element_id == "MESSAGES" then
			--Hack for hud messages
			target_document_name = "hud_msg"
		elseif element_id == "MP_HUD" then
			--Hack for MP HUD
			target_document_name = "mp_hud"
		end
	end

	--Set alpha based on fade
	local target_alpha
	if fade == 0 then
		target_alpha = 0
	elseif fade == 1 then
		target_alpha = .35
	else
		target_alpha = 1
	end

	local grp_h, current_alpha, twn_h

	--Figure out which document the elements exist in
	local target_doc_h = HUD_DOC_HANDLE
	if target_document_name ~= -1 then
		target_doc_h = vint_document_find(target_document_name)
		if target_doc_h == 0 then
			--This document is not loaded for whatever reason exit
			return
		end
	end

	if duration == -1 then
		duration = .25
	end

	local mp_enabled = mp_is_enabled()

	--Loop through the group and create tweens
	for idx, val in element_group do
		if mp_enabled == true and (val == "msg_diversion_anchor" or val == "msg_help_anchor") then
			--In MP Mode always show the Death kills and help text.
		else
			--get the group object to fade
			grp_h = vint_object_find(val, nil, target_doc_h)

			--Verify that we aren't already fading something
			for idx, val in Hud_element_tweens do
				if grp_h == val.grp_h then
					--tween exist so delete the tween
					vint_object_destroy(idx)
					Hud_element_tweens[idx] = nil
				end
			end

			--Get Current Alpha of object
			current_alpha = vint_get_property(grp_h, "alpha")

			local hud_root_animation =  vint_object_find("root_animation", nil, target_doc_h)

			--Create Tween and set values
			twn_h = vint_object_create("hud_fade_tweens", "tween", hud_root_animation, target_doc_h)

			vint_set_property(twn_h, "duration", duration)	--Fade time
			vint_set_property(twn_h, "target_handle", grp_h)
			vint_set_property(twn_h, "target_property", "alpha")
			vint_set_property(twn_h, "start_value", current_alpha)
			vint_set_property(twn_h, "end_value", target_alpha)
			vint_set_property(twn_h, "start_time",	vint_get_time_index(target_doc_h))
			vint_set_property(twn_h, "is_paused", false)

			--Set callback
			vint_set_property(twn_h, "end_event", "hud_element_fade_end")

			--Store for cleanup
			Hud_element_tweens[twn_h] = {
				grp_h = grp_h
			}
		end
	end
end

--Fades all HUD Elements
function hud_element_fade_all(fade, duration)
	if duration == nil then
		duration = -1
	end
	for idx, val in Hud_elements do
		hud_element_fade(val, fade, duration)
	end
end

function hud_element_fade_end(tween_h, event_name)
	--Delete all fade tweens and references
	vint_object_destroy(tween_h)
	Hud_element_tweens[tween_h] = nil
end

function hud_fade_out(duration)
	if duration == nil then
		duration = -1
	end
	hud_element_fade_all(0, duration)
end

function hud_fade_in(duration)
	if duration == nil then
		duration = -1
	end
	hud_element_fade_all(2, duration)
end

function hud_fade_half(duration)
	if duration == nil then
		duration = -1
	end
	hud_element_fade_all(1, duration)
end

---------[ BUSTED/SMOKED ]---------

function hud_busted_init()
	Hud_smoked_busted.handles = {}

	Hud_smoked_busted.handles.grp = vint_object_find("smoked_busted")
	vint_set_property(Hud_smoked_busted.handles.grp, "visible", false)

	--Fade In animations
	Hud_smoked_busted.handles.fade_in_anim = vint_object_find("sb_fade_in")
	vint_set_property(Hud_smoked_busted.handles.fade_in_anim , "is_paused", true)
end

function hud_busted_complete()
end

function hud_busted_fade_in(smoked, delay, fade_time)
	local msg, effect, color

	Sui_player_dead = true	-- Player dead on [nclok1405]

	-- Set death message [nclok1405]
	if smoked == true then
		local rnd = rand_int(1, 6)
		if rnd == 1 then
			msg = "GAMEPLAY_SMOKED"
		elseif rnd == 2 then
			msg = "WASTED!"
		elseif rnd == 3 then
			msg = "YOU'RE\nBROWN\nBREAD!"
		elseif rnd == 4 then
			msg = "DIVERSION_SURVIVAL_DEATH_TEXT"
		elseif rnd == 5 then
			msg = "GAMEPLAY_PASSED_OUT"
		else
			msg = "You Died"
		end
		effect = "smoked"
		color = {r = .9, g = .9, b = .9}
	else
		local rnd = rand_int(1, 4)
		if rnd == 1 then
			msg = "GAMEPLAY_BUSTED"
		elseif rnd == 2 then
			msg = "YOU'RE\nNICKED!"
		elseif rnd == 3 then
			msg = "ARRESTED"
		else
			msg = "MSN_FAIL"
		end

		effect = "busted"
		color = {r = .9, g = .9, b = .9}
	end
	-- Do not show death message if HUD is disabled [nclok1405]
	if Sui_hud_enable < 2 then
		msg = ""
	end

	--Show Smoked busted text
	vint_set_property(Hud_smoked_busted.handles.grp, "visible", true)
	vint_set_property(Hud_smoked_busted.handles.grp, "alpha", 0)
	vint_set_property(Hud_smoked_busted.handles.grp, "tint", color.r, color.g, color.b)

	-- Hide activity stuff
	local h = vint_object_find("collection_anim")
	h = vint_object_find("collection_msg_alpha_twn_2", h)
	vint_set_property(h, "start_value", 0)
	vint_set_property(vint_object_find("collection_msg"), "alpha", 0)

	--Fade out HUD
	hud_fade_out()

	--Busted/Smoked text fade in
	vint_set_property(vint_object_find("sb_text"), "text_tag", msg)
	lua_play_anim(Hud_smoked_busted.handles.fade_in_anim)

	--Start Interface effect
	interface_effect_begin(effect, 1, .5)
end

function hud_effect_smoked()
	interface_effect_begin("smoked", 1, 1)
end

function hud_effect_busted()
	interface_effect_begin("busted", 1, 1)
end

function hud_effect_pause()
	interface_effect_begin("pause", 1, 1)
end

function hud_effect_end()
	interface_effect_end()
end

function hud_player_reset_complete()
	--Reset the busted state
	interface_effect_end(0, false)
	--Hide Smoked busted text
	vint_set_property(Hud_smoked_busted.handles.grp, "visible", false)
	hud_fade_in()

	-- Reset health bar's visibility [nclok1405]
	Modern_hud_health_visibility = 100

	vint_set_property(Hud_player_status.health_bar.bg_h, "alpha", 1)
	vint_set_property(Hud_player_status.health_bar.fill_0_h, "alpha", 1)
	vint_set_property(Hud_player_status.health_bar.fill_1_h, "alpha", 1)
	vint_set_property(Hud_player_status.health_bar.fill_decay_h, "alpha", 1)

	vint_set_property(Hud_player_status.health_bar.bg_h, "visible", true)
	vint_set_property(Hud_player_status.health_bar.fill_0_h, "visible", true)
	vint_set_property(Hud_player_status.health_bar.fill_1_h, "visible", true)
	vint_set_property(Hud_player_status.health_bar.fill_decay_h, "visible", true)

	Sui_player_dead = false	-- Player dead off [nclok1405]
end

---------[ COLLECTION MESSAGES ]---------

Hud_collection_msgs = { num_msgs = 0 }

-- you can also call this to clear any existing messages
function hud_collection_msg_init()
	Hud_collection_msgs = { num_msgs = 0 }
	vint_set_property(vint_object_find("collection_msg"), "alpha", 0)
	vint_set_property(vint_object_find("collection_msg"), "visible", true)
	vint_set_property(vint_object_find("collection_anim"), "is_paused", true)
	vint_set_property(vint_object_find("collection_msg_alpha_twn_2"), "end_event", "hud_collection_msg_end")

	Hud_collection_msgs.ornate_right_h = vint_object_find("col_ornate_right")
	Hud_collection_msgs.ornate_left_h = vint_object_find("col_ornate_left")
	Hud_collection_msgs.ornate_x, Hud_collection_msgs.ornate_y = vint_get_property(Hud_collection_msgs.ornate_right_h, "anchor")
end

function hud_collection_msg_show(m)

	local header_text_h = vint_object_find("collection_header_text")
	local body_text_h = vint_object_find("collection_body_text")

	vint_set_property(header_text_h , "text_tag", m.header)


	local y_ornate_offset = 0
	if m.body ~= nil then
		vint_set_property(body_text_h, "text_tag", m.body)
		vint_set_property(body_text_h, "visible", true)
	else
		vint_set_property(body_text_h, "visible", false)
		--No body text so adjust the ornate
		y_ornate_offset = -10
	end

	--Tint body if Win(For MP)
	if m.win_status == -1 then
		--Normal
		vint_set_property(body_text_h, "tint", 0.8980, 0.8941, 0.874)
	elseif m.win_status == 0 then
		--Win
		vint_set_property(body_text_h, "tint", 0.2667, 0.5059, 0.844)
	elseif m.win_status == 1 then
		--Lose
		vint_set_property(body_text_h, "tint", 0.6863, 0.0000, 0.004)
	elseif m.win_status == 2 then
		--Tie
		vint_set_property(body_text_h, "tint", 0.623, 0.635, 0.644)
	end

	--Adjust ornate trim
	local width, height = element_get_actual_size(header_text_h)
	local y = Hud_collection_msgs.ornate_y + y_ornate_offset

	--Offset header animation and body if line wraps
	local collection_msg_anchor_twn_h = vint_object_find("collection_msg_anchor_twn_1")
	if height > 50 then
		--Header has \n in it so we need format for wrapping
		vint_set_property(collection_msg_anchor_twn_h, "start_value", 0, -35)
		vint_set_property(collection_msg_anchor_twn_h, "end_value", 0, -15)
		vint_set_property(body_text_h, "anchor", 0, 33)
	else
		--Header does not wrap
		vint_set_property(collection_msg_anchor_twn_h, "start_value", 0, -12)
		vint_set_property(collection_msg_anchor_twn_h, "end_value", 0, 12)
		vint_set_property(body_text_h, "anchor", 0, 26)
	end

	-- Hide the stuff about getting smoked like Thanksgiving turkey
	vint_set_property(Hud_smoked_busted.handles.fade_in_anim , "is_paused", true)
	vint_set_property(Hud_smoked_busted.handles.grp, "visible", false)
	vint_set_property(Hud_smoked_busted.handles.grp, "alpha", 0)

	-- Fix the tween if we were interrupted last time by dying
	local h = vint_object_find("collection_anim")
	h = vint_object_find("collection_msg_alpha_twn_2", h)
	vint_set_property(h, "start_value", 1)

	-- Animate the new stuff
	vint_set_property(Hud_collection_msgs.ornate_right_h, "anchor", width * .5, y)
	vint_set_property(Hud_collection_msgs.ornate_left_h , "anchor", -width * .5, y)
	lua_play_anim(vint_object_find("collection_anim"))

	if m.audio >= 0 then
		audio_play(m.audio, "foley", true)
	end
end

function hud_collection_msg_end()
	if Hud_collection_msgs.num_msgs > 0 then
		-- remove element 0 and push others up
		for i = 0, Hud_collection_msgs.num_msgs - 2 do
			Hud_collection_msgs[i] = Hud_collection_msgs[i + 1]
		end

		Hud_collection_msgs[Hud_collection_msgs.num_msgs - 1] = nil
		Hud_collection_msgs.num_msgs = Hud_collection_msgs.num_msgs - 1

		if Hud_collection_msgs.num_msgs > 0 then
			hud_collection_msg_show(Hud_collection_msgs[0])
		end
	end
end

function hud_collection_msg_new(header, body, audio, win_status)
	--TODO: ADD Header/Body/Win Status support (the body can be nil)

	local m = { header = header, body = body, win_status = win_status, audio = audio }
	Hud_collection_msgs[Hud_collection_msgs.num_msgs] = m
	Hud_collection_msgs.num_msgs = Hud_collection_msgs.num_msgs + 1

	if Hud_collection_msgs.num_msgs == 1 then
		hud_collection_msg_show(m)
	end
end


--===================================================
--Cruise Control
--===================================================
function hud_cruise_control_update(is_active)
	local h = vint_object_find("cruise_text", Hud_player_status.cruise_control_h)
	if is_active ~= Hud_player_status.cruise_control_active then
		if is_active == true then
			--Show Cruise Control Status and let it fade with the animation.
			vint_set_property(Hud_player_status.cruise_control_h, "visible", true)
			vint_set_property(Hud_player_status.cruise_control_h, "alpha", .8)
			lua_play_anim(Hud_player_status.cruise_control_anim, 0)
		else
			--Hide status
			vint_set_property(Hud_player_status.cruise_control_h, "visible", false)
		end
	Hud_player_status.cruise_control_active = is_active
	end
end

function hud_cruise_control_update_pos(y_pos)
	local resolution_adjust
	if vint_hack_is_std_res() then
		resolution_adjust = 175
	else
		resolution_adjust = 275
	end

	local x, y = vint_get_property(Hud_player_status.cruise_control_h, "anchor")
	vint_set_property(Hud_player_status.cruise_control_h, "anchor", x, (y_pos+resolution_adjust))
end


--===================================================
--Player Lockon
--===================================================
function hud_player_lockon_update(di_h)
	local x, y, width, rotation, is_locked, is_visible = vint_dataitem_get(di_h)

	vint_set_property(Hud_lockon.lock_h, "anchor", x, y)

	if is_visible == true then
		--Scale
		local scale = width/Hud_lockon.base_pixel_size

		vint_set_property(Hud_lockon.lock_h, "anchor", x, y)
		vint_set_property(Hud_lockon.lock_h, "scale", scale, scale)
		vint_set_property(Hud_lockon.lock_h, "rotation", rotation)

		local lock_inner_width = Hud_lockon.lock_base_width / scale
		local lock_inner_height = Hud_lockon.lock_base_height / scale

		--Rescale Innards
		vint_set_property(Hud_lockon.lock1_h, "scale",Hud_lockon.lock_base_width, lock_inner_height)
		vint_set_property(Hud_lockon.lock2_h, "scale", Hud_lockon.lock_base_width, lock_inner_height)
		vint_set_property(Hud_lockon.lock3_h, "scale", Hud_lockon.lock_base_width, lock_inner_height)
		vint_set_property(Hud_lockon.lock4_h, "scale", Hud_lockon.lock_base_width, lock_inner_height)

		--Tint lockon
		local color
		if is_locked == true then
			color = Hud_lockon.color_locked
		else
			color = Hud_lockon.color_unlocked
		end
		vint_set_property(Hud_lockon.lock_h, "tint", color.r, color.g, color.b)

		--Show lockon
		vint_set_property(Hud_lockon.lock_h, "visible", true)
	else
		vint_set_property(Hud_lockon.lock_h, "visible", false)
	end
end
