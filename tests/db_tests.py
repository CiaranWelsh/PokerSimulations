import unittest
from poker_simulations import engine, db
from poker_simulations.db import *
from poker_simulations.file_manager import FileManager

FILE_MANAGER = FileManager()


class ZipperTests(unittest.TestCase):

    def setUp(self) -> None:
        d = r'/home/ncw135/Documents/PokerSimulations/data/nl/0.01-0.02/Pacific-NoLimitHoldem-0.01-0.02-Full-Regular-20190106- 0 (0)'
        self.files = glob.glob(os.path.join(d, '*.txt'))

    def test(self):
        for f in self.files:
            z = Zipper().extract()
        print(z)
        # hands = e.read_file(self.files[0])
        # e.parse_hand(hands[0])


class HandParserTests(unittest.TestCase):

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
        h = HandParser(self.hand1)
        self.assertEqual(520860324, h.game_id())

    def test_steaks(self):
        h = HandParser(self.hand1)
        self.assertEqual((0.01, 0.02), h.steaks())

    def test_btn(self):
        h = HandParser(self.hand1)
        self.assertEqual(2, h.button())

    def test_num_players(self):
        h = HandParser(self.hand1)
        self.assertEqual(8, h.number_of_players())

    def test_player_info(self):
        h = HandParser(self.hand1)
        self.assertEqual(3.95, h.player_info()[4]['lilysami'])

    def test_preflop_actions(self):
        h = HandParser(self.hand1)
        self.assertEqual('folds', h.preflop_actions()['Dvg54RUS'][0])

    def test_flop_actions(self):
        h = HandParser(self.hand1)
        self.assertEqual('checks', h.flop_actions()['Kobe24LSB'][0])

    def test_turn_actions(self):
        h = HandParser(self.hand1)
        self.assertEqual('checks', h.turn_actions()['lilysami'][0])

    def test_river_actions(self):
        h = HandParser(self.hand1)
        self.assertEqual(0.06, h.river_actions()['Kobe24LSB'][1])

    def test_showdown_actions(self):
        h = HandParser(self.hand1)
        h.river_actions()
        self.assertEqual('checks', h.turn_actions()['lilysami'][0])

    def test_flop(self):
        h = HandParser(self.hand1)
        self.assertEqual('Qd', h.flop()[2])

    def test_turn(self):
        h = HandParser(self.hand1)
        self.assertEqual('92', h.turn())

    def test_river(self):
        h = HandParser(self.hand1)
        self.assertEqual('Kd', h.river())

    def test_winner(self):
        h = HandParser(self.hand1)
        self.assertEqual(0.15, h.winner()['cash'])

























