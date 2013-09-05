__author__ = 'esauro'

from django.utils import unittest
from models import Member

class AuctionTests(unittest.TestCase):

    def test_set_bids_bidsto_bigger_than_diff(self):
        member = Member(bids_left = 100, tokens_left = 100, bidsto_left = 100)
        member.set_bids('bid', 150)
        self.assertEqual(member.bidsto_left, 50)
        self.assertEqual(member.bids_left, 100)

    def test_set_bids_bidsto_equal_than_diff(self):
        member = Member(bids_left = 100, tokens_left = 100, bidsto_left = 100)
        member.set_bids('bid', 100)
        self.assertEqual(member.bidsto_left, 0)
        self.assertEqual(member.bids_left, 100)

    def test_set_bids_bidsto_smaller_than_diff(self):
        member = Member(bids_left = 100, tokens_left = 100, bidsto_left = 100)
        member.set_bids('bid', 50)
        self.assertEqual(member.bidsto_left, 0)
        self.assertEqual(member.bids_left, 50)

    def test_set_bids_nobidsto(self):
        member = Member(bids_left = 100, tokens_left = 100, bidsto_left = 0)
        member.set_bids('bid', 50)
        self.assertEqual(member.bidsto_left, 0)
        self.assertEqual(member.bids_left, 50)



