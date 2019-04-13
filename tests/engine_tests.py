import os, glob
import unittest
from poker_simulations.engine import *
from inspect import getmembers


class CardTests(unittest.TestCase):
    def test_card(self):
        C = Card(2, 'S')
        self.assertTrue(isinstance(C, Card))

    def test_card_errors(self):
        pass

    def test_card_equiv(self):
        c1 = Card(6, 'H')
        c2 = Card(6, 'H')
        self.assertTrue(c1 == c2)

    def test_card_not_equiv(self):
        c1 = Card(6, 'H')
        c2 = Card(6, 'D')
        self.assertTrue(c1 != c2)

    def test_card_greater_than_and_less_than(self):
        c1 = Card(2, 'S')
        c2 = Card(3, 'S')
        self.assertTrue(c2 > c1)
        self.assertTrue(c1 < c2)

    def test_card_greater_than_and_less_than2(self):
        c1 = Card('A', 'S')
        c2 = Card('K', 'S')
        self.assertTrue(c1 > c2)
        self.assertTrue(c2 < c1)


class DeckTests(unittest.TestCase):
    def setUp(self):
        self.D = Deck()
        self.D.shuffle()

    def test_number_of_cards(self):
        self.assertEqual(len(self.D.cards), 52)

    def test_shuffling(self):
        self.assertFalse(self.D == self.D.shuffle())

    def test_shuffling2(self):
        """
        make sure shuffling doesn't happen in
        predictable way
        :return:
        """
        D1 = Deck()
        D2 = Deck()
        self.assertFalse(D1 == D2)

    def test_get_card(self):
        self.assertEqual(Card(5, 'S'), self.D.get(5, 'S'))

    def test_get_card_removed_from_deck(self):
        card = self.D.get(5, 'D')
        self.assertEqual(len(self.D), 51)

    def test_pop(self):
        d = Deck()
        len_before = len(d)
        d.pop()
        len_after = len(d)
        self.assertNotEqual(len_before, len_after)


class StackTests(unittest.TestCase):
    def setUp(self) -> None:
        pass

    def test_add(self):
        c1 = Stack(4.00)
        c2 = Stack(6)
        self.assertEqual(10, c1 + c2)

    def test_add2(self):
        c1 = Stack(4.00)
        c2 = Stack(6)
        self.assertIsInstance(c1 + c2, numpy.float)

    def test_sub1(self):
        c1 = Stack(4.00)
        c2 = Stack(6)
        self.assertEqual(2, c2 - c1)

    def test_sub1(self):
        c1 = Stack(4.00)
        c2 = Stack(6)
        self.assertEqual(2, c1 - c2)


class PlayerTests(unittest.TestCase):
    def setUp(self):
        self.p = [Player(name='player{}'.format(i), stack=1.0,
                         seat=i, position=POSITIONS[i]) for i in range(9)]

    def test_player(self):
        p = Player('Ciaran', 50, 1, 'BTN')
        self.assertIsInstance(p, Player)

    def test_bet(self):
        p = Player('Ciaran', 50, 1, 'BTN')
        print(p.raise_(0.5))


class PlayersTest(unittest.TestCase):
    def setUp(self):
        import numpy
        seats = numpy.linspace(1, 9, num=9)
        shuffle(seats)
        # shuffle(positions)
        p = {}
        for i, pos in POSITIONS.items():
            p[pos] = Player(name='player' + str(i), position=pos, stack=1.0, seat=seats[i - 1])
        self.p = p

        assert self.p['btn'] != self.p['co']

    def test_players_ordered(self):
        p = Players(self.p)
        self.assertGreater(p[7], p[6])

    def test_position1(self):
        p = Players(self.p)
        self.assertEqual(p[0].position, 'btn')

    def test_position4(self):
        p = Players(self.p)
        print(p)
        self.assertEqual(p[3].position, 'utg1')

    def test_position9(self):
        p = Players(self.p)
        self.assertEqual(p[8].position, 'co')

    def test_len(self):
        p = Players(self.p)
        self.assertEqual(len(p), 9)

    def test_iterable_is_dct(self):
        p = Players(self.p)
        self.assertEqual(p['btn'].name, 'player0')

    def test_iter(self):
        p = Players(self.p)

        l = []
        for i in p:
            l.append(i)
        self.assertListEqual(['btn', 'sb', 'bb', 'utg1', 'utg2', 'mp1', 'mp2', 'mp3', 'co'], l)


class GameTests(unittest.TestCase):

    def setUp(self):
        self.p1 = {'name': 'a', 'stack': 100, 'position': 'btn'}
        self.p2 = {'name': 'b', 'stack': 110, 'position': 'sb'}
        self.p3 = {'name': 'c', 'stack': 190, 'position': 'bb'}
        self.p4 = {'name': 'd', 'stack': 140, 'position': 'utg1'}
        self.p5 = {'name': 'e', 'stack': 160, 'position': 'utg2'}
        self.p6 = {'name': 'f', 'stack': 120, 'position': 'mp1'}
        self.p7 = {'name': 'g', 'stack': 110, 'position': 'mp2'}
        self.p8 = {'name': 'h', 'stack': 100, 'position': 'mp3'}
        self.p = [self.p1, self.p2, self.p3, self.p4,
                  self.p5, self.p5, self.p7, self.p8]
        self.p = Players([Player(**i) for i in self.p])

    def test_create_seats1(self):
        g = Game(self.p)
        expected = 140
        self.assertEqual(expected, g.seats[3].stack)

    def test_create_seats2(self):
        g = Game(self.p)
        expected = 'empty'
        self.assertEqual(expected, g.seats[8])

    def test_to_yml(self):
        p = self.p
        t = Table(name='super_poker', players=p)
        game = t.play_game(to='showdown')
        self.assertTrue('players: !Players' in game.to_yaml())

    def test_yaml_load(self):
        string = """players: !Players
  num_players: 8
  iterable:
    btn: !Player
      name: a
      stack: !Stack
        amount: 100
        currency: $
      position: btn
      status: playing
      cards:
      - !Card
        rank: 9
        suit: H
      - !Card
        rank: 6
        suit: D
      hole_cards_hidden: true
    sb: !Player
      name: b
      stack: !Stack
        amount: 110
        currency: $
      position: sb
      status: playing
      cards:
      - !Card
        rank: 4
        suit: D
      - !Card
        rank: 7
        suit: C
      hole_cards_hidden: true
    bb: !Player
      name: c
      stack: !Stack
        amount: 190
        currency: $
      position: bb
      status: playing
      cards:
      - !Card
        rank: Q
        suit: H
      - !Card
        rank: A
        suit: D
      hole_cards_hidden: true
    utg1: !Player
      name: d
      stack: 90.0
      position: utg1
      status: playing
      cards:
      - !Card
        rank: 6
        suit: S
      - !Card
        rank: 6
        suit: C
      hole_cards_hidden: true
    utg2: !Player
      name: e
      stack: !Stack
        amount: 160
        currency: $
      position: utg2
      status: playing
      cards:
      - !Card
        rank: 9
        suit: C
      - !Card
        rank: 8
        suit: D
      hole_cards_hidden: true
    mp1: !Player
      name: e
      stack: !Stack
        amount: 160
        currency: $
      position: utg2
      status: playing
      cards:
      - !Card
        rank: 10
        suit: H
      - !Card
        rank: 5
        suit: C
      hole_cards_hidden: true
    mp2: !Player
      name: g
      stack: !Stack
        amount: 110
        currency: $
      position: mp2
      status: playing
      cards:
      - !Card
        rank: Q
        suit: C
      - !Card
        rank: 2
        suit: S
      hole_cards_hidden: true
    mp3: !Player
      name: h
      stack: !Stack
        amount: 100
        currency: $
      position: mp3
      status: playing
      cards:
      - !Card
        rank: 10
        suit: D
      - !Card
        rank: 7
        suit: H
      hole_cards_hidden: true
pot: 0"""
        y = Yaml()
        print(y.from_yaml(string))

    def test_summary(self):
        t = Table(name='super_poker', players=self.p)
        # game = t.play_game(to='river')
        # print(game)

    # def test_btn(self):
    #     g = Game(self.p)
    #     expected = 'a'
    #     self.assertEqual(expected, g.btn.name)

    # def test_btn_setter(self):
    #     g = Game(self.p)
    #     g.btn = g.players['sb']
    #     print(g.btn)
    #     expected = ''
    #     self.assertEqual(expected, g.btn)

    # def test_deal_Cards(self):
    #     t = Table(self.p)
    #     # print('seats', t.seats)
    #     t.play_game()
    #     # Btn()
    #
    # def test_blinds(self):
    #     g = Game(1, self.p)
    #     g.blinds()
    #     self.assertAlmostEqual(0.15, g.pot)
    #
    # def test_deal(self):
    #     """
    #     The only explaination is that these players are the same object!
    #     :return:
    #     """
    #     g = Game(1, self.p)
    #     g.deal()
    #     for k, v in g.players.items():
    #         self.assertEqual(2, len(v.cards))
    #
    # def test_flop(self):
    #     g = Game(1, self.p)
    #     self.assertEqual(3, len(g.flop))
    #
    # def test_turn(self):
    #     g = Game(1, self.p)
    #     self.assertEqual(1, len(g.turn))
    #
    # def test_river(self):
    #     g = Game(1, self.p)
    #     self.assertEqual(3, len(g.river))
    #
    # def test_correct_num_of_cards(self):
    #     g = Game(1, self.p)
    #     g.deal()  # 18
    #     g.flop()  # 3
    #     g.turn()  # 1
    #     g.river()  # 1
    #     self.assertEqual(52 - 23, len(g.deck))


class TableTests(unittest.TestCase):
    positions = {
        1: 'btn',
        2: 'sb',
        3: 'bb',
        4: 'utg1',
        5: 'utg2',
        6: 'mp1',
        7: 'mp2',
        8: 'mp3',
        9: 'co',
    }

    def setUp(self):
        self.p = [Player(name='player{}'.format(i), stack=1.0,
                         position=self.positions[i]) for i in range(1, 10)]
        self.p = Players(self.p)

    def test_instantiation(self):
        t = Table(name='super_poker', players=self.p)
        self.assertIsInstance(t, Table)

    def test_play_to_flop(self):
        p = self.p
        t = Table(name='super_poker', players=p)
        game = t.play_game(to='flop')
        self.assertNotEqual([], game.game_info.action_history['preflop'])

    def test_play_to_turn(self):
        p = self.p
        t = Table(name='super_poker', players=p)
        game = t.play_game(to='turn')
        self.assertNotEqual([], game.game_info.action_history['flop'])

    def test_play_to_river(self):
        p = self.p
        t = Table(name='super_poker', players=p)
        game = t.play_game(to='river')
        self.assertNotEqual([], game.game_info.action_history['river'])




class DealerTests(unittest.TestCase):

    def setUp(self):
        self.p = {POSITIONS[i]: Player(name='player{}'.format(i), stack=1.0,
                         position=POSITIONS[i]) for i in range(9)}

    def test_deck(self):
        d = Dealer()
        self.assertIsInstance(deque, d.deck)

    def test_deal_holecards(self):
        t = Table(name='super_poker', players=self.p)
        game = t.play_game(to='preflop')
        self.assertEqual(2, len(game.players['btn'].cards))

    def test_deal_flop(self):
        t = Table(name='super_poker', players=self.p)
        game = t.play_game(to='flop')
        self.assertEqual(3, len(game.game_info.community_cards))

    def test_deal_flop(self):
        t = Table(name='super_poker', players=self.p)
        game = t.play_game(to='flop')
        self.assertEqual(3, len(game.game_info.community_cards))

    def test_deal_turn(self):
        t = Table(name='super_poker', players=self.p)
        game = t.play_game(to='turn')
        self.assertEqual(4, len(game.game_info.community_cards))

    def test_deal_river(self):
        t = Table(name='super_poker', players=self.p)
        game = t.play_game(to='river')
        self.assertEqual(5, len(game.game_info.community_cards))


if __name__ == '__main__':
    unittest.main()
