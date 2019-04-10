import unittest
from poker_simulations import engine, db
from poker_simulations.db import *
from poker_simulations.file_manager import FileManager

FILE_MANAGER = FileManager()


class ZipperTests(unittest.TestCase):

    def setUp(self) -> None:
        project_dir = os.path.dirname(os.path.dirname(__file__))
        data_dir = os.path.join(project_dir, 'data')
        assert os.path.isdir(data_dir)
        nl_dir = os.path.join(data_dir, 'nl')
        assert os.path.isdir(nl_dir)
        dire = os.path.join(nl_dir, '0.25-0.50')
        assert os.path.isdir(dire)

        self.files = glob.glob(os.path.join(dire, '*.zip'))

    def test(self):
        for f in self.files:
            print(f)
            z = Zipper().extract()

        # hands = e.read_file(self.files[0])
        # e.parse_hand(hands[0])


class HandParser888Tests(unittest.TestCase):

    def setUp(self) -> None:
        self.hand1 = """#Game No : 520860324
***** 888poker Hand History for Game 520860324 *****
$0.01/$0.02 Blinds No Limit Holdem - *** 05 01 2019 20:57:07
Table Amsterdam 9 Max (Real Money)
Seat 2 is the button
Total number of players : 8
Seat 1: Faria014 ( $1.58 )
Seat 2: Zakarii ( $0.61 )
Seat 4: lilysami ( $3.95 )
Seat 5: Kobe24LSB ( $3.51 )
Seat 6: Dvg54RUS ( $1.78 )
Seat 7: volhv74 ( $2.21 )
Seat 9: Dot2MyDash ( $2.11 )
Seat 10: Orangertang ( $3.36 )
lilysami posts small blind [$0.01]
Kobe24LSB posts big blind [$0.02]
** Dealing down cards **
Dvg54RUS folds
volhv74 folds
Dot2MyDash folds
Orangertang folds
Faria014 folds
Zakarii folds
lilysami calls [$0.01]
Kobe24LSB checks
** Dealing flop ** [ 9d, 7d, Qd ]
lilysami checks
Kobe24LSB checks
** Dealing turn ** [ 9c ]
lilysami checks
Kobe24LSB checks
** Dealing river ** [ Kd ]
lilysami bets [$0.06]
Kobe24LSB calls [$0.06]
** Summary **
lilysami shows [ As, 4d ]
Kobe24LSB mucks [ Kh, 6c ]
lilysami collected [ $0.15 ]"""
        d = r'/home/ncw135/Documents/PokerSimulations/data/nl/0.01-0.02/Pacific-NoLimitHoldem-0.01-0.02-Full-Regular-20190106- 0 (0)'
        self.files = glob.glob(os.path.join(d, '*.txt'))

    def test_game_id(self):
        h = HandParser888(self.hand1)
        self.assertEqual(520860324, h.game_id())

    def test_steaks(self):
        h = HandParser888(self.hand1)
        self.assertEqual((0.01, 0.02), h.steaks())

    def test_btn(self):
        h = HandParser888(self.hand1)
        self.assertEqual(2, h.button())

    def test_num_players(self):
        h = HandParser888(self.hand1)
        self.assertEqual(8, h.number_of_players())

    def test_player_info(self):
        h = HandParser888(self.hand1)
        self.assertEqual(3.95, h.player_info()[4]['lilysami'])

    def test_preflop_actions(self):
        h = HandParser888(self.hand1)
        self.assertEqual('folds', h.preflop_actions()['Dvg54RUS'][0])

    def test_flop_actions(self):
        h = HandParser888(self.hand1)
        self.assertEqual('checks', h.flop_actions()['Kobe24LSB'][0])

    def test_turn_actions(self):
        h = HandParser888(self.hand1)
        self.assertEqual('checks', h.turn_actions()['lilysami'][0])

    def test_river_actions(self):
        h = HandParser888(self.hand1)
        self.assertEqual(0.06, h.river_actions()['Kobe24LSB'][1])

    def test_showdown_actions(self):
        h = HandParser888(self.hand1)
        h.river_actions()
        self.assertEqual('checks', h.turn_actions()['lilysami'][0])

    def test_flop(self):
        h = HandParser888(self.hand1)
        self.assertEqual('Qd', h.flop()[2])

    def test_turn(self):
        h = HandParser888(self.hand1)
        self.assertEqual('92', h.turn())

    def test_river(self):
        h = HandParser888(self.hand1)
        self.assertEqual('Kd', h.river())

    def test_winner(self):
        h = HandParser888(self.hand1)
        self.assertEqual(0.15, h.winner()['cash'])


class HandParserPokerStarsTests(unittest.TestCase):

    def setUp(self) -> None:
        self.hand1 = """PokerStars Hand #197832949072:  Hold'em No Limit ($0.10/$0.25 USD) - 2019/03/06 15:00:39 ET
Table 'Achilles' 9-max Seat #7 is the button
Seat 2: $$$kirillr80 ($7.25 in chips)
Seat 3: The Scandalist ($9.75 in chips)
Seat 5: maxymo722 ($32.32 in chips)
Seat 6: drscoot644 ($22.70 in chips)
Seat 7: é=mc² ($25 in chips)
Seat 8: bvbene211 ($19.75 in chips)
Seat 9: XOKCABAP3 ($20 in chips)
bvbene211: posts small blind $0.10
XOKCABAP3: posts big blind $0.25
Optimistic21: sits out
TregIvan: sits out
*** HOLE CARDS ***
$$$kirillr80: raises $0.50 to $0.75
The Scandalist: calls $0.75
maxymo722: folds
drscoot644: folds
é=mc²: folds
bvbene211: folds
XOKCABAP3: calls $0.50
*** FLOP *** [9s Js Qc]
XOKCABAP3: checks
$$$kirillr80: bets $1
The Scandalist: folds
XOKCABAP3: folds
Uncalled bet ($1) returned to $$$kirillr80
$$$kirillr80 collected $2.24 from pot
$$$kirillr80: doesn't show hand
*** SUMMARY ***
Total pot $2.35 | Rake $0.11
Board [9s Js Qc]
Seat 2: $$$kirillr80 collected ($2.24)
Seat 3: The Scandalist folded on the Flop
Seat 5: maxymo722 folded before Flop (didn't bet)
Seat 6: drscoot644 folded before Flop (didn't bet)
Seat 7: é=mc² (button) folded before Flop (didn't bet)
Seat 8: bvbene211 (small blind) folded before Flop
Seat 9: XOKCABAP3 (big blind) folded on the Flop"""
        d = r'/home/ncw135/Documents/PokerSimulations/data/nl/0.01-0.02/Pacific-NoLimitHoldem-0.01-0.02-Full-Regular-20190106- 0 (0)'
        self.files = glob.glob(os.path.join(d, '*.txt'))

    def test_stage(self):
        h = HandParserPokerStars(self.hand1)
        self.assertFalse(h.stage()['turn'])

    def test_game_id(self):
        h = HandParserPokerStars(self.hand1)
        self.assertEqual(197832949072, h.game_id())

    def test_vendor(self):
        h = HandParserPokerStars(self.hand1)
        self.assertEqual('PokerStars', h.vendor())

    def test_steaks(self):
        h = HandParserPokerStars(self.hand1)
        self.assertEqual((0.1, 0.25), h.steaks())

    def test_btn(self):
        h = HandParserPokerStars(self.hand1)
        self.assertEqual(7, h.button())

    def test_num_players(self):
        h = HandParserPokerStars(self.hand1)
        self.assertEqual(9, h.number_of_players())

    def test_player_info(self):
        h = HandParserPokerStars(self.hand1)
        self.assertEqual('XOKCABAP3', h.player_info()[9][0])

    def test_preflop_actions(self):
        h = HandParserPokerStars(self.hand1)
        self.assertEqual(0.75,
                         h.preflop_actions()['kirillr80'][2])

    def test_flop_actions(self):
        h = HandParserPokerStars(self.hand1)
        print(h.flop_actions())
        # self.assertEqual('checks', h.flop_actions()['Kobe24LSB'][0])

    def test_turn_actions(self):
        h = HandParserPokerStars(self.hand1)
        self.assertEqual('checks', h.turn_actions()['lilysami'][0])

    def test_river_actions(self):
        h = HandParserPokerStars(self.hand1)
        self.assertEqual(0.06, h.river_actions()['Kobe24LSB'][1])

    def test_showdown_actions(self):
        h = HandParserPokerStars(self.hand1)
        h.river_actions()
        self.assertEqual('checks', h.turn_actions()['lilysami'][0])

    def test_flop(self):
        h = HandParserPokerStars(self.hand1)
        self.assertEqual('Qd', h.flop()[2])

    def test_turn(self):
        h = HandParserPokerStars(self.hand1)
        self.assertEqual('92', h.turn())

    def test_river(self):
        h = HandParserPokerStars(self.hand1)
        self.assertEqual('Kd', h.river())

    def test_winner(self):
        h = HandParserPokerStars(self.hand1)
        self.assertEqual(0.15, h.winner()['cash'])
