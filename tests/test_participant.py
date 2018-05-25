import os
import unittest
from pprint import pprint
from peerplays import PeerPlays
from bookied_sync.lookup import Lookup
from bookied_sync.participant import LookupParticipants


class Testcases(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        Lookup._clear()
        Lookup(
            network="unittests",
            sports_folder=os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                "bookiesports"
            ),
            peerplays_instance=PeerPlays(
                nobroadcast=True,
            )
        )
        self.lookup = LookupParticipants(
            "AmericanFootball",
            "NFL_Teams_2017-18"
        )

    def test_init(self):
        self.assertIsInstance(self.lookup, dict)

    def test_is_participant(self):
        self.assertFalse(self.lookup.is_participant("foobarfoo"))
        self.assertTrue(self.lookup.is_participant("BuffBill"))
        self.assertTrue(self.lookup.is_participant("BuFFBiLL"))
        self.assertTrue(self.lookup.is_participant("Buffalo Bills"))
        self.assertTrue(self.lookup.is_participant("BuffaLO Bills"))
