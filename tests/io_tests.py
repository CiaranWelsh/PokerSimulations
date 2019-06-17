import unittest
import os, glob
from poker_simulations.engine import *
from poker_simulations.io import *


class ExampleHands:

    def hand5_game_end_at_showdown(self):
        return """PokerStars Hand #197820819683:  Hold'em No Limit ($0.10/$0.25 USD) - 2019/03/06 9:36:05 ET
Table 'Aigyptios' 9-max Seat #9 is the button
Seat 1: marianoboni ($24.75 in chips)
Seat 2: EddieK4 ($9.82 in chips)
Seat 3: Jamex19 ($35.43 in chips)
Seat 4: pocketsplant ($25 in chips)
Seat 5: maxymo722 ($25.05 in chips)
Seat 7: nombraalne1 ($43.53 in chips)
Seat 8: lumen21 ($25 in chips)
Seat 9: shelepova ($32.72 in chips)
marianoboni: posts small blind $0.10
EddieK4: posts big blind $0.25
*** HOLE CARDS ***
Jamex19: raises $0.50 to $0.75
pocketsplant: calls $0.75
maxymo722: folds
nombraalne1: folds
lumen21: folds
shelepova: folds
marianoboni: folds
Pete007poker is disconnected
EddieK4 has timed out
EddieK4: folds
*** FLOP *** [5s 4d 2h]
Jamex19: bets $0.90
pocketsplant: raises $1.65 to $2.55
Jamex19: calls $1.65
*** TURN *** [5s 4d 2h] [4s]
Jamex19: checks
pocketsplant: bets $3.25
Jamex19: calls $3.25
*** RIVER *** [5s 4d 2h 4s] [Ts]
Jamex19: checks
pocketsplant: checks
*** SHOW DOWN ***
Jamex19: shows [8d 8c] (two pair, Eights and Fours)
pocketsplant: mucks hand
Jamex19 collected $12.84 from pot
*** SUMMARY ***
Total pot $13.45 | Rake $0.61
Board [5s 4d 2h 4s Ts]
Seat 1: marianoboni (small blind) folded before Flop
Seat 2: EddieK4 (big blind) folded before Flop
Seat 3: Jamex19 showed [8d 8c] and won ($12.84) with two pair, Eights and Fours
Seat 4: pocketsplant mucked
Seat 5: maxymo722 folded before Flop (didn't bet)
Seat 7: nombraalne1 folded before Flop (didn't bet)
Seat 8: lumen21 folded before Flop (didn't bet)
Seat 9: shelepova (button) folded before Flop (didn't bet)"""

    def hand4_game_end_at_turn(self):
        return """PokerStars Hand #197820364753:  Hold'em No Limit ($0.10/$0.25 USD) - 2019/03/06 9:20:41 ET
Table 'Aigyptios' 9-max Seat #1 is the button
Seat 1: viangsueb ($22.58 in chips)
Seat 2: EddieK4 ($16.56 in chips)
Seat 3: Jamex19 ($25 in chips)
Seat 5: maxymo722 ($25.75 in chips)
Seat 6: Pete007poker ($25.98 in chips)
Seat 7: nombraalne1 ($28.99 in chips)
Seat 8: lumen21 ($25.35 in chips)
Seat 9: shelepova ($24.65 in chips)
EddieK4: posts small blind $0.10
Jamex19: posts big blind $0.25
pocketsplant: sits out
*** HOLE CARDS ***
maxymo722: folds
Pete007poker: folds
nombraalne1: folds
lumen21: raises $0.35 to $0.60
shelepova: folds
viangsueb: raises $1.65 to $2.25
EddieK4: calls $2.15
Jamex19: folds
lumen21: calls $1.65
*** FLOP *** [Qc Kc As]
EddieK4: checks
lumen21: checks
viangsueb: checks
*** TURN *** [Qc Kc As] [2d]
EddieK4: checks
lumen21: checks
viangsueb: checks
*** RIVER *** [Qc Kc As 2d] [3d]
EddieK4: bets $3.34
lumen21: folds
viangsueb: folds
Uncalled bet ($3.34) returned to EddieK4
EddieK4 collected $6.68 from pot
EddieK4: doesn't show hand
*** SUMMARY ***
Total pot $7 | Rake $0.32
Board [Qc Kc As 2d 3d]
Seat 1: viangsueb (button) folded on the River
Seat 2: EddieK4 (small blind) collected ($6.68)
Seat 3: Jamex19 (big blind) folded before Flop
Seat 5: maxymo722 folded before Flop (didn't bet)
Seat 6: Pete007poker folded before Flop (didn't bet)
Seat 7: nombraalne1 folded before Flop (didn't bet)
Seat 8: lumen21 folded on the River
Seat 9: shelepova folded before Flop (didn't bet)"""

    def hand3_game_end_at_turn(self):
        return """PokerStars Hand #197820749782:  Hold'em No Limit ($0.10/$0.25 USD) - 2019/03/06 9:33:45 ET
Table 'Aigyptios' 9-max Seat #5 is the button
Seat 2: EddieK4 ($9.82 in chips)
Seat 3: Jamex19 ($33.50 in chips)
Seat 4: pocketsplant ($25 in chips)
Seat 5: maxymo722 ($25.05 in chips)
Seat 7: nombraalne1 ($42.93 in chips)
Seat 8: lumen21 ($25 in chips)
Seat 9: shelepova ($33.07 in chips)
nombraalne1: posts small blind $0.10
lumen21: posts big blind $0.25
marianoboni: sits out
*** HOLE CARDS ***
shelepova: folds
EddieK4: folds
Jamex19: raises $0.50 to $0.75
pocketsplant: calls $0.75
maxymo722: folds
nombraalne1: folds
Pete007poker is disconnected
lumen21: folds
*** FLOP *** [Kh Td 7c]
Jamex19: bets $1
pocketsplant: calls $1
*** TURN *** [Kh Td 7c] [2s]
Jamex19: bets $3
pocketsplant: folds
Uncalled bet ($3) returned to Jamex19
Jamex19 collected $3.68 from pot
*** SUMMARY ***
Total pot $3.85 | Rake $0.17
Board [Kh Td 7c 2s]
Seat 2: EddieK4 folded before Flop (didn't bet)
Seat 3: Jamex19 collected ($3.68)
Seat 4: pocketsplant folded on the Turn
Seat 5: maxymo722 (button) folded before Flop (didn't bet)
Seat 7: nombraalne1 (small blind) folded before Flop
Seat 8: lumen21 (big blind) folded before Flop
Seat 9: shelepova folded before Flop (didn't bet)"""

    def hand2_game_end_at_flop(self):
        return """PokerStars Hand #197820674744:  Hold'em No Limit ($0.10/$0.25 USD) - 2019/03/06 9:31:14 ET
Table 'Aigyptios' 9-max Seat #2 is the button
Seat 1: viangsueb ($30.34 in chips)
Seat 2: EddieK4 ($9.82 in chips)
Seat 3: Jamex19 ($26.90 in chips)
Seat 4: pocketsplant ($25 in chips)
Seat 5: maxymo722 ($25.40 in chips)
Seat 7: nombraalne1 ($43.18 in chips)
Seat 8: lumen21 ($25 in chips)
Seat 9: shelepova ($33.07 in chips)
Jamex19: posts small blind $0.10
pocketsplant: posts big blind $0.25
*** HOLE CARDS ***
maxymo722: folds
nombraalne1: folds
lumen21: folds
shelepova: folds
viangsueb: raises $0.25 to $0.50
EddieK4: folds
Jamex19: raises $1.50 to $2
pocketsplant: calls $1.75
viangsueb: folds
*** FLOP *** [3s Qh 2d]
Jamex19: checks
Pete007poker is disconnected
pocketsplant: bets $1
Jamex19: folds
Uncalled bet ($1) returned to pocketsplant
pocketsplant collected $4.30 from pot
pocketsplant: doesn't show hand
*** SUMMARY ***
Total pot $4.50 | Rake $0.20
Board [3s Qh 2d]
Seat 1: viangsueb folded before Flop
Seat 2: EddieK4 (button) folded before Flop (didn't bet)
Seat 3: Jamex19 (small blind) folded on the Flop
Seat 4: pocketsplant (big blind) collected ($4.30)
Seat 5: maxymo722 folded before Flop (didn't bet)
Seat 7: nombraalne1 folded before Flop (didn't bet)
Seat 8: lumen21 folded before Flop (didn't bet)
Seat 9: shelepova folded before Flop (didn't bet)"""

    def hand1_game_end_at_preflop(self):
        return """PokerStars Hand #197820736575:  Hold'em No Limit ($0.10/$0.25 USD) - 2019/03/06 9:33:18 ET
Table 'Aigyptios' 9-max Seat #4 is the button
Seat 2: EddieK4 ($9.82 in chips)
Seat 3: Jamex19 ($33.15 in chips)
Seat 4: pocketsplant ($18.61 in chips)
Seat 5: maxymo722 ($25.15 in chips)
Seat 7: nombraalne1 ($43.18 in chips)
Seat 8: lumen21 ($25 in chips)
Seat 9: shelepova ($33.07 in chips)
maxymo722: posts small blind $0.10
nombraalne1: posts big blind $0.25
marianoboni: sits out
*** HOLE CARDS ***
lumen21: folds
shelepova: folds
EddieK4: folds
Jamex19: raises $0.50 to $0.75
pocketsplant: folds
maxymo722: folds
nombraalne1: folds
Uncalled bet ($0.50) returned to Jamex19
Jamex19 collected $0.60 from pot
*** SUMMARY ***
Total pot $0.60 | Rake $0
Seat 2: EddieK4 folded before Flop (didn't bet)
Seat 3: Jamex19 collected ($0.60)
Seat 4: pocketsplant (button) folded before Flop (didn't bet)
Seat 5: maxymo722 (small blind) folded before Flop
Seat 7: nombraalne1 (big blind) folded before Flop
Seat 8: lumen21 folded before Flop (didn't bet)
Seat 9: shelepova folded before Flop (didn't bet)"""


class PokerStarsParserTestsHand1(unittest.TestCase):

    def setUp(self) -> None:
        self.hand = ExampleHands().hand1_game_end_at_preflop()

    def test_re_winner(self):
        h = PokerStarsParser(self.hand)
        actions = re.findall(h._re_winner, self.hand)
        self.assertNotEqual(actions, [])

    def test_regex_vendor(self):
        h = PokerStarsParser(self.hand)
        actions = re.findall(h._re_vendor, self.hand)
        self.assertNotEqual(actions, [])

    def test_game_type(self):
        h = PokerStarsParser(self.hand)
        self.assertListEqual(h.game_type, ['preflop', 'summary'])

    def test__re_game_id(self):
        h = PokerStarsParser(self.hand)
        actions = re.findall(h._re_game_id, self.hand)
        self.assertNotEqual(actions, [])

    def test__re_table_name(self):
        h = PokerStarsParser(self.hand)
        actions = re.findall(h._re_table_name, self.hand)
        self.assertNotEqual(actions, [])

    def test__re_steaks(self):
        h = PokerStarsParser(self.hand)
        actions = re.findall(h._re_steaks, self.hand)
        self.assertNotEqual(actions, [])

    def test__re_datetime(self):
        h = PokerStarsParser(self.hand)
        actions = re.findall(h._re_datetime, self.hand)
        self.assertNotEqual(actions, [])

    def test__re_button(self):
        h = PokerStarsParser(self.hand)
        actions = re.findall(h._re_button, self.hand)
        self.assertNotEqual(actions, [])

    def test__re_number_of_players(self):
        h = PokerStarsParser(self.hand)
        actions = re.findall(h._re_number_of_players, self.hand)
        self.assertNotEqual(actions, [])

    def test__re_head_data(self):
        h = PokerStarsParser(self.hand)
        actions = re.findall(h._re_head_data, self.hand)
        self.assertNotEqual(actions, [])

    def test__re_player_info(self):
        h = PokerStarsParser(self.hand)
        actions = re.findall(h._re_player_info, self.hand)
        self.assertNotEqual(actions, [])

    def test__re_preflop_actions(self):
        h = PokerStarsParser(self.hand)
        actions = re.findall(h._re_preflop_actions, self.hand)
        self.assertNotEqual(actions, [])

    def test__re_flop_actions(self):
        h = PokerStarsParser(self.hand)
        actions = re.findall(h._re_flop_actions, self.hand)
        self.assertEqual(actions, [])

    def test__re_turn_actions(self):
        h = PokerStarsParser(self.hand)
        actions = re.findall(h._re_turn_actions, self.hand)
        self.assertEqual(actions, [])

    def test__re_river_actions(self):
        h = PokerStarsParser(self.hand)
        actions = re.findall(h._re_river_actions, self.hand)
        self.assertEqual(actions, [])

    def test__re_summary(self):
        h = PokerStarsParser(self.hand)
        actions = re.findall(h._re_summary, self.hand)
        self.assertNotEqual(actions, [])

    def test__re_flop(self):
        h = PokerStarsParser(self.hand)
        actions = re.findall(h._re_flop, self.hand)
        self.assertEqual(actions, [])

    def test__re_turn(self):
        h = PokerStarsParser(self.hand)
        actions = re.findall(h._re_turn, self.hand)
        self.assertEqual(actions, [])

    def test__re_river(self):
        h = PokerStarsParser(self.hand)
        actions = re.findall(h._re_river, self.hand)
        self.assertEqual(actions, [])

    def test__re_showdown(self):
        h = PokerStarsParser(self.hand)
        actions = re.findall(h._re_showdown, self.hand)
        self.assertEqual(actions, [])


class PokerStarsParserTestsHand2(PokerStarsParserTestsHand1):

    def setUp(self):
        self.hand = ExampleHands().hand2_game_end_at_flop()

    def test_game_type(self):
        h = PokerStarsParser(self.hand)
        self.assertListEqual(h.game_type, ['preflop', 'flop', 'summary'])

    def test__re_flop(self):
        h = PokerStarsParser(self.hand)
        actions = re.findall(h._re_flop, self.hand)
        self.assertNotEqual([], actions)

    def test__re_flop_actions(self):
        h = PokerStarsParser(self.hand)
        actions = re.findall(h._re_flop_actions, self.hand)
        self.assertNotEqual([], actions)


class PokerStarsParserTestsHand3(PokerStarsParserTestsHand2):

    def setUp(self):
        self.hand = ExampleHands().hand3_game_end_at_turn()

    def test_game_type(self):
        h = PokerStarsParser(self.hand)
        self.assertListEqual(h.game_type, ['preflop', 'flop', 'turn', 'summary'])

    def test__re_turn(self):
        h = PokerStarsParser(self.hand)
        actions = re.findall(h._re_turn, self.hand)
        self.assertNotEqual([], actions)

    def test__re_turn_actions(self):
        h = PokerStarsParser(self.hand)
        actions = re.findall(h._re_turn_actions, self.hand)
        self.assertNotEqual([], actions)


class PokerStarsParserTestsHand4(PokerStarsParserTestsHand3):

    def setUp(self):
        self.hand = ExampleHands().hand4_game_end_at_turn()

    def test_game_type(self):
        h = PokerStarsParser(self.hand)
        self.assertListEqual(h.game_type, ['preflop', 'flop', 'turn', 'river', 'summary'])

    def test__re_river(self):
        h = PokerStarsParser(self.hand)
        actions = re.findall(h._re_river, self.hand)
        self.assertNotEqual([], actions)

    def test__re_river_actions(self):
        h = PokerStarsParser(self.hand)
        actions = re.findall(h._re_river_actions, self.hand)
        print(actions)
        self.assertNotEqual([], actions)


class PokerStarsParserTestsHand5(PokerStarsParserTestsHand4):

    def setUp(self):
        self.hand = ExampleHands().hand5_game_end_at_showdown()

    def test_game_type(self):
        h = PokerStarsParser(self.hand)
        self.assertListEqual(h.game_type, ['preflop', 'flop', 'turn', 'river', 'showdown', 'summary'])

    def test__re_showdown(self):
        h = PokerStarsParser(self.hand)
        actions = re.findall(h._re_river, self.hand)
        self.assertNotEqual([], actions)

    def test__re_river_showdown(self):
        h = PokerStarsParser(self.hand)
        actions = re.findall(h._re_river_actions, self.hand)
        self.assertNotEqual([], actions)


class PokerStarsParserTests(unittest.TestCase):

    def setUp(self):
        self.hand5 = ExampleHands().hand5_game_end_at_showdown()
        self.hand4 = ExampleHands().hand4_game_end_at_turn()

    # def test1(self):
    #     p = PokerStarsParser(self.hand4)
    #     print(p.parse_hand())

    def test_game_id(self):
        h = PokerStarsParser(self.hand5)
        self.assertEqual(197820819683, h.game_id())

    def test_vendor(self):
        h = PokerStarsParser(self.hand4)
        self.assertEqual('PokerStars', h.vendor())

    def test_steaks(self):
        h = PokerStarsParser(self.hand4)
        self.assertEqual((0.1, 0.25), h.steaks())

    def test_btn(self):
        h = PokerStarsParser(self.hand4)
        self.assertEqual(1, h.button())

    def test_num_players(self):
        h = PokerStarsParser(self.hand4)
        self.assertEqual(9, h.number_of_players())

    def test_player_info(self):
        h = PokerStarsParser(self.hand4)
        print('ghftrxtj', h.player_info())
        # self.assertEqual('XOKCABAP3', h.player_info()[9][0])

    def test_blind_info(self):
        h = PokerStarsParser(self.hand4)
        b = h.blind_info()
        self.assertEqual('Jamex19', b['bb']['player'])

    def test_sitting_out(self):
        h = PokerStarsParser(self.hand4)
        sitting_out = h.sitting_out()
        exp = 'pocketsplant'
        self.assertEqual(exp, sitting_out[0])

    def test_preflop_actions(self):
        h = PokerStarsParser(self.hand4)
        self.assertEqual(0.75,
                         h.preflop_actions()['kirillr80'][2])

    def test_flop_actions(self):
        h = PokerStarsParser(self.hand4)
        print(h.flop_actions())
        # self.assertEqual('checks', h.flop_actions()['Kobe24LSB'][0])

    def test_turn_actions(self):
        h = PokerStarsParser(self.hand4)
        self.assertEqual('checks', h.turn_actions()['lilysami'][0])

    def test_river_actions(self):
        h = PokerStarsParser(self.hand4)
        self.assertEqual(0.06, h.river_actions()['Kobe24LSB'][1])

    def test_showdown_actions(self):
        h = PokerStarsParser(self.hand4)
        h.river_actions()
        self.assertEqual('checks', h.turn_actions()['lilysami'][0])

    def test_flop(self):
        h = PokerStarsParser(self.hand4)
        self.assertEqual('Qc', h.flop()[2])

    def test_turn(self):
        h = PokerStarsParser(self.hand4)
        self.assertEqual('92', h.turn())

    def test_river(self):
        h = PokerStarsParser(self.hand4)
        self.assertEqual('Kd', h.river())

    def test_winner(self):
        h = PokerStarsParser(self.hand4)
        self.assertEqual(0.15, h.winner()['cash'])

#todo implement session class