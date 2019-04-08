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
        self.p = [Player(name='player{}'.format(i), cash=1.0,
                         seat=i, position=self.positions[i]) for i in range(1, 10)]

    def test_instantiation(self):
        t = Table(name='super_poker', players=self.p)
        self.assertIsInstance(t, Table)

    def test_seats_init(self):
        t = Table(name='super_poker', players=self.p)
        for s in t.seats.values():
            self.assertTrue(s.isempty)

    def test_utg1(self):
        t = Table(name='poe', players=self.p)
        self.assertTrue(t.utg1)

    def test_btn(self):
        t = Table(name='poe', players=self.p)
        self.assertTrue(t.btn)

    def test_seat_players(self):
        t = Table(name='super_poker', players=self.p)
        t.seat_players()
        for s in t.seats.values():
            self.assertFalse(s.isempty)

    def test(self):
        t = Table(name='super_poker', players=self.p)
        print(t.play_game())

    def test_blinds(self):
        t = Table(name='super_poker', players=self.p)


class PlayerTests(unittest.TestCase):
    def setUp(self):
        self.p = [Player(name='player{}'.format(i), cash=1.0,
                         seat=i, position=POSITIONS[i]) for i in range(1, 10)]

    def test_player(self):
        p = Player('Ciaran', 50, 1, 'BTN')
        self.assertIsInstance(p, Player)


class PlayersTest(unittest.TestCase):
    def setUp(self):
        import numpy
        seats = numpy.linspace(1, 9, num=9)
        shuffle(seats)
        # shuffle(positions)
        p = {}
        for i, pos in POSITIONS.items():
            p[pos] = Player(name='player'+str(i), position=pos, cash=1.0, seat=seats[i-1])
        self.p = p

        assert self.p['btn'] != self.p['co']

    def test_players_ordered(self):
        p = Players(self.p)
        self.assertGreater(p[7], p[6])

    def test_position1(self):
        p = Players(self.p)
        self.assertEqual(p[1].position, 'btn')

    def test_position4(self):
        p = Players(self.p)
        print(p)
        self.assertEqual(p[4].position, 'utg1')

    def test_position9(self):
        p = Players(self.p)
        self.assertEqual(p[9].position, 'co')

    def test_len(self):
        p = Players(self.p)
        self.assertEqual(len(p), 9)

    def test_iterable_is_dct(self):
        p = Players(self.p)
        self.assertEqual(p['btn'].name, 'player1')

    def test_iter(self):
        p = Players(self.p)

        l = []
        for i in p:
            l.append(i)
        self.assertListEqual(['btn', 'sb', 'bb', 'utg1', 'utg2', 'mp1', 'mp2', 'mp3', 'co'], l)


class GameTests(unittest.TestCase):
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
        self.p = [Player(name='player{}'.format(i), cash=1.0,
                         seat=i, position=self.positions[i]) for i in range(1, 10)]

    def test_positions(self):
        g = Game(1, self.p)
        pos = g.positions()
        self.assertIsInstance(pos, dict)

    def test_blinds(self):
        g = Game(1, self.p)
        g.blinds()
        self.assertAlmostEqual(0.15, g.pot)

    def test_deal(self):
        """
        The only explaination is that these players are the same object!
        :return:
        """
        g = Game(1, self.p)
        g.deal()
        for p in g.players:
            print(p)
        # print(g.players['btn'].cards)


if __name__ == '__main__':
    unittest.main()
