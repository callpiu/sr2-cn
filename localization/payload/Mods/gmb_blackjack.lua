-- gmb_blackjack.lua: Blackjack Minigame
Gmb_blackjack = {}


Gmb_blackjack.card_twns = {}
Gmb_blackjack_thread = -1

--Card Enums
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

GMB_PLAYER_ENUMS = {
	DEALER_HAND = 0,
	PLAYER_HAND = 1,
	SPLIT_HAND = 2
}

GMB_HAND_VALUES = {
	[0] = "0",
	[1] = "WIN",
	[2] = "LOSE",
	[3] = "DIVERSION_BLACKJACK_BUST",
	[4] = "DIVERSION_BLACKJACK_BLACKJACK",
	[5] = "DIVERSION_BLACKJACK_PUSH",
	[6] = "DIVERSION_BLACKJACK_DEALER_BLACKJACK",
	[7] = "DIVERSION_BLACKJACK_DEALER_BUST"
}

--Input/Screen states
--All input states have a respresenting screenstate that is managed together in a sloppy way.
GMB_INPUT_STATES = {
	BET = 0,
	CONTINUE = 10,
	CONTINUE_SPLIT = 30,
	CONTINUE_DOUBLEDOWN = 40,
	FINISHED = 50,
}

--Initialize sound
GMB_BLACKJACK_AUDIO = {}
GMB_BLACKJACK_AUDIO.THEME 		= audio_get_audio_id("SYS_VPOKER_POKERTHEME")
GMB_BLACKJACK_AUDIO.NAV 			= audio_get_audio_id("SYS_VPOKER_UDLR")
GMB_BLACKJACK_AUDIO.SELECT 		= audio_get_audio_id("SYS_VPOKER_SELECT")
GMB_BLACKJACK_AUDIO.DEAL_CARD 	= audio_get_audio_id("SYS_VPOKER_DEALCARD")
GMB_BLACKJACK_AUDIO.WIN 			= audio_get_audio_id("SYS_VPOKER_WIN")
GMB_BLACKJACK_AUDIO.LOSE 		= audio_get_audio_id("SYS_VPOKER_LOSE")

function gmb_blackjack_init()

	local h, x, y
	--Load Bitmaps
	peg_load("ui_gambling")

	--Handles
	Gmb_blackjack.handles = {}

	--Bet button
	Gmb_blackjack.handles.btn_bet 				= vint_object_find("btn_bet") --Bet Button
	Gmb_blackjack.handles.btn_bet_arrow_left  = vint_object_find("arrow_left", Gmb_blackjack.handles.btn_bet)
	Gmb_blackjack.handles.btn_bet_arrow_right = vint_object_find("arrow_right", Gmb_blackjack.handles.btn_bet)
	Gmb_blackjack.handles.btn_bet_cash 			= vint_object_find("cash", Gmb_blackjack.handles.btn_bet)


	local confirm_button_h = vint_object_find("btn_a")
	vint_set_property(confirm_button_h, "image", get_a_button())

	local back_button_h = vint_object_find("btn_b")
	vint_set_property(back_button_h, "image", get_b_button())

	Gmb_blackjack.handles.cash = vint_object_find("player_cash") --Cash

	--Winnings
	Gmb_blackjack.handles.winnings 			= vint_object_find("winnings_grp") -- Winnings
	Gmb_blackjack.handles.winnings_type 	= vint_object_find("hand_type_txt", Gmb_blackjack.handles.winnings) -- Winnings
	Gmb_blackjack.handles.winnings_cash		= vint_object_find("cash_winnings_txt", Gmb_blackjack.handles.winnings) -- Cash Winnings
	Gmb_blackjack.handles.winnings_box_nw 	= vint_object_find("nw", Gmb_blackjack.handles.winnings)
	Gmb_blackjack.handles.winnings_box_n 	= vint_object_find("n",  Gmb_blackjack.handles.winnings)
	Gmb_blackjack.handles.winnings_box_ne 	= vint_object_find("ne", Gmb_blackjack.handles.winnings)
	Gmb_blackjack.handles.winnings_box_w 	= vint_object_find("w",  Gmb_blackjack.handles.winnings)
	Gmb_blackjack.handles.winnings_box_c 	= vint_object_find("c",  Gmb_blackjack.handles.winnings)
	Gmb_blackjack.handles.winnings_box_e 	= vint_object_find("e",  Gmb_blackjack.handles.winnings)
	Gmb_blackjack.handles.winnings_box_sw 	= vint_object_find("sw", Gmb_blackjack.handles.winnings)
	Gmb_blackjack.handles.winnings_box_s 	= vint_object_find("s",  Gmb_blackjack.handles.winnings)
	Gmb_blackjack.handles.winnings_box_se	= vint_object_find("se", Gmb_blackjack.handles.winnings)

	--Cards
	Gmb_blackjack.handles.cards = {}
	Gmb_blackjack.handles.cards[GMB_SUIT_ENUMS.BLANK] = vint_object_find("card_back")
	Gmb_blackjack.handles.cards[GMB_SUIT_ENUMS.SPADE] = vint_object_find("card_spade")
	Gmb_blackjack.handles.cards[GMB_SUIT_ENUMS.CLUB] = vint_object_find("card_club")
	Gmb_blackjack.handles.cards[GMB_SUIT_ENUMS.DIAMOND] = vint_object_find("card_diamond")
	Gmb_blackjack.handles.cards[GMB_SUIT_ENUMS.HEART] = vint_object_find("card_heart")

	--Card Sets
	Gmb_blackjack.handles.card_sets = {}
	Gmb_blackjack.handles.card_sets[GMB_PLAYER_ENUMS.DEALER_HAND] = vint_object_find("cards_dealer_1")
	Gmb_blackjack.handles.card_sets[GMB_PLAYER_ENUMS.PLAYER_HAND] = vint_object_find("cards_player_1")
	Gmb_blackjack.handles.card_sets[GMB_PLAYER_ENUMS.SPLIT_HAND]  = vint_object_find("cards_player_2")

	--Card Values
	h = vint_object_find("hand_value_grp")
	Gmb_blackjack.handles.hand_values = {}
	Gmb_blackjack.handles.hand_values[GMB_PLAYER_ENUMS.DEALER_HAND] = vint_object_clone(h)
	Gmb_blackjack.handles.hand_values[GMB_PLAYER_ENUMS.PLAYER_HAND] = vint_object_clone(h)
	Gmb_blackjack.handles.hand_values[GMB_PLAYER_ENUMS.SPLIT_HAND] = vint_object_clone(h)


	x, y = vint_get_property(Gmb_blackjack.handles.card_sets[GMB_PLAYER_ENUMS.DEALER_HAND], "anchor")
	vint_set_property(Gmb_blackjack.handles.hand_values[GMB_PLAYER_ENUMS.DEALER_HAND], "anchor", x, y)

	x, y = vint_get_property(Gmb_blackjack.handles.card_sets[GMB_PLAYER_ENUMS.PLAYER_HAND], "anchor")
	vint_set_property(Gmb_blackjack.handles.hand_values[GMB_PLAYER_ENUMS.PLAYER_HAND], "anchor", x, y)

	x, y = vint_get_property(Gmb_blackjack.handles.card_sets[GMB_PLAYER_ENUMS.SPLIT_HAND], "anchor")
	vint_set_property(Gmb_blackjack.handles.hand_values[GMB_PLAYER_ENUMS.SPLIT_HAND], "anchor", x, y)

	Gmb_blackjack.handles.hand_value_y = y

	--Split indicator
	Gmb_blackjack.handles.split_ind = vint_object_find("card_split")
	Gmb_blackjack.handles.card_select = vint_object_find("card_select_blink")

	--Cards fade in
	Gmb_blackjack.anims = {}
	Gmb_blackjack.anims.cards_fade  = vint_object_find("cards_fade_in")
	Gmb_blackjack.anims.card_twn_fade_in  = vint_object_find("card_twn_fade_in")
	vint_set_property(Gmb_blackjack.anims.cards_fade, "is_paused", true)

	--Align button Tips
	gmb_blackjack_btntips_align()

	--Initilize Globals
	Gmb_blackjack.current_bet = 0
	Gmb_blackjack.cash = 0

	Gmb_blackjack.cur_idx = 0			--Where the cursor is

	--Glowing Button Animation
	Gmb_blackjack.handles.glow_btn_anim = vint_object_find("btn_glow_anim")
	Gmb_blackjack.handles.glow_btn_twn = vint_object_find("btn_glow_twn", Gmb_blackjack.handles.glow_btn_anim)


	--Result blink anim
	Gmb_blackjack.handles.results_anim = vint_object_find("t_cash_blink")
	local twn_h = vint_object_find("t_cash_tint_twn_2")
	vint_set_property(twn_h, "end_event", "gmb_blackjack_loop_cash_anim")

	--Initialize functions and subscribe to events


	--Subscribe to cash data
	vint_dataitem_add_subscription("sr2_local_player_status_infrequent", "update", "gmb_blackjack_cash_update")

	--Cash process
	Gmb_blackjack_thread = thread_new("gmb_blackjack_process")

	--Initialize table by faking a new game...
	gmb_blackjack_table_init()
	gmb_blackjack_newgame_cb()

	--Subscribe to inputs
	gmb_blackjack_input_subscribe()

	--Event Tracking
	event_tracking_interface_enter("Gambling: Blackjack")
end

function gmb_blackjack_cleanup()

	--UnLoad Bitmaps
	peg_unload("ui_gambling")


	gmb_blackjack_input_desubscribe()

	if Gmb_blackjack_thread ~= -1 then
		thread_kill(Gmb_blackjack_thread)
	end

	--Event Tracking (Exit gambling)
	event_tracking_interface_exit()
end


function gmb_blackjack_input_subscribe()
	--Subscribe to input
	local g = Gmb_blackjack

--	-vint_set_input_params(subscription_handle, repeat_time, acceleration_factor, acceleration_limit, smooth_accelleration)
	g.input_subs = {
		vint_subscribe_to_input_event(nil, "nav_up",				"gmb_blackjack_input_event", 50),
		vint_subscribe_to_input_event(nil, "nav_down",			"gmb_blackjack_input_event", 50),
		vint_subscribe_to_input_event(nil, "nav_right",			"gmb_blackjack_input_event", 50),
		vint_subscribe_to_input_event(nil, "nav_left",			"gmb_blackjack_input_event", 50),
		vint_subscribe_to_input_event(nil, "select",				"gmb_blackjack_input_event", 50), --5
		vint_subscribe_to_input_event(nil, "pause",				"gmb_blackjack_input_event", 50), --6
		vint_subscribe_to_input_event(nil, "back",				"gmb_blackjack_input_event", 100), --7
		vint_subscribe_to_input_event(nil, "map",					"gmb_blackjack_input_event", 100), --7
	}

	vint_set_input_params(g.input_subs[5], 120, nil, nil, nil)
	vint_set_input_params(g.input_subs[6], 120, nil, nil, nil)
	vint_set_input_params(g.input_subs[7], 120, nil, nil, nil)
end

function gmb_blackjack_input_desubscribe()
	--	Unsubscribe to input
	local g = Gmb_blackjack
	for idx, val in g.input_subs do
		vint_unsubscribe_to_input_event(val)
	end
	g.input_subs = nil
end

function gmb_blackjack_input_event(target, event, accelleration)

	--Is input blocked?
	if gmb_blackjack_input_is_bocked() then
		return
	end

	if Gmb_blackjack.input_state == GMB_INPUT_STATES.BET then
		--Bet Mode
		if event == "nav_left" then
			--Bet Decrease
			vint_dataresponder_request("blackjack_responder", "gmb_blackjack_bet_change_cb", 0, 1)
			audio_play(GMB_BLACKJACK_AUDIO.NAV)
		elseif event == "nav_right" then
			--Bet Increase
			vint_dataresponder_request("blackjack_responder", "gmb_blackjack_bet_change_cb", 0, 0)
			audio_play(GMB_BLACKJACK_AUDIO.NAV)
		elseif event == "select" then
				--Check to make sure the player has enough cash to make current bet
			if Gmb_blackjack.current_bet > Gmb_blackjack.cash then
				gmb_blackjack_not_enough_cash_dialog()
				return
			end

			--Deal it
			gmb_blackjack_deal_first()
			audio_play(GMB_BLACKJACK_AUDIO.SELECT)

			gmb_blackjack_input_block(true)
		end
	elseif Gmb_blackjack.input_state > GMB_INPUT_STATES.BET then
		if event == "nav_up" then
			--Switch cursor
			local new_idx = Gmb_blackjack.cur_idx - 1
			if new_idx < 0 then
				new_idx = Gmb_blackjack.num_btns - 1
			end
			gmb_blackjack_btn_highlight(new_idx)
			Gmb_blackjack.cur_idx = new_idx
			audio_play(GMB_BLACKJACK_AUDIO.NAV)
		elseif event == "nav_down" then
			--Switch Cursor
			local new_idx = Gmb_blackjack.cur_idx + 1
			if new_idx > Gmb_blackjack.num_btns - 1 then
				new_idx = 0
			end
			gmb_blackjack_btn_highlight(new_idx)
			Gmb_blackjack.cur_idx = new_idx
			audio_play(GMB_BLACKJACK_AUDIO.NAV)
		elseif event == "select" then
			--Do the button action
			gmb_blackjack_btn_action(Gmb_blackjack.cur_idx)
			audio_play(GMB_BLACKJACK_AUDIO.SELECT)
		end
	end

	if event == "back" then
		gmb_blackjack_action_quit()
	end

	--No where to pause
	if event == "pause" then
		dialog_open_pause_display()
	end

end

Gmb_blackjack.deal_queue = {}
Gmb_blackjack.hands = {}

--=================================
--Initializes table
--==================================
function gmb_blackjack_table_init()
	gmb_blackjack_clear_deal_queue()
	gmb_blackjack_hand_init()
	gmb_blackjack_hand_info_update(0, 0)
	gmb_blackjack_hand_info_update(1, 0)
	gmb_blackjack_hand_info_update(2, 0)

	vint_set_property(Gmb_blackjack.handles.winnings, "visible", false)
end

--==================================
--Deal First
--==================================
function gmb_blackjack_deal_first()
	gmb_blackjack_clear_deal_queue()
	gmb_blackjack_hand_init()	--Initialize Hand data
	vint_dataresponder_request("blackjack_responder", "gmb_blackjack_deal_cb", 0, 2)
	Gmb_blackjack.first_deal = true
	gmb_blackjack_process_deal()
end

function gmb_blackjack_clear_deal_queue()
	--Clear Deal queue
	Gmb_blackjack.deal_queue = {}
	Gmb_blackjack.deal_queue.cards_to_deal = 0
end

function gmb_blackjack_hand_init()
	--Clear and initialize hand data
	Gmb_blackjack.hands = {}
	Gmb_blackjack.hands[0] = {}
	Gmb_blackjack.hands[1] = {}
	Gmb_blackjack.hands[2] = {}
	Gmb_blackjack.hands[0].cur_card_idx = 0
	Gmb_blackjack.hands[1].cur_card_idx = 0
	Gmb_blackjack.hands[2].cur_card_idx = 0
	Gmb_blackjack.hands[0].cards = {}
	Gmb_blackjack.hands[1].cards = {}
	Gmb_blackjack.hands[2].cards = {}

	--Remove cards from hands
	local has_children = true
	local child_h
	for i = 0, 2 do
		while has_children do
			--Find first child of hand elements
			child_h = vint_object_first_child(Gmb_blackjack.handles.card_sets[i])
			if child_h ~= nil then
				--Still has a child so destroy it
				vint_object_destroy(child_h)
			else
				has_children = false
			end
		end
		has_children = true
	end

	--clear out hand selector info
	if Gmb_blackjack.handles.split_ind_clone ~= nil then
		vint_object_destroy(Gmb_blackjack.handles.split_ind_clone)
	end

	if Gmb_blackjack.handles.split_anim_clone ~= nil then
		vint_object_destroy(Gmb_blackjack.handles.split_anim_clone)
	end
end

function gmb_blackjack_deal_cb(cb_type, param1, param2, param3, param4, param5)
	--This function basically queues up all the data for processing and displaying later

	if cb_type == 0 then
		--Store hand info for processing
		local hand_owner = param1
		Gmb_blackjack.deal_queue[hand_owner] = {}
		Gmb_blackjack.deal_queue[hand_owner].hand_result = param2
		Gmb_blackjack.deal_queue[hand_owner].value_of_hand = param3
		Gmb_blackjack.deal_queue[hand_owner].num_cards = param4
		Gmb_blackjack.deal_queue[hand_owner].is_active = param5
		Gmb_blackjack.deal_queue[hand_owner].cards = {}
		--[[
		--Debug spew
		debug_print("vint", "HAND DATA\n")
		debug_print("vint", " hand_owner" .. var_to_string(hand_owner) .. "\n")
		debug_print("vint", " Hand hand_result" .. var_to_string(param2) .. "\n")
		debug_print("vint", " value_of_hand" .. var_to_string(param3) .. "\n")
		debug_print("vint", " num_cards" .. var_to_string(param4) .. "\n")
		debug_print("vint", " is_active" .. var_to_string(param5) .. "\n")
		]]
	elseif cb_type == 1 then
		--Card Info
		local hand_owner = param1
		local card_index = param2

		--Store Cards Into player Info
		Gmb_blackjack.deal_queue[hand_owner].cards[card_index] = {}
		Gmb_blackjack.deal_queue[hand_owner].cards[card_index].card_value = param3
		Gmb_blackjack.deal_queue[hand_owner].cards[card_index].card_suit = param4
		Gmb_blackjack.deal_queue[hand_owner].cards[card_index].face_down = param5

		--Increment the amount of cards we have to deal
		Gmb_blackjack.deal_queue.cards_to_deal = Gmb_blackjack.deal_queue.cards_to_deal + 1

		--[[
		debug_print("vint", "CARD DATA\n")
		debug_print("vint", " Hand owner" .. var_to_string(hand_owner) .. "\n")
		debug_print("vint", " Card_index" .. var_to_string(card_index) .. "\n")
		debug_print("vint", " Card_value" .. var_to_string(param3) .. "\n")
		debug_print("vint", " Card_suit" .. var_to_string(param4) .. "\n")
		debug_print("vint", " Face_down" .. var_to_string(param5) .. "\n")
		]]

	elseif cb_type == 2 then

		--Game Status
		Gmb_blackjack.deal_queue.game_status = {}
		Gmb_blackjack.deal_queue.game_status.game_status = param1
		Gmb_blackjack.deal_queue.game_status.winning_type = param2
		Gmb_blackjack.deal_queue.game_status.winnings = param3
		Gmb_blackjack.deal_queue.game_status.bet = param4
		--[[
		debug_print("vint", "Game_status: " .. var_to_string(Gmb_blackjack.deal_queue.game_status.game_status) .. "\n")
		debug_print("vint", " Winning_type: " .. var_to_string(Gmb_blackjack.deal_queue.game_status.winning_type) .. "\n")
		debug_print("vint", " Winnings: " .. var_to_string(Gmb_blackjack.deal_queue.game_status.winnings)  .. "\n")
		]]
	end
end


function gmb_blackjack_process_deal()

	--Deal cards first?

	--Need to go back and forth between the player and the dealer
	local cur_card_set = 0

	--calculate how many cards to deal?
	local cards_to_deal

	--Destroy all buttons
	gmb_blackjack_btns_clear()

	--Display the cards on the table
	local card_x_offset = 28
	local current_hand = GMB_PLAYER_ENUMS.PLAYER_HAND
	local card_h
	local card_value, card_suit, face_down, card_number
	local cur_card
	local is_split = false 		--Is the current set a split hand?

	local hands_to_deal = 2
	if Gmb_blackjack.deal_queue[GMB_PLAYER_ENUMS.SPLIT_HAND] ~= nil then
		is_split = true
		hands_to_deal = 3
	end

	for i = 0, hands_to_deal - 1 do
		current_hand = i
		local card_num = 0

		--Clear out old cards
		if Gmb_blackjack.hands[current_hand].cards ~= nil then
			for idx, val in Gmb_blackjack.hands[current_hand].cards do
				vint_object_destroy(val)
				--Store previous card data for display information
				Gmb_blackjack.hands[current_hand].prev_card_idx = Gmb_blackjack.hands[current_hand].cur_card_idx
			end
			Gmb_blackjack.hands[current_hand].cards = {}
		end

		for idx, val in Gmb_blackjack.deal_queue[current_hand].cards do
			card_value = val.card_value
			card_suit = val.card_suit
			face_down = val.face_down

			--Clone proper card and set it in the right hand
			if face_down == true then
				card_h = vint_object_clone(Gmb_blackjack.handles.cards[GMB_SUIT_ENUMS.BLANK])
			else
				card_h = vint_object_clone(Gmb_blackjack.handles.cards[card_suit])
			end

			vint_object_set_parent(card_h, Gmb_blackjack.handles.card_sets[current_hand])
			vint_set_property(card_h, "depth", idx * -1)

			--Resolve the card number for the card
			if GMB_CARD_ENUMS[card_value] ~= nil then
				--Use specified string for the enum
				card_number = GMB_CARD_ENUMS[card_value]
			else
				--Use normal number
				card_number = card_value
			end

			if face_down == false then
				--Only set the card information if the card is face down
				local card_num_1_h = vint_object_find("card_num_1", card_h)
				local card_num_2_h = vint_object_find("card_num_2", card_h)
				vint_set_property(card_num_1_h, "text_tag", card_number)
				vint_set_property(card_num_2_h, "text_tag", card_number)
			end

			--Set positions
			vint_set_property(card_h, "anchor", idx * card_x_offset, 0)

			card_num = card_num + 1
			Gmb_blackjack.hands[current_hand].cards[idx] = card_h
			Gmb_blackjack.hands[current_hand].cur_card_idx = Gmb_blackjack.hands[current_hand].cur_card_idx + 1
		end

		--If there is a split hand draw the highligh indicator and add it to the card pile.
		if is_split == true then
			if Gmb_blackjack.deal_queue[current_hand].is_active == true then

				--debug_print("vint", "ACTIVE HAND: " .. current_hand .. "\n")
				--debug_print("vint", "card_num: " .. card_num .. "\n")


				local split_ind_h = vint_object_clone(Gmb_blackjack.handles.split_ind )
				local split_anim_h = vint_object_clone(Gmb_blackjack.handles.card_select)

				vint_object_set_parent(split_ind_h, Gmb_blackjack.handles.card_sets[current_hand])
				vint_set_property(split_ind_h, "depth", card_num * -1)
				vint_set_property(split_anim_h, "target_handle", split_ind_h)

				--Set positions
				vint_set_property(split_ind_h, "anchor", card_num * card_x_offset, 0)
				vint_set_property(split_ind_h, "visible", true)

				Gmb_blackjack.handles.split_ind_clone = split_ind_h
				Gmb_blackjack.handles.split_anim_clone = split_anim_h

				Gmb_blackjack.hands[current_hand].cards[card_num] = split_ind_h
				Gmb_blackjack.hands[current_hand].cards[card_num + 1] = split_anim_h
				card_num = card_num + 1
			end
		end
	end

	--Animate cards in:**HACKED**
	if Gmb_blackjack.first_deal == true then

		--hide hand info of the first player
		gmb_blackjack_hand_info_visible(1, false)

		--dealer card 1
		gmb_blackjack_card_set_fade(0, Gmb_blackjack.hands[1].cards[0])

		--player card 1
		gmb_blackjack_card_set_fade(1, Gmb_blackjack.hands[0].cards[0])

		--Dealer card 2
		gmb_blackjack_card_set_fade(2, Gmb_blackjack.hands[1].cards[1])

		--Player card 2
		gmb_blackjack_card_set_fade(3, Gmb_blackjack.hands[0].cards[1])

		--Set callback of master tween
		vint_set_property(Gmb_blackjack.anims.card_twn_fade_in, "end_event", "gmb_blackjack_cards_complete")

		--Set callback of master tween ot fire after last tween
		vint_set_property(Gmb_blackjack.anims.card_twn_fade_in, "start_time", 4 * .2)

		--Fade in cards
		lua_play_anim(Gmb_blackjack.anims.cards_fade, 0)

		Gmb_blackjack.first_deal = false
	else
		--Update hand info immediatly
		gmb_blackjack_hand_info_update_all()

		--Update gamestatus
		gmb_blackjack_game_status_update()
		--Just play sound of card poping in.
		audio_play(GMB_BLACKJACK_AUDIO.DEAL_CARD)
	end


	--Update Bet
	 gmb_blackjack_bet_update(Gmb_blackjack.deal_queue.game_status.bet)
end

--=================================
--
--=================================

function gmb_blackjack_game_status_update()
		--TODO: This might need to happen after the animations fly in...
	--Set button state
	local game_status = Gmb_blackjack.deal_queue.game_status.game_status
	if	game_status == 0 then
		--Continue playing
		gmb_blackjack_screen_state_set(GMB_INPUT_STATES.CONTINUE)
	elseif game_status == 1 then
		--Can split
		gmb_blackjack_screen_state_set(GMB_INPUT_STATES.CONTINUE_SPLIT)
	elseif game_status == 2 then
		--Can double down
		gmb_blackjack_screen_state_set(GMB_INPUT_STATES.CONTINUE_DOUBLEDOWN)
	elseif game_status == 3 then
		--Game Over man
		gmb_blackjack_screen_state_set(GMB_INPUT_STATES.FINISHED)
	end

	--Update Round status only if game is over
	if Gmb_blackjack.deal_queue.game_status.game_status == 3 then
		gmb_blackjack_winnings_payouts(Gmb_blackjack.deal_queue.game_status.winning_type, Gmb_blackjack.deal_queue.game_status.winnings)

		--Hide split control
		vint_set_property(Gmb_blackjack.handles.cards[GMB_SUIT_ENUMS.SPLIT], "visible", false)
	end

end



--==================================
--Betting
--==================================
function gmb_blackjack_bet_change_cb(callback_num, new_bet)
	--Update betting string in button
	gmb_blackjack_bet_update(new_bet)
end

function gmb_blackjack_bet_update(bet)
	vint_set_property(Gmb_blackjack.handles.btn_bet_cash, "text_tag", "$" .. format_cash(bet))
	Gmb_blackjack.current_bet = bet

	--adjust arrows
	local x, y = vint_get_property(Gmb_blackjack.handles.btn_bet_arrow_left, "anchor")
	local width, height = element_get_actual_size(Gmb_blackjack.handles.btn_bet_cash)
	local cash_x, cash_y = vint_get_property(Gmb_blackjack.handles.btn_bet_cash, "anchor")
	local half_width = width/2 + 5

	local left_x = cash_x - half_width + 5
	local right_x = cash_x + half_width

	vint_set_property(Gmb_blackjack.handles.btn_bet_arrow_left, "anchor", left_x, y)
	vint_set_property(Gmb_blackjack.handles.btn_bet_arrow_right, "anchor", right_x, y)
end

function gmb_blackjack_bet_show_arrows(visible)
	if visible == true then
		vint_set_property(Gmb_blackjack.handles.btn_bet_arrow_right, "visible", true)
		vint_set_property(Gmb_blackjack.handles.btn_bet_arrow_left, "visible", true)
		vint_set_property(Gmb_blackjack.handles.btn_bet_cash, "tint", 0.7725, 0.7961, 0.814)
	else
		vint_set_property(Gmb_blackjack.handles.btn_bet_arrow_right, "visible", false)
		vint_set_property(Gmb_blackjack.handles.btn_bet_arrow_left, "visible", false)
		vint_set_property(Gmb_blackjack.handles.btn_bet_cash, "tint", 0.6235, 0.6353, 0.644)
	end
end

--=================================
--Screenstate Set
--=================================
function gmb_blackjack_screen_state_set(state)

	--Make sure the buttons are initialized/cleared
	gmb_blackjack_btns_clear()

	--Reset cursor index
	Gmb_blackjack.cur_idx = 0

	--Hide betting arrows if we aren't in bet mode
	if state ~= GMB_INPUT_STATES.BET then

		gmb_blackjack_bet_show_arrows(false)
	end

	if state == GMB_INPUT_STATES.BET then
		gmb_blackjack_btn_create(false, "DIVERSION_BLACKJACK_DEAL", nil, gmb_blackjack_action_deal)
		gmb_blackjack_btn_highlight(Gmb_blackjack.cur_idx)

		--Show betting arrows
		gmb_blackjack_bet_show_arrows(true)

	elseif state == GMB_INPUT_STATES.CONTINUE then
		gmb_blackjack_btn_create(false, "DIVERSION_BLACKJACK_HIT", nil, gmb_blackjack_action_hit)
		gmb_blackjack_btn_create(false, "DIVERSION_BLACKJACK_STAND", nil, gmb_blackjack_action_stand)
		gmb_blackjack_btn_highlight(Gmb_blackjack.cur_idx)

	elseif state == GMB_INPUT_STATES.CONTINUE_SPLIT then
		gmb_blackjack_btn_create(false, "DIVERSION_BLACKJACK_HIT", nil, gmb_blackjack_action_hit)
		gmb_blackjack_btn_create(false, "DIVERSION_BLACKJACK_SPLIT", nil, gmb_blackjack_action_split)
		gmb_blackjack_btn_create(false, "DIVERSION_BLACKJACK_STAND", nil, gmb_blackjack_action_stand)
		gmb_blackjack_btn_highlight(Gmb_blackjack.cur_idx)

	elseif state == GMB_INPUT_STATES.CONTINUE_DOUBLEDOWN then
		gmb_blackjack_btn_create(false, "DIVERSION_BLACKJACK_HIT", nil, gmb_blackjack_action_hit)
		gmb_blackjack_btn_create(true, "DIVERSION_BLACKJACK_DOUBLEDOWN_LINE1", "DIVERSION_BLACKJACK_DOUBLEDOWN_LINE2", gmb_blackjack_action_doubledown)
		gmb_blackjack_btn_create(false, "DIVERSION_BLACKJACK_STAND", nil, gmb_blackjack_action_stand)
		gmb_blackjack_btn_highlight(Gmb_blackjack.cur_idx)

	elseif state == GMB_INPUT_STATES.FINISHED then
		gmb_blackjack_btn_create(true, "DIVERSION_BLACKJACK_NEWGAME_LINE1", "DIVERSION_BLACKJACK_NEWGAME_LINE2", gmb_blackjack_action_newgame)
		gmb_blackjack_btn_create(false, "DIVERSION_BLACKJACK_QUIT", nil, gmb_blackjack_action_quit)
		gmb_blackjack_btn_highlight(Gmb_blackjack.cur_idx)
	end

	--Set input state
	Gmb_blackjack.input_state = state
end


Gmb_blackjack.btns = {}
--=================================
--Setting up buttons/Controls
--=================================
function gmb_blackjack_btn_create(is_double_btn, text1, text2, action)
	local base_btn
	local btn_height

	if is_double_btn then
		base_btn = vint_object_find("btn_2_line")
		btn_height = 80
	else
		base_btn = vint_object_find("btn_1_line")
		btn_height = 52
	end

	local h = vint_object_clone(base_btn)
	local highlight_h = vint_object_find("highlight", h)

	--Position button
	local x = 0
	local y = 0
	if Gmb_blackjack.num_btns > 0 then
		y = Gmb_blackjack.btns[Gmb_blackjack.num_btns - 1].y + Gmb_blackjack.btns[Gmb_blackjack.num_btns - 1].height + 5
	end
	vint_set_property(h, "anchor", x, y)

	--Set Text and resize if text is too big.
	local text_1_h, text_2_h, width, height
	local max_text_width = 150
	if is_double_btn then
		text_1_h = vint_object_find("text_1", h)
		vint_set_property(text_1_h, "text_tag", text1)
		text_2_h = vint_object_find("text_2", h)
		vint_set_property(text_2_h, "text_tag", text2)

		--Reset Text Sizes
		gmb_blackjack_btn_text_size(text_1_h, max_text_width)
		gmb_blackjack_btn_text_size(text_2_h, max_text_width)
	else
		text_1_h = vint_object_find("text_1", h)
		vint_set_property(text_1_h, "text_tag", text1)
		--Reset Text Sizes
		gmb_blackjack_btn_text_size(text_1_h, max_text_width)
	end

	--Store data
	Gmb_blackjack.btns[Gmb_blackjack.num_btns] = {}
	Gmb_blackjack.btns[Gmb_blackjack.num_btns].btn_h = h
	Gmb_blackjack.btns[Gmb_blackjack.num_btns].highlight_h = highlight_h
	Gmb_blackjack.btns[Gmb_blackjack.num_btns].height = btn_height
	Gmb_blackjack.btns[Gmb_blackjack.num_btns].y = y
	Gmb_blackjack.btns[Gmb_blackjack.num_btns].action = action
	Gmb_blackjack.btns[Gmb_blackjack.num_btns].text_1_h = text_1_h
	Gmb_blackjack.btns[Gmb_blackjack.num_btns].text_2_h = text_2_h
	Gmb_blackjack.num_btns = Gmb_blackjack.num_btns + 1
end

function gmb_blackjack_btn_text_size(text_h, max_text_width)
	--Resizes text if we are over a max length
	local width, height = element_get_actual_size(text_h)

	if width > max_text_width then
		local scale_x, scale_y = vint_get_property(text_h, "scale")
		local scale =  max_text_width / width
		vint_set_property(text_h, "scale", scale , scale )

		--debug_print("vint", "scale: " .. scale .. "\n")
	end
end


function gmb_blackjack_btn_highlight(idx)
	vint_set_property(Gmb_blackjack.handles.glow_btn_twn, "target_handle", Gmb_blackjack.btns[idx].highlight_h)
	--change the animation target, then change the buttons back to normal
	for idx, val in Gmb_blackjack.btns do
		vint_set_property(val.highlight_h, "visible", false)
		vint_set_property(val.text_1_h, "tint", .77, .8, .81)
		vint_set_property(val.text_2_h, "tint", .77, .8, .81)
		vint_set_property(val.btn_h, "tint", 1, 1, 1)
	end
	--highlight the correct button
	vint_set_property(Gmb_blackjack.btns[idx].highlight_h, "visible", true)
	vint_set_property(Gmb_blackjack.btns[idx].text_1_h, "tint", .9, .74, .05)
	vint_set_property(Gmb_blackjack.btns[idx].text_2_h, "tint", .9, .74, .05)

end

function gmb_blackjack_btns_clear()
	--Clear out actual buttons
	for idx, val in Gmb_blackjack.btns do
		vint_object_destroy(val.btn_h)
	end

	--Reset data
	Gmb_blackjack.btns = {}
	Gmb_blackjack.num_btns = 0
end

function gmb_blackjack_btn_action(idx)
	local action = Gmb_blackjack.btns[idx].action
	action()
end

--=================================
--Button actions
--=================================
function gmb_blackjack_action_deal()

	--Deal CB
	gmb_blackjack_clear_deal_queue()
	vint_dataresponder_request("blackjack_responder", "gmb_blackjack_deal_cb", 0, 2)
	gmb_blackjack_process_deal()
end

function gmb_blackjack_action_hit()
	--Hit CB
	gmb_blackjack_clear_deal_queue()
	vint_dataresponder_request("blackjack_responder", "gmb_blackjack_deal_cb", 0, 3)
	gmb_blackjack_process_deal()
end

function gmb_blackjack_action_stand()
	--Stand CB
	gmb_blackjack_clear_deal_queue()
	vint_dataresponder_request("blackjack_responder", "gmb_blackjack_deal_cb", 0, 4)
	gmb_blackjack_process_deal()
end

function gmb_blackjack_action_doubledown()
	--Double Down CB
	gmb_blackjack_clear_deal_queue()
	vint_dataresponder_request("blackjack_responder", "gmb_blackjack_deal_cb", 0, 5)
	gmb_blackjack_process_deal()
end

function gmb_blackjack_action_split()
	--Split CB
	gmb_blackjack_clear_deal_queue()
	vint_dataresponder_request("blackjack_responder", "gmb_blackjack_deal_cb", 0, 6)
	gmb_blackjack_process_deal()
end

function gmb_blackjack_action_newgame()
	gmb_blackjack_table_init()
	vint_dataresponder_request("blackjack_responder", "gmb_blackjack_newgame_cb", 0, 7)
end

function gmb_blackjack_action_quit()
	--quit game dialog
	if (Gmb_blackjack.input_state == GMB_INPUT_STATES.BET) or (Gmb_blackjack.input_state == GMB_INPUT_STATES.FINISHED) then
		-- quit without dialog [nclok1405]
		gmb_blackjack_quit_dialog_cb(0, DIALOG_ACTION_CLOSE)
	else
		-- Show confirm dialog when still playing the game
		dialog_box_confirmation("DIVERSION_BLACKJACK_DIALOG_QUIT_HEADER", "DIVERSION_BLACKJACK_DIALOG_QUIT_BODY", "gmb_blackjack_quit_dialog_cb")
	end
end


--=================================
--New Game Updates
--======================

function gmb_blackjack_newgame_cb()
	--debug_print("vint", "gmb_blackjack_newgame_cb()\n")
	--Increment and decrement bet to reset the bet
	vint_dataresponder_request("blackjack_responder", "gmb_blackjack_bet_change_cb", 0, 1)
	vint_dataresponder_request("blackjack_responder", "gmb_blackjack_bet_change_cb", 0, 0)
	gmb_blackjack_screen_state_set(GMB_INPUT_STATES.BET)
end

--================================
--DIALOG BOXES
--================================
function gmb_blackjack_quit_dialog_cb(result, action)
	if action ~= DIALOG_ACTION_CLOSE then
		return
	end
	if result == 0 then

		vint_document_unload(vint_document_find("gmb_blackjack"))
		--Quit Request to game
		vint_dataresponder_request("blackjack_responder", "gmb_blackjack_quit_confirm", 0, 8)
	else
		--do nothing
	end
end

function gmb_blackjack_quit_confirm()
end

function gmb_blackjack_not_enough_cash_dialog()
	dialog_box_message("GAMBLING_POKER_DIALOG_NO_CASH_HEADER","GAMBLING_POKER_DIALOG_NO_CASH_BODY")
end

function gmb_poker_quit_dialog_cb(result, action)

end


--=================================
--Hand Info Updates
--=================================
function gmb_blackjack_hand_info_update_all()
	--Can only be called during a deal queue
	--UPDATE HAND INFO
	for i = 0, 2 do
		if Gmb_blackjack.deal_queue[i] ~= nil then

			local value_of_hand = Gmb_blackjack.deal_queue[i].value_of_hand
			local hand_result = Gmb_blackjack.deal_queue[i].hand_result
			local hand_string = value_of_hand

			--If the hand values are within a certain range then set the value
			--to a specified string defined by an enum in C
			if hand_result > 2 then
				hand_string  = GMB_HAND_VALUES[hand_result]
			end

			--Update value of each hand
			gmb_blackjack_hand_info_update(i, hand_string)
		end
	end
end

function gmb_blackjack_hand_info_update(hand_enum, value)
	local box_h = Gmb_blackjack.handles.hand_values[hand_enum]
	local text_h = vint_object_find("card_value_txt", box_h)

	local offset_x, offset_y = vint_get_property(box_h, "anchor")

	local height = -1

	local str = "" .. value
	if value ~= 0 then
		vint_set_property(box_h, "visible", true)
		vint_set_property(text_h, "text_tag", "" .. str)

		--update parts of box
		local width, height = element_get_actual_size(text_h)

		local m_h = vint_object_find("mid", box_h)
		local e_h = vint_object_find("e", box_h)
		local ne_h = vint_object_find("ne", box_h)
		local se_h = vint_object_find("se", box_h)
		local n_h = vint_object_find("n", box_h)
		local s_h = vint_object_find("s", box_h)
		local sw_h = vint_object_find("sw", box_h)
		local w_h = vint_object_find("w", box_h)

		--mid
		local m_width, m_height = element_get_actual_size(m_h)
		local se_x, se_y = vint_get_property(n_h, "source_se")

		--Floor & Cheat Width/Height Values
		m_width = floor(m_width)
		m_height = floor(m_height)
		width = floor(width) - 9
		height = floor(height)

		element_set_actual_size(m_h, width, height - 18)

		--North
		vint_set_property(n_h, "source_se", width, se_y)

		--South
		local se_x, se_y = vint_get_property(s_h, "source_se")
		vint_set_property(s_h, "source_se", width, se_y)

		--North East
		local x, y = vint_get_property(n_h, "anchor")
		vint_set_property(ne_h, "anchor", x + width, y)

		--East
		x, y = vint_get_property(m_h, "anchor")
		vint_set_property(e_h, "anchor", x + width, y)

		--East + West Anchors
		vint_set_property(e_h, "source_se", 24, height - 18)
		vint_set_property(w_h, "source_se", 24, height - 18)

		--South East
		x, y = vint_get_property(s_h, "anchor")
		vint_set_property(se_h, "anchor", x + width, floor(height))
		vint_set_property(s_h, "anchor", x, floor(height))
		vint_set_property(sw_h, "anchor", -6, floor(height))

		if height > 36 then
			vint_set_property(box_h, "anchor", offset_x, offset_y - 35)
		end

	else
		--debug_print("vint", "false, dont show hand info \n")
		vint_set_property(box_h, "visible", false)
	end

end

function gmb_blackjack_hand_info_visible(hand_enum, is_visible)
	--debug_print("vint", "gmb_blackjack_hand_info_visible \n")
	local box_h = Gmb_blackjack.handles.hand_values[hand_enum]
	vint_set_property(box_h, "visible", false)

	local text_h = vint_object_find("card_value_txt", box_h)
	local width, height = element_get_actual_size(text_h)

	local offset_x, offset_y = vint_get_property(box_h, "anchor")

	if height > 36 then
		vint_set_property(box_h, "anchor", offset_x, offset_y + 35)
	end
end

--=================================
--Winning Payouts
--==================================
function gmb_blackjack_winnings_payouts(game_state_enum, dollars_winnings)

	local winning_str

	--Game is over so we need to display round status.
	if game_state_enum == 0 then
		winning_str = "DIVERSION_BLACKJACK_LOSE"
	elseif game_state_enum == 1 then
		winning_str = "DIVERSION_BLACKJACK_WIN"
	elseif game_state_enum == 2 then
		winning_str = "DIVERSION_BLACKJACK_PUSH"
	end

	--Set text of winnings payout
	vint_set_property(Gmb_blackjack.handles.winnings_type, "text_tag", winning_str)
	vint_set_property(Gmb_blackjack.handles.winnings_cash, "text_tag", "$" .. format_cash(dollars_winnings))

	local t_width, t_height = element_get_actual_size(Gmb_blackjack.handles.winnings_type)
	local c_width, c_height = element_get_actual_size(Gmb_blackjack.handles.winnings_cash)
	local width, height
	if t_width > c_width then
		width = t_width
		height = t_height
	else
		width = c_width
		height = c_height
	end

	--Width calculations for setting the background box
	width = floor(width)
	height = floor(height)
	local x = floor(width/2)
	local y = floor(height/2)
	local box_shrink = 36

	local x_minus, y_minus
	x_minus = x * -1
	y_minus = y * -1

	local source_se_width, source_se_height

	--Set box background based on center
	element_set_actual_size(Gmb_blackjack.handles.winnings_box_c, width, height)

	vint_set_property(Gmb_blackjack.handles.winnings_box_nw, "anchor", x_minus, y_minus)
	vint_set_property(Gmb_blackjack.handles.winnings_box_n, "anchor", x_minus, y_minus)

	source_se_width, source_se_height = vint_get_property(Gmb_blackjack.handles.winnings_box_n, "source_se")

	if dollars_winnings == 0 then
		vint_set_property(Gmb_blackjack.handles.winnings_cash, "visible", false)
		vint_set_property(Gmb_blackjack.handles.winnings_box_c, "source_se", source_se_width, 8)
	else
		vint_set_property(Gmb_blackjack.handles.winnings_cash, "visible", true)
		vint_set_property(Gmb_blackjack.handles.winnings_box_c, "source_se", source_se_width, height)
		box_shrink = 0
	end

	vint_set_property(Gmb_blackjack.handles.winnings_box_n, "source_se", width, source_se_height)
	vint_set_property(Gmb_blackjack.handles.winnings_box_ne, "anchor", x, y_minus)

	vint_set_property(Gmb_blackjack.handles.winnings_box_w, "anchor", x_minus, y_minus)
	vint_set_property(Gmb_blackjack.handles.winnings_box_w, "source_se", width, height - box_shrink)
	vint_set_property(Gmb_blackjack.handles.winnings_box_e, "anchor", x, y_minus)
	vint_set_property(Gmb_blackjack.handles.winnings_box_e, "source_se", width, height - box_shrink)

	vint_set_property(Gmb_blackjack.handles.winnings_box_sw, "anchor", x_minus, y - box_shrink)
	vint_set_property(Gmb_blackjack.handles.winnings_box_s, "anchor", x_minus, y - box_shrink)
	vint_set_property(Gmb_blackjack.handles.winnings_box_s, "source_se", width, height - box_shrink)
	vint_set_property(Gmb_blackjack.handles.winnings_box_se, "anchor", x, y - box_shrink)

	if game_state_enum > 0 then
		--Win
		audio_play(GMB_BLACKJACK_AUDIO.WIN)
	else
		--lose
		audio_play(GMB_BLACKJACK_AUDIO.LOSE)
	end

	--Show box
	vint_set_property(Gmb_blackjack.handles.winnings, "visible", true)
end


--=================================
--INPUT BLOCK
--=================================
Gmb_blackjack_input_blocked = 0
function gmb_blackjack_input_block(block)
	if block == true then
		Gmb_blackjack_input_blocked = Gmb_blackjack_input_blocked + 1
	else
		Gmb_blackjack_input_blocked = Gmb_blackjack_input_blocked - 1
	end
end

function gmb_blackjack_input_is_bocked()
	if Gmb_blackjack_input_blocked > 0 then
		return true
	else
		return false
	end
end


--=================================
--Animation Loop Callbacks
--=================================

function gmb_blackjack_loop_cash_anim()
	--Looping callback
	lua_play_anim(Gmb_blackjack.handles.results_anim)
end

--=================================
--CASH UPDATES
--=================================
function gmb_blackjack_cash_update(di_h)
	local cash = vint_dataitem_get(di_h)
	Gmb_blackjack.cash = floor(cash)
end

function gmb_blackjack_process()
	local display_cash = Gmb_blackjack.cash - 1 --Subtract one so it gets formatted in the loop.
	while true do
		thread_yield()
		-- Animate Cash
		if display_cash ~= Gmb_blackjack.cash  then
			local diff_cash = Gmb_blackjack.cash  - display_cash

			if diff_cash > 5 or diff_cash < -5 then
				diff_cash = floor(diff_cash * 0.5)
			end

			display_cash = display_cash + diff_cash
			vint_set_property(Gmb_blackjack.handles.cash, "text_tag", "$" .. format_cash(display_cash))
		end
	end
end

--=================================
--Build fade events for cards)
--=================================
function gmb_blackjack_card_set_fade(card_index, card_h)
	--Create a tween for the card
	local twn_h = vint_object_clone(Gmb_blackjack.anims.card_twn_fade_in)

	--Offset time based on how many cards are delt this round
	vint_set_property(twn_h, "start_time", .2 * card_index)

	--Retarget
	vint_set_property(twn_h, "target_handle", card_h)

	--Hide object
	vint_set_property(card_h, "alpha", 0)
	vint_set_property(twn_h, "start_event", "gmb_blackjack_sound_dead_card")

	Gmb_blackjack.card_twns[twn_h] = true
end



function gmb_blackjack_sound_dead_card()
	audio_play(GMB_BLACKJACK_AUDIO.DEAL_CARD)
end

function gmb_blackjack_cards_complete()
	--clear all the tweens
	for idx, val in Gmb_blackjack.card_twns do
		vint_object_destroy(idx)
	end
	Gmb_blackjack.card_twns = {}

	--Unblock inputs
	gmb_blackjack_input_block(false)

	--show hand info of the first player
	gmb_blackjack_hand_info_update_all()

	--Update game status
	gmb_blackjack_game_status_update()
end

--=================================
--ALIGN BUTTONS
--=================================
function gmb_blackjack_btntips_align()
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
	--debug_print("vint", "btn tips\n")
end

--==================================
--
--==================================
