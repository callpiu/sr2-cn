-- gmb_poker.lua: Poker Minigame
Gmb_poker = {}

Gmb_poker_thread = -1

GMB_INPUT_STATES = {
	BET = 0,
	HOLDING = 10,
	COMPLETE = 20,
}

GMB_POKER_HANDS = {
	NONE = -1,
	JACKS_OR_HIGHER  = 0,
	TWO_PAIR = 1,
	THREE_OF_A_KIND = 2,
	STRAIGHT = 3,
	FLUSH = 4,
	FULL_HOUSE = 5,
	FOUR_OF_A_KIND = 6,
	STRAIGHT_FLUSH  = 7,
	ROYAL_FLUSH  = 8,
}


GMB_POKER_HANDS_STRINGS = {
	[-1] = 	"DIVERSION_POKER_LOSE",
	[0] = 	"DIVERSION_POKER_JACKS_OR_HIGHER",
	[1] =		"DIVERSION_POKER_TWO_PAIR",
	[2] =		"DIVERSION_POKER_THREE_OF_A_KIND",
	[3] = 	"DIVERSION_POKER_STRAIGHT",
	[4] = 	"DIVERSION_POKER_FLUSH",
	[5] = 	"DIVERSION_POKER_FULL_HOUSE",
	[6] = 	"DIVERSION_POKER_FOUR_OF_A_KIND",
	[7] = 	"DIVERSION_POKER_STRAIGHT_FLUSH",
	[8] = 	"DIVERSION_POKER_ROYAL_FLUSH",
}

GMB_SUIT_ENUMS = {
	BLANK = -1,
	SPADE = 0,
	CLUB = 1,
	DIAMOND = 2,
	HEART = 3,
}

GMB_CARD_ENUMS = {
	[1] = "A",
	[11] = "J",
	[12] = "Q",
	[13] = "K",
}

--Initialize sound
GMB_POKER_AUDIO = {}
GMB_POKER_AUDIO.THEME 		= audio_get_audio_id("SYS_VPOKER_POKERTHEME")
GMB_POKER_AUDIO.NAV 			= audio_get_audio_id("SYS_VPOKER_UDLR")
GMB_POKER_AUDIO.SELECT 		= audio_get_audio_id("SYS_VPOKER_SELECT")
GMB_POKER_AUDIO.DEAL_CARD 	= audio_get_audio_id("SYS_VPOKER_DEALCARD")
GMB_POKER_AUDIO.WIN 			= audio_get_audio_id("SYS_VPOKER_WIN")
GMB_POKER_AUDIO.LOSE 		= audio_get_audio_id("SYS_VPOKER_LOSE")


GMB_CARD_SPACING = 120	-- Spacing of cards
GMB_POKER_CARD_FADE_IN_DELAY = .2 --Every deal it waits this long in seconds before starting to fade in the cards
function gmb_poker_init()

	vint_object_destroy(vint_object_find("card_select_blink"))

	--Set buttons for console specific things
	local confirm_button_h = vint_object_find("btn_a")
	vint_set_property(confirm_button_h, "image", get_a_button())
	local back_button_h = vint_object_find("btn_b")
	vint_set_property(back_button_h, "image", get_b_button())

	--Align Button Tips
	gmb_poker_btntips_align()

	peg_load("ui_gambling")
	--Find objects
	Gmb_poker.handles = {}
	Gmb_poker.handles.cash = vint_object_find("player_cash")
	Gmb_poker.handles.winnings = vint_object_find("winnings_grp")
	Gmb_poker.handles.winnings_cash_txt = vint_object_find("cash_winnings_txt")
	Gmb_poker.handles.winnings_hand_txt = vint_object_find("hand_type_txt")

	Gmb_poker.handles.winnings_box_nw 	= vint_object_find("nw", Gmb_poker.handles.winnings)
	Gmb_poker.handles.winnings_box_n 	= vint_object_find("n", Gmb_poker.handles.winnings)
	Gmb_poker.handles.winnings_box_ne 	= vint_object_find("ne", Gmb_poker.handles.winnings)
	Gmb_poker.handles.winnings_box_w 	= vint_object_find("w", Gmb_poker.handles.winnings)
	Gmb_poker.handles.winnings_box_c 	= vint_object_find("c", Gmb_poker.handles.winnings)
	Gmb_poker.handles.winnings_box_e 	= vint_object_find("e", Gmb_poker.handles.winnings)
	Gmb_poker.handles.winnings_box_sw 	= vint_object_find("sw", Gmb_poker.handles.winnings)
	Gmb_poker.handles.winnings_box_s 	= vint_object_find("s", Gmb_poker.handles.winnings)
	Gmb_poker.handles.winnings_box_se	= vint_object_find("se", Gmb_poker.handles.winnings)

	Gmb_poker.handles.cards = {}
	Gmb_poker.handles.cards[GMB_SUIT_ENUMS.BLANK] = vint_object_find("card_back")
	Gmb_poker.handles.cards[GMB_SUIT_ENUMS.SPADE] = vint_object_find("card_spade")
	Gmb_poker.handles.cards[GMB_SUIT_ENUMS.CLUB] = vint_object_find("card_club")
	Gmb_poker.handles.cards[GMB_SUIT_ENUMS.DIAMOND] = vint_object_find("card_diamond")
	Gmb_poker.handles.cards[GMB_SUIT_ENUMS.HEART] = vint_object_find("card_heart")

	Gmb_poker.handles.card_select = vint_object_find("card_select")
	Gmb_poker.handles.cards_grp = vint_object_find("cards_grp")
	Gmb_poker.handles.hold_box = vint_object_find("hold_grp")

	Gmb_poker.handles.btn_action = vint_object_find("btn_action")
	Gmb_poker.handles.btn_action_text = vint_object_find("text", Gmb_poker.handles.btn_action)
	Gmb_poker.handles.btn_action_highlight = vint_object_find("highlight", Gmb_poker.handles.btn_action)
	Gmb_poker.handles.btn_action_mid = vint_object_find("mid", Gmb_poker.handles.btn_action)
	Gmb_poker.handles.btn_action_right = vint_object_find("right", Gmb_poker.handles.btn_action)

	Gmb_poker.handles.btn_action_highlight_mid = vint_object_find("highlight_mid", Gmb_poker.handles.btn_action)
	Gmb_poker.handles.btn_action_highlight_right = vint_object_find("highlight_right", Gmb_poker.handles.btn_action)

	Gmb_poker.handles.btn_bet = vint_object_find("btn_bet")
	Gmb_poker.handles.btn_bet_arrows = vint_object_find("bet_arrows", Gmb_poker.handles.btn_bet)
	Gmb_poker.handles.btn_bet_highlight = vint_object_find("highlight", Gmb_poker.handles.btn_bet)

	--Payout Objects
	local h = vint_object_find("payouts")
	Gmb_poker.handles.payouts_grp = h
	Gmb_poker.handles.payouts = {}
	Gmb_poker.handles.payouts[GMB_POKER_HANDS.ROYAL_FLUSH] = { val_h = vint_object_find("c_1", h), text_h = vint_object_find("t_1", h)}
	Gmb_poker.handles.payouts[GMB_POKER_HANDS.STRAIGHT_FLUSH] = { val_h = vint_object_find("c_2", h), text_h = vint_object_find("t_2", h)}
	Gmb_poker.handles.payouts[GMB_POKER_HANDS.FOUR_OF_A_KIND] = { val_h = vint_object_find("c_3", h), text_h = vint_object_find("t_3", h)}
	Gmb_poker.handles.payouts[GMB_POKER_HANDS.FULL_HOUSE] = { val_h = vint_object_find("c_4", h), text_h = vint_object_find("t_4", h)}
	Gmb_poker.handles.payouts[GMB_POKER_HANDS.FLUSH] = { val_h = vint_object_find("c_5", h), text_h = vint_object_find("t_5", h)}
	Gmb_poker.handles.payouts[GMB_POKER_HANDS.STRAIGHT] = { val_h = vint_object_find("c_6", h), text_h = vint_object_find("t_6", h)}
	Gmb_poker.handles.payouts[GMB_POKER_HANDS.THREE_OF_A_KIND] = { val_h = vint_object_find("c_7", h), text_h = vint_object_find("t_7", h)}
	Gmb_poker.handles.payouts[GMB_POKER_HANDS.TWO_PAIR] = { val_h = vint_object_find("c_8", h), text_h = vint_object_find("t_8", h)}
	Gmb_poker.handles.payouts[GMB_POKER_HANDS.JACKS_OR_HIGHER] = { val_h = vint_object_find("c_9", h), text_h = vint_object_find("t_9", h)}


	--Anim Objects
	local h = vint_object_find("cards_fade_in")
	Gmb_poker.anims = {}
	Gmb_poker.anims.cards_fade_in = vint_object_find("cards_fade_in")

	Gmb_poker.anims.card_twn_fade_in = vint_object_find("card_twn_fade_in", Gmb_poker.anims.cards_fade_in)

	Gmb_poker.handles.results_anim = vint_object_find("winnings_blink")
	local twn_h = vint_object_find("t_cash_tint_twn_2")
	vint_set_property(twn_h, "end_event", "gmb_poker_loop_cash_anim")

	--Glowing Button Animation
	Gmb_poker.handles.glow_btn_anim = vint_object_find("btn_glow_anim")
	Gmb_poker.handles.glow_btn_twn = vint_object_find("btn_glow_twn", Gmb_poker.handles.glow_btn_anim)


	--Data initialization
	Gmb_poker.current_bet 	= 0
	Gmb_poker.cash 			= 0
	Gmb_poker.cards_dealt 	= 0
	Gmb_poker.cur_idx 		= 0

	Gmb_poker.cards = {}					--Card Data
	Gmb_poker.card_twns = {}			--Card Tweens
	Gmb_poker.payout_data = {}			--Payout Data

	--Set input stat to betting state
	gmb_poker_screen_state_set(GMB_INPUT_STATES.BET)

	--Increment and decrement bet
	vint_dataresponder_request("poker_responder", "gmb_poker_bet_change_cb", 0, 1)
	vint_dataresponder_request("poker_responder", "gmb_poker_bet_change_cb", 0, 0)

	--Subscribe to data
	vint_datagroup_add_subscription("poker_hands", "insert", "gmb_poker_payouts_update")
	vint_datagroup_add_subscription("poker_hands", "update", "gmb_poker_payouts_update")

	--Subscribe to data
	vint_dataitem_add_subscription("sr2_local_player_status_infrequent", "update", "gmb_poker_cash_update")

	--Create cards
	gmb_poker_card_update("reset")

	--Subscribe to inputs
	gmb_poker_input_subscribe()

	--Process
	--cash process
	Gmb_poker_thread = thread_new("gmb_poker_process")

	--Play theme sound
	audio_play(GMB_POKER_AUDIO.THEME)

	--Event Tracking
	event_tracking_interface_enter("Gambling: Poker")
end

function gmb_poker_loop_cash_anim()
	lua_play_anim(Gmb_poker.handles.results_anim, 0)
end

function gmb_poker_input_subscribe()
	--Subscribe to input
	local g = Gmb_poker
	g.input_subs = {
		vint_subscribe_to_input_event(nil, "nav_up",				"gmb_poker_input_event", 50),
		vint_subscribe_to_input_event(nil, "nav_down",			"gmb_poker_input_event", 50),
		vint_subscribe_to_input_event(nil, "nav_right",			"gmb_poker_input_event", 50),
		vint_subscribe_to_input_event(nil, "nav_left",			"gmb_poker_input_event", 50),
		vint_subscribe_to_input_event(nil, "select",				"gmb_poker_input_event", 50),
		vint_subscribe_to_input_event(nil, "pause",				"gmb_poker_input_event", 50),
		vint_subscribe_to_input_event(nil, "back",				"gmb_poker_input_event", 100),
		vint_subscribe_to_input_event(nil, "map",				"gmb_poker_input_event", 100),
	}

	--Make repeat rate super high
	vint_set_input_params(g.input_subs[5], 120, nil, nil, nil)
	vint_set_input_params(g.input_subs[6], 120, nil, nil, nil)
	vint_set_input_params(g.input_subs[7], 120, nil, nil, nil)
end

function gmb_poker_input_desubscribe()
	--	Unsubscribe to input
	local g = Gmb_poker
	for idx, val in g.input_subs do
		vint_unsubscribe_to_input_event(val)
	end
	g.input_subs = nil
end

function gmb_poker_input_event(target, event, accelleration)

	--Is input blocked?
	if gmb_poker_input_is_bocked() then
		return
	end

	if Gmb_poker.input_state == GMB_INPUT_STATES.BET then
		if event == "nav_up" then
			--Increase bet
			audio_play(GMB_POKER_AUDIO.NAV)
			vint_dataresponder_request("poker_responder", "gmb_poker_bet_change_cb", 0, 0)
		elseif event == "nav_down" then
			--Decrease bet
			audio_play(GMB_POKER_AUDIO.NAV)
			vint_dataresponder_request("poker_responder", "gmb_poker_bet_change_cb", 0, 1)

		elseif event == "select" then
			--Check to make sure the player has enough cash to make current bet
			if Gmb_poker.current_bet > Gmb_poker.cash then
				gmb_poker_not_enough_cash_dialog()
				return
			end
			--Select bet
			audio_play(GMB_POKER_AUDIO.SELECT)
			gmb_poker_deal_first()
		end
	elseif Gmb_poker.input_state == GMB_INPUT_STATES.HOLDING then
		if event == "nav_up" or event == "nav_down" then
			--swap between deal and hold
			local new_idx
			if Gmb_poker.cur_idx > 0 then
				new_idx = 0
			else
				new_idx = 1
			end
			audio_play(GMB_POKER_AUDIO.NAV)
			gmb_poker_hold_nav(new_idx)
		elseif event == "nav_right" then
			local new_idx
			if Gmb_poker.cur_idx == 0 then
				--if not on a card select furthest right card
				new_idx  = 5
			else
				new_idx = Gmb_poker.cur_idx + 1
				if new_idx > 5 then
					--Wrap around to left card
					new_idx = 1
				end
			end
			audio_play(GMB_POKER_AUDIO.NAV)
			gmb_poker_hold_nav(new_idx)
		elseif event == "nav_left" then
			--if not on a card select furthest left card
			local new_idx
			if Gmb_poker.cur_idx == 0 then
				new_idx = 1
			else
				new_idx = Gmb_poker.cur_idx - 1
				if new_idx < 1 then
					--Wrap around to left card
					new_idx = 5
				end
			end
			audio_play(GMB_POKER_AUDIO.NAV)
			gmb_poker_hold_nav(new_idx)
		elseif event == "select" then

			audio_play(GMB_POKER_AUDIO.SELECT)
			if Gmb_poker.cur_idx == 0 then
				--deal
				gmb_poker_deal_second()
			else
				--hold toggle
				gmb_poker_hold_select()
			end
		end
	elseif Gmb_poker.input_state == GMB_INPUT_STATES.COMPLETE then
		if event == "select" then
			audio_play(GMB_POKER_AUDIO.SELECT)
			vint_dataresponder_request("poker_responder", "gmb_poker_restart", 0, 7)
		end
	end

	--No where to pause
	if event == "pause" then
		dialog_open_pause_display()
	end

	--Always able to quit
	if event == "back" then
		--Indicate to C that we've quit
		gmb_poker_quit_dialog()
	end
end

function gmb_poker_bet_change_cb(new_bet)
	--Update betting string in button
	Gmb_poker.current_bet = new_bet

	local btn_bet_h = vint_object_find("btn_bet")
	local cash_h = vint_object_find("cash", btn_bet_h)
	vint_set_property(cash_h, "text_tag", "$" .. format_cash(new_bet))


	gmb_poker_payouts_update_screen()
end

--[[
first parameter - message type
	0 - increment bet
	1 - decrement bet
	2 - hold card
		- second parameter - which card (0 - 4)
	3 - unhold
		- second parameter - which card (0 - 4)
	3 - first deal
	4 - second deal
	5 - quit
	6 - start new game
]]


function gmb_poker_cleanup()
	gmb_poker_input_desubscribe()
	--Kill process thread
	if Gmb_poker_thread ~= -1 then
		thread_kill(Gmb_poker_thread)
		Gmb_poker_thread = -1
	end
	--Unload Gambling Peg
	peg_unload("ui_gambling")

	--Event Tracking (Exit gambling)
	event_tracking_interface_exit()
end

function gmb_poker_screen_state_set(state)


	if state == GMB_INPUT_STATES.BET then
		vint_set_property(Gmb_poker.handles.winnings, "visible", false)
		--Set action button Text
		gmb_poker_action_btn_set_text("DIVERSION_POKER_DEAL")
		gmb_poker_action_btn_set_state(true)

		--Show arrows on betting and highlight btn
		vint_set_property(Gmb_poker.handles.btn_bet_arrows, "visible", true)
		vint_set_property(Gmb_poker.handles.btn_bet_highlight, "visible", false)

	elseif state == GMB_INPUT_STATES.HOLDING then
		--Reset cursor index
		Gmb_poker.cur_idx = 0
		gmb_poker_action_btn_set_text("DIVERSION_POKER_DEAL")
		gmb_poker_action_btn_set_state(true)
	elseif state == GMB_INPUT_STATES.COMPLETE then
		gmb_poker_action_btn_set_text("DIVERSION_POKER_PLAY_AGAIN")
		gmb_poker_action_btn_set_state(true)
	end

	--Set input state
	Gmb_poker.input_state = state
end


function gmb_poker_payouts_update(di_h)
	--Event from game dumps data into stored data and updates the item
	local hand_enum, value_multiplier, is_active = vint_dataitem_get(di_h)
	Gmb_poker.payout_data[hand_enum] = {hand_enum = hand_enum, value_multiplier = value_multiplier, is_active = is_active}
	gmb_poker_payouts_update_item(hand_enum)

	if is_active == true then
		--mark active
	else
		--mark normal
	end
end

function gmb_poker_payouts_update_screen()
	for idx, val in Gmb_poker.payout_data do
		gmb_poker_payouts_update_item(idx)
	end
end

function gmb_poker_payouts_update_item(hand_enum)
	--Updates the payout item with current data
	local payout_val_h = Gmb_poker.handles.payouts[hand_enum].val_h
	local hand_value = Gmb_poker.payout_data[hand_enum].value_multiplier * Gmb_poker.current_bet
	vint_set_property(payout_val_h, "text_tag", "$" .. format_cash(hand_value))
end

function gmb_poker_deal_first()
	--block input
	gmb_poker_input_block(true)

	--Deals hand
	--Remove all cards
	gmb_poker_card_clear_all()

	Gmb_poker.cards_dealt = 0
	vint_dataresponder_request("poker_responder", "gmb_poker_deal_cb", 0, 4)

	--Set callback of master tween
	vint_set_property(Gmb_poker.anims.card_twn_fade_in, "end_event", "gmb_poker_deal_first_complete")

	--Set callback of master tween ot fire after last tween
	vint_set_property(Gmb_poker.anims.card_twn_fade_in, "start_time", Gmb_poker.cards_dealt*.1)

	--Play card fade in animation
	lua_play_anim(Gmb_poker.anims.cards_fade_in, GMB_POKER_CARD_FADE_IN_DELAY)

	--Hide betting arrows and update betting state
	vint_set_property(Gmb_poker.handles.btn_bet_arrows , "visible", false)
	vint_set_property(Gmb_poker.handles.btn_bet_highlight , "visible", false)
end

function gmb_poker_deal_first_complete()
	--Cards have faded in now lets reset some status markers

	--clear all the tweens
	for idx, val in Gmb_poker.card_twns do
		vint_object_destroy(idx)
	end
	Gmb_poker.card_twns = {}

	--Set Hold status on all the cards
	for idx, val in Gmb_poker.cards do
		if val.is_held == true then
			vint_set_property(val.hold_h, "visible", true)
		else
			vint_set_property(val.hold_h, "visible", false)
		end
	end

	--Cards are dealt and visible now.. unblock input and change screen state.
	gmb_poker_screen_state_set(GMB_INPUT_STATES.HOLDING)
	--Unblock input
	gmb_poker_input_block(false)
end

function gmb_poker_deal_second()
	--block input
	gmb_poker_input_block(true)

	--Clear out unheld cards
	for idx, val in Gmb_poker.cards do
		if val.is_held == false then
			vint_object_destroy(val.hold_h)
			vint_object_destroy(val.grp_h)
			Gmb_poker.cards[idx] = nil
			Gmb_poker.cards_dealt = Gmb_poker.cards_dealt - 1
		end
		--Clear out hold status
		if val.is_held == true then
			vint_object_destroy(val.hold_h)
			Gmb_poker.cards[idx].hold_h = nil
			Gmb_poker.cards[idx].is_held = false
		end
	end

	--Reset how many cards are delt this round
	Gmb_poker.cards_dealt = 0

	--Deal new cards
	vint_dataresponder_request("poker_responder", "gmb_poker_deal_cb", 0, 5)

	--Set callback of master tween
	vint_set_property(Gmb_poker.anims.card_twn_fade_in, "end_event", "gmb_poker_deal_second_complete")

	--Set callback of master tween ot fire after last tween
	vint_set_property(Gmb_poker.anims.card_twn_fade_in, "start_time", Gmb_poker.cards_dealt*.1)

	--Play card fade in animation
	lua_play_anim(Gmb_poker.anims.cards_fade_in, GMB_POKER_CARD_FADE_IN_DELAY)
end


function gmb_poker_deal_cb(card_slot, suit_enum, card_enum, is_held)

	--Card already exists in slot... do not replace
	--However, we need to set its hold status
	if Gmb_poker.cards[card_slot] ~= nil then
		Gmb_poker.cards[card_slot].is_held = is_held
		return
	end

	--Update data
	local h = vint_object_clone(Gmb_poker.handles.cards[suit_enum])
	local hold_h = vint_object_clone(Gmb_poker.handles.hold_box)

	--Resolve the card number for the card
	local card_number
	if GMB_CARD_ENUMS[card_enum] ~= nil then
		--Use specified string for the enum
		card_number = GMB_CARD_ENUMS[card_enum]
	else
		--Use normal number
		card_number = card_enum
	end

	--Set text on card
	local card_num_1_h = vint_object_find("card_num_1", h)
	local card_num_2_h = vint_object_find("card_num_2", h)
	vint_set_property(card_num_1_h, "text_tag", card_number)
	vint_set_property(card_num_2_h, "text_tag", card_number)

	--Store into table
	Gmb_poker.cards[card_slot] = {
		grp_h = h,
		hold_h = hold_h,
		suite = suit_enum,
		card = card_enum,
		is_held = is_held,
	}

	--Position cards and hold status
	local x
	local y = 0
	local x = card_slot * GMB_CARD_SPACING
	vint_set_property(Gmb_poker.cards[card_slot].grp_h, "anchor", x, y)
	vint_set_property(Gmb_poker.cards[card_slot].hold_h, "anchor", x, y)
	vint_set_property(Gmb_poker.cards[card_slot].hold_h, "visible", false)

	--Create a tween for the card
	local twn_h = vint_object_clone(Gmb_poker.anims.card_twn_fade_in)

	--Offset time based on how many cards are delt this round
	vint_set_property(twn_h, "start_time", .1 * Gmb_poker.cards_dealt)

	--Retarget
	vint_set_property(twn_h, "target_handle", Gmb_poker.cards[card_slot].grp_h)

	--Hide object
	vint_set_property(Gmb_poker.cards[card_slot].grp_h, "alpha", 0)

	vint_set_property(twn_h, "end_event", "gmb_poker_deal_card_sound")

	--Store tween for cleanup
	Gmb_poker.card_twns[twn_h] = true

	Gmb_poker.cards_dealt = Gmb_poker.cards_dealt + 1
end

function gmb_poker_deal_second_complete()

	local x, y

	--Replace held card status with glowing highlights
	for idx, val in Gmb_poker.cards do
		if val.is_held == true then

			--Only clone a new one if we have another one
			if Gmb_poker.cards[idx].hold_h == nil then
				Gmb_poker.cards[idx].hold_h = vint_object_clone(Gmb_poker.handles.card_select)
			end

			vint_set_property(Gmb_poker.cards[idx].hold_h, "visible", true)
			x, y = vint_get_property(val.grp_h, "anchor")
			vint_set_property(Gmb_poker.cards[idx].hold_h, "anchor", x, y)
		end
	end

	vint_dataresponder_request("poker_responder", "gmb_poker_winnings_cb", 0, 8)

	--Show winnings
	vint_set_property(Gmb_poker.handles.winnings, "visible", true)

	gmb_poker_screen_state_set(GMB_INPUT_STATES.COMPLETE)
	gmb_poker_input_block(false)
end


function gmb_poker_winnings_cb(hand_enum, dollars_winnings)

	--Show winnings information
	vint_set_property(Gmb_poker.handles.winnings_hand_txt, "text_tag", var_to_string(GMB_POKER_HANDS_STRINGS[hand_enum]))
	vint_set_property(Gmb_poker.handles.winnings_cash_txt, "text_tag", "$" .. format_cash(dollars_winnings))

	local width, height = element_get_actual_size(Gmb_poker.handles.winnings_hand_txt)
	width = floor(width)
	height = floor(height)
	local x = floor(width/2)
	local y = floor(height/2)
	local box_shrink = 36

	local x_minus, y_minus
	x_minus = x * -1
	y_minus = y * -1

	local source_se_width, source_se_height

	--Everything based on center
	element_set_actual_size(Gmb_poker.handles.winnings_box_c, width, height)

	vint_set_property(Gmb_poker.handles.winnings_box_nw, "anchor", x_minus, y_minus)
	vint_set_property(Gmb_poker.handles.winnings_box_n, "anchor", x_minus, y_minus)

	source_se_width, source_se_height = vint_get_property(Gmb_poker.handles.winnings_box_n, "source_se")

	if dollars_winnings == 0 then
		vint_set_property(Gmb_poker.handles.winnings_cash_txt, "visible", false)
		vint_set_property(Gmb_poker.handles.winnings_box_c, "source_se", source_se_width, 8)
	else
		vint_set_property(Gmb_poker.handles.winnings_cash_txt, "visible", true)
		vint_set_property(Gmb_poker.handles.winnings_box_c, "source_se", source_se_width, height)
		box_shrink = 0
	end

	vint_set_property(Gmb_poker.handles.winnings_box_n, "source_se", width, source_se_height)
	vint_set_property(Gmb_poker.handles.winnings_box_ne, "anchor", x, y_minus)

	vint_set_property(Gmb_poker.handles.winnings_box_w, "anchor", x_minus, y_minus)
	vint_set_property(Gmb_poker.handles.winnings_box_w, "source_se", width, height - box_shrink)
	vint_set_property(Gmb_poker.handles.winnings_box_e, "anchor", x, y_minus)
	vint_set_property(Gmb_poker.handles.winnings_box_e, "source_se", width, height - box_shrink)

	vint_set_property(Gmb_poker.handles.winnings_box_sw, "anchor", x_minus, y - box_shrink)
	vint_set_property(Gmb_poker.handles.winnings_box_s, "anchor", x_minus, y - box_shrink)
	vint_set_property(Gmb_poker.handles.winnings_box_s, "source_se", width, height - box_shrink)
	vint_set_property(Gmb_poker.handles.winnings_box_se, "anchor", x, y - box_shrink)

	if hand_enum >= 0 then
		--Win
		audio_play(GMB_POKER_AUDIO.WIN)

	else
		--lose
		audio_play(GMB_POKER_AUDIO.LOSE)
	end
end

function gmb_poker_deal_card_sound()
	audio_play(GMB_POKER_AUDIO.DEAL_CARD)
end

function gmb_poker_card_update(action)
	if action == "reset" then
		--Clear cards out of slots
		gmb_poker_card_clear_all()

		--Create 5 blank cards
		local card_idx, h, x, y
		y = 0
		for card_idx = 0, 4 do
			h = vint_object_clone(Gmb_poker.handles.cards[GMB_SUIT_ENUMS.BLANK])
			Gmb_poker.cards[card_idx] = {
				grp_h = h,
				suite = GMB_SUIT_ENUMS.BLANK,
				is_held = false,
				card = -1
			}
			x = card_idx * GMB_CARD_SPACING
			vint_set_property(h, "anchor", x, y)
		end

	elseif action == "flip" then

	end
end


function gmb_poker_card_clear_all()
	for idx, val in Gmb_poker.cards do
		vint_object_destroy(val.grp_h)
		--Destroy hold card if it exists
		if val.hold_h ~= nil then
			vint_object_destroy(val.hold_h)
		end
	end
	Gmb_poker.cards = {}
end

--=================================
--Poker Hold Interface
--=================================
function gmb_poker_hold_nav(new_idx)

	if new_idx == 0 then
		--hide selector
		vint_set_property(Gmb_poker.handles.card_select, "visible", false)

		--Show deal highlight btn
		gmb_poker_action_btn_set_state(true)
	else
		--show Selector
		vint_set_property(Gmb_poker.handles.card_select, "visible", true)

		vint_set_property(Gmb_poker.handles.glow_btn_twn, "target_handle", Gmb_poker.handles.card_select)

		--move selector
		local target_card = Gmb_poker.cards[new_idx - 1].grp_h
		local x, y = vint_get_property(target_card, "anchor")
		vint_set_property(Gmb_poker.handles.card_select, "anchor", x, y)

		--Unhighlight deal btn
		gmb_poker_action_btn_set_state(false)
	end

	Gmb_poker.cur_idx = new_idx
end

function gmb_poker_hold_select()
	--Toggle hold
	--Make sure our index is greater than 0
	if Gmb_poker.cur_idx < 1 then
		return
	end

	local card_slot = Gmb_poker.cur_idx - 1
	local selected_card = Gmb_poker.cards[card_slot]

	--Get card status
	if selected_card.is_held == true then
		--hold card
		vint_dataresponder_request("poker_responder", "gmb_poker_hold_cb", 0, 2, card_slot)
	else
		--unhold card
		vint_dataresponder_request("poker_responder", "gmb_poker_hold_cb", 0, 3, card_slot)
	end
end

function gmb_poker_hold_cb(success)
	if success == true then
		local card_slot = Gmb_poker.cur_idx - 1
		local selected_card = Gmb_poker.cards[card_slot]

		--based on card status flip the is_held toggle
		if selected_card.is_held == true then
			--hide hold status and set data
			vint_set_property(selected_card.hold_h, "visible", false)
			selected_card.is_held = false
		else
			--Show hold status and set data
			vint_set_property(selected_card.hold_h, "visible", true)
			selected_card.is_held = true
		end
	end
end

function gmb_poker_restart(success)
	--mm... what do i do?
	gmb_poker_card_update("reset")
	gmb_poker_screen_state_set(GMB_INPUT_STATES.BET)
end

--=================================
--CASH UPDATES
--=================================
function gmb_poker_cash_update(di_h)
	local cash = vint_dataitem_get(di_h)
	Gmb_poker.cash = floor(cash)
end

function gmb_poker_process()

	local display_cash = Gmb_poker.cash - 1 --Subtract one so it gets formatted in the loop.
	while true do
		thread_yield()

		-- Animate Cash
		if display_cash ~= Gmb_poker.cash  then
			local diff_cash = Gmb_poker.cash  - display_cash

			if diff_cash > 5 or diff_cash < -5 then
				diff_cash = floor(diff_cash * 0.5)
			end

			display_cash = display_cash + diff_cash
			vint_set_property(Gmb_poker.handles.cash, "text_tag", "$" .. format_cash(display_cash))
		end
	end
end

--==================================
--ACTION BUTTON
--==================================
function gmb_poker_action_btn_set_text(text_string)

	--Set text tag
	vint_set_property(Gmb_poker.handles.btn_action_text, "text_tag", text_string)

	--Adjust widths
	local width, height = element_get_actual_size(Gmb_poker.handles.btn_action_text)
	width = floor(width)
	height = floor(height)
	local x, y
	vint_set_property(Gmb_poker.handles.btn_action_mid, "source_se", width, 200)
   x, y = vint_get_property(Gmb_poker.handles.btn_action_mid , "anchor")
	vint_set_property(Gmb_poker.handles.btn_action_right, "anchor", x + width, y)
	vint_set_property(Gmb_poker.handles.btn_action_highlight_mid, "source_se", width, 200)
	vint_set_property(Gmb_poker.handles.btn_action_highlight_right, "anchor",  x + width, y)
end

function gmb_poker_action_btn_set_state(active)
	if active == true then
		vint_set_property(Gmb_poker.handles.glow_btn_twn, "target_handle", Gmb_poker.handles.btn_action_highlight)
		vint_set_property(Gmb_poker.handles.btn_action_highlight, "visible", true)
		vint_set_property(Gmb_poker.handles.btn_action_text, "tint", .9, .74, .05)
	else
		vint_set_property(Gmb_poker.handles.btn_action_highlight, "visible", false)
		vint_set_property(Gmb_poker.handles.btn_action_highlight, "tint", 1, 1, 1)
		vint_set_property(Gmb_poker.handles.btn_action_text, "tint", .77, .8, .81)
	end
end

--=================================
--QUIT POKER
--=================================
function gmb_poker_quit(success)
	if success == true then
		vint_document_unload(vint_document_find("gmb_poker"))
	end
end

--================================
--DIALOG BOXES
--================================
function gmb_poker_quit_dialog()
	if Gmb_poker.input_state == GMB_INPUT_STATES.HOLDING then
		-- If middle of the game show confirm dialog
		dialog_box_confirmation("GAMBLING_POKER_DIALOG_QUIT_HEADER", "GAMBLING_POKER_DIALOG_QUIT_BODY", "gmb_poker_quit_dialog_cb")
	else
		vint_dataresponder_request("poker_responder", "gmb_poker_quit", 0, 6)	-- Quit without dialog [nclok1405]
	end
end

function gmb_poker_quit_dialog_cb(result, action)
	if action ~= DIALOG_ACTION_CLOSE then
		return
	end
	if result == 0 then
		--Quit Request
		vint_dataresponder_request("poker_responder", "gmb_poker_quit", 0, 6)
	else
		--do nothing
	end
end

function gmb_poker_not_enough_cash_dialog()
	dialog_box_message("GAMBLING_POKER_DIALOG_NO_CASH_HEADER","GAMBLING_POKER_DIALOG_NO_CASH_BODY")
end

--=================================
--INPUT BLOCK
--=================================
Gmb_poker_input_blocked = 0
function gmb_poker_input_block(block)
	if block == true then
		Gmb_poker_input_blocked = Gmb_poker_input_blocked + 1
	else
		Gmb_poker_input_blocked = Gmb_poker_input_blocked - 1
	end
end

function gmb_poker_input_is_bocked()
	if Gmb_poker_input_blocked > 0 then
		return true
	else
		return false
	end
end



--=================================
--ALIGN BUTTONS
--=================================
function gmb_poker_btntips_align()
	local btn_spacing = 1
	local grp_spacing = 30
	local h = vint_object_find("btn_tips")
	local btn_b_h = vint_object_find("btn_b", h)
	local text_b_h = vint_object_find("b_text", h)
	local a_text_h = vint_object_find("a_text", h)
	local a_text_width, a_text_height = element_get_actual_size(a_text_h)
	local btn_b_width, btn_b_height = element_get_actual_size(btn_b_h)
	local a_text_x, a_text_y = vint_get_property(a_text_h, "anchor")

	--B Btn
	local x = a_text_x + a_text_width + grp_spacing
	local y = a_text_y
	vint_set_property(btn_b_h, "anchor", x, y)

	--B Text
	local x = x + btn_b_width/2 + btn_spacing
	vint_set_property(text_b_h, "anchor", x, y)
end
