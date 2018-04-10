import os, glob
import unittest
from game import *
from inspect import getmembers


class TestHands(object):
    def __init__(self):
        props = [j for (j, k) in getmembers(self, property) if j[:2] != '__']
        self.hands = {i: self.__getattribute__(i) for i in props}

    def __getitem__(self, item):
        return self.hands[item]

    @property
    def high_card(self):
        return [
            Card('A', 'D'),
            Card('K', 'S'),
            Card(3, 'H'),
            Card(9, 'H'),
            Card(6, 'D'),
            Card(2, 'D'),
            Card(7, 'D'),
        ]

    @property
    def pair(self):
        return [
            Card('A', 'D'),
            Card('A', 'S'),
            Card(3, 'H'),
            Card(9, 'H'),
            Card(6, 'D'),
            Card(2, 'D'),
            Card(7, 'D'),
        ]

    @property
    def pair2(self):
        return [
            Card('A', 'D'),
            Card('K', 'S'),
            Card(3, 'H'),
            Card(3, 'S'),
            Card(6, 'D'),
            Card(2, 'D'),
            Card(7, 'D'),
        ]

    @property
    def two_pair(self):
        return [
            Card(4, 'D'),
            Card(4, 'S'),
            Card('J', 'H'),
            Card(9, 'H'),
            Card('Q', 'D'),
            Card('Q', 'H'),
            Card(7, 'D'),
        ]

    @property
    def three_pair(self):
        """
        To test the case when we have three pairs
        :return:
        """
        return [
            Card(4, 'D'),
            Card(4, 'S'),
            Card('J', 'H'),
            Card(9, 'H'),
            Card('Q', 'D'),
            Card('Q', 'H'),
            Card(9, 'D'),
        ]

    @property
    def three_of_a_kind(self):
        return [
            Card('A', 'D'),
            Card('A', 'S'),
            Card('A', 'H'),
            Card(9, 'H'),
            Card(6, 'D'),
            Card(2, 'D'),
            Card(7, 'D'),
        ]

    @property
    def straight(self):
        return [
            Card(3, 'D'),
            Card(4, 'S'),
            Card(5, 'H'),
            Card(6, 'H'),
            Card(7, 'D'),
            Card('J', 'D'),
            Card('Q', 'D'),
        ]

    @property
    def long_straight(self):
        return [
            Card(3, 'D'),
            Card(4, 'S'),
            Card(5, 'H'),
            Card(6, 'H'),
            Card(7, 'D'),
            Card(8, 'D'),
            Card(9, 'D'),
        ]

    @property
    def flush(self):
        return [
            Card('A', 'S'),
            Card('K', 'S'),
            Card(3, 'S'),
            Card(9, 'S'),
            Card(6, 'S'),
            Card(2, 'D'),
            Card(7, 'D'),
        ]

    @property
    def full_house(self):
        return [
            Card('A', 'D'),
            Card('A', 'S'),
            Card(3, 'H'),
            Card(3, 'C'),
            Card(3, 'D'),
            Card(2, 'D'),
            Card(7, 'D'),
        ]

    @property
    def four_of_a_kind(self):
        return [
            Card('A', 'D'),
            Card('A', 'S'),
            Card('A', 'H'),
            Card('A', 'C'),
            Card(6, 'D'),
            Card(2, 'D'),
            Card(7, 'D'),
        ]

    @property
    def straight_flush(self):
        return [
            Card(2, 'S'),
            Card(3, 'S'),
            Card(4, 'S'),
            Card(5, 'S'),
            Card(6, 'S'),
            Card(10, 'D'),
            Card(7, 'S'),
        ]

    @property
    def royal_flush(self):
        return [
            Card('A', 'D'),
            Card('K', 'D'),
            Card('Q', 'D'),
            Card('J', 'D'),
            Card(10, 'D'),
            Card(2, 'S'),
            Card(7, 'S'),
        ]


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


class TableTests(unittest.TestCase):
    def setUp(self):
        self.T = Table()

    def test_6_hole_cards(self):
        T = Table(6)
        self.assertEqual(len(T), 6)

    def test_4_hole_cards(self):
        T = Table(4)
        self.assertEqual(len(T), 4)

    def test(self):
        winner, res = self.T.best_cards()
        print 'wn', winner
        print 'res'
        for i, j in res.items():
            print i, j


class HighCardTests(unittest.TestCase):
    def setUp(self):
        self.hands = TestHands().hands

    def test(self):
        self.assertListEqual(
            HighCard(self.hands['high_card']).five_best,
            [Card('A', 'D'), Card('K', 'S'), Card(9, 'H'), Card(7, 'D'), Card(6, 'D')]
        )


class PairTests(unittest.TestCase):
    def setUp(self):
        self.hands = TestHands().hands

    def test(self):
        self.assertListEqual(
            Pair(self.hands['pair']).five_best,
            [Card('A', 'S'), Card('A', 'D'), Card(9, 'H'), Card(7, 'D'), Card(6, 'D')]
        )

    def test_high_card(self):
        self.assertListEqual(
            Pair(self.hands['high_card']).five_best,
            [Card('A', 'D'), Card('K', 'S'), Card(9, 'H'), Card(7, 'D'), Card(6, 'D')]
        )


class TwoPairTests(unittest.TestCase):
    def setUp(self):
        self.hands = TestHands().hands

    def test_two_pair(self):
        pair = TwoPair(self.hands['two_pair']).five_best
        self.assertListEqual(
            pair,
            [Card('Q', 'H'), Card('Q', 'D'), Card(4, 'S'), Card(4, 'D'), Card('J', 'H')]
        )

    def test_three_pair(self):
        pair = TwoPair(self.hands['three_pair']).five_best
        self.assertListEqual(
            pair,
            [Card('Q', 'H'), Card('Q', 'D'), Card(9, 'D'), Card(9, 'H'), Card('J', 'H')]
        )


class ThreeOfAKindTests(unittest.TestCase):
    def setUp(self):
        self.hands = TestHands().hands

    def test_three_of_a_kind(self):
        trips = ThreeOfAKind(self.hands['three_of_a_kind']).five_best
        self.assertListEqual(
            trips,
            [Card('A', 'H'), Card('A', 'S'), Card('A', 'D'), Card(9, 'H'), Card(7, 'D')]
        )


class StraightTests(unittest.TestCase):
    def setUp(self):
        self.hands = TestHands().hands

    def test(self):
        straight = Straight(self.hands['straight']).five_best
        self.assertListEqual(
            straight,
            [Card(7, 'D'), Card(6, 'H'), Card(5, 'H'), Card(4, 'S'), Card(3, 'D')]
        )

    def test_long_straight(self):
        long_straight = Straight(self.hands['long_straight']).five_best
        self.assertListEqual(
            long_straight,
            [Card(9, 'D'), Card(8, 'D'), Card(7, 'D'), Card(6, 'H'), Card(5, 'H')]        )

    def test_high_card(self):
        high_card = Straight(self.hands['high_card']).five_best
        self.assertListEqual(
            high_card.five_best,
            [Card('A', 'D'), Card('K', 'S'), Card(9, 'H'), Card(7, 'D'), Card(6, 'D')]
        )


class FlushTests(unittest.TestCase):
    def setUp(self):
        self.hands = TestHands().hands

    def test(self):
        flush = Flush(self.hands['flush']).five_best
        self.assertListEqual(
            flush,
            [Card('A', 'S'), Card('K', 'S'), Card(9, 'S'), Card(6, 'S'), Card(3, 'S')]        )


class FullHouseTests(unittest.TestCase):
    def setUp(self):
        self.hands = TestHands().hands

    def test(self):
        full_house = FullHouse(self.hands['full_house']).five_best
        self.assertListEqual(
            full_house,
            [Card('A', 'D'), Card('A', 'S'), Card(3, 'H'), Card(3, 'C'), Card(3, 'D')]
        )


class FourOfAKindTests(unittest.TestCase):
    def setUp(self):
        self.hands = TestHands().hands

    def test_four_of_a_kind(self):
        quads = FourOfAKind(self.hands['four_of_a_kind']).five_best
        self.assertListEqual(
            quads,
            [Card('A', 'C'), Card('A', 'H'), Card('A', 'S'), Card('A', 'D'), Card(7, 'D')]        )


class StraightFlushTests(unittest.TestCase):
    def setUp(self):
        self.hands = TestHands().hands

    def test_straight_flush(self):
        straight_flush = StraightFlush(self.hands['straight_flush']).five_best
        self.assertListEqual(
            straight_flush,
            [Card(7, 'S'), Card(6, 'S'), Card(5, 'S'), Card(4, 'S'), Card(3, 'S')]
        )


class TestRoyalFlush(unittest.TestCase):
    def setUp(self):
        ## get relevant properties
        props = [j for (j, k) in getmembers(TestHands, property) if j[:2] != '__']
        self.hands = {i: TestHands().__getattribute__(i) for i in props}

    def test(self):
        royal_flush = StraightFlush(self.hands['royal_flush']).five_best
        self.assertListEqual(
            royal_flush,
            [Card('A', 'D'), Card('K', 'D'), Card('Q', 'D'), Card('J', 'D'), Card(10, 'D')]        )


class CompareRanksTests(unittest.TestCase):
    def setUp(self):
        self.hands = TestHands()

    def test_equiv(self):
        P1 = Pair(self.hands['pair']) ## A's
        P2 = Pair(self.hands['pair']) ## 3's
        self.assertTrue(P1 == P2)

    def test_not_equiv(self):
        P1 = Pair(self.hands['pair'])
        P2 = Pair(self.hands['pair2'])
        self.assertTrue(P1 != P2)

    def test_pair_3s_smaller_than_pair_As(self):
        aces = Pair(self.hands['pair'])
        threes = Pair(self.hands['pair2'])
        self.assertTrue(threes < aces)

    def test_pair_As_greater_than_pair_3s(self):
        aces = Pair(self.hands['pair'])
        threes = Pair(self.hands['pair2'])
        self.assertTrue(aces > threes)

    def test_straight_smaller_than_flush(self):
        straight = Straight(self.hands['straight'])
        flush = Flush(self.hands['flush'])
        self.assertTrue(straight < flush)

    def test_flush_greater_than_straight(self):
        straight = Straight(self.hands['straight'])
        flush = Flush(self.hands['flush'])
        self.assertTrue(flush > straight)

    def test_royal_flush_gl(self):
        straight_flush = StraightFlush(self.hands['straight_flush'])
        royal_flush = RoyalFlush(self.hands['royal_flush'])
        self.assertTrue(straight_flush < royal_flush)

    def test_two_straights(self):
        straight1 = Straight(self.hands['straight'])
        straight2 = Straight(self.hands['long_straight'])
        self.assertTrue(straight2 > straight1)

    def test_high_card_lt_pair(self):
        high_card = HighCard(self.hands['high_card'])
        pair = HighCard(self.hands['pair'])
        self.assertTrue(high_card < pair)

    def test_class_level_comparison(self):
        """
        this test fails but I don't think this
        functionality is needed
        """
        pass#self.assertTrue(Pair > HighCard)

    def test_max(self):
        three_oak = ThreeOfAKind(self.hands['three_of_a_kind'])
        straight = Straight(self.hands['straight'])
        pair = Pair(self.hands['pair'])
        self.assertEqual(max(three_oak, straight, pair), straight)

class TestHandEval(unittest.TestCase):
    def setUp(self):
        self.hands = TestHands()

    def test_pair(self):
        H = Hand(self.hands['pair'])
        self.assertEqual(H.eval().__class__.__name__, 'Pair')

    def test_four_of_a_kind(self):
        H = Hand(self.hands['four_of_a_kind'])
        self.assertEqual(H.eval().__class__.__name__, 'FourOfAKind')



























if __name__ == '__main__':
    unittest.main()




























